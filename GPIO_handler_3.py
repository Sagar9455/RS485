# GPIO_handler.py
import RPi.GPIO as GPIO
import time
import os

def setup_gpio(buttons):
    GPIO.setmode(GPIO.BCM)
    for btn in buttons:
        GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def handle_buttons(get_ecu_information):
    selected_sequence = []
    menu_combinations = {
        (12, 20): "ECU Information",
        (16, 20): "Testcase Execution",
        (12, 16, 20): "ECU Flashing",
        (16, 12, 20): "File Transfer\ncopying log files\nto USB device",
        (12, 12, 20): "Reserved1\nfor future versions",
        (16, 16, 20): "Reserved2\nfor future versions"
    }

    variable = 0
    varFinal = 0

    if GPIO.input(12) == GPIO.LOW:
        time.sleep(0.2)
        variable = (variable * 10) + 1
        selected_sequence.append(12)

    if GPIO.input(16) == GPIO.LOW:
        time.sleep(0.2)
        variable = (variable * 10) + 2
        selected_sequence.append(16)

    if GPIO.input(20) == GPIO.LOW:
        varFinal = variable
        variable = 0
        selected_sequence.append(20)
        selected_option = menu_combinations.get(tuple(selected_sequence), "Invalid Input")

        if selected_option == "ECU Information":
            time.sleep(0.5)
            get_ecu_information()

        if selected_option == "Exit":
            os.system("exit")

        selected_sequence.clear()

    if GPIO.input(21) == GPIO.LOW:
        time.sleep(0.1)
        os.system('sudo poweroff')

def cleanup():
    GPIO.cleanup()

