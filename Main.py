class Bunch(dict):
    def __init__(self, *args, **kwds):
        super(Bunch, self).__init__(*args, **kwds)
        self.__dict__.update(self)

class BunchPython(dict):
    def __init__(self, *args, **kwds):
        super(BunchPython, self).__init__(*args, **kwds)
        self.__dict__ = self


Configs = Bunch()
Configs.plotMethod = 2
Configs.desimaler = 5


d = Bunch()
d.tid = []
d.rand = []
d.rand2 = []
d.index = []
d.Ts = []
d.f_Ts = []
