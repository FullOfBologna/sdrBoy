from SingletonBase import *

from Registers import Byte
from Registers import Word
from Registers import RegByte
from Registers import RegWord
from Registers import Flag
from Registers import InterruptMask
import numpy as np

from Bus import Bus

# PPU Timing Constants
CYCLES_PER_SCANLINE = 456
VISIBLE_SCANLINES = 144
VBLANK_SCANLINES = 10
TOTAL_SCANLINES = VISIBLE_SCANLINES + VBLANK_SCANLINES


class PPU(SingletonBase):
    _initialized = False

    def __init__(self):

        # Initialization Guard
        if hasattr(self, '_initialized') and self._initialized:
            print(f"... Skipping PPU __init__ due to existing initialization {id(self)}")
            return

        print(f"Iniitalizing PPU instance {id(self)}")

        self.Bus = Bus()

        # PPU Registers
        self.registers = {
            0xFF40: Byte(0), # LCDC
            0xFF41: Byte(0), # STAT
            0xFF42: Byte(0), # SCY
            0xFF43: Byte(0), # SCX
            0xFF44: Byte(0), # LY
            0xFF45: Byte(0), # LYC
            0xFF46: Byte(0), # DMA
            0xFF47: Byte(0), # BGP
            0xFF48: Byte(0), # OBP0
            0xFF49: Byte(0), # OBP1
            0xFF4A: Byte(0), # WY
            0xFF4B: Byte(0), # WX
        }

        self._initialized = True

    def step():
        pass

    def reset(self):
        pass

    def renderScanline(self):
        pass

    def renderFrame(self):
        pass

    def writeRegister(self, addr, value):
        if addr in self.registers:
            self.registers[addr] = value

    def readRegister(self, addr):
        return self.registers.get(addr, Byte(0xFF))

    # Properties for named access
    @property
    def LCDC(self): return self.registers[0xFF40]
    @LCDC.setter
    def LCDC(self, value): self.registers[0xFF40] = value

    @property
    def STAT(self): return self.registers[0xFF41]
    @STAT.setter
    def STAT(self, value): self.registers[0xFF41] = value

    @property
    def SCY(self): return self.registers[0xFF42]
    @SCY.setter
    def SCY(self, value): self.registers[0xFF42] = value

    @property
    def SCX(self): return self.registers[0xFF43]
    @SCX.setter
    def SCX(self, value): self.registers[0xFF43] = value

    @property
    def LY(self): return self.registers[0xFF44]
    @LY.setter
    def LY(self, value): self.registers[0xFF44] = value

    @property
    def LYC(self): return self.registers[0xFF45]
    @LYC.setter
    def LYC(self, value): self.registers[0xFF45] = value

    @property
    def DMA(self): return self.registers[0xFF46]
    @DMA.setter
    def DMA(self, value): self.registers[0xFF46] = value

    @property
    def BGP(self): return self.registers[0xFF47]
    @BGP.setter
    def BGP(self, value): self.registers[0xFF47] = value

    @property
    def OBP0(self): return self.registers[0xFF48]
    @OBP0.setter
    def OBP0(self, value): self.registers[0xFF48] = value

    @property
    def OBP1(self): return self.registers[0xFF49]
    @OBP1.setter
    def OBP1(self, value): self.registers[0xFF49] = value

    @property
    def WY(self): return self.registers[0xFF4A]
    @WY.setter
    def WY(self, value): self.registers[0xFF4A] = value

    @property
    def WX(self): return self.registers[0xFF4B]
    @WX.setter
    def WX(self, value): self.registers[0xFF4B] = value

    def dmaTransfer(self,byte):
        pass

    def updateLCDC(self,byte):
        pass

    def updateSTAT(self,byte):
        pass

    def updateBGP(self,byte):
        pass

    def updateOBP0(self,byte):
        pass

    def updateOBP1(self,byte):
        pass


    
