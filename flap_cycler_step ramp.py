import time
import dp_multi
from gpiozero import PWMOutputDevice
from csv_logger import CsvLogger
from datetime import datetime


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

fanspeed = 35
ascending = True

while(True):
    measure_all_sensors()
    print("fan duty", fanspeed, "inlet pressure", values["dp_inlet_flap_Pa"], "outlet pressure", values["dp_outlet_flap_Pa"], 'internal pressure', values['pack_internal_pressure_Pa'])
    log_newline()
    if (ascending):
        if (fanspeed < 100):
            fanspeed += 5
            set_fanspeed(fanspeed)
        elif (fanspeed >= 100):
            fanspeed = 100
            set_fanspeed(fanspeed)
            ascending = False
    if (not ascending):
        if (fanspeed > 20):
            fanspeed -= 5
            set_fanspeed(fanspeed)
        elif (fanspeed <= 20):
            fanspeed = 0
            set_fanspeed(fanspeed)
            
    time.sleep(10)
    
