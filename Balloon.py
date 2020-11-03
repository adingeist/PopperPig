from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.config import Config
import random, math
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button, ButtonBehavior
from kivy.uix.image import Image

def getNewDestination():
    global balloonYDestination, balloonYSpawn, balloonSpawnHeading
    balloonYDestination = random.randint(math.floor(Window.height * 0.2), math.floor(Window.height * 0.7))
    if balloonYSpawn > balloonYDestination:
        balloonSpawnHeading = "down"
    else:
        balloonSpawnHeading = "up"

def moveYTowardDestination():
    global balloonYSpawn
    if balloonSpawnHeading == "up":
        balloonYSpawn += balloonHeight
    else:
        balloonYSpawn -= balloonHeight



class Balloon(Widget):
    position_x = NumericProperty(0)
    position_y = NumericProperty(0)
    myHeight = NumericProperty(0)
    myWidth = NumericProperty(0)

    def __init__(self, **kwargs):
        self.position_x = Window.width
        global balloonYSpawn
        self.position_y = balloonYSpawn
        self.mySource = "Assets/balloon_" + str(random.randint(1, 4)) + ".png"
        self.myHeight = Window.height * 0.0462*1.5
        self.myWidth = (87/103) * self.myHeight
        global balloonWidth, balloonHeight
        balloonWidth = self.myWidth
        balloonHeight = self.myHeight

        # CHECK IF THE BALLOONS SURPASSED THEIR DESTINATION OR DO NOT HAVE A TARGET
        if balloonSpawnHeading == "initialize":
            getNewDestination()
        elif (balloonSpawnHeading == "up") and (balloonYSpawn > balloonYDestination):
            getNewDestination()
        elif (balloonSpawnHeading == "down") and (balloonYSpawn < balloonYDestination):
            getNewDestination()
        else:
            moveYTowardDestination()
        self.position_y = balloonYSpawn
        # Move the balloon
        Clock.schedule_interval(self.move_balloon, 1/60.)
        super().__init__(**kwargs)
    def move_balloon(self, time_passed):
        myParent = None
        if self.position_x < -self.myWidth:
            if self.parent is not None:
                myParent = self.parent
            if myParent is not None:
                myParent.remove_widget(self)
        global balloonSpeed
        self.position_x -= balloonSpeed
