from os import pipe, fork, close, dup2, execv, set_blocking, read, waitpid, getpid
from struct import pack, unpack
from select import select

def wait_for(pid):
    sc = pack(
        "<I", waitpid(pid, 0)[1]
    )
    return unpack("bb", sc[0:2])[1]

def piped_subproc(*args):
    ''' runs command on forked (parallel) subproc
        returns subproc pipe-ends for IO operations and pid
    '''

    # ls -la /proc/$$/fd
    # pipe() returns 2 non-inheritable file descriptors (r, w)

    STDIN_read, STDIN_write = pipe()
    STDOUT_read, STDOUT_write = pipe()
    STDERR_read, STDERR_write = pipe()

    pid = fork() # fork() subproc
    # both main and subproc have access to the same scope?

    # execution continues on both sides of if
    if pid == 0: # SUB PROC
        # close unnecessary pipe-ends
        close(STDIN_write)
        close(STDOUT_read)
        close(STDERR_read)

        # close defaults and assign appropriate pipe-ends to child STDIN, STDOUT, STERR
        close(0)
        dup2(STDIN_read, 0)

        close(1)
        dup2(STDOUT_write, 1)

        close(2)
        dup2(STDERR_write, 2)

        # exec.() replaces current proc with cmd & gets proc's PID
        execv(args[0], args)
        # will NOT return to calling proc

    else: # MAIN PROC
        # close unnecessary pipe-ends
        close(STDIN_read)
        close(STDOUT_write)
        close(STDERR_write)
        return pid, STDIN_write, STDOUT_read, STDERR_read


def read_cmd(*cmd, buffer_size=1024):
    '''
        allows to read piped_proc stdOut | stdErr
    '''

    child_pid, stdIn_fd, stdOut_fd, stdErr_fd = piped_subproc(*cmd)
    set_blocking(stdOut_fd, False)
    set_blocking(stdErr_fd, False)

    read_fds = {
        stdOut_fd: {
            'data': bytearray(), 'depleted': False
        },
        stdErr_fd: {
            'data': bytearray(), 'depleted': False
        },
    }

    while not read_fds[stdOut_fd]['depleted'] or not read_fds[stdErr_fd]['depleted']:

        for fd in select(
            [stdOut_fd, stdErr_fd], # rlist
            [],                     # wlist
            [],                     # xlist
            0.2,
        )[0]:

            current_fd_data = read(fd, buffer_size) # how to set optimal BUFFER SIZE?
            if current_fd_data:
                read_fds[fd]['data'].extend(current_fd_data)
            else:
                read_fds[fd]['depleted'] = True

    status_code = wait_for(child_pid)

    for fd in (stdIn_fd, stdOut_fd, stdErr_fd):
        close(fd)
    
    return read_fds[stdOut_fd]['data'], read_fds[stdErr_fd]['data'], status_code
