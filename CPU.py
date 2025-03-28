

import ctypes

Byte = ctypes.c_ubyte

class Registers8bit:
    def __init__(self):
        self._B = 0
        self._C = 0
        self._D = 0
        self._E = 0
        self._H = 0
        self._L = 0
        self._HL = 0
        self._A = 0
    
    def write(self,byte):
        self.B = byte & 0x1
        self.C = (byte & 0x2) >>  1
        self.D = (byte & 0x4) >>  2
        self.E = (byte & 0x8) >>  3
        self.H = (byte & 0x10) >>  4
        self.L = (byte & 0x20) >>  5
        self.HL = (byte & 0x40) >>  6
        self.A = (byte & 0x80) >>  7
    
    def reset(self):
        self.write(0x00)

    def read(self):
        outByte = self.A << 7 | self.HL << 6 | self.L << 5 | self.H << 4 | self.E << 3 | self.D << 2 | self.C << 1 | self.B
        print(f"{outByte}")
        return outByte
    
    @property    
    def A(self):
        return self._A
    
    @A.setter
    def A(self, bit):
        if not (bit == 1 or bit == 0):
            raise ValueError(f"bit = {bit}: Bit must be [0|1]")
        self._A = bit

    @property
    def B(self):
        return self._B
    
    @B.setter
    def B(self, bit):
        if not (bit == 1 or bit == 0):
            raise ValueError(f"bit = {bit}: Bit must be [0|1]")
        self._B = bit

    @property    
    def C(self):
        return self._C
    @C.setter
    def C(self, bit):
        if not (bit == 1 or bit == 0):
            raise ValueError(f"bit = {bit}: Bit must be [0|1]")
        self._C = bit

    @property    
    def D(self):
        return self._D
    @D.setter
    def D(self, bit):
        if not (bit == 1 or bit == 0):
            raise ValueError(f"bit = {bit}: Bit must be [0|1]")
        self._D = bit

    @property    
    def E(self):
        return self._E
    @E.setter
    def E(self, bit):
        if not (bit == 1 or bit == 0):
            raise ValueError(f"bit = {bit}: Bit must be [0|1]")
        self._E = bit
    
    @property    
    def H(self):
        return self._H
    @H.setter
    def H(self, bit):
        if not (bit == 1 or bit == 0):
            raise ValueError(f"bit = {bit}: Bit must be [0|1]")
        self._H = bit

    @property   
    def L(self):
        return self._L
    @L.setter
    def L(self, bit):
        if not (bit == 1 or bit == 0):
            raise ValueError(f"bit = {bit}: Bit must be [0|1]")
        self._L = bit

    @property    
    def HL(self):
        return self._HL
    @HL.setter
    def HL(self, bit):
        if not (bit == 1 or bit == 0):
            raise ValueError(f"bit = {bit}: Bit must be [0|1]")
        self._HL = bit

class CPU:
    def __init__(self):
        # Need to define op codes
        # 8 bit register 
        # self.reg_8bit[] 
        pass