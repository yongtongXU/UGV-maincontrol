import socket
import threading
from queue import Queue
import threading
import socket
import datetime
from time import strftime
 



class network(object):
    def __init__(self,id_addr_list):

        self.Q_1 = Queue(5)
        self.id_addr_list = id_addr_list
        self.port = 8000
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        host_address = (self.get_ip_port(),self.port)
        self.udp_socket.bind(host_address)

        # self.net_sendThread = threading.Thread(target=self.netsend, args=())
        # self.net_sendThread.start()
        # self.net_recvThread = threading.Thread(target=self.netrecv, args=())
        # self.net_recvThread.start()

    def get_ip_port(self):
        self.self_ip = socket.gethostbyname(socket.gethostname())
        return self.self_ip

    def netsend(self,data):

        x = data.encode()
        for i in range(len(self.id_addr_list)):
            self.udp_socket.sendto(x, self.id_addr_list[i])


    def netrecv(self):


        return 0