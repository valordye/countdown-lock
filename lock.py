from PIL import Image, ImageDraw, ImageFont
import time
from gpiozero import Button, LED, Buzzer
from waveshare_epd import epd2in13_V4

btn1 = Button(23)
btn2 = Button(5)
btn3 = Button(6)

led_red = LED(27) #13
led_green = LED(22) #15
buzzer = Buzzer(4) #7

epd = epd2in13_V4.EPD() 

# system target 
CORRECT_PIN = [1, 2, 3]
PIN_LENGTH = 3

current_input = []

#need to capture button press events 
#emite audio click with buzzer
#redraw canvas 
#display feedback * * _ 
#count entries in current-input and build display string based on filled slots
#current_input = [1] -> string render * _ _
#maybe start as * * * and do like * * 1, and it goes left with inputs. 
# * * 1 --> * 1 2 

#verity logic: current_input == CORRECT_PIN to trigger countdown

def setup(str="* * *"):
    # Create 250x122 monochrome canvas
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
    #font = ImageFont.load_default()

    font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    font_pin = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)

    #header
    draw.rectangle([(0, 0), (epd.height - 1, 22)], fill=0)

    #header text 
    draw.text((75,3), "ENTER PIN:", fill = 255, font = font_header)

    draw.text((75, 50), str, fill = 0, font = font_pin )

    epd.init_fast()
    epd.display_fast(epd.getbuffer(image))
    epd.sleep()


def button_press(num): 
    global current_input
    current_input.append(num)

    #play the buzzer beep 
    #make it in background so less delay
    buzzer.beep(on_time=0.1, off_time=0.1, n=1, background=True)

    led_green.on()
    time.sleep(0.1)
    led_green.off()
    time.sleep(0.1)

    #formatting PIN string: left shifting 
    padding_count = PIN_LENGTH - len(current_input)
    display_list = ["*"] * padding_count + [str(n) for n in current_input]
    display_str = " ".join(display_list)

    #update screen display with current_input status
    setup(display_str)

    check_pin()
     
    print(f"Registered button: {num} | Display: {display_str}")

def check_pin(): 
    global current_input
    #check if entry is compelte 
    if len(current_input) == len(CORRECT_PIN):
        if current_input == CORRECT_PIN:
            trigger_success()
        else:
            setup("ERROR")
        
        #clear buffer for next attempt 
        current_input = []
        setup("* * *")

def trigger_success():
    setup("PLANTED")
    
    for i in range(15):
        #could display text dynamically each second with
        #setup(f"closing in {15 - i}s")

        led_red.on()
        buzzer.beep(on_time=0.1, off_time=0.1, n=1)
        time.sleep(0.1)
        led_red.off()

        speed_stage = i // 5
        current_sleep = max(0.1, 0.7 - (speed_stage * 0.25))

        time.sleep(current_sleep) #adjust sleep so total time loos is one second

    led_red.on() #solid
    buzzer.on() #buzzzzzz
    time.sleep(1.5) #long buzz
    buzzer.off() #stops buzzer


def main():

    epd.init()
    epd.Clear()
    epd.sleep()

    setup()

    try:
        while True:
            if btn1.is_pressed:
                button_press(1)
                while btn1.is_pressed:
                    time.sleep(0.01)

            elif btn2.is_pressed:
                button_press(2)
                while btn2.is_pressed:
                    time.sleep(0.01)

            elif btn3.is_pressed:
                button_press(3)
                while btn3.is_pressed:
                    time.sleep(0.01)

            time.sleep(0.05) #small CPU pause per iteration
            

    except KeyboardInterrupt:
        print("\nExiting")
        led_red.off()
        led_green.off()
        epd.init()
        epd.Clear()
        epd.sleep()

if __name__ == '__main__':
    main()
    





