
from ST7735 import TFT, TFTColor
from sysfont import sysfont
from machine import SPI, Pin, Timer

import time
import math
import random
import sys

# PINS for buttons and
# Handle button button states and debounce 


class button:

    def __init__(self, pinNo):
        self._pin = Pin(pinNo, Pin.IN, Pin.PULL_DOWN)
        self._pin.irq(trigger=Pin.IRQ_RISING, handler=self.debounce)
        self.total_count = 0
        self.pressed = False
        self.pinNo = pinNo
        self.timer = Timer(-1)

    def change_status(self):
        self.pressed = bool(self.pressed) ^ bool(self.pressed)

    def debounce(self, _):
       # print("btn debounce" + str(self.pressed) + " " + str(self.pinNo ))
        if self.pressed == False and self._pin.value() == 1:
            t = self.timer.init(mode=Timer.ONE_SHOT, period=2,
                                callback=self.on_pressed)

    def on_pressed(self, _):
        self.total_count += 1
        self.pressed = True
        #print(str(self.pinNo) + "btn pressed " + str(self.total_count))

    def disable_irq(self, _):
        self._pin.irq(handler=None)


class Figure:
    x = 0
    y = 0
    # Tetris figures shapes on 4x4 block store only shape as solid part of block together with rotations
    # Numbers 0 to 15 represent horizontal numbering of grid each row start 0,4,8,12
    #Shapes roughly  |  S L T O (Square)
    figures = [
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        [[4, 5, 9, 10], [2, 6, 5, 9]],
        [[6, 7, 9, 10], [1, 5, 6, 10]],
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        [[1, 2, 5, 6]],
    ]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.x_org = 0
        self.y_org = 0
        self.rotation_org = 0
        self.type = random.randint(0, len(self.figures) - 1)
        tcolor = random.choice(list(colours.items()))
        self.color = TFTColor(tcolor[1][0], tcolor[1][1], tcolor[1][2])
        self.rotation = 0

    # current orientations of shape '''
    def orientation(self):
        return self.figures[self.type][self.rotation]

    def orientation_last(self):
        return self.figures[self.type][self.rotation_org]
    
    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.figures[self.type])


# Tetris game holds game state 
class Tetris:
    level = 2
    score = 0
    state = "start"
    field = []
    height = 0   # Board In memory Grid 
    width = 0
    # off sets for screen
    x = 4
    y = 10
    Scale = {}
    figure = None

    def __init__(self, height, width):
        self.height = height  # What is this height and width
        self.width = width
        self.field = []  # Contains zeros when empty otherwise colors as int of forzen bricks 
        self.score = 0
        self.state = "Run"
        self.play_grid()

    # Build  playing board as field array of lines
    def play_grid(self):
        for i in range(self.height):
            new_line = []
            for j in range(self.width):
                new_line.append(0)
            self.field.append(new_line)

    def new_figure(self):
        self.figure = Figure(3, 0)
        print("New figure")
        
    #Check for intersection or collision of falling bricks
    def intersects(self):
        intersection = False
        for i in range(4):
            for j in range(4):
                print("intersect ortient" + str(self.figure.orientation()))
                if i * 4 + j in self.figure.orientation():
                    if i + self.figure.y > self.height - 1 or \
                            j + self.figure.x > self.width - 1 or \
                            j + self.figure.x < 0 or \
                            self.field[i + self.figure.y][j + self.figure.x] > 0:
                        intersection = True
        return intersection

    # Score game for each filled line 10 points 
    # Each filled square 1 point 
    # removes filled lines
    # Side effect removes full lines 
    def score_lines(self):
        lines = 0
        score = 0
        for i in range(1, self.height):
            zeros = 0
            for j in range(self.width):
                if self.field[i][j] == 0:
                    zeros += 1
                else:
                    score += 1
            if zeros == 0:
                lines += 1

                for i1 in range(i, 1, -1):
                    for j in range(self.width):
                        self.field[i1][j] = self.field[i1 - 1][j]
        self.score = lines * 10 + score

    # When the bricks ()figures) cannot move any further freeze them to board grid
    def freeze(self):
        print( "freeze" + str(self.figure.orientation()))
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.orientation():
                    print('i: {0} j: {1} x:{2} y:{3}'.format(i,j,self.figure.x,self.figure.y))
                    self.field[i + self.figure.y][j +
                                                  self.figure.x] = self.figure.color
        self.score_lines()
        self.new_figure()
        if self.intersects():
            self.state = "End"
            
            
    # Keep a copy of the last transition and or rotation
    # expect no need or deep copy as these simple varaibles are immutable.  
    def shadow_copy(self):
        self.figure.y_org = self.figure.y
        self.figure.x_org = self.figure.x
        self.figure.rotation_org = self.figure.rotation

    def go_down(self):
        self.shadow_copy()
        self.figure.y += 1
        if self.intersects():
            self.figure.y -= 1
            self.freeze()

    # left orright horizontal movement
    def traverse(self, dx):
        self.shadow_copy()
        old_x = self.figure.x
        self.figure.x += dx
        if self.intersects():
            self.figure.x = old_x

    def rotate(self):
        self.shadow_copy()
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            self.figure.rotation = old_rotation



colours = {
           'TANGO': (0xFF, 0xA5, 0x00),
           'GREEN': (0x00, 0xFF, 0x00),
           'FOREST': (0x22, 0x8B, 0x22),
           'BLUE': (0x00, 0x00, 0xFF),
           'CYAN': (0x00, 0xFF, 0xFF),
           'YELLOW': (0xFF, 0xFF, 0x00),
           'PURPLE': (0xFF, 0x00, 0xFF),
           'WHITE': (0xFF, 0xFF, 0xFF)}
# Define  Constants for Tetris
GRID_WIDTH = 10
GRID_HEIGHT = 20
# LEDS
led = Pin(15, Pin.OUT, Pin.PULL_DOWN)
led2 = Pin(18, Pin.OUT, Pin.PULL_DOWN)
# Buttons
# See pin diagram  
BTN_LEFT =  19
BTN_RIGHT = 14
# Screen ST7735
# SEE https://datasheets.raspberrypi.org/pico/Pico-R3-A4-Pinout.pdf
# SEE https://www.oshwa.org/a-resolution-to-redefine-spi-signal-names/

#         # ST7735 Driver              Pico               ST7735 Board           
SPI_SCK = 10 # sck                     SPI1_SCK (GP10)    SCK            
SPI_SDO = 11 # mosi(Controller SDO)    SPI_TX   (GP11)     SDA
SPI_DC = 3  # aDC                      GP3                 DC 
SPI_RS = 2  # aReset                   GP2                 RS
SPI_CS = 4  # ACS                      GP4                 CS    
# VCC
# GND 
# Define constants for the screen width and colors for block
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 160
# Tetris Board offset
OFFSET_X = 4
OFFSET_Y = 2
ScreenSize = (SCREEN_WIDTH, SCREEN_HEIGHT)


class GameEngine:
    def __init__(self, screensize):
        spi = SPI(1, baudrate=20000000, polarity=0, phase=0,
                  sck=Pin(SPI_SCK), mosi=Pin(SPI_SDO), miso=None)
        # def __init__( self, spi, aDC, aReset, aCS) :
        # Pin details for SPI interface for screen
        self.tft = TFT(spi, SPI_DC, SPI_RS, SPI_CS)
        self.tft.initg()   # Change this to make screen dimensions match board i.e if you get a line around the edge driver needs rewwwok for this
        self.tft.rgb(True)
        self.tft.set_size(screensize)
        self.set_caption("Tetris")
        self.level = 2
        self.screenSize = screensize
        # Board offsets
        self.x = 4
        self.y = 10
        
        # Pin details for buttons.
        self.right_button = button(19)
        self.left_button = button(14)

    def set_caption(self, caption):
        self.tft.fill(TFT.BLACK)
        v = 30
        v += sysfont["Height"] * 2
        self.tft.text((20, v), caption, TFT.GREEN, sysfont, 2, nowrap=True)
        time.sleep_ms(1000)

    def render_text(self, aText, aColour, vPos, fSize):
        self.tft.text((8, vPos), aText, aColour, sysfont, fSize, nowrap=True)

    # Draw a grid by drawing hollow rectangles starting a smallest coordinate'''
    # Then fill the hollow retangles with colours of fallen frozen blocks '''
    # For the filled rectangle.  aStart is the smallest coordinate corner
    # and aSize is a tuple indicating width, heightalready rededuced for  the ineer block
    def draw_board(self, myTetris):
        gridLineColour = TFT.RED

        # print (' blockOuter: {0} blockInner: {1}  TWidth: {2} THeight: {3}'.format( blockOuter, blockInner, myTetris.width, myTetris.height))
      
        for i in range(0, myTetris.width):
            for j in range(0, myTetris.height):

                # Render grid
                self.tft.rect((self.x + 12 * i  , self.y + 7*j ),
                             (120//10+1, 155//20+1), gridLineColour)
             
    def render_all(self,myTetris):
        for i in range(0, myTetris.width):
            for j in range(0, myTetris.height):
                self.tft.fillrect((self.x + 12 * i +1 , self.y + 7 * j + 1),
                                    (11,5)  , (myTetris.field[j][i]))
                
        #print('\n'.join(' '.join(map(str,sl)) for sl in myTetris.field))
        
    def render_frozen(self,myTetris):
        for i in range(0, myTetris.width):
            for j in range(0, myTetris.height):
                if myTetris.field[j][i] > 0:
                    #(120//10-2, 155//20-2)
                    self.tft.fillrect((self.x + 12 * i , self.y + 7 * j),
                                  (12,7)    , (myTetris.field[j][i]))
       
       
    def hide_figure(self,figure):
        for i in range(4):
            for j in range(4):
                p = i * 4 + j        
                if p in figure.orientation():
                    blockColor = TFT.BLACK
                    fx = figure.x
                    fy = figure.y
                    self.tft.fillrect(
                                (self.x + 12 * (j + fx) + 1, self.y + 7 * (fy + i) + 1),  (120//10-2, 155//20-1),  blockColor)
   # Render the floating blocks 
    def render_figure(self, figure):
        if figure is not None:
           # print("fig or last:" + str(figure.orientation_last()))
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in figure.orientation_last():
                        blockColor = TFT.BLACK
                        fx = figure.x_org
                        fy = figure.y_org

                        self.tft.fillrect(
                            (self.x + 12 * (j + fx) +1 , self.y + 7 * (fy + i) +1 ), (11,5) ,  blockColor)
                for i in range(4):
                    for j in range(4):
                        p = i * 4 + j        
                        if p in figure.orientation():
                            blockColor = figure.color
                            fx = figure.x 
                            fy = figure.y

                            self.tft.fillrect(
                                (self.x + 12 * (j + fx) +1, self.y + 7 * (fy + i)+1), (11,5) ,  blockColor)


    def game_end(self):
        self.tft.fill(TFT.BLACK)
        self.render_text("Game Over", TFT.ORANGE, 50, 2)
        self.render_text("PRESS ANY KEY", TFT.ORANGE, 90, 1)

    def game_score(self, ascore):
        self.render_text("Tetris Score: " + str(ascore), TFT.ORANGE, 1, 1)

    def game_quit(self):
        self.tft.fill(TFT.BLACK)
        self.render_text("Game END", TFT.ORANGE, 50, 2)
        return
# Run the game this is main


# Initialize the game engine this deals with setup button and screen and deals with rendering
game = GameEngine(screensize=ScreenSize)
# The game loop
counter = 0
done = False
playGame = Tetris(GRID_HEIGHT, GRID_WIDTH)
# print("Start Game loop")
pressing_down = False
game.tft.fill(TFT.BLACK)
#game.draw_board(playGame)
while not done:
    if playGame.figure is None:
        playGame.new_figure()
    counter += 1
    if counter > 100000:
        counter = 0

    if game.right_button.pressed is True and game.left_button.pressed is True:
        led.value(1)
        led2.value(1)
        print("Both rotate")
        playGame.rotate()
        game.right_button.pressed = False
        game.left_button.pressed = False
    elif game.right_button.pressed is True:
        led.value(1)
        led2.value(0)
        print("Right")
        playGame.traverse(1)
        game.right_button.pressed = False
    elif game.left_button.pressed is True:
        led.value(0)
        led2.value(1)
        print("Left")
        playGame.traverse(-1)
        game.left_button.pressed = False
    else:
        
        if  (playGame.figure.y ==0):
            game.render_all(playGame)
            game.draw_board(playGame)
            time.sleep(0.02)
        playGame.go_down()
        
            
        #print('render fig c : x: {0} y: {1} cnt:{2}'.format(
            #playGame.figure.x, playGame.figure.y ,counter))

    game.game_score(playGame.score)
 
    if playGame.figure is not None:
        game.render_figure(playGame.figure)


        
    if playGame.state == "End":
        led.value(0)
        led2.value(0)
        game.right_button.pressed = False
        game.left_button.pressed = False
        game.game_end()
        game.game_score(playGame.score)

    while (playGame.state == "End"):
        if game.right_button.pressed is True or game.left_button.pressed is True:
            playGame.__init__(GRID_HEIGHT, GRID_WIDTH)
            game.tft.fill(TFT.BLACK)
           
