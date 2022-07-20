import sys

# from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu
# from PySide6.QtUiTools import QUiLoader
# from PySide6.QtCore import QFile, QIODevice
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtWidgets import  QMainWindow, QMenuBar, QMenu
from PyQt5.QtCore import QFile, QIODevice,QSize
from PyQt5 import uic
from qt_material import apply_stylesheet,QtStyleTools
# create the application and the main window
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from SatelliteTrajectory import SatelliteTrajectory 
from SubSatellitePoint import SubSatellitePoint
from ZenithTrajectory import ZenithTrajectory
from DOPLineChart import DOPLineChart

import georinex as gr
import time
import pickle
import numpy as np
from gnsstimetrans import utctoweekseconds
from gpspos import gpspos_ecef, correctPosition


from matplotlib.backends.qt_compat import QtCore, QtWidgets
if QtCore.qVersion() >= "5.":
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure


class MyMainForm(QMainWindow):
    def __init__(self, parent=None):
        
        super(MyMainForm, self).__init__(parent)
        self.initUI()
        print("self.initUI()")
        desktop = QApplication.desktop()
        rect = desktop.frameSize()
        # self.add_menu_theme(self.ui, self.ui.menuStyles)
        self.ui.resize(QSize(rect.width(), rect.height()))
        # self.setupUi(self)
        # self.initZenithTrajectoryRawData()
        self.initPlotZenithTrajectory()
   
   
        # self.ui.btnOpenEphemerisFile.clicked.connect(self.cao("btnOpenEphemerisFile"))
        self.ui.resize(1920, 1080)


    def initUI(self):
        ui_file_name = "mainwindow.ui"
        ui_file = QFile(ui_file_name)
        if not ui_file.open(QIODevice.ReadOnly):
            print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
            sys.exit(-1)
        self.ui = uic.loadUi(ui_file)
        ui_file.close()
        if not self.ui:
            print(QUiLoader().errorString())
            sys.exit(-1)
        print(ui_file_name)
        print(self.ui.children())
        

    def initPlotZenithTrajectory(self):
        subSatellitePoint = SubSatellitePoint()
        satelliteTrajectory = SatelliteTrajectory()
        zenithTrajectory = ZenithTrajectory()
        dOPLineChart = DOPLineChart()
        
        self.ui.plotSubSatellitePointLayout.addWidget(subSatellitePoint)
        self.ui.plotSatelliteTrajectoryLayout.addWidget(satelliteTrajectory)
        self.ui.plotZenithTrajectoryLayout.addWidget(zenithTrajectory)
        self.ui.plotDOPLineChartLayout.addWidget(dOPLineChart)
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_teal.xml')
    myWin = MyMainForm()
    myWin.ui.show()
    sys.exit(app.exec())


'''



['dark_amber.xml',
 'dark_blue.xml',
 'dark_cyan.xml',
 'dark_lightgreen.xml',
 'dark_pink.xml',
 'dark_purple.xml',
 'dark_red.xml',
 'dark_teal.xml',
 'dark_yellow.xml',
 'light_amber.xml',
 'light_blue.xml',
 'light_cyan.xml',
 'light_cyan_500.xml',
 'light_lightgreen.xml',
 'light_pink.xml',
 'light_purple.xml',
 'light_red.xml',
 'light_teal.xml',
 'light_yellow.xml']
'''
