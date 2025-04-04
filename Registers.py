import numpy as np
from SingletonBase import SingletonBase

Byte = np.uint8
Word = np.uint16

INIT_STACK_POINTER = 0xFFFE
INIT_PROG_COUNTER = 0x0100 # Post Boot ROM program counter. Entry point for the game cartridge

class Flag(SingletonBase):
    _initialized = False # Flag to ensure __init__ runs only once

    def __init__(self):

        # Initialization Guard
        if hasattr(self, '_initialized') and self._initialized:
            print(f"... Skipping Flag __init__ due to existing initialization {id(self)}")
            return

        print(f"Iniitalizing Flag instance {id(self)}")

        # Initializing for DMG post bootstrap ROM. These values may differ per version of gameboy and game boy color
        self._z = 1
        self._n = 0
        self._h = 1
        self._c = 1
        self._flag = Byte(self.c << 7 | self.h << 6 | self.n << 5 | self.z << 4)
        self._initialized = True
    
    def flagReset(self):
        self._flag = 0x00

    @property
    def F(self):
        # self._flag = Byte(self.c << 7 | self.h << 6 | self.n << 5 | self.z << 4)
        # print(f"{self.F}")
        return self._flag

    @F.setter
    def F(self, byte):
        self.c = (byte & 0x10) >>  4
        self.h = (byte & 0x20) >>  5
        self.n = (byte & 0x40) >>  6
        self.z = (byte & 0x80) >>  7
        self._flag = Byte(self.c << 7 | self.h << 6 | self.n << 5 | self.z << 4)

    @property    
    def c(self):
        return self._c
    @c.setter
    def c(self, bit):
        if not (bit == 1 or bit == 0):
            raise ValueError(f"bit = {bit}: Bit must be [0|1]")
        self._c = bit

    @property    
    def h(self):
        return self._h
    @h.setter
    def h(self, bit):
        if not (bit == 1 or bit == 0):
            raise ValueError(f"bit = {bit}: Bit must be [0|1]")
        self._h = bit

    @property    
    def n(self):
        return self._n
    @n.setter
    def n(self, bit):
        if not (bit == 1 or bit == 0):
            raise ValueError(f"bit = {bit}: Bit must be [0|1]")
        self._n = bit

    @property    
    def z(self):
        return self._z
    @z.setter
    def z(self, bit):
        if not (bit == 1 or bit == 0):
            raise ValueError(f"bit = {bit}: Bit must be [0|1]")
        self._z = bit

class RegByte(SingletonBase):
    _initialized = False # Flag to ensure __init__ runs only once

    def __init__(self):
        """
        Initializes the instance state *only the first time*.
        """
        # Check if this specific instance has already been initialized

        # Initialization Guard
        if hasattr(self, '_initialized') and self._initialized:
            print(f"... Skipping Flag __init__ due to existing initialization {id(self)}")
            return


        print(f"Iniitalizing RegByte instance {id(self)}")
        print(f"Initializing to magical post boot ROM values.")
        self._initialized = True
        self._B = Byte(0x00)
        self._C = Byte(0x13)
        self._D = Byte(0x00)
        self._E = Byte(0xD8)
        self._H = Byte(0x01)
        self._L = Byte(0x4D)
        self._HL = Word(self.H << 8 | self.L)
        self._A = Byte(1)
    
    @property    
    def A(self):
        return self._A
    
    @A.setter
    def A(self, byte : Byte):
        self._A = byte

    @property
    def B(self):
        return self._B
    
    @B.setter
    def B(self, byte : Byte):
        self._B = byte

    @property    
    def C(self):
        return self._C

    @C.setter
    def C(self, byte : Byte):
        self._C = byte

    @property    
    def D(self):
        return self._D
    @D.setter
    def D(self, byte : Byte):
        self._D = byte

    @property    
    def E(self):
        return self._E
    @E.setter
    def E(self, byte : Byte):
        self._E = byte
    
    @property    
    def H(self):
        return self._H
    @H.setter
    def H(self, byte : Byte):
        self._H = byte

    @property   
    def L(self):
        return self._L
    @L.setter
    def L(self, byte : Byte):
        self._L = byte

class RegWord(SingletonBase):

    # Main Question with this class, do the words here need to track their respective bytes real time?  YES
    # Seemingly would need real time, pointer like behavior. 
    # TODO To satisfy this, implement the subject/observer data pattern of RegByte instance

    _initialized = False # Flag to ensure __init__ runs only once

    def __init__(self, byte : RegByte, flag : Flag):
        # Initialization Guard
        if hasattr(self, '_initialized') and self._initialized:
            print(f"... Skipping RegWord __init__ due to existing initialization {id(self)}")
            return

        print(f"Iniitalizing Flag instance {id(self)}")

        self.byte = byte
        self._AF = (self.byte.A << 8) | flag.F # Need to explicitly tell python to access the flags property
        self._BC = (self.byte.B << 8) | self.byte.C
        self._DE = (self.byte.D << 8) | self.byte.E
        self._HL = (self.byte.H << 8) | self.byte.L
        self._SP = Word(INIT_STACK_POINTER)
        self._PC = Word(INIT_PROG_COUNTER)
        self._initialized = True
    
    #============ Stack Pointer and Program Counter Properties===#

    @property
    def SP(self):
        return self._SP
    
    @SP.setter
    def SP(self,value:Word):
        self._SP = value

    def SP_Reset(self, value:Word = None):
        self._SP = 0
        if value is not None:
            self._SP = value

    @property
    def PC(self):
        return self._PC
    
    # TODO: Need to determine whether carry/wrap around needs to be handled
    @PC.setter
    def PC(self,value:Word):
        self._PC += value

    def PC_Reset(self, value:Word = None):
        self._PC = 0
        if value is not None:
            self._PC = value


    #============ 16 bit Words of Core Registers=================#
    
    # Getter will update the value when it is called, from referencing the underlying core register
    @property    
    def AF(self):
        self._AF = (self.byte.A << 8) | self.F
        return self._AF
    
    @AF.setter
    def AF(self, word : Word):
        self.byte.A = (word & 0xFF00) >> 8
        self.F = (word & 0xFF)
        self._AF = (self.byte.A << 8) | self.F

    @property    
    def BC(self):
        self._BC = (self.byte.B << 8) | self.byte.C
        return self._BC
    
    @BC.setter
    def BC(self, word : Word):
        self.byte.B = (word & 0xFF00) >> 8
        self.byte.C = (word & 0xFF)
        self._BC = (self.byte.B  << 8) | self.byte.C
    
    @property    
    def DE(self):
        self._DE = (self.byte.D << 8) | self.byte.E
        return self._DE
    
    @DE.setter
    def DE(self, word : Word):
        self.byte.D = (word & 0xFF00) >> 8
        self.byte.E = (word & 0xFF)
        self._DE = (self.byte.D  << 8) | self.byte.E

    @property    
    def HL(self):
        self._HL = (self.byte.H << 8) | self.byte.L
        return self._HL
    
    @HL.setter
    def HL(self, word : Word):
        self.byte.H = (word & 0xFF00) >> 8
        self.byte.L = (word & 0xFF)
        self._HL = (self.byte.H  << 8) | self.byte.L
