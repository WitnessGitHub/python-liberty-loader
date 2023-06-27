#!/usr/bin/env python
import re
import threading
import tkinter
from time import sleep

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox
import sys
import os
from datetime import datetime

from img_files import ImgFiles
from lib_jlink import JLink
from mpu import Mpu


class MainWindow(QtWidgets.QMainWindow):

    SN_MAIN = 52003835
    SN_NETW = 52003834
    SN_REM = 601015761
    SN_GW = 601015769

    DEVICE_TYPE_REM = 1
    DEVICE_TYPE_MAIN = 2
    DEVICE_TYPE_NETW = 3
    DEVICE_TYPE_GW = 4

    LIB_VERSION = 'Microbot Medical Loader      Version: 0.95 '

    MAX_ID_VALUE = 1000000

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        #Load the UI Page
        # self.ui_file = os.environ['WORKBENCH_PATH'] + "/win.ui"
        self.ui_file = "gui/loader_win.ui"
        uic.loadUi(self.ui_file, self)
        self.checkBox.setChecked(True)

        self.files = ImgFiles()

        self.mpuMain = Mpu(self.SN_MAIN, self.DEVICE_TYPE_MAIN)
        self.mpuNetw = Mpu(self.SN_NETW, self.DEVICE_TYPE_NETW)
        self.mpuGw = Mpu(self.SN_GW, self.DEVICE_TYPE_GW)
        self.mpuRem = Mpu(self.SN_REM, self.DEVICE_TYPE_REM)

        self.varCurrVersionNbrMp.setText("__.__.__")
        self.varCurrVersionNbrNw.setText("__.__.__")
        self.varCurrVersionNbrGw.setText("__.__.__")
        self.varCurrVersionNbrRem.setText("__.__.__")

        self.released_imgs_update(self.checkBox.isChecked())
        self.checkBox.released.connect(self.changeSet)

        threading.Timer(2.0, self.delay_init).start()

    def delay_init(self):
        # print('start JLink control')
        self.taskJLinkControl = threading.Thread(target=self.remTask, daemon=True).start()
        self.taskJLinkControl = threading.Thread(target=self.netwTask, daemon=True).start()
        self.taskJLinkControl = threading.Thread(target=self.mainTask, daemon=True).start()
        self.taskJLinkControl = threading.Thread(target=self.gwTask, daemon=True).start()

    def remTask(self):
        while True:
            self.mpuRem.checkJLink()
            self.varJLinkStateRem.setText(str(self.mpuRem.strStatus))

    def netwTask(self):
        while True:
            self.mpuNetw.checkJLink()
            self.varJLinkStateNw.setText(str(self.mpuNetw.strStatus))

    def mainTask(self):
        while True:
            self.mpuMain.checkJLink()
            self.varJLinkStateMp.setText(str(self.mpuMain.strStatus))
            if self.mpuMain.strStatus:
                self.groupBoxMain.setStyleSheet("background-color: blue;")
            else:
                self.groupBoxMain.setStyleSheet("background-color: cyan;")

    def gwTask(self):
        while True:
            self.mpuGw.checkJLink()
            self.varJLinkStateGw.setText(str(self.mpuGw.strStatus))

    def changeSet(self):
        self.released_imgs_update(self.checkBox.isChecked())

    def released_imgs_update(self, lts):
        try:
            list = self.files.list_files(lts)
            for file_name in list:
                if re.search("LIB_MAIN", file_name):
                    self.varAvailableVersionNbrMp.setText(file_name)

                if re.search("LIB_NETW", file_name):
                    self.varAvailableVersionNbrNw.setText(file_name)

                if re.search("LIB_GW", file_name):
                    self.varAvailableVersionNbrGw.setText(file_name)

                if re.search("LIB_REM",file_name):
                    self.varAvailableVersionNbrRem.setText(file_name)
        except:
            self.semOk = False

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
