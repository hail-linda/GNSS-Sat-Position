import sys

from qt_material import apply_stylesheet
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
# create the application and the main window
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D

from geodesy import llh2ecef,ECEF2ENU,ENU2EA
import numpy as np

import georinex as gr
import time
import pickle
import numpy as np
from gnsstimetrans import utctoweekseconds
from gpspos import gpspos_ecef, correctPosition
import math
import random
from matplotlib import cm


from matplotlib.backends.qt_compat import QtCore, QtWidgets
if QtCore.qVersion() >= "5.":
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure


class ZenithTrajectory(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        # super(QWidget, self).__init__(parent)

        self.initZenithTrajectoryRawData()
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
        #         ax = self.fig.subplots()
        random.seed(2)
#         plt.figure(figsize=(6,6))    # 创建一个空白窗体

        # 
        GPS_EA =self.GPS_EA 
        def EA2xy(Pos):
            (E,A) = Pos
            r = (-A/9)+10
            x = r * math.sin(E *math.pi/180)
            y = r * math.cos(E *math.pi/180)
            return x,y

        # 画同心圆
        for i in range(0,11,2):
            x,y = 0,0
            r=i
            a = np.arange(x-r,x+r,0.001)
            # 点的纵坐标为b
            b = np.sqrt(np.power(r,2)-np.power((a-x),2))+y
            plt.plot(a,b,color='grey',linestyle='-')
            plt.plot(a,-b,color='grey',linestyle='-')
        #     plt.scatter(0,0,c='b',marker='o')

        # 画放射线
        for i in range(0,360,30):
            r = 10
            x = math.sin(i/180*math.pi)*r
            y = math.cos(i/180*math.pi)*r
            plt.plot([0,x],[0,y],color='pink',linestyle='-')


        # 画卫星轨迹
        for GPS_EA_sv in GPS_EA:
            lastPos = (0,0)
            c = plt.cm.Dark2(random.randint(0,10))
            for item in GPS_EA_sv:
                Pos = tuple(item)
                if lastPos[0]>0:
                    start_x,start_y = EA2xy(lastPos)
                    end_x,end_y = EA2xy(Pos)
        #             plt.plot(start_lon, start_lat, end_lon, end_lat, linewidth=2,color = "red")
                    plt.plot([start_x,end_x],[start_y, end_y], color=c)
                lastPos = Pos


        plt.grid(True)

        plt.xticks([])  # 去掉x轴
        plt.yticks([])  # 去掉y轴
        plt.axis('off')  # 去掉坐标轴
        


        
    def initZenithTrajectoryRawData(self):
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
        
        (x0,y0,z0) = llh2ecef([30.549,32.229,6378137])
        # [x,y,z] = [ 9961723.82902699,12152465.86317696 ,-21341977.12095519]
        # ENU2EA(ECEF2ENU(x, y, z, x0, y0, z0))
        GPS_EA = []
        for item in GPS_row:
            GPS_EA_part = []
            for t in item:
                [x,y,z] = t.tolist()
                (E,A) = ENU2EA(ECEF2ENU(x, y, z, x0, y0, z0))
                if A >0 :
                    print(ENU2EA(ECEF2ENU(x, y, z, x0, y0, z0)))
                    GPS_EA_part.append((E,A))
            GPS_EA.append(GPS_EA_part)
            self.GPS_EA = GPS_EA
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_teal.xml')

    myWin = ZenithTrajectory()
    myWin.show()
    sys.exit(app.exec())


