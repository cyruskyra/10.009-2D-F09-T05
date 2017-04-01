# -*- coding: utf-8 -*-
"""
Created on Sat Apr 01 13:54:13 2017

@author: Kyra
"""

import os
import glob
import time
import subprocess
import RPi.GPIO as GPIO
from libdw import sm

########## Temperature Sensor Setup ##########

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

########## GPIO Setup ##########

# Use the BCM GPIO numbers as the numbering scheme
GPIO.setmode(GPIO.BCM)

# Use GPIO17, GPIO18 and GPIO26 for the motor
motor = [17,18,26]

# Set GPIO17, GPIO18 and GPIO26 as output
GPIO.setup(motor, GPIO.OUT)

# Set GPIO26 as PWM with frequency = 100Hz
p = GPIO.PWM(motor[2],100)

# Start PWM
p.start(0)

########## State Machine ##########

# Set target temperature
desiredTemp = 20.0

# inp is current temperature
# state is last recorded temperature
# If inp above desiredTemp, 100% power
# If inp below desiredTemp, 0% power
class Controller(sm.SM):
    startstate = readTemp()
    def getNextValues(self, state, inp):
        if inp > desiredTemp:
            return (readTemp(),1.0)
        else:
            return (readTemp(),0.0)

# Begin pump operation
GPIO.output(motor[0],True)    
GPIO.output(motor[1],False)

# Start an instance of the Controller state machine
Control = Controller()
Control.start()

# Run state machine until user interrupts with an input
try:
    while True:
        Temp = readTemp()
        print Temp
        p.ChangeDutyCycle(Control.step(Temp)*100)
        time.sleep(0.1)
except KeyboardInterrupt:
    pass

# Stops PWM and cleans up GPIO
p.stop()
GPIO.cleanup()