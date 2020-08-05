import subprocess
import os
import struct
import time
import select
import traceback

from bestia.output import tty_cols

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
        o = bytes()
        o = subprocess.check_output(['which', binary])
    except subprocess.CalledProcessError:
        pass
    finally:
        return o.decode().strip()


class Process(object):

    def __init__(self, command):
        self.command = command.strip()
        self.stdout = bytearray()
        self.stderr = bytearray()
        self.rc = -1

    def parse_command(self):
        arguments = self.command.split()[1:]
        executable = self.command.split()[0]
        if which(executable):
            executable = which(executable)

        elif os.path.isfile(executable):
            # check executable flag ???
            print(f"Running local file")

        else:
            print(f"Failed to locate {executable} executable")  
            return (None, None)

        return executable, arguments


    def banner(self, msg='', sep='\\', lead_lines=0, trail_lines=0):
        msg = f"[{self.command}]{msg} "
        c = 0
        if len(msg) < tty_cols():
            c = tty_cols() - len(msg)
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
        if not self.command or not type(self.command) == str:
            return -1

        if verbose > 0:
            self.banner(lead_lines=1)

        executable, arguments = self.parse_command()
        if not executable:
            return -1

        child_pid, stdin_fd, stdout_fd, stderr_fd = fork_subproc(path=executable, args=arguments)

        os.set_blocking(stdout_fd, False)
        os.set_blocking(stderr_fd, False)

        byte = { stdout_fd: True        , stderr_fd: True        }
        line = { stdout_fd: bytearray() , stderr_fd: bytearray() }

        while byte[stdout_fd] or byte[stderr_fd]:
            for readable_fd in select.select(
                [stdout_fd, stderr_fd, ], # rlist
                [],                       # wlist
                [],                       # xlist
                0.2,
            )[0]:
                byte[readable_fd] = os.read(readable_fd, 1)  # read 1 byte at a time
                if byte[readable_fd]:

                    line[readable_fd] += byte[readable_fd]

                    if byte[readable_fd] == b'\n':
                        
                        if readable_fd == stderr_fd:
                            self.stderr += line[readable_fd]

                        elif readable_fd == stdout_fd:
                            self.stdout += line[readable_fd]
                            if verbose > 1:
                                print(line[readable_fd].decode(), end='')

                        line[readable_fd] = bytearray()

        if verbose > 1 and self.stderr:
            self.banner(msg=" stderr", sep='?', lead_lines=1)
            print(self.stderr.decode(), end='')

        self.rc = wait_for(child_pid)
        for fd in (stdin_fd, stdout_fd, stderr_fd):
            os.close(fd)

        if verbose > 0:
            self.banner(
                msg=f" exit={self.rc}",
                sep='/' if self.rc == SUCCESS else '!',
                trail_lines=1,
            )

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
