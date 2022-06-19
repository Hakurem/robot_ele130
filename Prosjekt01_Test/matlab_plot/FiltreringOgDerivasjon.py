# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 10:55:41 2022

@author: admin
"""

import numpy as np
import matplotlib.pyplot as plt


class Bunch(dict):
    def __init__(self, *args, **kwds):
        super(Bunch, self).__init__(*args, **kwds)
        self.__dict__ = self


nrows = 1
ncols = 1
fig, ax = plt.subplots(nrows, ncols, sharex=False)

d = Bunch()

d.Tid = []
d.Ts = []

d.s = []
d.v = []
d.a = []

d.s_IIR = []
d.v_IIR = []
d.a_IIR = []


"""
def Filter(f_IIR, f, alpha, k):
    if len(f) == 1:
        pass
    elif len(f) > 1:
        pass
"""




def CalcTs(Ts, f, k):
    if len(f) > 1:
        Ts.append(f[k]-f[k-1])
    
def IIR_Filter(f_IIR, f, alpha, k):
    if len(f) == 1:
        f_IIR.append(f[k])
    elif len(f) > 1:
        iir = alpha * f[k] + (1-alpha) * f_IIR[k-1]
        f_IIR.append(iir)

def NumDer(f_Der, f, Ts, k):
    if len(f) > 1 and len(f) > 0:
        res = (f[k] - f[k-1])/Ts[k-1]
        f_Der.append(res)
        
        
def EasyWrite(d,k,*variabelNavn):
    streng = ""    
    last_index = len(variabelNavn)-1
    if k == 0:
		# Skriv bare variabelnavn på første linje
        for i,v in enumerate(variabelNavn):
            if i == last_index:
                streng += "{navn}\n".format(navn = v)
            else:
                streng += "{navn}, ".format(navn = v)
        streng  += "\n"
    # Så skriver vi bare verdiene som strenger
    for i,v in enumerate(variabelNavn):
        if i == last_index:
            try:
                streng += str(d[v][-1])
            except IndexError:
                pass
        else:
            try:
                streng += str(d[v][-1]) + ","
            except IndexError:
                streng += ","
                pass
    streng  += "\n"
    return streng
#_________________________________________________________

        
alpha = 0.1

with open("CalcOffline.txt","w",encoding="UTF8") as file:
  
      
        
        for k in range(10):
            
            d.Tid.append(k)
            d.s.append(300+k**3)
            
            
            # beregn Ts
            CalcTs(d.Ts, d.Tid, len(d.Tid)-1)
            
            # beregn filtrert avstand
            IIR_Filter(d.s_IIR, d.s, alpha, len(d.s)-1)
            
            
            # beregn fart og filtrert fart
            NumDer(d.v, d.s, d.Ts, len(d.s)-1)
            IIR_Filter(d.v_IIR, d.v, alpha, len(d.v)-1)
            
            
            # beregn akselerasjon og filtrert akselerasjon
            NumDer(d.a, d.v, d.Ts, len(d.v)-1)
            IIR_Filter(d.a_IIR, d.a, alpha, len(d.a)-1)
            
            ToFile = EasyWrite(d,k,
                      "Tid",
                      "s",
                      "Ts",
                      "s_IIR",
                      "v",
                      "v_IIR",
                      "a",
                      "a_IIR",
                      )
            file.write(ToFile)
           




    
    
  