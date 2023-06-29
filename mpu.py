import threading
from time import sleep

# from img_files import ImgFiles
from lib_jlink import JLink


class Mpu:
    def __exit__(self):
        self.semOk = False
        self.link.jlink._finalize()

    def __init__(self, sn, type):

        self.strStatus = ''
        self.type = type
        self.semOk = False
        self.semBusy = False
        self.strOut = ""
        self.fileName = ""
        self.strFileVerCs = ""
        # self.files = ImgFiles()

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
            self.semOk, self.strOut = self.link.get_product_name()
        if self.semOk and self.semBusy == False:
            self.semOk, self.strOut, self.id = self.link.read_id()
        if self.semOk and self.semBusy == False:
            self.semOk, self.strOut, self.ver = self.link.read_info()
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
        self.semBusy = True
        print('file', path + '/' + file)
        print('start flashing')
        try:
            link.flash_img(path + '/' + file)
        except:
            print('Cannot flash')
            self.semBusy = False
            return
        sleep(1.0)
        print('end flashing')
        _sem, _res = link.set_img_info(file)
        self.semOk = _sem
        print('Curr State ', _sem, _res)
        self.semBusy = False

    def set_id(self, id):
        if self.semOk == False or self.semBusy == True:
            return False, ''

        self.link.set_id(id)
        sem, res, read_id = self.link.read_id()
        print(sem, res, read_id)
        if res:
            return True, "Written ID: " + str(read_id)
        else:
            return False, 'Unknown ID'
