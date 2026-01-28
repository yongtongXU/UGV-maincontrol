import threading
from queue import Queue
import serial
import serial.tools.list_ports
import datetime
from time import strftime
import time

class Serial_COM(object):
    def __init__(self,com,bound):
        
        # 数据有效标识
        self.dataTpye = 0
        # 看门狗标识
        self.dog_num = 0
        # 共享的信息
        self.get_message = None

        self.message_queue = Queue(10)

        self.RUN_flag=True
        self.AGV_serial = serial.Serial(com, bound, timeout=1)

        # 读取数据
        self.revThread = threading.Thread(target=self.getdataThread, args=())
        self.revThread.start()
        # 数据看门狗
        self.dog_thread = threading.Thread(target=self.dogLoop,args=())
        self.dog_thread.start()

        self.send_data_demo = b'\x7B\x00\x00\x00\x01\x00\x00\x00\x00\xA1\x7D'
        self.rev_data_demo = b'\x7B\x00\x01\x01\x00\x01\x00\x00\xFE\x96\xFD\xCE\x40\x80\xFF\xFB\x00\x07\x00\x01\x58\x38\x83\x7D'


        self.data_head = '7b'
        self.head_check_data = bytes()


    def getdataThread(self):

        while self.RUN_flag:
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

                    # 共享的信息
                    self.get_message = self.AGV_list_state
                    self.dog_num = 0
                    # print(self.get_message)
                    # 清空队列
                    self.checkQueue(self.message_queue)
                    # 数据放入队列
                    self.message_queue.put(self.AGV_list_state)
 
    def data_send(self,mes):
        data_send_mes_flag = self.AGV_serial.write(mes)
        return data_send_mes_flag
    
    def checkQueue(self, one_queue):
        for i in range(one_queue.qsize()):
            if one_queue.qsize() == 0:
                return
            one_queue.get()
        

    def dogLoop(self):
        '''
        接受数据看门狗
        '''
        dog_max = 2
        while True:
            # 喂狗
            self.dog_num += 1
            if self.dog_num > dog_max:
                # 清空共享变量
                self.get_message = None
                # 清空消息队列
                self.checkQueue(self.message_queue)
                # 防止dog_num过大
                self.dog_num = dog_max
            # 计数周期
            time.sleep(1)

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
    
    def data_BCC(self,list_bytes):
        check_id = None
        for i in range(len(list_bytes)):
            if i :
                check_id ^=list_bytes[i]
            else:
                check_id = list_bytes[i]^0
        return check_id
    
    def xxx(self):
        print(self.get_message)

    


if __name__ == '__main__':
    
    # id_addr = [('192.168.100.101', 8001), ('192.168.100.101', 8001), ('192.168.100.102', 8001),('192.168.100.103', 8001), ('192.168.100.104', 8001), ('192.168.100.105', 8001)]
   
    # print(net_01.get_ip_port())

    ser_01 = Serial_COM('com1',9600)
    while True:
        ser_01.xxx()
        time.sleep(0.5)
    