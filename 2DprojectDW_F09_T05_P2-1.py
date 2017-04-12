# -*- coding: utf-8 -*-
"""
Created on Sat Apr 01 13:54:13 2017

@authors:
F09 T05
Ang Wei Shan | 1002083 
Cyrus Wang | 1002176
John Chan | 1002056
Wu Jiayue | 1002360
Yang Lujia | 1002204
"""

import os
import glob
import time
import subprocess
import RPi.GPIO as GPIO
from libdw import sm

########## Temperature Reading Function ##########

# Issue the 'modprobe' commands that are needed to start the interface running
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# Find the file from which the messages can be read
baseDir = '/sys/bus/w1/devices/'
deviceFolder = glob.glob(baseDir + '28-000008ab199a')[0]
deviceFile = deviceFolder + '/w1_slave'

# Fetch the two lines of the message from the interface
def readTempRaw():
	catData = subprocess.Popen(['cat',deviceFile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out,err = catData.communicate()
	outDecode = out.decode('utf-8')
	lines = outDecode.split('\n')
	return lines

# Checking for a message with 'YES' on end of the first line
# Returns temperature in Celsius
def readTemp():
    lines = readTempRaw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = readTempRaw()
    equalsPos = lines[1].find('t=')
    if equalsPos != -1:
        tempString = lines[1][equalsPos+2:]
        tempC = float(tempString) / 1000.0
        return tempC

########## GPIO and PWM Setup ##########

# Use the BCM GPIO numbers as the numbering scheme
GPIO.setmode(GPIO.BCM)

# Use GPIO17, GPIO18 and GPIO26 for the motor
motor = [17,18,26]

# Use GPIO5, GPIO6 and GPIO12 for the fan
fan = [5,6,12]

# Set motor and fan GPIOs as output
GPIO.setup(motor, GPIO.OUT)
GPIO.setup(fan, GPIO.OUT)

# Set GPIO26 (for the motor) and GPIO12 (for the fan) as PWM with frequency = 100Hz
pMotor = GPIO.PWM(motor[2],100.0)
pFan = GPIO.PWM(fan[2],100.0)

# Start PWM
pMotor.start(0.0)
pFan.start(0.0)

########## PWM control function ##########

# Changes PWM duty cycle based on the input of a tuple
# Tuple contains (pump power,fan power)
# Values range from 0.0 to 1.0
def pwmAdjust(power):
    pMotor.ChangeDutyCycle(power[0]*100.0)
    pFan.ChangeDutyCycle(power[1]*100.0)

########## State Machine ##########

# Code for the temperature control state machine
# Power output is determined by PD controller
# Proportionality is error between the current and target temperature
# Derivative is change in the error over time
# States are a dictionary containing the errors and times from the last 20 steps
# Values in these lists are averaged for the derivative calculation
# inp is current temperature 
class Controller(sm.SM):
    targetTemp = 27.0 # Change your target temperature here
    errorOne = readTemp() - targetTemp
    timeOne = time.time()
    startState = {'lastErrors' : [errorOne]*20,'lastTimes' : [timeOne]*20,'targetTemp' : targetTemp}
    def getNextValues(self, state, inp):
        kp = 0.7 # Proportionality constant
        kd = 0.4 # Derivative constant
        error = inp - state['targetTemp']
        currentTime = time.time()
        errorDelta = (error - (sum(state['lastErrors'])/20)) / (currentTime - (sum(state['lastTimes'])/20))
        powerOut = kp*error + kd*errorDelta
        newLastErrors = state['lastErrors']
        newLastErrors.insert(0,error)
        newLastErrors.pop(-1)
        newLastTimes = state['lastTimes']
        newLastTimes.insert(0,currentTime)
        newLastTimes.pop(-1)
        print 'The current temperature is {}°C.'.format(str(inp))
        print 'The target temperature is {}°C.'.format(str(state['targetTemp']))
        if powerOut <= 1.0 and powerOut >= 0:
            return ({'lastErrors' : newLastErrors,'lastTimes' : newLastTimes, 'targetTemp' : state['targetTemp']},(powerOut,powerOut))
        elif powerOut < 0:
            return ({'lastErrors' : newLastErrors,'lastTimes' : newLastTimes, 'targetTemp' : state['targetTemp']},(0,0))
        elif powerOut > 1.0:
            return ({'lastErrors' : newLastErrors,'lastTimes' : newLastTimes, 'targetTemp' : state['targetTemp']},(1.0,1.0))

########## Program ##########

# Begin pump operation
GPIO.output(motor[0],True)    
GPIO.output(motor[1],False)

# Start an instance of the Controller state machine
Control = Controller()
Control.start()

# Runs until user interrupts with an input
# Calls function to read temperature
# Moves the state machine to next state
# Uses the output to output a PWM signal
try:
    while True:
        temp = readTemp()
        power = Control.step(temp)
        pwmAdjust(power)
        print 'The current power output is {}%.'.format(str(power))
        time.sleep(0.2) # Adjust frequency of getNextValues in state machine
except KeyboardInterrupt:
    pass

# Stops PWM and cleans up GPIO
pMotor.stop()
pFan.stop()
GPIO.cleanup()
