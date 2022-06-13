# -*- coding: utf-8 -*-
from multiprocessing import Process, Queue
import math
from Main import d
from plotClass import PlotObject
import socket
from time import perf_counter, sleep
import json
import tkinter as tk
import _thread



class Bunch(dict):
    def __init__(self, *args, **kwds):
        super(Bunch, self).__init__(*args, **kwds)
        self.__dict__ = self

def FIR_filter(f_fir,f,m,k):
	if k == 0:
		f_fir.append(f[0])
	else:
		k+=1 
		if k < m:
			res = (1/k) * sum(f[:k])
		else:
			res = (1/m) * sum(f[(k-m):k])
		f_fir.append(res)

def producer(signal_queue):
    # Sett opp socketobjektet, og hør etter for "connection"
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", 8070))
    sock.listen(1)

    print("waiting for connection from computer",flush=True)
    signal_queue.put(1)

    connection, _ = sock.accept()
    connection.send(b"ack")

    dt_stamp = perf_counter()
    k=0
    while True:

        try:
            if k == 0:
                stamp = perf_counter()
                d.tid.append(0)
            else:
                t = perf_counter()-stamp
                d.tid.append(t)
                d.Ts.append(d.tid[k]-d.tid[k-1])
                FIR_filter(d.f_Ts,d.Ts,1000,len(d.Ts)-1)

       
            d.rand.append(math.sin(0.1*k)) #d.rand.append(random.randint(-10,10))
            d.index.append(k)

            # Create a temp dict to store most recent values
            data = Bunch()
            for key in d:
                try:
                    data[key] = d[key][-1]
                except:
                    pass

            msg = json.dumps(data) # serializing med json tar overraskende lang tid på roboten
            connection.send(bytes(msg, "utf-8") + b"?") # Sender målinger fra Ev3 til PC-en din

        except Exception as e:
            print(f'noe gikk galt {e}')
            break
            
        sleep(0.04)
        """
        dt = perf_counter()-dt_stamp
        dt_stamp = perf_counter()
        if dt < 0.01:
            ts = 0.01-dt
            sleep(ts)
        else:
            sleep(0.01)
        """
        k+=1
        


def CustomStop():
    pass
	# def StopProgram():
	# 	button.config(text="fix plot")
	# 	#SEND STOP COMMAND TO ROBOT
	# 	try:
	# 		plt.stopPlot()
	# 	except:
	# 		pass

	# window = tk.Tk()
	# window.title("EV3 Custom Stop")
	# window.config(bg='#567')
	# ws = window.winfo_screenwidth()
	# hs = window.winfo_screenheight()
	# w = 250
	# h = 250
	# x = ws - (w) 	#(ws/2) - (w/2)
	# y = hs/2 - h/2 #(hs/2) - (h/2)
	# window.geometry('%dx%d+%d+%d' % (w, h, x, y))
	# button = tk.Button(window, text ="Stop Program!",command=StopProgram)
	# button.config(font=("Consolas",15))
	# button.place(relx=.5, rely=.5, anchor="center", width = 200, height = 200)
	# window.mainloop()



def main():
    signal_queue = Queue()
    p = Process(target=producer, args = (signal_queue,))
    p.start()
    signal_queue.get()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        addr = ("localhost", 8070)
        print("Attempting to connect to {}".format(addr))
        sock.connect(addr)
        callback = sock.recv(1024)
        if callback == b"ack":
            print("Connection established")
        else:
            print("no ack")
            exit()

    except socket.timeout:
        print("failed")
        exit()
    runPlot(sock)



def runPlot(sock):
    plt = PlotObject(nrows = 3, ncols = 1)
    plt.InitializeData(d,sock)
    ax = plt.ax
    ax[0].set_title('Random')
    ax[1].set_title('Index')
    ax[2].set_title('Ts')

    plt.createlines(
        subplot         = ax[0],    
        xListName       = "tid",       
        yListName       = "rand",
        color           = "b",
        yname			= "random values"
    )


    plt.createlines(
        subplot         = ax[1],    
        xListName       = "tid",       
        yListName       = "index",
        color           = "r",
        yname			= "length of list"
    )


    plt.createlines(
        subplot         = ax[2],    
        xListName       = "tid",       
        yListName       = "Ts",
        color           = "g",
        yname			= "time step (s)"
    )
    #________________________________
    
    #_thread.start_new_thread(CustomStop, (plt,))
    plt.startPlot()

if __name__=="__main__":
    main()