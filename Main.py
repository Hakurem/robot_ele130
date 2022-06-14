class Bunch(dict):
    def __init__(self, *args, **kwds):
        super(Bunch, self).__init__(*args, **kwds)
        self.__dict__ = self

plotMethod = 1
desimaler = 5


d = Bunch()
d.tid = []
d.rand = []
d.index = []
d.Ts = []
d.f_Ts = []
