import time
import dp_multi
from gpiozero import PWMOutputDevice
from csv_logger import CsvLogger
from datetime import datetime
import threading


fan = PWMOutputDevice(7, initial_value=0, frequency=2000)

def set_fanspeed(val)  : #value from 0 to 100
    fan.value = (100 - val) / 100

fanspeed = 0
set_fanspeed(fanspeed)
print('waiting 10 s to zero sensors')
time.sleep(10)

dp = dp_multi.DP_Multi(5)
time.sleep(3)
#five pressure sensors
#0 - inlet flap diff pressure
#1 - outlet flap diff pressure
#2 - pitot tube at pack inlet --> tube ID = 52 mm
#3 - pitot tube at pack outlet  --> tube ID = 100 mm
#4 - pressure of pack relative to ambient

#measurements to log
values = {
    'dp_inlet_flap_Pa': 0,
    'dp_outlet_flap_Pa': 0,
    'windspeed_pre_pack_mps': 0,
    'windspeed_post_pack_mps': 0,
    'pack_internal_pressure_Pa': 0
}

now_dt = datetime.now()
now = now_dt.strftime("%d%m%Y_%H%M%S")
start_sec = now_dt.timestamp()
logfile = f'flap_log_{now}.csv'
fmt = f'%(message)s'
header = ['time (ms)',
          'fan duty',
          'inlet flap pressure drop (Pa)',
          'outlet flap pressure drop (Pa)',
          'pre-pack windspeed (m/s)',
          'post-pack windspeed (m/s)',
          'pack internal pressure (Pa)'
          ]
logger = CsvLogger(filename=logfile, fmt=fmt, header=header)


def measure_all_sensors():
    values["dp_inlet_flap_Pa"] = dp.measure_pressure(0)
    values["dp_outlet_flap_Pa"] = dp.measure_pressure(1)
    values["windspeed_pre_pack_mps"] = dp.measure_windspeed(2)
    values["windspeed_post_pack_mps"] = dp.measure_windspeed(3)
    values["pack_internal_pressure_Pa"] = dp.measure_pressure(4)
    
def log_newline():
    now_dt = datetime.now()
    now_sec = now_dt.timestamp()
    secs = now_sec - start_sec
    vals = [secs,
            fanspeed,
            values["dp_inlet_flap_Pa"],
            values["dp_outlet_flap_Pa"],
            values["windspeed_pre_pack_mps"],
            values["windspeed_post_pack_mps"],
            values["pack_internal_pressure_Pa"]
            ]
    logger.info(vals)

def print_vals():
    print("fan duty", fanspeed, "inlet pressure", values["dp_inlet_flap_Pa"], "outlet pressure", values["dp_outlet_flap_Pa"], 'internal pressure', values['pack_internal_pressure_Pa'])

ascending = True
def progress_fanspeed(increment, min, max):     #ramps up fanspeed every time it's called. Once it hits maximum, it steps back down until minimum
    global fanspeed
    global ascending
    if (ascending):
        if (fanspeed == 0):     #ascending and zero only happens the very first time
            fanspeed = min
        elif (fanspeed < max):
            fanspeed += increment   
        if (fanspeed >= max):
            fanspeed = max
            ascending = False
        set_fanspeed(fanspeed)
    elif (not ascending):
        if (fanspeed > min):
            fanspeed -= increment
        elif (fanspeed <= min):
            fanspeed = 0
        set_fanspeed(fanspeed)

print_thread = threading.Thread(target=print_vals)

def measure_recurring():
    measure_all_sensors()
    log_newline()  
    threading.Timer(0.1, measure_recurring).start()

def update_fan_recurring():
    progress_fanspeed(0.1, 30, 100)
    threading.Timer(0.2, update_fan_recurring).start()

def print_recurring():
    print_vals()
    threading.Timer(2, print_recurring).start()

measure_recurring()
update_fan_recurring()
print_recurring()