import datetime
import time
from time import strftime


if __name__ == '__main__':

    i = 1
    while True:
        now = datetime.datetime.now()
        a = now.strftime('%Y-%m-%d %H:%M:%S.%f')
        print(now.strftime('%Y-%m-%d %H:%M:%S.%f'))
        print(type(a))
        time.sleep(1)
        i +=1
        if i==10:
            break