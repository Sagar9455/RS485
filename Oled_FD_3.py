
# OLED_handler.py
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import time

def setup_oled():
    i2c = busio.I2C(board.SCL, board.SDA)
    oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)
    time.sleep(0.5)  # Added delay for OLED stability
    return oled
