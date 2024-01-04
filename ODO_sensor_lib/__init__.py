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
       Example: sensor = YSIOdoRtuSensor(port='COM3', baudrate=9600)
    
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
__version__ = "0.0.1"
from .core import YSIOdoRtuSensor