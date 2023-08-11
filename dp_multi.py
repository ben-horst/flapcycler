from diff_pressure_4525 import DPSensor_4525
from qwiic import QwiicTCA9548A
import math

sens = DPSensor_4525()
mux = QwiicTCA9548A()
AIR_DENSITY = 1.225     #kg/m^3

class DP_Multi():
    def __init__(self, num_channels):
        self.num_channels = num_channels
        self.p_offset = [0] * self.num_channels
        for channel in range(self.num_channels):
            self.p_offset[channel] = -1 * self.measure_pressure(channel)
        print(self.p_offset)
        mux.disable_channels([0,1,2,3,4,5,6,7])

    def measure(self, channel):
        mux.enable_channels(channel)
        sens.measure()
        mux.disable_channels(channel)

    def measure_pressure(self, channel):
        mux.enable_channels(channel)
        p = sens.pressure_pa + self.p_offset[channel]
        mux.disable_channels(channel)
        return p

    def measure_temp(self, channel):
        mux.enable_channels(channel)
        t = sens.temperature_c
        mux.disable_channels(channel)
        return t

    def measure_windspeed(self, channel):
        p = self.measure_pressure(channel)
        return math.sqrt(2 * (abs(p) / AIR_DENSITY))
        