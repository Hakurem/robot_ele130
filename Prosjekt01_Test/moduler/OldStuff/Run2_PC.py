# coding=utf-8
# Legger til mappene i søkestien for imports
import os
import sys
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), r'HovedFiler'))
sys.path.append(os.path.join(os.getcwd(), r'Moduler'))
#_______________________________________________________

from multiprocessing import Queue, Process
import tkinter as tk
import socket
import sys
import json
import _thread
from funksjoner import Bunch
from Main import Configs, d, MathCalculations,  unpackMeasurement, lagPlot, writeOfflineCalc, InputToRobot
filenameMeas = Configs.filenameMeas
#---------------------------------------------------------------------

# lager en grafisk brukergrensesnitt (GUI) for å håndtere stopping av Ev3 fra PC
def CustomStop(sock):
    def StopProgram():
        sock.send(b'Stop')
    window = tk.Tk()
    window.title("EV3 Custom Stop")
    window.config( bg='#567')
    ws = window.winfo_screenwidth()
    hs = window.winfo_screenheight()
    w = 250
    h = 250
    x = ws-(w)
    y = hs/2-h/2
    window.geometry('%dx%d+%d+%d' % (w, h, x, y))
    button = tk.Button(window, text ="Stop Program!", command = StopProgram)
    button.config(font=("Consolas",15))
    button.place(relx=.5, rely=.5, anchor="center", width = 200, height = 200)
    window.mainloop()
#______________________________________________________________________________


# Funksjon som sender input fra PC til robot
def InputFunksjon(sock):
    InputToRobot(sock)
#__________________________________________



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



def runPlot(plotQueue):
    plt = lagPlot()
    plt.InitializeData(d,Configs,plotQueue)
    _thread.start_new_thread(CustomStop, (plt,))
    plt.startPlot()
   



 # Setup sockets
def main():
    if Configs.Online:
        if Configs.communicateWithEv3: # If you want to communicate back to the ev3
            input_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                input_addr = (Configs.EV3_IP, 8080)
                print("Attempting to connect to {}".format(input_addr))
                input_sock.connect(input_addr)
                input_callback = input_sock.recv(1024)
                if input_callback == b"ack":
                    print("Input port connected")
                else:
                    print("no ack from input socket")
                    sys.exit()
            except socket.timeout:
                print("failed input socket")
                sys.exit()
            _thread.start_new_thread(InputFunksjon, (input_sock, ))

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
                
        plotQueue = Queue()
        plot_consumer = Process(target=runPlot, args = (plotQueue,))
        plot_consumer.start()
        socketData = fetchData(sock)

        # On laptop reading from socket
        while True:
            #try:
            bytesData = next(socketData)
            if bytesData == b'':
                continue
            elif bytesData == b"end":
                print("Recieved end signal")
                break
            Data = json.loads(bytesData)
            unpackAndPlot(Data,plotQueue)
           # except Exception as e:
           #    print(f"error occured when reading socket {e}")
           #     continue

# Generator to read socket bytes fifo
def fetchData(sock):
	bytesData = b""
	while True:
		bytesData += sock.recv(1024)
		idx = bytesData.find(b"?")
		if idx != -1:
			packet = bytesData[:idx]
			if bytesData[idx:] == b"?":
				bytesData = b""
			else:
				bytesData = bytesData[idx+1:]
			yield packet # do something with packet

# Parse Data and send with a queue to plotObject
def unpackAndPlot(data,queue):

    dataToPlot = {}
    for key in data:
        dataToPlot[key] = data[key]
    queue.put(dataToPlot)
    # try:
    #     # finding the longest list
    #     max_index = 0
    #     for key in data:
    #         if len(data[key]) > max_index:
    #             max_index = len(data[key])
    #     #________________________

    #     for k in range(max_index):
    #         dataToPlot = Bunch() 
    #         for key in data:
    #             dataToPlot[key] = data[key][k]
    #         queue.put(dataToPlot)

    # except Exception as e:
    #     print(f"error with unpackAndPlot {e}",flush=True)



if __name__=="__main__":
    main()