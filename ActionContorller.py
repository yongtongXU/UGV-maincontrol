import time
import threading
import control
class ActionControllerClass(object):
    def __init__(self):
        self.pose_queue = None
        self.BD_queue = None
        self.RunFlag = True
        
        self.get_pose_thread = threading.Thread(target=self.getPoseLoop, args=())
        self.get_pose_thread.start()
        
    def getPoseLoop(self):
        while self.RunFlag:

            if self.pose_queue == None or self.BD_queue == None:
                time.sleep(1)

            get_pose = self.pose_queue.get()
            get_BD = self.BD_queue.get()


            # print(' +++++++ 获取的最新姿态信息: %s  +++++++' % get_pose)

