#!/usr/bin/env pybricks-micropython
# coding=utf-8

# Legger til mappene i søkestien for imports bare når programmet kjører
import os
import sys
import _thread
p_root = os.getcwd() #root of project
sys.path.append(p_root)
sys.path.append(p_root+"/"+"HovedFiler")
sys.path.append(p_root+"/"+"moduler")
#_______________________________________________________


import config
from Main import Configs, d, _g, setPorts, addMeasurements, MathCalculations, writeMeasToFile, writeCalcToFile, SendLiveData, setMotorPower, stopMotors
try:
    from EV3AndJoystick import *
    from pybricks.parameters import Port
    import pybricks.ev3devices as devices
except Exception as e:
    print(e)
    pass  # for å kunne eksportere funksjoner


ProgramEnded = False # boolean flagg for å stoppe programmet fra pc-en
def StopLoop(robot):
    global ProgramEnded
    connection = robot.connection
    while True:
        msg = connection.recv(1024)
        if msg == b"Stop":
            print('received stop signal')
            ProgramEnded = True
            break


# Modify live plot lists to run for a longer time
def limit_measurements(d, k):
    max_values = 1000 # how many values to save on ev3
    if k >= max_values:
        k = max_values-1
        for key in d:
            if len(d[key]) > max_values: # make sure lists are not empty 
                d[key].pop(0) # runs at O(n), but neglishable since n = max_values --> O(1)
    return k
#-----------------------------

def main():
    try:
        robot = Initialize(Configs.runFromPC, Configs.filenameMeas, Configs.filenameCalcOnline)
        setPorts(robot,devices,Port)
        if robot.joystick["in_file"] is not None:
            _thread.start_new_thread(getJoystickValues, [robot]) # make a thread to stop ev3 from joystick
        else:
            print(" --> Joystick er ikke koplet til")
        
        # make a thread to stop the ev3 from the laptop
        if "connection" in robot.__dict__:
            print(' --> setter opp stopp-knapp via PC')
            _thread.start_new_thread(StopLoop, (robot,))  

     
        k = 0
        while True:

            addMeasurements(d,robot,_g,k) # just use k to check if we are at k=0 or k>0

            if len(Configs.filenameMeas)>4:
                writeMeasToFile(d,robot,k)
            
            MathCalculations(d,_g,k)

            if len(Configs.filenameCalcOnline)>4:
                writeCalcToFile(d,robot,k)

            setMotorPower(d,robot)

            # Sender live målinger og plotter
            if Configs.runFromPC and Configs.livePlot:
                SendLiveData(d,robot)
            
            
            # Hvis skyteknappen trykkes inn så skal programmet avsluttes
            if config.joyMainSwitch:
                print("joyMainSwitch er satt til 1")
                break

            # Hvis du trykket stopp-knappen på pc-en
            elif ProgramEnded:
                print("Stopp knappen på PC-en ble trykket")
                break
            k += 1

            # Avoid saving long lists in online mode hogging memory of ev3 and crashing
            if Configs.limitMeasurements:
                k = limit_measurements(d,k) # will make FIR (that has m > limit) inaccurate in online mode


    except Exception as e:
        sys.print_exception(e)
    finally:
        stopMotors(robot)
        CloseJoystickAndEV3(robot, Configs.runFromPC)
        robot.brick.speaker.beep()
        sys.exit()
        


if __name__ == '__main__':
    if Configs.Online:
        main()
    else:
        raise Exception("Kan ikke kjøre robotfilen når du er i offline")