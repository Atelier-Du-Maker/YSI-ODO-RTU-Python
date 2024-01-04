# YSI ODO RTU Python Interface

This Python package provides an interface for communicating with the YSI ODO RTU sensor via the Modbus RTU protocol.

Development of this package was funded by [INRAE](https://www.inrae.fr/) (REVERSAAL research unit, Villeurbanne, France).

## Installation

You can install the YSI ODO RTU Python interface using either `git` or `pip`.

### Using git

To install using `git`, clone the repository and install the package manually:

```shell
git clone https://github.com/Atelier-Du-Maker/YSI-ODO-RTU-Python
cd YSI-ODO-RTU-Python
python3 setup.py install
```
### Using pip

To install using pip, simply run the following command:
```shell
pip install git+https://github.com/Atelier-Du-Maker/YSI-ODO-RTU-Python
```

## Usage

After installation, you can import the module in your Python projects:
```shell
from ODO_sensor_lib import YSIOdoRtuSensor
```

Create an instance of the sensor with the appropriate configuration, and use the provided methods to interact with the sensor.
Contributing

## Contributing
Contributions to the project are welcome. Please ensure that any pull requests or issues are made through the GitHub repository.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

