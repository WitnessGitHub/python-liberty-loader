import threading
from time import sleep

# from img_files import ImgFiles
from lib_jlink import JLink


class Mpu:
    MAX_ID_VALUE = 1000000
    def __exit__(self):
        self.semOk = False
        self.link.jlink._finalize()

    def __init__(self, sn, type):

        self.sn = sn
        self.strStatus = ''
        self.type = type
        self.semOk = False
        self.semFwUpdated = False
        self.strOut = ""
        self.fileName = ""
        self.strFileVerCs = ""
        self.semSetId = False
        self.newId = 1
        self.semFlasImage = False
        self.pathImage = ''

        self.link = JLink(type)
        self.semOk, self.strOut = self.link.init(sn)
        # print(self.semOk, self.strOut)
        self.strDeviceType = self.link.str_dev_type(type)

    def getStrVerId(self):
        _strVer = '__'
        _strCs = '__'
        _strId = '__'
        if self.semOk:
            _strCs = f'{self.cs:X}'
            _strVer = str(self.ver).zfill(6) + '  ' +  _strCs
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
        self.semOk, self.strOut = self.link.get_product_name(self.sn)
        # print('SN ', self.sn, 'checkJLink', self.semOk)
        # set ID
        if self.semOk and self.semSetId and self.newId > 0:
            self.semSetId = False
            self.semOk, self.strOut = self.set_id(self.newId)
        # flash Image
        if self.semOk and self.semFlasImage:
            self.semFlasImage = False
            self.flash_image(self.pathImage)
        # read ver
        _semTempOk = False
        if self.semOk:
            _semTempOk, self.strOut, self.ver, self.cs = self.link.read_info(self.sn)
            if self.ver > 0xF00000:
                self.ver = 0
                self.cs = 0
        # read id
        if self.semOk:
            _semTempOk, self.strOut, self.id = self.link.read_id(self.sn)
            if self.id > self.MAX_ID_VALUE or self.id == 0:
                self.id = self.MAX_ID_VALUE - 1
        # print('_semTempOk', _semTempOk)
        self.strStatus = self.strOut

    def req_flash_image(self, path):
        if self.semOk:
            self.pathImage = path
            self.semFlasImage = True

    def flash_image(self, path):
        if self.sanity_file(path, self.fileName):
            self.funFlashing(path, self.fileName, self.link)

    def sanity_file(self, path, file_name):
        if file_name == "":
            return False
        else:
            # file = open(path + '/' + file_name, 'r')
            # print(file.read())
            return True

    def funFlashing(self, path, file, link):
        # print('file', path + '/' + file)
        # print('start flashing')
        try:
            link.flash_img(self.sn, path + '/' + file)
        except:
            print('Cannot flash')
            return
        sleep(0.5)
        # print('end flashing')
        _sem, _res = link.set_img_info(self.sn, file)
        self.semOk = _sem
        self.semFwUpdated = _sem
        # print('Curr State ', _sem, _res)

    def req_set_id(self, id):
        if self.semOk:
            self.newId = id
            self.semSetId = True

    def set_id(self, id):
        _sem, _res = self.link.set_id(self.sn, id)
        if _sem == False:
            return False, _res
        _sem, _res, read_id = self.link.read_id(self.sn)
        print(_sem, _res, read_id)
        if _sem:
            return True, "written id: " + str(read_id)
        else:
            return False, 'unknown id'
