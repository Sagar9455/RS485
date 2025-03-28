# CAN_handler.py
import json
import logging
import os
import can
import isotp
from udsoncan.client import Client
from udsoncan.connections import PythonIsoTpConnection
import udsoncan.configs

def setup_can_interface(interface):
    if os.system(f'ip link show {interface} > /dev/null 2>&1') == 0:
        logging.info(f"{interface} is already active")
    else:
        os.system(f'sudo ip link set {interface} up type can bitrate 500000 dbitrate 1000000 restart-ms 1000 berr-reporting on fd on')

def get_ecu_information():
    with open('config.json') as config_file:
        config_data = json.load(config_file)

    setup_can_interface(config_data["can_interface"])
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

    bus = can.interface.Bus(channel=config_data["can_interface"], bustype="socketcan", fd=True)
    bus.set_filters([{"can_id": int(config_data["can_ids"]["rx_id"], 16), "can_mask": 0xFFF}])

    tp_addr = isotp.Address(isotp.AddressingMode.Normal_11bits,
                            txid=int(config_data["can_ids"]["tx_id"], 16),
                            rxid=int(config_data["can_ids"]["rx_id"], 16))

    stack = isotp.CanStack(bus=bus, address=tp_addr, params=config_data["isotp_params"])
    conn = PythonIsoTpConnection(stack)

    config = dict(udsoncan.configs.default_client_config)
    config["ignore_server_timing_requirements"] = config_data["uds_config"]["ignore_server_timing_requirements"]
    config["data_identifiers"] = {
        int(key, 16): udsoncan.AsciiCodec(value)
        for key, value in config_data["uds_config"]["data_identifiers"].items()
    }

    with Client(conn, request_timeout=2, config=config) as client:
        logging.info("UDS Client Started")
        client.tester_present()
        logging.info("Tester Present sent successfully")
        change_session_with_retry(client, 0x01)
        change_session_with_retry(client, 0x03)
        for did in config["data_identifiers"]:
            try:
                response = client.read_data_by_identifier(did)
                if response.positive:
                    logging.info(f"ECU information (DID {hex(did)}): {response.service_data.values[did]}")
                else:
                    logging.warning(f"Failed to read ECU information (DID {hex(did)})")
            except Exception as e:
                logging.error(f"Error reading ECU information (DID {hex(did)}): {e}")

def change_session_with_retry(client, session_type, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.change_session(session_type)
            if response.positive:
                logging.info(f"Switched to session {session_type} successfully")
                return
            else:
                logging.warning(f"Attempt {attempt + 1}: Failed to switch to session {session_type}")
        except Exception as e:
            logging.error(f"Attempt {attempt + 1}: Error in session {session_type} - {e}")
        time.sleep(0.5)
