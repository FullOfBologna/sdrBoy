import numpy as np

Byte = np.uint8
Word = np.uint16

# class SingletonBase:
#TODO : Establish a Singleton base class

class Flag:
    _instance = None  # Class variable to store the single instance
    _initialized = False # Flag to ensure __init__ runs only once

    def __new__(cls):
        """
        Controls the instance creation process.
        """
        if cls._instance is None:
            print("Creating Flag Instance...")
            # Call the superclass's __new__ to actually create the object
            cls._instance = super().__new__(cls)
        else:
            print("Flag already exists, returning it.")
        return cls._instance

    def __init__(self):
        self._z = 0
        self._n = 0
        self._h = 0
        self._c = 0

    def write(self,byte):
        self.c = (byte & 0x10) >>  4
        self.h = (byte & 0x20) >>  5
        self.n = (byte & 0x40) >>  6
        self.z = (byte & 0x80) >>  7
    
    def reset(self):
        self.write(0x00)

    def read(self):
        outByte = Byte(self.A << 7 | self.HL << 6 | self.L << 5 | self.H << 4)
        print(f"{outByte}")
        return outByte
    
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
        self._c = bit

class RegByte:
    _instance = None  # Class variable to store the single instance
    _initialized = False # Flag to ensure __init__ runs only once

    def __new__(cls):
        """
        Controls the instance creation process.
        """
        if cls._instance is None:
            print("Creating RegByte Instance...")
            # Call the superclass's __new__ to actually create the object
            cls._instance = super().__new__(cls)
        else:
            print("RegByte already exists, returning it.")
        return cls._instance

    def __init__(self):
        """
        Initializes the instance state *only the first time*.
        """
        # Check if this specific instance has already been initialized
        if self._initialized:
            print("Initialization skipped (already done).")
            return

        print(f"Initializing RegByte (first time)...")

        self._initialized = True
        self._B = Byte(0)
        self._C = Byte(0)
        self._D = Byte(0)
        self._E = Byte(0)
        self._H = Byte(0)
        self._L = Byte(0)
        self._HL = Word(self.H << 8 | self.L)
        self._A = Byte(0)
    
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

class RegWord:

    # Main Question with this class, do the words here need to track their respective bytes real time? 
    # Seemingly would need real time, pointer like behavior, with the 
    _instance = None  # Class variable to store the single instance
    _initialized = False # Flag to ensure __init__ runs only once

    def __new__(cls):
        """
        Controls the instance creation process.
        """
        if cls._instance is None:
            print("Creating RegByte Instance...")
            # Call the superclass's __new__ to actually create the object
            cls._instance = super().__new__(cls)
        else:
            print("RegByte already exists, returning it.")
        return cls._instance

    def __init__(self, byte : RegByte, flag : Flag):
        self._AF = (byte.A << 8) | flag
        self._BC = (byte.B << 8) | byte.C
        self._DE = (byte.D << 8) | byte.E
        self._HL = (byte.H << 8) | byte.L
        self._SP = Word(0)
        self._PC = Word(0)
    
    #============ Stack Pointer and Program Counter Properties===#

    @property
    def SP(self):
        return self._SP
    
    # TODO: Need to determine whether carry/wrap around needs to be handled
    @SP.setter
    def SP(self,value:Word):
        self._SP += value

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
    ## TODO : Implement logic within the getter to decompose the high and low bytes, or leave that to the high level user. TBD

    @property    
    def AF(self):
        return self._AF
    
    @AF.setter
    def AF(self, word : Word):
        self._AF = word

    @AF.setter
    def AF(self, aByte : Byte, flag : Flag):
        self._AF = (aByte << 8) | flag

    @property    
    def BC(self):
        return self._BC
    
    @BC.setter
    def BC(self, word : Word):
        self._BC = word

    @BC.setter
    def BC(self, bByte : Byte, cByte : Byte):
        self._BC = (bByte << 8) | cByte

    @property    
    def DE(self):
        return self._DE
    
    @DE.setter
    def DE(self, word : Word):
        self._DE = word

    @DE.setter
    def DE(self, dByte : Byte, eByte : Byte):
        self._DE = (dByte << 8) | eByte

    @property    
    def HL(self):
        return self._HL
    
    @HL.setter
    def HL(self, word : Word):
        self._HL = word


    @HL.setter
    def HL(self, hByte : Byte, lByte : Byte):
        self._HL = (hByte << 8) | lByte

    