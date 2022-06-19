# coding=utf-8
# Legger til mappene midlertidig i søkestien for imports til programmet slutter
import os
import sys
import socket
p_root = os.getcwd() #root of project
sys.path.append(p_root)
sys.path.append(os.path.join(p_root, r'HovedFiler'))
sys.path.append(os.path.join(p_root, r'Moduler'))
#_______________________________________________________

from plotClass import PlotObject
from funksjoner import BunchPython, writeToFile, unpackMeasurement, parseMeasurements
from Main import Configs, d, MathCalculations, lagPlot
d = BunchPython(d.__dict__)
#---------------------------------------------------------------------


def offline():
    # Leser av fil online file og skriver til offline med nye berekninger
    # fr: file read
    # fw: file write
    with open(p_root+"/Data/"+Configs.filename,"r") as fr:

        # parsing out which keys are measurements
        keys = {}
        m_keys = {}
        _g = BunchPython()
        meta_data = fr.readline().rstrip().split(",")
        for rawkey in meta_data:
            if rawkey.find("=meas") != -1:
                key = rawkey.replace("=meas","")
                m_keys[key] = key
            key = rawkey.replace("=calc","").replace("=meas","")
            keys[key] = key

        # parsing out initial values to calculate offline
        initial_verdier = fr.readline().rstrip().split(",")
        for g_data in initial_verdier:
            v = g_data.split("=")
            _g[v[0]] = parseMeasurements(v[1])
        
        # parsing out measurements and recalculating
        dataFromFile = fr.readlines()
        if len(Configs.filenameOffline)>4:
            fw = open(p_root+"/Data/"+Configs.filenameOffline,"w",encoding="utf-8")
            for k,EachRow in enumerate(dataFromFile):
                m_data = EachRow.split(",")
                unpackMeasurement(d, keys, m_keys, m_data)
                MathCalculations(d,k,_g)
                try:
                    streng = writeToFile(d,k,m_keys,_g)
                    fw.write(streng)
                except Exception as e:
                    print(e)
                    fw.close()
            fw.close()

    # tilslutt plotter vi data
    plt = PlotObject(d, Configs)
    lagPlot(plt)

    # for line in plt.lines.values():
    #     plt.Extended(line)
    plt.stopPlot()



# # Hide empty plot and keep the custom stop button
# if not Configs.livePlot:
#     plt.gcf().set_visible(False)
            
# elif not Configs.Online:
#     offline(filenameMeas)


# Setup sockets
def main():
    if Configs.Online:
       
        # If online, setup socket object and connect to EV3.
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            addr = (Configs.EV3_IP, 8070)
            print("Attempting to connect to {}".format(addr))
            print("Starter ikke programmet etter noen sekunder kan det hende at ip-adressen er endret")
            sock.connect(addr)
            DataToOnlinePlot = sock.recv(1024)
            if DataToOnlinePlot == b"ack":
                print("Connection established for plotting")
            else:
                print("no ack")
                sys.exit()
        except socket.timeout:
            print("failed (sjekk om IP addressen er forandret)")
            sys.exit()

        except Exception as e:
            print("\n____________Error was caught________________________")
            print("Possible mistakes")
            print('Did you try to run it in offline with online on?')
            print("Did you run this file without running Run_1_Robot.py before?")
            print(e)
            sys.exit()
        
        plt = PlotObject(d, Configs, sock)
        lagPlot(plt)
        sock.send(b'Done_Initializing_Plot')
        print("sending ready signal to robot")
        plt.startPlot()


if __name__=="__main__":
    if Configs.Online:
        main()
    else:
        print("Calculate in Offline")
        offline()