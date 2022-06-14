from multiprocessing import Process, Queue
import multiprocessing
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



def QueueHandler(queue,connection):
	while True:
		length = queue.qsize() # avoid blocking
		if length > 0:
			d = {}
			for _ in range(length):
				recvData = queue.get()
				for key in recvData:
					if key in d:
						d[key].append(recvData[key])
					else:
						d[key] = [recvData[key]]
			jsonData = json.dumps(d)
			byteData = bytes(jsonData, "utf-8") + b"?"
			connection.send(byteData)
			sleep(0.1)



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



def setup_socket(signal_queue):
	# Sett opp socketobjektet, og hør etter for "connection"
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(("", 8070))
	sock.listen(1)

	print("waiting for connection from computer",flush=True)
	signal_queue.put(1)

	connection, _ = sock.accept()
	connection.send(b"ack")
	
	queue = Queue()
	consumer = Process(target=QueueHandler, args = (queue,connection))
	consumer.start()

	print('READY TO PRODUCE',flush=True)
	k = 0

	#with open('socket_data.txt', "w", encoding="utf-8") as file:

	dt_stamp = perf_counter()
	while True:
		
		try:
			if k == 0:
				#file.write('Test\n')
				stamp = perf_counter()
				d.tid.append(0)
			else:
				t = perf_counter()-stamp
				d.tid.append(t)
				d.Ts.append(d.tid[k]-d.tid[k-1])
				FIR_filter(d.f_Ts,d.Ts,1000,len(d.Ts)-1)

				#value = str(d.Ts[-1])
				#file.write(value+"\n")
			
			
			d.rand.append(math.sin(0.1*k)) #d.rand.append(random.randint(-10,10))
			d.index.append(k)

			# Create a temp dict to store most recent values
			data = Bunch()
			for key in d:
				try:
					data[key] = d[key][-1]
				except:
					pass
			queue.put(data)
			
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


def runPlot(queue):
	
	plt = PlotObject(nrows = 3, ncols = 1, queue=queue)
	plt.InitializeData(d)
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

	_thread.start_new_thread(CustomStop, (plt,))
	plt.startPlot()



def CustomStop(plt):

	def StopProgram():
		button.config(text="fix plot")
		#SEND STOP COMMAND TO ROBOT
		try:
			plt.stopPlot()
		except:
			pass

	window = tk.Tk()
	window.title("EV3 Custom Stop")
	window.config(bg='#567')
	ws = window.winfo_screenwidth()
	hs = window.winfo_screenheight()
	w = 250
	h = 250
	x = ws - (w) 	#(ws/2) - (w/2)
	y = hs/2 - h/2 #(hs/2) - (h/2)
	window.geometry('%dx%d+%d+%d' % (w, h, x, y))
	button = tk.Button(window, text ="Stop Program!",command=StopProgram)
	button.config(font=("Consolas",15))
	button.place(relx=.5, rely=.5, anchor="center", width = 200, height = 200)
	window.mainloop()

def addData(sock,plotQueue):
	# On laptop reading from socket
	socketData = fetchData(sock)
	while True:
		try:
			bytesData = next(socketData)
			if bytesData == b'':
				continue
			elif bytesData == b"end":
				print("Recieved end signal")
				break
			Data = json.loads(bytesData)
			unpackAndPlot(Data,plotQueue)	
		except Exception as e:
			print(f"error occured when reading socket {e}")
			continue



def main():
	
	signal_queue = Queue()
	producer = Process(target=setup_socket, args = (signal_queue,))
	producer.start()

	# blocks until server loads
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


	plotQueue = Queue()
	adder = Process(target=addData, args = (sock,plotQueue))
	adder.start()
	runPlot(plotQueue)



# Generator to read socket bytes fifo
def fetchData(sock):
	bytesData = b""
	while True:
		bytesData += sock.recv(2048)
		idx = bytesData.find(b"?")
		if idx != -1:
			packet = bytesData[:idx]
			if bytesData[idx:] == b"?":
				bytesData = b""
			else:
				bytesData = bytesData[idx+1:]
			yield packet # do something with packet
		
def unpackAndPlot(data,queue):
	try:
		# finding the longest list
		max_index = 0
		for key in data:
			if len(data[key]) > max_index:
				max_index = len(data[key])
		#________________________

		for k in range(max_index):
			dataToPlot = Bunch() 
			for key in data:
				dataToPlot[key] = data[key][k]
			queue.put(dataToPlot)
	except Exception as e:
		pass
		#print(f"oh no error {e}",flush=True)

	
if __name__=="__main__":
	main()