from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import os
from PyQt5.QtWebEngineWidgets import QWebEngineView


class Window(QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.qwebengine = QWebEngineView()
        url = os.getcwd() + os.path.sep + "save_map.html"  # 要绝对路径，不然无法加载
        print(url)
        self.qwebengine.load(QUrl.fromLocalFile(url))

        # self.qwebengine.load(QUrl('https://www.baidu.com'))
        self.setCentralWidget(self.qwebengine)


app = QApplication(sys.argv)
screen = Window()
screen.showMaximized()
sys.exit(app.exec_())