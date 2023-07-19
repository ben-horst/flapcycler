import time
import dp_multi

dp = dp_multi.DP_Multi(2)

while(True):
    print(dp.measure_pressure(0))
    #print(dp.measure_pressure(1))
    time.sleep(1)

