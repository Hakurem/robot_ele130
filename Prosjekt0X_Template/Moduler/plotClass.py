import os
import sys
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), r'HovedFiler'))
sys.path.append(os.path.join(os.getcwd(), r'Moduler'))
#_______________________________________________________


import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from funksjoner import *
import json



# Klasse for plotting
class Plotter:
	def __init__(self, nrows, ncols, sharex):
		self.nrows = nrows
		self.ncols = ncols
		self.fig, self.ax = plt.subplots(nrows, ncols, sharex=sharex)
		self.online = True
		self.counter = 0
		
		# creates artists to be rendered and maps them with a dictionary
		self.Mapping = {}
		self.figure_list = []
		self.x_label_list = []
		self.y_label_list = []
		self.lines = {}


	def InitializeData(self, Data, Configs, sock = None):
		self.Data = Data
		self.Configs = Configs
		self.sock = sock

		# formats the subplots to one dimension list
		if self.nrows*self.ncols > 1:
			iterator = self.ax.flat
		else:
			iterator = [self.ax]

		for subplot in iterator:
			
			if self.Configs.plotMethod == 3 and self.Configs.Online:
				subplot.set_xticklabels("")
				subplot.set_yticklabels("") 

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

	def live(self,k):
		try:
			DataToOnlinePlot = self.sock.recv(1024)
		except Exception as e:
			return
		try:
			DataToOnlinePlot = DataToOnlinePlot.split(b"?")
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
				except:
					continue
				# Unpack the recieved row of data
				unpackLiveData(self.Data, rowOfData)
		except Exception as e:
			print(e)
			print("Data error")
			self.stopPlot()
			return

		return *self.figure_list, *self.x_label_list, *self.y_label_list

	def stopPlot(self):
		try:
			self.livePlot.event_source.stop()
		except:
			pass


	def plotData(self):
		
		# Håndtering av online live plotting
		if self.Configs.Online and self.Configs.livePlot:
			for line in self.lines.values():
				if self.Configs.plotMethod == 0:
					self.Default(line)
				elif self.Configs.plotMethod == 1:
					self.Extended(line)
				elif self.Configs.plotMethod == 2:
					self.Hybrid(line)
				elif self.Configs.plotMethod == 3:
					self.Blitting(line)
				else:
					raise Exception("Velg plottemetode 1,2 eller 3 i Configs variabelen i filen Main.py")
		
		# Håndtering av plotting i offline
		elif not self.Configs.Online:
			self.Default(line)


	# PLOTTING METHODS:
	def Blitting(self, lineInfo):
		lineId          = lineInfo["lineId"]
		subplot         = lineInfo["subplot"]    
		xListName       = lineInfo["xListName"]       
		yListName       = lineInfo["yListName"]
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

			# limits min and max doesn't exist, then assign them
			if self.Mapping[subplot]["min"] is None:
				self.Mapping[subplot]["min"] = min_y

			if self.Mapping[subplot]["max"] is None:
				self.Mapping[subplot]["max"] = max_y
			
			if self.Mapping[subplot]["maxX"] is None:
				self.Mapping[subplot]["maxX"] = max_x
			#______________________________________

			# Handle axes limits for animation
			min_y = max_y = self.Data[yListName][-1]
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
				max_y += 1e-10
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


	def Hybrid(self, lineInfo):

		lineId          = lineInfo["lineId"]
		subplot         = lineInfo["subplot"]    
		xListName       = lineInfo["xListName"]       
		yListName       = lineInfo["yListName"]
		yListName       = lineInfo["yListName"]
		color           = lineInfo["color"]
		linestyle       = lineInfo["linestyle"]
		linewidth       = lineInfo["linewidth"]
		marker          = lineInfo["marker"]
		

		if yListName in self.Data and len(self.Data[yListName]) == 0:
			return
		line = None
		if subplot in self.Mapping:
			if lineId in self.Mapping[subplot]:
				line = self.Mapping[subplot][lineId]["line"]
			else:
				line, = subplot.plot([], [], color= color, linewidth = linewidth, linestyle=linestyle, marker = marker, label= str(yListName))
				self.Mapping[subplot][lineId] = {"line": line}
				self.figure_list.append(line)
				subplot.set_xlim(self.Data[xListName][0],self.Mapping[subplot]["maxX"] or 0.1)
				subplot.legend(loc='upper left', frameon=False)
				plt.show()
		if line:
			updateLimits = False
			max_x = self.Data[xListName][-1]
			min_y = max_y = self.Data[yListName][-1]
			# limits min and max doesn't exist, then assign them
			if self.Mapping[subplot]["min"] is None:
				self.Mapping[subplot]["min"] = min_y
				updateLimits = True

			if self.Mapping[subplot]["max"] is None:
				self.Mapping[subplot]["max"] = max_y
				updateLimits = True
			
			if self.Mapping[subplot]["maxX"] is None:
				self.Mapping[subplot]["maxX"] = 0.1
				updateLimits = True
			#______________________________________
			
			# Handling x-axis limits for subplots
			if max_x >= self.Mapping[subplot]["maxX"]:
				self.Mapping[subplot]["maxX"] += 10 #*=2 
				subplot.set_xlim(self.Data[xListName][0], 1.02*self.Mapping[subplot]["maxX"])
				updateLimits = True
			#___________________________________

			# Handle y-axis limits for subplots
			if min_y < self.Mapping[subplot]["min"]:
				self.Mapping[subplot]["min"] = (min_y - abs(min_y))
				updateLimits = True
			else:
				min_y = self.Mapping[subplot]["min"]

			if max_y > self.Mapping[subplot]["max"]:
				self.Mapping[subplot]["max"] = 2*max_y
				updateLimits = True
			else:
				max_y = self.Mapping[subplot]["max"]
			#__________________________________

			# Update only when necessary to avoid slowing down
			if updateLimits:
				plt.show()
			#___________________________________________________
		
			# Make sure there are some leeway (vertical) for the line so it doesn't hit the figure box
			if (max_y - min_y) == 0:
				min_y += 1e-10
				max_y += 1e-10
			dy = 0.1*(max_y-min_y)
			#__________________________________________________________
			
			dif = len(self.Data[xListName]) - len(self.Data[yListName])
			subplot.set_ylim(min_y-dy,max_y+dy)
			if dif > 0 :
				line.set_data(self.Data[xListName][:-dif], self.Data[yListName])
			else:
				line.set_data(self.Data[xListName], self.Data[yListName])

	
	def Extended(self, lineInfo):
		
		lineId          = lineInfo["lineId"]
		subplot         = lineInfo["subplot"]    
		xListName       = lineInfo["xListName"]       
		yListName       = lineInfo["yListName"]
		color           = lineInfo["color"]
		linestyle       = lineInfo["linestyle"]
		linewidth       = lineInfo["linewidth"]
		marker          = lineInfo["marker"]
			
		if yListName in self.Data and len(self.Data[yListName]) == 0:
			return
		
	
		line = None
		if subplot in self.Mapping:
			if lineId in self.Mapping[subplot]:
				line = self.Mapping[subplot][lineId]["line"]
			else:
				line, = subplot.plot([], [], color= color, linewidth = linewidth, linestyle=linestyle, marker = marker, label= str(yListName))
				self.Mapping[subplot][lineId] = {"line": line}
				self.figure_list.append(line)
				subplot.set_xlim(self.Data[xListName][0],self.Mapping[subplot]["maxX"] or 1)
				subplot.legend(loc='upper left', frameon=False)
		if line:
			scale_X = 1.02
			max_x = self.Data[xListName][-1]
			min_y = max_y = self.Data[yListName][-1]

			# limits min and max doesn't exist, then assign them
			if self.Mapping[subplot]["min"] is None:
				self.Mapping[subplot]["min"] = min_y

			if self.Mapping[subplot]["max"] is None:
				self.Mapping[subplot]["max"] = max_y
			
			if self.Mapping[subplot]["maxX"] is None:
				self.Mapping[subplot]["maxX"] = max_x
			#______________________________________

			# Handle axes limits for animation
			min_y = max_y = self.Data[yListName][-1]
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
				max_y += 1e-10
			dy = 0.1*(max_y-min_y)
			#__________________________________________________________

		
			dif = len(self.Data[xListName]) - len(self.Data[yListName])
			subplot.set_xlim(self.Data[xListName][0],scale_X*max_x or 1) #set x limit of axis    
			subplot.set_ylim(min_y-dy,max_y+dy)

			if dif > 0 :
				line.set_data(self.Data[xListName][:-dif], self.Data[yListName])
			else:
				line.set_data(self.Data[xListName], self.Data[yListName])
			plt.show(block=False)


	def Default(self, lineInfo):
		subplot         = lineInfo["subplot"]    
		xListName       = lineInfo["xListName"]       
		yListName       = lineInfo["yListName"]
		color           = lineInfo["color"]
		linestyle       = lineInfo["linestyle"]
		linewidth       = lineInfo["linewidth"]
		marker          = lineInfo["marker"]
			
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
				marker=marker
			)
		else:
			subplot.plot(
				self.Data[xListName], 
				self.Data[yListName], 
				color=color,
				linestyle=linestyle, 
				linewidth=linewidth, 
				marker=marker
			)
		


	def startPlot(self):

		if self.Configs.Online and self.Configs.livePlot: 
			self.livePlot = FuncAnimation(self.fig, self.live, init_func=self.figureTitles, interval= 10, blit=True)
			self.fig.set_tight_layout(True)
			plt.show()

		elif not self.Configs.Online:
			self.plotData()
			self.stopPlot()
			plt.show() 
		
		