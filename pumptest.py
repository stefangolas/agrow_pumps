from agpumps import DualArray
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.exceptions import ModbusIOException
import IPython
import time



config_list = [{'port':'COM13', 'unit' : 0}, {'port':'COM16', 'unit' : 1}]

speed_dict = {2:100, 11:100}

simulating = False
i= 0
with DualArray(config_list, simulating) as a:
    a.pump_by_number(pump = 4, volume = 28, speed = 'high') #Water
    a.ensure_empty()
