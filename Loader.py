#!/usr/bin/env python
import re
import signal
import threading
from time import sleep

from PyQt6 import QtWidgets, uic

import sys

from config import Config
from img_files import ImgFiles, SetVersions
from mpu import Mpu
from lib_jlink import JLink

class MainWindow(QtWidgets.QMainWindow):

    DEVICE_TYPE_REM = 1
    DEVICE_TYPE_MAIN = 2
    DEVICE_TYPE_NETW = 3
    DEVICE_TYPE_GW = 4

    SN_MIN = 10000000
    SN_MAX = 1000000000

    LIB_VERSION = 'Microbot Medical Loader      Version: 1.9 '

    MAX_ID_VALUE = 1000000
    MAX_IDLE_TIME = 5*60 # 5min

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        #Base Patch building
        rootPath = ""
        # print(sys.platform, os.name)
        if sys.platform == "win32":
            rootPath = "C:" # win32
        basePath = rootPath + "/Users/Shared/Loader" # macOs

        #Load the UI Page
        self.ui_file = basePath + "/gui/loader_win.ui"
        uic.loadUi(self.ui_file, self)
        self.setWindowTitle(self.LIB_VERSION)

        self.config = Config(basePath)
        self.config.load()
        self.files = ImgFiles(basePath)

        self.mpuMain = Mpu(self.config.set['main'], self.DEVICE_TYPE_MAIN)
        self.mpuNetw = Mpu(self.config.set['netw'], self.DEVICE_TYPE_NETW)
        self.mpuGw = Mpu(self.config.set['gw'], self.DEVICE_TYPE_GW)
        self.mpuRem = Mpu(self.config.set['rem'], self.DEVICE_TYPE_REM)

        self.labelSnMain.setText('SN: ' + str(self.config.set['main']))
        self.labelSnNetw.setText('SN: ' + str(self.config.set['netw']))
        self.labelSnGw.setText('SN: ' + str(self.config.set['gw']))
        self.labelSnRem.setText('SN: ' + str(self.config.set['rem']))


        # buttons connection
        self.pushButtonUpdateImages.clicked.connect(self.funUpdateImages)
        self.pushButtonUpdateId.clicked.connect(self.funUpdateId)
        self.toolButtonCnfgMain.clicked.connect(self.funConfigMaibnSn)
        self.toolButtonCnfgNetw.clicked.connect(self.funConfigNetwSn)
        self.toolButtonCnfgMGw.clicked.connect(self.funConfigGwSn)
        self.toolButtonCnfgRem.clicked.connect(self.funConfigRemSn)
        self.toolButtonCnfgSetEnb.clicked.connect(self.funConfigSetEnb)
        self.toolButtonCnfgSetEnb.setEnabled(False)# config set button is disabled

        threading.Timer(2.0, self.delay_init).start()

        # self.comboBox.addItems(["STABLE", "MBOT", "LTS"])
        self.comboBox.addItems(["MBOT"])
        # self.comboBox.addItems(["STABLE", "MBOT"])
        self.comboBox.currentIndexChanged.connect(self.index_changed)
        self.set_ver = SetVersions.MBOT
        self.released_imgs_update(SetVersions.MBOT)
        self.comboBox.setEnabled(False)#self.config.set['setv'] == 1)

        # Init idle timer
        self.countIdleTime = 0
        threading.Timer(1.0, self.incIdleCounter).start()
        self.semTo = True
        
  
    def closeEvent(self, event):
        self.semTo = False

    def incIdleCounter(self):
        self.countIdleTime = self.countIdleTime + 1
        if self.countIdleTime > self.MAX_IDLE_TIME:
            # print("too long time")
            self.semTo = False
            self.mpuMain.libExit()
            self.mpuNetw.libExit()
            self.mpuGw.libExit()
            self.mpuRem.libExit()
            sleep(1)
            self.destroy()
        else:
            if self.semTo == True:
                threading.Timer(1, self.incIdleCounter).start()
            print("incIdleCounter", self.countIdleTime)

    def index_changed(self, ind):  # i is an int
        self.set_ver = SetVersions(ind)
        self.released_imgs_update(self.set_ver)

    def funConfigMaibnSn(self):
        newSn, ok = QtWidgets.QInputDialog.getInt(self, 'Main JLink SN', 'Currrent JLink SN:', self.config.set['main'], self.SN_MIN, self.SN_MAX)
        if ok:
            self.countIdleTime = 0
            self.mpuMain.sn = newSn
            self.config.set['main'] = newSn
            self.config.save()
            self.labelSnMain.setText('SN: ' + str(self.config.set['main']))

    def funConfigNetwSn(self):
        newSn, ok = QtWidgets.QInputDialog.getInt(self, 'Network JLink SN', 'Currrent JLink SN:', self.config.set['netw'], self.SN_MIN, self.SN_MAX)
        if ok:
            self.countIdleTime = 0
            self.mpuNetw.sn = newSn
            self.config.set['netw'] = newSn
            self.config.save()
            self.   labelSnNetw.setText('SN: ' + str(self.config.set['netw']))

    def funConfigGwSn(self):
        newSn, ok = QtWidgets.QInputDialog.getInt(self, 'Guidewire JLink SN', 'Currrent JLink SN:', self.config.set['gw'], self.SN_MIN, self.SN_MAX)
        if ok:
            self.countIdleTime = 0
            self.mpuGw.sn = newSn
            self.config.set['gw'] = newSn
            self.config.save()
            self.labelSnGw.setText('SN: ' + str(self.config.set['gw']))

    def funConfigRemSn(self):
        newSn, ok = QtWidgets.QInputDialog.getInt(self, 'Remote Ctr JLink SN', 'Currrent JLink SN:', self.config.set['rem'], self.SN_MIN, self.SN_MAX)
        if ok:
            self.countIdleTime = 0
            self.mpuRem.sn = newSn
            self.config.set['rem'] = newSn
            self.config.save()
            self.labelSnRem.setText('SN: ' + str(self.config.set['rem']))

    def funConfigSetEnb(self):
        res, ok = QtWidgets.QInputDialog.getInt(self, 'Change Versions Set', 'Status:', self.config.set['setv'], 0, 1)
        if ok:
            self.config.set['setv'] = res
            self.config.save()
            self.comboBox.setEnabled(res == 1)

    def delay_init(self):
        # print('start JLink control')
        self.taskJLinkControlRem = threading.Thread(target=self.remTask, daemon=True).start()
        self.taskJLinkControlNetw = threading.Thread(target=self.netwTask, daemon=True).start()
        self.taskJLinkControlMain = threading.Thread(target=self.mainTask, daemon=True).start()
        self.taskJLinkControlGw = threading.Thread(target=self.gwTask, daemon=True).start()

    def remTask(self):
        while True:
            self.mpuRem.checkJLink()
            self.varJLinkStateRem.setText(str(self.mpuRem.strStatus))
            _strVer, _strId = self.mpuRem.getStrVerId()
            self.varCurrVersionNbrRem.setText(_strVer)
            self.varCurrIdNbrRem.setText(_strId)

            # colored version status
            if self.mpuRem.semOk:
                if int(self.mpuRem.fileName.split('_')[2]) == self.mpuRem.ver:
                    self.varCurrVersionNbrRem.setStyleSheet("QLabel { color : green; font: 14pt}")
                else:
                    self.varCurrVersionNbrRem.setStyleSheet("QLabel { color : red; font: 16pt}")
            else:
                self.varCurrVersionNbrRem.setStyleSheet("QLabel { color : blue; font: 12pt}")
            # compare the written fw version with the received one
            if self.mpuRem.semFwUpdated:
                self.mpuRem.semFwUpdated = False
                self.varCurrVersionNbrRem.setText("Success")
                self.varCurrVersionNbrRem.setStyleSheet("QLabel { color : blue; font: 18pt}")
                sleep(0.5)
            sleep(1)

    def netwTask(self):
        while True:
            self.mpuNetw.checkJLink()
            self.varJLinkStateNw.setText(str(self.mpuNetw.strStatus))
            _strVer, _strId = self.mpuNetw.getStrVerId()
            self.varCurrVersionNbrNw.setText(_strVer)
            self.varCurrIdNbrNw.setText(_strId)

            # colored version status
            if self.mpuNetw.semOk:
                if int(self.mpuNetw.fileName.split('_')[2]) == self.mpuNetw.ver:
                    self.varCurrVersionNbrNw.setStyleSheet("QLabel { color : green; font: 14pt}")
                else:
                    self.varCurrVersionNbrNw.setStyleSheet("QLabel { color : red; font: 16pt}")
            else:
                self.varCurrVersionNbrNw.setStyleSheet("QLabel { color : blue; font: 12pt}")
            # compare the written fw version with the received one
            if self.mpuNetw.semFwUpdated:
                self.mpuNetw.semFwUpdated = False
                self.varCurrVersionNbrNw.setText("Success")
                self.varCurrVersionNbrNw.setStyleSheet("QLabel { color : blue; font: 18pt}")
                sleep(0.5)
            sleep(1)

    def mainTask(self):
        while True:
            self.mpuMain.checkJLink()
            self.varJLinkStateMp.setText(str(self.mpuMain.strStatus))
            _strVer, _strId = self.mpuMain.getStrVerId()
            self.varCurrVersionNbrMp.setText(_strVer)
            self.varCurrIdNbrMp.setText(_strId)

            # colored version status
            if self.mpuMain.semOk:
                if int(self.mpuMain.fileName.split('_')[2]) == self.mpuMain.ver:
                    self.varCurrVersionNbrMp.setStyleSheet("QLabel { color : green; font: 14pt}")
                else:
                    self.varCurrVersionNbrMp.setStyleSheet("QLabel { color : red; font: 16pt}")
            else:
                self.varCurrVersionNbrMp.setStyleSheet("QLabel { color : blue; font: 12pt}")
            # compare the written fw version with the received one
            if self.mpuMain.semFwUpdated:
                self.mpuMain.semFwUpdated = False
                self.varCurrVersionNbrMp.setText("Success")
                self.varCurrVersionNbrMp.setStyleSheet("QLabel { color : blue; font: 18pt}")
                sleep(0.5)
            sleep(1)

    def gwTask(self):
        while True:
            self.mpuGw.checkJLink()
            self.varJLinkStateGw.setText(str(self.mpuGw.strStatus))
            _strVer, _strId = self.mpuGw.getStrVerId()
            self.varCurrVersionNbrGw.setText(_strVer)
            self.varCurrIdNbrGw.setText(_strId)

            # colored version status
            if self.mpuGw.semOk:
                if int(self.mpuGw.fileName.split('_')[2]) == self.mpuGw.ver:
                    self.varCurrVersionNbrGw.setStyleSheet("QLabel { color : green; font: 14pt}")
                else:
                    self.varCurrVersionNbrGw.setStyleSheet("QLabel { color : red; font: 16pt}")
            else:
                self.varCurrVersionNbrGw.setStyleSheet("QLabel { color : blue; font: 12pt}")
            # compare the written fw version with the received one
            if self.mpuGw.semFwUpdated:
                self.mpuGw.semFwUpdated = False
                self.varCurrVersionNbrGw.setText("Success")
                self.varCurrVersionNbrGw.setStyleSheet("QLabel { color : blue; font: 18pt}")
                sleep(0.5)
            sleep(1)

    def released_imgs_update(self, set_ver):
        try:
            list = self.files.list_files(set_ver)
            # print(list)
            for file_name in list:
                if re.search("LIB_MAIN_", file_name) or re.search("MBOT_MAIN_", file_name):
                    self.mpuMain.fileName = file_name
                    self.varAvailableVersionNbrMp.setText(self.mpuMain.getStrVerCs())

                if re.search("LIB_NETW_", file_name) or re.search("MBOT_NETW_", file_name):
                    self.mpuNetw.fileName = file_name
                    self.varAvailableVersionNbrNw.setText(self.mpuNetw.getStrVerCs())

                if re.search("LIB_GW_", file_name) or re.search("MBOT_GW_", file_name):
                    self.mpuGw.fileName = file_name
                    self.varAvailableVersionNbrGw.setText(self.mpuGw.getStrVerCs())

                if re.search("LIB_REM_",file_name) or re.search("MBOT_REM_",file_name):
                    self.mpuRem.fileName = file_name
                    self.varAvailableVersionNbrRem.setText(self.mpuRem.getStrVerCs())
        except:
            self.semOk = False

    def funUpdateImages(self):
        self.countIdleTime = 0
        self.mpuMain.req_flash_image(self.files.path)
        self.mpuNetw.req_flash_image(self.files.path)
        self.mpuGw.req_flash_image(self.files.path)
        self.mpuRem.req_flash_image(self.files.path)

    def clearMsg(self):
        self.labelNewIdStatus.setText('')

    def funUpdateId(self):
        self.countIdleTime = 0
        _new_id = 0
        try:
            _new_id = int(self.lineNewId.text())
        except ValueError:
            self.labelNewIdStatus.setText('not correct id')
            self.lineNewId.setText('')
            threading.Timer(5, self.clearMsg).start()
            return
        if _new_id >= self.MAX_ID_VALUE or _new_id == 0:
            self.labelNewIdStatus.setText('not correct id')
            self.lineNewId.setText('')
            threading.Timer(5, self.clearMsg).start()
            return
        self.mpuMain.req_set_id(_new_id)
        self.mpuNetw.req_set_id(_new_id)
        self.mpuGw.req_set_id(_new_id)
        self.mpuRem.req_set_id(_new_id)

        # self.labelNewIdStatus.setText(_strRes)

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
