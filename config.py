import pickle

class Config():
    def __init__(self, patch):
        self.patch = patch
        # init by default values
        self.set = dict(main=52003835, netw=52003834, gw=52003833, rem=52003841, setv=0)

    def load(self):
        # load from a saved file
        try:
            self.set = pickle.load(open(self.patch + "/config/config.pckl", "rb"))
            # print("has been loaded set: ", self.set)
        except:
            self.save()

    def save(self):
        try:
            # print("will be saved set: ", self.set)
            pickle.dump(self.set, open(self.patch + "/config/config.pckl", "wb"))
        except:
            pass


