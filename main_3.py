import time
import os
from GPIO_handler import setup_gpio, read_buttons
from CAN_handler import get_ecu_information
from OLED_handler import display_menu

# Initialize GPIO setup
setup_gpio()

# Menu combinations
menu_combinations = {
    (12, 20): "ECU Information",
    (16, 20): "Testcase Execution",
    (12, 16, 20): "ECU Flashing",
    (16, 12, 20): "File Transfer\ncopying log files\nto USB device",
    (12, 12, 20): "Reserved1\nfor future versions",
    (16, 16, 20): "Reserved2\nfor future versions"
}

selected_sequence = []
variable = 0
varFinal = 0

try:
    while True:
        button_pressed = read_buttons()
        if button_pressed:
            if button_pressed == 12:
                time.sleep(0.2)
                variable = (variable * 10) + 1
                selected_sequence.append(12)

            elif button_pressed == 16:
                time.sleep(0.2)
                variable = (variable * 10) + 2
                selected_sequence.append(16)

            elif button_pressed == 20:
                varFinal = variable
                variable = 0
                selected_sequence.append(20)

                selected_option = menu_combinations.get(tuple(selected_sequence), "Invalid Input")
                display_menu(selected_option)

                if selected_option == "ECU Information":
                    time.sleep(0.5)
                    get_ecu_information()

                if selected_option == "Exit":
                    os.system("exit")

                selected_sequence.clear()

            elif button_pressed == 21:
                time.sleep(0.1)
                os.system('sudo poweroff')

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    import RPi.GPIO as GPIO
    GPIO.cleanup()
