from SingletonBase import *

import numpy as np
from Registers import Byte
from Registers import Word

class MemoryAccessError(Exception):
    def __init__(self, address: Word, message: str = "Invalid memory access"):
        self.address = address
        self.message = f"{message} at address {hex(address)}"
        super().__init__(self.message)


class Bus(SingletonBase):
    
    _initialized = False

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            print(f"... Skipping re-initialization of {self.__class__.__name__}")
            return
        
        print ("... Initializing Bus")

        self.wram = np.zeros(0x2000, dtype=Byte)
        self.hram = np.zeros(0x80, dtype=Byte)

        self.rom_data = None

        ### Instances of other components
        self.cpu = None
        self.ppu = None


    def loadROM(self, rom_bytes: bytes):
        self.rom_data = np.frombuffer(rom_bytes, dtype=Byte)

    # Bus Read/Write Methods

    def readByte(self, addr: Word) -> Byte:
        if 0x0000 <= addr <= 0x7FFF:
            # ROM Area
            return self.rom_data[addr]
        elif 0x8000 <= addr <= 0x9FFF:
            # VRAM Area
            if self.ppu is None:
                raise MemoryAccessError("PPU not initialized in Bus readByte")
            return self.ppu.vram[addr - 0x8000]
        elif 0xC000 <= addr <= 0xDFFF:
            # WRAM Area
            return self.wram[addr - 0xC000]
        elif 0xFF40 <= addr <= 0xFF4B: 
            # PPU Registers
            if self.ppu is None:
                raise MemoryAccessError("PPU not initialized in Bus readByte")
            return self.ppu.readRegister(addr)
        elif 0xFF80 <= addr <= 0xFFFE:
            # HRAM Area
            return self.hram[addr - 0xFF80]
        else:
            # Other areas (I/O, OAM, etc.)
            raise MemoryAccessError(f"Read from unhandled address: {hex(addr)}")
        
    def writeByte(self, addr: Word, value: Byte):
        if 0x8000 <= addr <= 0x9FFF:
            # VRAM Area
            if self.ppu is None:
                raise MemoryAccessError("PPU not initialized in Bus writeByte")
            self.ppu.vram[addr - 0x8000] = value
        elif 0xC000 <= addr <= 0xDFFF:
            # WRAM Area
            self.wram[addr - 0xC000] = value
        elif 0xFF40 <= addr <= 0xFF4B:
            # PPU Registers
            if self.ppu is None:
                raise MemoryAccessError("PPU not initialized in Bus writeByte")
            self.ppu.writeRegister(addr, value)
        elif 0xFF80 <= addr <= 0xFFFE:
            # HRAM Area
            self.hram[addr - 0xFF80] = value
        else:
            # Other areas (I/O, OAM, etc.)
            raise MemoryAccessError(f"Write to unhandled address: {hex(addr)} with value {hex(value)}")        
        
    def writeWord(self, addr: Word, value: Word):
        low = value & 0x00FF
        high = (value >> 8) & 0x00FF
        self.writeByte(addr, low)
        self.writeByte(addr + 1, high)

    def readWord(self, addr: Word) -> Word:
        low = self.readByte(addr)
        high = self.readByte(addr + 1)
        return (high << 8) | low
    
