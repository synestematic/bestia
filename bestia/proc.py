import subprocess
import os
import struct
import time
import select

from .output import tty_cols
from .error import *

SUCCESS =  0
FAILURE = -1

DEFAULT_STDIN  = 0
DEFAULT_STDOUT = 1
DEFAULT_STDERR = 2

def change_directory(original_func):
    def decorated_func(*args, **kwargs):
        # check if dir exists
        if "in_dir" in kwargs:
            previous_dir = os.getcwd()
            os.chdir(kwargs["in_dir"])
            rc = original_func(*args, **kwargs)
            os.chdir(previous_dir)
            return rc
        return original_func(*args, **kwargs)
    return decorated_func

def which(binary):
    try:
        o = subprocess.check_output(['which', binary])
        return o.decode().strip()
    except subprocess.CalledProcessError:
        return ''


class Process(object):

    def __init__(self, command):
        if not command or not type(command) == str:
            raise InvalidCommand(f'Invalid command -> {command}')

        self.command = command.strip()
        self.stdout = bytearray()
        self.stderr = bytearray()
        self.rc = FAILURE

    def parse_command(self):
        command_arguments = self.command.split()

        # executable is in PATH, returns absolute path
        executable_in_path = which(command_arguments[0])
        if executable_in_path:
            return executable_in_path, command_arguments[1:]

        # executable is in PWD
        if os.path.isfile(command_arguments[0]):
            # check executable flag ?
            return command_arguments[0], command_arguments[1:]

        raise InvalidCommand(f"Failed to find executable -> {self.command}")


    def banner(self, msg='', sep='#', lead_lines=0, trail_lines=0):
        msg = f"[{self.command}]{msg} "
        c = 0
        cols = tty_cols()
        if len(msg) < cols:
            c = cols - len(msg)
        for _ in range(lead_lines):
            print()
        print(f"{msg}{sep*c}")
        for _ in range(trail_lines):
            print()


    @change_directory
    def run(self, verbose=2, in_dir=''):
        ''' 
        verbose: 2|1|0
            2: displays command & status & stdout & stderr
            1: displays command & status
            0: displays None

        in_dir: discarded ( used/passed by @change_directory )
        '''
        if verbose > 0:
            self.banner(
                sep='>',
                lead_lines=1,
            )

        ###################################
        self._no_shell_run(verbose=verbose)
        ###################################

        if verbose > 1 and self.stderr:
            self.banner(
                msg=f" stderr",
                sep='?',
                lead_lines=1
            )
            print(self.stderr.decode(), end='')

        if verbose > 0:
            self.banner(
                msg=f" exit={self.rc}",
                sep='<' if self.rc == SUCCESS else '!',
                trail_lines=1,
            )

        return self.rc


    def _no_shell_run(self, verbose):
        executable, arguments = self.parse_command()

        child_pid, stdin_fd, stdout_fd, stderr_fd = fork_subproc(path=executable, args=arguments)

        os.set_blocking(stdout_fd, False)
        os.set_blocking(stderr_fd, False)

        byte = {
            stdout_fd: True,
            stderr_fd: True,
        }

        while byte[stdout_fd] or byte[stderr_fd]:
            for readable_fd in select.select(
                [stdout_fd, stderr_fd, ], # rlist
                [],                       # wlist
                [],                       # xlist
                0.2,                      # timeout
            )[0]:
                byte[readable_fd] = os.read(readable_fd, 1)  # read 1 byte at a time
                if byte[readable_fd]:

                    if readable_fd == stderr_fd:
                        self.stderr += byte[readable_fd]
                    elif readable_fd == stdout_fd:
                        self.stdout += byte[readable_fd]
                        if verbose > 1:
                            print(byte[readable_fd].decode(), end='', flush=True)

        self.rc = wait_for(child_pid)
        for fd in (stdin_fd, stdout_fd, stderr_fd):
            os.close(fd)

        return self.rc


def wait_for(pid):
    ''' docs.python.org/3/library/os.html#os.wait '''
    _, rc = os.waitpid(pid, 0)
    sc = struct.pack("<I", rc)
    retval = struct.unpack("bb", sc[0:2])[1]
    return retval

def fork_subproc(path, args):
    ''' runs command on forked (parallel) subproc
        returns subproc pipe-ends for IO operations and pid
    '''

    # ls -la /proc/$$/fd
    # pipe() returns 2 non-inheritable file descriptors (r, w)
    child_STDIN_read,  child_STDIN_write  = os.pipe()
    child_STDOUT_read, child_STDOUT_write = os.pipe()
    child_STDERR_read, child_STDERR_write = os.pipe()

    child_pid = os.fork() # fork() subproc
    # both main and subproc have access to the same scope
    # execution continues on both sides of if
    if not child_pid:
        # SUB PROC

        # close unnecessary pipe-ends
        os.close(child_STDIN_write)
        os.close(child_STDOUT_read)
        os.close(child_STDERR_read)

        # close defaults and assign appropriate pipe-ends to child STDIN, STDOUT, STERR
        os.close(DEFAULT_STDIN)
        os.dup2(child_STDIN_read, DEFAULT_STDIN)

        os.close(DEFAULT_STDOUT)
        os.dup2(child_STDOUT_write, DEFAULT_STDOUT)

        os.close(DEFAULT_STDERR)
        os.dup2(child_STDERR_write, DEFAULT_STDERR)

        # exec.() replaces current proc with cmd & gets proc's PID
        args.insert(0, path)  # ensure args[0] == path
        os.execv(path, args)

        # does NOT return to calling proc

    elif child_pid:
        # MAIN PROC
        # close unnecessary pipe-ends
        os.close(child_STDIN_read)
        os.close(child_STDOUT_write)
        os.close(child_STDERR_write)
        return child_pid, child_STDIN_write, child_STDOUT_read, child_STDERR_read
