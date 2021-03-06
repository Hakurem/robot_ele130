# -*- coding: utf-8 -*-
from multiprocessing import Process, Queue
import math
from Main import d, Configs, BunchPython
from plotClass import PlotObject
import socket
from time import perf_counter, sleep
import json
d = BunchPython(d.__dict__)



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
    print("socket connection established. Sending data through socket",flush=True)

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
            d.rand2.append(math.cos(0.1*k)) #d.rand.append(random.randint(-10,10))
            d.index.append(k)

            # Create a temp dict to store most recent values
            data = BunchPython()
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
            
       
        dt = perf_counter()-dt_stamp
        dt_stamp = perf_counter()
        if dt < 0.01:
            ts = 0.01-dt
            sleep(ts)
        else:
            sleep(0.01)
        k+=1
        

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
    plt = PlotObject(d, Configs, sock) # ikke rør
    runPlot(plt)



def runPlot(plt):
    
    plt.create(nrows=3, ncols=1, sharex=False)
    ax = plt.ax
    
    # Legg til navn og aksetitler for hver subplot
    ax[0].set_title('Random')
    ax[0].set_xlabel("tid [sek]")
    ax[0].set_ylabel("flow")

    ax[1].set_title('Index')
    ax[1].set_xlabel("tid [sek]")
    ax[1].set_ylabel('antall')

    ax[2].set_title('Ts')
    ax[2].set_xlabel("tid [sek]")
    ax[2].set_ylabel("tid [sek]")
    

    plt.plot(
        subplot         = ax[0],    
        xListName       = "tid",       
        yListName       = "rand",
        color           = "b",
        yname			= "sinus"
    )

    plt.plot(
        subplot         = ax[0],    
        xListName       = "tid",       
        yListName       = "rand2",
        color           = "r",
        yname			= "cosinus"
    )


    plt.plot(
        subplot         = ax[1],    
        xListName       = "tid",       
        yListName       = "index",
        color           = "r",
        yname			= "length of list"
    )


    plt.plot(
        subplot         = ax[2],    
        xListName       = "tid",       
        yListName       = "Ts",
        color           = "g",
        yname			= "time step (s)"
    )
    #________________________________
    
    
    plt.startPlot()

if __name__=="__main__":
    main()