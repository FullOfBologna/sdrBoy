from SingletonBase import *

from Registers import Byte
from Registers import Word
from Registers import RegByte
from Registers import RegWord
from Registers import Flag
from Registers import InterruptMask
import numpy as np

from Bus import Bus

Byte = np.uint8
Word = np.uint16

from Memory import Memory

# PPU Timing Constants
CYCLES_PER_SCANLINE = 456
VISIBLE_SCANLINES = 144
VBLANK_SCANLINES = 10
TOTAL_SCANLINES = VISIBLE_SCANLINES + VBLANK_SCANLINES


class PPU(SingletonBase):
    _initialized = False

    def __init__(self, bus: Bus):

        # Initialization Guard
        if hasattr(self, '_initialized') and self._initialized:
            print(f"... Skipping PPU __init__ due to existing initialization {id(self)}")
            return

        print(f"Iniitalizing PPU instance {id(self)}")

        self.Memory = Memory()

        # PPU Registers
        self.LCDC = Byte(0xFF40)   # LCD Control
        self.STAT = Byte(0xFF41)   # LCD Status
        self.SCY  = Byte(0xFF42)   # Scroll Y
        self.SCX  = Byte(0xFF43)   # Scroll X
        self.LY   = Byte(0xFF44)   # LCD Y-Coordinate
        self.LYC  = Byte(0xFF45)   # LY Compare
        self.DMA  = Byte(0xFF46)   # DMA Transfer and Start Address
        self.BGP  = Byte(0xFF47)   # BG Palette Data
        self.OBP0 = Byte(0xFF48)   # Object Palette 0 Data
        self.OBP1 = Byte(0xFF49)   # Object Palette 1 Data
        self.WY   = Byte(0xFF4A)   # Window Y Position
        self.WX   = Byte(0xFF4B)   # Window X Position minus 7

        self._initialized = True

    def step():
        pass

    def reset(self):
        pass

    def renderScanline(self):
        pass

    def renderFrame(self):
        pass

    def writeRegister(self,addr,byte):
        pass

    def readRegister(self,addr):
        pass

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


    
