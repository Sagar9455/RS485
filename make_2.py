.PHONY: all install setup run clean

# Default target
all: install setup run

# Install required libraries
install:
	pip install -r requirements.txt

# Setup CAN interface
setup:
	sudo ip link set can0 type can bitrate 500000
	sudo ifconfig can0 up

# Run the main program
run:
	python3 main.py

# Cleanup resources (useful if CAN interface needs reset)
clean:
	sudo ifconfig can0 down
