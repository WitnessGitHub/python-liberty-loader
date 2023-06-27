
import re
import pylink

class JLink():
    def __init__(self):
        self.ADD_ID     = 0x7e000
        self.ADD_PRM    = 0x7d800
        self.ADD_INFO   = 0x7d000
        self.PAGE_PREAMBLE = 0x115566AA
        self.SZ_PAGE_PREAMBLE  = 4
        self.SZ_PAGE_DATA  = 24
        self.SZ_PAGE_CS  = 4
        self.BGM13S = 'BGM13S32F512GA'
        self.BG12P = 'EFR32BG12PXXXF1024'
        self.jlink = pylink.JLink()
        self.sn = 0
        # -- linux --
        # lib = pylink.library.Library('/home/pi/PycharmProjects/LibertyUpdater/libjlinkarm.so.7.88.3')
        # self.jlink = pylink.JLink(lib)


    def sanity_block_id(self, list):
        sublist_prm = list[:4]
        sublist_id = list[4:8]
        sublist_data = list[8:28]
        sublist_cs = list[28:]
        # rx preamble
        rx_pream = sum(e * 0x100 ** (i) for i, e in enumerate(sublist_prm))
        # rx id
        id = sum(e * 0x100 ** (i) for i, e in enumerate(sublist_id))
        # rx cs
        rx_cs = sum(e * 0x100 ** (i) for i, e in enumerate(sublist_cs))
        # calculate cs
        calc_cs = sum(e for i, e in enumerate(sublist_prm))
        calc_cs += sum(e for i, e in enumerate(sublist_id))
        calc_cs += sum(e for i, e in enumerate(sublist_data))
        # print('preamble id ', rx_pream, self.PAGE_PREAMBLE, rx_pream == self.PAGE_PREAMBLE)
        # print('cs id ', rx_cs, calc_cs, rx_cs == calc_cs)
        return ((rx_pream == self.PAGE_PREAMBLE) and (rx_cs == calc_cs)), id

    def sanity_block_info(self, list):
        sublist_prm = list[:4]
        sublist_img_cs = list[4:8]
        sublist_dev_type = list[8:12]
        sublist_ver_nbr = list[12:16]
        sublist_data = list[16:28]
        sublist_cs = list[28:]
        # rx preamble
        rx_pream = sum(e * 0x100 ** (i) for i, e in enumerate(sublist_prm))
        # rx img_cs
        rx_img_cs = sum(e * 0x100 ** (i) for i, e in enumerate(sublist_img_cs))
        # rx dev_type
        rx_dev_type = sum(e * 0x100 ** (i) for i, e in enumerate(sublist_dev_type))
        # rx ver_nbr
        rx_ver_nbr = sum(e * 0x100 ** (i) for i, e in enumerate(sublist_ver_nbr))
        # rx cs
        rx_cs = sum(e * 0x100 ** (i) for i, e in enumerate(sublist_cs))
        # calculate cs
        calc_cs = sum(e for i, e in enumerate(sublist_prm))
        calc_cs += sum(e for i, e in enumerate(sublist_img_cs))
        calc_cs += sum(e for i, e in enumerate(sublist_dev_type))
        calc_cs += sum(e for i, e in enumerate(sublist_ver_nbr))
        # print('preamble info ', rx_pream, self.PAGE_PREAMBLE, rx_pream == self.PAGE_PREAMBLE)
        # print('cs info ', rx_cs, calc_cs, rx_cs == calc_cs)
        return ((rx_pream == self.PAGE_PREAMBLE) and (rx_cs == calc_cs)), rx_img_cs, rx_dev_type, rx_ver_nbr

    def init(self, sn):
        self.sn = sn
        try:
            self.jlink.open(serial_no=self.sn)
            self.jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
            self.jlink.connect(self.BGM13S)
            self.jlink.coresight_configure()
            self.jlink.set_reset_strategy(pylink.enums.JLinkResetStrategyCortexM3.RESETPIN)
            # self.jlink.reset(ms=10, halt=False)
            # print(self.jlink.core_id())
            # print(self.jlink.device_family())
            # print(self.jlink.product_name)
            self.jlink.close()
            return True, "JLink Connected"
        except pylink.JLinkException as e:
            self.jlink.close()
            return False, e

    def reopen(self):
        try:
            # jlink operation
            self.jlink.open(serial_no=self.sn)
            self.jlink.set_tif(pylink.enums.JLinkInterfaces.SWD)
            self.jlink.connect(self.BGM13S)
            self.jlink.coresight_configure()
            # self.jlink.set_reset_strategy(pylink.enums.JLinkResetStrategyCortexM3.RESETPIN)
            # self.jlink.reset(ms=10, halt=False)
            return True, "JLink Connected"
        except pylink.JLinkException as e:
            self.jlink.close()
            return False, e

    def get_product_name(self):
        try:
            #: jlink operation
            self.reopen()
            product = self.jlink.product_name
            if re.search('J-Link', product):
                self.jlink.close()
                return True, "JLink Connected"
            else:
                self.jlink.close()
                return False, "JLink Unknown"
        except pylink.JLinkException as e:
            self.jlink.close()
            return False, e

    def read_id(self):
        # jlink operation
        self.reopen()
        buff = self.jlink.memory_read8(self.ADD_ID, 32)
        self.jlink.close()
        return self.sanity_block_id(buff)
    def read_info(self):
        # jlink operation
        self.reopen()
        buff = self.jlink.memory_read8(self.ADD_INFO, 32)
        self.jlink.close()
        return self.sanity_block_info(buff)

    def set_id(self, id):
        pream_list = [(self.PAGE_PREAMBLE >> (8 * i)) & 0xff for i in range(4)]
        id_list = [(id >> (8 * i)) & 0xff for i in range(4)]
        uuid_list = list(bytearray(self.SZ_PAGE_DATA - self.SZ_PAGE_PREAMBLE))
        # print('prepared id ', pream_list, id_list, uuid_list)
        # calculate cs
        calc_cs = sum(e for i, e in enumerate(pream_list))
        calc_cs += sum(e for i, e in enumerate(id_list))
        calc_cs += sum(e for i, e in enumerate(uuid_list))
        cs_list = [(calc_cs >> (8 * i)) & 0xff for i in range(4)]
        out_list = pream_list + id_list + uuid_list + cs_list
        self.sanity_block_id(out_list)
        # jlink operation
        self.reopen()
        self.jlink.flash(out_list, self.ADD_ID)
        self.jlink.close()
        return out_list

    def flash_img(self, img_file):
        # jlink operation
        self.reopen()
        self.jlink.flash_file(img_file, 0)
        self.jlink.close()

    def int_dev_type(self, str_dev_type):
        if str_dev_type == 'REM':
            return 1
        elif str_dev_type == 'MAIN':
            return 2
        elif str_dev_type == 'NETW':
            return 3
        elif str_dev_type == 'GW':
            return 4

    def str_dev_ver(self, int_dev_ver):
        if int_dev_ver < 100000 - 1:
            return '0' + str(int_dev_ver)
        else:
            return str(int_dev_ver)

    def str_dev_type(self, int_dev_type):
        if int_dev_type == 1:
            return 'REM'
        elif int_dev_type == 2:
            return 'MAIN'
        elif int_dev_type == 3:
            return 'NETW'
        elif int_dev_type == 4:
            return 'GW'

    def set_img_info(self, file_name):
        list = file_name.split('_')
        pream_list = [(self.PAGE_PREAMBLE >> (8 * i)) & 0xff for i in range(4)]
        dev_cs = int(list[3].split('.')[0], 16)
        dev_type = self.int_dev_type(list[1])
        ver_nbr = int(list[2])
        # print('dev_type', dev_type, 'ver_nbr', ver_nbr, 'dev_cs', dev_cs)
        dev_cs_buff = [(dev_cs >> (8 * i)) & 0xff for i in range(4)] # 4
        dev_type_buff = [(dev_type >> (8 * i)) & 0xff for i in range(4)] # 4
        ver_nbr_buff = [(ver_nbr >> (8 * i)) & 0xff for i in range(4)] # 4
        zero_buff = [0 for i in range(12)] # 12
        # print('prepared info ', pream_list, dev_cs_buff, dev_type_buff, ver_nbr_buff)
        # calculate cs
        calc_cs = sum(e for i, e in enumerate(pream_list))
        calc_cs += sum(e for i, e in enumerate(dev_cs_buff))
        calc_cs += sum(e for i, e in enumerate(dev_type_buff))
        calc_cs += sum(e for i, e in enumerate(ver_nbr_buff))
        info_cs_buff = [(calc_cs >> (8 * i)) & 0xff for i in range(4)]
        out_buff = pream_list + dev_cs_buff + dev_type_buff + ver_nbr_buff + zero_buff + info_cs_buff
        self.sanity_block_info(out_buff)
        # jlink operation
        self.reopen()
        self.jlink.flash(out_buff, self.ADD_INFO)
        self.jlink.close()
        return list[1], list[2]