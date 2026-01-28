from PySide6.QtGui import *
from PySide6.QtQml import *
from PySide6.QtCore import *
from pathlib import *
from PySide6.QtQuickControls2 import *
import sys



if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    QQuickStyle.setStyle("Material")
    engine = QQmlApplicationEngine()

    # Get the path of the current directory, and then add the name
    # of the QML file, to load it.
    
    qml_file = Path(__file__).parent / 'qmltest.qml'
    engine.load(qml_file)
    print(qml_file)

    app.exec_()
