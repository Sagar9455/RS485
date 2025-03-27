from gpio_utils import GPIOHandler
from can_utils import CANHandler
from oled_utils import display_text
import time

# Initialize CAN and OLED
can_handler = CANHandler(display_callback=display_text)

# Display welcome message
display_text("Welcome to CAN Demo")
time.sleep(1.5)

# Button callback function
def handle_button_press(btn):
    can_handler.send_can_message(btn)

# Initialize GPIO with button callback
gpio_handler = GPIOHandler(button_callback=handle_button_press)

# Start CAN reception in a separate thread
can_handler.start_rx_thread()

# Main loop
try:
    while True:
        display_text("Press a Button to Send:\n1. 0x123\n2. 0x456\n3. 0x789\n4. 0x111", y=0)
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nExiting...")
    gpio_handler.cleanup()  # Cleanup GPIO resources
