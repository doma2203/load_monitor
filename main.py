#!/usr/bin/env python3
import kivy
kivy.require('1.9.1')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.accordion import Accordion
from kivy.core.text import LabelBase
from kivy.uix.tabbedpanel import TabbedPanel

LabelBase.register('digital-7', 'fonts/digital-7.ttf')

class CurrentStateScreen(BoxLayout):
    pass


class CurrentStateDescription(BoxLayout):
    pass


class StateScreen(GridLayout):
    pass


class MainScreen(GridLayout):
    pass


class StatsScreen(GridLayout):
    pass

class SettingsScreen(GridLayout):
    pass

class MyApp(App):
    def build(self):
        self.title = "Load monitor v. 0.0.2 (przynajmniej wyglada)"
        return MainScreen()


if __name__ == '__main__':
    MyApp().run()
