# -*- coding: utf-8 -*-
"""
Created on Wed Apr 05 20:10:50 2017

@authors:
F09 T05
Ang Wei Shan | 1002083 
Cyrus Wang | 1002176
John Chan | 1002056
Wu Jiayue | 1002360
Yang Lujia | 1002204
"""

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
from kivy.core.image import Image
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
                        rgba: 0.1, 0.1, 0.1, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                Image:
                    source: '2Dgui_temperature.png'
                    size_hint_y: None
                    height: dp(50)
                    center: self.parent.center
            Label:
                canvas.before:
                    Color:
                        rgba: 0.1, 0.1, 0.1, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                text: 'System Temperature'
            Label:
                canvas.before:
                    Color:
                        rgba: 0.1, 0.1, 0.1, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                text: '{} °C'.format(float(SystemTempSlider.value)) if SystemTempSlider.value else '30.0 °C'
                id: SystemTemp
        BoxLayout:
            Slider:
                canvas.before:
                    Color:
                        rgba: 0.1, 0.1, 0.1, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                range: (20.0,40.0)
                value: 30.0
                step: 0.01
                id: SystemTempSlider
        
        BoxLayout:
            Label:
                canvas.before:
                    Color:
                        rgba: 0, 0, 0, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                Image:
                    source: '2Dgui_pump.png'
                    size_hint_y: None
                    height: dp(50)
                    center: self.parent.center
            Label:
                canvas.before:
                    Color:
                        rgba: 0, 0, 0, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                text: 'Pump Power'
            Label:
                canvas.before:
                    Color:
                        rgba: 0, 0, 0, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                id: PowerPump
        
        BoxLayout:
            Label:
                canvas.before:
                    Color:
                        rgba: 0.1, 0.1, 0.1, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                Image:
                    source: '2Dgui_fan.png'
                    size_hint_y: None
                    height: dp(50)
                    center: self.parent.center
            Label:
                canvas.before:
                    Color:
                        rgba: 0.1, 0.1, 0.1, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                text: 'Fan Power'
            Label:
                canvas.before:
                    Color:
                        rgba: 0.1, 0.1, 0.1, 1
                    Rectangle:
                        pos: self.pos
                        size: self.size
                id: PowerFan
        
        BoxLayout:
            Button:
                text: 'Change Settings'
                on_press: root.manager.current = 'settings'
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
                Image:
                    source: '2Dgui_target.png'
                    size_hint_y: None
                    height: dp(50)
                    center: self.parent.center
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
                Image:
                    source: '2Dgui_proportional.png'
                    size_hint_y: None
                    height: dp(50)
                    center: self.parent.center
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
                Image:
                    source: '2Dgui_derivative.png'
                    size_hint_y: None
                    height: dp(50)
                    center: self.parent.center
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
                text: 'Back to Overview'
                on_press: root.manager.current = 'menu'
            Button:
                text: 'Exit Application'
                on_press: App.get_running_app().stop()
""")

# Declare both screens
class MenuScreen(Screen):
    pass
class SettingsScreen(Screen):
    pass

# Code for the temperature control state machine
# Power output is determined by PD controller
# Proportionality is error between the current and target temperature
# Derivative is change in the error over time
# States are dictionaries containing the errors and times from the last 100 steps
# inp is current temperature 
class Controller(sm.SM):
    timeOne = time.time()
    startState = {'lastErrors' : [3.0]*100, 'lastTimes' : [timeOne]*100}
    def getNextValues(self, state, inp):
        error = inp - self.targetTemp
        currentTime = time.time()
        errorDelta = (error - sum(state['lastErrors'])/100) / (currentTime - sum(state['lastTimes'])/100)
        powerOut = self.kp*error + self.kd*errorDelta
        newLastErrors = state['lastErrors']
        newLastErrors.insert(0,error)
        newLastErrors.pop(-1)
        newLastTimes = state['lastTimes']
        newLastTimes.insert(0,currentTime)
        newLastTimes.pop(-1)
        if powerOut <= 1.0 and powerOut >= 0:
            return ({'lastErrors' : newLastErrors,'lastTimes' : newLastTimes},(powerOut,powerOut))
        elif powerOut < 0:
            return ({'lastErrors' : newLastErrors,'lastTimes' : newLastTimes},(0,0))
        elif powerOut > 1.0:
            return ({'lastErrors' : newLastErrors,'lastTimes' : newLastTimes},(1.0,1.0))

# Code for the GUI application
class SMSimulatorApp(App):

    # This is the build function for the GUI
    # It initializes the screen manager with the screens defined in the buildstring
    # It then starts an instance of the Controller state machine
    # self.updatevalues() is scheduled to run every 0.1 seconds
    def build(self):
        sm = ScreenManager()
        self.ms = MenuScreen(name = "menu")
        self.st = SettingsScreen(name = "settings")
        sm.add_widget(self.ms)
        sm.add_widget(self.st)
        sm.current = "menu"
        self.Control = Controller()
        self.Control.targetTemp = float(self.st.ids.TargetTemp.text)
        self.Control.kp = float(self.st.ids.Kp.text)
        self.Control.kd = float(self.st.ids.Kd.text)
        self.Control.start()
        Clock.schedule_interval(self.updateValues,0.1)
        return sm

    # This function runs the Controller state machine through a step
    # It updates the state machine's self variables using the settings in the GUI
    # After running getNextValues, it then updates the GUI with the output power
    def updateValues(self,dt):
        self.Control.targetTemp = float(self.st.ids.TargetTemp.text)
        if self.Control.targetTemp < self.ms.ids.SystemTempSlider.value:
            self.ms.ids.SystemTemp.color = (1,0,0,1)
        else:
            self.ms.ids.SystemTemp.color = (1,1,1,1)
        self.Control.kp = float(self.st.ids.Kp.text)
        self.Control.kd = float(self.st.ids.Kd.text)
        powerTuple = self.Control.step(float(self.ms.ids.SystemTempSlider.value))
        self.ms.ids.PowerPump.text = str(round(powerTuple[0]*100.0,2)) + ' %'
        self.ms.ids.PowerFan.text = str(round(powerTuple[1]*100.0,2)) + ' %'
    

    
SMSimulatorApp().run()