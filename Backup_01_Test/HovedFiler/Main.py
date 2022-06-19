# coding=utf-8

# +++++++++++++++++++++++++++++ IKKE ENDRE ++++++++++++++++++++++++++++++++++++++++
# Setter opp søkestier og importerer pakker (sjekker om vi er på ev3 eller på pc)
import os
import sys
import json
from time import perf_counter
sys.path.append(os.getcwd())
sys.path.append(os.getcwd()+"/"+"HovedFiler")
sys.path.append(os.getcwd()+"/"+"moduler")
if sys.implementation.name.lower().find("micropython") != -1:
	from EV3AndJoystick import *
from MineFunksjoner import *
from funksjoner import *
d = Bunch()					# dataobjektet ditt (punktum notasjon)
Configs = Bunch()			# konfiguarsjonene dine
_g = Bunch()				# globale variabler lagres i denne listen
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



# SEKSJON 1: KONFIGURASJON, VARIABLER, SENSORER, MÅLINGER og BEREGNINGER

#++++++++++++++++++++++++++++++++++++++++++ Konfigurasjoner +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Configs.EV3_IP = "169.254.123.184"	# se ip-adressen på skjermen til ev3-roboten
Configs.Online = True				# kjører du programmet uten robot, så er det Online=False
Configs.runFromPC = True			# programmet kjøres fra PC (True) eller KUN fra Ev3-roboten (False) (Det vi kalte wired før)
Configs.livePlot = True				# lar deg plotte live. Kan sette false om du ønsker mindre tids-skritt uten å måtte ta av ledning
Configs.plotMethod = 2				# (1,2) mulige metoder å plotte på (hver med sine fordeler og ulemper).
Configs.desimaler = 3 				# sett antall desimaler ved manuell markering av (x,y) verdi etter plott 

Configs.filenameMeas = "measurements.txt"
Configs.filenameCalcOnline = "calculations.txt" 
Configs.filenameCalcOffline = ".txt"  

Configs.limitMeasurements = False	# mulighet å kjøre programmet lenge uten at roboten kræsjer pga minnet (kommer selvsagt med ulemper)
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


#++++++++++++++++ Variabler (lister) for målinger og beregninger ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# OBS! Bruk kun punktum notasjon for dette objektet d.variabelnavn = [] (ikke d["variabelnavn"] = [])

d.Tid = []            # måling av tidspunkt
d.Lys = []            # måling av reflektert lys fra ColorSensor

d.Ts = []             # beregning av tidsskritt
d.Flow = []           # beregning som bruker målingen lys og trekker fra første lysmåling (normalisering)
d.Euler = []   		  # beregninger av numerisk integrasjon ved Euler metode


"""
d.LysDirekte = []         # måling av lys direkte inn fra ColorSensor
d.Bryter = []             # registrering av trykkbryter fra TouchSensor
d.Avstand = []            # måling av avstand fra UltrasonicSensor
d.GyroAngle = []          # måling av gyrovinkel fra GyroSensor
d.GyroRate = []           # måling av gyrovinkelfart fra GyroSensor

d.VinkelPosMotorA = []    # vinkelposisjon motor A
d.HastighetMotorA = []    # hastighet motor A
d.VinkelPosMotorB = []    # vinkelposisjon motor B 
d.HastighetMotorB = []    # hastighet motor B
d.VinkelPosMotorC = []    # vinkelposisjon motor C
d.HastighetMotorC = []    # hastighet motor C
d.VinkelPosMotorD = []    # vinkelposisjon motor D
d.HastighetMotorD = []    # hastighet motor D

d.joyForward = []         # måling av foroverbevegelse styrestikke
d.joySide = []            # måling av sidebevegelse styrestikke
d.joyTwist = []           # måling av vribevegelse styrestikke
d.joyPotMeter = []        # måling av potensionmeter styrestikke
d.joyPOVForward = []      # måling av foroverbevegelse toppledd
d.joyPOVSide = []         # måling av sidebevegelse toppledd

d.joy1 = []               # måling av knapp 1 (skyteknappen)
d.joy2 = []               # måling av knapp 2 (ved tommel)
d.joy3 = []               # måling av knapp 3 
d.joy4 = []               # måling av knapp 4 
d.joy5 = []               # måling av knapp 5 
d.joy6 = []               # måling av knapp 6 
d.joy7 = []               # måling av knapp 7 
d.joy8 = []               # måling av knapp 8 
d.joy9 = []               # måling av knapp 9 
d.joy10 = []              # måling av knapp 10 
d.joy11 = []              # måling av knapp 11 
d.joy12 = []              # måling av knapp 12

d.PowerA = []         # berenging av motorpådrag A
d.PowerB = []         # berenging av motorpådrag B
d.PowerC = []         # berenging av motorpådrag C
d.PowerD = []         # berenging av motorpådrag D
"""
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


# oppdater portnummer for sensorer til roboten
# port S1, S2, S3, S4 ligger på undersiden av ev3 (brukes for sensorer) 
# port A, B, C ,D ligger på oversiden av ev3 (brukes for motorer)

def setPorts(r, devices, port):
	r.ColorSensor = devices.ColorSensor(port.S1) # lyssensoren
	"""
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


# legg til målinger fra roboten inn i listene du ønsker
# husk at målinger kommer fra avlesning av sensorene til roboten (ikke beregninger)
# d: data  | "data-objektet" der du får take i variablene dine med punktum notasjon e.g (d.Tid)
# r: robot | inneholder sensorer, motorer og diverse
# _g: "globale" verdier | Du kan lagre initialverdier som kan brukes i mathcalculation
# k: indeks som starter på 0 og øker [0,--> uendelig]
# config: inneholder joystick målinger

def addMeasurements(d,r,_g,k):

	if k==0:        
		# Definer initialverdier for målinger inn i _g variabelen.
		# Da kan du også bruke disse i mathcalculations 
		_g.start_tidspunkt = perf_counter() 			# lagrer første time_stamp
		_g.lys_initial = r.ColorSensor.reflection() 	# lagrer første lysmåling som kan brukes til å beregne Flow
		d.Tid.append(0)
	else:
		# lagrer målinger av tid
		d.Tid.append(perf_counter() - _g.start_tidspunkt)
	
	# lagrer målinger av lys
	d.Lys.append(r.ColorSensor.reflection())
	

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
def MathCalculations(d,_g,k):
	# Parametre
	m = 3  # fir filter konstant
	a = 0.5 # iir-filter konstant

	# Initialverdi for beregnede variabler
	if k == 0:
		d.Flow.append(0)
		d.Euler.append(0)
	else:
		# Beregne tidsskrittet
		d.Ts.append(d.Tid[k]-d.Tid[k-1])

		# Beregn Flow (bruk av initialverdier fra "_g")
		d.Flow.append(d.Lys[k] - _g.lys_initial)

		# Matematiske beregninger: kaller på funksjon fra MineFunksjoner.py
		EulerForward(d.Euler,d.Flow,d.Ts,k)
		"""
		FirFilter(...,m)
		IIRFilter(...,a)
		Num_Derivation(...)
		CalculateMotors(...)
		"""
#__________________________________________________


# Hvis motor(er) brukes i prosjektet så sendes
# beregnet pådrag til motor(ene).
# Motorene oppdateres for hver iterasjon etter mathcalculations
def setMotorPower(d,r):
	return # fjern denne om motor(er) brukes
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
	return # fjern denne om motor(er) brukes
	r.motorA.stop()
	r.motorB.brake()
	r.motorC.hold()
	r.motorD.hold()
#__________________________________________________


# SEKSJON 2: 
# - Skriv målinger og beregninger til "txt" fil
# - Send data fra ROBOT til PC for å plotte live
# - Definer hvilke variabler du vil plotte
# - husk at filename i configs må være et navn større enn ".txt"

# Skriv målinger til fil (LIVE).
def writeMeasToFile(d,r,k):
	streng = EasyWrite(d,k,
		"Tid",
		"Lys",
	)
	r.measurements.write(streng)

# Skriv beregning til fil (LIVE)
def writeCalcToFile(d,r,k):
	streng = EasyWrite(d,k,
		"Tid",
		"Ts",
		"Flow",
		"Euler"
	)
	r.calculations.write(streng)
# --------------------------------------------------------



# Kjører kun på PC-en i offline.
# Leser gjennom filnameMeasurement og henter ut målinger.
# Målingene beregnes og lagres i til fil
def writeOfflineCalc(d, lengde):
	streng = ""
	with open(Configs.filenameCalcOffline, "w") as f:
		for k in range(lengde):
			streng += EasyWrite(d,k,
				"Tid",
				"Ts",
				"Flow",
				"Euler"
			)
		f.write(streng)
#_______________________________________________________________________



# Om du har satt True på runFromPC, livePlot og Online, så får du live målinger fra ROBOTEN til PC
# vil gi litt tregere tidsskritt enn om livePlot = False (som da ikke viser noe plot)
def SendLiveData(data,robot):
	LiveData = packLiveData(data,
		"Tid",
		"Lys",
		"Flow",
		"Ts",
		"Euler"
	)
	#++++++++++++++++++++++ sender over data til PC ++++++++++++++++++++++++++++++++++++++++
	msg = json.dumps(LiveData) # serializing med json tar overraskende lang tid på roboten
	robot.connection.send(bytes(msg, "utf-8") + b"?") # Sender målinger fra Ev3 til PC-en din
	#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


# Dersom nrows og ncols = 1, så har du bare ax.
# Dersom enten nrows = 1 eller ncols = 1, så gis ax 1 argument som ax[0], ax[1], osv.
# Dersom både nrows > 1 og ncols > 1,  så må ax gis 2 argumenter som ax[0,0], ax[1,0], osv
def lagPlot(plt):
	nrows = 2
	ncols = 2
	sharex = False

	plt.create(nrows,ncols,sharex)
	ax = plt.ax

	# TODO: Legg inn titler og aksenavn (optional) på subplotsene dine (eks er under)
	ax[0,0].set_title('Målinger av flow')  
	ax[0,0].set_xlabel("Tid [sek]")
	ax[0,0].set_ylabel("Flow")

	ax[0,1].set_title('Beregning av Euler')
	ax[0,1].set_xlabel("Tid [sek]")
	ax[0,1].set_ylabel("Volum")

	ax[1,0].set_title('Tidsskritt')
	ax[1,0].set_xlabel("Tid [sek]")
	ax[1,0].set_ylabel("tidsskritt")

	
	plt.plot(
		# OBLIGATORISK
		subplot         = ax[0,0],    
		xListName       = "Tid", 	# navn på x-aksen som plottes     
		yListName       = "Flow",	# navn på y-aksen som plottes

		# VALGFRITT
		color           = "b",		# farget på kurven som plottes
		linestyle       = "solid",  # "solid" / "dashed" / "dotted" 
		linewidth       = 1,		# tykkelse på linjen
		marker          = "",       # legg til markør på hvert punkt (anbefales for det meste ikke)

		# VALGFRITT 2: Ekstra argumenter som kan brukes ved valg av plottemetode 2
		xname			= "🕒",	# navn på animerte x-verdien
		yname			= "💡",	# navn på animerte y-verdien
		ycolor			= "k",	# farge på animerte y-verdien
	)

	plt.plot(
		subplot         = ax[0,1],    
		xListName       = "Tid",       
		yListName       = "Euler",
	)


	plt.plot(
		subplot         = ax[1,0],    
		xListName       = "Tid",       
		yListName       = "Ts",
	)
#______________________________________ FERDIG _______________________________________________