from ODO_sensor_lib import YSIOdoRtuSensor
import time
import logging
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
def main():
    # Create an instance of the sensor with the appropriate settings
    # Replace 'COM3' with your actual port
    sensor = YSIOdoRtuSensor(port='/dev/ttyUSB0', baudrate=9600, stop_bits=1, parity='E', unit_id=1)

    # Connect to the sensor
    if sensor.connect():
        print("Connected to the sensor.")
    else:
        print("Failed to connect to the sensor.")
        return

    FORMAT = ('%(asctime)-15s %(threadName)-15s' 
    ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
    logging.basicConfig(format=FORMAT)
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    def processResponse(result):
        log.debug(result)

    try:           
        sensor.odo_factory_reset()
        print(sensor.get_odo_last_calibration_time_and_qc_score())

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Disconnect from the sensor
        sensor.disconnect()
        print("Disconnected from the sensor.")

if __name__ == "__main__":
    main() 