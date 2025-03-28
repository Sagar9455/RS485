import time
import os
from GPIO_handler import setup_gpio, handle_buttons, cleanup
from CAN_handler import get_ecu_information
from OLED_handler import display_menu
import json

# Load configuration
with open('config.json') as config_file:
    config_data = json.load(config_file)

# Initialize GPIO setup
buttons = [
    config_data["gpio_pins"]["btn_first"],
    config_data["gpio_pins"]["btn_second"],
    config_data["gpio_pins"]["btn_enter"],
    config_data["gpio_pins"]["btn_thanks"]
]

setup_gpio(buttons)

try:
    while True:
        handle_buttons(get_ecu_information)
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    cleanup()
