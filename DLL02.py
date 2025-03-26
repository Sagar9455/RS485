import unittest
import can
import csv
import isotp
import udsoncan
from udsoncan.client import Client
from udsoncan.connections import PythonIsoTpConnection
import udsoncan.configs
import logging
import os
import time


# CAN Configuration
#CAN_CHANNEL = "can0"
#TX_ID = 0x7A0
#RX_ID = 0x7A8


class TestUDSFromText(unittest.TestCase):
      test_cases = []
      with open("test_cases.txt", "r") as f:
           reader = csv.reader(f)
           next(reader)  # Skip header
           for row in reader:
               if not row[0].startswith("#"):  # Ignore comments
                  test_cases.append(row)
           print(test_cases)
           
      """Retrieve and display ECU information."""
      os.system('sudo ip link set can0 up type can bitrate 500000 dbitrate 1000000 restart-ms 1000 berr-reporting on fd on')  # Set bitrate to 500kbps
      os.system('sudo ifconfig can0 up')

      # Logging setup
      logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')
      logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')
      # Define ISO-TP parameters for CAN FD with 11-bit identifiers
      isotp_params = {
        'stmin': 32,
        'blocksize': 8,
        'wftmax': 0,
        'tx_padding': 0x00,
        'rx_flowcontrol_timeout': 1000,
        'rx_consecutive_frame_timeout': 1000,
        'max_frame_size': 4095,
        'can_fd': True,    
        'bitrate_switch': True# Enable CAN FD mode
      }   
       # UDS Client Configuration
      config = dict(udsoncan.configs.default_client_config)
      config["ignore_server_timing_requirements"] = True
      #config["padding_byte"] = 0x00
      config["data_identifiers"] = {
          0xF100: udsoncan.AsciiCodec(8),
          0xF101: udsoncan.AsciiCodec(8),
          0xF187: udsoncan.AsciiCodec(13),
          0xF1AA: udsoncan.AsciiCodec(13),
          0xF1B1: udsoncan.AsciiCodec(13),
          0xF193: udsoncan.AsciiCodec(13),
          0xF120: udsoncan.AsciiCodec(16),
          0xF18B: udsoncan.AsciiCodec(8),
          0xF102: udsoncan.AsciiCodec(13) 
      }
      # Define CAN interface
      interface = "can0"

      # Create CAN bus interface
      bus = can.interface.Bus(channel=interface, bustype="socketcan", fd=True)
      bus.set_filters([{"can_id":0x18DAF110,"can_mask":0xFFF}])

      # Define ISO-TP addressing for 11-bit CAN IDs
      tp_addr = isotp.Address(isotp.AddressingMode.Normal_29bits, txid=0x18DA34FA, rxid=0x18DAFA34)

      # Create ISO-TP stack
      stack = isotp.CanStack(bus=bus, address=tp_addr, params=isotp_params)

      # Create UDS connection
      conn = PythonIsoTpConnection(stack)
      
      # Start UDS Client
      with Client(conn, request_timeout=5,config=config) as client:
           logging.info("UDS Client Started")
           """Execute UDS test cases dynamically from a file."""
        
           for case in test_cases:
               tc_id, step, service_id, subfunction, expected_response = case

               service_id = int(service_id, 16)
               subfunction = int(subfunction, 16)
               expected_response = int(expected_response, 16)
 
               print(f"Executing {tc_id}: {step}")
               time.sleep(0.5)
               if service_id == 0x10:  # Diagnostic Session Control                           
                   try:
                       response = client.change_session(subfunction)
                       if response.positive:
                          logging.info("Switched to Extended Session")
                       else:
                            logging.warning("Failed to switch to Extended Session")
                   except Exception as e:
                          logging.error(f"Error in Extended Session: {e}")
                          
               elif service_id == 0x22:  # Read Data By Identifier
                     try:
                        response = client.read_data_by_identifier(subfunction)
                        if response.positive:
                           logging.info("Switched to rdbi  ")
                        else:
                           logging.warning("Failed to switch to RDBI ")
                     except Exception as e:
                           logging.error(f"Error in RDBI : {e}")                 
        
               elif service_id == 0x27:  # Security Access
                    try:
                      if subfunction == 0x01: # Security Access
                          response = client.request_seed(SecurityAccess.Level.requestSeed)
                      else:
                          response = client.send_key(b"\x12\x34\x56\x78")  # Mock key
                      if response.positive:
                          logging.info("switched Security Access ")
                      else:
                          logging.warning("Failed switched Security Access")
                    except Exception as e:
                          logging.error(f"Error in security Extended Session: {e}")
                          
               elif service_id == 0x2E:  # Write Data By Identifier
                    try:
                        response = client.write_data_by_identifier(subfunction, b"\x01\x02\x03\x04")
                        if response.positive:
                           logging.info("Switched to WDBI  ")
                        else:
                           logging.warning("Failed to switch to WDBI ")
                    except Exception as e:
                           logging.error(f"Error in WDBI : {e}")    
               else:
                    fail(f"Unsupported service {hex(service_id)}")

               #self.assertEqual(response.service_data[0], expected_response, f"Test {tc_id} failed")

   
if __name__ == "__main__":
    unittest.main()

