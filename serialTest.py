import serial
import serial.tools.list_ports
import threading
from queue import Queue
import socket
import pandas
import datetime
from time import strftime
import AGV_UI

list_Q = Queue(5)
list_states = Queue(5)




class AGV(object):
    def __init__(self):

        global list_Q
        global list_states
        # 接收串口名
        self.read_gps_serial_name = None
        # 转发消息串口名
        self.send_gps_serial_name = None

        read_com = 'COM3'

        # 获取设备列表
        self.usb_list = list(serial.tools.list_ports.comports())

        for one_serial in self.usb_list:
            one_name = one_serial[0]
            print(one_name)
            if one_name == read_com:
                self.read_gps_serial_name = one_name
                print('找到读取设备：', one_name)


        # 开启设备
        self.AGV_serial = serial.Serial(self.read_gps_serial_name, 115200, timeout=1)
        self.gps_open_status = self.AGV_serial.isOpen()
        print("开启状态:", self.AGV_serial)

        self.sendThread = threading.Thread(target=self.getdataThread, args=())
        self.sendThread.start()

        self.send_data_demo = b'\x7B\x00\x00\x00\x01\x00\x00\x00\x00\xA1\x7D'
        self.rev_data_demo = b'\x7B\x00\x01\x01\x00\x01\x00\x00\xFE\x96\xFD\xCE\x40\x80\xFF\xFB\x00\x07\x00\x01\x58\x38\x83\x7D'


        self.data_head = '7b'
        self.head_check_data = bytes()


    def getdataThread(self):

        while True:
            self.head_check_data = self.AGV_serial.read(1)
            if self.head_check_data.hex() == self.data_head:
                body_data = self.AGV_serial.read(23)
                results_data = self.head_check_data + body_data
                if self.data_BCC(results_data[:22])  == results_data[22]:
                    self.flag_stop = results_data[1]
                    self.speed_x = self.bytesToShort(results_data[2:4])
                    self.speed_y = self.bytesToShort(results_data[4:6])
                    self.speed_z = self.bytesToShort(results_data[6:8])
                    self.acc_x = self.bytesToShort(results_data[8:10])/1672
                    self.acc_y = self.bytesToShort(results_data[10:12])/1672
                    self.acc_z = self.bytesToShort(results_data[12:14])/1672
                    self.ang_x = self.bytesToShort(results_data[14:16])/3753
                    self.ang_y = self.bytesToShort(results_data[16:18])/3753
                    self.ang_z = self.bytesToShort(results_data[18:20])/3753
                    self.battery = self.bytesToShort(results_data[20:22])
                    self.data_check = results_data[22]
                    self.last = results_data[23]

                    self.new_time = datetime.datetime.now()
                    self.new_time_0 = self.new_time.strftime('%Y-%m-%d %H:%M:%S.%f')

                    self.AGV_list_state = [self.new_time,self.speed_x,self.speed_y,self.speed_z,self.acc_x,self.acc_y,self.acc_z,self.ang_x,self.ang_y,self.ang_z,self.battery]

                    list_states.put(self.AGV_list_state)
                    list_Q.put(results_data)

                    print(list_Q.get())
                    print(list_states.get())


                    # print("x方向速度：",self.speed_x,"mm/s")
                    # print("y方向速度：", self.speed_y,"mm/s")
                    # print("z方向速度：", self.speed_z,"mm/s")
                    # print("x方向加速度：", self.acc_x,"m/s^2")
                    # print("y方向加速度：", self.acc_y,"m/s^2")
                    # print("z方向加速度：", self.acc_z,"m/s^2")
                    # print("x方向角加速度：", self.ang_x,"rad/s")
                    # print("y方向角加速度：", self.ang_y,"rad/s")
                    # print("z方向角加速度：", self.ang_z,"rad/s")
                    # print("当前电池电压：",self.battery,"mv")

    def senddataThread(self,senddata):

        self.AGV_serial.write(senddata)
        return len(senddata)

    def bytesToShort(self, bytes_data):
        a1 = bytes_data[0] << 8 | bytes_data[1]
        if a1 & 0x8000 == 0x8000 :
            b = 0xFFFF - a1
            return b
        else:
            return a1

    def shortTobytes(self,short_data):
        """
        转为字节，先返回高8位，再返回低8位
        """
        if short_data >= 0 :
            b_L = short_data & 0xFF
            b_H = short_data >> 8
        else:
            short_data = 0xFFFF - short_data
            b_L = short_data & 0xFF
            b_H = short_data >> 8
        return b_H,b_L

    def data_cul(self):



        return 0

    def data_BCC(self,list_bytes):
        check_id = None
        for i in range(len(list_bytes)):
            if i :
                check_id ^=list_bytes[i]
            else:
                check_id = list_bytes[i]^0
        return check_id

    def data_CRC(self,list_bytes):
        check_id = None



class network(object):
    def __init__(self):
        global list_Q
        global list_states

        self.id_addr = [('192.168.100.101',8001),('192.168.100.101',8001),('192.168.100.102',8001),('192.168.100.103',8001),('192.168.100.104',8001),('192.168.100.105',8001)]
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        host_address = ('192.168.100.101',8000)
        self.udp_socket.bind(host_address)

        self.net_sendThread = threading.Thread(target=self.netsendThread, args=())
        self.net_sendThread.start()
        self.net_recvThread = threading.Thread(target=self.netrecvThread, args=())
        self.net_recvThread.start()
    def netsendThread(self):
        while True:

            x = list_Q.get()
            y = list_states.get()
            self.udp_socket.sendto(x, self.id_addr[0])
            #self.udp_socket.sendto(y,self.id_addr[0])
            print(type(x))
            print(x)

    def netrecvThread(self):


        return 0

class control(object):

    def __init__(self):

        global list_states

        self.V_pid = [3,0,0] #速度pid参数，kp ki kd
        self.R_pid = [5,0,0] #方向pid参数，kp ki kd



    def speed_PID_contrul(self,V_input):
        V_output = V_input
        v_error = V_input
        return V_output

    def angle_PID_contrul(self,R_input):
        R_output = R_input

        return R_output

    def LOS(self):

        return 0



if __name__ == '__main__':


    agv_1 = AGV()

    #network_1 = network()
