#!/usr/bin/env pybricks-micropython


# Legger til mappene midlertidig i søkestien
import os
import sys
import json
import _thread
from time import perf_counter, sleep
p_root = os.getcwd() #root of project
sys.path.append(p_root)
sys.path.append(p_root+"/"+"HovedFiler")
sys.path.append(p_root+"/"+"moduler")
#_______________________________________________________

from Main import Configs, d, _g, setPorts, addMeasurements, MathCalculations, SendLiveData, setMotorPower, stopMotors, config
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
        robot = Initialize(Configs)
        setPorts(robot,devices,Port)


        # Setter opp joystick eller gui knapp
        if Configs.livePlot:
            stop_type = ""
            if robot.joystick["in_file"] is not None:
                print(' --> setter opp stopp-knapp med joystick')
                stop_type = "joystick"
                robot.connection.send(b"joystick")
                
            elif "connection" in robot.__dict__:
                print(' --> setter opp stopp-knapp via PC')
                stop_type = "gui"
                robot.connection.send(b"gui")
                
            robot.connection.recv(1024)
            if stop_type == "joystick":
                _thread.start_new_thread(getJoystickValues, [robot])
            elif stop_type == "gui":
                _thread.start_new_thread(StopLoop, (robot,))

        #____________________________________________



        if not Configs.livePlot:
            robot.brick.speaker.set_volume(2, which='Beep')
            print("\n___________STATUS_____________")
            print('Running with livePlot = False')
            print('begins in: 3')
            robot.brick.speaker.play_notes(['A3/4'])
            sleep(0.1)
            print('begins in: 2')
            robot.brick.speaker.play_notes(['A3/4'])
            sleep(0.1)
            print('begins in: 1')
            robot.brick.speaker.play_notes(['A3/4'])
            sleep(0.1)
            print('GO!')
            print('______________________________\n')
            robot.brick.speaker.play_notes(['A4/4'])
            robot.brick.speaker.set_volume(50, which='Beep')
        k = 0
        meas = {}

        # check if you have key_inputs
        if Configs.controlRobot:
            inputVars = {}
            for key in d.__dict__:
                if key[-1] == "_":
                    inputVars[key] = key

  
        while True:
            
            # reading inputs from pc
            if Configs.controlRobot:
                d_object = d.__dict__
                try:
                    byteData = robot.inputConnection.recv(1024)
                    splitData = byteData.split(b"?")
                    for data in reversed(splitData):
                        if data != b"" and data != b"{}":
                            rowData = data
                            break
                    data = rowData.decode('utf-8').split(",")
                    temp = {}
                    for key in data:
                        temp[key] = 1
                    for var in inputVars:
                        if var in temp:
                            d_object[var].append(1) # int(inputData[var])
                        else:
                            d_object[var].append(0)  
                
                   
                except Exception as e:
                    for var in inputVars:
                        d_object[var].append(0)
            #______________________
                    
            
            
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
        print("If you wish to run for longer, set limitMeasurements in Configs to True")
        print(e)
        print("___________________________\n",)

    except Exception as e:
        print('encountered unknown error in robot main thread')
        sys.print_exception(e)
    finally:
        stopMotors(robot)
        CloseJoystickAndEV3(robot,Configs)
        robot.brick.speaker.beep()
        sys.exit()
        


if __name__ == '__main__':
    if Configs.Online:
        main()
    else:
        print()
        raise Exception("This file can only be run when Online=True")