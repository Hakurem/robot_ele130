# coding=utf-8
# Legger til mappene i søkestien for imports
import os
import sys
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), r'HovedFiler'))
sys.path.append(os.path.join(os.getcwd(), r'Moduler'))
#_______________________________________________________

from plotClass import PlotObject
import socket
import sys
from funksjoner import BunchPython
from Main import Configs, d, MathCalculations, unpackMeasurement, lagPlot, writeOfflineCalc
filenameMeas = Configs.filenameMeas
d = BunchPython(d.__dict__)
#---------------------------------------------------------------------


def offline(filenameMeas):
    with open(filenameMeas) as f:
        keys = f.readlines()[0].rstrip().split(",")
        MeasurementFromFile = f.readlines()[2:]
        length = len(MeasurementFromFile)
        for k,EachRow in enumerate(MeasurementFromFile):
            m_data = EachRow.split(",")
            unpackMeasurement(d, keys, m_data)
            MathCalculations(d,k)
        if len(Configs.filenameCalcOffline)>4:
            writeOfflineCalc(d,length)
    plt = lagPlot()



# # Hide empty plot and keep the custom stop button
# if not Configs.livePlot:
#     plt.gcf().set_visible(False)
            
# elif not Configs.Online:
#     offline(filenameMeas)


# Setup sockets
def main():
    if Configs.Online:
       
        # If online, setup socket object and connect to EV3.
        if Configs.runFromPC:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                addr = (Configs.EV3_IP, 8070)
                print("Attempting to connect to {}".format(addr))
                sock.connect(addr)
                DataToOnlinePlot = sock.recv(1024)
                if DataToOnlinePlot == b"ack":
                    print("Connection established for plotting")
                else:
                    print("no ack")
                    sys.exit()
            except socket.timeout:
                print("failed")
                sys.exit()
            
            plt = PlotObject(d, Configs, sock)
            lagPlot(plt)
            plt.startPlot()


if __name__=="__main__":
    main()