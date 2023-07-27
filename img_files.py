import os
import re

class ImgFiles:
     def __init__(self):
        self.path = "./files/LastRelease"
        self.lib_path_lts = "./files/LastRelease"
        self.lib_path_dev = "./files/Candidates"
        self.lib_path_mbot = "./files/Microbot"
        # -- linux --
        # self.lib_path_lts = "/opt/liberty/LastRelease"
        # self.lib_path_dev = /opt/liberty/Candidates"
        self.dir_list = []

     def list_files(self, lts, mbot):
         list = []
         self.path = self.lib_path_lts
         if lts:
            self.path = self.lib_path_dev
         if mbot:
            self.path = self.lib_path_mbot
         # print(self.path)
         if os.path.exists(self.path) == True:
             self.dir_list = os.listdir(self.path)
             for ind in range(len(self.dir_list)):
                 if mbot == False:
                     if re.search("LIB", self.dir_list[ind]):
                         list.append(self.dir_list[ind])
                 else:
                     if re.search("MBOT", self.dir_list[ind]):
                         list.append(self.dir_list[ind])
         # print(list)
         return list
