import RPi.GPIO as GPIO
import time
import threading

class GPIOHandler:
    def __init__(self, button_callback):
        self.button_callback = button_callback
        self.buttons = [12, 16, 20, 21]  # Button GPIO pins
        self.setup_gpio()
        self.start_button_thread()

    def setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        for btn in self.buttons:
            GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def monitor_buttons(self):
        while True:
            for btn in self.buttons:
                if GPIO.input(btn) == GPIO.LOW:
                    self.button_callback(btn)
                    time.sleep(0.3)  # Debounce delay

    def start_button_thread(self):
        threading.Thread(target=self.monitor_buttons, daemon=True).start()

    def cleanup(self):
        GPIO.cleanup()
