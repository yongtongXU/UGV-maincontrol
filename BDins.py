import threading
from queue import Queue
import serial
import serial.tools.list_ports
import datetime
from time import strftime
import time
import math
import struct
class Serial_BD(object):
    def __init__(self,COM_name):

        self.RUN_FLAG = True

        self.BD_message_queue = Queue(10)
        self.BD_list = []
        
        self.MY_INDEX = 1
        # 接收GPS串口名
        self.read_gps_serial_name = COM_name

        # read_com = 'COM5'

        # 开启设备
        self.gps_serial = serial.Serial(self.read_gps_serial_name, 460800, timeout=1)
        self.gps_open_status = self.gps_serial.isOpen()
        print("开启状态:", self.gps_serial)

        self.sendThread = threading.Thread(target=self.getGPSThread, args=())
        self.sendThread.start()
        # self.gps_serial.write(ord(data))

    def getGPSThread(self):

        # 大小端
        self.byteorder = 'little'

        # bdfpdb 报文头
        bdfpdb_head_str = 'aa4410' # AA 44 10 3C 00 00 00 00 2B 91 05 44 57 85 F3 3E 95 46 B4 3F 47 08 57 C0 A4 9F BC AD 00 2B 32 40 36 B6 0E 92 8A 35 5B 40 74 51 E0 48 C2 F2 40 C3 06 6A DC C2 FB 1E DF 44 00 00 00 00 00 00 00 00 F9 E8 39 57
        # rawimusb 报文头
        rawimusb_head_str = 'aa4413' #AA 44 13 28 45 01 00 00 E3 26 08 00 00 00 00 00 14 12 69 3C F2 B1 80 40 77 00 00 00 99 E2 0A 00 3D 1E 00 00 71 10 00 00 01 FD FF FF 77 01 00 00 B2 00 00 00 56 17 FB F5
        # 帧头
        head_check_data = bytes()

        # 陀螺仪计算基数
        acceleration_base = 200 * 200 * pow(2, -31)
        # 加速度计算基数
        gyroscope_base = 200 * 720 * pow(2, -31)

        print('加速度计算基数', 200 * 720 *4)
        print("x= {:.4f}".format(gyroscope_base))

        while self.RUN_FLAG:
            # 读串口
            get_data = self.gps_serial.read(1)

            if get_data == bytes().fromhex('aa'):
                head_check_data = bytes()
            # 累加帧头
            head_check_data += get_data

            # 判断帧头 是否匹配
            if len(head_check_data) == 3:
                # bdfpdb 卫星定位
                if head_check_data.hex() == bdfpdb_head_str:
                    body_data = self.gps_serial.read(65)
                    results_data = head_check_data + body_data
                    # print('长度：',len(results_data))

                    # GNSS周
                    self.gps_week = int.from_bytes(results_data[4:8], self.byteorder, signed=False)
                    # print('周:', self.gps_week)
                    # 周秒
                    self.gps_seconds = self.bytesToFloat(results_data[8:12])
                    # print('周秒:', self.gps_seconds)
                    # 偏航角
                    self.yaw_angle = self.bytesToFloat(results_data[12:16])
                    # print('偏航角:', self.yaw_angle)
                    # 俯仰角
                    self.pitch_angle = self.bytesToFloat(results_data[16:20])
                    # print('俯仰角:', self.pitch_angle)
                    # 滚动角
                    self.roll_angle = self.bytesToFloat(results_data[20:24])
                    # print('滚动角:', self.roll_angle)
                    # 纬度
                    self.latitude = self.bytesToFloat(results_data[24:32])
                    # print('纬度:', self.latitude)
                    # 经度
                    self.longitude = self.bytesToFloat(results_data[32:40])
                    # print('经度:', self.longitude)
                    # 高度
                    self.elevation = self.bytesToFloat(results_data[40:44])
                    # print('高度:', self.elevation)
                    # 东速
                    self.east_speed = self.bytesToFloat(results_data[44:48])
                    # print('东速:', self.east_speed)
                    # 北速
                    self.north_speed = self.bytesToFloat(results_data[48:52])
                    # print('北速:', self.north_speed)
                    # 天速
                    self.sky_speed = self.bytesToFloat(results_data[52:56])
                    # print('天速:', self.sky_speed)
                    # 天线 1 卫星数
                    self.nsv1_num = int.from_bytes(results_data[56:58], self.byteorder, signed=False)
                    # print('天线 1 卫星数:', self.nsv1_num)
                    # 天线 2 卫星数
                    self.nsv2_num = int.from_bytes(results_data[58:60], self.byteorder, signed=False)
                    # print('天线 2 卫星数:', self.nsv2_num)
                    # 定位类型
                    self.bestpos_type = self.bytesToShort(results_data[60:62])
                    # print('定位类型:', self.bestpos_type)
                    # 定向类型
                    self.heading_type = self.bytesToShort(results_data[62:64])
                    # print('定向类型:', self.heading_type)
                    # 获取校验和
                    get_checksum = results_data[64:68]

                    # 格式化 输出字符串
                    self.formatIMUStr()


                # rawimusb 陀螺仪
                if head_check_data.hex() == rawimusb_head_str:

                    body_data = self.gps_serial.read(53)
                    results_data = head_check_data + body_data
                    # print('rawimusb长度：', len(results_data))

                    # 报文ID
                    rawimusb_id = results_data[4:6].hex()
                    # print('rawimusb 报文ID号：', rawimusb_id)
                    # rawimusb GNSS周
                    rawimusb_week = self.bytesToShort(results_data[6:8])
                    # print('rawimusb 周:', rawimusb_week)
                    # rawimusb 周秒
                    rawimusb_seconds = self.bytesToFloat(results_data[8:12])
                    # print('周秒:', rawimusb_seconds)

                    # IMU 状态
                    imu_status = results_data[24:28]
                    imu_status_bit = bin(imu_status[0])[2:]

                    # Z 向加速度计状态
                    self.acceleration_z_status = imu_status_bit[0]
                    # print('Z 向加速度计状态', self.acceleration_z_status)
                    # Z 向加速度计输出（上）
                    self.acceleration_plus_z = int.from_bytes(results_data[28:32], self.byteorder, signed=True) * acceleration_base
                    # print('Z 向加速度计输出（上）', self.acceleration_plus_z)

                    # Y 向加速度计状态
                    self.acceleration_y_status = imu_status_bit[1]
                    # print('Y 向加速度计状态:', self.acceleration_y_status)
                    # -Y 向加速度计输出（后）
                    self.acceleration_minus_y = int.from_bytes(results_data[32:36], self.byteorder, signed=True) * acceleration_base
                    # print('-Y 向加速度计输出（后）:', self.acceleration_minus_y)

                    # X 向加速度计状态
                    self.acceleration_x_status = imu_status_bit[2]
                    # print('X 向加速度计状态:', self.acceleration_x_status)
                    # X 向加速度计输出（右）
                    self.acceleration_plus_x = int.from_bytes(results_data[36:40], self.byteorder, signed=True) * acceleration_base
                    # print('X 向加速度计输出（右）:', self.acceleration_plus_x)

                    # Z 向陀螺仪状态
                    self.rotate_speed_z_status = imu_status_bit[4]
                    # print('Z 向陀螺仪状态:', self.rotate_speed_z_status)
                    # Z 向陀螺仪输出（上）
                    self.rotate_speed_plus_z = int.from_bytes(results_data[40:44], self.byteorder, signed=True) * gyroscope_base
                    # print('Z 向陀螺仪输出（上）:', self.rotate_speed_plus_z)

                    # Y 向陀螺仪状态
                    self.rotate_speed_y_status = imu_status_bit[5]
                    # print('Y 向陀螺仪状态:', self.rotate_speed_y_status)
                    # -Y 向陀螺仪输出（后）
                    self.rotate_speed_minus_y = int.from_bytes(results_data[44:48], self.byteorder, signed=True) * gyroscope_base
                    # print('-Y 向陀螺仪输出（后）:', self.rotate_speed_minus_y)

                    # X 向陀螺仪状态
                    self.rotate_speed_x_status = imu_status_bit[6]
                    # print('X 向陀螺仪状态:', self.rotate_speed_x_status)
                    # X 向陀螺仪输出（右）
                    self.rotate_speed_plus_x = int.from_bytes(results_data[48:52], self.byteorder, signed=True) * gyroscope_base
                    # print('X 向陀螺仪输出（右）:', self.rotate_speed_plus_x)

                    # 获取校验和
                    get_checksum = results_data[52:56]
        self.close_event()

    def bytesToShort(self, bytes_data):
        """
        bytes转换成 short
        """
        byte_ary = bytearray()

        for one_byte in bytes_data:
            byte_ary.append(one_byte)

        return struct.unpack('H'*int(len(byte_ary)/2), byte_ary)[0]

    def bytesToFloat(self, bytes_data):
            """
            bytes转换成 float
            """
            byte_ary = bytearray()

            for one_byte in bytes_data:
                byte_ary.append(one_byte)

            if len(byte_ary) > 4:
                return struct.unpack("<d", byte_ary)[0]
            else:
                return struct.unpack("<f",byte_ary)[0]

    

    def formatIMUStr(self):
        """
        拼接传给总控的字符串
        :return:
        """

        coursett = 0
        # 计算航向
        if self.north_speed == 0:
            if self.east_speed > 0:
                coursett = 90
            elif self.east_speed < 0:
                coursett = 270
            else:
                coursett = 0
        else:
            if self.east_speed == 0:
                if self.north_speed > 0:
                    coursett = 0
                else:
                    coursett = 180
            else:
                coursett = math.atan(self.east_speed / self.north_speed) * 180 / 3.1415926

                if self.east_speed > 0 and self.north_speed < 0:
                    coursett += 90
                elif self.east_speed < 0 and self.north_speed < 0:
                    coursett += 180
                elif self.east_speed < 0 and self.north_speed > 0:
                    coursett += 270

        comput_yaw_angle = 0
        if self.yaw_angle <= 90:
            comput_yaw_angle = self.yaw_angle
        elif self.yaw_angle > 90 and self.yaw_angle <= 180:
            comput_yaw_angle = self.yaw_angle - 90
        elif self.yaw_angle > 180 and self.yaw_angle <= 270:
            comput_yaw_angle = self.yaw_angle - 180
        elif self.yaw_angle > 270:
            comput_yaw_angle = self.yaw_angle - 270

        comput_yaw_angle = comput_yaw_angle / 180 * 3.141592
        # 计算纵向速度
        protait_speed = math.cos(comput_yaw_angle) * self.north_speed + math.sin( comput_yaw_angle) * self.east_speed

        # 计算横向速度
        landscape_speed = math.sin(comput_yaw_angle) * self.north_speed + math.cos(comput_yaw_angle) * self.east_speed
        time_str = time.strftime('%X',time.localtime(time.time()))

        # 内容
        body_str = ("%s,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.6f,%.6f,%.2f,%.2f,%.2f,%.2f,0,0,0,%s*&&" %
                    (self.MY_INDEX,
                  protait_speed, landscape_speed, self.sky_speed,
                  self.rotate_speed_plus_x, self.rotate_speed_minus_y,
                  self.rotate_speed_plus_z,
                  self.pitch_angle, self.roll_angle, self.yaw_angle,
                  self.latitude, self.longitude,
                  self.acceleration_minus_y, self.acceleration_plus_x,
                  self.acceleration_plus_z,
                  coursett,time_str))
        # 计算长度
        send_length = len(body_str)
        if send_length < 99:
            send_length += 7
        else:
            send_length += 8
        sv_str = ("$SV,%d,%s" % (send_length, body_str))
        # print(sv_str)
        self.BD_str = sv_str
        self.BD_list = [protait_speed, landscape_speed, self.sky_speed,
                  self.rotate_speed_plus_x, self.rotate_speed_minus_y,
                  self.rotate_speed_plus_z,
                  self.pitch_angle, self.roll_angle, self.yaw_angle,
                  self.latitude, self.longitude,
                  self.acceleration_minus_y, self.acceleration_plus_x,
                  self.acceleration_plus_z,
                  coursett,time_str]
        
        # 清空队列
        self.checkQueue(self.BD_message_queue)
        # 数据放入队列
        self.BD_message_queue.put(self.BD_list)

        
    def checkQueue(self, one_queue):
        for i in range(one_queue.qsize()):
            if one_queue.qsize() == 0:
                return
            one_queue.get()
    
    def gps_checksum(self, source_string):
        """
            简单的异或校验
            :param source_string:数据
            :return:
        """
        # 检验和
        checksum = 0
        # 字节累加长度
        sum_len = 4

        # 校验次数
        check_num = math.floor(len(source_string)/sum_len)

        for i in range(check_num):
            check_str = source_string[:sum_len]
            source_string = source_string[sum_len:]

            check_one = 0
            for t in range(sum_len):

                check_one += int.from_bytes(check_str[t:(t + 1)], self.byteorder, signed=False)

            if i:
                checksum ^= check_one
            else:
                checksum = check_one ^ 0
            # if i:
            #     checksum ^= int.from_bytes(source_string[sum_len*i : sum_len*(i+1)], byteorder, signed=True)
            # else:
            #     checksum = int.from_bytes(source_string[:sum_len], byteorder, signed=True) ^ 0
        return checksum
    
    def close_event(self):
        
        
        print("组合导航读取关闭")
    
if __name__ == '__main__':

    print("test")
    test1 = Serial_BD()