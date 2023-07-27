#!/usr/bin/env python
import re
import threading
from time import sleep

from PyQt6 import QtWidgets, uic
import sys

from config import Config
from img_files import ImgFiles
from mpu import Mpu


class MainWindow(QtWidgets.QMainWindow):

    DEVICE_TYPE_REM = 1
    DEVICE_TYPE_MAIN = 2
    DEVICE_TYPE_NETW = 3
    DEVICE_TYPE_GW = 4

    SN_MIN = 10000000
    SN_MAX = 1000000000

    LIB_VERSION = 'Microbot Medical Loader      Version: 1.1 '

    MAX_ID_VALUE = 1000000

    def __exit__(self):
        print('stop')
        self.taskJLinkControlRem.stop()
        self.taskJLinkControlMain.stop()
        self.taskJLinkControlNetw.stop()
        self.taskJLinkControlGw.stop()

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        #Load the UI Page
        self.ui_file = "./gui/loader_win.ui"
        uic.loadUi(self.ui_file, self)
        self.setWindowTitle(self.LIB_VERSION)
        self.checkBox_lts.setChecked(True)
        self.checkBox_mbot.setChecked(False)

        self.config = Config()
        self.config.load()
        self.files = ImgFiles()

        self.mpuMain = Mpu(self.config.set['main'], self.DEVICE_TYPE_MAIN)
        self.mpuNetw = Mpu(self.config.set['netw'], self.DEVICE_TYPE_NETW)
        self.mpuGw = Mpu(self.config.set['gw'], self.DEVICE_TYPE_GW)
        self.mpuRem = Mpu(self.config.set['rem'], self.DEVICE_TYPE_REM)

        self.labelSnMain.setText('SN: ' + str(self.config.set['main']))
        self.labelSnNetw.setText('SN: ' + str(self.config.set['netw']))
        self.labelSnGw.setText('SN: ' + str(self.config.set['gw']))
        self.labelSnRem.setText('SN: ' + str(self.config.set['rem']))


        self.released_imgs_update(self.checkBox_lts.isChecked(), self.checkBox_mbot.isChecked())
        self.released_imgs_update(self.checkBox_lts.isChecked(), self.checkBox_mbot.isChecked())
        # checkbox connection
        self.checkBox_lts.released.connect(self.changeSetLts)
        self.checkBox_mbot.released.connect(self.changeSetMbot)
        # productline feature
        # self.checkBox.setEnabled(False)
        # buttons connection
        self.pushButtonUpdateImages.clicked.connect(self.funUpdateImages)
        self.pushButtonUpdateId.clicked.connect(self.funUpdateId)
        self.toolButtonCnfgMain.clicked.connect(self.funConfigMaibnSn)
        self.toolButtonCnfgNetw.clicked.connect(self.funConfigNetwSn)
        self.toolButtonCnfgMGw.clicked.connect(self.funConfigGwSn)
        self.toolButtonCnfgRem.clicked.connect(self.funConfigRemSn)

        threading.Timer(2.0, self.delay_init).start()

    def funConfigMaibnSn(self):
        newSn, ok = QtWidgets.QInputDialog.getInt(self, 'Main JLinl SN', 'Currrent JLink SN:', self.config.set['main'], self.SN_MIN, self.SN_MAX)
        if ok:
            self.config.set['main'] = newSn
            self.config.save()
            self.labelSnMain.setText('SN: ' + str(self.config.set['main']))

    def funConfigNetwSn(self):
        newSn, ok = QtWidgets.QInputDialog.getInt(self, 'Network JLinl SN', 'Currrent JLink SN:', self.config.set['netw'], self.SN_MIN, self.SN_MAX)
        if ok:
            self.config.set['netw'] = newSn
            self.config.save()
            self.   labelSnNetw.setText('SN: ' + str(self.config.set['netw']))

    def funConfigGwSn(self):
        newSn, ok = QtWidgets.QInputDialog.getInt(self, 'Guidewire JLinl SN', 'Currrent JLink SN:', self.config.set['gw'], self.SN_MIN, self.SN_MAX)
        if ok:
            self.config.set['gw'] = newSn
            self.config.save()
            self.labelSnGw.setText('SN: ' + str(self.config.set['gw']))

    def funConfigRemSn(self):
        newSn, ok = QtWidgets.QInputDialog.getInt(self, 'Remote Ctr JLinl SN', 'Currrent JLink SN:', self.config.set['rem'], self.SN_MIN, self.SN_MAX)
        if ok:
            self.config.set['rem'] = newSn
            self.config.save()
            self.labelSnRem.setText('SN: ' + str(self.config.set['rem']))

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
            sleep(1)

    def netwTask(self):
        while True:
            self.mpuNetw.checkJLink()
            self.varJLinkStateNw.setText(str(self.mpuNetw.strStatus))
            _strVer, _strId = self.mpuNetw.getStrVerId()
            self.varCurrVersionNbrNw.setText(_strVer)
            self.varCurrIdNbrNw.setText(_strId)
            sleep(1)

    def mainTask(self):
        while True:
            self.mpuMain.checkJLink()
            self.varJLinkStateMp.setText(str(self.mpuMain.strStatus))
            _strVer, _strId = self.mpuMain.getStrVerId()
            self.varCurrVersionNbrMp.setText(_strVer)
            self.varCurrIdNbrMp.setText(_strId)
            sleep(1)

    def gwTask(self):
        while True:
            self.mpuGw.checkJLink()
            self.varJLinkStateGw.setText(str(self.mpuGw.strStatus))
            _strVer, _strId = self.mpuGw.getStrVerId()
            self.varCurrVersionNbrGw.setText(_strVer)
            self.varCurrIdNbrGw.setText(_strId)
            sleep(1)

    def changeSetLts(self):
        self.released_imgs_update(self.checkBox_lts.isChecked(), self.checkBox_mbot.isChecked())
    def changeSetMbot(self):
        self.released_imgs_update(self.checkBox_lts.isChecked(), self.checkBox_mbot.isChecked())

    def released_imgs_update(self, lts, mbot):
        try:
            list = self.files.list_files(lts == False, mbot)
            for file_name in list:
                if re.search("_MAIN_", file_name):
                    self.mpuMain.fileName = file_name
                    self.varAvailableVersionNbrMp.setText(self.mpuMain.getStrVerCs())

                if re.search("_NETW_", file_name):
                    self.mpuNetw.fileName = file_name
                    self.varAvailableVersionNbrNw.setText(self.mpuNetw.getStrVerCs())

                if re.search("_GW_", file_name):
                    self.mpuGw.fileName = file_name
                    self.varAvailableVersionNbrGw.setText(self.mpuGw.getStrVerCs())

                if re.search("_REM_",file_name):
                    self.mpuRem.fileName = file_name
                    self.varAvailableVersionNbrRem.setText(self.mpuRem.getStrVerCs())
        except:
            self.semOk = False

    def funUpdateImages(self):
        self.mpuMain.req_flash_image(self.files.path)
        self.mpuNetw.req_flash_image(self.files.path)
        self.mpuGw.req_flash_image(self.files.path)
        self.mpuRem.req_flash_image(self.files.path)

    def funUpdateId(self):
        _new_id = 0
        try:
            _new_id = int(self.lineNewId.text())
        except ValueError:
            self.labelNewIdStatus.setText('not correct id')
            self.lineNewId.setText('')
            return
        if _new_id >= self.MAX_ID_VALUE or _new_id == 0:
            self.labelNewIdStatus.setText('not correct id')
            self.lineNewId.setText('')
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
