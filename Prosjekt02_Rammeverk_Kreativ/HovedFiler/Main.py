# Rammeverk med mulighet å sende inputs til roboten fra pc

# +++++++++++++++++++++++++++++ IKKE ENDRE ++++++++++++++++++++++++++++++++++++++++
# Setter opp midlertidige søkestier og importerer pakker (sjekker om vi er på ev3)
import os
import sys
import json
from time import perf_counter, sleep
sys.path.append(os.getcwd())
sys.path.append(os.getcwd()+"/"+"HovedFiler")
sys.path.append(os.getcwd()+"/"+"moduler")
if sys.implementation.name.lower().find("micropython") != -1:
	from EV3AndJoystick import *
	import config
from MineFunksjoner import *
from funksjoner import *
d = Bunch()					# dataobjektet ditt (punktum notasjon)
Configs = Bunch()			# konfiguarsjonene dine
_g = Bunch()				# initalverdier kun for bruk i addmeasurement og mathcalculations 
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



# SEKSJON 1: KONFIGURASJON, VARIABLER, SENSORER, MÅLINGER, BEREGNINGER, MOTORPÅDRAG

#++++++++++++++++++++++++++++++++++++++++++ Konfigurasjoner +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Configs.EV3_IP = "169.254.187.134"		# se ip-adressen på skjermen til ev3-roboten
Configs.Online = True					# kjører du programmet uten robot, så er det Online=False
Configs.livePlot = True					# lar deg plotte live. Sett til False og få lavere tidsskritt, men ingen plott
Configs.plotMethod = 2					# (1,2) mulige metoder å plotte på (hver med sine fordeler og ulemper).
Configs.desimaler = 3 					# antall desimal for punktmarkering (om du har reliability pakken installert) 

Configs.filename = "P0X_BeskrivendeTekst_Y.txt"					# Eksempel: P01_NumeriskIntegrasjon_1.txt		
Configs.filenameOffline = "Offline_P0X_BeskrivendeTekst_Y.txt"	# Eksempel: Offline_P01_NumeriskIntegrasjon_1.txt
Configs.plotBackend = ""				# qt5agg, qtagg, tkagg, macosx. Ønsker du spesifikt å bruke end backend, skriv den her
Configs.limitMeasurements = False		# mulighet å kjøre programmet lenge uten at roboten kræsjer pga minnet (kommer selvsagt med ulemper)
Configs.controlRobot = True			# send input from laptop to robot
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


#++++++++++++++++ Variabler (lister) for målinger og beregninger ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# OBS! Bruk kun punktum notasjon for dette objektet d.variabelnavn = [] (ikke d["variabelnavn"] = [])
# Vanlige variabler skal ikke ende med "_" (underscode). Dette er forbeholdt kommunikasjon mellom pc og robot
d.Tid = []          
d.PowerA = []
d.PowerB = []
d.PowerC = []
d.PowerD = []
d.Ts = []


# OBS! input-variabler som skal sendes til roboten MÅ SLUTTE MED "_".
# andre variabler skal ikke slutte med "_" ellers blir programmet forvirret.
# Dette er fordi roboten kjører egen kode for disse 
d.W_ = []
d.A_ = []
d.S_ = []
d.D_ = []


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


# oppdater portnummer for sensorer til roboten
# port S1, S2, S3, S4 ligger på undersiden av ev3 (brukes for sensorer) 
# port A, B, C ,D ligger på oversiden av ev3 (brukes for motorer)
def setPorts(r, devices, port):
	r.motorA = devices.Motor(port.A)
	r.motorB = devices.Motor(port.B)
	r.motorC = devices.Motor(port.C)
	r.motorD = devices.Motor(port.D)
	"""
	r.ColorSensor = devices.ColorSensor(port.S1) # lyssensoren
	r.TouchSensor = devices.TouchSensor(port.SX)
	r.UltrasonicSensor = devices.UltrasonicSensor(port.SX)
	r.GyroSensor = devices.GyroSensor(port.SX)
	
	r.motorA = devices.Motor(port.A)
	r.motorB = devices.Motor(port.B)
	r.motorC = devices.Motor(port.C)
	r.motorD = devices.Motor(port.D)

	# resetting angles of motors
	r.motorA.reset_angle(0)
	r.motorB.reset_angle(0)
	r.motorC.reset_angle(0)
	r.motorD.reset_angle(0)
	"""
#___________________________________________



# SEKSJON (1.5). NYTT OM KOMMUNIKASJON MELLOM PC OG ROBOT

# Sender over inputs fra pc til roboten. 
# Variabelen som legges i "inputs={}" må matche med variabelen i definert i "d".
# Eksempel: Du spesifiserer d.W_, da må du sende inputs["W_"]. 
# PC sender dette til roboten som legger det inn automatisk for deg rett før addMeasurements()
def sendInputs(connection):

	# du står fritt til å importere pakker i python som lar deg lese mus/tastur eller andre inputs 
	# som du kan sende til roboten. Under er et eksempel på keyboard-pakken
	# pip install keyboard
	import keyboard  # https://github.com/boppreh/keyboard#api  (et eksempel på en pakke som kan lese tastatur)
	while True:
		inputs = {}
		if keyboard.is_pressed('w'): inputs["W_"] = True
		if keyboard.is_pressed('a'): inputs["A_"]= True
		if keyboard.is_pressed('s'): inputs["S_"] = True
		if keyboard.is_pressed('d'): inputs["D_"] = True

		#+++++++++ sender over data til PC (Ikke endre) ++++++++++++
		if inputs != {}:
			msg = parseInput(inputs)
			connection.send(msg)
		sleep(0.05)
		#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	

#_______________________________________________________
 
	


# legg til målinger fra roboten inn i listene du ønsker
# husk at målinger kommer fra avlesning av sensorene til roboten (ikke beregninger)
# d: data  | "data-objektet" der du får take i variablene dine med punktum notasjon e.g (d.Tid)
# r: robot | inneholder sensorer, motorer og diverse
# _g: initalverdier som settes i addMeasurements ved k==0 og kan også brukes i mathcalculations
# k: indeks som starter på 0 og øker [0,--> uendelig]
# config: inneholder joystick målinger
# VIKTIG: Må bare inneholde målinger og første måling må være tilstede i listen når k == 0
def addMeasurements(d,r,_g,k):
	if k==0:        
		# Definer initialverdier for målinger inn i _g variabelen.
		# Disse kan også bli brukt i mathcalculations 
		_g.start_tidspunkt = perf_counter() 			# lagrer første time_stamp
		d.Tid.append(0)
	else:
		# lagrer "målinger" av tid
		d.Tid.append(perf_counter() - _g.start_tidspunkt)
	

	
	"""
	d.LysDirekte.append(r.ColorSensor.ambient())
	d.Bryter.append(r.TouchSensor.pressed())
	d.Avstand.append(r.UltrasonicSensor.distance())
	d.GyroAngle.append(r.GyroSensor.angle())
	d.GyroRate.append(r.GyroSensor.speed())

	d.VinkelPosMotorA.append(r.motorA.angle())
	d.HastighetMotorA.append(r.motorA.speed())
	d.VinkelPosMotorB.append(r.motorB.angle())
	d.HastighetMotorB.append(r.motorB.speed())
	d.VinkelPosMotorC.append(r.motorC.angle())
	d.HastighetMotorC.append(r.motorC.speed())
	d.VinkelPosMotorD.append(r.motorD.angle())
	d.HastighetMotorD.append(r.motorD.speed())

	d.joyForward.append(config.joyForwardInstance)
	d.joySide.append(config.joySideInstance)
	d.joyTwist.append(config.joyTwistInstance)
	d.joyPotMeter.append(config.joyPotMeterInstance)
	d.joyPOVForward.append(config.joyPOVForwardInstance)
	d.joyPOVSide.append(config.joyPOVSideInstance)

	d.joy1.append(config.joy1Instance)
	d.joy2.append(config.joy2Instance)
	d.joy3.append(config.joy3Instance)
	d.joy4.append(config.joy4Instance)
	d.joy5.append(config.joy5Instance)
	d.joy6.append(config.joy6Instance)
	d.joy7.append(config.joy7Instance)
	d.joy8.append(config.joy8Instance)
	d.joy9.append(config.joy9Instance)
	d.joy10.append(config.joy10Instance)
	d.joy11.append(config.joy11Instance)
	d.joy12.append(config.joy12Instance)
	"""
#______________________________________________________



# Mathcalculations (bruk målinger for å beregne og legge til nye variabler)
# OBS! funksjonen brukes både i online og offline.
def MathCalculations(d,k,_g):
	if k > 0:
		d.Ts.append(d.Tid[k]-d.Tid[k-1])


	# tastur-knapper er trykket inn
	calculatePower(d,k) # studenten lager denne funksjonen inni i MineFunksjoner filen
	
	

#__________________________________________________


# Hvis motor(er) brukes i prosjektet så sendes
# beregnet pådrag til motor(ene).
# Motorene oppdateres for hver iterasjon etter mathcalculations
def setMotorPower(d,r):
	r.motorA.dc(d.PowerA[-1])
	r.motorB.dc(d.PowerB[-1])
	r.motorC.dc(d.PowerC[-1])
	r.motorD.dc(d.PowerD[-1])
#__________________________________________________


# Når programmet slutter, spesifiser hvordan du vil at motoren(e) skal stoppe.
# Det er 3 forskjellige måter å stoppe motorene på:
# - stop() ruller videre og bremser ikke.
# - brake() ruller videre, men bruker strømmen generert av rotasjonen til å bremse.
# - hold() bråstopper umiddelbart og holder posisjonen
def stopMotors(r):
	r.motorA.stop()
	r.motorB.brake()
	r.motorC.hold()
	r.motorD.hold()
#__________________________________________________



# SEKSJON 2 SEND DATA OG PLOTTING AV DATA

# Om du har satt True på runFromPC, livePlot og Online, så får du live målinger fra ROBOTEN til PC
# vil gi litt tregere tidsskritt enn om livePlot = False (som da ikke viser noe plot)
def SendLiveData(data,robot):
	LiveData = packLiveData(data,
		"Tid",
		"W_",
		"A_",
		"S_",
		"D_",
		"PowerA",
		"PowerB",
		"PowerC",
		"PowerD",
		"Ts",
	)
	#++++++++++++++++++++++ sender over data til PC ++++++++++++++++++++++++++++++++++++++++
	msg = json.dumps(LiveData) # serializing med json tar overraskende lang tid på roboten
	robot.connection.send(bytes(msg, "utf-8") + b"?") # Sender målinger fra Ev3 til PC-en din
	#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


# Dersom nrows og ncols = 1, så har du bare ax.
# Dersom enten nrows = 1 eller ncols = 1, så gis ax 1 argument som ax[0], ax[1], osv.
# Dersom både nrows > 1 og ncols > 1,  så må ax gis 2 argumenter som ax[0,0], ax[1,0], osv
def lagPlot(plt):
	nrows = 3
	ncols = 4
	sharex = False

	plt.create(nrows,ncols,sharex)
	ax = plt.ax

	# TODO: Legg inn titler og aksenavn (optional) på subplotsene dine (eks er under)
	ax[0,0].set_title('keyboard press W')  
	ax[0,1].set_title('keyboard press A')  
	ax[0,2].set_title('keyboard press S')
	ax[0,3].set_title('keyboard press D')
	
	
	ax[1,0].set_title('PowerA')  
	ax[1,1].set_title('PowerB')
	ax[1,2].set_title('PowerC')
	ax[1,3].set_title('PowerD')

	ax[2,2].set_title('Ts')


	
	plt.plot(
		subplot         = ax[0,0],    
		xListName       = "Tid", 	# navn på x-aksen som plottes     
		yListName       = "W_",	# navn på y-aksen som plottes
		yname			= "W-knapp",
		linestyle		= "dotted",
		ycolor 			= "k"
	)

	plt.plot(
		subplot         = ax[0,1],    
		xListName       = "Tid", 	# navn på x-aksen som plottes     
		yListName       = "A_",	# navn på y-aksen som plottes
		yname			= "A-knapp",
		color			= "r",
		linestyle		= "dotted",
		ycolor 			= "k"
	)

	plt.plot(
		subplot         = ax[0,2],    
		xListName       = "Tid", 	# navn på x-aksen som plottes     
		yListName       = "S_",	# navn på y-aksen som plottes
		yname			= "S-knapp",
		color			= "g",
		linestyle		= "dotted",
		ycolor 			= "k"
	)


	plt.plot(
		subplot         = ax[0,3],    
		xListName       = "Tid", 	# navn på x-aksen som plottes     
		yListName       = "D_",	# navn på y-aksen som plottes
		yname			= "D-knapp",
		color			= "m",
		linestyle		= "dotted",
		ycolor 			= "k"
	)

	plt.plot(
		subplot         = ax[1,0],    
		xListName       = "Tid", 	# navn på x-aksen som plottes     
		yListName       = "PowerA",	# navn på y-aksen som plottes
		linestyle		= "dashed",
		ycolor 			= "k"
	)

	plt.plot(
		subplot         = ax[1,1],    
		xListName       = "Tid", 	# navn på x-aksen som plottes     
		yListName       = "PowerB",	# navn på y-aksen som plottes
		color			= "r",
		linestyle		= "dashed",
		ycolor 			= "k"
	)

	plt.plot(
		subplot         = ax[1,2],    
		xListName       = "Tid", 	# navn på x-aksen som plottes     
		yListName       = "PowerC",	# navn på y-aksen som plottes
		color			= "g",
		linestyle		= "dashed",
		ycolor 			= "k"
	)

	plt.plot(
		subplot         = ax[1,3],    
		xListName       = "Tid", 	# navn på x-aksen som plottes     
		yListName       = "PowerD",	# navn på y-aksen som plottes
		color			= "m",
		linestyle		= "dashed",
		ycolor 			= "k"
	)


	plt.plot(
		subplot         = ax[2,2],    
		xListName       = "Tid", 	# navn på x-aksen som plottes     
		yListName       = "Ts",	# navn på y-aksen som plottes
		color			= "r",
		linestyle		= "dotted",
		ycolor			= "k"
	)

#______________________________________ FERDIG _______________________________________________