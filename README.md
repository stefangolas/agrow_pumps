# Agrow Pumps
Interface for Agrowtek peristaltic pump arrays

### Example

```python
from agpumps import DualArray

config_list = [{'port':'COM13', 'unit' : 0}, {'port':'COM16', 'unit' : 1}]

speed_dict = {2:100, 11:100}

simulating = False
i= 0
with DualArray(config_list, simulating) as a:
    a.pump_by_number(pump = 4, volume = 28, speed = 'high') #Water
    a.ensure_empty()

```

### How to Use

**DualArray** implements behavior for a specific PRANCE setup with bacteria culture and other sources.
**MultiArrayHandler** is a general interface to a set of multiple AgrowTek modbus pump arrays.

**Make sure to set a safe timeout value in the pump array register table.<br>  
Using automated pumps improperly can damage equipment.**<br>  

### Configuration

<img src="https://github.com/stefangolas/agrow_pumps/blob/master/assets/docs/compressed_air_diagram.png" width="700">


# Pump Setup Instructions

This guide is to set up the AD6i dosing pump array from Agrowtek. The pump array should ship with the AgrowLINK LX1 bridge device.

To install the pump array connect the USB cable from the LX1 device to your PC COM port and the ethernet cable from the LX1 device to the pump array as shown.

![alt text](https://github.com/Golaszewski/PRANCE/blob/main/perma_pump/images/lx1%20connection.png)

Once the pump is set up, go to the [Agrowtek downloads page](https://www.agrowtek.com/index.php/software), scroll to Link Modules, and download both the AgrowLINK and ModLINK utilities. Install AgrowLINK and verify that the pump array is connected with the Read Status button. Take note of the COM port identified near the top of the window.

Next, open the ModLINK utility. Verify that the default settings are correct (Data Bits: 8, Parity: Even, Stop Bits: One, Baud Rate: 115200) in the ModLINK Settings tab. Then go to the slave devices tab, set an address in the Device Address section, and click Set. It is not important what the address is, except that each pump array must have a unique address. This step is necessary for operating the pumps from the Python interface provided.

![alt text](https://github.com/Golaszewski/PRANCE/blob/main/perma_pump/images/ModLINK.png)

Now you can import the pump interface into a script.


If you get a time-out error while setting up the pumps, power cycle the array by unplugging it and then reset the address in ModLINK. This might take a few tries.
