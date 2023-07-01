#!/usr/bin/env python
import re
import threading
import tkinter
from time import sleep

from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMessageBox, QInputDialog
import sys

from config import Config
from img_files import ImgFiles
from mpu import Mpu


class MainWindow(QtWidgets.QMainWindow):

    SN_MAIN = 52003835
    SN_NETW = 52003834
    SN_REM = 52003841
    SN_GW = 52003833

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

        self.config = Config()
        self.config.load()
        self.files = ImgFiles()

        self.mpuMain = Mpu(self.SN_MAIN, self.config.set['main'])
        self.mpuNetw = Mpu(self.SN_NETW, self.DEVICE_TYPE_NETW)
        self.mpuGw = Mpu(self.SN_GW, self.DEVICE_TYPE_GW)
        self.mpuRem = Mpu(self.SN_REM, self.DEVICE_TYPE_REM)

        self.released_imgs_update(self.checkBox.isChecked())
        # checkbox connection
        self.checkBox.released.connect(self.changeSet)
        # buttons connection
        self.pushButtonUpdateImages.clicked.connect(self.funUpdateImages)
        self.pushButtonUpdateId.clicked.connect(self.funUpdateId)
        self.toolButtonCnfgMain.clicked.connect(self.funConfigMaibnSn)
        self.toolButtonCnfgNetw.clicked.connect(self.funConfigNetwSn)
        self.toolButtonCnfgMGw.clicked.connect(self.funConfigGwSn)
        self.toolButtonCnfgRem.clicked.connect(self.funConfigRemSn)

        threading.Timer(2.0, self.delay_init).start()

    # btn = QPushButton('Set Window Title')
    # btn.clicked.connect(self.open_input_dialog)
    def funConfigMaibnSn(self):
        newSn, ok = QtWidgets.QInputDialog.getInt(self, 'Main JLinl SN', 'Currrent JLink SN:                 .', self.SN_MAIN, 10000000, 100000000, 1)
        if ok:
            self.config.set['main'] = newSn
            self.config.save()
    def funConfigNetwSn(self):
        newSn, ok = QtWidgets.QInputDialog.getInt(self, 'Network JLinl SN', 'Currrent JLink SN:                 .', self.SN_NETW, 10000000, 100000000, 1)
        if ok:
            self.config.set['netw'] = newSn
            self.config.save()

    def funConfigGwSn(self):
        newSn, ok = QtWidgets.QInputDialog.getInt(self, 'Guidewire JLinl SN', 'Currrent JLink SN:                 .', self.SN_GW, 10000000, 100000000, 1)
        if ok:
            self.config.set['gw'] = newSn
            self.config.save()

    def funConfigRemSn(self):
        newSn, ok = QtWidgets.QInputDialog.getInt(self, 'Remote Ctr JLinl SN', 'Currrent JLink SN:                 .', self.SN_REM, 10000000, 100000000, 1)
        if ok:
            self.config.set['rem'] = newSn
            self.config.save()

        # dlg = ConfigDialog()
        # if dlg.exec():
        #     print("Success!")
        # else:
        #     print("Cancel!")
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

    def changeSet(self):
        self.released_imgs_update(self.checkBox.isChecked())

    def released_imgs_update(self, lts):
        try:
            list = self.files.list_files(lts == False)
            for file_name in list:
                if re.search("LIB_MAIN", file_name):
                    self.mpuMain.fileName = file_name
                    self.varAvailableVersionNbrMp.setText(self.mpuMain.getStrVerCs())

                if re.search("LIB_NETW", file_name):
                    self.mpuNetw.fileName = file_name
                    self.varAvailableVersionNbrNw.setText(self.mpuNetw.getStrVerCs())

                if re.search("LIB_GW", file_name):
                    self.mpuGw.fileName = file_name
                    self.varAvailableVersionNbrGw.setText(self.mpuGw.getStrVerCs())

                if re.search("LIB_REM",file_name):
                    self.mpuRem.fileName = file_name
                    self.varAvailableVersionNbrRem.setText(self.mpuRem.getStrVerCs())
        except:
            self.semOk = False

    def funUpdateImages(self):
        self.mpuMain.flash_image(self.files.path)
        self.mpuNetw.flash_image(self.files.path)
        self.mpuGw.flash_image(self.files.path)
        self.mpuRem.flash_image(self.files.path)

    def funUpdateId(self):
        _new_id = 0
        try:
            _new_id = int(self.lineNewId.text())
        except ValueError:
            self.labelNewIdStatus.setText('not correct ID')
            self.lineNewId.setText('')
            return
        if _new_id >= self.MAX_ID_VALUE or _new_id == 0:
            self.labelNewIdStatus.setText('not correct ID')
            self.lineNewId.setText('')
            return
        _strRes = ''
        _sem, _out = self.mpuMain.set_id(_new_id)
        if _sem:
            _strRes += 'mp : ' + _out
        _sem, _out = self.mpuNetw.set_id(_new_id)
        if _sem:
            _strRes += 'np : ' + _out
        _sem, _out = self.mpuGw.set_id(_new_id)
        if _sem:
            _strRes += 'gp : ' + _out
        _sem, _out = self.mpuRem.set_id(_new_id)
        if _sem:
            _strRes += 'rp : ' + _out

        self.labelNewIdStatus.setText(_strRes)

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
