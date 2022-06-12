#!/usr/bin/env pybricks-micropython
# coding=utf-8

# class Bunch(dict):
#     def __init__(self, *args, **kwds):
#         super(Bunch, self).__init__(*args, **kwds)
#         #self.__dict__ = self

#     def __setattr__(self,key,value):
#         if not key in self:
#             print('setting',key)
#             self[key] = value
#         else:
#             return self[key]


#     def __getattr__(self,key):
#         print('getting',key)
#         return self[key]



class Bunch(dict):
    def __init__(self, *args, **kwds):
        super(Bunch, self).__init__(*args, **kwds)
        self.__dict__.update(self)
    def keys(self):
        return self.__dict__.keys()

    

 




def main():
    d = Bunch()
    d.a = ['oh no']
    d.b = 2
    d.c = 3
    d.a.append('is wrong with you')
   
    for key in d.keys():
        print(key)

    
    

if __name__ == '__main__':
    main()