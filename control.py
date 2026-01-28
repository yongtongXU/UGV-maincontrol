import matplotlib.pyplot as plt
import numpy as np
from configparser import ConfigParser
class DeltaPID(object):
    """增量式PID算法实现"""

    def __init__(self, target, cur_val, dt,model):
        self.control_value_list = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.read_value_rw()
        self.value_set(model)

        self.dt = dt  # 循环时间间隔


        self.target = target  # 目标值
        self.cur_val = cur_val  # 算法当前PID位置值
        self._pre_error = 0  # t-1 时刻误差值
        self._pre_pre_error = 0  # t-2 时刻误差值

    def read_value_rw(self):
        self.cf = ConfigParser()
        self.cf.read('config.ini')
        for i in range(len(self.cf.items('control value'))):
            self.control_value_list[i] = self.cf.items('control value')[i][1]

    def value_set(self,model):
        if model == 0:#艏向
            self.k_p = float(self.control_value_list[0])  # 比例系数
            self.k_i = float(self.control_value_list[1])  # 积分系数
            self.k_d = float(self.control_value_list[2])  # 微分系数

        elif model == 1:#航速
            self.k_p = float(self.control_value_list[3])  # 比例系数
            self.k_i = float(self.control_value_list[4])  # 积分系数
            self.k_d = float(self.control_value_list[5])  # 微分系数

    def calcalate(self):
        error = self.target - self.cur_val
        p_change = self.k_p * (error - self._pre_error)
        i_change = self.k_i * error
        d_change = self.k_d * (error - 2 * self._pre_error + self._pre_pre_error)
        delta_output = p_change + i_change + d_change  # 本次增量
        self.cur_val += delta_output  # 计算当前位置

        self._pre_error = error
        self._pre_pre_error = self._pre_error

        return self.cur_val

    def fit_and_plot(self, count=200):
        counts = np.arange(count)
        outputs = []
        for i in counts:
            outputs.append(self.calcalate())
            print('Count %3d: output: %f' % (i, outputs[-1]))

        print('Done')

        plt.figure()
        plt.axhline(self.target, c='red')
        plt.plot(counts, np.array(outputs), 'k.')
        plt.ylim(min(outputs) - 0.1 * min(outputs),
                 max(outputs) + 0.1 * max(outputs))
        plt.plot(outputs)
        plt.show()


if __name__ == '__main__':
    pid = DeltaPID(0, 0, 0, 0)
    pid.fit_and_plot(150)
