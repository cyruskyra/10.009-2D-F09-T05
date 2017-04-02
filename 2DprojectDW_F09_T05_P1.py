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
p = GPIO.PWM(motor[2],100.0)
pTwo = GPIO.PWM(fan[2],100.0)

# Start PWM
p.start(0.0)
pTwo.start(0.0)

########## PWM control function ##########

# Changes PWM duty cycle based on the input of a tuple
# Tuple contains (pump power,fan power)
# Values range from 0.0 to 1.0
def pwmAdjust(power):
    p.ChangeDutyCycle(power[0]*100.0)
    pTwo.ChangeDutyCycle(power[1]*100.0)

########## State Machine ##########

# Set target temperature
desiredTemp = 27.0

# inp is current temperature
# state is last recorded temperature
# If inp above desiredTemp, 100% power for both pump and fan
# If inp below desiredTemp, 0% power
class Controller(sm.SM):
    startstate = readTemp()
    def getNextValues(self, state, inp):
        if inp > desiredTemp:
            return (inp,(1.0,1.0))
        else:
            return (inp,(0.0,0.0))

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
        Temp = readTemp()
        power = Control.step(Temp)
        pwmAdjust(power)
        time.sleep(0.1)
except KeyboardInterrupt:
    pass

# Stops PWM and cleans up GPIO
p.stop()
GPIO.cleanup()
