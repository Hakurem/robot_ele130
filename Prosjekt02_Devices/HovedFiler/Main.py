# coding=utf-8

# +++++++++++++++++++++++++++++ IKKE ENDRE ++++++++++++++++++++++++++++++++++++++++
# Setter opp midlertidige søkestier og importerer pakker (sjekker om vi er på ev3)
import os
import sys
import json
from time import perf_counter
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



# SEKSJON 1: KONFIGURASJON, VARIABLER, SENSORER, MÅLINGER og BEREGNINGER

#++++++++++++++++++++++++++++++++++++++++++ Konfigurasjoner +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Configs.EV3_IP = "169.254.151.11"	# se ip-adressen på skjermen til ev3-roboten
Configs.Online = False				# kjører du programmet uten robot, så er det Online=False
Configs.livePlot = True				# lar deg plotte live. Sett til False og få lavere tidsskritt, men ingen plott
Configs.plotMethod = 1				# (1,2) mulige metoder å plotte på (hver med sine fordeler og ulemper).
Configs.desimaler = 3 				# antall desimal for punktmarkering (om du har mplcursors eller reliability installert) 

Configs.filename = "P02_BeskrivendeTekst_Y.txt"					# Eksempel: P01_NumeriskIntegrasjon_1.txt		
Configs.filenameOffline = "test.txt"	# Eksempel: Offline_P01_NumeriskIntegrasjon_1.txt #

Configs.limitMeasurements = False	# mulighet å kjøre programmet lenge uten at roboten kræsjer pga minnet (kommer selvsagt med ulemper)
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


#++++++++++++++++ Variabler (lister) for målinger og beregninger ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# OBS! Bruk kun punktum notasjon for dette objektet d.variabelnavn = [] (ikke d["variabelnavn"] = [])

d.Tid = []            # måling av tidspunkt
d.Lys = []     
d.Bryter = [] 
d.GyroAngle = []
d.PowerA = []
d.PowerD = []
d.Avstand = []
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


# oppdater portnummer for sensorer til roboten
# port S1, S2, S3, S4 ligger på undersiden av ev3 (brukes for sensorer) 
# port A, B, C ,D ligger på oversiden av ev3 (brukes for motorer)

def setPorts(r, devices, port):
	r.ColorSensor = devices.ColorSensor(port.S1) # lyssensoren
	r.UltrasonicSensor = devices.UltrasonicSensor(port.S2)
	r.TouchSensor = devices.TouchSensor(port.S3)
	r.GyroSensor = devices.GyroSensor(port.S4)

	r.motorA = devices.Motor(port.A)
	r.motorD = devices.Motor(port.D)

	r.motorA.reset_angle(0)
	r.motorD.reset_angle(0)
#___________________________________________


# legg til målinger fra roboten inn i listene du ønsker
# husk at målinger kommer fra avlesning av sensorene til roboten (ikke beregninger)
# d: data  | "data-objektet" der du får take i variablene dine med punktum notasjon e.g (d.Tid)
# r: robot | inneholder sensorer, motorer og diverse
# _g: initalverdier som settes i addMeasurements og brukes i mathcalculations
# k: indeks som starter på 0 og øker [0,--> uendelig]
# config: inneholder joystick målinger
# VIKTIG: Må bare inneholde målinger og første måling må være tilstede i listen når k == 0

def addMeasurements(d,r,_g,k):

	if k==0:        
		# Definer initialverdier for målinger inn i _g variabelen.
		# Disse kan også bli brukt i mathcalculations 
		_g.start_tidspunkt = perf_counter() 			# lagrer første time_stamp
		_g.lys_initial = r.ColorSensor.reflection() 	# lagrer første lysmåling som kan brukes til å beregne Flow
		d.Tid.append(0)
	else:
		# lagrer "målinger" av tid
		d.Tid.append(perf_counter() - _g.start_tidspunkt)
	
	# lagrer målinger av lys
	d.Lys.append(r.ColorSensor.reflection())
	
	
	d.Bryter.append(r.TouchSensor.pressed())
	d.GyroAngle.append(r.GyroSensor.angle())
	#d.Avstand.append(r.UltrasonicSensor.distance())
	#d.PowerA.append("JIBBERISH")
	d.PowerD.append(config.joyPotMeterInstance)
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
	# Parametre
	m = 3  # fir filter konstant
	a = 0.5 # iir-filter konstant
	# Initialverdi for beregnede variabler
	pass
#__________________________________________________


# Hvis motor(er) brukes i prosjektet så sendes
# beregnet pådrag til motor(ene).
# Motorene oppdateres for hver iterasjon etter mathcalculations
def setMotorPower(d,r):
	r.motorA.dc(d.PowerA[-1])
	r.motorD.dc(d.PowerD[-1])
#__________________________________________________


# Når programmet slutter, spesifiser hvordan du vil at motoren(e) skal stoppe.
# Det er 3 forskjellige måter å stoppe motorene på:
# - stop() ruller videre og bremser ikke.
# - brake() ruller videre, men bruker strømmen generert av rotasjonen til å bremse.
# - hold() bråstopper umiddelbart og holder posisjonen
def stopMotors(r):
	r.motorA.stop()
	r.motorD.hold()
#__________________________________________________



# SEKSJON 2 SEND DATA OG PLOTTING AV DATA

# Om du har satt True på runFromPC, livePlot og Online, så får du live målinger fra ROBOTEN til PC
# vil gi litt tregere tidsskritt enn om livePlot = False (som da ikke viser noe plot)
def SendLiveData(data,robot):
	LiveData = packLiveData(data,
		"Tid",
		"Lys",
		"Bryter",
		"GyroAngle",
		#"PowerA",
		"PowerD",
		#"Avstand"
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
	ncols = 2
	sharex = False

	plt.create(nrows,ncols,sharex)
	ax = plt.ax

	# TODO: Legg inn titler og aksenavn (optional) på subplotsene dine (eks er under)
	ax[0,0].set_title('Målinger av lys')  
	ax[0,1].set_title('Bryter')
	ax[1,0].set_title('GyroAngle')
	ax[1,1].set_title('PowerA')
	ax[2,0].set_title('PowerD')
	ax[2,1].set_title('Avstand')
	

	
	plt.plot(
		# OBLIGATORISK
		subplot         = ax[0,0],    
		xListName       = "Tid", 	# navn på x-aksen som plottes     
		yListName       = "Lys",	# navn på y-aksen som plottes
	)

	plt.plot(
		subplot         = ax[0,1],    
		xListName       = "Tid",       
		yListName       = "Bryter",
	)

	plt.plot(
		subplot         = ax[1,0],    
		xListName       = "Tid",       
		yListName       = "GyroAngle",
	)

	# plt.plot(
	# 	subplot         = ax[1,1],    
	# 	xListName       = "Tid",       
	# 	yListName       = "PowerA",
	# )

	plt.plot(
		subplot         = ax[2,0],    
		xListName       = "Tid",       
		yListName       = "PowerD",
	)

	# plt.plot(
	# 	subplot         = ax[2,1],    
	# 	xListName       = "Tid",       
	# 	yListName       = "Avstand",
	# )

	
	

#______________________________________ FERDIG _______________________________________________