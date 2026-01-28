import datetime
import time
from time import strftime
import sys
from commuication import *
from loguru import logger
import handle
from queue import Queue
import threading
import AGV_UI
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import *
import control
import serial
import serial.tools.list_ports
import BDins
import ActionContorller
import multiprocessing

flag_Q = Queue(3)


class AGV_MA(object):

    def __init__(self):

        # self.handle = handle.handle()
        # self.handle_Thread = threading.Thread(target=self.handle.get_value(), args=())
        # self.handle_Thread.start()

        

        self.RUN_flag = True
        self.Serial_AGV_flag = False
        self.Serial_BD_flag = False
        self.Network = False
        self.Servo = False
        self.Monter_Left = False
        self.Monter_Right = False

        self.global_state = [False,False,False,False,False,False,False,False,False]#系统各个模块的开关

        self.usb_list = list(serial.tools.list_ports.comports())

        # 串口接收
        self.AGV_serial = Serial_COM('com1',9600)
        # self.BD_serial = BDins.Serial_BD('com4')

        # 运动控制
        self.ActionControllerClass = ActionContorller.ActionControllerClass()
        self.ActionControllerClass.pose_queue = self.AGV_serial.message_queue
        # self.ActionControllerClass.BD_queue = self.BD_serial.BD_message_queue

        self.UI_Thread = threading.Thread(target=self.UI_window, args=())
        self.UI_Thread.start()
        time.sleep(1)
        self.te_Thread = threading.Thread(target=self.log_m, args=())
        self.te_Thread.start()

        self.flash_Thread = threading.Thread(target=self.global_flash, args=())
        self.flash_Thread.start()

        self.AGV_mes_flash_Thread = threading.Thread(target=self.agvMesFlashLoop, args=())
        self.AGV_mes_flash_Thread.start()




    def UI_window(self):
        self.app = QApplication(sys.argv)
        self.s1 = AGV_UI.States()

        self.s1.runsignal.connect(self.stop_flag)#
        self.s1.commuication_signal.connect(self.commuication)
        self.s1.control_signal.connect(self.control)
        # 刷新AGV界面
        self.s1.refresh_AGV_signal.connect(self.refreshUI)
        # 刷新组合导航界面
        # self.s1.refresh_BD_signal.connect(self.BD_mes_flash)

        self.s1.show()
        self.app.exec_()

    def PID_control(self):
        self.A_pid = control.DeltaPID(100,0,1,0) #航向控制PID
        self.V_pid = control.DeltaPID(100,0,1,1) #航速控制PID


    def global_flash(self):

        while self.RUN_flag:
            time.sleep(1)
            self.global_state[0] = self.RUN_flag
            self.global_state[1] = self.Serial_AGV_flag
            self.global_state[2] = self.Serial_BD_flag
            self.global_state[3] = self.Network
            self.global_state[4] = self.Servo
            self.global_state[5] = self.Monter_Left
            self.global_state[6] = self.Monter_Right
            self.global_state[7] = False
            self.global_state[8] = False
            logger.info(self.global_state)
            

    def agvMesFlashLoop(self):
        """
        刷新界面信号
        """
        while self.RUN_flag:
            self.s1.refresh_AGV_signal.emit(True)
            self.s1.refresh_BD_signal.emit(True)
            time.sleep(0.1)
       
    def refreshUI(self, refreshStatus):
            AGV_serial_message = self.AGV_serial.get_message
            if self.AGV_serial.get_message is not None:
                
                self.s1.AGV_speed_x_text.setText(str(round(AGV_serial_message[1],2)))
                self.s1.AGV_speed_x_text.setAlignment(Qt.AlignCenter)

                self.s1.AGV_speed_y_text.setText(str(round(AGV_serial_message[2],2)))
                self.s1.AGV_speed_y_text.setAlignment(Qt.AlignCenter)

                self.s1.AGV_speed_z_text.setText(str(round(AGV_serial_message[3],2)))
                self.s1.AGV_speed_z_text.setAlignment(Qt.AlignCenter)

                self.s1.AGV_acc_x_text.setText(str(round(AGV_serial_message[4],2)))
                self.s1.AGV_acc_x_text.setAlignment(Qt.AlignCenter)

                self.s1.AGV_acc_y_text.setText(str(round(AGV_serial_message[5],2)))
                self.s1.AGV_acc_y_text.setAlignment(Qt.AlignCenter)

                self.s1.AGV_acc_z_text.setText(str(round(AGV_serial_message[6],2)))
                self.s1.AGV_acc_z_text.setAlignment(Qt.AlignCenter)

                self.s1.AGV_ang_x_text.setText(str(round(AGV_serial_message[7],2)))
                self.s1.AGV_ang_x_text.setAlignment(Qt.AlignCenter)

                self.s1.AGV_ang_y_text.setText(str(round(AGV_serial_message[8],2)))
                self.s1.AGV_ang_y_text.setAlignment(Qt.AlignCenter)

                self.s1.AGV_ang_z_text.setText(str(round(AGV_serial_message[9],2)))
                self.s1.AGV_ang_z_text.setAlignment(Qt.AlignCenter) 

                self.s1.state_battery_text.setText(str(AGV_serial_message[10]))
                self.s1.state_battery_text.setAlignment(Qt.AlignCenter)   

                self.s1.TxtBrowser_01.append(str(AGV_serial_message))   

    def BD_mes_flash(self, refreshStatus):

        BD_serial_message = self.BD_serial.BD_str
        BD_serial_list = self.BD_serial.BD_list
        if BD_serial_message is not None:
            self.s1.TxtBrowser_02.append(BD_serial_message)

            '''
            刷新UI上的组合导航信息
            self.BD_list = [protait_speed, landscape_speed, self.sky_speed, 0 1 2
                  self.rotate_speed_plus_x, self.rotate_speed_minus_y, 3 4
                  self.rotate_speed_plus_z, 5
                  self.pitch_angle, self.roll_angle, self.yaw_angle, 6 7 8
                  self.latitude, self.longitude, 9 10 
                  self.acceleration_minus_y, self.acceleration_plus_x, 11 12
                  self.acceleration_plus_z, 13
                  coursett,time_str] 14 15
            '''
            self.s1.AGV_BD_speed_x_text.setText(str(BD_serial_list[3]))
            self.s1.AGV_BD_speed_x_text.setAlignment(Qt.AlignCenter)

            self.s1.AGV_BD_speed_y_text.setText(str(BD_serial_list[4]))
            self.s1.AGV_BD_speed_y_text.setAlignment(Qt.AlignCenter)
            
            self.s1.AGV_BD_speed_z_text.setText(str(BD_serial_list[5]))
            self.s1.AGV_BD_speed_z_text.setAlignment(Qt.AlignCenter)

            self.s1.AGV_BD_acc_x_text.setText(str(BD_serial_list[12]))
            self.s1.AGV_BD_acc_x_text.setAlignment(Qt.AlignCenter)
            
            self.s1.AGV_BD_acc_y_text.setText(str(BD_serial_list[11]))
            self.s1.AGV_BD_acc_y_text.setAlignment(Qt.AlignCenter)

            self.s1.AGV_BD_acc_z_text.setText(str(BD_serial_list[13]))
            self.s1.AGV_BD_acc_z_text.setAlignment(Qt.AlignCenter)

            self.s1.AGV_BD_ang_x_text.setText(str(BD_serial_list[6]))
            self.s1.AGV_BD_ang_x_text.setAlignment(Qt.AlignCenter)

            self.s1.AGV_BD_ang_y_text.setText(str(BD_serial_list[7]))
            self.s1.AGV_BD_ang_y_text.setAlignment(Qt.AlignCenter)

            self.s1.AGV_BD_ang_z_text.setText(str(BD_serial_list[8]))
            self.s1.AGV_BD_ang_z_text.setAlignment(Qt.AlignCenter)

            self.s1.AGV_BD_time_text.setText(str(BD_serial_list[15]))
            self.s1.AGV_BD_time_text.setAlignment(Qt.AlignCenter)

            self.s1.AGV_BD_lon_text.setText(str(BD_serial_list[10]))
            self.s1.AGV_BD_lon_text.setAlignment(Qt.AlignCenter)

            self.s1.AGV_BD_lat_text.setText(str(BD_serial_list[9]))
            self.s1.AGV_BD_lat_text.setAlignment(Qt.AlignCenter)

            self.s1.AGV_BD_roll_text.setText(str(BD_serial_list[7]))
            self.s1.AGV_BD_roll_text.setAlignment(Qt.AlignCenter)

            self.s1.AGV_BD_yaw_text.setText(str(BD_serial_list[8]))
            self.s1.AGV_BD_yaw_text.setAlignment(Qt.AlignCenter)

            self.s1.AGV_BD_pitch_text.setText(str(BD_serial_list[6]))
            self.s1.AGV_BD_pitch_text.setAlignment(Qt.AlignCenter)

            self.s1.AGV_BD_a_x_text.setText(str(BD_serial_list[6]))
            self.s1.AGV_BD_a_x_text.setAlignment(Qt.AlignCenter)

            self.s1.AGV_BD_a_y_text.setText(str(BD_serial_list[7]))
            self.s1.AGV_BD_a_y_text.setAlignment(Qt.AlignCenter)

            self.s1.AGV_BD_a_z_text.setText(str(BD_serial_list[8]))
            self.s1.AGV_BD_a_z_text.setAlignment(Qt.AlignCenter)

        return 0

    def commuication(self,comm):
        if comm == 0:
            print("停止发送")
        elif comm == 1:
            print("手动发送",self.s1.move_buff)
            self.AGV_serial.data_send(self.s1.move_buff)
        elif comm == 2:
            print("自动发送",self.s1.move_buff)
            self.AGV_serial.data_send(self.s1.move_buff)



    def control(self,con):
        if con == 1:
            print("遥控模式")#手动输入舵角、推进器转速（或者电压）


        elif con == 2:
            print("智能模式")#规划路径，自主航行

        elif con == 3:
            print("自动模式")#手动输入航速航向
            # 
        elif con == 4:
            print("手柄模式")#XBOX手柄控制



    
    def stop_flag(self):

        print("程序结束")
        self.RUN_flag = False
        self.AGV_serial.RUN_flag = False
        self.ActionControllerClass.RunFlag = False
        self.BD_serial.RUN_FLAG = False

    def log_m(self):

        while self.RUN_flag:
            # logger.info('--AGV主程序----占位--')
            print(self.RUN_flag)
            time.sleep(1)





if __name__ == '__main__':
    ss = AGV_MA()

