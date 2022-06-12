#!/usr/bin/env pybricks-micropython
# coding=utf-8

# Legger til mappene i søkestien for imports bare når programmet kjører
import os
import sys
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), r'HovedFiler'))
sys.path.append(os.path.join(os.getcwd(), r'Moduler'))
#_______________________________________________________


import sys
import _thread
import json
import config
from funksjoner import Bunch
from Main import Configs, d, _G, setPorts, addMeasurements, MathCalculations, writeMeasToFile, writeCalcToFile, SendLiveData, setMotorPower, stopMotors, AnalyzeInput
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
    connection = robot["connection"]
    while True:
        msg = connection.recv(1024)
        if msg == b"Stop":
            print('robot received stop signal')
            ProgramEnded = True
            break

def InputFromPC(robot):
    connection = robot["input_connection"]
    while not ProgramEnded:
        try:
            msg = connection.recv(1024)
            info = json.loads(msg.decode('utf-8'))
            recvData = Bunch(info)
            AnalyzeInput(robot, recvData)
        # cannot decode json string to dictionary
        except Exception as e:
            #print(e,flush=True)
            pass
   

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
        robot = Initialize(Configs.runFromPC, Configs.communicateWithEv3, Configs.filenameMeas, Configs.filenameCalcOnline)
        setPorts(robot,devices,Port)
        if robot.joystick.in_file is not None:
            _thread.start_new_thread(getJoystickValues, [robot]) # make a thread to stop ev3 from joystick
        else:
            print(" --> Joystick er ikke koplet til")
        
        # make a thread to stop the ev3 from the laptop
        if "connection" in robot:
            _thread.start_new_thread(StopLoop, (robot,))  

        # make a thread to communicate with ev3
        if "input_connection" in robot:
            _thread.start_new_thread(InputFromPC, (robot,)) 

        k = 0
        while True:
            addMeasurements(d,robot,_G,k) # just use k to check if we are at k=0 or k>0

            if len(Configs.filenameMeas)>4:
                writeMeasToFile(d,robot,k)
            
            MathCalculations(d,_G,k)

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
        CloseJoystickAndEV3(robot, Configs.runFromPC, Configs.communicateWithEv3)

if __name__ == '__main__':
    if Configs.Online:
        main()
    else:
        raise Exception("Kan ikke kjøre robotfilen når du er i offline")