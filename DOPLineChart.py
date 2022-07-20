import sys

from qt_material import apply_stylesheet
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
# create the application and the main window
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.ticker as ticker

import georinex as gr
import time
import pickle
import numpy as np
from gnsstimetrans import utctoweekseconds
from gpspos import gpspos_ecef, correctPosition

from geodesy import llh2ecef,ENU2EA,ECEF2ENU,dop


from matplotlib.backends.qt_compat import QtCore, QtWidgets
if QtCore.qVersion() >= "5.":
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure


class DOPLineChart(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        # super(QWidget, self).__init__(parent)

        self.initDOPLineChartRawData()
        self.initUI()
        # self.plotfig()
        

    def initUI(self):
        self.fig,ax = plt.subplots(1,1,figsize=(12,6))                                           #创建figure对象
        self.canvas=FigureCanvas(self.fig)                              #创建figure画布
        self.figtoolbar=NavigationToolbar(self.canvas, self)     #创建figure工具栏
       
        vlayout=QVBoxLayout()
        vlayout.addWidget(self.canvas)                                 #画布添加到窗口布局中
        vlayout.addWidget(self.figtoolbar)                             #工具栏添加到窗口布局中
        self.setLayout(vlayout)
        
        
        print("plotfig")
        # ax = self.fig.subplots()
        print(self.fig)

        tick_spacing = 2
        #通过修改tick_spacing的值可以修改x轴的密度
        #1的时候1到16，5的时候只显示几个
        # fig, ax 
        # plt.figure(figsize=(6,8))
        ax.plot(self.tList, self.GDOPList, "g", marker='D', markersize=5, label="周活")
        ax.set_xlabel("Date Time")
        ax.set_ylabel("DOP")
        plt.xticks(rotation=-20)   # 设置横坐标显示的角度，角度是逆时针，自己看
        ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
        # plt.show()
                

        
    def initDOPLineChartRawData(self):
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
        for minute in range(0,60,2):
            second = 0
            tList.append(f"2021-01-02T12:{minute}:{second}")

        (x0,y0,z0) = llh2ecef([30.549,32.229,6378137])

        GPS_row = []
        for n in range(len(GPS)):
            GPS_row_singleSat = {"sv":GPS[n],"dataByTime":[]}
            for t in tList:
                # print('Use satellite:', GPS[n])
                ## calculate the position of satellite GPS_n
                GPS_n = eph.sel(sv=GPS[n]).dropna(dim='time', how='all')
                soW = utctoweekseconds(t, 0)[1]
                # print('Time of the week:', soW)
                GPS_n_pos_raw = gpspos_ecef(GPS_n, soW)
                [x,y,z] = GPS_n_pos_raw.tolist()
                (E,A) = ENU2EA(ECEF2ENU(x, y, z, x0, y0, z0))
    #             print(E,A)
                GPS_row_singleSat['dataByTime'].append({"time":t,"data":GPS_n_pos_raw,"EA":[E,A]})
                # print('\nPosition of satellite', GPS[n], ':\n', GPS_n_pos)
                print(GPS_n_pos_raw,E,A)
            GPS_row.append(GPS_row_singleSat)
        self.GPS_row = GPS_row
        
        XYZ_obs = list(llh2ecef([30.549,32.229,6378137]))

        GDOPList = []
        for t in tList:
        #     print(t)
            satGroup = []
            for sv in GPS_row:
                for item in sv['dataByTime']:
                    if item['time'] == t:
                        if item['EA'][1]>15:
                            satGroup.append(item['data'])
            GDOP = dop(satGroup, XYZ_obs)[0]
            GDOPList.append(GDOP)
        self.tList = tList
        self.GDOPList = GDOPList

        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_teal.xml')

    myWin = SatelliteTrajectory()
    myWin.show()
    sys.exit(app.exec())


