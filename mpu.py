import threading
from time import sleep

# from img_files import ImgFiles
from lib_jlink import JLink


class Mpu:
    def __exit__(self):
        self.semOk = False
        self.link.jlink._finalize()

    def __init__(self, sn, type):

        self.sn = sn
        self.strStatus = ''
        self.type = type
        self.semOk = False
        self.semBusy = False
        self.strOut = ""
        self.fileName = ""
        self.strFileVerCs = ""

        self.link = JLink()
        self.semOk, self.strOut = self.link.init(sn)
        print(self.semOk, self.strOut)
        self.strDeviceType = self.link.str_dev_type(type)


    def getStrVerId(self):
        _strVer = '__'
        _strId = '__'
        if self.semOk:
            _strVer = str(self.ver).zfill(6)
            _strId = str(self.id)
        return _strVer, _strId
    def getStrVerCs(self):
        _list = self.fileName.split('_')
        if len(_list) > 4:
            return 'Ver: ' + _list[2] + '   Cs: ' + _list[3]
        elif len(_list) > 3:
            return 'Ver: ' + _list[2] + '   Cs: ' + _list[3].split('.')[0]
        else:
            return ''

    def checkJLink(self):
        if self.semBusy == False:
            self.semOk, self.strOut = self.link.get_product_name(self.sn)
        else:
            print('SN ', self.sn, 'busy')
        if self.semOk and self.semBusy == False:
            self.semOk, self.strOut, self.id = self.link.read_id(self.sn)
        if self.semOk and self.semBusy == False:
            self.semOk, self.strOut, self.ver = self.link.read_info(self.sn)
        self.strStatus = self.strOut

    def flash_image(self, path):
        if self.semOk == False or self.semBusy == True:
            return
        if self.sanity_file(self.fileName):
            self.taskImgFlashing = threading.Thread(target=self.funFlashing, daemon=True, args=(path, self.fileName, self.link)).start()

    def sanity_file(self, file_name):
        if file_name == "":
            return False
        else:
            return True

    def funFlashing(self, path, file, link):
        if self.semOk == False:
            return
        if self.semBusy == True:
            sleep(0.5)
        self.semBusy = True
        print('file', path + '/' + file)
        print('start flashing')
        try:
            link.flash_img(self.sn, path + '/' + file)
        except:
            print('Cannot flash')
            self.semBusy = False
            return
        sleep(1.0)
        print('end flashing')
        _sem, _res = link.set_img_info(self.sn, file)
        self.semOk = _sem
        print('Curr State ', _sem, _res)
        self.semBusy = False

    def set_id(self, id):
        if self.semOk == False:
            return False, ' '

        if self.semBusy == True:
            sleep(0.5)
        self.semBusy = True
        sem, res = self.link.set_id(self.sn, id)
        if sem == False:
            self.semBusy = False
            return False, ' '
        sem, res, read_id = self.link.read_id(self.sn)
        print(sem, res, read_id)
        if sem:
            self.semBusy = False
            return True, "written id: " + str(read_id)
        else:
            self.semBusy = False
            return False, 'unknown id'
