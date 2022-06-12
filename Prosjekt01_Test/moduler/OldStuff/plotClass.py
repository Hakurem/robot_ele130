# Legger til mappene i søkestien for imports bare når programmet kjører
import os
import sys
p_root = os.getcwd() #root of project
sys.path.append(p_root)
sys.path.append(p_root+"/"+"HovedFiler")
sys.path.append(p_root+"/"+"moduler")
#_______________________________________________________



from time import perf_counter
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from tkinter import Tk
from time import sleep


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
	
		root = Tk()
		screen_x = root.winfo_screenwidth()
		screen_y = root.winfo_screenheight()
		root.withdraw()

		thismanager = plt.get_current_fig_manager()
		thismanager.window.wm_geometry(f"-{int(screen_x//2)}+0")
	
		self.fig.set_figheight(screen_y/100)
		self.fig.set_figwidth(screen_x/96/2)

		
		# creates artists to be rendered and maps them with a dictionary
		self.Mapping = {}
		self.figure_list = []
		self.x_label_list = []
		self.y_label_list = []
		self.lines = {}

		# overhead from animating the rocket
		self.stamp = perf_counter()
		self.y_limits = {}

		

	def InitializeData(self, Data, Configs, queue):
		self.Data = Data
		self.plotMethod = Configs.plotMethod
		self.desimaler = Configs.desimaler
		self.queue = queue


		# formats the subplots to one dimension list
		if self.nrows*self.ncols > 1:
			iterator = self.ax.flat
		else:
			iterator = [self.ax]

		for subplot in iterator:
			
			if self.plotMethod == 2:
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

	
	
	
	def live(self,_):
		
		# retreive data from queue
		#try:
			
		length = self.queue.qsize()
		if length > 0:
			for _ in range(length):
				values = self.queue.get()
				if values == "StopPlot":
					self.Stop = True
					self.stopPlot()
					return

				for key in values:
					self.Data[key].append(values[key])
					# in case of blitting we need to manually set axis limits (keeping track of max and min values)
					if self.plotMethod == 2:				
						if not key in self.y_limits:
							self.y_limits[key] = [0,0]
						elif values[key] < self.y_limits[key][0]:
							self.y_limits[key][0] = values[key]
						elif values[key] > self.y_limits[key][1]:
							self.y_limits[key][1] = values[key]
						#_________________________________
			
			self.plotData()
		
		# except (KeyError, ZeroDivisionError) as e:
		# 	print(e,flush=True)
		
		
		# except Exception as e:
		# 	print(e,flush=True)
		# 	print('i PlotConfig retreive error',flush=True)
		
		
		return *self.figure_list, *self.x_label_list, *self.y_label_list 

	def plotData(self):

		if self.plotMethod == 1:
			for lineInfo in self.lines.values():
				subplot = lineInfo["subplot"]
				for line in subplot.get_lines():
					line.remove()
		
		
		# Håndtering av plottemetoder
		for line in self.lines.values():
			if self.plotMethod == 1:
				self.Extended(line)
			elif self.plotMethod == 2:
				self.Blitting(line)
			else:
				raise Exception("Velg plottemetode 1 eller 2")


	def stopPlot(self):
		# clear canvas  and redraw canvas
		if self.plotMethod == 1:
			try:
				for lineInfo in self.lines.values():
					subplot = lineInfo["subplot"]
					for line in subplot.get_lines():
						line.remove()
			except Exception as e:
				print(f'issues with stopping plot: {e}',flush=True)
		
		# stop liveplot event
		try:
			self.livePlot.event_source.stop()
			self.livePlot._stop()
		except Exception as e:
			print(f"error when trying to stop plot event{e}",flush=True)
			pass
		

		sleep(0.1)
		
		
		# Remove labels and lines from our custom storage
		for line in self.figure_list:
			line.remove()
			
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
			if self.plotMethod == 2:
				subplot.tick_params(axis='x', colors='black') 
				subplot.tick_params(axis='y', colors='black')

		
		if Interactivity:
			crosshairs(xlabel="x",ylabel="y",decimals=self.desimaler) #it is important to call this last   
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
		self.livePlot = FuncAnimation(self.fig, self.live, init_func=self.figureTitles, interval=0, blit=True)
		plt.show()  
	
