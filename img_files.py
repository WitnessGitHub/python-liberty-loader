import os
import re
from enum import Enum


class SetVersions(Enum):
    STABLE = 0
    MBOT = 1
    LTS = 2

class ImgFiles:
     def __init__(self):
        self.path = "./files/LastRelease"
        self.lib_path_dev = "./files/Stable"
        self.lib_path_mbot = "./files/Microbot"
        self.lib_path_lts = "./files/LastRelease"
        # -- linux --
        # self.lib_path_lts = "/opt/liberty/LastRelease"
        # self.lib_path_dev = /opt/liberty/Stable"
        self.dir_list = []

     def list_files(self, set_ver):
         list = []
         self.path = self.lib_path_lts
         if set_ver == SetVersions.LTS:
            self.path = self.lib_path_lts
         if set_ver == SetVersions.STABLE:
            self.path = self.lib_path_dev
         if set_ver == SetVersions.MBOT:
            self.path = self.lib_path_mbot
         # print(self.path)
         if os.path.exists(self.path) == True:
             self.dir_list = os.listdir(self.path)
             for ind in range(len(self.dir_list)):
                 if set_ver != SetVersions.MBOT:
                     if re.search("LIB", self.dir_list[ind]):
                         list.append(self.dir_list[ind])
                 else:
                     if re.search("MBOT", self.dir_list[ind]):
                         list.append(self.dir_list[ind])
         # print(list)
         return list
