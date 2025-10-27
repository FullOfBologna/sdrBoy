from SingletonBase import *
import numpy as np
from Registers import Byte
from Registers import Word


GAMEBOY_MEMORY_SIZE = 0x10000 # 64KB

class Memory(SingletonBase):
    _initialized = False

    def __init__(self):

                # Initialization Guard
        if hasattr(self, '_initialized') and self._initialized:
            print(f"... Skipping Flag __init__ due to existing initialization {id(self)}")
            return

        print(f"Iniitalizing Flag instance {id(self)}")


        self.memBank = np.zeros(GAMEBOY_MEMORY_SIZE, dtype=Byte)
        self.memoryMap = {
            "ROM_BANK_0"    : (0x0000, 0x3FFF),
            "ROM_BANK_N"    : (0x4000, 0x7FFF),
            "VRAM"          : (0x8000, 0x9FFF),
            "EXT_RAM"       : (0xA000, 0xBFFF),
            "WRAM_BANK_0"   : (0xC000, 0xCFFF),
            "WRAM_BANK_N"   : (0xD000, 0xDFFF),
            "OAM"           : (0xFE00, 0xFE9F),
            "IO_REGISTERS"  : (0xFF00, 0xFF7F),
            "HRAM"          : (0xFF80, 0xFFFE),
            "IE_REGISTER"   : (0xFFFF, 0xFFFF),
        }
        self._initialized = True
        
    def loadRom(self,byte, addr):
        romN_start, romN_end = self.memoryMap["ROM_BANK_N"]

        if addr <= romN_end:
            self.memBank[addr] = byte
        pass

    def writeByte(self,byte,addr):  
        # Prevent writing to ROM Banks
        rom0_start, rom0_end = self.memoryMap["ROM_BANK_0"]
        romN_start, romN_end = self.memoryMap["ROM_BANK_N"]

        if addr > romN_end:
            self.memBank[addr] = byte
    
    def writeWord(self,word,addr):
        romN_start, romN_end = self.memoryMap["ROM_BANK_N"]

        # Little Endian
        if addr > romN_end:
            self.memBank[addr]      = word & 0xFF
            self.memBank[addr+1]    =  (word & 0xFF00) >> 8
        
    def readByte(self,addr):
        return self.memBank[addr]
    
    # Little Endian Read
    def readWord(self,addr):
        return (self.memBank[addr+1].astype(Word) << 8) | self.memBank[addr] 

