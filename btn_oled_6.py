import time
import RPi.GPIO as GPIO
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)

# Define button pins
BTN_FIRST = 12  # First button in combination
BTN_SECOND = 16  # Second button in combination
BTN_ENTER = 20  # Confirm selection
BTN_THANKS = 21  # System is shutting down
buttons = [BTN_FIRST, BTN_SECOND, BTN_ENTER, BTN_THANKS]

# Set up buttons as input with pull-up resistors
for btn in buttons:
    GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize I2C and OLED
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

# Load font
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)

# Menu options mapped to button sequences
menu_combinations = {
    (BTN_FIRST, BTN_ENTER): "ECU Information",
    (BTN_SECOND, BTN_ENTER): "Testcase Execution",
    (BTN_FIRST, BTN_SECOND, BTN_ENTER): "ECU Flashing",
    (BTN_SECOND, BTN_FIRST, BTN_ENTER): "File Transfer (copying log files into USB device)",
    (BTN_FIRST, BTN_SECOND, BTN_ENTER): "Reserved for future versions",
    (BTN_SECOND, BTN_SECOND, BTN_ENTER): "Reserved for future versions"
}
selected_sequence = []
selected_option = None
last_displayed_text = ""

def display_text(text):
    """Function to display text on OLED only if changed"""
    global last_displayed_text
    if text != last_displayed_text:  # Avoid redundant updates
        oled.fill(0)  # Clear screen
        oled.show()
        
        image = Image.new("1", (oled.width, oled.height))
        draw = ImageDraw.Draw(image)
        draw.text((10, 25), text, font=font, fill=255)
        
        oled.image(image)
        oled.show()
        last_displayed_text = text

try:
    while True:
        if GPIO.input(BTN_FIRST) == GPIO.LOW:
            selected_sequence.append(BTN_FIRST)
            time.sleep(0.3)  # Improved debounce
        
        if GPIO.input(BTN_SECOND) == GPIO.LOW:
            selected_sequence.append(BTN_SECOND)
            time.sleep(0.3)  # Improved debounce
        
        if GPIO.input(BTN_ENTER) == GPIO.LOW:
            selected_sequence.append(BTN_ENTER)
            selected_option = menu_combinations.get(tuple(selected_sequence), "Unknown Option")
            display_text(f"Confirmed: {selected_option}")
            selected_sequence.clear()  # Reset sequence after confirmation
            time.sleep(1)
        
        if GPIO.input(BTN_THANKS) == GPIO.LOW:
            display_text("System is shutting down")
            time.sleep(1)
        
        time.sleep(0.1)  # Shorter general debounce delay

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    GPIO.cleanup()