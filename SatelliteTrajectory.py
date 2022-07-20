import sys

from qt_material import apply_stylesheet
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
# create the application and the main window
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D

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


class SatelliteTrajectory(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        # super(QWidget, self).__init__(parent)

        self.initSatelliteTrajectoryRawData()
        self.initUI()
        # self.plotfig()
        

    def initUI(self):
        self.fig = plt.figure()                                                   #创建figure对象
        self.canvas=FigureCanvas(self.fig)                              #创建figure画布
        self.figtoolbar=NavigationToolbar(self.canvas, self)     #创建figure工具栏
       
        vlayout=QVBoxLayout()
        vlayout.addWidget(self.canvas)                                 #画布添加到窗口布局中
        vlayout.addWidget(self.figtoolbar)                             #工具栏添加到窗口布局中
        self.setLayout(vlayout)
        
        
        print("plotfig")
        # ax = self.fig.subplots()
        print(self.fig)
        ax = plt.axes(projection='3d')
        GPS_n_pos_raw_part = self.GPS_row[:]
        for n in range(len(self.GPS)):
            x = [item[0] for item in GPS_n_pos_raw_part[n]]
            y = [item[1] for item in GPS_n_pos_raw_part[n]]
            z = [item[2] for item in GPS_n_pos_raw_part[n]]
            # ax.plot(t,np.sin(t))
            ax.plot3D(x, y, z, 'gray')
        # plot earth
        xx, yy, zz = self.hua_qiu(x=0, y=0, z=0, r=3474.8/2*1000*10, dense=40)
        ax.plot_surface(xx, yy, zz, rstride=1, cstride=1, cmap='gray', alpha=0.5) # cmap='rainbow',
        
        ax.autoscale_view()
        

    def hua_qiu(self, x, y, z, r, dense):
        """
            圆心坐标 半径 稠密程度
        """
        t = np.linspace(0, np.pi * 2, dense)
        s = np.linspace(0, np.pi, dense)
        t, s = np.meshgrid(t, s)             # 生成稠密网格点
        x = x + r * np.sin(s) * np.cos(t)    # 球面坐标公式
        y = y + r * np.sin(s) * np.sin(t)
        z = z + r * np.cos(s)
        return x, y, z

        
    def initSatelliteTrajectoryRawData(self):
        def SellectSystem(all_sat, system):
            system_letter = {
                'GPS': "G",
                'GLONASS': "R",
                'Beidou': "C",
                'Galileo': "E",
            }
            letter = system_letter.get(system, None)

            all_sat = np.array(all_sat)
            want_sat = []
            for i in range(len(all_sat)):
                if all_sat[i][0] == letter:
                    want_sat = np.append(want_sat, all_sat[i])
            return want_sat

        # load observation
        obs = gr.load('data/20200384.21o')
        epoch_first = str(np.array(obs.time[0]))[0:19]
        print(epoch_first)
        epoch_last = str(np.array(obs.time[-1]))[0:19]
        print(epoch_last)
        eph = gr.load('data/20200384.21n', tlim=[epoch_first, epoch_last])
        print("init obs eph")
        # list all available satellites
        
        self.GPS = SellectSystem(eph.sv, 'GPS')
        GPS = self.GPS
        print('\nAvailable satellite:\n', GPS)
        P_obs = np.zeros([len(GPS), 1])
        P_computed = np.zeros([len(GPS), 1])
        A = np.zeros([len(GPS), 4])
        delta_P = np.zeros([len(GPS), 1])
        A[:, 3] = 299792458
        sat_pos = np.zeros([len(GPS), 3])
        tList = []
        for minute in range(0,60,12):
            second = 0
            tList.append(f"2021-01-02T12:{minute}:{second}")

        GPS_row = []
        for n in range(len(GPS)):
            GPS_row_singleSat = []
            for t in tList:
                # print('Use satellite:', GPS[n])
                ## calculate the position of satellite GPS_n
                GPS_n = eph.sel(sv=GPS[n]).dropna(dim='time', how='all')
                soW = utctoweekseconds(t, 0)[1]
                # print('Time of the week:', soW)
                GPS_n_pos_raw = gpspos_ecef(GPS_n, soW)
                GPS_row_singleSat.append(GPS_n_pos_raw)
                # print('\nPosition of satellite', GPS[n], ':\n', GPS_n_pos)
                print(GPS_n_pos_raw)
            GPS_row.append(GPS_row_singleSat)
        self.GPS_row = GPS_row
        

    def initPlotZenithTrajectory(self):
        self.fig = plt.figure()                             #创建figure对象
        self.canvas=FigureCanvas(self.fig)                  #创建figure画布
        self.figtoolbar=NavigationToolbar(self.canvas, self.ui.plotZenithTrajectory)     #创建figure工具栏
        
        self.plotZenithTrajectory.addWidget(self.canvas)                                 #画布添加到窗口布局中
        self.plotZenithTrajectory.addWidget(self.figtoolbar)                             #工具栏添加到窗口布局中

        print("plotfig")
        # ax = self.fig.subplots()
        print(self.fig)
        ax = plt.axes(projection='3d')
        # ax.rcParams['figure.figsize'] = (12.0, 8.0)
        # ax.figure(figsize=(6.4,4.8),dpi=200)
        GPS_n_pos_raw_part = self.GPS_row[:]
        for n in range(len(GPS)):
            x = [item[0] for item in GPS_n_pos_raw_part[n]]
            y = [item[1] for item in GPS_n_pos_raw_part[n]]
            z = [item[2] for item in GPS_n_pos_raw_part[n]]
            # ax.plot(t,np.sin(t))
            ax.plot3D(x, y, z, 'gray')
        # plot earth
        xx, yy, zz = self.hua_qiu(x=0, y=0, z=0, r=3474.8/2*1000*10, dense=40)
        ax.plot_surface(xx, yy, zz, rstride=1, cstride=1, cmap='gray', alpha=0.5) # cmap='rainbow',
        
        ax.autoscale_view()
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_teal.xml')

    myWin = SatelliteTrajectory()
    myWin.show()
    sys.exit(app.exec())


