# -*- coding: utf-8 -*-
# Legger til mappene i søkestien for imports bare når programmet kjører
import os
import sys
from HovedFiler.Main import Configs
sys.path.append(os.getcwd())
sys.path.append(os.getcwd()+"/"+"HovedFiler")
sys.path.append(os.getcwd()+"/"+"moduler")
#_______________________________________________________
import matplotlib
import json
import tkinter as tk


# Bruk modulen til å velge datapunkter om den er installert
Interactivity = True
try:
	from reliability.Other_functions import crosshairs
except:
	Interactivity = False
#_______________________________________


# Klassen som inneholder data og metoder til visualisering av plott

class PlotObject:

	def __init__(self, Data, Configs, sock=None, gui=True):
		self.Data = Data
		self.sock = sock
		self.Configs = Configs
		self.gui = gui
		self.bytesData = b""
		self.validSubplot = {}

	def create(self, nrows, ncols, sharex=False):

		# Qt5Agg/QtAgg er ideelle backends (etter min mening) på mac (veldig rask og responsivt). 
		# TkAgg og macosx er ok backends. (TkAgg ser ut som å være default backend på windows)
		# macosx fungerer ikke med plottemetode 2

		# detekterer plotte-metode 2 og prøver å skifte backend (gir status melding i konsollen)
		print("\n___Status for plotting___",flush=True)
		try:
			matplotlib.use(Configs.plotBackend)
			print(f"The student has chosen backend {Configs.plotBackend}",flush=True)
		except:
			if  matplotlib.get_backend().lower() == "macosx": #Configs.plotMethod == 2 and
				backends = ["Qt5Agg","QtAgg","TkAgg"]
				success=0
				for b in backends:
					try:
						matplotlib.use(b)
						print(f"Switching backend from macosx to {b}",flush=True)
						success=1
						break
					except:
						pass
				if not success:
					print("Important: Please choose plot-method 1. read more here: https://matplotlib.org/3.5.0/users/explain/backends.html",flush=True)
					print("Failed to switch backend from macosx",flush=True)
		import matplotlib.pyplot as plt
		from matplotlib.animation import FuncAnimation
		self.plt = plt
		self.FuncAnimation = FuncAnimation
		print(f"Using backend {matplotlib.get_backend().lower()} for plotting",flush=True)
		if matplotlib.get_backend().lower() == "macosx" and Configs.plotMethod == 2:
			print("macosx backend does not support plot-method 2!",flush=True)
		print("___________________________\n",flush=True)
		#__________________________________________________________________


		if Configs.Online and self.gui:
			self.window = tk.Tk()
		self.nrows = nrows
		self.ncols = ncols
		self.fig, self.ax = plt.subplots(nrows, ncols, sharex=sharex)
		self.counter = 0
		self.Mapping = {}
		self.figure_list = []
		self.x_label_list = []
		self.y_label_list = []
		self.lines = {}

		# keep track of highest/lowest value to manually update limits of y-axis when blitting
		self.y_limits = {}

		# formats the subplots to one dimension list
		if self.nrows*self.ncols > 1:
			iterator = self.ax.flat
		else:
			iterator = [self.ax]

		for subplot in iterator:
			
			if Configs.plotMethod == 2:
				subplot.tick_params(axis='x', colors='white') 
				subplot.tick_params(axis='y', colors='white')

			# initiates a map/dict to be used to access the artists easier
			self.Mapping[subplot] = {
				"min": None, 
				"max": None,
				"maxX": None,
				"x_label": None,
			}


		

	def plot(self, subplot, xListName,  yListName, **kwargs):
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

		self.validSubplot[subplot] = True

	def figureTitles(self):
		return *self.figure_list, *self.x_label_list, *self.y_label_list

	
	def plotData(self):

		if Configs.plotMethod == 1:
			for lineInfo in self.lines.values():
				subplot = lineInfo["subplot"]
				for line in subplot.get_lines():
					line.remove()
				
		
		# Håndtering av plottemetoder
		for line in self.lines.values():
			if Configs.plotMethod == 1:
				self.Extended(line)
			elif Configs.plotMethod == 2:
				self.Blitting(line)
			else:
				raise Exception("Velg plottemetode 1 eller 2")


	def live(self,i): # i is required internally (removing this causes bugs when resizing window)
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
					break

				try:
					rowOfData = json.loads(rowOfData)
					for key in rowOfData:
						self.Data[key].append(rowOfData[key])
						if Configs.plotMethod == 2:				
							if not key in self.y_limits:
								self.y_limits[key] = [rowOfData[key],rowOfData[key]]
							elif rowOfData[key] < self.y_limits[key][0]:
								self.y_limits[key][0] = rowOfData[key]
							elif rowOfData[key] > self.y_limits[key][1]:
								self.y_limits[key][1] = rowOfData[key]
							#_________________________________
					
				except json.decoder.JSONDecodeError:
					self.bytesData += rowOfData

				except Exception as e:
					print('unknown error')
					print(e,flush=True)
					continue
			
			self.plotData()

		except KeyError as e:
			print(f'Variabelen {e} er ikke definert')
			print('Sjekk om navnet er stavet riktig (case sensitive)')
			self.stopPlot()
			return
		except ValueError as e:
			print(e)
			print('En variabel har mest sannsynlig ikke blitt sent til livePlot')
			self.stopPlot()
			return
		except Exception as e:
			print("Unknown Error when plotting")
			print(e)
			print(type(e))
			self.stopPlot()
			return
		return *self.figure_list, *self.x_label_list, *self.y_label_list 


	def stopPlot(self):
		
		# hide invalid subplots
		if self.nrows*self.ncols > 1:
			iterator = self.ax.flat
		else:
			iterator = [self.ax]
		for subplot in iterator:
			if not subplot in self.validSubplot:
				subplot.axis('off')
		#______________________

		# stop liveplot event
		try:
			self.livePlot.pause()
			self.livePlot.event_source.stop()
			self.livePlot._stop()
		except Exception as e:
			if Configs.Online:
				print(f"Error when trying to stop plot event (ikke problem): {e}",flush=True)
				

		# clear old lines before redrawing
		if Configs.plotMethod == 1:
			try:
				for lineInfo in self.lines.values():
					subplot = lineInfo["subplot"]
					for line in subplot.get_lines():
						line.remove()
			except Exception as e:
				print(f'stopping plot status: {e}',flush=True)
		
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
			if Configs.plotMethod == 2:
				subplot.tick_params(axis='x', colors='black') 
				subplot.tick_params(axis='y', colors='black')

		if Interactivity:
			crosshairs(xlabel="x",ylabel="y",decimals=Configs.desimaler) #it is important to call this last

		if Configs.plotMethod == 2:
			self.plt.tight_layout()
		if Configs.Online and self.gui:
			self.window.withdraw()
		self.plt.pause(0) # blokkerer programmet så vi unngår at alt lukkes
	

		

	# plotte-metode 2: Veldig rask, men ulempen er at akseverdier ikke vises
	# har lagt til labels for å få et bedre inntrykk av x og y verdier 
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
			
			#min_y = max_y = self.Data[yListName][-1]
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
				max_y += 1e-10
				min_y -= 1e-10
			dy = 0.1*(max_y-min_y)


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

	# Litt tregere plottemetode, men vi får vist frem akseverdier
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
				label= f"{yname}: {round(self.Data[yListName][-1],2)}"
			)
		else:
			subplot.plot(
				self.Data[xListName], 
				self.Data[yListName], 
				color=color,
				linestyle=linestyle, 
				linewidth=linewidth, 
				marker=marker,
				label= f"{yname}: {round(self.Data[yListName][-1],2)}"
			)
		subplot.legend(loc='upper left', frameon=False)

	def startPlot(self):
		
		if Configs.Online and self.gui:
			# Sender signal for å stoppe robot og stopper plottet
			def signalRobot():
				self.sock.send(b'Stop')
				self.stopPlot()
				
			# bruker tkinter (standard library)
			self.window.title("EV3 Custom Stop")
			self.window.config(bg='#567')
			ws = self.window.winfo_screenwidth()
			hs = self.window.winfo_screenheight()
			w = 250
			h = 250
			x = ws - (w)
			y = hs/2 - h/2
			self.window.geometry('%dx%d+%d+%d' % (w, h, x, y))
			button = tk.Button(self.window, text ="Stop Program!",command=signalRobot)
			button.config(font=("Consolas",15))
			button.place(relx=.5, rely=.5, anchor="center", width = 200, height = 200)


		# hide invalid subplots
		if self.nrows*self.ncols > 1:
			iterator = self.ax.flat
		else:
			iterator = [self.ax]
		for subplot in iterator:
			if not subplot in self.validSubplot:
				subplot.axis('off')
		#______________________


		# liveplot eventen som er ansvarlig for plotting.
		self.livePlot = self.FuncAnimation(self.fig, self.live, init_func=self.figureTitles, interval=1, blit=True)
		if Configs.Online and self.gui:
			self.plt.show(block=False)
			self.window.mainloop()
		self.plt.show()


	
	
if __name__ == "__main__":
	pass