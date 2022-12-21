from agpumps import DualArray
import time

config_list = [{'port':'COM15', 'unit' : 0}, {'port':'COM14', 'unit' : 1}]

with DualArray(config_list) as a:
    for array in a.array_list:
        array.shutdown_all_pumps()
    