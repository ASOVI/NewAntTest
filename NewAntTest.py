# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 11:07:24 2017

@author: Alena
"""

import sys
import os
import time
from PyQt5 import QtGui,QtWidgets,QtCore,QtNetwork
from datetime import datetime
import numpy as NP
from astropy.time import Time, TimeDelta
import struct
import winsound
import ntplib
from time import ctime

class NewAntTest(QtWidgets.QMainWindow):
    def SendTimePacket(self):
        client = ntplib.NTPClient()
        try:
            response = client.request('192.168.0.2')
            self.NTPState = True            
            print (ctime(response.tx_time))
            print (response.offset)
  #          _date = time.strftime('%Y-%m-%d',time.localtime(response.tx_time)) 
   #         _time = time.strftime('%X',time.localtime(response.tx_time)) 
  #          os.system('date {} && time {}'.format(_date,_time))            
        except (ntplib.NTPException):
            self.NTPState = False            
        self.NTPSync.setPixmap(self.redGreen(self.NTPState))
           
    def onTimer(self):
        timeStr=Time(datetime.utcnow(), scale='utc').iso.split('.')[0]
        self.curTime.setText(timeStr.split(" ")[1])
        #print('write ' + timeStr.split(" ")[1])           
        dateStr=Time(datetime.utcnow(), scale='utc').iso.split(' ')[0]
        self.curDate.setText(dateStr)        
        if (self.cmd < 200):
            self.cmd = 200;
        else: 
            self.cmd = 100;
            self.SendTimePacket();
            
        self.SrhAntSocket.writeDatagram(QtCore.QByteArray(struct.pack('!16sHHHLL',b'_Srh_Net_Packet_',0,self.cmd,0,0,0)),QtNetwork.QHostAddress('192.168.0.168'),9998)

        testSocket=QtNetwork.QTcpSocket()
        testSocket.connectToHost('192.168.0.1',80)
        if testSocket.waitForConnected() == True:
            self.Network.setPixmap(self.greenBox)
        else:
            self.Network.setPixmap(self.redBox)
        testSocket.close()
        
    def onSrhAntSocketReady(self):
        buf = self.SrhAntSocket.readDatagram(40)
        if('%c'%buf[0][0]=='G'):
            GPSpacket = struct.unpack('<18sHLLLLf',QtCore.QByteArray(buf[0]));
            Secs     = GPSpacket[2]
            Longitude= GPSpacket[4]/10000000
            Latitude = GPSpacket[5]/10000000
            Altitude = GPSpacket[6]
            print('%.3f'%Longitude,'%.3f'%Latitude,'%.3f'%Altitude)
            print("%02d:%02d:%02d"%((int(Secs/3600%24)),(int(Secs/60%60)),(Secs%60)))
            self.Latitude.setText('%.3f'%Latitude)
            self.Longitude.setText('%.3f'%Longitude)
            self.Altitude.setText('%.3f'%Altitude)
        else:
#    def onSrhAntSocketReady(self):
#        buf = self.SrhAntSocket.readDatagram(40)
            packet = struct.unpack('<16sHHiLLHHHH',QtCore.QByteArray(buf[0]));
            AzState=packet[6]
            AzActSpeed=packet[7]
            ElState=packet[8]
            ElActSpeed=packet[9]
      #  print("%02d:%02d:%02d"%((int(packet[4]/3600%24)),(int(packet[4]/60%60)),(packet[4]%60)))
            if(AzActSpeed & 0x8000):
                AzSign=-1
                AzActSpeed ^= 0xFFFF
                AzActSpeed += 1;
            else:
                AzSign=1
                
            if(ElActSpeed & 0x8000):                
                ElSign=-1
                ElActSpeed ^= 0xFFFF
                ElActSpeed += 1;
            else:
                ElSign=1
    
            speedStrAz=('%.3f '%(AzActSpeed * AzSign * self.RPMlimit/0x4000))
            speedStrEl=('%.3f '%(ElActSpeed * ElSign * self.RPMlimit/0x4000))
        
            self.AzActualSpeed.setText(speedStrAz)
            self.VLTStateAz.setPixmap(self.redGreen(AzState & 0x0001))
            self.FCStateAz.setPixmap(self.redGreen(AzState & 0x0002))
            self.CoastStateAz.setPixmap(self.redGreen(AzState & 0x0004))
            if(AzState & 0x0008):
                self.AlarmAz = ~self.AlarmAz
            else:
                self.AlarmAz = False            
            self.AlarmStateAz.setPixmap(self.redGray(self.AlarmAz)) 
                
            self.WarningStateAz.setPixmap(self.redGreen(~(AzState & 0x0080)))
            if(AzState & 0x0080):
                self.WarningAz = ~self.WarningAz
            else:
                self.WarningAz = False            
            self.WarningStateAz.setPixmap(self.redGray(self.WarningAz)) 

        
            self.ReferenceStateAz.setPixmap(self.redGreen(AzState & 0x0100))
            self.AutoModeStateAz.setPixmap(self.redGreen(AzState & 0x0200))
            self.InFrequencyRangeStateAz.setPixmap(self.redGreen(AzState & 0x0400))
            self.RunStateAz.setPixmap(self.redGreen(AzState & 0x0800))
            self.VoltageWarningStateAz.setPixmap(self.redGreen(~(AzState & 0x2000)))
            self.CurLimitStateAz.setPixmap(self.redGreen(~(AzState & 0x4000)))
            self.ThermalWarningStateAz.setPixmap(self.redGreen(~(AzState & 0x8000)))
            
            self.ElActualSpeed.setText(speedStrEl)
            self.VLTStateEl.setPixmap(self.redGreen(ElState & 0x0001))
            self.FCStateEl.setPixmap(self.redGreen(ElState & 0x0002))
            self.CoastStateEl.setPixmap(self.redGreen(ElState & 0x0004))
            if(ElState & 0x0008):
                self.AlarmEl = ~self.AlarmEl
            else:
                self.AlarmEl = False            
            self.AlarmStateEl.setPixmap(self.redGray(self.AlarmEl)) 
            
            if(ElState & 0x0080):
                self.WarningEl = ~self.WarningEl
            else:
                self.WarningEl = False            
            self.WarningStateEl.setPixmap(self.redGray(self.WarningEl))         
            self.ReferenceStateEl.setPixmap(self.redGreen(ElState & 0x0100))
            self.AutoModeStateEl.setPixmap(self.redGreen(ElState & 0x0200))
            self.InFrequencyRangeStateEl.setPixmap(self.redGreen(AzState & 0x0400))
            self.RunStateEl.setPixmap(self.redGreen(ElState & 0x0800))
            self.VoltageWarningStateEl.setPixmap(self.redGreen(~(ElState & 0x2000)))
            self.CurLimitStateEl.setPixmap(self.redGreen(~(ElState & 0x4000)))
            self.ThermalWarningStateEl.setPixmap(self.redGreen(~(ElState & 0x8000)))

    def redGreen(self,value):
        if(value):
            return self.greenBox
        else:
            return self.redBox
            
    def redGray(self,value):
        if(value):
            return self.redBox
        else:
            return self.grayBox
        
        
#    def onNTPSocketReady(self):
#        buf = self.NTPSocket.readDatagram(48)
#        print('NTP '+buf)
#        
    def onPowerButton(self,value):
        timeStr=Time(datetime.utcnow(), scale='utc').iso.split('.')[0]
        if(self.powerButton.isChecked()):
            self.powerButton.setStyleSheet('QPushButton {color: green}')
            self.Log.append('%s %d %s'%(timeStr,value,'ON'))

        else:
            self.powerButton.setStyleSheet('QPushButton {color: gray}')
            self.Log.append('%s %d %s'%(timeStr,value,'OFF'))

            
    def onAntButton1(self,value):
        timeStr=Time(datetime.utcnow(), scale='utc').iso.split('.')[0]
        self.Log.append('%s %d %s'%(timeStr,value,self.sender().text()))
        
    def onAntButton2(self,value):
        timeStr=Time(datetime.utcnow(), scale='utc').iso.split('.')[0]
        self.Log.append('%s %d %s'%(timeStr,value,self.sender().text()))
        
    def onAntButton3(self,value):
        timeStr=Time(datetime.utcnow(), scale='utc').iso.split('.')[0]
        self.Log.append('%s %d %s'%(timeStr,value,self.sender().text()))
        
    def onForw(self,value):
        timeStr=Time(datetime.utcnow(), scale='utc').iso.split('.')[0]
        self.Log.append('%s %d %s'%(timeStr,value,'Forward'))
        ds=int((self.AzDesiredSpeed.value())*0x4000/self.RPMlimit)-16
        self.SrhAntSocket.writeDatagram(QtCore.QByteArray(struct.pack('!16sHHhLL',b'_Srh_Net_Packet_',0,102,ds,0,0)),QtNetwork.QHostAddress('192.168.0.168'),9998)        
  ###  разобраться с 0 если он <0 выдает-16 
        
    def onBack(self,value):
        timeStr=Time(datetime.utcnow(), scale='utc').iso.split('.')[0]
        ds=-int(((self.AzDesiredSpeed.value()*0x4000/self.RPMlimit)-16))
        self.Log.append('%s %d %s'%(timeStr,value,'Backward'))
        self.SrhAntSocket.writeDatagram(QtCore.QByteArray(struct.pack('!16sHHhLL',b'_Srh_Net_Packet_',0,102,ds,0,0)),QtNetwork.QHostAddress('192.168.0.168'),9998)
        
    def onDown(self,value):
        timeStr=Time(datetime.utcnow(), scale='utc').iso.split('.')[0]
        ds=int(((self.ElDesiredSpeed.value()*0x4000/self.RPMlimit)-16))
        self.Log.append('%s %d %s'%(timeStr,value,'Up'))
        self.SrhAntSocket.writeDatagram(QtCore.QByteArray(struct.pack('!16sHHhLL',b'_Srh_Net_Packet_',0,104,ds,0,0)),QtNetwork.QHostAddress('192.168.0.168'),9998)
        
    def onUp(self,value):
        timeStr=Time(datetime.utcnow(), scale='utc').iso.split('.')[0]
        ds=-int(((self.ElDesiredSpeed.value()*0x4000/self.RPMlimit)-16))
        self.Log.append('%s %d %s'%(timeStr,value,'Down'))
        self.SrhAntSocket.writeDatagram(QtCore.QByteArray(struct.pack('!16sHHhLL',b'_Srh_Net_Packet_',0,104,ds,0,0)),QtNetwork.QHostAddress('192.168.0.168'),9998)
        
    def onStopAz(self):
        timeStr=Time(datetime.utcnow(), scale='utc').iso.split('.')[0]
        self.Log.append('%s %s'%(timeStr,'Stop'))
        self.SrhAntSocket.writeDatagram(QtCore.QByteArray(struct.pack('!16sHHhLL',b'_Srh_Net_Packet_',0,101,0,0,0)),QtNetwork.QHostAddress('192.168.0.168'),9998)        
        self.Forw.setChecked(False)
        self.Back.setChecked(False)
        
    def onStopElev(self):
        timeStr=Time(datetime.utcnow(), scale='utc').iso.split('.')[0]
        self.Log.append('%s %s'%(timeStr,'Stop'))
        self.SrhAntSocket.writeDatagram(QtCore.QByteArray(struct.pack('!16sHHhLL',b'_Srh_Net_Packet_',0,106,0,0,0)),QtNetwork.QHostAddress('192.168.0.168'),9998)
        self.Up.setChecked(False)
        self.Down.setChecked(False)
       ### 101 заменить на 106.106 не работает
       
    def closeEvent(self, event):
        close = QtWidgets.QMessageBox.question(self, 'NewAntTest', "Are you sure?",QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if close == QtWidgets.QMessageBox.Yes:
            self.Timer.stop()
            self.SrhAntSocket.close()
            event.accept()
        else:
            event.ignore()
            
    def __init__(self, parent=None):
        self.RPMlimit=100;
        self.cmd=100; 
        QtWidgets.QMainWindow.__init__(self,parent);
        self.setGeometry(200,100,650,300);
        
        self.h_f=QtGui.QPixmap('NewAntTest_res/h_f.png')#GROUP_FAST_BACKWARD 
        self.h_b=QtGui.QPixmap('NewAntTest_res/h_bb.png')#GROUP_BACKWARD
        self.d_u=QtGui.QPixmap('NewAntTest_res/d_u.png')#GROUP_UP
        self.d_d=QtGui.QPixmap('NewAntTest_res/d_d.png')#GROUP_DOWN
        self.hd_stop=QtGui.QPixmap('NewAntTest_res/hd_stop.png')#GROUP_STOP_X
        self.redBox=QtGui.QPixmap('NewAntTest_res/redBox.png')
        self.grayBox=QtGui.QPixmap('NewAntTest_res/grayBox.png')
        self.greenBox=QtGui.QPixmap('NewAntTest_res/greenBox.png')
        
        
        
        self.Timer=QtCore.QTimer(self)
        self.Timer.timeout.connect(self.onTimer)
        self.Timer.start(1000)
        
        self.curTime=QtWidgets.QTextEdit(self);
        self.curTime.setText('00:00:00')
        self.curTime.setGeometry(100,260,70,30)
        
        self.curDate=QtWidgets.QTextEdit(self);
        self.curDate.setText('00:00:00')
        self.curDate.setGeometry(20,260,70,30)
        
        self.NTPSync=QtWidgets.QLabel(self)
        self.NTPSync.setPixmap(self.redBox)
        self.NTPSync.setGeometry(180,268,12,12)
        self.NTPSynced=False        
        self.NTPState=False
        
        self.Network=QtWidgets.QLabel(self)
        self.Network.setGeometry(560,10,30,30)
        self.NetworkSynced=False        
        self.NetworkState=False
        
        
        self.Latitude=QtWidgets.QTextEdit(self)
        self.Latitude.setText('')
        self.Latitude.setGeometry(200,170,80,25)
        self.LatitudeLabel=QtWidgets.QLabel('Latitude',self)
        self.LatitudeLabel.setGeometry(220,150,60,20)
        
        self.Longitude=QtWidgets.QTextEdit(self)
        self.Longitude.setText('')
        self.Longitude.setGeometry(285,170,80,25)
        self.LongitudeLabel=QtWidgets.QLabel('Longitude',self)
        self.LongitudeLabel.setGeometry(300,150,60,20)
        
        self.Altitude=QtWidgets.QTextEdit(self)
        self.Altitude.setText('')
        self.Altitude.setGeometry(370,170,80,25)
        self.AltitudeLabel=QtWidgets.QLabel('Altitude',self)
        self.AltitudeLabel.setGeometry(380,150,60,20)
        
        self.AzActualSpeed=QtWidgets.QTextEdit(self)
        self.AzActualSpeed.setText(' ')
        self.AzActualSpeed.setGeometry(150,43,80,23)
        self.AzActualSpeedLabel=QtWidgets.QLabel('Actual',self)
        self.AzActualSpeedLabel.setGeometry(165,25,60,20)
        
        self.AzDesiredSpeed=QtWidgets.QDoubleSpinBox(self)
        self.AzDesiredSpeed.setSingleStep(0.01)
        self.AzDesiredSpeed.setRange(0,self.RPMlimit)        
        self.AzDesiredSpeed.setGeometry(235,43,80,23)
        self.AzDesiredSpeedLabel=QtWidgets.QLabel('Desired',self)
        self.AzDesiredSpeedLabel.setGeometry(245,25,60,20)
        
        
        self.ElActualSpeed=QtWidgets.QTextEdit(self)
        self.ElActualSpeed.setText(' ')
        self.ElActualSpeed.setGeometry(350,43,80,23)
        self.ElActualSpeedLabel=QtWidgets.QLabel('Actual',self)
        self.ElActualSpeedLabel.setGeometry(370,25,60,20)
        
        self.ElDesiredSpeed=QtWidgets.QDoubleSpinBox(self)
        self.ElDesiredSpeed.setSingleStep(0.1)
        self.ElDesiredSpeed.setRange(0,self.RPMlimit)
        self.ElDesiredSpeed.setGeometry(435,43,80,23)
        self.ElDesiredSpeedLabel=QtWidgets.QLabel('Desired',self)
        self.ElDesiredSpeedLabel.setGeometry(440,25,60,20)
        
        self.Azimuth=QtWidgets.QLabel('AZIMUTH',self)
        self.Azimuth.setGeometry(200,5,60,20)
        
        self.Elevation=QtWidgets.QLabel('ELEVATION',self)
        self.Elevation.setGeometry(400,5,60,20)
        
        
        
#        self.ClientSocket=QtNetwork.QUdpSocket()
 #       self.ClientSocket.bind(QtNetwork.QHostAddress.Any,0)
 #       self.ClientSocket.readyRead.connect(self.onClientSocketReady)
        
        self.powerLabel=QtWidgets.QLabel(self)
        self.powerLabel.setGeometry(80,115,20,30)
        self.powerState=QtWidgets.QLabel(self)
        self.powerState.setGeometry(80,112,20,20)
        self.powerButton=QtWidgets.QPushButton('ON/OFF',self)
        self.powerButton.setGeometry(580,10,60,25)
        self.powerButton.setCheckable(True)        
        self.powerButton.clicked.connect(self.onPowerButton)
        pal = self.powerButton.palette()
        pal.setColor(QtGui.QPalette.Button,QtGui.QColor('red'))
        self.powerButton.setAutoFillBackground(True)
        self.powerButton.setStyleSheet('QPushButton {color: green}') 
        self.powerButton.setPalette(pal)
        self.powerButton.update()
        
        
        self.AntButton1=QtWidgets.QPushButton('ANT1',self)
        self.AntButton1.setCheckable(True)
        self.AntButton1.setGeometry(20,10,40,30)
        self.AntButton1.toggled.connect(self.onAntButton1)
        
        self.AntButton2=QtWidgets.QPushButton('ANT2',self)
        self.AntButton2.setCheckable(True)
        self.AntButton2.setGeometry(60,10,40,30)
        self.AntButton2.toggled.connect(self.onAntButton2)
        
        self.AntButton3=QtWidgets.QPushButton('ANT3',self)
        self.AntButton3.setCheckable(True)
        self.AntButton3.setGeometry(100,10,40,30)
        self.AntButton3.toggled.connect(self.onAntButton3)
        
        self.Forw=QtWidgets.QPushButton(self)
        self.Forw.setCheckable(True)
        self.Forw.setIcon(QtGui.QIcon(self.h_f))        
        self.Forw.setIconSize(QtCore.QSize(20,20))
        self.Forw.setGeometry(245,100,40,30)
        self.Forw.toggled.connect(self.onForw)
        
        self.Back=QtWidgets.QPushButton(self)
        self.Back.setCheckable(True)
        self.Back.setIcon(QtGui.QIcon(self.h_b))
        self.Back.setIconSize(QtCore.QSize(20,20))
        self.Back.setGeometry(155,100,40,30)
        self.Back.toggled.connect(self.onBack)
        
        self.Up=QtWidgets.QPushButton(self)
        self.Up.setCheckable(True)
        self.Up.setIcon(QtGui.QIcon(self.d_u))
        self.Up.setIconSize(QtCore.QSize(20,20))
        self.Up.setGeometry(350,100,40,30)
        self.Up.toggled.connect(self.onUp)

        self.Down=QtWidgets.QPushButton(self)
        self.Down.setCheckable(True)
        self.Down.setIcon(QtGui.QIcon(self.d_d))
        self.Down.setIconSize(QtCore.QSize(20,50))
        self.Down.setGeometry(440,100,40,30)
        self.Down.toggled.connect(self.onDown)

        self.StopAz=QtWidgets.QPushButton(self)
        self.StopAz.setIcon(QtGui.QIcon(self.hd_stop))
        self.StopAz.setIconSize(QtCore.QSize(18,18))
        self.StopAz.setGeometry(200,100,40,30)
        self.StopAz.clicked.connect(self.onStopAz)

        self.StopElev=QtWidgets.QPushButton(self)
        self.StopElev.setIcon(QtGui.QIcon(self.hd_stop))
        self.StopElev.setIconSize(QtCore.QSize(18,18))
        self.StopElev.setGeometry(395,100,40,30)
        self.StopElev.clicked.connect(self.onStopElev)
        
        self.VLTStateAz=QtWidgets.QLabel(self)
        self.VLTStateAz.setPixmap(self.redBox)
        self.VLTStateAz.setGeometry(20,70,12,12)        
        self.VLTStateAzLabel=QtWidgets.QLabel("VLT ready",self)
        self.VLTStateAzLabel.setGeometry(35,60,120,30)        
        
        self.VLTStateEl=QtWidgets.QLabel(self)
        self.VLTStateEl.setPixmap(self.redBox)
        self.VLTStateEl.setGeometry(618,70,12,12) 
        self.VLTStateElLabel=QtWidgets.QLabel("VLT ready",self)
        self.VLTStateElLabel.setGeometry(495,60,120,30) 
        self.VLTStateElLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)         

        self.FCStateAz=QtWidgets.QLabel(self)
        self.FCStateAz.setPixmap(self.redBox)
        self.FCStateAz.setGeometry(20,85,12,12)
        self.FCTStateAzLabel=QtWidgets.QLabel("FC ready",self)
        self.FCTStateAzLabel.setGeometry(35,75,120,30)
        
        self.FCStateEl=QtWidgets.QLabel(self)        
        self.FCStateEl.setPixmap(self.redBox)
        self.FCStateEl.setGeometry(618,85,12,12)
        self.FCStateElLabel=QtWidgets.QLabel("FC ready",self)
        self.FCStateElLabel.setGeometry(495,75,120,30)
        self.FCStateElLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
         
        self.CoastStateAz=QtWidgets.QLabel(self)        
        self.CoastStateAz.setPixmap(self.redBox)
        self.CoastStateAz.setGeometry(20,100,12,12)        
        self.CoastStateAzLabel=QtWidgets.QLabel("Coasting stop",self)
        self.CoastStateAzLabel.setGeometry(35,90,120,30)
        
        self.CoastStateEl=QtWidgets.QLabel(self)        
        self.CoastStateEl.setPixmap(self.redBox)
        self.CoastStateEl.setGeometry(618,100,12,12)
        self.CoastStateElLabel=QtWidgets.QLabel("Coasting stop",self)
        self.CoastStateElLabel.setGeometry(495,90,120,30)        
        self.CoastStateElLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)         
        
        self.AlarmStateAz=QtWidgets.QLabel(self)
        self.AlarmStateAz.setPixmap(self.redBox)
        self.AlarmStateAz.setGeometry(20,115,12,12)        
        self.AlarmStateAzLabel=QtWidgets.QLabel("Alarm",self)
        self.AlarmStateAzLabel.setGeometry(35,105,120,30)
        
        self.AlarmStateEl=QtWidgets.QLabel(self)
        self.AlarmStateEl.setPixmap(self.redBox)
        self.AlarmStateEl.setGeometry(618,115,12,12)
        self.AlarmStateElLabel=QtWidgets.QLabel("Alarm",self)
        self.AlarmStateElLabel.setGeometry(495,105,120,30)        
        self.AlarmStateElLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)         
        
        self.RunStateAz=QtWidgets.QLabel(self)
        self.RunStateAz.setPixmap(self.redBox)
        self.RunStateAz.setGeometry(20,130,12,12)        
        self.RunStateAzLabel=QtWidgets.QLabel("Running",self)
        self.RunStateAzLabel.setGeometry(35,120,120,30)
        
        self.RunStateEl=QtWidgets.QLabel(self)
        self.RunStateEl.setPixmap(self.redBox)
        self.RunStateEl.setGeometry(618,130,12,12)
        self.RunStateElLabel=QtWidgets.QLabel("Running",self)
        self.RunStateElLabel.setGeometry(495,120,120,30)        
        self.RunStateElLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)         
        
        self.WarningStateAz=QtWidgets.QLabel(self)
        self.WarningStateAz.setPixmap(self.redBox)
        self.WarningStateAz.setGeometry(20,145,12,12)        
        self.WarningStateAzLabel=QtWidgets.QLabel("Warning",self)
        self.WarningStateAzLabel.setGeometry(35,135,120,30)
        
        self.WarningStateEl=QtWidgets.QLabel(self)
        self.WarningStateEl.setPixmap(self.redBox)
        self.WarningStateEl.setGeometry(618,145,12,12)
        self.WarningStateElLabel=QtWidgets.QLabel("Warning",self)
        self.WarningStateElLabel.setGeometry(495,135,120,30)        
        self.WarningStateElLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)         
        
        self.ReferenceStateAz=QtWidgets.QLabel(self)
        self.ReferenceStateAz.setPixmap(self.redBox)
        self.ReferenceStateAz.setGeometry(20,160,12,12)        
        self.ReferenceStateAzLabel=QtWidgets.QLabel("Reference",self)
        self.ReferenceStateAzLabel.setGeometry(35,150,120,30)
        
        self.ReferenceStateEl=QtWidgets.QLabel(self)
        self.ReferenceStateEl.setPixmap(self.redBox)
        self.ReferenceStateEl.setGeometry(618,160,12,12)
        self.ReferenceStateElLabel=QtWidgets.QLabel("Reference",self)
        self.ReferenceStateElLabel.setGeometry(495,150,120,30)        
        self.ReferenceStateElLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)         
        
        self.AutoModeStateAz=QtWidgets.QLabel(self)
        self.AutoModeStateAz.setPixmap(self.redBox)
        self.AutoModeStateAz.setGeometry(20,175,12,12)        
        self.AutoModeStateAzLabel=QtWidgets.QLabel("Auto mode",self)
        self.AutoModeStateAzLabel.setGeometry(35,165,120,30)
        
        self.AutoModeStateEl=QtWidgets.QLabel(self)
        self.AutoModeStateEl.setPixmap(self.redBox)
        self.AutoModeStateEl.setGeometry(618,175,12,12)
        self.AutoModeStateElLabel=QtWidgets.QLabel("Auto mode",self)
        self.AutoModeStateElLabel.setGeometry(495,165,120,30)        
        self.AutoModeStateElLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)         
        
        self.InFrequencyRangeStateAz=QtWidgets.QLabel(self)
        self.InFrequencyRangeStateAz.setPixmap(self.redBox)
        self.InFrequencyRangeStateAz.setGeometry(20,190,12,12)        
        self.InFrequencyRangeStateAzLabel=QtWidgets.QLabel("In frequency range",self)
        self.InFrequencyRangeStateAzLabel.setGeometry(35,180,120,30)
        
        self.InFrequencyRangeStateEl=QtWidgets.QLabel(self)
        self.InFrequencyRangeStateEl.setPixmap(self.redBox)
        self.InFrequencyRangeStateEl.setGeometry(618,190,12,12)
        self.InFrequencyRangeStateElLabel=QtWidgets.QLabel("In frequency range",self)
        self.InFrequencyRangeStateElLabel.setGeometry(495,180,120,30)        
        self.InFrequencyRangeStateElLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
      #  self.InFrequencyRangeStateElLabel.setFrameShape(QtGui.QFrame.Panel)         
        
        self.VoltageWarningStateAz=QtWidgets.QLabel(self)
        self.VoltageWarningStateAz.setPixmap(self.redBox)
        self.VoltageWarningStateAz.setGeometry(20,205,12,12)        
        self.VoltageWarningStateAzLabel=QtWidgets.QLabel("Voltage warning",self)
        self.VoltageWarningStateAzLabel.setGeometry(35,195,120,30)
        
        self.VoltageWarningStateEl=QtWidgets.QLabel(self)
        self.VoltageWarningStateEl.setPixmap(self.redBox)
        self.VoltageWarningStateEl.setGeometry(618,205,12,12)
        self.VoltageWarningStateElLabel=QtWidgets.QLabel("Voltage warning",self)
        self.VoltageWarningStateElLabel.setGeometry(495,195,120,30)        
        self.VoltageWarningStateElLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)         
        
        
        self.CurLimitStateAz=QtWidgets.QLabel(self)
        self.CurLimitStateAz.setPixmap(self.redBox)
        self.CurLimitStateAz.setGeometry(20,220,12,12)        
        self.CurLimitStateAzLabel=QtWidgets.QLabel("Current limit",self)
        self.CurLimitStateAzLabel.setGeometry(35,210,120,30)
        
        self.CurLimitStateEl=QtWidgets.QLabel(self)
        self.CurLimitStateEl.setPixmap(self.redBox)
        self.CurLimitStateEl.setGeometry(618,220,12,12)
        self.CurLimitStateElLabel=QtWidgets.QLabel("Current limit",self)
        self.CurLimitStateElLabel.setGeometry(495,210,120,30)        
        self.CurLimitStateElLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)         
        
        self.ThermalWarningStateAz=QtWidgets.QLabel(self)
        self.ThermalWarningStateAz.setPixmap(self.redBox)
        self.ThermalWarningStateAz.setGeometry(20,235,12,12)        
        self.ThermalWarningStateAzLabel=QtWidgets.QLabel("Thermal warning",self)
        self.ThermalWarningStateAzLabel.setGeometry(35,225,120,30)
        
        self.ThermalWarningStateEl=QtWidgets.QLabel(self)
        self.ThermalWarningStateEl.setPixmap(self.redBox)
        self.ThermalWarningStateEl.setGeometry(618,235,12,12)
        self.ThermalWarningStateElLabel=QtWidgets.QLabel("Thermal warning",self)
        self.ThermalWarningStateElLabel.setGeometry(495,225,120,30)        
        self.ThermalWarningStateElLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)         
        
        
        
        self.Log=QtWidgets.QTextEdit(self); 
        self.Log.setGeometry(200,200,250,90);
        
        self.SrhAntSocket=QtNetwork.QUdpSocket()
        self.SrhAntSocket.bind(QtNetwork.QHostAddress.Any,9998)
        self.SrhAntSocket.readyRead.connect(self.onSrhAntSocketReady)

#        self.NTPSocket=QtNetwork.QUdpSocket()
#        self.NTPSocket.bind(QtNetwork.QHostAddress.Any,1234)
#        self.NTPSocket.readyRead.connect(self.onNTPSocketReady)
#        
        self.AlarmAz=(False)
        self.AlarmEl=(False)
        self.WarningAz=(False)
        self.WarningEl=(False)

        
application = QtWidgets.QApplication.instance();
if not application:
    application = QtWidgets.QApplication(sys.argv);
    
mainWidget=NewAntTest();
mainWidget.show();
sys.exit(application.exec_());
