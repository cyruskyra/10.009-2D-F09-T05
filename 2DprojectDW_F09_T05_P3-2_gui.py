# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 07:19:48 2017

@authors:
F09 T05
Ang Wei Shan | 1002083 
Cyrus Wang | 1002176
John Chan | 1002056
Wu Jiayue | 1002360
Yang Lujia | 1002204
"""
# Begin the simulator before starting the gui controller


import time
import serial

ser = serial.Serial(
        port = '/dev/ttyS0',
        baudrate = '9600',
        parity = serial.PARITY_NONE,
        stopbits = serial.STOPBITS_ONE,
        bytesize = serial.EIGHTBITS,
        timeout = 0.5
        )

from libdw import sm
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager,Screen
from kivy.config import Config
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
import time


Config.set('graphics', 'fullscreen', 'auto')
Config.write()

Builder.load_string("""
<MenuScreen>:
    GridLayout:
        cols: 1
        
        BoxLayout:
            Label:
                canvas.before:
                    Color:
                        rgba: 0, 0, 0, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                text: 'Monitoring'
        
        BoxLayout:
            Label:
                canvas.before:
                    Color:
                        rgba: 0.1, 0.1, 0.1, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                text: 'Time Elapsed'
            Label:
                canvas.before:
                    Color:
                        rgba: 0.1, 0.1, 0.1, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                text: '0 Weeks 0 Days 00 Hours 00 Minutes 00 Seconds'
                id: TimeElapsed
        
        BoxLayout:
            Label:
                canvas.before:
                    Color:
                        rgba: 0, 0, 0, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                text: 'System Temperature (°C)'
            Label:
                canvas.before:
                    Color:
                        rgba: 0, 0, 0, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                text: '35.0'
                id: SystemTemp
        
        BoxLayout:
            Label:
                canvas.before:
                    Color:
                        rgba: 0.1, 0.1, 0.1, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                text: 'Pump Power'
            Label:
                canvas.before:
                    Color:
                        rgba: 0.1, 0.1, 0.1, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                id: PowerPump
        
        BoxLayout:
            Button:
                text: 'Change Settings'
                on_press: root.manager.current = 'settings'
            Button:
                text: 'Power Consumption Overview'
                on_press: root.manager.current = 'power'
            Button:
                text: 'Exit Application'
                on_press: App.get_running_app().stop()

<SettingsScreen>:
    GridLayout:
        cols: 1
        
        BoxLayout:
            Label:
                canvas.before:
                    Color:
                        rgba: 0, 0, 0, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                text: 'Settings'
        
        BoxLayout:
            Label:
                canvas.before:
                    Color:
                        rgba: 0.1, 0.1, 0.1, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                text: 'Set Target Temperature (°C)'
            GridLayout:
                cols: 1
                Label:
                    canvas.before:
                        Color:
                            rgba: 0.1, 0.1, 0.1, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    text: '{}'.format(float(TargetTempSlider.value)) if TargetTempSlider.value else '27.0'
                    id: TargetTemp
                Slider:
                    canvas.before:
                        Color:
                            rgba: 0.1, 0.1, 0.1, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    range: (20.0,35.0)
                    value: 27.0
                    step: 0.1
                    id: TargetTempSlider
                    
        BoxLayout:
            Label:
                canvas.before:
                    Color:
                        rgba: 0, 0, 0, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                text: 'Set Proportionality Constant Kp'
            GridLayout:
                cols: 1
                Label:
                    canvas.before:
                        Color:
                            rgba: 0, 0, 0, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    text: '{}'.format(float(KpSlider.value)) if KpSlider.value else '0.1'
                    id: Kp
                Slider:
                    canvas.before:
                        Color:
                            rgba: 0, 0, 0, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    range: (0.01,1.0)
                    value: 0.7
                    step: 0.01
                    id: KpSlider
        
        BoxLayout:
            Label:
                canvas.before:
                    Color:
                        rgba: 0.1, 0.1, 0.1, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                text: 'Set Derivative Constant Kd'
            GridLayout:
                cols: 1
                Label:
                    canvas.before:
                        Color:
                            rgba: 0.1, 0.1, 0.1, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    text: '{}'.format(float(KdSlider.value)) if KdSlider.value else '0.1'
                    id: Kd
                Slider:
                    canvas.before:
                        Color:
                            rgba: 0.1, 0.1, 0.1, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    range: (0.01,1.0)
                    value: 0.4
                    step: 0.01
                    id: KdSlider
        
        BoxLayout:
            Button:
                text: 'Back to Monitoring'
                on_press: root.manager.current = 'menu'
            Button:
                text: 'Power Consumption Overview'
                on_press: root.manager.current = 'power'
            Button:
                text: 'Exit Application'
                on_press: App.get_running_app().stop()
                
<PowerScreen>:
    GridLayout:
        cols: 1
        
        BoxLayout:
            Label:
                canvas.before:
                    Color:
                        rgba: 0, 0, 0, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                text: 'Power Consumption Overview'
        
        BoxLayout:
            Label:
                canvas.before:
                    Color:
                        rgba: 0.1, 0.1, 0.1, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                text: "This Week's Power Consumption"

            Label:
                canvas.before:
                    Color:
                        rgba: 0.1, 0.1, 0.1, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                text: 'N/A'
                id: PowerConsumption
                    
        BoxLayout:
            Label:
                canvas.before:
                    Color:
                        rgba: 0, 0, 0, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                text: "Past Weeks' Power Consumption"
        
        BoxLayout:
            GridLayout:
                cols: 1
                Label:
                    canvas.before:
                        Color:
                            rgba: 0, 0, 0, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    text: 'Last week'
                Label:
                    canvas.before:
                        Color:
                            rgba: 0, 0, 0, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    text: 'N/A'
                    id: LastWeek
            GridLayout:
                cols: 1
                Label:
                    canvas.before:
                        Color:
                            rgba: 0, 0, 0, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    text: '2 weeks ago'
                Label:
                    canvas.before:
                        Color:
                            rgba: 0, 0, 0, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    text: 'N/A'
                    id: TwoWeek
            GridLayout:
                cols: 1
                Label:
                    canvas.before:
                        Color:
                            rgba: 0, 0, 0, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    text: '3 weeks ago'
                Label:
                    canvas.before:
                        Color:
                            rgba: 0, 0, 0, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    text: 'N/A'
                    id: ThreeWeek
            
        BoxLayout:
            Button:
                text: 'Change Settings'
                on_press: root.manager.current = 'settings'
            Button:
                text: 'Back to Monitoring'
                on_press: root.manager.current = 'menu'
            Button:
                text: 'Exit Application'
                on_press: App.get_running_app().stop()
""")

# Declare screens
class MenuScreen(Screen):
    pass
class SettingsScreen(Screen):
    pass
class PowerScreen(Screen):
    pass

# Code for the temperature control state machine
# Power output is determined by PD controller
# Proportionality is error between the current and target temperature
# Derivative is change in the error over time
# States are a dictionary containing the error and time from the last step
# inp is current temperature 
class Controller(sm.SM):
    timeOne = time.time()
    startState = {'lastErrors' : [3.0]*10, 'lastTimes' : [timeOne]*10}
    def getNextValues(self, state, inp):
        error = inp - self.targetTemp
        currentTime = time.time()
        errorDelta = (error - (sum(state['lastErrors'])/10)) / (currentTime - (sum(state['lastTimes'])/10))
        powerOut = self.kp*error + self.kd*errorDelta
        newLastErrors = state['lastErrors']
        newLastErrors.insert(0,error)
        newLastErrors.pop(-1)
        newLastTimes = state['lastTimes']
        newLastTimes.insert(0,currentTime)
        newLastTimes.pop(-1)
        if powerOut <= 1.0 and powerOut >= 0:
            return ({'lastErrors' : newLastErrors,'lastTimes' : newLastTimes},powerOut)
        elif powerOut < 0:
            return ({'lastErrors' : newLastErrors,'lastTimes' : newLastTimes},0.0)
        elif powerOut > 1.0:
            return ({'lastErrors' : newLastErrors,'lastTimes' : newLastTimes},1.0)

# Code for the GUI application
class SMSimulatorApp(App):

    # This is the build function for the GUI
    # It initializes the screen manager with the screens defined in the buildstring
    # It then starts an instance of the Controller state machine
    # self.updatevalues() is scheduled to run every second
    def build(self):
        sm = ScreenManager()
        self.ms = MenuScreen(name = "menu")
        self.st = SettingsScreen(name = "settings")
        self.ps = PowerScreen(name = "power")
        sm.add_widget(self.ms)
        sm.add_widget(self.st)
        sm.add_widget(self.ps)
        sm.current = "menu"
        self.Control = Controller()
        self.Control.targetTemp = float(self.st.ids.TargetTemp.text)
        self.Control.kp = float(self.st.ids.Kp.text)
        self.Control.kd = float(self.st.ids.Kd.text)
        self.Control.start()
        Clock.schedule_interval(self.updateValues,1)
        return sm

    # This method is used to update the values in the GUI and controller every second 
    # First, three values are read and updated from the simulation via serial communication:
    # The time elapsed, the current system temperature, and the power consumption so far for the week
    # It updates the state machine's variables using the settings in the GUI
    # After running getNextValues, it then updates the GUI with the output power and sends it to the simulator
    def updateValues(self,dt):
        try:
            values = ser.readline().split()
            ser.flushInput()
            self.ms.ids.SystemTemp.text = str(round(float(values[1]),3))
            
            time = int(values[0])
            weeks = time/604800
            days = (time%604800)/86400
            hours = ((time%604800)%86400)/3600
            minutes = (((time%604800)%86400)%3600)/60
            seconds = (((time%604800)%86400)%3600)%60
            self.ms.ids.TimeElapsed.text = '{} Weeks {} Days {} Hours {} Minutes {} Seconds'.format(weeks,days,hours,minutes,seconds)
            
            kWhWeek = float(values[2])
            if kWhWeek != 0.0:
                self.ps.ids.PowerConsumption.text = '{} kWh'.format(values[2])
            else:
                self.ps.ids.ThreeWeek.text = self.ps.ids.TwoWeek.text
                self.ps.ids.TwoWeek.text = self.ps.ids.LastWeek.text
                self.ps.ids.LastWeek.text = self.ps.ids.PowerConsumption.text
                self.ps.ids.PowerConsumption.text = '0.0 kWh'
        except ValueError:
            pass
        
        self.Control.targetTemp = float(self.st.ids.TargetTemp.text)
        self.Control.kp = float(self.st.ids.Kp.text)
        self.Control.kd = float(self.st.ids.Kd.text)
        power = self.Control.step(float(self.ms.ids.SystemTemp.text))
        self.ms.ids.PowerPump.text = str(round(power*100.0,2)) + ' %'
        ser.write('{}'.format(power))
    

    
SMSimulatorApp().run()