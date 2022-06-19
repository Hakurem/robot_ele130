#!/usr/bin/env pybricks-micropython
# coding=utf-8

# Legger til mappene i søkestien midlertidig for imports bare når programmet kjører
import os
import sys
import _thread
from time import sleep
p_root = os.getcwd() #root of project
sys.path.append(p_root)
sys.path.append(p_root+"/"+"HovedFiler")
sys.path.append(p_root+"/"+"moduler")
#_______________________________________________________

import config
from Main import Configs, d, _g, setPorts, addMeasurements, MathCalculations, SendLiveData, setMotorPower, stopMotors
from funksjoner import writeToFile
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
        g_map = d.__dict__
        for key in g_map:
            if len(g_map[key]) > max_values: # make sure lists are not empty
                g_map[key].pop(0) # runs at O(n), but neglishable since n = max_values --> O(1)
    return k
#-----------------------------

def main():
    try:
        robot = Initialize(Configs.filename)
        setPorts(robot,devices,Port)

        # initialize plot before starting main loop
        # we wish to visualize everything from the start
        while True:
            msg = robot.connection.recv(1024)
            print(msg)
            if msg == b"Done_Initializing_Plot":
                sleep(0.5)
                break
        #____________________________________________

        # make a thread to stop ev3 from joystick
        if robot.joystick["in_file"] is not None:
            _thread.start_new_thread(getJoystickValues, [robot]) 
        else:
            print(" --> Joystick er ikke koplet til")
        
        # make a thread to stop the ev3 from the laptop
        if "connection" in robot.__dict__:
            print(' --> setter opp stopp-knapp via PC')
            _thread.start_new_thread(StopLoop, (robot,))  

     
        

        k = 0
        meas = {}
        while True:
            addMeasurements(d,robot,_g,k) # just use k to check if we are at k=0 or k>0

            # figure out which values are measurements and mark them in the txt_file
            if k == 0:
                d_map = d.__dict__
                for key in d_map:
                    if len(d_map[key]) > 0:
                        meas[key] = key
            #________________________________________________________________________    
                    
            MathCalculations(d,k,_g)
            if len(Configs.filename)>4:
                streng = writeToFile(d,k,meas,_g)
                robot.dataToFile.write(streng)

            setMotorPower(d,robot)

            # Sender live målinger og plotter
            if Configs.livePlot:
                SendLiveData(d,robot)
            
            
            # Hvis skyteknappen trykkes inn så skal programmet avsluttes
            if config.joyMainSwitch:
                print("joyMainSwitch er satt til 1")
                break

            # Hvis du trykket stopp-knappen på pc-en
            elif ProgramEnded:
                print("Stopp knappen på PC-en ble trykket")
                break
            

            # Avoid saving long lists in online mode hogging memory of ev3 and crashing
            if Configs.limitMeasurements:
                k = limit_measurements(d,k) # will make FIR (that has m > limit) inaccurate in online mode

            k += 1

    except MemoryError as e:
        print("\n___Status for minnebruk__")
        print("Det er fullt minne fordi variablene/listene dine ble for lange")
        print("Om du ønsker å kjøre lenger, vurder å sette limitMeasurements i Configs til True")
        print(e)
        print("___________________________\n",)

    except Exception as e:
        sys.print_exception(e)
    finally:
        stopMotors(robot)
        CloseJoystickAndEV3(robot)
        #robot.brick.speaker.beep()
        sys.exit()
        


if __name__ == '__main__':
    if Configs.Online:
        main()
    else:
        raise Exception("Kan ikke kjøre robotfilen når du er i offline.")