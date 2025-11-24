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

        self.oam = np.zeros((0xA0), dtype=Byte)
        self.vram = np.zeros((0x2000), dtype=Byte)


        self.cycleCounter = 0
        self._initialized = True

    def step(self, cycles):
        # Check if LCD is enabled (Bit 7 of LCDC)
        if not (self.LCDC & 0x80):
            self.cycleCounter = 0
            self.LY = 0
            self.STAT &= 0xFC # Set mode to 0
            return

        self.cycleCounter += cycles

        current_mode = self.STAT & 0x03

        if self.LY >= 144:
            # VBlank (Mode 1)
            mode = 1
            self.STAT = (self.STAT & 0xFC) | 0x01
            
            # Check for end of scanline
            if self.cycleCounter >= 456:
                self.cycleCounter -= 456
                self.LY += 1
                
                if self.LY > 153:
                    self.LY = 0
                    # End of VBlank, start of new frame
                    # Reset to Mode 2 (OAM Scan)
                    self.STAT = (self.STAT & 0xFC) | 0x02
        else:
            # Visible Scanlines
            if self.cycleCounter < 80:
                # Mode 2 (OAM Scan)
                mode = 2
                self.STAT = (self.STAT & 0xFC) | 0x02
            elif self.cycleCounter < 252: # 80 + 172
                # Mode 3 (Drawing)
                mode = 3
                self.STAT = (self.STAT & 0xFC) | 0x03
            else:
                # Mode 0 (HBlank)
                mode = 0
                self.STAT = (self.STAT & 0xFC) | 0x00
                
            # Check for end of scanline
            if self.cycleCounter >= 456:
                self.cycleCounter -= 456
                self.LY += 1
                
                # Render the line we just finished
                self.renderScanline()
                
                if self.LY == 144:
                    # Enter VBlank
                    self.STAT = (self.STAT & 0xFC) | 0x01
                    # Request VBlank Interrupt (Bit 0 of IF)
                    if_reg = self.Bus.readByte(0xFF0F)
                    self.Bus.writeByte(0xFF0F, if_reg | 0x01)

    def reset(self):
        self.cycleCounter = 0
        self.LY = 0
        self.STAT = 0
        self.vram = np.zeros((0x2000), dtype=Byte)
        self.oam = np.zeros((0xA0), dtype=Byte)
        # Framebuffer: 160x144 pixels, storing RGB values (3 bytes per pixel)
        # Using uint32 for easier integration with some GUI libs, or uint8 (144, 160, 3)
        self.framebuffer = np.zeros((144, 160, 3), dtype=np.uint8)

    def renderScanline(self):
        # Basic Background Rendering
        
        # LCDC Bit 0: BG Display (0=Off, 1=On)
        if not (self.LCDC & 0x01):
            # If BG is off, render white (or transparent?)
            # For now, let's just fill with white
            self.framebuffer[self.LY, :, :] = 255
            return

        # LCDC Bit 3: BG Tile Map Area (0=9800-9BFF, 1=9C00-9FFF)
        tile_map_base = 0x1C00 if (self.LCDC & 0x08) else 0x1800
        
        # LCDC Bit 4: BG & Window Tile Data Area (0=8800-97FF, 1=8000-8FFF)
        tile_data_base = 0x0000 if (self.LCDC & 0x10) else 0x0800
        is_signed_addressing = not (self.LCDC & 0x10)

        # SCY and SCX (Scroll Y and X)
        scy = int(self.SCY)
        scx = int(self.SCX)
        
        y_pos = (int(self.LY) + scy) & 0xFF
        
        # Calculate which row of tiles we are on
        tile_row = y_pos // 8
        
        # Iterate through the 160 pixels of the scanline
        # Optimization: Iterate by tiles (20 tiles per line)
        for x in range(160):
            x_pos = (x + scx) & 0xFF
            tile_col = x_pos // 8
            
            # Calculate the address in the Tile Map
            tile_address = tile_map_base + (tile_row * 32) + tile_col
            
            # Get the tile index
            tile_index = self.vram[tile_address]
            
            # Calculate the address of the tile data
            if is_signed_addressing:
                # In 8800 mode, indices are -128 to 127
                # 0 maps to 9000. 128 maps to 8800.
                # Python's uint8 0-255: 0-127 is 0-127. 128-255 is -128 to -1.
                if tile_index > 127:
                    tile_index = tile_index - 256
                # Address = 0x1000 (offset for 9000 relative to 8000) + (index * 16)
                # But we are using 0-based VRAM array.
                # 0x8000 is index 0.
                # 0x8800 is index 0x800.
                # 0x9000 is index 0x1000.
                tile_data_addr = 0x1000 + (tile_index * 16)
            else:
                # 8000 mode, indices are 0-255 unsigned
                tile_data_addr = tile_data_base + (tile_index * 16)
            
            # Which line of the tile (0-7)
            line_in_tile = y_pos % 8
            
            # Read the 2 bytes of data for this line
            # Each tile is 16 bytes (2 bytes per line x 8 lines)
            data1 = self.vram[tile_data_addr + (line_in_tile * 2)]
            data2 = self.vram[tile_data_addr + (line_in_tile * 2) + 1]
            
            # Which bit (pixel) in the tile line (0-7)
            # Bit 7 is the leftmost pixel, Bit 0 is the rightmost
            bit_index = 7 - (x_pos % 8)
            
            # Decode the color index (0-3)
            # Color bit 0 comes from data1, Color bit 1 comes from data2
            color_bit_0 = (data1 >> bit_index) & 0x01
            color_bit_1 = (data2 >> bit_index) & 0x01
            color_id = (color_bit_1 << 1) | color_bit_0
            
            # Map color_id to actual color using BGP (Background Palette)
            # BGP bits: 7-6 (Color 3), 5-4 (Color 2), 3-2 (Color 1), 1-0 (Color 0)
            palette_color = (self.BGP >> (color_id * 2)) & 0x03
            
            # Map palette_color (0-3) to RGB
            # 0 = White, 1 = Light Gray, 2 = Dark Gray, 3 = Black
            colors = [
                [255, 255, 255], # 0: White
                [192, 192, 192], # 1: Light Gray
                [96, 96, 96],    # 2: Dark Gray
                [0, 0, 0]        # 3: Black
            ]
            
            self.framebuffer[self.LY, x] = colors[palette_color]

    def renderFrame(self):
        # Placeholder for full frame rendering if needed
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


    
