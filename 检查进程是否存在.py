import os
import time

def check_process_exists(pid):
    """Check if a process with the given PID exists."""
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

def wait_or_execute(pid):
    """Wait for a process with the given PID to exit, or execute a command if it doesn't exist."""
    if check_process_exists(pid):
        print(f"Process {pid} exists, waiting...")
        # 这里我们使用简单的轮询来模拟等待，但这不是最高效的方法
        # 在实际应用中，你可能需要更复杂的逻辑或第三方库来等待进程
        while check_process_exists(pid):
            time.sleep(1)  # 等待1秒然后再次检查
        print(f"Process {pid} has exited.")
    else:
        print(f"Process {pid} does not exist, executing command: ")

if __name__ == '__main__':
    wait_or_execute(123)