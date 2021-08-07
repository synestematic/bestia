import os
import select
import struct
import subprocess

from datetime import datetime

from .output import tty_cols, FString, Row
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
                            # buffer this bytes until they are utf-8 printable...
                            try:
                                print(
                                    byte[readable_fd].decode(),
                                    end='',
                                    flush=True,
                                )
                            except:
                                pass
                                # print(
                                #     '�',
                                #     end='',
                                #     flush=True,
                                # )

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


class SSHCommand(Process):

    WHITELIST = (
        # sudo does not need to be in here  LOL :)
        'cat',
        'docker',
        'find',
        'fgrep',
        'grep',
        'hostname',
        'ls',
        'netstat',
        'ping',
        'ps',
        'pwd',
        'ssh',
        'wget',
        'whoami',
    )

    def __init__(self, command, user, host, timeout=2):
        # -F /dev/null               discards custom search ssh configs in ~/.ssh/config
        # -o ConnectTimeout=2        avoids waiting for unresponsive hosts
        # -o ServerAliveInterval=60  client sends null packet to server to keep connection alive
        #                            avoids zombie ssh sessions...
        super().__init__(
            'ssh -F /dev/null -o ServerAliveInterval=60 -o ConnectTimeout={} {}@{} {}'.format(
                timeout, user, host, command
            )
        )
        self.user = user
        self.host = host

    def banner(self, msg='', sep='\\', lead_lines=0, trail_lines=0):

        for arg in self.command.split():

            if arg.startswith(f'{self.user}@'):
                ssh_command = f'{self.command.split(arg)[0]}{arg}'
                # ssh -F /dev/null -o ServerAliveInterval=60 -o ConnectTimeout=2 user@my.host.com sudo whoami
                host = ssh_command.split(f'{self.user}@')[-1] # my.host.com
                ssh_command = ssh_command.replace(host, '')   # ssh -F /dev/null -o ServerAliveInterval=60 -o ConnectTimeout=2 user@
                rmt_command = self.command.split(arg)[1]      # sudo whoami

                Row(
                    FString(
                        ssh_command,
                        size=len(ssh_command),
                        fx=['faint'],
                    ),
                    FString(
                        host,
                        size=len(host),
                        fg='cyan',
                        # fx=['bold'],
                    ),
                    FString(
                        rmt_command,
                        size=len(rmt_command),
                        fg='blue',
                    ),
                    FString(
                        f'{msg} ',
                        pad=sep,
                        fx=['bold'],
                    )
                ).echo(mode='retro')

                if 'exit=' in msg: print()

                return

        super().banner(msg=msg, sep=sep, lead_lines=lead_lines, trail_lines=trail_lines)



def _log_host_command(host, cmd, o , e):
    """ logs commands stdout and stderr for non-ephemeral usage
    """
    datehost_dir = _create_datehost_dir(host)
    if not datehost_dir:
        return FAILURE

    try:
        log_cmd_dir = '{datehost_dir}/[{time}] {cmd}'.format(
            datehost_dir=datehost_dir,
            time=datetime.now().strftime('%H:%M:%S'),
            cmd=cmd.replace('/', '∕'),
        )
        os.makedirs(log_cmd_dir, exist_ok=False)

        # CREATE FILES
        if o:
            with open(f'{log_cmd_dir}/1', 'wb') as stdout:
                stdout.write(o)

        if e:
            with open(f'{log_cmd_dir}/2', 'wb') as stderr:
                stderr.write(e)

        return SUCCESS

    except:
        return FAILURE


class RemoteHost(object):

    def __init__(self, user, host):
        self.user = user
        self.host = host

    def ssh_run(
            self,
            cmd,
            sudo=False,
            strict=False,
            timeout=2,
            verbose=1,
            log=False,
            risk=False
        ):
        """ sudo   = executes ssh command as root
            strict = raises exception if rc is not 0
            log    = store results locally for logging
            risk   = ignores COMMAND_WHITELIST, allows execution of any command
        """
        # ONLY RUN IF NODE IS NOT DISABLED IN CC...
        if not risk and cmd.split()[0] not in SSHCommand.WHITELIST:
            raise RuntimeError(f'ssh command not allowed -> [{cmd}]')

        cmd = cmd if not sudo else f'sudo {cmd}'

        ssh_proc = SSHCommand(
            command=cmd,
            user=self.user,
            host=self.host,
            timeout=timeout,
        )
        ssh_proc.run(verbose=verbose)

        if log:
            _log_host_command(self.host, cmd, ssh_proc.stdout, ssh_proc.stderr)

        if ssh_proc.rc != 0 and strict:
            raise RuntimeError(f'Failed to run -> {cmd}')

        return ssh_proc

    def docker_exec(self, container, cmd, sudo=False, strict=False, verbose=1, log=False, risk=False):
        """ ssh user@my.host.com sudo docker exec my_container cat /var/log/gunicorn/error.log
        """
        if not risk and cmd.split()[0] not in SSHCommand.WHITELIST:
            raise RuntimeError(f'ssh command not allowed -> [{cmd}]')
        user = '' if not sudo else '-u root'
        return self.ssh_run(
            sudo=True,
            cmd=f'docker exec {user} {container.name} {cmd}',
            strict=strict,
            verbose=verbose,
            log=log
        )

    def lxc_attach(self, container, cmd, user='', verbose=2, log=False, risk=False):
        """ ssh user@my.host.com sudo lxc-attach --name="proxy" -- su - client -c "ls -l"
        """
        if not risk and cmd.split()[0] not in SSHCommand.WHITELIST:
            raise RuntimeError(f'ssh command not allowed -> [{cmd}]')
        return self.ssh_run(
            sudo=True,
            cmd=f'lxc-attach --name="{container}" -- su - {user} -c "{cmd}"',
            verbose=verbose,
            log=log,
            risk=True,
        )

    def get_remote_file(self,
        remote_filename,
        remote_directory='',
        # local_filename='',
        # local_directory='',
        container=None,
        fgrep='',
    ):
        """ cats remote_file contents to stdout and writes to local_file
            DOES NOT work with directories     !
            DOES NOT keep original permissions !
        """
        remote_filepath, _local_filepath = _resolve_filepath_locations(
            remote_filename=remote_filename,
            remote_directory=remote_directory,
            # local_filename=local_filename,
            # local_directory=local_directory if local_directory else create_datehost_dir(self.host),
        )

        # 1 allows to monitor read file, 2 risks printing non printable bytes
        verbose = 1

        cmd = f'cat {remote_filepath}' if not fgrep else f'fgrep {fgrep} {remote_filepath}'

        if container:
            cmd = self.docker_exec(
                container=container,
                cmd=cmd,
                verbose=verbose,
                log=True,
            )
        else:
            cmd = self.ssh_run(
                sudo=True,
                cmd=cmd,
                verbose=verbose,
                log=True,
            )

        ###########################################
        # this WILL overwrite your local files!
        # NOTE: using log=True now instead
        ###########################################
        # try:
        #     with open(_local_filepath, 'wb') as f:
        #         f.write(cmd.stdout)
        #     return SUCCESS
        # except:
        #     return FAILURE
        ###########################################


def _create_datehost_dir(host):
    """ /home/user/S1/logs/2021-02-17-Wed/my.host.com
    """
    try:
        datehost_dir = '/home/{user}/S1/logs/{date}/{host}'.format(
            user=os.environ['USER'],
            date=datetime.now().strftime('%Y-%m-%d-%a'),
            host=host,
        )
        os.makedirs(datehost_dir, exist_ok=True)
        return datehost_dir
    except Exception:
        raise Exception(f'Failed to create store dir for {host}')


def _resolve_filepath_locations(
    remote_filename, remote_directory='', local_filename='', local_directory='',
):
    """ if remote_directory is not specified, remote_file must be in ssh_user home dir
        if local_directory  is not specified, local_file  will be put in local CWD
        if local_filename   is not specified, local_file  will have same name as remote_filename
    """
    if remote_directory:
        remote_directory = remote_directory.rstrip('/')
        remote_filepath = f'{remote_directory}/{remote_filename}'
    else:
        remote_filepath = remote_filename

    if not local_filename:
        local_filename = remote_filename

    if local_directory:
        local_directory = local_directory.rstrip('/')
        local_filepath = f'{local_directory}/{local_filename}'

    else:
        local_filepath = local_filename

    return remote_filepath, local_filepath
