import threading
from time import sleep

from lib_jlink import JLink


class Mpu:
    def __exit__(self):
        self.semOk = False
        self.taskJLinkControl.stop()
        self.link.jlink._finalize()

    def __init__(self, sn, type):

        self.strStatus = ''
        self.type = type
        self.semOk = False
        self.semBusy = False
        self.strOut = ""

        self.link = JLink()
        self.semOk, self.strOut = self.link.init(sn)
        print(self.semOk, self.strOut)
        self.strDeviceType = self.link.str_dev_type(type)


    def checkJLink(self):
        if self.semBusy == False:
            self.semOk, self.strOut = self.link.get_product_name()
            self.strStatus = self.strOut
        if self.semOk and self.semBusy == False:
            self.semOk, self.id = self.link.read_id()
        if self.semOk and self.semBusy == False:
            self.semOk, cs, type, self.ver, len = self.link.read_info()
        self.strStatus = self.strOut

    def open_file(self, cpu, lts):
        try:
            res, file_name = self.files.read_files(cpu, lts)
            if res:
                list = file_name.split('_')
                self.label_file_img.configure(text='File Ver: ' + list[1] + ' ' + list[2])
                return True, file_name
            else:
                # print('Unknown File')
                return False, ""
        except:
            self.semOk = False
            return False, ""

    def flash_image(self, lts):
        self.single_img_flash(self.type, lts, self.link)
    def single_img_flash(self, cpu, lts, link):
        if self.semOk == False or self.semBusy == True:
            return
        sem, file_name = self.open_file(cpu, lts)
        if sem:
            if self.sanity_file(file_name):
                if self.semOk:
                    self.taskImgFlashing = threading.Thread(target=self.imgFlashing, daemon=True, args=(file_name, link)).start()
            else:
                return False, ''

    def set_id(self):
        if self.semOk == False or self.semBusy == True:
            return
        new_id = 0
        try:
            new_id = int(self.entry.get())
        except ValueError:
            self.entry.delete(first_index=0, last_index=50)
            self.label_curr_id.configure(text='Wrong ID')
            return False
        if new_id >= self.MAX_ID_VALUE:
            self.entry.delete(first_index=0, last_index=50)
            self.label_curr_id.configure(text='Unknown ID')
            return False
        self.link.set_id(new_id)
        res, inp = self.link.read_id()
        # print(res,inp )
        if res:
            self.label_curr_id.configure(text="Written ID:  " + str(inp))
        else:
            self.entry.delete(first_index=0, last_index=50)
            self.label_curr_id.configure(text='Unknown ID')


    def read_img_id(self):
        try:
            res, _id = self.link.read_id()
            if res:
                self.label_curr_id.configure(text="Current ID:  " + str(_id))
            else:
                self.label_curr_id.configure(text='Unknown ID')
        except:
            self.semOk = False

    def read_img_info(self, link):
        try:
            res, cs, type, ver = link.read_info()
            # print('res', res, 'cs', cs, 'type', type, 'ver', ver)
            if res:
                self.strDeviceType = link.str_dev_type(type)
                self.label_curr_img.configure(text="Curr Ver:  " + self.strDeviceType + ": " + link.str_dev_ver(ver))
            else:
                self.label_curr_img.configure(text='Unknown Img Info')
        except:
            self.semOk = False


    def imgFlashing(self, file, link):
        self.semBusy = True
        # self.progressbar.configure(height=10)
        # self.progressbar.start()
        print('file', self.files.path + '/' + file)
        # self.label_curr_img.configure(text='Image is Flashing...')
        try:
            link.flash_img(self.files.path + '/' + file)
        except:
            # self.label_curr_img.configure(text='Cannot flash')
            # self.progressbar.configure(height=2)
            # self.progressbar.stop()
            self.semBusy = False
            return
        sleep(1.0)
        # print('end flashing')
        self.progressbar.configure(height=2)
        self.progressbar.stop()
        type, ver = link.set_img_info(file)
        self.label_curr_img.configure(text='Curr Ver ' + type + ": " + ver)
        self.semBusy = False