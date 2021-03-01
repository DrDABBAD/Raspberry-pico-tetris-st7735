# Explore buttons and IRQ
# Based on reaction game micro python book
#
from machine import Pin , Timer
import utime
import urandom
#switch_pins = [14, 19]
#Switches = [right,left]
led = Pin(15, Pin.OUT, Pin.PULL_DOWN)
led2 = Pin(18, Pin.OUT, Pin.PULL_DOWN)
ledOnboard = Pin(25, Pin.OUT, Pin.PULL_DOWN)
#left_button = Pin(14, Pin.IN, Pin.PULL_DOWN)
#right_button = Pin(19, Pin.IN, Pin.PULL_DOWN)

# press_button = None

# p2.irq(lambda pin: print("IRQ with flags:", pin.irq().flags()),Pin.IRQ_FALLING)

# Whats the difference handler and callback
#_DEBOUNCE_INTERVAL = const(5)
#_DEBOUNCED_STATE = const(0x01)
#_UNSTABLE_STATE = const(0x02)
#_CHANGED_STATE = const(0x04)


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
        
    
    def debounce(self,_):
        print("debounce " + str(self.pressed) + " " + str(self.pinNo ))
        if self.pressed == False and self._pin.value() == 1:
            #
            t = self.timer.init(mode=Timer.ONE_SHOT, period=200,
                           callback=self.on_pressed)

    def on_pressed(self,_):
        self.total_count += 1
        self.pressed = True
        print(str(self.pinNo) + " presssed " + str(self.total_count))

    def disable_irq(self,_):
        self._pin.irq(handler=None)

# def button_handler(pin):

   # global press_button
    #press_button = pin

   # if press_button is left_button:
   #     led.value(1)
   #     led2.value(0)
   # elif press_button is right_button:
   #     led.value(0)
   #     led2.value(1)


print("start")

ledOnboard.value(1)
timer_start = utime.ticks_ms()

#right_button.irq(trigger=Pin.IRQ_RISING, handler=button_handler)
#left_button.irq(trigger=Pin.IRQ_RISING, handler=button_handler)
right_button = button(19)
left_button = button(14)
timer_reaction = 0

while timer_reaction < 20000:
    timer_reaction = utime.ticks_diff(utime.ticks_ms(), timer_start)
    utime.sleep(0.4)
   # print( str(timer_reaction) + " secs")

   # irq_state = machine.disable_irq()
   # Is_right_button_pressed = right_button.pressed
   # Is_left_button_pressed  = left_button.pressed
   # right_button.pressed =False
   # left_button.pressed = False
   # machine.enable_irq(irq_state)

    if right_button.pressed is True and left_button.pressed is True:
        led.value(1)
        led2.value(1)
        print("B")
        right_button.pressed = False
        left_button.pressed = False
    elif right_button.pressed is True:
        led.value(1)
        led2.value(0)
        print("R")
        right_button.pressed = False
    elif left_button.pressed is True:
        led.value(0)
        led2.value(1)
        print("L")
        left_button.pressed = False

    #     led.value(1)
   #     led2.value(0)
left_button.disable_irq
right_button.disable_irq
ledOnboard.value(0)
led.value(0)
led2.value(0)
print("end")
