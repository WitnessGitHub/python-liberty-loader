import os
import re


class ImgFiles:
     def __init__(self):
        self.path = "C:/Liberty/LastRelease"
        self.lib_path_lts = "C:/Liberty/LastRelease"
        self.lib_path_dev = "C:/Liberty/Candidates"
        # -- linux --
        # self.lib_path_lts = "/opt/liberty/LastRelease"
        # self.lib_path_dev = /opt/liberty/Candidates"
        self.imgs = {' Main CPU': 'LIB_MAIN', ' Network CPU': 'LIB_NETW', ' Remote CPU': 'LIB_REM', ' GuideWire CPU': 'LIB_GW'}
        self.dir_list = []

     def list_files(self, lts):
         list = []
         self.path = self.lib_path_lts
         if lts:
            self.path = self.lib_path_dev
         if os.path.exists(self.path) == True:
             self.dir_list = os.listdir(self.path)
             for ind in range(len(self.dir_list)):
                 if re.search("LIB", self.dir_list[ind]):
                     list.append(self.dir_list[ind])
         return list

     def read_files(self, image, lts):
         self.path = self.lib_path_lts
         if lts:
             self.path = self.lib_path_dev
         if os.path.exists(self.path) == True:
                self.dir_list = os.listdir(self.path)
                # print(self.dir_list, len(self.dir_list), image)
                sem = False
                for ind in range(len(self.dir_list)):
                    matches = [match for match in self.dir_list if self.imgs[image] in match]
                    if len(matches) > 0:
                        # print(matches[0])
                        return True, matches[0]
                if sem == False:
                    return False, ""
                else:
                    return False, ""
