from agpumps import DualArray
import time

config_list = [{'port':'COM13', 'unit' : 0}, {'port':'COM16', 'unit' : 1}]
#config_list = [{'port':'COM13', 'unit' : 0}]

with DualArray(config_list, False) as a:
    a.ensure_empty()
    for bacteria_pump in range(6,10):
        print(bacteria_pump)
        time.sleep(5)
        a.simultaneous_pump({bacteria_pump:75, 5:80}, 60)    
#a = DualArray(config_list)
#.pump_by_number(11, 50, speed = 'low')


#a.array_list[1].write_register(105, 90, unit = array_list[1].unit)
#a = AgrowPumps('COM15',0)

#    addresses = [100,101,102,103,104,105]
#addresses = [100]
#    while True:
        #b = a.modbus.read_holding_registers(106, 1, unit = a.unit).registers[0]
#        for address in addresses:
#            if address == 105:
#                b.pump_by_address(address, 100, speed = "high")
#            else:
#                b.pump_by_address(address, 5, speed = "high")
            #time.sleep(1)
            #a.ensure_set_speed(100, 0)
