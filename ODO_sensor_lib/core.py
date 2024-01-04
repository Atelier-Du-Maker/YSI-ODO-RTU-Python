#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    The ``YSIOdoRtuSensor`` package
    ======================


    .. warning:: Use the correct voltage to avoid problem with the chip.


    A Python interface to interact with the YSI ODO RTU sensor through Modbus RTU.

    This class provides methods to connect to the sensor, read sensor data, perform calibrations, and reset the sensor.

    How to Use:
    1. Initialize the sensor object with the appropriate serial port and settings.
       Example: sensor = YSIOdoRtuSensor(port='/dev/ttyUSB0', baudrate=9600)

    2. Connect to the sensor using the `connect` method.
       Example: sensor.connect()

    3. Read sensor data using methods like `get_odo_saturation`, `get_temperature`, etc.
       Example: odo_saturation = sensor.get_odo_saturation()

    4. Perform calibrations if necessary using methods like `perform_mg_L_calibration`.
       Example: sensor.perform_mg_L_calibration(timestamp, calibration_value, salinity)

    5. Reset the sensor to factory defaults using `factory_reset` if needed.
       Example: sensor.factory_reset()

    6. Always disconnect from the sensor after operations are complete.
       Example: sensor.disconnect()

    Detailed method documentation is provided with each method.

    Attributes:
        client (ModbusClient): The Modbus RTU client used for communication.
        unit_id (int): The Modbus unit ID of the sensor.


     Licence
    ------------------------

    MIT License
    -----------

    Copyright (c) 2024 Mickaël Veleine from Atelier du Maker ( https://atelierdumaker.com ) with
    the support of INREA ( Unité REVERSAAL at Villeurbanne )

    Permission is hereby granted, free of charge, to any person
    obtaining a copy of this software and associated documentation
    files (the "Software"), to deal in the Software without
    restriction, including without limitation the rights to use,
    copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following
    conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.

"""


from pymodbus.client import ModbusSerialClient as ModbusClient
from pymodbus.exceptions import ModbusException
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian

class YSIOdoRtuSensor:
    """
    A Python interface to interact with the YSI ODO RTU sensor through Modbus RTU.
    """
    
    baud_rates = {
        9600: 0x00,
        19200: 0x01,
        38400: 0x02,
        57600: 0x03,
        115200: 0x04,
    }

    parities = {
        'none': 0x00,
        'odd': 0x01,
        'even': 0x02,
        }

    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, unit_id=1, stop_bits=1, parity='E'):
        """
        Initialize a new instance of the YSIOdoRtuSensor class which provides methods to interact with the YSI ODO RTU sensor.

        This constructor sets up the Modbus RTU client with the specified port, baud rate, unit ID, stop bits, and parity.
        The default values are set for a typical connection. You may need to change them according to your sensor and
        computer setup.

        Args:
            port (str): The serial port to connect to the sensor. Defaults to '/dev/ttyUSB0'.
            baudrate (int): The baud rate for the serial communication. Defaults to 9600.
            unit_id (int): The Modbus unit ID of the sensor. Defaults to 1.
            stop_bits (int): The number of stop bits to use. Defaults to 1.
            parity (str): The parity to use. Can be 'N' (none), 'E' (even), or 'O' (odd). Defaults to 'E'.

        Example usage:
            # Create an instance with default parameters
            sensor = YSIOdoRtuSensor()

            # Create an instance with a specific serial port, baud rate, stop bits, and parity
            sensor = YSIOdoRtuSensor(port='/dev/ttyUSB0', baudrate=9600, stop_bits=1, parity='E')

        After instantiation, you should call the 'connect' method to establish communication with the sensor.
        """
        self.client = ModbusClient(method='rtu', port=port, baudrate=baudrate, stopbits=stop_bits, parity=parity, timeout=3)
        self.unit_id = unit_id
        self.connected = False

    def connect(self):
        """
        Establish a connection with the YSI ODO RTU sensor over Modbus RTU.

        This method attempts to open the communication port specified during the initialization of the sensor instance.
        If the connection is successful, it sets the 'connected' attribute to True.

        Returns:
            bool: True if the connection was successful, False otherwise.

        Example usage:
            sensor = YSIOdoRtuSensor(port='/dev/ttyUSB0', baudrate=9600, stop_bits=1, parity='E')
            if sensor.connect():
                print("Connected to the sensor.")
            else:
                print("Failed to connect to the sensor.")
        """
        try:
            self.connected = self.client.connect()
            return self.connected
        except ModbusException as e:
            print(f"Failed to connect to the sensor: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """
        Disconnect from the Modbus sensor.
        """
        self.client.close()

    def get_baud_rate_and_parity(self):
        """
        Retrieve the current baud rate and parity settings from the sensor.

        This method reads a specific register from the sensor, which contains both the baud rate and parity settings. 
        The response is decoded to extract these settings. The values are then matched against predefined mappings 
        to convert them to human-readable formats.

        Returns:
            dict: A dictionary containing 'baud_rate' and 'parity' settings as human-readable strings. 
                  Returns None if there is an error in reading from the registers.

        Example usage:
            sensor = YSIOdoRtuSensor(port='/dev/ttyUSB0', baudrate=9600, unit_id=1)
            if sensor.connect():
                config = sensor.get_baud_rate_and_parity()
                if config:
                    print("Current Baud Rate:", config['baud_rate'])
                    print("Current Parity:", config['parity'])
                else:
                    print("Failed to retrieve baud rate and parity settings.")
                sensor.disconnect()
            else:
                print("Failed to connect to the sensor.")

        Raises:
            ValueError: If there is an error in reading the register or if the decoded values 
                        do not match any entry in the predefined mappings.
        """   

        data = {}
        try:
            response = self.client.read_holding_registers(0x0001, 1, self.unit_id)
            if response.isError():
                raise ValueError("Error reading device information registers")
                
                
            decoder = BinaryPayloadDecoder.fromRegisters(response.registers, byteorder=Endian.BIG)
            parity   = decoder.decode_8bit_uint()
            baud_rate  = decoder.decode_8bit_uint()
            data['parity'] = list(self.parities.keys())[list(self.parities.values()).index(parity)]
            data['baud_rate'] = list(self.baud_rates.keys())[list(self.baud_rates.values()).index(baud_rate)]
            
            return data
            
        except Exception as e:
            print(f"Error retrieving baud rate and parity settings: {e}")
            return None 

    def set_baud_rate_and_parity(self, baud_rate, parity):
        """
           Set the baud rate and parity for the sensor's Modbus RTU communication.

           This function writes a combined value of parity and baud rate to the sensor's
           appropriate register. The upper byte of the register value sets the parity, and
           the lower byte sets the baud rate.

           Args:
               baud_rate (int): The baud rate to set (9600, 19200, 38400, 57600, 115200).
               parity (str): The parity to set ('none', 'odd', 'even').

           Returns:
               bool: True if the configuration was successful, False otherwise.

           Raises:
               ValueError: If the provided baud rate or parity is not supported.

           Example usage:
               success = sensor.set_baud_rate_and_parity(19200, 'even')
               if success:
                   print("Baud rate and parity have been successfully set. You have to reconnect")
               else:
                   print("Failed to set baud rate and parity.")
           """


        # Validate baud rate and parity
        if baud_rate not in self.baud_rates or parity not in self.parities:
            raise ValueError("Invalid baud rate or parity.")

        # Combine parity and baud rate for the register value
        # Parity is the upper byte and baud rate is the lower byte
        combined_value = (self.parities[parity] << 8) | self.baud_rates[baud_rate]

        try:
            # Write the combined value to the register 0x0001
            # Using function code 0x06 (preset single register)
            write_result = self.client.write_register(0x0001, combined_value, self.unit_id)
            #### HERE You have to reset your connexion with the good parameters. Becarfull, stop_bit=2 if parity is None 
            return True
        except ModbusException as e:
            print(f"Failed to set baud rate and parity: {e}")
            return False

    def get_device_info(self):
        """
        Retrieve detailed information about the sensor, such as product ID, model, submodel, and various revisions.

        This method reads multiple registers from the sensor and decodes them to extract information like product ID,
        model ID, submodel ID, firmware revisions, hardware revisions, and serial numbers.

        Returns:
            dict: A dictionary containing the sensor's information if successful, None otherwise.

        Example usage:
            sensor = YSIOdoRtuSensor(port='COM3', baudrate=9600, unit_id=1)
            if sensor.connect():
                device_info = sensor.get_device_info()
                if device_info:
                    for key, value in device_info.items():
                        print(f"{key}: {value}")
                else:
                    print("Failed to retrieve device information.")
                sensor.disconnect()
            else:
                print("Failed to connect to the sensor.")
        """
        info = {}
        try:
            response = self.client.read_holding_registers(0x1000, 17, self.unit_id)
            if response.isError():
                raise ValueError("Error reading device information registers")
                
            info['product_id'] = BinaryPayloadDecoder.fromRegisters(response.registers[0:1], byteorder=Endian.BIG).decode_16bit_uint()
            info['model_id'] = BinaryPayloadDecoder.fromRegisters(response.registers[1:2], byteorder=Endian.BIG).decode_16bit_uint()
            info['submodel_id'] = BinaryPayloadDecoder.fromRegisters(response.registers[2:3], byteorder=Endian.BIG).decode_16bit_uint()
            info['firmware_major_revision'] = BinaryPayloadDecoder.fromRegisters(response.registers[3:4], byteorder=Endian.BIG).decode_16bit_uint()
            info['firmware_minor_revision'] = BinaryPayloadDecoder.fromRegisters(response.registers[4:5], byteorder=Endian.BIG).decode_16bit_uint()
            info['firmware_subminor_revision'] = BinaryPayloadDecoder.fromRegisters(response.registers[5:6], byteorder=Endian.BIG).decode_16bit_uint()
            info['hardware_major_revision'] = BinaryPayloadDecoder.fromRegisters(response.registers[6:7], byteorder=Endian.BIG).decode_16bit_uint()
            info['hardware_minor_revision'] = BinaryPayloadDecoder.fromRegisters(response.registers[7:8], byteorder=Endian.BIG).decode_16bit_uint()
            info['manufacturing_serial_number'] = BinaryPayloadDecoder.fromRegisters(response.registers[8:13], byteorder=Endian.BIG).decode_string(10)
            info['printed_circuit_board_serial_number'] = BinaryPayloadDecoder.fromRegisters(response.registers[13:17], byteorder=Endian.BIG).decode_string(8)

            return info
            
        except Exception as e:
            print(f"Error retrieving device info: {e}")
            return None
                     
    def get_data(self):
        """
        Retrieve a comprehensive set of sensor readings in a single Modbus request.

        This method reads multiple input registers from the sensor and decodes them to extract a variety of measurements,
        including dissolved oxygen saturation, concentration, temperature, and more. The readings are returned as a 
        dictionary with each key representing a specific type of measurement.

        Returns:
            dict: A dictionary containing key-value pairs of sensor readings. The keys include 'odo_saturation', 
            'odo_concentration', 'odo_local_barometer_compensated', 'temperature', 'ref_temperature', 'time_since_boot', 
            'conductivity', 'specific_conductivity', 'salinity', 'conductivity_nLF', and 'total_dissolved_solids'. 
            Each key's value is the corresponding measurement from the sensor, or None if the reading is unsuccessful.

        Example usage:
            sensor = YSIOdoRtuSensor(port='/dev/ttyUSB0', baudrate=9600, unit_id=1)
            if sensor.connect():
                data = sensor.get_data()
                if data:
                    for key, value in data.items():
                        print(f"{key}: {value}")
                else:
                    print("Failed to retrieve sensor data.")
                sensor.disconnect()
            else:
                print("Failed to connect to the sensor.")

        Raises:
            ValueError: If there is an error in reading from the registers.
        """

        data = {}
        try:
            response = self.client.read_input_registers(0x0000, 24, self.unit_id)
            if response.isError():
                raise ValueError("Error reading device information registers")
                
            data['odo_saturation'] = BinaryPayloadDecoder.fromRegisters(response.registers[0:2], byteorder=Endian.BIG, wordorder=Endian.BIG).decode_32bit_float()
            data['odo_concentration'] = BinaryPayloadDecoder.fromRegisters(response.registers[2:4], byteorder=Endian.BIG, wordorder=Endian.BIG).decode_32bit_float()
            data['odo_local_barometer_compensated'] = BinaryPayloadDecoder.fromRegisters(response.registers[4:8], byteorder=Endian.BIG, wordorder=Endian.BIG).decode_32bit_float()
            data['temperature'] = BinaryPayloadDecoder.fromRegisters(response.registers[8:10], byteorder=Endian.BIG, wordorder=Endian.BIG).decode_32bit_float()
            data['ref_temperature'] = BinaryPayloadDecoder.fromRegisters(response.registers[10:12], byteorder=Endian.BIG, wordorder=Endian.BIG).decode_32bit_float()
            data['time_since_boot'] = BinaryPayloadDecoder.fromRegisters(response.registers[12:14], byteorder=Endian.BIG, wordorder=Endian.BIG).decode_32bit_uint()
            data['conductivity'] = BinaryPayloadDecoder.fromRegisters(response.registers[14:16], byteorder=Endian.BIG, wordorder=Endian.BIG).decode_32bit_float()
            data['specific_conductivity'] = BinaryPayloadDecoder.fromRegisters(response.registers[16:18], byteorder=Endian.BIG, wordorder=Endian.BIG).decode_32bit_float()
            data['salinity'] = BinaryPayloadDecoder.fromRegisters(response.registers[18:20], byteorder=Endian.BIG, wordorder=Endian.BIG).decode_32bit_float()
            data['conductivity _nLF'] = BinaryPayloadDecoder.fromRegisters(response.registers[20:22], byteorder=Endian.BIG, wordorder=Endian.BIG).decode_32bit_float()
            data['total_dissolved_solids'] = BinaryPayloadDecoder.fromRegisters(response.registers[22:24], byteorder=Endian.BIG, wordorder=Endian.BIG).decode_32bit_float()

            return data
            
        except Exception as e:
            print(f"Error retrieving device info: {e}")
            return None

    def get_cap_serial(self):

        try:
            response = self.client.read_holding_registers(0x120, 5, self.unit_id)
            if response.isError():
                raise ValueError("Error reading device information registers")
                
            return BinaryPayloadDecoder.fromRegisters(response.registers, byteorder=Endian.BIG).decode_string(10)

        
            
        except Exception as e:
            print(f"Error retrieving device info: {e}")
            return None

    def odo_factory_reset(self):
        """
        Reset the sensor to its factory calibration settings.

        This method writes a specific value to a register on the sensor to initiate a factory reset.
        This action might revert any custom settings or calibrations that have been applied to the sensor.

        Returns:
            bool: True if the reset was successful, False otherwise.

        Example usage:
            sensor = YSIOdoRtuSensor()
            sensor.connect()
            if sensor.odo_factory_reset():
                print("Sensor has been reset to factory defaults.")
            else:
                print("Failed to reset the sensor.")
            sensor.disconnect()
        """
        try:
            # Function code 0x06 is a preset single register.
            result = self.client.write_register(0x0200, 0x0001, self.unit_id)
            return not result.isError()
        except ModbusException as e:
            print(f"Failed to reset the sensor to factory defaults: {e}")
            return False

    def get_odo_last_calibration_time_and_qc_score(self):
        """
        Retrieve the last calibration time and quality control (QC) score from the sensor.

        This method reads the relevant registers from the sensor to get the time of the last calibration 
        and the QC score associated with it. The calibration time is returned as a Unix timestamp and the 
        QC score is a numerical value representing the quality of the calibration.

        Returns:
            dict: A dictionary containing 'last_calibration_time' as a Unix timestamp and 'qc_score' as an integer.
                  Returns None if there is an error in reading from the registers.

        Example usage:
            sensor = YSIOdoRtuSensor(port='/dev/ttyUSB0', baudrate=9600, unit_id=1)
            if sensor.connect():
                calibration_data = sensor.get_odo_last_calibration_time_and_qc_score()
                if calibration_data:
                    print("Last Calibration Time:", calibration_data['last_calibration_time'])
                    print("QC Score:", calibration_data['qc_score'])
                else:
                    print("Failed to retrieve calibration data.")
                sensor.disconnect()
            else:
                print("Failed to connect to the sensor.")

        Raises:
            ValueError: If there is an error in reading from the registers.
        """
        data = {}
        try:
            response = self.client.read_holding_registers(0x0210, 3, self.unit_id)
            if response.isError():
                raise ValueError("Error reading device information registers")
            data['last_calibration_time'] = BinaryPayloadDecoder.fromRegisters(response.registers[0:2], byteorder=Endian.BIG, wordorder=Endian.BIG).decode_32bit_uint()    
            data['qc_score'] = BinaryPayloadDecoder.fromRegisters(response.registers[2:3], byteorder=Endian.BIG, wordorder=Endian.BIG).decode_16bit_uint()       
            return data
            
        except Exception as e:
            print(f"Error retrieving device info: {e}")
            return None 

    def perform_odo_zero_calibration(self, calibration_time):
        """
        Perform an ODO zero point calibration by writing the calibration time to the sensor.

        This method constructs a payload consisting of a 32-bit unsigned integer for the calibration time. It then writes
        this payload to the appropriate registers on the sensor.

        Args:
            calibration_time (int): The calibration time in seconds since epoch.

        Example usage:
            sensor = YSIOdoRtuSensor(port='/dev/ttyUSB0', baudrate=9600, unit_id=1)
            sensor.connect()
            sensor.perform_odo_zero_calibration(1610000000)
            sensor.disconnect()
        """
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)
        
        # Add the calibration time as a 32-bit unsigned integer
        builder.add_32bit_uint(calibration_time)
        
        # Build the payload
        payload = builder.build()
        try:
            # Write the payload to the sensor
            # Function code 0x10 is 'write multiple registers'
            address = 0x0220  # Starting register address for ODO Zero Calibration Time
            self.client.write_registers(address, payload, skip_encode=True, slave=self.unit_id)
            return True
        except Exception as e:
            print(f"Error setting ODO Zero Calibration Time: {e}")
            return False
        return

    def perform_odo_percent_saturation_calibration(self, calibration_time, barometric_pressure):
        """
        Perform a percent saturation calibration by writing the calibration time and barometric pressure to the sensor.

        This method constructs a payload consisting of a 32-bit unsigned integer for the calibration time and a 32-bit float
        for the barometric pressure. It then writes this payload to the appropriate registers on the sensor.

        Args:
            calibration_time (int): The calibration time in seconds since epoch.
            barometric_pressure (float): The barometric pressure in mmHg at the time of calibration.

        Example usage:
            sensor = YSIOdoRtuSensor(port='/dev/ttyUSB0', baudrate=9600, unit_id=1)
            sensor.connect()
            sensor.perform_odo_percent_saturation_calibration(1610000000, 760.0)
            sensor.disconnect()
        """
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)
        
        # Add the calibration time as a 32-bit unsigned integer
        builder.add_32bit_uint(calibration_time)
        
        # Add the barometric pressure as a 32-bit float
        builder.add_32bit_float(barometric_pressure)
        
        # Build the payload
        payload = builder.build()
        
        # Write the payload to the sensor
        # Function code 0x10 is 'write multiple registers'
        address = 0x0230  # Starting register address as per the provided table
        self.client.write_registers(address, payload, skip_encode=True, slave=self.unit_id)

    def perform_odo_mgL_calibration(self, calibration_time, calibration_value, calibration_salinity):
            """
            Perform an mg/L calibration by writing the calibration time, value, and salinity to the sensor.

            This method constructs a payload consisting of a 32-bit unsigned integer for the calibration time and two 32-bit floats
            for the calibration value and salinity. It then writes this payload to the appropriate registers on the sensor.

            Args:
                calibration_time (int): The calibration time in seconds since epoch.
                calibration_value (float): The calibration value in mg/L.
                calibration_salinity (float): The calibration salinity in parts per thousand (ppt).

            Example usage:
                sensor = YSIOdoRtuSensor(port='/dev/ttyUSB0', baudrate=9600, unit_id=1)
                sensor.connect()
                sensor.perform_odo_mgL_calibration(1610000000, 8.68, 0.5)
                sensor.disconnect()
            """
            builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)
            
            # Add the calibration time as a 32-bit unsigned integer
            builder.add_32bit_uint(calibration_time)
            
            # Add the calibration value and salinity as 32-bit floats
            builder.add_32bit_float(calibration_value)
            builder.add_32bit_float(calibration_salinity)
            
            # Build the payload
            payload = builder.build()
            
            # Write the payload to the sensor
            # Function code 0x10 is 'write multiple registers'
            address = 0x0240  # Starting register address as per the provided table
            self.client.write_registers(address, payload, skip_encode=True, slave=self.unit_id)

    def get_odo_cap_coefficients(self):
        """
        Retrieve the current ODO cap coefficients from the sensor.

        Returns:
            dict: A dictionary containing the ODO cap coefficients if successful, None otherwise.

        Example usage:
            sensor = YSIOdoRtuSensor()
            sensor.connect()
            coefficients = sensor.get_odo_cap_coefficients()
            if coefficients:
                print("ODO Cap Coefficients:", coefficients)
            sensor.disconnect()
        """
        try:
            response = self.client.read_holding_registers(0x0100, 17, slave=self.unit_id)
            if response.isError():
                raise ValueError("Error reading ODO cap coefficients")

            decoder = BinaryPayloadDecoder.fromRegisters(response.registers, byteorder=Endian.BIG)
            coefficients = {
                'K1': decoder.decode_32bit_float(),
                'K2': decoder.decode_32bit_float(),
                'K3': decoder.decode_32bit_float(),
                'K4': decoder.decode_32bit_float(),
                'K5': decoder.decode_32bit_float(),
                'K6': decoder.decode_32bit_float(),
                'K7': decoder.decode_32bit_float(),
                'KC': decoder.decode_16bit_uint(),
                'Cap Replacement Time': decoder.decode_32bit_uint()
            }
            return coefficients
        except Exception as e:
            print(f"Error retrieving ODO cap coefficients: {e}")
            return None

    def set_odo_cap_coefficients(self, coefficients):
        """
        Set new ODO cap coefficients on the sensor.

        Args:
            coefficients (dict): A dictionary containing the ODO cap coefficients to set.

        Example usage:
            sensor = YSIOdoRtuSensor()
            sensor.connect()
            new_coefficients = {
                'K1': 1.0,
                'K2': 0.0,
                'K3': -0.1,
                'K4': 0.01,
                'K5': -0.001,
                'K6': 0.0001,
                'K7': -0.00001,
                'KC': 1,
                'Cap Replacement Time': 1610000000
            }
            success = sensor.set_odo_cap_coefficients(new_coefficients)
            if success:
                print("ODO Cap Coefficients have been updated.")
            sensor.disconnect()
        """
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG)
        for key in ['K1', 'K2', 'K3', 'K4', 'K5', 'K6', 'K7', 'KC', 'Cap Replacement Time']:
            if key == 'KC':  # KC is a 16-bit value
                builder.add_16bit_uint(coefficients[key])
            else:  # The rest are 32-bit floats
                builder.add_32bit_float(coefficients[key])

        payload = builder.build()
        try:
            # Write the payload to the sensor
            # Function code 0x10 is 'write multiple registers'
            address = 0x0100  # Starting register address for ODO Cap Coefficients
            self.client.write_registers(address, payload, skip_encode=True, slave=self.unit_id)
            return True
        except Exception as e:
            print(f"Error setting ODO cap coefficients: {e}")
            return False

    def conductivity_factory_reset(self):
        """
        Reset the sensor to its factory calibration settings.

        This method writes a specific value to a register on the sensor to initiate a factory reset.
        This action might revert any custom settings or calibrations that have been applied to the sensor.

        Returns:
            bool: True if the reset was successful, False otherwise.

        Example usage:
            sensor = YSIOdoRtuSensor()
            sensor.connect()
            if sensor.conductivity_factory_reset():
                print("Sensor has been reset to factory defaults.")
            else:
                print("Failed to reset the sensor.")
            sensor.disconnect()
        """
        try:
            # Function code 0x06 is a preset single register.
            result = self.client.write_register(0x0300, 0x0001, self.unit_id)
            return not result.isError()
        except ModbusException as e:
            print(f"Failed to reset the sensor to factory defaults: {e}")
            return False

    def get_conductivity_last_calibration_time_and_qc_score(self):
        """
        Retrieve the last calibration time and quality control (QC) score from the sensor.

        This method reads the relevant registers from the sensor to get the time of the last calibration 
        and the QC score associated with it. The calibration time is returned as a Unix timestamp and the 
        QC score is a numerical value representing the quality of the calibration.

        Returns:
            dict: A dictionary containing 'last_calibration_time' as a Unix timestamp and 'qc_score' as an integer.
                  Returns None if there is an error in reading from the registers.

        Example usage:
            sensor = YSIOdoRtuSensor(port='/dev/ttyUSB0', baudrate=9600, unit_id=1)
            if sensor.connect():
                calibration_data = sensor.get_conductivity_last_calibration_time_and_qc_score()
                if calibration_data:
                    print("Last Calibration Time:", calibration_data['last_calibration_time'])
                    print("QC Score:", calibration_data['qc_score'])
                else:
                    print("Failed to retrieve calibration data.")
                sensor.disconnect()
            else:
                print("Failed to connect to the sensor.")

        Raises:
            ValueError: If there is an error in reading from the registers.
        """
        data = {}
        try:
            response = self.client.read_holding_registers(0x0310, 3, self.unit_id)
            if response.isError():
                raise ValueError("Error reading device information registers")
            data['last_calibration_time'] = BinaryPayloadDecoder.fromRegisters(response.registers[0:2], byteorder=Endian.BIG, wordorder=Endian.BIG).decode_32bit_uint()    
            data['qc_score'] = BinaryPayloadDecoder.fromRegisters(response.registers[2:3], byteorder=Endian.BIG, wordorder=Endian.BIG).decode_16bit_uint()       
            return data
            
        except Exception as e:
            print(f"Error retrieving device info: {e}")
            return None 

    def perform_us_cm_calibration(self, calibration_time, calibration_value):
        """
        Perform a µS/cm calibration by writing the calibration time and value.

        Args:
            calibration_time (int): The Unix timestamp of the calibration time in seconds.
            calibration_value (float): The conductivity value in µS/cm to be used for calibration.

        Example usage:
            sensor = YSIOdoRtuSensor()
            sensor.connect()
            sensor.perform_us_cm_calibration(1610000000, 1413.0)  # example values
            sensor.disconnect()
        """
        # Create a binary payload with the calibration time and value
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)
        builder.add_32bit_uint(calibration_time)
        builder.add_32bit_float(calibration_value)
        
        # Build the payload
        payload = builder.to_registers()

        try:
            # Write the calibration time and value to the sensor
            # Function code 0x10 is 'write multiple registers'
            self.client.write_registers(0x0320, payload, slave=self.unit_id)
            print("µS/cm calibration performed successfully.")
        except Exception as e:
            print(f"Failed to perform µS/cm calibration: {e}")

    def perform_salinity_ppt_calibration(self, calibration_time, calibration_value):
        """
        Perform a salinity ppt calibration by writing the calibration time and value.

        Args:
            calibration_time (int): The Unix timestamp of the calibration time in seconds.
            calibration_value (float): The salinity value in ppt to be used for calibration.

        Example usage:
            sensor = YSIOdoRtuSensor()
            sensor.connect()
            sensor.perform_salinity_ppt_calibration(1610000000, 35.0)  # example values
            sensor.disconnect()
        """
        # Create a binary payload with the calibration time and value
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)
        builder.add_32bit_uint(calibration_time)
        builder.add_32bit_float(calibration_value)

        # Build the payload
        payload = builder.to_registers()

        try:
            # Write the calibration time and value to the sensor
            # Function code 0x10 is 'write multiple registers'
            self.client.write_registers(0x0330, payload, slave=self.unit_id)
            print("Salinity ppt calibration performed successfully.")
        except Exception as e:
            print(f"Failed to perform salinity ppt calibration: {e}")

    def perform_specific_conductance_calibration(self, calibration_time, calibration_value):
        """
        Perform specific conductance µS/cm calibration by writing the calibration time and value.

        Args:
            calibration_time (int): The calibration time in seconds.
            calibration_value (float): The specific conductance value in µS/cm.

        Example:
            # Example to perform specific conductance calibration
            sensor.perform_specific_conductance_calibration(1610000000, 1500.0)
        """
        # Ensure connection
        assert self.connect(), "Failed to connect to the sensor"

        # Build the payload
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)
        builder.add_32bit_uint(calibration_time)
        builder.add_32bit_float(calibration_value)
        payload = builder.to_registers()

        # Write the calibration data
        result = self.client.write_registers(0x0340, payload, slave=self.unit_id)
        if result.isError():
            raise Exception("Specific conductance calibration failed.")
        else:
            print("Specific conductance calibration successful.")

    def perform_nlf_conductivity_calibration(self, calibration_time, calibration_value):
        """
        Perform non-linear function conductivity calibration by writing the calibration time and value.

        Args:
            calibration_time (int): The calibration time in seconds.
            calibration_value (float): The nLF conductivity value in µS/cm.

        Example:
            # Example to perform nLF conductivity calibration
            sensor.perform_nlf_conductivity_calibration(1610000000, 1.5)
        """
        # Ensure connection
        assert self.connect(), "Failed to connect to the sensor"

        # Build the payload
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)
        builder.add_32bit_uint(calibration_time)
        builder.add_32bit_float(calibration_value)
        payload = builder.to_registers()

        # Write the calibration data
        result = self.client.write_registers(0x0350, payload, slave=self.unit_id)
        if result.isError():
            raise Exception("nLF conductivity calibration failed.")
        else:
            print("nLF conductivity calibration successful.")
            
            
    def get_user_tds_coefficient(self):
        """
        Retrieve the user-defined TDS coefficient from the sensor.
        """
        response = self.client.read_holding_registers(0x0500, 2, slave=self.unit_id)
        if response.isError():
            raise Exception("Failed to read TDS coefficient")
        decoder = BinaryPayloadDecoder.fromRegisters(response.registers, byteorder=Endian.BIG)
        return decoder.decode_32bit_float()

    def set_user_tds_coefficient(self, tds_coefficient):
        """
        Set the user-defined TDS coefficient in the sensor.

        Args:
            tds_coefficient (float): The TDS coefficient to set.
        """
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG)
        builder.add_32bit_float(tds_coefficient)
        payload = builder.to_registers()
        result = self.client.write_registers(0x0500, payload, slave=self.unit_id)
        if result.isError():
            raise Exception("Failed to set TDS coefficient")

    def get_user_temperature_reference(self):
        """
        Retrieve the user-defined temperature reference for specific conductance calculation from the sensor.
        """
        response = self.client.read_holding_registers(0x0502, 2, slave=self.unit_id)
        if response.isError():
            raise Exception("Failed to read temperature reference")
        decoder = BinaryPayloadDecoder.fromRegisters(response.registers, byteorder=Endian.BIG)
        return decoder.decode_32bit_float()

    def set_user_temperature_reference(self, temperature_reference):
        """
        Set the user-defined temperature reference for specific conductance calculation in the sensor.

        Args:
            temperature_reference (float): The temperature reference to set.
        """
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG)
        builder.add_32bit_float(temperature_reference)
        payload = builder.to_registers()
        result = self.client.write_registers(0x0502, payload, slave=self.unit_id)
        if result.isError():
            raise Exception("Failed to set temperature reference")
            
    def get_user_temperature_coefficient(self):
        """
        Retrieve the user-defined temperature coefficient for specific conductance from the sensor.
        """
        response = self.client.read_holding_registers(0x0504, 2, slave=self.unit_id)
        if response.isError():
            # Handle error appropriately.
            raise Exception("Failed to read temperature coefficient")
        decoder = BinaryPayloadDecoder.fromRegisters(response.registers, byteorder=Endian.BIG)
        temperature_coefficient = decoder.decode_32bit_float()
        return temperature_coefficient

    def set_user_temperature_coefficient(self, temperature_coefficient):
        """
        Set the user-defined temperature coefficient for specific conductance in the sensor.

        Args:
            temperature_coefficient (float): The temperature coefficient to set.
        """
        builder = BinaryPayloadBuilder(byteorder=Endian.BIG)
        builder.add_32bit_float(temperature_coefficient)
        payload = builder.to_registers()
        result = self.client.write_registers(0x0504, payload, slave=self.unit_id)
        if result.isError():
            # Handle error appropriately.
            raise Exception("Failed to set temperature coefficient")