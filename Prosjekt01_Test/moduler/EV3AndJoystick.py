#!/usr/bin/env pybricks-micropython
# coding=utf-8

# Legger til mappene i søkestien for imports bare når programmet kjører
import os
import sys
p_root = os.getcwd() #root of project
sys.path.append(p_root)
sys.path.append(p_root+"/"+"HovedFiler")
sys.path.append(p_root+"/"+"moduler")
#_______________________________________________________
from pybricks.hubs import EV3Brick
from funksjoner import Bunch
import socket
import struct
import uselect
import config


def Initialize(filename):
    

    # robot inneholder all info om roboten
    robot = Bunch()
    ev3 = EV3Brick()
    robot.brick = ev3

    # joystick inneholder all info om joysticken.
    robot.joystick = infoJoystick()
    
    
    # Sett opp socketobjektet, og hør etter for "connection"
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    robot.sock = sock
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", 8070))
    sock.listen(1)

    # Gi et pip fra robotten samt print i terminal
    # for å vise at den er klar for socketkobling fra PC
    print("Waiting for connection from computer.")
    #ev3.speaker.beep()

    # Motta koblingen og send tilbake "acknowledgment" som byte
    connection, _ = sock.accept()
    connection.send(b"ack")
    print("Acknowlegment sent to computer.")
    robot.connection = connection

    # Fila hvor alle dataene dine lagres
    robot.dataToFile = open(filename, "w")
    return robot



def identifyJoystick():
    """
    Identifiserer hvilken styrestikk som er koblet til;
    enten logitech eller dacota (eventuelt en annen styrestikk)
    Denne funksjonen skal ikke endres.
    """

    for i in range(2, 1000):
        path = ("/dev/bus/usb/001/{:03d}".format(i))
        try:
            with open(path, "rb") as f:
                joy = f.read()
                if joy[2] == 16:
                    return "logitech"
                elif joy[2] == 0:
                    return "dacota"
                else:
                    return "Ukjent styrestikk."
        except:
            # print("Feil i identifyJoystick!")
            pass



def infoJoystick():
    """
    Fyller ut og returnerer en "joystick"-dictionary som inneholder all info om styrestikk.
    Nøkler i dictionaryen er som følger:
    "id" - retur fra identifyJoystick()
    "scale" - skaleringsverdi, avhengig av hvilken styrestikk som brukes
    "FORMAT" - long int x2, unsigned short x2, unsigned int
    "EVENT_SIZE" - struct.calcsize av "FORMAT"
    "in_file" - hvor bevegelsene til styrestikken lagres på EV3en
    """

    joystick = {}
    joystick["id"] = identifyJoystick()
    joyScale = 0
    if joystick["id"] == "logitech":
        joyScale = 1024
    elif joystick["id"] == "dacota":
        joyScale = 255
    joystick["scale"] = joyScale
    joystick["FORMAT"] = 'llHHI'
    joystick["EVENT_SIZE"] = struct.calcsize(joystick["FORMAT"])
    try:
        joystick["in_file"] = open("/dev/input/event2", "rb")
    except OSError:  # hvis ingen joystick er koblet til
        joystick["in_file"] = None
    return joystick



def getJoystickValues(robot):
    
    # https://docs.micropython.org/en/v1.9.3/pyboard/library/uselect.html

    event_poll = uselect.poll()
    if robot.joystick["in_file"] is not None:
        event_poll.register(robot.joystick["in_file"], uselect.POLLIN)
    else:
        return
    while True:
        events = event_poll.poll(0)
        if len(events) > 0 and events[0][1] & uselect.POLLIN:
            try:
                (_, _, ev_type, code, value) = struct.unpack(
                    robot.joystick["FORMAT"],
                    robot.joystick["in_file"].read(
                        robot.joystick["EVENT_SIZE"]))
            except Exception as e:
                print(e)
            if ev_type == 1:
                if value == 0:
                    #print("ev_type: " + str(ev_type) + ". code: " + str(code) + ". value: " + str(value) + ".")
                    config.knappSlippInstance = True
                # når en knapp slippes (etter knappetrykk) gis det ut en ny 
                # hendelse med "ev_type" og "code" helt lik knappetrykket, 
                # bare med "value" lik 0 (istedenfor 1 for knappetrykket)
                #print("ev_type: " + str(ev_type) + ". code: " + str(code) + ". value: " + str(value) + ".")
                if code == 288:
                    print("Joystick signal received, stopping program.")
                    config.joy1Instance = True
                    config.joyMainSwitch = True
                elif code == 289:
                    config.joy2Instance = True
                elif code == 290:
                    config.joy3Instance = True
                elif code == 291:
                    config.joy4Instance = True
                elif code == 292:
                    config.joy5Instance = True
                elif code == 293:
                    config.joy6Instance = True
                elif code == 294:
                    config.joy7Instance = True
                elif code == 295:
                    config.joy8Instance = True  
                elif code == 296:
                    config.joy9Instance = True
                elif code == 297:
                    config.joy10Instance = True
                elif code == 298:
                    config.joy11Instance = True
                elif code == 299:
                    config.joy12Instance = True
                else:
                    # indikasjon på at jeg har glemt å ta med en knapp; legg til i koden
                    print("--------------------------------------")
                    print("Unknown code!")
                    print("ev_type: " + str(ev_type) + ". code: " + str(code) + ". value: " + str(value) + ".")
                    print("--------------------------------------")

            elif ev_type == 3:
                # all dacota-relatert informasjon (kode 2 og kode 5 for dacota) er usikkert, test?
                if code == 0:
                    config.joySideInstance = scale(
                        value,
                        (robot.joystick["scale"], 0),
                        (100, -100))
                elif code == 1:
                    config.joyForwardInstance = scale(
                        value,
                        (0, robot.joystick["scale"]),
                        (100, -100))
                elif code == 2 and robot.joystick["id"] == "dacota":
                    #POTENSIOMETER - dacota - USIKKERT
                    config.joyPotMeterInstance = scale(
                        value,
                        (255, 0),
                        (-100, +100))
                elif code == 5:
                    #TORSION - dacota og logitech
                    config.joyTorsionInstance = scale(
                        value,
                        (255, 0),
                        (+100, -100))
                elif code == 6 and robot.joystick["id"] == "logitech":
                    #POTENSIOMETER - logitech
                    config.joyPotMeterInstance = scale(
                        value,
                        (255, 0),
                        (-100, +100))
                # kode 16 og 17 indikerer bevegelse på POV/hat switch
                # se https://en.wikipedia.org/wiki/Joystick#/media/File:Joyopis.svg
                elif code == 16 and robot.joystick["id"] == "logitech":
                    # POV/hat switch - hoyre - venstre, 1 - 4294967295
                    config.joyPOVSideInstance = scale(
                        value,
                        (4294967295, 1),
                        (-1, +1))
                elif code == 17 and robot.joystick["id"] == "logitech":
                    # POW/hat switch - ned - opp, 1 - 4294967295
                    config.joyPOVForwardInstance = scale(
                        value,
                        (1, 4294967295),
                        (-1, +1))



def CloseJoystickAndEV3(robot):  
    if  robot.joystick["in_file"] != None:
        robot.joystick["in_file"].close()
   
    
    robot.dataToFile.close()

    robot.connection.send(b"end")
    robot.connection.close()
    robot.sock.close()




def scale(value, src, dst):
    return ((float(value - src[0])
            / (src[1] - src[0])) * (dst[1] - dst[0])
            + dst[0])