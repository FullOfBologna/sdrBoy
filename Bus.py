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
            return
        
        self.wram = np.zeros(0x2000, dtype=Byte)
        self.hram = np.zeros(0x80, dtype=Byte)
        self.ext_ram = np.zeros(0x2000, dtype=Byte)
        self.io_regs = np.zeros(0x80, dtype=Byte)
        self.ie_reg = Byte(0)

        self.rom_data = np.zeros(0x8000, dtype=Byte)

        ### Instances of other components
        self.cpu = None
        self.ppu = None

        self._initialized = True
        
    def reset(self):
        self.wram.fill(0)
        self.hram.fill(0)
        self.ext_ram.fill(0)
        self.io_regs.fill(0)
        self.ie_reg = Byte(0)
        
        # Note: We don't clear ROM or VRAM/OAM here as VRAM/OAM belongs to PPU
        # and ROM should persist. PPU reset should be handled if needed.


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
                raise MemoryAccessError(addr, "PPU not initialized in Bus readByte")
            return self.ppu.vram[addr - 0x8000]
        elif 0xA000 <= addr <= 0xBFFF:
            return self.ext_ram[addr - 0xA000]
        elif 0xC000 <= addr <= 0xDFFF:
            # WRAM Area
            return self.wram[addr - 0xC000]
        elif 0xE000 <= addr <= 0xFDFF: # Echo RAM
            return self.wram[addr - 0xE000]
        elif 0xFE00 <= addr <= 0xFE9F:
            # OAM Area
            if self.ppu is None:
                raise MemoryAccessError(addr, "PPU not initialized in Bus readByte")
            return self.ppu.oam[addr - 0xFE00]
        elif 0xFEA0 <= addr <= 0xFEFF:
            # Not Usable
            return Byte(0xFF)
        elif 0xFF40 <= addr <= 0xFF4B: 
            # PPU Registers
            if self.ppu is None:
                raise MemoryAccessError(addr, "PPU not initialized in Bus readByte")
            return self.ppu.readRegister(addr)
        elif 0xFF00 <= addr <= 0xFF7F:
            # Other IO Registers
            return self.io_regs[addr - 0xFF00]
        elif 0xFF80 <= addr <= 0xFFFE:
            # HRAM Area
            return self.hram[addr - 0xFF80]
        elif addr == 0xFFFF:
            return self.ie_reg
        else:
            # Other areas (I/O, OAM, etc.)
            raise MemoryAccessError(addr, f"Read from unhandled address: {hex(addr)}")
        
    def writeByte(self, addr: Word, value: Byte):
        if 0x0000 <= addr <= 0x7FFF:
            # ROM Area - Read Only
            # raise MemoryAccessError(addr, f"Cannot write to ROM at address {hex(addr)}")
            pass # Ignore writes to ROM for now, or raise error? User said "Cannot write".
                 # Real hardware ignores it (or MBC handles it). 
                 # For now, let's ignore it to be safe, or raise if we want to be strict.
                 # Given the user's prompt "We cannot write...", raising an error might be better to catch bad tests.
                 # But let's stick to "ignore" or "error". 
                 # Actually, let's raise an error to force us to fix the tests as requested.
            raise MemoryAccessError(addr, f"Cannot write to ROM at address {hex(addr)}")
        elif 0x8000 <= addr <= 0x9FFF:
            # VRAM Area
            if self.ppu is None:
                raise MemoryAccessError(addr, "PPU not initialized in Bus writeByte")
            self.ppu.vram[addr - 0x8000] = value
        elif 0xA000 <= addr <= 0xBFFF:
            self.ext_ram[addr - 0xA000] = value
        elif 0xC000 <= addr <= 0xDFFF:
            # WRAM Area
            self.wram[addr - 0xC000] = value
        elif 0xE000 <= addr <= 0xFDFF: # Echo RAM
            self.wram[addr - 0xE000] = value
        elif 0xFF40 <= addr <= 0xFF4B:
            # PPU Registers
            if self.ppu is None:
                raise MemoryAccessError(addr, "PPU not initialized in Bus writeByte")
            self.ppu.writeRegister(addr, value)
        elif 0xFE00 <= addr <= 0xFE9F:
            # OAM Area
            if self.ppu is None:
                raise MemoryAccessError(addr, "PPU not initialized in Bus writeByte")
            self.ppu.oam[addr - 0xFE00] = value
        elif 0xFEA0 <= addr <= 0xFEFF:
            # Not Usable
            pass
        elif 0xFF00 <= addr <= 0xFF7F:
            # Other IO Registers
            self.io_regs[addr - 0xFF00] = value
            
            # Serial Port Implementation
            if addr == 0xFF02 and value == 0x81:
                char = chr(self.io_regs[0xFF01 - 0xFF00])
                print(char, end="", flush=True)
        elif 0xFF80 <= addr <= 0xFFFE:
            # HRAM Area
            self.hram[addr - 0xFF80] = value
        elif addr == 0xFFFF:
            self.ie_reg = value
        else:
            # Other areas (I/O, OAM, etc.)
            raise MemoryAccessError(addr, f"Write to unhandled address: {hex(addr)} with value {hex(value)}")        
        
    def writeWord(self, addr: Word, value: Word):
        low = value & 0x00FF
        high = (value >> 8) & 0x00FF
        self.writeByte(addr, low)
        self.writeByte(addr + 1, high)

    def readWord(self, addr: Word) -> Word:
        low = self.readByte(addr)
        high = self.readByte(addr + 1)
        return (high.astype(Word) << 8) | low

    
