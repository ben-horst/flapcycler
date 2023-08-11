import smbus2 as smbus

class I2CInterface:
    """Generic I2C interface with read and write"""
    def __init__(self, bus):
        self.bus = smbus.SMBus(bus)

    def write_byte_data(self, i2c_addr, register, data_byte):
        self.bus.write_byte_data(i2c_addr, register, data_byte)

    def read_byte_data(self, i2c_addr, register):
        return self.bus.read_byte_data(i2c_addr, register)
    
    def read_block_data(self, i2c_addr, register, data_bytes):
        return self.bus.read_i2c_block_data(i2c_addr, register, data_bytes)

class DPSensor_4525(I2CInterface):
    DEFAULT_ADDRESS = 0x28

    def __init__(self, address=DEFAULT_ADDRESS):
        super().__init__(1)     #use I2C bus number 1
        self.address = address

    @property
    def connected(self):
        return self.connected
    
    def measure(self):
        try:
            resp = self.read_block_data(self.address, 0, 1)
            self._connected = True
        except:
            self._connected = False
            #print("cannot communicate to 4525 module")

    @property
    def pressure_pa(self): 
        #pressure in pascals
        try:
            raw_data = self.read_block_data(self.address, 0, 4)
            self._connected = True
            dp_raw = ((raw_data[0]<<8) + raw_data[1]) & 0x3FFF
            self._pressure_p = raw_to_pressure_pa(dp_raw)
        except:
            self._connected = False
            #print("cannot communicate to 4525 module")
            self._pressure_p = 0
        return self._pressure_p

    @property
    def temperature_c(self):
        #temperature in degrees C
        try:
            raw_data = self.read_block_data(self.address, 0, 4)
            self._connected = True
            temp_raw = (((raw_data[2]<<8) + raw_data[3]) & 0xFFE0) >> 5
            self._temperature_c = raw_to_temperature_c(temp_raw)
        except:
            self._connected = False
            #print("cannot communicate to 4525 module")
            self._temperature_c = 0
        return  self._temperature_c

def raw_to_pressure_pa(raw_14bit):
    P_MAX = 6894.757  #pascals
    #P_MIN = -P_MAX
    MAX_ADC = 2**14 - 1
    #return -((raw_14bit - 0.1 * MAX_ADC) * (P_MAX - P_MIN) / (0.8 * MAX_ADC) + P_MIN)
    return P_MAX * (raw_14bit - MAX_ADC/2) / (0.4 * MAX_ADC)

def raw_to_temperature_c(raw_11bit):
    MAX_ADC = 2**11 - 1
    TEMP_SPAN = 200
    TEMP_OFFSET = 50
    return (((TEMP_SPAN * raw_11bit) / MAX_ADC) - TEMP_OFFSET)