# -*- coding: utf-8 -*-
"""
Created on Mon Mar 29 13:32:51 2021

@author: stefa
"""

import serial
import logging
import time
from contextlib import ExitStack
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.exceptions import ModbusIOException
import threading

import logging


from pymodbus.constants import Defaults
Defaults.RetryOnEmpty = True

    
class AgrowModbusInterface():
    
    """
    AgrowModbusInterface is a class that allows users to control pumps through Modbus communication.

    Attributes:
        modbus_pump_map (dict): Maps pump numbers to Modbus registers.
        port (str): Port that the Modbus connection will be made through.
        unit (int): Modbus slave unit that the connection will be made to.
        activecontext (bool): Indicates whether the class is being used within a context manager.
        modbus (ModbusClient): Instance of the ModbusClient class used for communication.

    """
    
    modbus_pump_map = {
        0:100,
        1:101,
        2:102,
        3:103,
        4:104,
        5:105,
    } 
    

    
    def __enter__(self):
        
        self.activecontext = True
        return self
    
    def __init__(self, port, unit):
        self.port = port
        self.unit = unit
        self.activecontext = False
        mb = self.connect(self.port)
        self.keep_alive_thread()
        
    
    def keep_alive_thread(self):
        
        """
        keep_alive_thread(self):

            This method creates a daemon thread that sends a Modbus request every 25 seconds to keep the connection alive.

        """
       
        def keep_alive():
            while True:
                time.sleep(25)
                self.modbus.read_holding_registers(0, 1, unit = self.unit)
                
        
        thread = threading.Thread(target = keep_alive, daemon=True)
        thread.start()
    
    def ensure_connection(self):
        try:
            response = self.modbus.read_holding_registers(0, 1, unit = self.unit).registers[0]
            print('Response is ' + str(response))
        except:
            raise ConnectionFailed("One of your pump arrays failed to connect")

            
    def connect(self, port):
        
        """
        connect(self, port):

            This method connects to the Modbus slave unit.

            Attributes:
                self: The AgrowModbusInterface object.
                port (str): Port that the Modbus connection will be made through.

            Returns:
                self.modbus (ModbusClient): Instance of the ModbusClient class used for communication.

        """
        self.modbus = ModbusClient(method = 'rtu', port = port, baudrate = 115200, timeout = 1, stopbits = 1, bytesize = 8, parity = 'E')
        response = self.modbus.connect()
        return self.modbus

    def pump_by_address(self, address, volume, speed='low'):
        
        if not self.activecontext:
            raise Exception("Pump must be initialized in a context manager to ensure safe operation!")
        
        try:
            assert(address in range(100,106))
        except:
            raise ValueError("Pump address out of range")
        
        if speed == 'low':
            pumptime = volume/1.2
            power = 80
    
        if speed == 'high':
            pumptime = volume/2.2
            power = 100
        
        self.ensure_set_speed(address = address, set_speed = power)
        time.sleep(pumptime)
        self.ensure_set_speed(address = address, set_speed = 0)
    
    def ensure_set_speed(self, address, set_speed):
        self.modbus.write_register(address, set_speed, unit = self.unit)

    
    def read_register(self, address):
        register_return = self.modbus.read_holding_registers(address, 1, unit = self.unit)
        
        while True:
            if type(register_return) != ModbusIOException:
                return register_return.registers[0]
            else:
                print("Exception caught on read register, trying again")
                register_return = self.modbus.read_holding_registers(address, 1, unit = self.unit)
                pass
            
    def pump_by_number(self, pump, volume, speed):
        self.pump_by_address(self.modbus_pump_map[pump], volume, speed = speed)
    
    def shutdown_all_pumps(self):
        print("Engaging shutdown routine")
        for pump in self.modbus_pump_map:
            address = self.modbus_pump_map[pump]
            self.modbus.write_register(address, 0, unit = self.unit)
    
    def __exit__(self, type, value, tb):
        while True:
            try:
                self.shutdown_all_pumps()
                break
            except:
                print("Caught exception on shutdown routine. STOP TOUCHING KEYBOARD!!")
                time.sleep(0.1)
                pass
        print("Safely exited pump program")
        

class MultiArrayHandler:


    def __init__(self, config_list, simulating):
        self.activecontext = False
        self.config_list = config_list
        self.array_list = []
        self.simulating = simulating
        
        if self.simulating:
            return
        
        for array in self.config_list:
            self.array_list.append(self.instantiate_array(array))
    
        self.dual_array_unit_map = {address:(address//6, address%6) for address in range(6*len(self.array_list))}
        
        self.speed_calibration_dict = {address: 1.0 for address in range(6*len(self.array_list))}
        
        for array in self.array_list:
            array.ensure_connection()
        
    def instantiate_array(self, config_dict):
        port = config_dict['port']
        unit = config_dict['unit']
        pump = AgrowModbusInterface(port, unit)
        return pump
    
    def pump_by_number(self, pump, volume, speed = 'low'):
        if self.simulating:
            return
        array_id, pump_id = self.dual_array_unit_map[pump]
        self.array_list[array_id].pump_by_number(pump_id, volume*self.speed_calibration_dict[pump], speed)
            
    def disable(self):
        self.simulating = True
    
    def __enter__(self):
        self.activecontext = True
        with ExitStack() as stack:
            for array in self.array_list:
                stack.enter_context(array)
            self._stack = stack.pop_all()
        return self
    
    def __exit__(self, exc_type, exc, traceback):
        self._stack.__exit__(exc_type, exc, traceback)


class DualArray(MultiArrayHandler):
       
    bacteria_pump_map={'0':6, '1':7, '2':8, '3':9, '4':10}
    
    empirical_speed_calibration = {
        6:1.0,
        7:0.833,
        8:0.8,
        9:0.77,
    }
    
    def __init__(self, *args):
        super().__init__(*args)
        self.simulating = args[1]
        if self.simulating:
            return
        self.speed_calibration_dict.update(self.empirical_speed_calibration)

    def simultaneous_pump(self, pump_speeds_dict, pump_time):
        if self.simulating:
            return
    
        for pump in pump_speeds_dict:
            array_id, pump_id = self.dual_array_unit_map[pump]
            array_int = self.array_list[array_id]
            res = array_int.modbus.write_register(array_int.modbus_pump_map[pump_id], pump_speeds_dict[pump], unit = array_int.unit)
        
        time.sleep(pump_time)
        
        for pump in pump_speeds_dict:
            array_id, pump_id = self.dual_array_unit_map[pump]
            array_int = self.array_list[array_id]
            res = array_int.modbus.write_register(array_int.modbus_pump_map[pump_id], 0, unit = array_int.unit)
    
    def ensure_empty(self):
        self.pump_by_number(pump = 5, volume = 40, speed = 'high') #Waste
        print("Empty finished")
    
    def bleach_clean(self):
        self.ensure_empty()
        self.pump_by_number(pump = 3, volume = 24, speed = 'high') #Bleach #TODO not filling enough
        self.ensure_empty()
        self.pump_by_number(pump = 4, volume = 28, speed = 'high') #Water
        #time.sleep(50)
        self.ensure_empty()
        self.pump_by_number(pump = 4, volume = 28, speed = 'high') #Water
        #time.sleep(50)
        self.ensure_empty()
        self.pump_by_number(pump = 4, volume = 28, speed = 'high') #Water
        #time.sleep(50)
        self.ensure_empty()

    
    def air_purge_bacteria_line(self, culture_id):
        select_pump = self.bacteria_pump_map[culture_id]
        speed_dict = {select_pump:80, 2:100}
        self.simultaneous_pump(speed_dict, 15)

    
    def refill_culture(self, culture_id, add_culture_vol):
        self.ensure_empty()
        if culture_id not in self.bacteria_pump_map:
            raise Exception("ID not found in bacteria pump map")
        select_pump = self.bacteria_pump_map[culture_id]
        self.pump_by_number(pump = select_pump, volume = add_culture_vol, speed = 'low')
        self.air_purge_bacteria_line(culture_id)

    
    def rinse_out(self, rinse_cycles=3):
        
        for _ in range(rinse_cycles):
            self.ensure_empty()
            self.pump_by_number(pump=4, volume=28, speed = 'high')
        self.ensure_empty()    


class ConnectionFailed(Exception):
    print("One of your pumps failed to connect")
    pass
        
