# this project uses the kivy package. Here is the link to download it: https://kivy.org/#download
# Kivy allows python to create an intractable user interface. I like to think of python as javascript while kivy
# acts as css. Kivy also allows this project to be exported to files compatible with iOS and android, which would not
# be possible since they require Swift and Java, respectively.

# import the math and random packages
import math
import random

# import App, Window, Clock, SoundLoader, JsonStore, NumericProperty, ObjectProperty, StringProperty, Button,
# FloatLayout, Image, Label, and Widget from kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.storage.jsonstore import JsonStore
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
# import Config from kivy (recommended for testing app in a desired screen size)
# used for testing: from kivy.config import Config

# GLOBAL VARIABLES
# creates a json file named 'popper_pig.json' in the device's local memory and can be referenced by code with the
# variable store
store = JsonStore('popper_pig.json')
# balloonSpeed tells the balloons how many pixels it should move per frame
balloonSpeed = 5
# the amount of pixels balloons are vertically spaced apart
balloonIncline = 0
# balloons travel toward a y destination set by the balloon spawner. Once a balloon reaches the y destination
# a new random destination is selected. This creates a wave of balloons always heading to a destination.
# Tells the balloon spawner if the balloon should head "down", "up", or "initialize" the spawner with a starting
# direction
balloonSpawnHeading = "initialize"
# the y coordinate the wave of balloons move to
balloonYDestination = 0
# keeps record of the last the y position of the last balloon spawned
balloonYSpawn = 0
# height of balloons
balloonHeight = 0
# width of balloons
balloonWidth = 0
# distance since the last balloon spawned. Allows for spacing between balloon spawns.
distSinceLastSpawn = 0
# x and y positions of the pig (player)
pigX = 0
pigY = 0
# height of the pig
pigHeight = 0
# pops the player accumulates during gameplay by colliding the pig with the balloons
popCount = 0
# best pop count ever achieved in a single game. This value is set from the 'popper_pig.json' file
bestPopCount = 0
# amount of balloons missed during gameplay. Raised by balloons moving off the left side of the screen.
missCount = 0
# number of misses allowed. Once misses reaches this allowance the game ends.
missesAllowed = 10
# tells the game if the user clicked out of the main menu and can start the gameplay action
gameStage = "menu"


# STEP 3: Create classes that build objects within the game
# inherits the background as a Widget. See the corresponding main.kv file.
class Background(Widget):
    # the background does nothing so this class is passed. However, kivy still requires the structure of a widget
    # so this class is still necessary.
    pass


# structures a FloatLayout layer that is spawned above the background. The clouds are spawned in this layout to ensure
# the clouds spawn behind important objects such as the pig and balloons
class CloudLayout(FloatLayout):
    # initialize the CloudLayout with the parameters defined by the parent FloatLayout class. **kwargs allows for kivy
    # to pass an undefined number of arguments
    def __init__(self, **kwargs):
        # enables access to properties and methods to its parent class
        super(CloudLayout, self).__init__(**kwargs)
        # starts a clock the spawns a cloud every 2 seconds
        Clock.schedule_interval(self.spawn_cloud, 2.)

    # method that spawns a cloud. time_passed is a required parameter that is always passed by kivy in any Clock
    def spawn_cloud(self, time_passed):
        # creates a cloud object
        cloud = Cloud()
        # adds the cloud object to the CloudLayout canvas
        self.add_widget(cloud)


# structures a Widget as clouds. See the corresponding cloud.kv file.
class Cloud(Widget):
    # defaults width, height, x, and y attributes to 0 with the type NumericProperty. Attributes that are referenced in
    # .kv files must be NumericProperty or StringProperty type to be recognized
    myWidth = NumericProperty(0)
    myHeight = NumericProperty(0)
    position_x = NumericProperty(0)
    position_y = NumericProperty(0)
    # defaults the base cloud movement speed to 0
    moveSpeed = NumericProperty(0)
    # defaults the cloud's image source to a blank file. StringProperty tells .kv that the attribute is a string that
    # is updated with python code
    mySource = StringProperty("")

    # all new Cloud objects are initialized with the following:
    def __init__(self, **kwargs):
        # enables access to properties and methods to its parent class
        super(Cloud, self).__init__(**kwargs)
        # enables access to the global variable, balloonSpeed
        global balloonSpeed
        # randomly sets the cloud's height between 10-50% of the screen height
        self.myHeight = Window.height * random.randint(10, 50) / 100  # .01 0.5 very small to half the screen
        # preserves the height and width ratio of the original cloud_1.ong file. cloud_2.png has similar dimension that
        # it can be set to the same ratio as cloud_1.png
        self.myWidth = self.myHeight * (690 / 343)
        # the position at the bottom-left of a widget is (0,0). Spawns the cloud off the right side of the screen.
        self.position_x = Window.width
        # sets a random y position between off the bottom of the screen to off the top of the screen
        self.position_y = random.randint(int(-self.myHeight), int(Window.height))
        # sets the base movement speed of the clouds to and random number between 10% and 150% the of initial balloon
        # speed. This number does not accelerate with the game.
        self.moveSpeed = random.randint(int((balloonWidth / 48.467) * 1), int((balloonWidth / 48.467) * 7.5))
        # randomly sets the image of the cloud to 1 of 4 cloud images
        self.mySource = "Assets/cloud_" + str(random.randint(1, 4)) + ".png"
        # randomly sets opacity of the cloud between 1% and 50%
        self.opacity = random.randint(1, 50) / 100
        # starts a personal clock that moves the cloud 60 frames per second
        Clock.schedule_interval(self.move_cloud, 1 / 60.)

    # method executed 60fps to move the cloud widget
    def move_cloud(self, time_passed):
        global balloonSpeed
        # moves the cloud left the amount the balloons are moving plus the default movement speed of the cloud
        self.position_x -= (balloonSpeed + self.moveSpeed)
        # if the cloud is off the left of the screen
        if self.position_x <= -self.myWidth:
            # stop running the clock. Clocks are demanding to the computer and becomes very laggy if clocks continue
            # to run.
            Clock.unschedule(self.move_cloud)
            # remove the cloud off the screen
            self.parent.remove_widget(self)
            # delete this object from memory
            del self


# structures a widget as the tutorial image showing the user how to raise the pig. Additionally, this object is used
# to start the game action. See taptostart.kv
class TapToStart(Widget):
    # define and default to 0 the attributes that are used in this class's .kv file
    myWidth = NumericProperty(0)
    myHeight = NumericProperty(0)
    position_x = NumericProperty(0)
    position_y = NumericProperty(0)

    # all new TapToStart objects are initialized with the following:
    def __init__(self, **kwargs):
        # enables access to properties and methods of the parent class
        super(TapToStart, self).__init__(**kwargs)
        # sets the height of the image to half of the screen height
        self.myHeight = Window.height * 0.5
        # makes the image a square by setting it to the same width as the height
        self.myWidth = self.myHeight
        # centers the object in the middle of the screen
        self.position_x = Window.width / 2 - self.myWidth / 2
        self.position_y = Window.height / 2 - self.myHeight / 2

    # When the screen is touched anywhere: resets game if game was played before. Sets up variables if first game.
    def on_touch_down(self, touch):
        # give access to modify the following global variables:
        global gameStage, balloonSpeed, popCount, missCount, missesAllowed, distSinceLastSpawn, balloonSpawnHeading
        # reset the balloons to move 5px 60fps. This portion -> (balloonWidth / 48.467) <- equals 1 in the testing
        # environment and changes proportional to the size of the reformatted game window. This lets the game play
        # the same on numerous devices. This tactic is used frequently throughout all code below.
        balloonSpeed = 5 * (balloonWidth / 48.467)
        # reset global variables
        popCount = 0
        missCount = 0
        missesAllowed = 10
        distSinceLastSpawn = 0
        # start spawning using the method ask_balloon_spawner
        Clock.schedule_interval(self.parent.ask_balloon_spawner, 1 / 60.)
        # allow for the destination to be randomly chosen when the game starts
        balloonSpawnHeading = "initialize"
        # set the gameStage to be in game
        gameStage = "inGame"
        # remove this object from the parent widget
        self.parent.remove_widget(self)
        # delete this object from memory
        del self


# This is the main character. It is a widget that corresponds to the pig.kv file.
class Pig(Widget):
    # define and default to 0 the attributes that are used in this class's .kv file
    myHeight = NumericProperty(0)
    myWidth = NumericProperty(0)
    position_x = NumericProperty(0)
    position_y = NumericProperty(0)
    # how fast the pig moves. Positive velocity = up. Negative = down.
    velocity = NumericProperty(0)

    # all new pig objects are initialized with the following:
    def __init__(self, **kwargs):
        # sets the height of the pig to be 10.38% of the screen's height. This multiplier was obtained by drawing out
        # the desired final product in photoshop and calculating how much the pig took up of the screen's height.
        self.myHeight = Window.height * 0.1038
        # access global variables
        global pigHeight, pigX, pigY
        # set the global variable pig height to the pig's height. This lets other objects access the pig's height.
        pigHeight = self.myHeight
        # ensures the width and height of the pig maintain the same ratio as the pig.png file
        self.myWidth = (234 / 171) * self.myHeight
        # places the left side of the pig half of a pig's width from the left side of the screen
        self.position_x = self.myWidth / 2
        # tells the rest of the game where the pig's x position is
        pigX = self.position_x
        # sets the starting y position of the pig to the middle
        self.position_y = Window.height / 2
        # tells the rest of the game where the pig's y position is
        pigY = self.position_y
        # enables access to properties and methods of the parent class
        super().__init__(**kwargs)

    # runs 60fps if touch is up. Lowers the velocity of the pig.
    def accelerate_down(self, time_passed):
        # gain access to global variables
        global balloonSpeed, gameStage, balloonHeight, pigY
        # if balloonSpeed is 0. (flooring balloonSpeed is required because extra frames could be run in clocks making
        # balloonSpeed actually 0.002ish.
        if math.floor(balloonSpeed) == 0:
            # game must be over. Call the destroy pig method.
            self.destroy_pig()
        # Pig was not destroyed. Two things impact pig's ability to accelerate: balloonSpeed and screenSize. The first
        # part of the max function subtracts 0.262 at the starting game speed of 5. As the game speeds up, the ability
        # for the pig to accelerate increases proportionally, allowing for the same game to be played a faster speed.
        # The second part of the max function acts as a cap to how fast the pig can accelerate, otherwise the pig will
        # shoot to the center of the earth.
        self.velocity = max(self.velocity - (balloonSpeed / 5) * 0.262,
                            (balloonSpeed / 5) * -10)
        # now that the new velocity is calculated, add the velocity to y. Velocity can be positive or negative
        # depending on how far one way the pig was moving.
        self.position_y += self.velocity
        # update the global variable pigY
        pigY = self.position_y

    # runs 60fps if touch is down. Raises the velocity of the pig.
    def accelerate_up(self, time_passed):
        # gain access to global variables
        global balloonSpeed, gameStage, pigY
        # if balloonSpeed is 0. (flooring balloonSpeed is required because extra frames could be run in clocks making
        # balloonSpeed actually 0.002ish.
        if math.floor(balloonSpeed) == 0:
            # game must be over. Call the destroy pig method.
            self.destroy_pig()
        # Pig was not destroyed. Two things impact pig's ability to accelerate: balloonSpeed and screenSize. The first
        # part of the max function adds 0.262 at the starting game speed of 5. As the game speeds up, the ability
        # for the pig to accelerate increases proportionally, allowing for the same game to be played a faster speed.
        # The second part of the max function acts as a cap to how fast the pig can accelerate, otherwise the pig will
        # shoot to the moon.
        self.velocity = min(self.velocity + (balloonSpeed / 5) * 0.262, (balloonSpeed / 5) * 10)
        # now that the new velocity is calculated, add the velocity to y. Velocity can be positive or negative
        # depending on how far one way the pig was moving.
        self.position_y += self.velocity
        # update the global variable pigY
        pigY = self.position_y

    # method that always listens for a touch to be down and executes once a touch is placed anywhere on screen
    def on_touch_down(self, touch):
        # if the game is not over
        if math.floor(balloonSpeed) != 0:
            # stop the clock causing the pig to accelerate down
            Clock.unschedule(self.accelerate_down)
            # start the clock that causes the pig to accelerate up
            Clock.schedule_interval(self.accelerate_up, 1 / 60)

    # method that always listens for a touch to be released and executes upon release
    def on_touch_up(self, touch):
        # if the game is not over
        if math.floor(balloonSpeed) != 0:
            # stop the clock that causes the pig to accelerate up
            Clock.unschedule(self.accelerate_up)
            # start the clock that causes the pig to accelerate down
            Clock.schedule_interval(self.accelerate_down, 1 / 60)

    # destroys the pig when the game is over
    def destroy_pig(self):
        # stop accelerating clocks if they're running
        Clock.unschedule(self.accelerate_down)
        Clock.unschedule(self.accelerate_up)
        # remove the pig from the parent layout
        self.parent.remove_widget(self)
        # delete the pig object from memory
        del self


# constructs balloons that can be popped by the main character. It is a widget that corresponds to the balloon.kv file
class Balloon(Widget):
    # defaults attributes to 0 or an empty string that are referenced by balloon.kv
    position_x = NumericProperty(0)
    position_y = NumericProperty(0)
    myHeight = NumericProperty(0)
    myWidth = NumericProperty(0)
    mySource = StringProperty("")

    # initialize balloon objects
    def __init__(self, **kwargs):
        # global variables used in this method
        global balloonYSpawn, balloonWidth, balloonHeight
        # set their x position to be off the screen on the right
        self.position_x = Window.width
        # sets y position to the global variable balloonYSpawn
        self.position_y = balloonYSpawn
        # makes balloon 1 of 4 colors
        self.mySource = "Assets/balloon_" + str(random.randint(1, 4)) + ".png"
        # sets width and height based on already calculated values
        self.myWidth = balloonWidth
        self.myHeight = balloonHeight
        # check if the balloons surpassed their destination or do not have a target
        if balloonSpawnHeading == "initialize":
            # not yet defined a direction where their destination is so get a new destination
            self.get_new_destination()
        elif (balloonSpawnHeading == "up") and (balloonYSpawn > balloonYDestination):
            # balloon surpassed destination going up so get a new destination
            self.get_new_destination()
        elif (balloonSpawnHeading == "down") and (balloonYSpawn < balloonYDestination):
            # balloon surpassed destination going down so get a new target
            self.get_new_destination()
        else:
            # balloon did not surpass a destination so move the balloon Y toward the destination
            self.move_y_toward_destination()
        # set the y position of the balloon to be accessed globally
        self.position_y = balloonYSpawn
        # start clock to move the balloon 60fps.
        Clock.schedule_interval(self.move_balloon, 1 / 60.)
        # enable access to properties and methods of the parent class
        super().__init__(**kwargs)

    # method ran 60fps that moves the balloon
    def move_balloon(self, time_passed):
        global balloonSpeed
        # is the game over?
        if math.floor(balloonSpeed) == 0:
            # clear the balloon from the screen without a pop effect
            Clock.schedule_once(self.destroy_without_pop, 0.5)
        # is this balloon visible?
        if self.position_x < -self.myWidth:
            # This is how only balloon objects must reference their parent since the self.parent method flipped back to
            # referencing None rather than the actual parent FloatLayout from main.kv
            # define a variable set to be blank
            my_parent = None
            # if the parent is not none
            if self.parent is not None:
                # set the parent variable to it
                my_parent = self.parent
            # if the parent variable is not none
            if my_parent is not None:
                # This balloon was missed. Add it to the misses.
                global missCount
                missCount += 1
                # load the pop sound
                sound = SoundLoader.load("Audio/miss.wav")
                # the sound shouldn't play on a loop
                sound.loop = False
                # play the sound full volume
                sound.volume = 1
                # play the sound through the device
                sound.play()
                # stop the clock responsible for moving the balloon
                Clock.unschedule(self.move_balloon)
                # remove the balloon from the screen
                my_parent.remove_widget(self)
                # remove the balloon object from memory
                del self
        # balloon is not off the screen
        else:
            # move the balloon left
            self.position_x -= balloonSpeed
            # check if the balloon is popped by the pig
            self.check_balloon_pop()

    # checks if the balloon collided with the pig
    def check_balloon_pop(self):
        # global variables used in this method
        global pigX, pigHeight, balloonSpeed, popCount
        # is the balloon within the left and right bounds of the pig Widget?
        if (self.position_x <= (pigX + (234 / 171) * pigHeight)) and (self.position_x >= 0):
            # is the balloon within the top and bottom bounds of the pig Widget?
            if (pigY / 1.1 <= self.position_y <= pigY + pigHeight) * 1.1:
                # speed up the game. Multiplying by balloonWidth ensures the game accelerates proportionally to device
                # size
                balloonSpeed += balloonWidth * .00025
                # load the pop sound
                sound = SoundLoader.load("Audio/pop2.wav")
                # don't loop the sound
                sound.loop = False
                # add a variety to popping noises by making the pitch a random level between .8 and 2. The default
                # pitch is 1.
                sound.pitch = random.randint(8, 20) / 10
                # set the volume of the sound
                sound.volume = 1
                # play the sound through the device
                sound.play()
                # add 1 to the pop count
                popCount += 1
                # remove the balloon with the following steps. Set the parent variable to none.
                my_parent = None
                # if the parent isn't none
                if self.parent is not None:
                    # set the variable to the parent
                    my_parent = self.parent
                # if the parent isn't none
                if my_parent is not None:
                    # stop the clock responisble for moving the balloon
                    Clock.unschedule(self.move_balloon)
                    # create the pop image that appears where the balloon is popped. The balloon's x, y, width, and
                    # height are passed into the constructor.
                    pop = PopImage(self.position_x, self.position_y, self.myWidth, self.myHeight)
                    # add the pop object to the parent
                    my_parent.add_widget(pop)
                    # remove the balloon from the parent
                    my_parent.remove_widget(self)
                # delete this object from memory
                del self

    # method called when a balloon surpasses its destination or the destination needs initialized
    def get_new_destination(self):
        global balloonYDestination, balloonYSpawn, balloonSpawnHeading, balloonIncline
        # to get to the next destination how steep should the balloons climb? They can climb from a random number
        # between 20-80% of the balloon's height
        balloonIncline = random.randint(int(self.myHeight / 5), int(self.myHeight * 0.8))
        # sets a new balloon destination
        balloonYDestination = random.randint(math.floor(Window.height * 0.2), math.floor(Window.height * 0.7))
        # if the destination is greater than where the balloons are currently spawning, spawn down
        if balloonYSpawn > balloonYDestination:
            # balloon is higher than the destination, start spawning down
            balloonSpawnHeading = "down"
        else:
            # balloon is lower than the destination, start spawning up
            balloonSpawnHeading = "up"

    # method called when the balloon has not reached its destination yet
    def move_y_toward_destination(self):
        global balloonYSpawn
        # if the balloons are moving up to the destination
        if balloonSpawnHeading == "up":
            # increase in y position
            balloonYSpawn += balloonIncline
        # balloons are moving down toward the destination
        else:
            # move down in y position
            balloonYSpawn -= balloonIncline

    # method called and after 0.5 seconds triggers the balloon to be destroyed without a pop icon or sound
    def destroy_without_pop(self, time_passed):
        # creates an empty variable
        my_parent = None
        # if the parent isn't none
        if self.parent is not None:
            # set the parent variable to the parent
            my_parent = self.parent
        # if the parent variable isn't none
        if my_parent is not None:
            # unschedule the clock to move the balloon
            Clock.unschedule(self.move_balloon)
            # remove the balloon from the layout
            self.parent.remove_widget(self)
            # delete the object from memory
            del self


# image that displays the cartoon-like pop for a split-second after a balloon pops. See the corresponding popimage.kv
# file.
class PopImage(Widget):
    # create attribute referenced in popimage.kv
    position_x = NumericProperty(0)
    position_y = NumericProperty(0)
    myHeight = NumericProperty(0)
    myWidth = NumericProperty(0)
    myAngle = NumericProperty(0)

    # initialize new balloon objects. Receives the x, y, width, and height of the balloon that is calling on the
    # creation of this pop image.
    def __init__(self, parent_pos_x, parent_pos_y, parent_width, parent_height, **kwargs):
        # enables access to the parent class's methods and properties
        super().__init__(**kwargs)
        # Height of the balloon image multiplied by the ratio of pixelHeight_pop_image:pixelHeight_balloon_image
        # gives the adjusted height of the pop image. Keeps original width:height ratio.
        self.myHeight = parent_height * (84 / 103)
        self.myWidth = parent_width * (92 / 87)
        # spawn the object in the same position the parent balloon was popped
        self.position_x = parent_pos_x
        self.position_y = parent_pos_y
        # move the pop image at the rate the balloons are moving
        Clock.schedule_interval(self.move, 1 / 60.)
        # destroy after .1 second
        Clock.schedule_once(self.destroy, 0.1)

    # method for moving the balloon called 60fps.
    def move(self, time_passed):
        # move the balloon left at the rate the balloons are moving
        self.position_x -= balloonSpeed

    # method for destroy the image after 0.1 seconds
    def destroy(self, time_passed):
        # stop running the clock for moving the balloon pop image
        Clock.unschedule(self.move)
        # tell the parent to remove this widget
        self.parent.remove_widget(self)
        # delete this object from memory
        del self


# this class builds the status bar at the top of the screen. It displays icons and labels of the pop count, best pop
# count, and the amount of balloons missed. See the corresponding popcount.kv file.
class PopCount(Widget):
    # create attributes referenced in the popcount.kv files
    # attributes for the pop count icon
    pop_position_x = NumericProperty(0)
    pop_position_y = NumericProperty(0)
    popWidth = NumericProperty(0)
    popHeight = NumericProperty(0)
    # attributes for the miss count icon
    miss_position_x = NumericProperty(0)
    miss_position_y = NumericProperty(0)
    missWidth = NumericProperty(0)
    missHeight = NumericProperty(0)
    # attribute for how wide the textbox for the pop count is
    pop_label_width = NumericProperty(0)

    # initialize the widget and add labels to it
    def __init__(self, **kwargs):
        # access methods and properties of the parent class
        super(PopCount, self).__init__(**kwargs)
        global popCount, missCount, missesAllowed, bestPopCount

        # every 50 pops, 10 more misses are allowed. When these lives are added this variable because True to prevent
        # the game from adding more lives since a clock checks if the pig popped 50 balloons 60fps and would continue
        # adding lives until another balloon is popped.
        self.added_lives = False
        # the pop icon y position is located roughly 8% down from the top of the screen
        self.pop_position_y = Window.height - Window.height * .0846
        # the pop icon height is 7% of screen height
        self.popHeight = Window.height * 0.07
        # ensure the balloon image keeps its original width:height ratio
        self.popWidth = self.popHeight * 97 / 103
        # place the icon slightly to the right of the the left side of the screen
        self.pop_position_x = self.popWidth / 2

        # sets the width of the pop count text box proportional to the its icon's width, which is proportional to the
        # device size
        self.pop_label_width = 350 * self.popWidth / 54.5836
        # create a Label object with pre-set attributes
        self.pop_label = Label(
            # the label is located to the right of the pop icon with a 40% margin. It has the same y pos as the icon.
            pos=(self.pop_position_x + self.popWidth * 1.4, self.pop_position_y),
            # the text this label says is the pop count
            text=str(popCount),
            # set the text box to the size of the calculated label width and the height the same height as the icon.
            size=(self.pop_label_width, self.popHeight),
            # the size of the text is the same as the line above. These two lines create the text box.
            text_size=(self.pop_label_width, self.popHeight),
            # since the game is written in a FloatLayout kivy likes to know if the object should be position between
            # 0-100% from the right size of the screen, this is the size hint. Since we know the exact x position,
            # that is already proportional to device size pass in None.
            size_hint_x=None,
            # 23sp size of the text in the testing environment. This text size is proportional to the height of
            # of the screen.
            font_size=str(23 * self.popWidth / 54.5836) + "sp",
            # sets the font to a pixelated arcade font located in this projects directory
            font_name="PressStart2P.ttf",
            # align text to the left of the text area horizontally
            halign='left',
            # align text to the center of the text area vertically
            valign='center'
        )

        # spawns the miss icon left of the label with a 20% margin
        self.miss_position_x = self.pop_position_x + self.pop_label_width * 1.2
        # sets the y position of the miss icon to the same as the pop label y
        self.miss_position_y = self.pop_position_y
        # sets the miss icon width to the same value as the pop width
        self.missWidth = self.popWidth
        # sets the miss icon height to the same value as the pop height
        self.missHeight = self.popHeight

        # creates a label with pre-set attributes
        self.misses_label = Label(
            # the label is located to the right of the pop label with a 40% margin. It has the same y pos as the icon.
            pos=(self.miss_position_x + self.missWidth * 1.4, self.miss_position_y),
            # concatenates the miss count with a "/" and the miss allowed
            text=str(missCount) + "/" + str(missesAllowed),
            # width and height of textbox set to the same value as the pop count text box.
            size=(self.pop_label_width, self.popHeight),
            # same as size of the label. Creates the textbox.
            text_size=(self.pop_label_width, self.popHeight),
            # since the game is written in a FloatLayout kivy likes to know if the object should be position between
            # 0-100% from the right size of the screen, this is the size hint. Since we know the exact x position,
            # that is already proportional to device size pass in None.
            size_hint_x=None,
            # 23sp size of the text in the testing environment. This text size is proportional to the height of
            # of the screen.
            font_size=str(23 * self.popWidth / 54.5836) + "sp",
            # sets the font to a pixelated arcade font located in this projects directory
            font_name="PressStart2P.ttf",
            # align text to the left of the text area horizontally
            halign='left',
            # align text to the center of the text area vertically
            valign='center'
        )
        # creates the best pop count label
        self.best_label = Label(
            # located at the same x position at the pop icon and beneath the pop icon.
            pos=(self.pop_position_x, self.pop_position_y - self.popHeight),
            # displays the text Best: bestPopCount
            text=str("Best:" + str(bestPopCount)),
            # creates the textbox size as the same as the pop count label's textbox
            size=(self.pop_label_width, self.popHeight),
            # creates the textbox size as the same as the pop count label's textbox
            text_size=(self.pop_label_width, self.popHeight),
            # do not place the x position proportional to the device size since it is already hard-coded into an x
            # value
            size_hint_x=None,
            # set the font size to be smaller than the pop count label and make it proportional to the device size
            font_size=str(14 * self.popWidth / 54.5836) + "sp",
            # sets the font to a pixelated arcade font located in this projects directory
            font_name="PressStart2P.ttf",
            # align text to the left of the text area horizontally
            halign='left',
            # align text to the center of the text area vertically
            valign='center',
            # set the color of the font to white
            color=(1, 1, 1, 1)
        )
        # add the labels and icons to the canvas
        self.add_widget(self.best_label)
        self.add_widget(self.pop_label)
        self.add_widget(self.misses_label)
        # start a clock to continuously update the text of the labels
        Clock.schedule_interval(self.update_text, 1 / 60.)

    # clock that updates the labels 60fps.
    def update_text(self, time_passed):
        global popCount, bestPopCount, missesAllowed
        # if the game is just starting/reset
        if popCount == 0:
            # set the best label text to white
            self.best_label.color = (1, 1, 1, 1)
        # update the pop count label to the pop count
        self.pop_label.text = str(popCount)
        # update the miss count label to the misscount
        self.misses_label.text = str(missCount) + "/" + str(missesAllowed)
        # gain 10 misses allowed every 50 pops
        if popCount % 50 == 0 and popCount != 0 and not self.added_lives:
            # prevent extra lives from adding since this is looped 60fps
            self.added_lives = True
            # play a bonus sound when lives are added
            sound = SoundLoader.load("Audio/bonus.wav")
            sound.loop = False
            sound.volume = 1
            sound.play()
            # add lives
            missesAllowed += 10
            # set the misses label color to green
            self.misses_label.color = (0, .85, 0, 1)
            # schedule the mises label color to revert back to white 0.1 seconds later
            Clock.schedule_once(self.ungreen_label, 0.1)
        # if lives were added and the pop count no longer is a multiple of 50
        if popCount % 50 != 0 and self.added_lives:
            # change added lives back to False
            self.added_lives = False
        # if the pop count is greater than the best score
        if popCount > bestPopCount:
            # change the best pop count label to gold
            self.best_label.color = (.9, .85, .05, 1)
            # update the best pop count label to update with the pop count
            self.best_label.text = "Best:" + str(popCount)

    # method that reverts the misses label color back to white
    def ungreen_label(self, time_passed):
        # change text back to white
        self.misses_label.color = (1, 1, 1, 1)


# STEP 2: Create the game window. See the corresponding main.kv file.
class MainGame(FloatLayout):
    # initializes the game when the app is started
    def __init__(self, **kwargs):
        # accesses properties and methods from FloatLayout
        super().__init__(**kwargs)
        global bestPopCount, store
        # create a cloud layout layer where all the clouds will be spawned (this will be above the sky background)
        cloud_layout = CloudLayout()
        self.add_widget(cloud_layout)
        # in the json file set as store in global variables, get the best score value saved to local memory in at the
        # key 'bestScore'
        bestPopCount = store.get('bestScore')[
            'best']
        # create a new float layout for menu items
        self.menu_layout = FloatLayout()
        # create the start button
        start_button = Button()
        # the start button width and height should both take up 30% of the screen
        start_button.size_hint = (.3, .3)
        # the start button should be located in the middle of the screen horizontally and 30% up the screen vertically
        start_button.pos_hint = {'center_x': .5, 'center_y': .3}
        # set the start button text to say "start"
        start_button.text = "Start"
        # change its font style
        start_button.font_name = "PressStart2P.ttf"
        # make the font medium sized
        start_button.font_size = "20sp"
        # upon the buttons release it will remove the layout with all menu items attached to it
        start_button.bind(on_release=self.remove_layout)
        # creates an image object for the title image
        title = Image()
        # the image should take up no more than 90% of the screen horizontally and no more than 90% of screen vertically
        title.size_hint = (.9, .9)
        # the title image is centered horizontally and located 70% up screen vertically
        title.pos_hint = {'center_x': .5, 'center_y': .7}
        # changes the title image to the title image .png file
        title.source = "Assets/popper_pig_title.png"
        # add the start button and the title to the menu layout
        self.menu_layout.add_widget(start_button)
        self.menu_layout.add_widget(title)
        # add the menu layout
        self.add_widget(self.menu_layout)

    # removes the menu layout. *ignore is needed on button release commands since they pass an additional argument
    # to the function they call.
    def remove_layout(self, *ignore):
        global balloonSpeed, balloonYSpawn, balloonHeight, balloonWidth
        # game is now starting
        # start the initial y position of the balloons to the middle of the screen
        balloonYSpawn = Window.height / 2
        # create a pop count widget
        pop_count_widget = PopCount()
        # create a tap to start widget that shows the user when they tap the screen the pig goes up
        tap_start_widget = TapToStart()
        # create the main character pig
        pig = Pig()
        # add the objects created
        self.add_widget(tap_start_widget)
        self.add_widget(pop_count_widget)
        self.add_widget(pig)

        # set the balloon height to  6.93% of the screen
        balloonHeight = Window.height * 0.0693
        # persevere the width:height ratio of the balloon.png file
        balloonWidth = (87 / 103) * balloonHeight
        # set the starting balloon speed. This will be added increased, making the game faster over time.
        balloonSpeed = balloonWidth * 0.1
        # remove the menu layout and its children
        self.remove_widget(self.menu_layout)

    # after 0.5 seconds after the game ends prepare for the next game
    def build_end_game_menu(self, time_passed):
        # create a new pig and tap to start tutorial image
        pig = Pig()
        tap_start_widget = TapToStart()
        # add the objects to the layout
        self.add_widget(pig)
        self.add_widget(tap_start_widget)

    # when the game is over by the pig flying off the screen or getting too many misses
    def end_game(self):
        global balloonSpeed, bestPopCount, gameStage, pigX, pigY, pigHeight, store
        # stop the balloons from moving (this also tells the rest of the game the player lost)
        balloonSpeed = 0
        # play a pop sound as the pig gets popped
        sound = SoundLoader.load("Audio/pop2.wav")
        sound.loop = False
        sound.pitch = random.randint(8, 20) / 10
        sound.volume = 0.1
        sound.play()
        # change the game stage to end game
        gameStage = "endGame"
        # create a pop image at the location of the pig with the same height as the pig
        pop = PopImage(pigX * 1.2, pigY, pigHeight * (84 / 92), pigHeight)
        # add the pop image to the layout
        self.add_widget(pop)
        # if the user got a new high score
        if popCount > bestPopCount:
            # update the high score to the pop count
            bestPopCount = popCount
            # Writes high score to local memory in the JSON file, popper_pig.json. "best" is the key and bestPopCount
            # is the value.
            store.put('bestScore', best=int(bestPopCount))
        # after 0.5 build the end game menu to prepare for the next game
        Clock.schedule_once(self.build_end_game_menu, 0.5)

    # ran 60fps to check if a balloon should be spawned and if the game is over
    def ask_balloon_spawner(self, time_passed):
        global pigY, pigHeight, balloonSpeed, balloonWidth, distSinceLastSpawn
        # did the player lose by getting too many misses or flying off the screen?
        if (missCount >= missesAllowed) or (pigY < -pigHeight) or (pigY > Window.height + pigHeight):
            # stop the clock that runs this method
            Clock.unschedule(self.ask_balloon_spawner)
            # end the game
            self.end_game()
        # if the space between the last balloon spawned is greater than 120% of a balloons width
        if distSinceLastSpawn >= balloonWidth * 1.2 and gameStage == "inGame":
            # then spawn a balloon
            balloon = Balloon()
            self.add_widget(balloon)
            # reset the distance since last spawning a balloon back to 0
            distSinceLastSpawn = 0
        else:
            # add the distance the balloons moved this frame to the distance since a balloon was last spawned
            distSinceLastSpawn += balloonSpeed


# STEP 1: Create the app by inheriting from the class App made by kivy.
class MainApp(App):
    # as the app is being built
    def build(self):
        # this is how I tested the game. Every proportion to adjust graphics and movemnt proportionally to the device's
        # size comes from these values.
        # Window.size = (2688 / 3, 1242 / 3)
        # Config.set('graphics', 'width', 2688 / 3)
        # Config.set('graphics', 'height', 1242 / 3)
        # - - -
        # create the window where the game will take place
        game = MainGame()
        # return the game to the device
        return game


# run the app
MainApp().run()
