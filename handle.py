import pygame
import threading
class handle(object):
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.joystick = pygame.joystick.Joystick(0)

        self.axis_value = [0, 0, 0, 0, 0, 0]
        self.btn_value = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0]
        self.hat_value = [0,0,0,0,0,0]

        self.stop_flag = 0
        # self.get_value_thread = threading.Thread(target=self.get_value, args=())
        # self.get_value_thread.start()
        # self.get_value()

    def get_value(self):
        done = False
        done_flag = self.stop_flag
        btn_num = self.joystick.get_numbuttons()
        axis_num = self.joystick.get_numaxes()
        hat_num = self.joystick.get_numhats()
        while done == False:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                if event.type == pygame.JOYBUTTONDOWN:
                    for i in range(btn_num):
                        btn = self.joystick.get_button(i)
                        self.btn_value[i] = btn
                    print(self.btn_value)
                    if self.btn_value[6] == 1:
                        done = True

                if event.type == pygame.JOYHATMOTION:
                    for i in range(hat_num):
                        hat = self.joystick.get_hat(i)
                        self.hat_value[i] = hat
                    print(self.hat_value)

                if event.type == pygame.JOYAXISMOTION:
                    for i in range(axis_num):
                        axis = self.joystick.get_axis(i)
                        self.axis_value[i] = int(axis*1000)
                        self.axis_value[1] = -self.axis_value[1]
                        self.axis_value[3] = -self.axis_value[3]


                    print(self.axis_value)

                if done_flag :
                    done_flag = self.stop_flag
                    done = True

        pygame.quit()

if __name__ == '__main__':

    joy_0 = handle()
    joy_0.get_value()