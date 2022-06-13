from time import perf_counter
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from Main import d, plotMethod, desimaler
import json
from time import sleep
import tkinter as Tk



class Bunch(dict):
    def __init__(self, *args, **kwds):
        super(Bunch, self).__init__(*args, **kwds)
        self.__dict__ = self

# If we have installed reliability, use it
Interactivity = True
try:
	from reliability.Other_functions import crosshairs
except:
	Interactivity = False

#_______________________________________

class PlotObject:
	def __init__(self, nrows, ncols, sharex=True):


		self.nrows = nrows
		self.ncols = ncols
		self.fig, self.ax = plt.subplots(nrows, ncols, sharex=sharex)
		self.counter = 0
		
		try:
			root = Tk()
			screen_x = root.winfo_screenwidth()
			screen_y = root.winfo_screenheight()
			root.withdraw()

			thismanager = plt.get_current_fig_manager()
			thismanager.window.wm_geometry(f"-{int(screen_x//2)}+0")
		
			self.fig.set_figheight(screen_y/100)
			self.fig.set_figwidth(screen_x/96/2)
		except:
			print('kan ikke endre posisjon av plotvindu på MAC',flush=True)
			pass
		


		self.Data = d
		
		# creates artists to be rendered and maps them with a dictionary
		# self.reDraw = {}
		self.Mapping = {}
		self.figure_list = []
		self.x_label_list = []
		self.y_label_list = []
		self.lines = {}

		# keep track of highest/lowest value to manually update limits of y-axis when blitting
		self.y_limits = {}


	def InitializeData(self, Data, sock):
		self.Data = Data
		self.sock = sock
		#self.socketData = self.fetchData(sock)
		self.bytesData = b""


		# formats the subplots to one dimension list
		if self.nrows*self.ncols > 1:
			iterator = self.ax.flat
		else:
			iterator = [self.ax]

		for subplot in iterator:
			
			if plotMethod == 2:
				subplot.tick_params(axis='x', colors='white') 
				subplot.tick_params(axis='y', colors='white')

			# initiates a map/dict to be used to access the artists easier
			self.Mapping[subplot] = {
				"min": None, 
				"max": None,
				"maxX": None,
				"x_label": None,
			}




	def createlines(self, subplot, xListName,  yListName, **kwargs):
		lineInfo = {}

		# REQUIRED
		lineInfo["lineId"] = self.counter
		lineInfo["subplot"] = subplot
		lineInfo["xListName"] = xListName
		lineInfo["yListName"] = yListName

		# OPTIONAL
		lineInfo["color"] = kwargs.get("color","b") or "b"
		lineInfo["linestyle"] = kwargs.get("linestyle","solid") or "solid"
		lineInfo["linewidth"] = kwargs.get("linewidth",1) or 1
		lineInfo["marker"] = kwargs.get("marker","")

		# FULL BLITTING OPTIONAL
		lineInfo["xname"] =  kwargs.get("xname",xListName) or xListName
		lineInfo["yname"] = kwargs.get("yname",yListName) or yListName
		lineInfo["ycolor"] = kwargs.get("ycolor",lineInfo["color"]) or lineInfo["color"]

		self.lines[self.counter] = lineInfo
		self.counter +=1

	def figureTitles(self):
		return *self.figure_list, *self.x_label_list, *self.y_label_list

	
	def plotData(self):

		if plotMethod == 1:
			for lineInfo in self.lines.values():
				subplot = lineInfo["subplot"]
				for line in subplot.get_lines():
					line.remove()
				
		
		# Håndtering av plottemetoder
		for line in self.lines.values():
			if plotMethod == 1:
				self.Extended(line)
			elif plotMethod == 2:
				self.Blitting(line)
			else:
				raise Exception("Velg plottemetode 1 eller 2")

	
	# Generator to read socket bytes fifo
	"""
	def fetchData(self,sock):
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
	"""


	def live(self,i): # i is required internally (removing this causes bugs when resizing window)
		"""
		try:
			bytesData = next(self.socketData)
			if bytesData == b"end":
				print("Recieved end signal")
			rowOfData = json.loads(bytesData)
			for key in rowOfData:
				self.Data[key].append(rowOfData[key])
				if plotMethod == 2:				
					if not key in self.y_limits:
						self.y_limits[key] = [0,0]
					elif rowOfData[key] < self.y_limits[key][0]:
						self.y_limits[key][0] = rowOfData[key]
					elif rowOfData[key] > self.y_limits[key][1]:
						self.y_limits[key][1] = rowOfData[key]
					#_________________________________

			self.plotData()

		except Exception as e:
			print(f"error occured when reading socket {e}")
		
		"""

		try:
			self.bytesData += self.sock.recv(1024)
		except Exception as e:
			print(e,flush=True)
			print("Lost connection to EV3",flush=True)
			self.stopPlot()

		try:
			DataToOnlinePlot = self.bytesData.split(b"?")
			self.bytesData = b""
			for rowOfData in DataToOnlinePlot:
				if rowOfData == b'':
					continue
				# If the data received is the end signal, freeze plot.
				elif rowOfData == b"end":
					print("Recieved end signal")
					self.stopPlot()
					return
				try:
					rowOfData = json.loads(rowOfData)
					for key in rowOfData:
						self.Data[key].append(rowOfData[key])
						
						if plotMethod == 2:				
							if not key in self.y_limits:
								self.y_limits[key] = [0,0]
							elif rowOfData[key] < self.y_limits[key][0]:
								self.y_limits[key][0] = rowOfData[key]
							elif rowOfData[key] > self.y_limits[key][1]:
								self.y_limits[key][1] = rowOfData[key]
							#_________________________________
				except json.decoder.JSONDecodeError:
					self.bytesData += rowOfData

				except Exception as e:
					print(e,flush=True)
					continue
			
			self.plotData()

		except Exception as e:
			print(e)
			print("Data error")
			self.stopPlot()
			return
		

		return *self.figure_list, *self.x_label_list, *self.y_label_list 


	def stopPlot(self):
		
		# stop liveplot event
		try:
			self.livePlot.event_source.stop()
			self.livePlot._stop()
		except Exception as e:
			print(f"error when trying to stop plot event{e}",flush=True)
			pass
		

		sleep(0.1)


		# clear canvas  and redraw canvas
		if plotMethod == 1:
			try:
				for lineInfo in self.lines.values():
					subplot = lineInfo["subplot"]
					subplot.get_legend().remove()
					for line in subplot.get_lines():
						line.remove()
					
			except Exception as e:
				print(f'issues with stopping plot: {e}',flush=True)
		
		
		# Remove labels and lines from our custom storage
		for line in self.figure_list:
			try:
				line.remove()
			except:
				pass
			
		for xlabel in self.x_label_list:
			xlabel.remove()

		for ylabel in self.y_label_list:
			ylabel.remove()
		#_______________________________________________

		for lineInfo in self.lines.values():
			subplot         = lineInfo["subplot"]    
			xListName       = lineInfo["xListName"]       
			yListName       = lineInfo["yListName"]
			color           = lineInfo["color"] 
			linestyle       = lineInfo["linestyle"]
			linewidth       = lineInfo["linewidth"]
			marker          = lineInfo["marker"]
			yname			= lineInfo["yname"]


			dif = len(self.Data[xListName]) - len(self.Data[yListName])
			if dif > 0 :
				subplot.plot(
					self.Data[xListName][:-dif], 
					self.Data[yListName], 
					color=color,
					linestyle=linestyle, 
					linewidth=linewidth, 
					marker=marker,
					label= str(yname)
				)
				
			else:
				subplot.plot(
					self.Data[xListName], 
					self.Data[yListName], 
					color=color,
					linestyle=linestyle, 
					linewidth=linewidth, 
					marker=marker,
					label= str(yname),
				)
				
			
			subplot.legend(loc='upper left', frameon=False)
			if plotMethod == 2:
				subplot.tick_params(axis='x', colors='black') 
				subplot.tick_params(axis='y', colors='black')

		
		if Interactivity:
			crosshairs(xlabel="x",ylabel="y",decimals=desimaler) #it is important to call this last   
		plt.show()
		

	# PLOTTING METHODS:
	def Blitting(self, lineInfo):
		lineId          = lineInfo["lineId"]
		subplot         = lineInfo["subplot"]    
		xListName       = lineInfo["xListName"]       
		yListName       = lineInfo["yListName"]
		color           = lineInfo["color"]
		linestyle       = lineInfo["linestyle"]
		linewidth       = lineInfo["linewidth"]
		marker          = lineInfo["marker"]
		xname			= lineInfo["xname"]
		yname			= lineInfo["yname"]
		ycolor			= lineInfo["ycolor"]

		if yListName in self.Data and len(self.Data[yListName]) == 0:
			return

		line = None
		y_label = None
		x_label = None

		if subplot in self.Mapping:
			if not self.Mapping[subplot]["x_label"]:
				x_label = subplot.text(x=0.5,y = 0, s="x-value", bbox={'facecolor':'w', 'alpha':0.5, 'pad':5},
						transform=subplot.transAxes, ha="center", va = "bottom")
				self.Mapping[subplot]["x_label"] = x_label
				self.x_label_list.append(x_label,)
			else:
				x_label = self.Mapping[subplot]["x_label"]

			if lineId in self.Mapping[subplot]:
				line = self.Mapping[subplot][lineId]["line"]
				y_label = self.Mapping[subplot][lineId]["y_label"]
			else:
				line, = subplot.plot([], [], color= color, linewidth = linewidth, linestyle=linestyle, marker = marker)
				y_label = subplot.text(x=0,y = 0, s="y-value", ha='right', va='center')
				self.Mapping[subplot][lineId] = {"line": line, "y_label": y_label}
				self.figure_list.append(line)
				self.y_label_list.append(y_label,)

		if line:
			scale_X = 1.02
			max_x = self.Data[xListName][-1] or 0.1
			min_y = max_y = self.Data[yListName][-1]

			
			min_y = self.y_limits[yListName][0]
			max_y = self.y_limits[yListName][1]

			
			# limits min and max doesn't exist, then assign them
			if self.Mapping[subplot]["min"] is None:
				self.Mapping[subplot]["min"] = min_y

			if self.Mapping[subplot]["max"] is None:
				self.Mapping[subplot]["max"] = max_y
			
			if self.Mapping[subplot]["maxX"] is None:
				self.Mapping[subplot]["maxX"] = max_x
			#______________________________________

			

			# Handle axes limits for animation
			
			if min_y < self.Mapping[subplot]["min"]:
				self.Mapping[subplot]["min"] = min_y
			else:
				min_y = self.Mapping[subplot]["min"]

			if max_y > self.Mapping[subplot]["max"]:
				self.Mapping[subplot]["max"] = max_y
			else:
				max_y = self.Mapping[subplot]["max"]
			#__________________________________


			# Make sure there are some leeway for the line so it doesn't hit the figure box
			if (max_y - min_y) == 0:
				min_y += 1e-10
				max_y -= 1e-10
			dy = 0.1*(max_y-min_y)
			#__________________________________________________________

			dif = len(self.Data[xListName]) - len(self.Data[yListName])
			subplot.set_xlim(self.Data[xListName][0],scale_X*max_x) #set x limit of axis    
			subplot.set_ylim(min_y-dy,max_y+dy)

			if dif > 0 :
				line.set_data(self.Data[xListName][:-dif], self.Data[yListName])
			else:
				line.set_data(self.Data[xListName], self.Data[yListName])
		
			x_label.set_text(f"{xname}: {round(self.Data[xListName][-1],1)}") 
			y_label.set_color(ycolor)
			y_label.set_text(f"{yname}: {round(self.Data[yListName][-1],2)}")
			
			y_label.set_x(self.Data[xListName][-1])
			y_label.set_y(self.Data[yListName][-1])


	def Extended(self, lineInfo):
		
		subplot         = lineInfo["subplot"]    
		xListName       = lineInfo["xListName"]       
		yListName       = lineInfo["yListName"]
		color           = lineInfo["color"]
		linestyle       = lineInfo["linestyle"]
		linewidth       = lineInfo["linewidth"]
		marker          = lineInfo["marker"]
		yname			= lineInfo["yname"]

		if yListName in self.Data and len(self.Data[yListName]) == 0:
			return

		dif = len(self.Data[xListName]) - len(self.Data[yListName])
		if dif > 0 :
			subplot.plot(
				self.Data[xListName][:-dif], 
				self.Data[yListName], 
				color=color,
				linestyle=linestyle, 
				linewidth=linewidth, 
				marker=marker,
				label= f"{yname}: {round(self.Data[yListName][-1],20)}"
			)
		else:
			subplot.plot(
				self.Data[xListName], 
				self.Data[yListName], 
				color=color,
				linestyle=linestyle, 
				linewidth=linewidth, 
				marker=marker,
				label= f"{yname}: {round(self.Data[yListName][-1],20)}"
			)

		subplot.legend(loc='upper left', frameon=False)

	def startPlot(self):
		print("CALL TO START",flush=True)
		self.livePlot = FuncAnimation(self.fig, self.live, init_func=self.figureTitles, interval=1, blit=True)
		plt.show()  
	
