# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 07:30:30 2017

@authors:
F09 T05
Ang Wei Shan | 1002083 
Cyrus Wang | 1002176
John Chan | 1002056
Wu Jiayue | 1002360
Yang Lujia | 1002204
"""
# Begin this simulator first before starting the gui controller

import simpy
import math
import serial


# Opening the serial port to begin communication with the controller
ser = serial.Serial(
        port = 'COM3',
        baudrate = '9600',
        parity = serial.PARITY_NONE,
        stopbits = serial.STOPBITS_ONE,
        bytesize = serial.EIGHTBITS,
        timeout = 0.5
        )


# This class will define all the processes involved in the simulation
class HeatExchanger:
    
    
    # Initialize environment and load processes
    def __init__(self,env):
        # Container representing the heat energy stored in the algae water in joules
        # 40 ml of water initialized at 35 degrees Celsius
        self.heat = simpy.Container(env,init = 51571.984)
        
        # Container representing the heat energy of water in the pump tubes in joules
        # 0.2 m tubing full of water initialized at 25 degrees Celsius
        self.tubeHeat = simpy.Container(env,init = 783.053)
        
        # Container representing the power consumption of the pump over the course of the week
        self.powerConsumption = simpy.Container(env)
        
        # Monitor and heat transfer processes, detailed descriptions at their definitions
        self.writeMonitor = env.process(self.writeMonitor(env))
        self.sunGain = env.process(self.sunGain(env))
        self.wallLoss = env.process(self.wallLoss(env))
        self.pumpLoss = env.process(self.pumpLoss(env))
    
        
    # Monitors key statistics and sends them to the controller via serial communication   
    # Tracks current algae water temperature and current power consumption for the week
    # Time is converted from seconds to weeks:days:hours:minutes:seconds
    # Current time is also sent to the controller
    def writeMonitor(self,env):
        while True:
            systemTemp = (self.heat.level/167.36) - 273.15
            kWhWeek = self.powerConsumption.level * 2.77778e-7
            
            weeks = env.now/604800
            days = (env.now%604800)/86400
            hours = ((env.now%604800)%86400)/3600
            minutes = (((env.now%604800)%86400)%3600)/60
            seconds = (((env.now%604800)%86400)%3600)%60
            time = '{}:{}:{}:{}:{}'.format(weeks,days,hours,minutes,seconds)

            ser.write('{} {} {}'.format(env.now,systemTemp,kWhWeek))
            print 'time {}\npow  {}\ntemp {}'.format(time,kWhWeek,systemTemp)
            yield env.timeout(1)
    
            
    # Process simulating solar irradiance
    # Adds heat to the algae water as a product of exposed surface area and solar irradiance
    # Repeats every second, i.e. 1 W * 1 s = 1 J
    def sunGain(self,env):
        while True:
            yield env.timeout(1)
            
            # Assuming only one large side of the algae bottle facing sun
            surfaceArea = 0.001997
            
            # Formula for solar irradiance as a function of time
            # Simulation starts at 12 midnight
            # Sunrise at 0700 and sunset at 1900 everyday
            # Peak irradiance at 1300 everyday with 1000 W/m^2
            irradiance = 1000 * math.sin(0.00007272205216643 * env.now - 1.832595714594)
            
            # Adds the resultant energy from solar irradiation to the algae heat container
            if irradiance > 0:
                jouleGain = surfaceArea * irradiance
                print 'sun  {}'.format(jouleGain)
                yield self.heat.put(jouleGain)
            else:
                print 'sun  0'
      
                
    # Process simulating loss of heat to surroundings outside of the bottle
    # Repeats every second, i.e. 1 W * 1 s = 1 J
    def wallLoss(self,env):
        while True:
            yield env.timeout(1)
            
            # Derived via Physical World 2D experimental results
            combiThermRes = 7.04225
            
            # Heat loss calculated by finding the temperature difference and dividing the combined thermal resistance
            tempDiff = (self.heat.level/167.36) - 298.15
            jouleLoss = (tempDiff/combiThermRes)
            print 'wall {}'.format(jouleLoss)
            yield self.heat.get(jouleLoss)
    
            
    # Process simulating loss of heat to flowing water from the pump
    # Repeats every second, i.e. 1 W * 1 s = 1 J
    def pumpLoss(self,env):
        while True:
            yield env.timeout(1)
            
            # Reads the pump power data from the controller via serial communication
            try:
                powerPump = float(ser.readline().strip()) * 100.0
                ser.flushInput()
            except ValueError:
                powerPump = 0.0
            print 'inp  {}'.format(powerPump)

            # If the pump is powered, adds to the powerConsumption container
            # 100 % pump power is 5 W of power
            # When the week ends, the powerConsumption container is reset
            if env.now % 604800 == 0:
                self.powerConsumption.get(self.powerConsumption.level)
            else:
                if powerPump > 0:
                    self.powerConsumption.put((5.0/100.0) * powerPump)

            # Calculation for heat transfer correlation for laminar flow in a tube
            # Taken from A.F. Mills, Heat Transfer, Second Edition
            flowVelocity = (0.53/100.0) * powerPump
            reynolds = (1000 * flowVelocity * 0.002)/(8.9 * 10**-4)
            prandtl = 6.04228
            tubeLength = 0.2
            hydrauDia = 0.002
            nusselt = 3.66 + (0.065 * reynolds * prandtl * (hydrauDia/tubeLength))/(1 + 0.04 * (reynolds * prandtl * (hydrauDia/tubeLength))**(2/3))
            flowCoeff = (615.4 * nusselt) / hydrauDia
            
            # If the pump is powered, room temperature water is continuously introduced to the system to replace the heated water
            # Thus, tubeHeat.level loses heat, and thermal resistance is calculated with forced convection
            # However, if the pump is unpowered, the water in the tubes will gain heat from the algae water
            if flowVelocity > 0.2:
                self.tubeHeat.get(self.tubeHeat.level)
                self.tubeHeat.put(783.053)
                combiThermRes = 4.28494 + (1/(flowCoeff * 0.001257))
            elif flowVelocity != 0 and flowVelocity < 0.2:
                displaced = math.pi * (0.001**2) * flowVelocity
                totalVol = math.pi * (0.001**2) * 0.2
                waterHeatDiff = ((displaced/totalVol) * self.tubeHeat.level) - (displaced * 1000 * 298.15 * 4178)
                self.tubeHeat.get(waterHeatDiff)
                combiThermRes = 4.28494 + (1/(flowCoeff * 0.001257))
            else:
                combiThermRes = 5.34434
            
            # Heat transfer between algae water and flowing water is calculated
            # Temperature difference divided by the previously calculated combined thermal resistance
            tempDiff = (self.heat.level/167.36) - (self.tubeHeat.level/2.62637)
            jouleLoss = (tempDiff/combiThermRes)
            print 'pump {}\n'.format(jouleLoss)
            if jouleLoss >= 0:
                yield self.heat.get(jouleLoss)
                yield self.tubeHeat.put(jouleLoss)
            else:
                yield self.heat.put(-jouleLoss)
                yield self.tubeHeat.get(-jouleLoss)

                
# Initiate and run the environment
# Run this script at the same time as the controller
env = simpy.rt.RealtimeEnvironment()
HeatExchanger = HeatExchanger(env)
env.run()
