import time


def print_run_time(func):
    def wrapper(*args, **kw):
        local_time = time.time()
        ret = func(*args, **kw)
        info_str = 'Function [%s] run time is %.2f' % (func.__name__, time.time() - local_time)
        print(info_str)
        return ret
    return wrapper


def print_ts(message):
    print ("[%s] %s"%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), message))


if __name__ == '__main__':
    pass
