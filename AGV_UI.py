import sys
import os
import folium
import threading
import math
import handle
import datetime
import time
from time import strftime
from configparser import ConfigParser
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngine import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtQml import *
from pathlib import *
import sys
import makeJS
import DataChange


class States(QMainWindow):
    runsignal = pyqtSignal(bool)#主程序运行标识符
    control_signal = pyqtSignal(object)#控制信号，发送标识符
    commuication_signal = pyqtSignal(object)#通信信号，发送标识符
    control_value_signal = pyqtSignal(object)#告诉主程序，控制参数改变
    UDP_signal = pyqtSignal(object)
    time_flash_signal = pyqtSignal(object)
    map_waypoint_signal = pyqtSignal(object)#地图标点
    get_location_signal = pyqtSignal(object)
    Serial_signal = pyqtSignal(object)#串口信号
    # 刷新AGV界面
    refresh_AGV_signal = pyqtSignal(bool)
    # 刷新组合导航界面
    refresh_BD_signal = pyqtSignal(bool)

    def __init__(self, *args, **kwargs):

        super(States, self).__init__(*args, **kwargs)

        
        self.setFixedSize(1650, 900)
        self.move(300, 300)
        self.setWindowTitle('AGV总控')
        self.setWindowIcon(QIcon("./res/AGV.ico"))

        self.RUN_flag=True

        self.ctrl_model_flag = 0
        

        self.gaode_map_view_label = QWebEngineView(self)
        self.gaode_map_view_label.move(520,50)
        self.gaode_map_view_label.resize(670,580)
        self.gaode_map_wab_path = "file:\\" + os.getcwd() + "\\res\\amap.html"
        self.gaode_map_wab_path = self.gaode_map_wab_path.replace('\\', '/')
        self.gaode_map_view_label.load(QUrl(self.gaode_map_wab_path))
        print(self.gaode_map_wab_path)
        #地图预留

        self.marker_list = []
        self.marker_path = []
        self.marker_path_plan = []

        self.ip_flag = 0
        self.ip_address_list = ['','','','','','','']
        self.control_value_list = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.add_lat_lon = [0,0]
        self.config_rw()

        self.move_value_input_list = [0.0,0.0] # 运动控制输入量 期望艏向、期望速度
        self.force_value_input_list = [0.0,0.0] # 期望舵角、推进器
        self.action_value_out_list = [0,0,0] #实际艏向 速度 舵角
        self.action_value_error_list = [0,0,0] #偏差：艏向 速度 舵角

        self.time_open_str = datetime.datetime.now()
        self.time_now_str = datetime.datetime.now()
        self.time_least_str = self.time_now_str - self.time_open_str

        print(self.time_open_str.strftime('%Y-%m-%d %H:%M:%S.%f'))

        test_ser_list = ['请选择','COM1','COM2','COM3','COM4']
        self.AGV_BD_text_box()
        self.AGV_UI_lable()
        self.AGV_UI_text_box()
        self.AGV_UI_button()
        self.AGV_UI_checkbox()
        self.communication_lable(test_ser_list)
        self.control_mode_UI()
        self.control_value()
        # self.map_bg()
        self.mes_AGV()
        self.map_sss()
        self.order_box()
        self.ip_select()
        self.global_state()
        self.order_control()
        self.time_box()
        

        get_dic = {}
        self.get_location_signal.connect(self.refreshShow)
        self.get_location_signal.emit(get_dic)

        self.time_flash_Thread = threading.Thread(target=self.time_flash, args=())
        self.time_flash_Thread.start()

        self.Get_Touch_Thread = threading.Thread(target=self.Get_Touch, args=())
        self.Get_Touch_Thread.start()

        self.roboFlash_Thread = threading.Thread(target=self.roboFlash, args=())
        self.roboFlash_Thread.start()

        

    def map_sss(self):
        self.map_waypoint_zero_btn = QPushButton(self)
        self.map_waypoint_zero_btn.setGeometry(1000,680,80,30) 
        self.map_waypoint_zero_btn.setText("标点清除")
        self.map_waypoint_zero_btn.clicked.connect(lambda a:self.clearMarker())

        self.map_waypoint_back_btn = QPushButton(self)
        self.map_waypoint_back_btn.setGeometry(900,680,80,30)
        self.map_waypoint_back_btn.setText("撤销标点")
        self.map_waypoint_back_btn.clicked.connect(lambda a:self.delMarker())

        self.map_waypoint_way_line_btn = QPushButton(self)
        self.map_waypoint_way_line_btn.setGeometry(1100,680,80,30)
        self.map_waypoint_way_line_btn.setText("顺序轨迹")
        self.map_waypoint_way_line_btn.clicked.connect(lambda a:self.PathFromMarkers())

        self.map_waypoint_way_path_btn = QPushButton(self)
        self.map_waypoint_way_path_btn.setGeometry(800,680,80,30)
        self.map_waypoint_way_path_btn.setText("路径规划")
        self.map_waypoint_way_path_btn.clicked.connect(lambda a:self.PathPlan())

    def config_rw(self):
        self.cf = ConfigParser()
        self.cf.read('config.ini')
        for i in range(len(self.cf.items('control value'))):
            self.control_value_list[i] = self.cf.items('control value')[i][1]

        for i in range(len(self.cf.items('IP address'))):
            self.ip_address_list[i] = self.cf.items('IP address')[i][1]


        self.ip_flag = self.cf.items('IP FLAG')[0][1]

        self.add_lat_lon[0] = self.cf.items('Address LL')[0][1]
        self.add_lat_lon[1] = self.cf.items('Address LL')[1][1]
        print(self.add_lat_lon)

    def ip_select(self):
        self.self_ip_flag = QLineEdit(self)
        self.self_ip_flag.move(0,0)
        self.self_ip_flag.resize(50,50)
        self.self_ip_flag.setText(str(self.ip_flag))
        self.self_ip_flag.setStyleSheet('''font-size:24pt;color:red;font-family:SongTi''')

    def AGV_UI_checkbox(self):
        
        self.btn_01 = QCheckBox('显示AGV上传信息', self)
        self.btn_01.move(380, 80)
        self.btn_01.resize(120, 20)
        self.btn_01.stateChanged.connect(lambda state: self.mes_01_show())

    def AGV_UI_lable(self):

        self.state_speed_x = QLabel(self)
        self.state_speed_x.move(1200, 100)
        self.state_speed_x.resize(120, 30)
        self.state_speed_x.setText("X速度(mm/s):")
        self.state_speed_x.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.state_speed_x.setAlignment(Qt.AlignCenter)

        self.state_speed_y = QLabel(self)
        self.state_speed_y.move(1400, 100)
        self.state_speed_y.resize(120, 30)
        self.state_speed_y.setText("Y速度(mm/s):")
        self.state_speed_y.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.state_speed_y.setAlignment(Qt.AlignCenter)

        self.state_speed_z = QLabel(self)
        self.state_speed_z.move(1200, 150)
        self.state_speed_z.resize(120, 30)
        self.state_speed_z.setText("Z速度(mm/s):")
        self.state_speed_z.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.state_speed_z.setAlignment(Qt.AlignCenter)

        self.state_acc_x = QLabel(self)
        self.state_acc_x.move(1400, 150)
        self.state_acc_x.resize(120, 30)
        self.state_acc_x.setText("X加(m/s^2):")
        self.state_acc_x.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.state_acc_x.setAlignment(Qt.AlignCenter)

        self.state_acc_y = QLabel(self)
        self.state_acc_y.move(1200, 200)
        self.state_acc_y.resize(120, 30)
        self.state_acc_y.setText("Y加(m/s^2):")
        self.state_acc_y.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.state_acc_y.setAlignment(Qt.AlignCenter)

        self.state_acc_z = QLabel(self)
        self.state_acc_z.move(1400, 200)
        self.state_acc_z.resize(120, 30)
        self.state_acc_z.setText("Z加(m/s^2):")
        self.state_acc_z.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.state_acc_z.setAlignment(Qt.AlignCenter)

        self.state_ang_x = QLabel(self)
        self.state_ang_x.move(1200, 250)
        self.state_ang_x.resize(120, 30)
        self.state_ang_x.setText("X(rad/s^2):")
        self.state_ang_x.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.state_ang_x.setAlignment(Qt.AlignCenter)

        self.state_ang_y = QLabel(self)
        self.state_ang_y.move(1400, 250)
        self.state_ang_y.resize(120, 30)
        self.state_ang_y.setText("Y(rad/s^2):")
        self.state_ang_y.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.state_ang_y.setAlignment(Qt.AlignCenter)

        self.state_ang_z = QLabel(self)
        self.state_ang_z.move(1200, 300)
        self.state_ang_z.resize(120, 30)
        self.state_ang_z.setText("Z(rad/s^2):")
        self.state_ang_z.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.state_ang_z.setAlignment(Qt.AlignCenter)

        self.state_time = QLabel(self)
        self.state_time.move(1400, 300)
        self.state_time.resize(120, 30)
        self.state_time.setText("时间(H:M:S):")
        self.state_time.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.state_time.setAlignment(Qt.AlignCenter)

        self.state_lon = QLabel(self)
        self.state_lon.move(1200, 350)
        self.state_lon.resize(100, 30)
        self.state_lon.setText("经度:")
        self.state_lon.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.state_lon.setAlignment(Qt.AlignCenter)

        self.state_lat = QLabel(self)
        self.state_lat.move(1400, 350)
        self.state_lat.resize(100, 30)
        self.state_lat.setText("纬度:")
        self.state_lat.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.state_lat.setAlignment(Qt.AlignCenter)

        self.state_roll = QLabel(self)
        self.state_roll.move(1200, 400)
        self.state_roll.resize(100, 30)
        self.state_roll.setText("横滚角:")
        self.state_roll.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.state_roll.setAlignment(Qt.AlignCenter)

        self.state_yaw = QLabel(self)
        self.state_yaw.move(1400, 400)
        self.state_yaw.resize(100, 30)
        self.state_yaw.setText("偏航角:")
        self.state_yaw.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.state_yaw.setAlignment(Qt.AlignCenter)

        self.state_pitch = QLabel(self)
        self.state_pitch.move(1200, 450)
        self.state_pitch.resize(100, 30)
        self.state_pitch.setText("俯仰角:")
        self.state_pitch.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.state_pitch.setAlignment(Qt.AlignCenter)

        self.state_a_x = QLabel(self)
        self.state_a_x.move(1400, 450)
        self.state_a_x.resize(100, 30)
        self.state_a_x.setText("X(°/s):")
        self.state_a_x.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.state_a_x.setAlignment(Qt.AlignCenter)

        self.state_a_y = QLabel(self)
        self.state_a_y.move(1200, 500)
        self.state_a_y.resize(100, 30)
        self.state_a_y.setText("-Y(°/s):")
        self.state_a_y.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.state_a_y.setAlignment(Qt.AlignCenter)

        self.state_a_z = QLabel(self)
        self.state_a_z.move(1400, 500)
        self.state_a_z.resize(100, 30)
        self.state_a_z.setText("Z(°/s):")
        self.state_a_z.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.state_a_z.setAlignment(Qt.AlignCenter)

    def AGV_UI_text_box(self):

        self.TxtBrowser_01 = QTextBrowser(self)
        self.TxtBrowser_01.setPlainText("原始信息:来自下位机")
        self.TxtBrowser_01.move(25, 750)
        self.TxtBrowser_01.resize(350, 100)

        self.TxtBrowser_02 = QTextBrowser(self)
        self.TxtBrowser_02.setPlainText("原始信息:来自组合导航")
        self.TxtBrowser_02.move(425, 750)
        self.TxtBrowser_02.resize(350, 100)

        self.TxtBrowser_03 = QTextBrowser(self)
        self.TxtBrowser_03.setPlainText("原始信息:来自其他无人艇")
        self.TxtBrowser_03.move(825, 750)
        self.TxtBrowser_03.resize(350, 100)

        self.TxtBrowser_04 = QTextBrowser(self)
        self.TxtBrowser_04.setPlainText("原始信息:来自岸基")
        self.TxtBrowser_04.move(1225, 750)
        self.TxtBrowser_04.resize(350, 100)

        self.TxtBrowser_list = [self.TxtBrowser_01,self.TxtBrowser_02,self.TxtBrowser_03,self.TxtBrowser_04]

        self.lab_1 = QLabel(self)
        self.lab_1.move(25, 850)
        self.lab_1.resize(350, 50)
        self.lab_1.setText("原始信息:来自下位机")
        self.lab_1.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.lab_1.setAlignment(Qt.AlignCenter)

        self.lab_2 = QLabel(self)
        self.lab_2.move(425, 850)
        self.lab_2.resize(350, 50)
        self.lab_2.setText("原始信息:来自组合导航")
        self.lab_2.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.lab_2.setAlignment(Qt.AlignCenter)

        self.lab_3 = QLabel(self)
        self.lab_3.move(825, 850)
        self.lab_3.resize(350, 50)
        self.lab_3.setText("原始信息:来自其他无人艇")
        self.lab_3.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.lab_3.setAlignment(Qt.AlignCenter)

        self.lab_4 = QLabel(self)
        self.lab_4.move(1225, 850)
        self.lab_4.resize(350, 50)
        self.lab_4.setText("原始信息:来自岸基")
        self.lab_4.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.lab_4.setAlignment(Qt.AlignCenter)

    def AGV_BD_text_box(self):

        self.AGV_BD_speed_x_text = QTextBrowser(self)
        self.AGV_BD_speed_x_text.move(1320, 100)
        self.AGV_BD_speed_x_text.resize(80, 30)
        self.AGV_BD_speed_x_text.setText("00.00")
        self.AGV_BD_speed_x_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_BD_speed_x_text.setAlignment(Qt.AlignCenter)

        self.AGV_BD_speed_y_text = QTextBrowser(self)
        self.AGV_BD_speed_y_text.move(1520, 100)
        self.AGV_BD_speed_y_text.resize(80, 30)
        self.AGV_BD_speed_y_text.setText("00.00")
        self.AGV_BD_speed_y_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_BD_speed_y_text.setAlignment(Qt.AlignCenter)

        self.AGV_BD_speed_z_text = QTextBrowser(self)
        self.AGV_BD_speed_z_text.move(1320, 150)
        self.AGV_BD_speed_z_text.resize(80, 30)
        self.AGV_BD_speed_z_text.setText("00.00")
        self.AGV_BD_speed_z_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_BD_speed_z_text.setAlignment(Qt.AlignCenter)

        self.AGV_BD_acc_x_text = QTextBrowser(self)
        self.AGV_BD_acc_x_text.move(1520, 150)
        self.AGV_BD_acc_x_text.resize(80, 30)
        self.AGV_BD_acc_x_text.setText("00.00")
        self.AGV_BD_acc_x_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_BD_acc_x_text.setAlignment(Qt.AlignCenter)

        self.AGV_BD_acc_y_text = QTextBrowser(self)
        self.AGV_BD_acc_y_text.move(1320, 200)
        self.AGV_BD_acc_y_text.resize(80, 30)
        self.AGV_BD_acc_y_text.setText("00.00")
        self.AGV_BD_acc_y_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_BD_acc_y_text.setAlignment(Qt.AlignCenter)

        self.AGV_BD_acc_z_text = QTextBrowser(self)
        self.AGV_BD_acc_z_text.move(1520, 200)
        self.AGV_BD_acc_z_text.resize(80, 30)
        self.AGV_BD_acc_z_text.setText("00.00")
        self.AGV_BD_acc_z_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_BD_acc_z_text.setAlignment(Qt.AlignCenter)

        self.AGV_BD_ang_x_text = QTextBrowser(self)
        self.AGV_BD_ang_x_text.move(1320, 250)
        self.AGV_BD_ang_x_text.resize(80, 30)
        self.AGV_BD_ang_x_text.setText("00.00")
        self.AGV_BD_ang_x_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_BD_ang_x_text.setAlignment(Qt.AlignCenter)

        self.AGV_BD_ang_y_text = QTextBrowser(self)
        self.AGV_BD_ang_y_text.move(1520, 250)
        self.AGV_BD_ang_y_text.resize(80, 30)
        self.AGV_BD_ang_y_text.setText("00.00")
        self.AGV_BD_ang_y_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_BD_ang_y_text.setAlignment(Qt.AlignCenter)

        self.AGV_BD_ang_z_text = QTextBrowser(self)
        self.AGV_BD_ang_z_text.move(1320, 300)
        self.AGV_BD_ang_z_text.resize(80, 30)
        self.AGV_BD_ang_z_text.setText("00.00")
        self.AGV_BD_ang_z_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_BD_ang_z_text.setAlignment(Qt.AlignCenter)

        self.AGV_BD_time_text = QTextBrowser(self)
        self.AGV_BD_time_text.move(1520, 300)
        self.AGV_BD_time_text.resize(80, 30)
        self.AGV_BD_time_text.setText("00:00:00")
        self.AGV_BD_time_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_BD_time_text.setAlignment(Qt.AlignCenter)

        self.AGV_BD_lon_text = QTextBrowser(self)
        self.AGV_BD_lon_text.move(1320, 350)
        self.AGV_BD_lon_text.resize(80, 30)
        self.AGV_BD_lon_text.setText("00.00")
        self.AGV_BD_lon_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_BD_lon_text.setAlignment(Qt.AlignCenter)

        self.AGV_BD_lat_text = QTextBrowser(self)
        self.AGV_BD_lat_text.move(1520, 350)
        self.AGV_BD_lat_text.resize(80, 30)
        self.AGV_BD_lat_text.setText("00.00")
        self.AGV_BD_lat_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_BD_lat_text.setAlignment(Qt.AlignCenter)

        self.AGV_BD_roll_text = QTextBrowser(self)
        self.AGV_BD_roll_text.move(1320, 400)
        self.AGV_BD_roll_text.resize(80, 30)
        self.AGV_BD_roll_text.setText("00.00")
        self.AGV_BD_roll_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_BD_roll_text.setAlignment(Qt.AlignCenter)

        self.AGV_BD_yaw_text = QTextBrowser(self)
        self.AGV_BD_yaw_text.move(1520, 400)
        self.AGV_BD_yaw_text.resize(80, 30)
        self.AGV_BD_yaw_text.setText("00.00")
        self.AGV_BD_yaw_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_BD_yaw_text.setAlignment(Qt.AlignCenter)

        self.AGV_BD_pitch_text = QTextBrowser(self)
        self.AGV_BD_pitch_text.move(1320, 450)
        self.AGV_BD_pitch_text.resize(80, 30)
        self.AGV_BD_pitch_text.setText("00.00")
        self.AGV_BD_pitch_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_BD_pitch_text.setAlignment(Qt.AlignCenter)

        self.AGV_BD_a_x_text = QTextBrowser(self)
        self.AGV_BD_a_x_text.move(1520, 450)
        self.AGV_BD_a_x_text.resize(80, 30)
        self.AGV_BD_a_x_text.setText("00.00")
        self.AGV_BD_a_x_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_BD_a_x_text.setAlignment(Qt.AlignCenter)

        self.AGV_BD_a_y_text = QTextBrowser(self)
        self.AGV_BD_a_y_text.move(1320, 500)
        self.AGV_BD_a_y_text.resize(80, 30)
        self.AGV_BD_a_y_text.setText("00.00")
        self.AGV_BD_a_y_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_BD_a_y_text.setAlignment(Qt.AlignCenter)

        self.AGV_BD_a_z_text = QTextBrowser(self)
        self.AGV_BD_a_z_text.move(1520, 500)
        self.AGV_BD_a_z_text.resize(80, 30)
        self.AGV_BD_a_z_text.setText("00.00")
        self.AGV_BD_a_z_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_BD_a_z_text.setAlignment(Qt.AlignCenter)

    def communication_lable(self,serial_list):

        self.self_net_lable = QLabel(self)
        self.self_net_lable.move(1200, 15)
        self.self_net_lable.resize(120, 30)
        self.self_net_lable.setText("当前地址/端口:")
        self.self_net_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.self_net_lable.setAlignment(Qt.AlignCenter)

        self.serial_lable = QLabel(self)
        self.serial_lable.move(1200, 50)
        self.serial_lable.resize(120, 30)
        self.serial_lable.setText("组合导航串口:")
        self.serial_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.serial_lable.setAlignment(Qt.AlignCenter)

        self.AGV_stm32_lable = QLabel(self)
        self.AGV_stm32_lable.move(1400, 50)
        self.AGV_stm32_lable.resize(120, 30)
        self.AGV_stm32_lable.setText("小车底盘串口:")
        self.AGV_stm32_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.AGV_stm32_lable.setAlignment(Qt.AlignCenter)

        self.serial_list_box = QComboBox(self)
        self.serial_list_box.move(1520,50)
        self.serial_list_box.resize(80,30)
        self.serial_list_box.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.serial_list_box.addItems(serial_list)
        self.serial_list_box.currentIndexChanged.connect(lambda state:print(state))

        self.BD_list_box = QComboBox(self)
        self.BD_list_box.move(1320,50)
        self.BD_list_box.resize(80,30)
        self.BD_list_box.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.BD_list_box.addItems(serial_list)
        self.BD_list_box.currentIndexChanged.connect(lambda state:print(state))

        self.IP_text = QTextBrowser(self)
        self.IP_text.move(1320, 15)
        self.IP_text.resize(170, 30)
        self.IP_text.setText(str(self.ip_address_list[0]))
        self.IP_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.IP_text.setAlignment(Qt.AlignCenter)

        self.IP_port_text = QTextBrowser(self)
        self.IP_port_text.move(1520, 15)
        self.IP_port_text.resize(80, 30)
        self.IP_port_text.setText("0000")
        self.IP_port_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.IP_port_text.setAlignment(Qt.AlignCenter)

    def control_mode_UI(self):

        self.control_mode_lable = QLabel(self)
        self.control_mode_lable.move(200, 300)
        self.control_mode_lable.resize(120, 30)
        self.control_mode_lable.setText("控制模式")
        self.control_mode_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.control_mode_lable.setAlignment(Qt.AlignCenter)

        self.control_mode_IR_box = QRadioButton(self)
        self.control_mode_IR_box.move(70, 350)
        self.control_mode_IR_box.resize(120, 30)
        self.control_mode_IR_box.setText("遥控")
        self.control_mode_IR_box.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.control_mode_IR_box.clicked.connect(lambda a:self.contrul_model(1))

        self.control_mode_AI_box = QRadioButton(self)
        self.control_mode_AI_box.move(170, 350)
        self.control_mode_AI_box.resize(120, 30)
        self.control_mode_AI_box.setText("智能")
        self.control_mode_AI_box.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.control_mode_AI_box.clicked.connect(lambda a: self.contrul_model(2))

        self.control_mode_auto_box = QRadioButton(self)
        self.control_mode_auto_box.move(270, 350)
        self.control_mode_auto_box.resize(120, 30)
        self.control_mode_auto_box.setText("自动")
        self.control_mode_auto_box.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.control_mode_auto_box.clicked.connect(lambda a: self.contrul_model(3))

        self.control_mode_HA_box = QRadioButton(self)
        self.control_mode_HA_box.move(370, 350)
        self.control_mode_HA_box.resize(120, 30)
        #self.control_mode_HA_box.setChecked(True)
        self.control_mode_HA_box.setText("手柄")
        self.control_mode_HA_box.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.control_mode_HA_box.clicked.connect(lambda a:self.contrul_model(4))

    def control_value(self):

        self.control_value_lable = QLabel(self)
        self.control_value_lable.move(100, 150)
        self.control_value_lable.resize(120, 30)
        self.control_value_lable.setText("运动控制参数")
        self.control_value_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.control_value_lable.setAlignment(Qt.AlignCenter)

        self.control_value_btn = QPushButton(self)
        self.control_value_btn.move(300, 150)
        self.control_value_btn.resize(120, 30)
        self.control_value_btn.setText("控制参数更新")
        self.control_value_btn.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.control_value_btn.clicked.connect(lambda :self.get_control_value())

        self.control_value_A_P_lable = QLabel(self)
        self.control_value_A_P_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.control_value_A_P_lable.setAlignment(Qt.AlignCenter)
        self.control_value_A_P_lable.move(100, 200)
        self.control_value_A_P_lable.resize(60, 30)
        self.control_value_A_P_lable.setText("艏向P：")

        self.control_value_A_I_lable = QLabel(self)
        self.control_value_A_I_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.control_value_A_I_lable.setAlignment(Qt.AlignCenter)
        self.control_value_A_I_lable.move(200, 200)
        self.control_value_A_I_lable.resize(60, 30)
        self.control_value_A_I_lable.setText("艏向I：")

        self.control_value_A_D_lable = QLabel(self)
        self.control_value_A_D_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.control_value_A_D_lable.setAlignment(Qt.AlignCenter)
        self.control_value_A_D_lable.move(300, 200)
        self.control_value_A_D_lable.resize(60, 30)
        self.control_value_A_D_lable.setText("艏向D：")

        self.control_value_V_P_lable = QLabel(self)
        self.control_value_V_P_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.control_value_V_P_lable.setAlignment(Qt.AlignCenter)
        self.control_value_V_P_lable.move(100, 230)
        self.control_value_V_P_lable.resize(60, 30)
        self.control_value_V_P_lable.setText("速度P：")

        self.control_value_V_I_lable = QLabel(self)
        self.control_value_V_I_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.control_value_V_I_lable.setAlignment(Qt.AlignCenter)
        self.control_value_V_I_lable.move(200, 230)
        self.control_value_V_I_lable.resize(60, 30)
        self.control_value_V_I_lable.setText("速度I：")

        self.control_value_V_D_lable = QLabel(self)
        self.control_value_V_D_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.control_value_V_D_lable.setAlignment(Qt.AlignCenter)
        self.control_value_V_D_lable.move(300, 230)
        self.control_value_V_D_lable.resize(60, 30)
        self.control_value_V_D_lable.setText("速度D：")

        self.control_value_LOS_C1_lable = QLabel(self)
        self.control_value_LOS_C1_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.control_value_LOS_C1_lable.setAlignment(Qt.AlignCenter)
        self.control_value_LOS_C1_lable.move(100, 260)
        self.control_value_LOS_C1_lable.resize(60, 30)
        self.control_value_LOS_C1_lable.setText("C1：")

        self.control_value_LOS_C2_lable = QLabel(self)
        self.control_value_LOS_C2_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.control_value_LOS_C2_lable.setAlignment(Qt.AlignCenter)
        self.control_value_LOS_C2_lable.move(200, 260)
        self.control_value_LOS_C2_lable.resize(60, 30)
        self.control_value_LOS_C2_lable.setText("C2：")

        self.control_value_LOS_C3_lable = QLabel(self)
        self.control_value_LOS_C3_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.control_value_LOS_C3_lable.setAlignment(Qt.AlignCenter)
        self.control_value_LOS_C3_lable.move(300, 260)
        self.control_value_LOS_C3_lable.resize(60, 30)
        self.control_value_LOS_C3_lable.setText("C3：")

        self.control_value_A_P = QLineEdit(self)
        self.control_value_A_P.setStyleSheet('''font-size:12pt;color:blue;font-weight:bold;font-family:SongTi''')
        self.control_value_A_P.setText(str(self.control_value_list[0]))
        self.control_value_A_P.move(150, 200)
        self.control_value_A_P.resize(50, 25)

        self.control_value_A_I = QLineEdit(self)
        self.control_value_A_I.setStyleSheet('''font-size:12pt;color:blue;font-weight:bold;font-family:SongTi''')
        self.control_value_A_I.setText(str(self.control_value_list[1]))
        self.control_value_A_I.move(250, 200)
        self.control_value_A_I.resize(50, 25)

        self.control_value_A_D = QLineEdit(self)
        self.control_value_A_D.setStyleSheet('''font-size:12pt;color:blue;font-weight:bold;font-family:SongTi''')
        self.control_value_A_D.setText(str(self.control_value_list[2]))
        self.control_value_A_D.move(350, 200)
        self.control_value_A_D.resize(50, 25)

        self.control_value_V_P = QLineEdit(self)
        self.control_value_V_P.setStyleSheet('''font-size:12pt;color:blue;font-weight:bold;font-family:SongTi''')
        self.control_value_V_P.setText(str(self.control_value_list[3]))
        self.control_value_V_P.move(150, 230)
        self.control_value_V_P.resize(50, 25)

        self.control_value_V_I = QLineEdit(self)
        self.control_value_V_I.setStyleSheet('''font-size:12pt;color:blue;font-weight:bold;font-family:SongTi''')
        self.control_value_V_I.setText(str(self.control_value_list[4]))
        self.control_value_V_I.move(250, 230)
        self.control_value_V_I.resize(50, 25)

        self.control_value_V_D = QLineEdit(self)
        self.control_value_V_D.setStyleSheet('''font-size:12pt;color:blue;font-weight:bold;font-family:SongTi''')
        self.control_value_V_D.setText(str(self.control_value_list[5]))
        self.control_value_V_D.move(350, 230)
        self.control_value_V_D.resize(50, 25)

        self.control_value_LOS_C1 = QLineEdit(self)
        self.control_value_LOS_C1.setStyleSheet('''font-size:12pt;color:blue;font-weight:bold;font-family:SongTi''')
        self.control_value_LOS_C1.setText(str(self.control_value_list[6]))
        self.control_value_LOS_C1.move(150, 260)
        self.control_value_LOS_C1.resize(50, 25)

        self.control_value_LOS_C2 = QLineEdit(self)
        self.control_value_LOS_C2.setStyleSheet('''font-size:12pt;color:blue;font-weight:bold;font-family:SongTi''')
        self.control_value_LOS_C2.setText(str(self.control_value_list[7]))
        self.control_value_LOS_C2.move(250, 260)
        self.control_value_LOS_C2.resize(50, 25)

        self.control_value_LOS_C3 = QLineEdit(self)
        self.control_value_LOS_C3.setStyleSheet('''font-size:12pt;color:blue;font-weight:bold;font-family:SongTi''')
        self.control_value_LOS_C3.setText(str(self.control_value_list[8]))
        self.control_value_LOS_C3.move(350, 260)
        self.control_value_LOS_C3.resize(50, 25)

    def get_control_value(self):

        self.control_value_list[0] = float(self.control_value_A_P.text())
        self.control_value_list[1] = float(self.control_value_A_I.text())
        self.control_value_list[2] = float(self.control_value_A_D.text())
        self.control_value_list[3] = float(self.control_value_V_P.text())
        self.control_value_list[4] = float(self.control_value_V_I.text())
        self.control_value_list[5] = float(self.control_value_V_D.text())
        self.control_value_list[6] = float(self.control_value_LOS_C1.text())
        self.control_value_list[7] = float(self.control_value_LOS_C2.text())
        self.control_value_list[8] = float(self.control_value_LOS_C3.text())

        self.cf.set("control value", "a_p", str(self.control_value_list[0]))
        self.cf.set("control value", "a_i", str(self.control_value_list[1]))
        self.cf.set("control value", "a_d", str(self.control_value_list[2]))
        self.cf.set("control value", "v_p", str(self.control_value_list[3]))
        self.cf.set("control value", "v_i", str(self.control_value_list[4]))
        self.cf.set("control value", "v_d", str(self.control_value_list[5]))
        self.cf.set("control value", "los_c1", str(self.control_value_list[6]))
        self.cf.set("control value", "los_c1", str(self.control_value_list[7]))
        self.cf.set("control value", "los_c1", str(self.control_value_list[8]))

        self.cf.write(open("config.ini",'w'))

        print(self.control_value_list)
        return self.control_value_list

    def order_control(self):

        self.A_hope_lable = QLabel(self)
        self.A_hope_lable.move(50,450)
        self.A_hope_lable.resize(100,20)
        self.A_hope_lable.setText("期望艏向：")
        self.A_hope_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.A_hope_lable.setAlignment(Qt.AlignCenter)

        self.A_hope_text = QLineEdit(self)
        self.A_hope_text.move(140,450)
        self.A_hope_text.resize(60,30)
        self.A_hope_text.setStyleSheet('''font-size:14pt;color:blue;font-weight:bold;font-family:SongTi''')
        self.A_hope_text.setText("00.00")
        

        self.A_real_lable = QLabel(self)
        self.A_real_lable.move(200,450)
        self.A_real_lable.resize(100,20)
        self.A_real_lable.setText("实际艏向：")
        self.A_real_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.A_real_lable.setAlignment(Qt.AlignCenter)

        self.A_real_text = QTextBrowser(self)
        self.A_real_text.move(290,450)
        self.A_real_text.resize(60,30)
        self.A_real_text.setStyleSheet('''font-size:12pt;color:blue;font-weight:bold;font-family:SongTi''')
        self.A_real_text.setText("00.00")

        self.V_hope_lable = QLabel(self)
        self.V_hope_lable.move(50,500)
        self.V_hope_lable.resize(100,20)
        self.V_hope_lable.setText("期望速度：")
        self.V_hope_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.V_hope_lable.setAlignment(Qt.AlignCenter)

        self.V_hope_text = QLineEdit(self)
        self.V_hope_text.move(140,500)
        self.V_hope_text.resize(60,30)
        self.V_hope_text.setStyleSheet('''font-size:14pt;color:blue;font-weight:bold;font-family:SongTi''')
        self.V_hope_text.setText("00.00")

        self.V_real_lable = QLabel(self)
        self.V_real_lable.move(200,500)
        self.V_real_lable.resize(100,20)
        self.V_real_lable.setText("实际速度：")
        self.V_real_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.V_real_lable.setAlignment(Qt.AlignCenter)

        self.V_real_text = QTextBrowser(self)
        self.V_real_text.move(290,500)
        self.V_real_text.resize(60,30)
        self.V_real_text.setStyleSheet('''font-size:12pt;color:blue;font-weight:bold;font-family:SongTi''')
        self.V_real_text.setText("00.00")

        self.A_error_lable = QLabel(self)
        self.A_error_lable.move(350,450)
        self.A_error_lable.resize(100,20)
        self.A_error_lable.setText("偏差（°）")
        self.A_error_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.A_error_lable.setAlignment(Qt.AlignCenter)

        self.A_error_text = QTextBrowser(self)
        self.A_error_text.move(440,450)
        self.A_error_text.resize(60,30)
        self.A_error_text.setStyleSheet('''font-size:12pt;color:blue;font-weight:bold;font-family:SongTi''')
        self.A_error_text.setText("00.00")

        self.V_error_lable = QLabel(self)
        self.V_error_lable.move(350,500)
        self.V_error_lable.resize(100,20)
        self.V_error_lable.setText("偏差（m/s）")
        self.V_error_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.V_error_lable.setAlignment(Qt.AlignCenter)

        self.V_error_text = QTextBrowser(self)
        self.V_error_text.move(440,500)
        self.V_error_text.resize(60,30)
        self.V_error_text.setStyleSheet('''font-size:12pt;color:blue;font-weight:bold;font-family:SongTi''')
        self.V_error_text.setText("00.00")

        self.servo_hope_lable = QLabel(self)
        self.servo_hope_lable.move(50,550)
        self.servo_hope_lable.resize(100,20)
        self.servo_hope_lable.setText("期望舵角：")
        self.servo_hope_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.servo_hope_lable.setAlignment(Qt.AlignCenter)

        self.servo_hope_text = QLineEdit(self)
        self.servo_hope_text.move(140,550)
        self.servo_hope_text.resize(60,30)
        self.servo_hope_text.setStyleSheet('''font-size:14pt;color:blue;font-weight:bold;font-family:SongTi''')
        self.servo_hope_text.setText("00.00")

        self.servo_real_lable = QLabel(self)
        self.servo_real_lable.move(200,550)
        self.servo_real_lable.resize(100,20)
        self.servo_real_lable.setText("实际舵角：")
        self.servo_real_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.servo_real_lable.setAlignment(Qt.AlignCenter)

        self.servo_real_text = QTextBrowser(self)
        self.servo_real_text.move(290,550)
        self.servo_real_text.resize(60,30)
        self.servo_real_text.setStyleSheet('''font-size:12pt;color:blue;font-weight:bold;font-family:SongTi''')
        self.servo_real_text.setText("00.00")

        self.servo_error_lable = QLabel(self)
        self.servo_error_lable.move(350,550)
        self.servo_error_lable.resize(100,20)
        self.servo_error_lable.setText("偏差（°）")
        self.servo_error_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.servo_error_lable.setAlignment(Qt.AlignCenter)

        self.servo_error_text = QTextBrowser(self)
        self.servo_error_text.move(440,550)
        self.servo_error_text.resize(60,30)
        self.servo_error_text.setStyleSheet('''font-size:12pt;color:blue;font-weight:bold;font-family:SongTi''')
        self.servo_error_text.setText("00.00")

        self.montor_hope_lable = QLabel(self)
        self.montor_hope_lable.move(50,600)
        self.montor_hope_lable.resize(100,20)
        self.montor_hope_lable.setText("推进器：")
        self.montor_hope_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.montor_hope_lable.setAlignment(Qt.AlignCenter)

        self.montor_hope_text = QLineEdit(self)
        self.montor_hope_text.move(140,600)
        self.montor_hope_text.resize(60,30)
        self.montor_hope_text.setStyleSheet('''font-size:14pt;color:blue;font-weight:bold;font-family:SongTi''')
        self.montor_hope_text.setText("00.00")

        self.beiyong_1_lable = QLabel(self)
        self.beiyong_1_lable.move(200,600)
        self.beiyong_1_lable.resize(100,20)
        self.beiyong_1_lable.setText("备用1：")
        self.beiyong_1_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.beiyong_1_lable.setAlignment(Qt.AlignCenter)

        self.beiyong_1_text = QTextBrowser(self)
        self.beiyong_1_text.move(290,600)
        self.beiyong_1_text.resize(60,30)
        self.beiyong_1_text.setStyleSheet('''font-size:12pt;color:blue;font-weight:bold;font-family:SongTi''')
        self.beiyong_1_text.setText("NaN")

        self.beiyong_2_lable = QLabel(self)
        self.beiyong_2_lable.move(350,600)
        self.beiyong_2_lable.resize(100,20)
        self.beiyong_2_lable.setText("备用2：")
        self.beiyong_2_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.beiyong_2_lable.setAlignment(Qt.AlignCenter)

        self.beiyong_2_text = QTextBrowser(self)
        self.beiyong_2_text.move(440,600)
        self.beiyong_2_text.resize(60,30)
        self.beiyong_2_text.setStyleSheet('''font-size:12pt;color:blue;font-weight:bold;font-family:SongTi''')
        self.beiyong_2_text.setText("NaN")

    def move_action(self):

        self.move_buff = None
        # 运动控制输入量 期望艏向、期望速度
        self.move_value_input_list[0] = float(self.A_hope_text.text()) #期望艏向
        self.move_value_input_list[1] = float(self.V_hope_text.text()) #期望速度
        # 期望舵角、推进器
        self.force_value_input_list[0] = float(self.servo_hope_text.text()) #期望舵角
        self.force_value_input_list[1] = float(self.montor_hope_text.text()) # 期望推进器
        #实际艏向 速度 舵角
        self.action_value_out_list[0] = 0
        self.action_value_out_list[1] = 0
        self.action_value_out_list[2] = 0
        #偏差：艏向 速度 舵角
        self.action_value_error_list[0] = 0
        self.action_value_error_list[1] = 0
        self.action_value_error_list[2] = 0

        # print(self.move_value_input_list)
        # print(self.force_value_input_list)
        if self.ctrl_model_flag == 1: #遥控：舵角 推进器
            self.move_buff = DataChange.forceTobyte(self.force_value_input_list)
            self.A_hope_text.setText("00.00")
            self.V_hope_text.setText("00.00")
            print(self.move_buff)
            self.commuication_signal.emit(self.ctrl_model_flag)
        elif self.ctrl_model_flag == 2:#智能：航速 航向
            self.move_buff,move_buff_show = DataChange.moveTobyte(self.move_value_input_list)
            self.servo_hope_text.setText("00.00")
            self.montor_hope_text.setText("00.00")
            print(self.move_buff)
            self.order_text_box.setPlainText(move_buff_show)
            self.commuication_signal.emit(self.ctrl_model_flag)

        elif self.ctrl_model_flag == 3:
            print("请规划路径点")

        elif self.ctrl_model_flag == 4:
            print("当前为手柄操纵")

        else:
            print("error!!!")
            
        

    def order_box(self):

        self.order_enter = QPushButton(self)
        self.order_enter.move(50,650)
        self.order_enter.resize(100,30)
        self.order_enter.setText("执行指令")
        self.order_enter.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.order_enter.clicked.connect(lambda: self.move_action())
        
        self.order_text_box = QPlainTextEdit(self)
        self.order_text_box.move(350, 650)
        self.order_text_box.resize(350, 50)
        self.order_text_box.setPlainText("7B 00 00 00 01 00 00 00 00 A1 7D")
        self.order_text_box.setStyleSheet('''font-size:12pt;color:black;font-family:SongTi''')

        self.order_text_auto_check = QCheckBox(self)
        self.order_text_auto_check.move(150,650)
        self.order_text_auto_check.resize(100,30)
        self.order_text_auto_check.setText("自动发送")
        self.order_text_auto_check.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi;QCheckBox { text-align: right; }''')
        self.order_text_auto_check.stateChanged.connect(lambda state: self.auto_send(state))

        self.order_text_send_btn = QPushButton(self)
        self.order_text_send_btn.move(50, 700)
        self.order_text_send_btn.resize(100, 30)
        self.order_text_send_btn.setText("手动发送")
        self.order_text_send_btn.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.order_text_send_btn.clicked.connect(lambda: self.move_action())

        self.order_text_send_time = QLineEdit(self)
        self.order_text_send_time.move(250, 700)
        self.order_text_send_time.resize(50, 30)
        self.order_text_send_time.setText("0.1")
        self.order_text_send_time.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')

        self.order_text_send_time_lable = QLabel(self)
        self.order_text_send_time_lable.move(150, 700)
        self.order_text_send_time_lable.resize(100, 30)
        self.order_text_send_time_lable.setText("发送周期(秒)")
        self.order_text_send_time_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')

        self.order_text_send_line_lable = QLabel(self)
        self.order_text_send_line_lable.move(350, 700)
        self.order_text_send_line_lable.resize(100, 30)
        self.order_text_send_line_lable.setText("发送数：")
        self.order_text_send_line_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')

        self.order_text_send_line_cont = QLabel(self)
        self.order_text_send_line_cont.move(400, 700)
        self.order_text_send_line_cont.resize(100, 30)
        self.order_text_send_line_cont.setText("00000")
        self.order_text_send_line_cont.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')

        self.order_text_recv_line_lable = QLabel(self)
        self.order_text_recv_line_lable.move(450, 700)
        self.order_text_recv_line_lable.resize(100, 30)
        self.order_text_recv_line_lable.setText("接受数：")
        self.order_text_recv_line_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')

        self.order_text_recv_line_cont = QLabel(self)
        self.order_text_recv_line_cont.move(520, 700)
        self.order_text_recv_line_cont.resize(100, 25)
        self.order_text_recv_line_cont.setText("00000")
        self.order_text_recv_line_cont.setStyleSheet('''background-color:White;font-size:12pt;color:black;font-family:SongTi''')

        self.order_text_line_cont_zero = QPushButton(self)
        self.order_text_line_cont_zero.move(600,700)
        self.order_text_line_cont_zero.resize(50,30)
        self.order_text_line_cont_zero.setText("清零")
        self.order_text_line_cont_zero.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')

    def Get_Touch(self):

        time.sleep(5)
        while self.RUN_flag:
            touch_js_str = makeJS.getMapTouchJS()
            self.gaode_map_view_label.page().runJavaScript(touch_js_str, self.testCallBackTouch)
            time.sleep(0.1)

    def testCallBackTouch(self, js_back_message):

        if len(js_back_message) > 0:
            print('用户点击了坐标:( %s)' % js_back_message)
            self.marker_list.append(js_back_message)
            add_mark_js_str = makeJS.add_markMap_JS(js_back_message,len(self.marker_list))
            self.gaode_map_view_label.page().runJavaScript(add_mark_js_str,self.print_marker)
            print(self.marker_list)
            print('=============')
           
    def print_marker(self,xxx_back_message):
        print(xxx_back_message)    
       
    def refreshShow(self,get_dic):
        print(get_dic)
        base_js_str = makeJS.getBaseJS()
        self.gaode_map_view_label.page().runJavaScript(base_js_str)
        print('刷新地图')

    def clearMarker(self):
        self.marker_list = []
        clearMarker_JS_str = makeJS.clear_markMap_JS()
        self.gaode_map_view_label.page().runJavaScript(clearMarker_JS_str)
        print("标点已清除",self.marker_list)

    def delMarker(self):
        if self.marker_list:
            
            print(self.marker_list[-1])
            del_marker_str = makeJS.del_markMap_JS()
            self.gaode_map_view_label.page().runJavaScript(del_marker_str)
            self.marker_list.pop()
            
            
            print(self.marker_list)
        else:
            print("无标点，无法删除")

    def PathFromMarkers(self):
        
        if self.marker_list :
            PathFromMarkers_JS_str = makeJS.path_markMap_JS(self.marker_list)
            self.gaode_map_view_label.page().runJavaScript(PathFromMarkers_JS_str)
        else:
            print("请先规划轨迹点")
        
        print("顺序路径")

    def PathPlan(self):
        print("路径规划")

    def roboFlash(self):
        time.sleep(1)
        temp_lon = 126.663762
        temp_lat = 45.801751
        temp_i = 0
        lon_lat_waypoint = ['126.663762,45.801751','126.663762,45.801751']
        while self.RUN_flag:
            self.robo_lon_lat = str(temp_lon)+','+str(temp_lat)
            lon_lat_waypoint[1]= self.robo_lon_lat
            
            roboFlash_str_JS = makeJS.roboFlash_JS(self.robo_lon_lat)
            self.gaode_map_view_label.page().runJavaScript(roboFlash_str_JS)
            
            robo_path_Flash_str_JS = makeJS.roboPathFlash_JS(lon_lat_waypoint)
            self.gaode_map_view_label.page().runJavaScript(robo_path_Flash_str_JS)
            # print(lon_lat_waypoint)

            lon_lat_waypoint[0]= self.robo_lon_lat
            temp_lon =  126.663762 + 0.001 * math.cos(temp_i) - 0.001
            temp_lat =  45.801751  + 0.001 * math.sin(temp_i)
            temp_i = temp_i + 0.01

            time.sleep(1000)

    def AGV_UI_button(self):

        self.btn_02 = QPushButton('信息更新', self)
        self.btn_02.move(20, 110)
        self.btn_02.resize(80, 20)
        self.btn_02.clicked.connect(self.mes_chenged_AGV)

        self.btn_03 = QPushButton('文本测试', self)
        self.btn_03.move(100, 110)
        self.btn_03.resize(80, 20)
        self.btn_03.clicked.connect(lambda :self.text_test(0))

        self.btn_04 = QPushButton('文本测试', self)
        self.btn_04.move(200, 110)
        self.btn_04.resize(80, 20)
        self.btn_04.clicked.connect(lambda :self.text_test(1))

        self.btn_05 = QPushButton('文本测试', self)
        self.btn_05.move(300, 110)
        self.btn_05.resize(80, 20)
        self.btn_05.clicked.connect(lambda :self.text_test(2))

        self.btn_06 = QPushButton('文本测试', self)
        self.btn_06.move(400, 110)
        self.btn_06.resize(80, 20)
        self.btn_06.clicked.connect(lambda :self.text_test(3))

    def mes_AGV(self):

        
        self.mes_01 = QDialog(self)
        self.mes_01.setFixedSize(400, 500)
        self.mes_01.setWindowTitle("AGV数据")

        self.AGV_speed_x = QLabel(self.mes_01)
        self.AGV_speed_x.move(20, 20)
        self.AGV_speed_x.resize(120, 30)
        self.AGV_speed_x.setText("X速度(mm/s):")
        self.AGV_speed_x.setStyleSheet('''font-size:12pt;color:blue;font-family:KaiTi''')
        self.AGV_speed_x.setAlignment(Qt.AlignCenter)

        self.AGV_speed_x_text = QTextBrowser(self.mes_01)
        self.AGV_speed_x_text.move(200, 25)
        self.AGV_speed_x_text.resize(150, 30)
        self.AGV_speed_x_text.setText("00.00")
        self.AGV_speed_x_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_speed_x_text.setAlignment(Qt.AlignCenter)

        self.AGV_speed_y = QLabel(self.mes_01)
        self.AGV_speed_y.move(20, 60)
        self.AGV_speed_y.resize(120, 30)
        self.AGV_speed_y.setText("Y速度(mm/s):")
        self.AGV_speed_y.setStyleSheet('''font-size:12pt;color:blue;font-family:KaiTi''')
        self.AGV_speed_y.setAlignment(Qt.AlignCenter)

        self.AGV_speed_y_text = QTextBrowser(self.mes_01)
        self.AGV_speed_y_text.move(200, 60)
        self.AGV_speed_y_text.resize(150, 30)
        self.AGV_speed_y_text.setText("00.00")
        self.AGV_speed_y_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_speed_y_text.setAlignment(Qt.AlignCenter)

        self.AGV_speed_z = QLabel(self.mes_01)
        self.AGV_speed_z.move(20, 100)
        self.AGV_speed_z.resize(120, 30)
        self.AGV_speed_z.setText("Z速度(mm/s):")
        self.AGV_speed_z.setStyleSheet('''font-size:12pt;color:blue;font-family:KaiTi''')
        self.AGV_speed_z.setAlignment(Qt.AlignCenter)

        self.AGV_speed_z_text = QTextBrowser(self.mes_01)
        self.AGV_speed_z_text.move(200, 100)
        self.AGV_speed_z_text.resize(150, 30)
        self.AGV_speed_z_text.setText("00.00")
        self.AGV_speed_z_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_speed_z_text.setAlignment(Qt.AlignCenter)

        self.AGV_acc_x = QLabel(self.mes_01)
        self.AGV_acc_x.move(20, 140)
        self.AGV_acc_x.resize(120, 30)
        self.AGV_acc_x.setText("X加速度(m/s^2):")
        self.AGV_acc_x.setStyleSheet('''font-size:12pt;color:blue;font-family:KaiTi''')
        self.AGV_acc_x.setAlignment(Qt.AlignCenter)

        self.AGV_acc_x_text = QTextBrowser(self.mes_01)
        self.AGV_acc_x_text.move(200, 140)
        self.AGV_acc_x_text.resize(150, 30)
        self.AGV_acc_x_text.setText("00.00")
        self.AGV_acc_x_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_acc_x_text.setAlignment(Qt.AlignCenter)

        self.AGV_acc_y = QLabel(self.mes_01)
        self.AGV_acc_y.move(20, 180)
        self.AGV_acc_y.resize(120, 30)
        self.AGV_acc_y.setText("Y加速度(m/s^2):")
        self.AGV_acc_y.setStyleSheet('''font-size:12pt;color:blue;font-family:KaiTi''')
        self.AGV_acc_y.setAlignment(Qt.AlignCenter)

        self.AGV_acc_y_text = QTextBrowser(self.mes_01)
        self.AGV_acc_y_text.move(200, 180)
        self.AGV_acc_y_text.resize(150, 30)
        self.AGV_acc_y_text.setText("00.00")
        self.AGV_acc_y_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_acc_y_text.setAlignment(Qt.AlignCenter)

        self.AGV_acc_z = QLabel(self.mes_01)
        self.AGV_acc_z.move(20, 220)
        self.AGV_acc_z.resize(120, 30)
        self.AGV_acc_z.setText("Z加速度(m/s^2):")
        self.AGV_acc_z.setStyleSheet('''font-size:12pt;color:blue;font-family:KaiTi''')
        self.AGV_acc_z.setAlignment(Qt.AlignCenter)

        self.AGV_acc_z_text = QTextBrowser(self.mes_01)
        self.AGV_acc_z_text.move(200, 220)
        self.AGV_acc_z_text.resize(150, 30)
        self.AGV_acc_z_text.setText("00.00")
        self.AGV_acc_z_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_acc_z_text.setAlignment(Qt.AlignCenter)

        self.AGV_ang_x = QLabel(self.mes_01)
        self.AGV_ang_x.move(20, 260)
        self.AGV_ang_x.resize(120, 30)
        self.AGV_ang_x.setText("X(rad/s^2):")
        self.AGV_ang_x.setStyleSheet('''font-size:12pt;color:blue;font-family:KaiTi''')
        self.AGV_ang_x.setAlignment(Qt.AlignCenter)

        self.AGV_ang_x_text = QTextBrowser(self.mes_01)
        self.AGV_ang_x_text.move(200, 260)
        self.AGV_ang_x_text.resize(150, 30)
        self.AGV_ang_x_text.setText("00.00")
        self.AGV_ang_x_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_ang_x_text.setAlignment(Qt.AlignCenter)

        self.AGV_ang_y = QLabel(self.mes_01)
        self.AGV_ang_y.move(20, 300)
        self.AGV_ang_y.resize(120, 30)
        self.AGV_ang_y.setText("Y(rad/s^2):")
        self.AGV_ang_y.setStyleSheet('''font-size:12pt;color:blue;font-family:KaiTi''')
        self.AGV_ang_y.setAlignment(Qt.AlignCenter)

        self.AGV_ang_y_text = QTextBrowser(self.mes_01)
        self.AGV_ang_y_text.move(200, 300)
        self.AGV_ang_y_text.resize(150, 30)
        self.AGV_ang_y_text.setText("00.00")
        self.AGV_ang_y_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_ang_y_text.setAlignment(Qt.AlignCenter)

        self.AGV_ang_z = QLabel(self.mes_01)
        self.AGV_ang_z.move(20, 340)
        self.AGV_ang_z.resize(120, 30)
        self.AGV_ang_z.setText("Z(rad/s^2):")
        self.AGV_ang_z.setStyleSheet('''font-size:12pt;color:blue;font-family:KaiTi''')
        self.AGV_ang_z.setAlignment(Qt.AlignCenter)

        self.AGV_ang_z_text = QTextBrowser(self.mes_01)
        self.AGV_ang_z_text.move(200, 340)
        self.AGV_ang_z_text.resize(150, 30)
        self.AGV_ang_z_text.setText("00.00")
        self.AGV_ang_z_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.AGV_ang_z_text.setAlignment(Qt.AlignCenter)

        self.state_battery = QLabel(self.mes_01)
        self.state_battery.move(20, 380)
        self.state_battery.resize(120, 30)
        self.state_battery.setText("电池电压(mv):")
        self.state_battery.setStyleSheet('''font-size:12pt;color:blue;font-family:KaiTi''')
        self.state_battery.setAlignment(Qt.AlignCenter)

        self.state_battery_text = QTextBrowser(self.mes_01)
        self.state_battery_text.move(200, 380)
        self.state_battery_text.resize(150, 30)
        self.state_battery_text.setText("00.00")
        self.state_battery_text.setStyleSheet('''font-size:12pt;color:red;font-family:KaiTi''')
        self.state_battery_text.setAlignment(Qt.AlignCenter)

            
    def mes_01_show(self):
        self.mes_01.show()
    
    def global_state(self):
        self.ins_state_lable = QLabel(self)
        self.ins_state_lable.move(1250,600)
        self.ins_state_lable.resize(100,20)
        self.ins_state_lable.setText("组合导航")
        self.ins_state_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.ins_state_lable.setAlignment(Qt.AlignCenter)

        self.ins_state_lable_light = QLabel(self)
        self.ins_state_lable_light.setGeometry(QRect(1350, 600, 25, 25))
        self.ins_state_lable_light.setStyleSheet("border-radius:10px;background-color:red")

        self.montor_state_lable = QLabel(self)
        self.montor_state_lable.move(1250,650)
        self.montor_state_lable.resize(100,20)
        self.montor_state_lable.setText("推进器")
        self.montor_state_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.montor_state_lable.setAlignment(Qt.AlignCenter)

        self.montor_state_lable_light = QLabel(self)
        self.montor_state_lable_light.setGeometry(QRect(1350, 650, 25, 25))
        self.montor_state_lable_light.setStyleSheet("border-radius:10px;background-color:red")

        self.radio_state_lable = QLabel(self)
        self.radio_state_lable.move(1400,600)
        self.radio_state_lable.resize(100,20)
        self.radio_state_lable.setText("通信电台")
        self.radio_state_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.radio_state_lable.setAlignment(Qt.AlignCenter)

        self.radio_state_lable_light = QLabel(self)
        self.radio_state_lable_light.setGeometry(QRect(1500, 600, 25, 25))
        self.radio_state_lable_light.setStyleSheet("border-radius:10px;background-color:red")

        self.radar_state_lable = QLabel(self)
        self.radar_state_lable.move(1400,650)
        self.radar_state_lable.resize(100,20)
        self.radar_state_lable.setText("感知设备")
        self.radar_state_lable.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.radar_state_lable.setAlignment(Qt.AlignCenter)

        self.radar_state_lable_light = QLabel(self)
        self.radar_state_lable_light.setGeometry(QRect(1500, 650, 25, 25))
        self.radar_state_lable_light.setStyleSheet("border-radius:10px;background-color:red")

    def text_test(self,id_num):

        for i in range(50):
            self.TxtBrowser_list[id_num].append("测试:"+str(i)+"times")

    def mes_chenged_AGV(self,list_data):

        list_data = [0,1,2,3,4,5,6,7,8,9,10]

        self.AGV_speed_x_text.setText(str(list_data[1]))
        self.AGV_speed_x_text.setAlignment(Qt.AlignCenter)

        self.AGV_speed_y_text.setText(str(list_data[2]))
        self.AGV_speed_y_text.setAlignment(Qt.AlignCenter)

        self.AGV_speed_z_text.setText(str(list_data[3]))
        self.AGV_speed_z_text.setAlignment(Qt.AlignCenter)

        self.AGV_acc_x_text.setText(str(list_data[4]))
        self.AGV_acc_x_text.setAlignment(Qt.AlignCenter)

        self.AGV_acc_y_text.setText(str(list_data[5]))
        self.AGV_acc_y_text.setAlignment(Qt.AlignCenter)

        self.AGV_acc_z_text.setText(str(list_data[6]))
        self.AGV_acc_z_text.setAlignment(Qt.AlignCenter)

        self.AGV_ang_x_text.setText(str(list_data[7]))
        self.AGV_ang_x_text.setAlignment(Qt.AlignCenter)

        self.AGV_ang_y_text.setText(str(list_data[8]))
        self.AGV_ang_y_text.setAlignment(Qt.AlignCenter)

        self.AGV_ang_z_text.setText(str(list_data[9]))
        self.AGV_ang_z_text.setAlignment(Qt.AlignCenter)

        self.state_battery_text.setText(str(list_data[10]))
        self.state_battery_text.setAlignment(Qt.AlignCenter)

    def time_box(self):

        self.time_new_label = QLabel(self)
        self.time_new_label.move(1250,680)
        self.time_new_label.resize(50,30)
        self.time_new_label.setText("时间")
        self.time_new_label.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.time_new_label.setAlignment(Qt.AlignCenter)

        self.time_new_text = QLabel(self)
        self.time_new_text.move(1300,680)
        self.time_new_text.resize(200,30)
        self.time_new_text.setText(self.time_open_str.strftime('%Y-%m-%d %H:%M:%S'))
        self.time_new_text.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.time_new_text.setAlignment(Qt.AlignCenter)

        self.time_open_label = QLabel(self)
        self.time_open_label.move(1250,710)
        self.time_open_label.resize(50,30)
        self.time_open_label.setText("运行")
        self.time_open_label.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.time_open_label.setAlignment(Qt.AlignCenter)

        self.time_open_test = QLabel(self)
        self.time_open_test.move(1300,710)
        self.time_open_test.resize(200,30)
        self.time_open_test.setText(str(self.time_least_str))
        self.time_open_test.setStyleSheet('''font-size:12pt;color:black;font-family:KaiTi''')
        self.time_open_test.setAlignment(Qt.AlignCenter)

    def time_flash(self):

        while(self.RUN_flag):
            self.time_now_str = datetime.datetime.now()
            self.time_new_text.setText(self.time_now_str.strftime('%Y-%m-%d %H:%M:%S'))
            self.time_least_str = self.time_now_str - self.time_open_str
            self.time_open_test.setText(str(self.time_least_str))
            #print("ok")
            time.sleep(0.01)

    def mes_get(self):
        return 0

    def auto_send(self,check_state):
        if check_state:
            print("自动发送消息")

    def contrul_model(self,model_flag):
        self.control_signal.emit(model_flag)
        if model_flag == 1:
            print("UI:远程遥控")
            self.ctrl_model_flag = 1

        elif model_flag == 2:
            print("UI:智能控制")
            self.ctrl_model_flag = 2

        elif model_flag == 3:
            print("UI:自主控制")
            self.ctrl_model_flag = 3

        elif model_flag == 4:
            print("UI:手柄控制")
            self.ctrl_model_flag = 4

    def closeEvent(self, event):
        result = QMessageBox.question(self,
                                            "正在退出",
                                            "确定要退出程序吗？",
                                            QMessageBox.Yes | QMessageBox.No)
        event.ignore()

        if result == QMessageBox.Yes:
            print("窗口关闭")
            '''
            程序结束工作
            '''
            self.RUN_flag = False
            self.runsignal.emit(0)


            event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    s1 = States()
    
    s1.show()

    sys.exit(app.exec_())
