# coding=utf-8

# Setter opp søkestier og importerer pakker (sjekker om vi er på ev3 eller på pc)
import os
import sys
try:
	sys.path.append(os.getcwd())
	sys.path.append(os.path.join(os.getcwd(), r'HovedFiler'))
	sys.path.append(os.path.join(os.getcwd(), r'Moduler'))
	from plotClass import PlotObject
except AttributeError:
	p_root = os.getcwd() # on ev3
	sys.path.append(p_root)
	sys.path.append(p_root+"/"+"HovedFiler")
	sys.path.append(p_root+"/"+"moduler")
except Exception as e:
	print('unknown error contact Erik')
	print(e)
import json
from time import perf_counter, sleep
from EV3AndJoystick import *
from funksjoner import *
from MineFunksjoner import *
d = Bunch()							
Configs = Bunch()
_G = Bunch()
#_______________________________________________



# SEKSJON 1: KONFIGURASJON, VARIABLER, SENSORER, MÅLINGER og BEREGNINGER

 
#++++++++++++++++++++++++++++++++++++++++++ Konfigurasjoner +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Configs["EV3_IP"] = "169.254.63.42"
Configs["Online"] = True

Configs["filenameMeas"] = "Meas_Euler.txt"
Configs["filenameCalcOnline"] = ".txt" 
Configs["filenameCalcOffline"] = ".txt"  

Configs["runFromPC"] = True	# programmet kjøres fra PC (True) eller fra Ev3-roboten (False)
Configs["livePlot"] = True		# lar deg plotte live. Kan sette false om du ønsker mindre tids-skritt
Configs["plotMethod"] = 2		# (1,2) mulige metoder å plotte på (hver med sine fordeler og ulemper).
Configs["desimaler"] = 5


# For spesielt interesserte
Configs.communicateWithEv3 = False  # mulighet i kreativ del å gi kommandoer fra PC til EV3
Configs.limitMeasurements = False	# mulighet å kjøre programmet lenge uten at roboten kræsjer pga minnet (kommer selvsagt med ulemper)
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


#++++++++++++++++ variabler (lister) for målinger og beregninger ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
d["Tid"] = []            # registring av tidspunkt for målinger
d["Lys"] = []            # måling av reflektert lys fra ColorSensor
d["Flow"] = []           # en berekning som bruker målingen lys og normaliserer dette
d["Ts"] = []             # tidsskritt
d["Euler"] = []   		 # f.eks kan beregninger av euler forward legges inn her (kan gi et annet navn om du vil)


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
# husk at målinger kommer fra roboten og ikke er beregninger
# d: data  | "dictionary" med dine dine lister
# r: robot | inneholder sensorer,motorer, forbindelser og diverse
# _G: globale verdier | Du kan lagre initialverdier fra målinger som tidsskritt og første lysmåling
# k: indeks som starter på 0 og øker [0,-->]
# config: inneholder joystick målinger

def addMeasurements(d,r,_G,k):

	if k==0:        
		# Definer starttidspunkt for eksperimentet
		_G.start_tidspunkt = perf_counter() 			# lagrer tids_stemplet
		_G.lys_initial = r.ColorSensor.reflection() 	# lagrer første lysmåling som kan brukes til å beregne Flow
		d.Tid.append(0)
	else: 
		# For hver ny runde i while-løkka, registrerer 
		d.Tid.append(perf_counter() - _G.start_tidspunkt)
	
	# Legger til lysmålingen i en liste
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
def MathCalculations(d,_G,k):
	# Parametre
	m = 20  # fir filter konstant
	a = 0.5 # iir-filter konstant

	# Initialverdi for beregnede variabler
	if k == 0:
		d.Flow.append(_G.lys_initial)
		d.Euler.append(0)
	else:
		# Beregne tidsskrittet
		d.Ts.append(d.Tid[k]-d.Tid[k-1])

		# Beregn Flow
		d.Flow.append(d.Lys[k]-_G.lys_initial)

		EulerForward(d.Euler,d.Flow,d.Ts,k)


		# Matematiske beregninger: kaller på funksjon fra MineFunksjoner.py
		"""
		FirFilter(...,m)
		IIRFilter(...,a)
		Num_Derivation(...)
		CalculateMotors(...)
		"""
	pass

#__________________________________________________


# Hvis motor(er) brukes i prosjektet så sendes
# beregnet pådrag til motor(ene).
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
# - Skriv målinger og beregninger til "txt" fil inni ROBOTEN (online) eller inni PC i offline modus
# - Send data fra ROBOT til PC for å plotte live
# - Definer hva du vil plotte (både online og offline)



# Skriv målinger til filenameMeas mens roboten kjører.
def writeMeasToFile(d,r,k):
	streng = EasyWrite(d,k,
		"Tid",
		"Lys",
	)
	r.measurements.write(streng)



# Gi navn på filen "filenameCalcOnline" i Configs øverst for å kunne skrive til fil i online modus
# Har du satt ".txt" vil ikke live beregniner bli skrevet til fil
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
# vil være noe tregere pga pakking av data, konverteringer og sending fra EV3 til PC
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
	robot.connection.send(bytes(msg, "utf-b") + b"?") # Sender målinger fra Ev3 til PC-en din
	#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


# Dersom nrows og ncols = 1, så har du bare ax.
# Dersom enten nrows = 1 eller ncols = 1, så gis ax 1 argument som ax[0], ax[1], osv.
# Dersom både nrows > 1 og ncols > 1,  så må ax gis 2 argumenter som ax[0,0], ax[1,0], osv
def lagPlot():
	nrows = 2
	ncols = 2
	sharex = False

	#++++++++Lager objekt fra plottklassen og sender nødvendig data++++
	plt = PlotObject(nrows = nrows, ncols = ncols, sharex = sharex)
	ax = plt.ax
	#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

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


	plt.createlines(
		# REQUIRED
		subplot         = ax[0,0],    
		xListName       = "Tid",       
		yListName       = "Flow",

		# OPTIONAL
		color           = "b",
		linestyle       = "solid",  # "solid" / "dashed" / "dotted" 
		linewidth       = 1,
		marker          = "",       # brukes nesten aldri

		# OPTIONAL2: Ekstra argumenter som kan brukes ved valg av plottemetode 3
		xname			= "",	# navn på animerte x-verdien
		yname			= "",	# navn på animerte y-verdien
		ycolor			= "",	# farge på animerte y-verdien
	)

	plt.createlines(
		subplot         = ax[0,1],    
		xListName       = "Tid",       
		yListName       = "Euler",
	)


	plt.createlines(
		subplot         = ax[1,0],    
		xListName       = "Tid",       
		yListName       = "Ts",
	)

	return plt

	
#______________________________________ FERDIG _______________________________________________



# SEKSJON 3 (for spesielt interesserte):
# Kommunikasjon mellom EV3 og PC
# Legger ikke til muligheter for å lese eller appende fra/til variabelen "d" fordi 
# dette vil føre til race-conditions mellom threads om ressursen "d".

# Send data til roboten fra PC-en
def InputToRobot(sock):

    # kan godt legge til noen funksjoner her før while loopen 


    while True:
        sendData = Bunch()
        # Kan hente data fra tastaturet ditt og legg i en dictionary
        # f.eks kan du bruke tkinter (ligger i standardbiblioteket til python) eller keyboard module (som da krever pip install)
        """ 
        if w is pressed:
        sendData.w = True
        else:
        sendData.w = False
        """
        #++++++Sender kommandoer til roboten+++++++++++++++++
        commands = json.dumps(sendData).encode('utf-8')
        sock.send(commands)
        #+++++++++++++++++++++++++++++++++++++++++++++++++++++

        sleep(0.1) # OBS pass på å ikke ha for lite tidsskritt



# Roboten (r) mottar data (recvData) og du velger hva den skal gjøre med sensorene
def AnalyzeInput(r, recvData):
    # Husk at bare sensorene du spesifiserte i funksjonen setPorts() er tilstede 
    """ 
    r.TouchSensor
    r.UltrasonicSensor
    r.GyroSensor
    r.motorA
    r.motorB
    r.motorC
    r.motorD
    """
    """
    if sendData.get("w"):
        retning = 1
    elif sendData.get("s"):
        retning = -1
    r.motorA.dc(r.Paadrag * retning)
    """
    return