# Raspberry pico tetris using st7735 and micro python

The Original idea for this project was to emulate the simple tetris programs found for [Micro:bit] <https://blog.withcode.uk/2016/12/microbit-tetris-in-python/>.
(This probably would have been better implemented using pico display pack <https://shop.pimoroni.com/collections/pico>.) and learn something  about the Raspberry pi pico board.:
I knew I needed a pair of buttons; a screen and micro controller. I could then split the programming into
3 tasks:

* Buttons and events
* Screen and graphic rendering
* Game logic and loops.

As a neophyte with limited  electronics, MicroPython and raspberry pi pico knowledge I started off following [Get started with MicroPython on raspberry pi pico]<https://www.raspberrypi.org/blog/new-book-get-started-with-micropython-on-raspberry-pi-pico/>.
 I thought this would give pointers for the code needed to control both the buttons and screen.

 ## Buttons bounce (or debounce) who new?

Well, everybody but me apparently. Following the text for IRQ buttons I wired buttons and started writing code examples. I immediately found problems, the examples did not work as expected with LEDs either not lighting or staying on. There were three issues: 1) [Errata in the book]<https://hackspace.raspberrypi.org/downloads/eyJfcmFpbHMiOnsibWVzc2FnZSI6IkJBaHBBcW9SIiwiZXhwIjpudWxsLCJwdXIiOiJibG9iX2lkIn19--6dc8e90235a820703b1ce14d62cf4999c2e02c49/210226%20Get%20Started%20with%20Micropython%20Errata.pdf> 2) Firmware for the board <https://micropython.org/download/rp2-pico/>3) buttons bouncing.
The former were fixed by making sure all a pull_down constant was included in all button initiation statements.
```
Pin(15, Pin.OUT, Pin.PULL_DOWN)
```

The latter button debounce  was bit more involved.  Button bouncing  results in an oscillation of voltage caused by button making contacts connecting several times during a press or release of button. The fix is either smoothing circuity or more usually timing  lags or looping counts in the program.
An elegant solutionand description included in [Adafruit debouce libraires] <https://learn.adafruit.com/debouncer-library-python-circuitpython-buttons-sensors> however this is circuit python and had a few more decencies to unpick than the this weekend coding project would allow.
So I plumped for the time delay implemented in the buttons class.

## ST7735 screen

For this project used the MakerHawk TFT LCD Screen 1.8inch Graphic Color Screen <https://www.amazon.co.uk/gp/product/B07N6FQ5XW/ref=ppx_yo_dt_b_asin_title_o06_s01?ie=UTF8&psc=1>

Originally I naively though I could just pick the SPI examples  in [Get started with MicroPython on raspberry pi pico]<https://www.raspberrypi.org/blog/new-book-get-started-with-micropython-on-raspberry-pi-pico/>, however nothing happened.
Looking at C code supplied with the ST7735 together with,at least to me, the obtuse documentation on the screen itself two thing were apparent: You need a font library file and  pins other than
SPI pins to switch between command and data sent between from the pico board to the screen.
A search for with google exposed elegant libraries from Adafruit but these were circuit python with a string of dependencies that would need conversion as I chased through the libraries.
In this case I picked the libraries of [boochow] <https://github.com/boochow/MicroPython-ST7735> and [GuyCarver]<https://github.com/GuyCarver/MicroPython/blob/master/lib/ST7735.py> as this would need a small amount of hacking to include the machine pins modules. an issue still remains with this driver
 the init functions, I used initg since it mostly worked. but it still needs some hacking to remove a
 a 1 pixel screen shift around the edge of the screen.
## Game logic and loop

Although I originally though micro:bit would be good fit game logic I quickly released that several articles on the pygame module and tetris <https://levelup.gitconnected.com/writing-tetris-in-python-2a16bddb5318> were a much better fit. The main recoding here was to replace the pygame libraries with those of the ST7735 used to render the blocks and text.

## Parts
LED     x2
Buttons x2
330Kohm x2
Screen ST7735

## Pinouts

### Screen
ST7735 Driver                      |Pico               |ST7735 Board
---------------------------------------------------------|--------------
SPI_SCK = 10 # sck                   |  SPI1_SCK (GP10)  |  SCK
SPI_SDO = 11 # mosi(Controller SDO)  |  SPI_TX   (GP11)  |  SDA
SPI_DC = 3  # aDC                    |  GP3              |  DC
SPI_RS = 2  # aReset                 |  GP2              |  RS
SPI_CS = 4  # ACS                    |  GP4              |  CS
VCC                                     VCC                 VCC
GND                                     GND                 GND

### Buttons and LED GPIO

led = 15
led2 = 18
BTN_LEFT =  19
BTN_RIGHT = 14

## Resources
SEE <https://datasheets.raspberrypi.org/pico/Pico-R3-A4-Pinout.pdf>
 SEE <https://www.oshwa.org/a-resolution-to-redefine-spi-signal-names/>

 https://www.pygame.org/docs/tut/tom_games2.html
 https://www.techwithtim.net/tutorials/game-development-with-python/tetris-pygame/tutorial-2/

 https://www.101computing.net/bbc-microbit-tetris-game/
 https://blog.withcode.uk/2016/12/microbit-tetris-in-python/

 https://shop.pimoroni.com/products/get-started-with-micropython-on-raspberry-pi-pico


https://www.amazon.co.uk/gp/product/B07N6FQ5XW/ref=ppx_yo_dt_b_asin_title_o06_s01?ie=UTF8&psc=1
https://drive.google.com/drive/folders/1TnI11iVNIAmHYrTuW_EMTs_RG-VNEeyI