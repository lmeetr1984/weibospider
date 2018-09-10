import threading
import sys


class KThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        # 调用父初始化函数
        threading.Thread.__init__(self, *args, **kwargs)
        self.killed = False

    def start(self):
        """Start the thread."""
        # 替换了系统的run方法
        self.__run_backup = self.run
        self.run = self.__run  # Force the Thread to install our trace.

        threading.Thread.start(self)

    def __run(self):

        """Hacked run function, which installs the trace."""
        sys.settrace(self.globaltrace)

        # 恢复方法
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):
        # 'call' 函数运行之前触发
        if why == 'call':
            return self.localtrace

        else:
            return None

    def localtrace(self, frame, why, arg):
        # 如果线程已经被kill
        if self.killed:
            # 并且在一行被执行前
            if why == 'line':
                # 退出
                raise SystemExit()

        return self.localtrace

    def kill(self):
        self.killed = True
