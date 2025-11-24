import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import numpy as np
from PPU import PPU
from Registers import Byte

class TestPPURender(unittest.TestCase):
    def setUp(self):
        self.ppu = PPU()
        self.ppu.reset()

    def test_render_simple_tile(self):
        # 1. Setup Registers
        # LCDC: Bit 7 (Enable), Bit 4 (Tile Data 8000), Bit 0 (BG Enable) -> 1001 0001 -> 0x91
        self.ppu.LCDC = 0x91
        # BGP: 11 10 01 00 -> 0xE4 (Standard Palette: Black, Dark Gray, Light Gray, White)
        self.ppu.BGP = 0xE4
        
        # 2. Create a Tile (8x8 pixels)
        # Let's make a solid block of color 3 (Black)
        # Each line needs 2 bytes. For color 3 (binary 11), both bytes need to be 0xFF.
        tile_data = [0xFF] * 16 
        
        # Write Tile 0 to VRAM (Address 0x0000 in VRAM array, which corresponds to 0x8000)
        for i, byte in enumerate(tile_data):
            self.ppu.vram[i] = byte
            
        # 3. Set Tile Map
        # Map 0x9800 (Offset 0x1800 in VRAM)
        # Set (0,0) to Tile 0
        self.ppu.vram[0x1800] = 0x00
        
        # 4. Run PPU for one scanline (Line 0)
        # We need to step enough cycles to complete the line (456)
        # The renderScanline happens at cycle 252 (start of Mode 0)
        self.ppu.step(456)
        
        # 5. Verify Framebuffer
        # We expect the first 8 pixels of line 0 to be Black [0, 0, 0]
        # The rest should be White [255, 255, 255] (default initialized to 0, but our logic fills white if BG off... wait, BG is on)
        # Actually, VRAM is 0 initialized, so other tiles will be Tile 0 too!
        # So the WHOLE screen should be black if Tile 0 is all black.
        
        # Let's check pixel (0,0)
        pixel = self.ppu.framebuffer[0, 0]
        np.testing.assert_array_equal(pixel, [0, 0, 0], "Pixel (0,0) should be Black")
        
        # Let's check pixel (0, 159)
        pixel = self.ppu.framebuffer[0, 159]
        np.testing.assert_array_equal(pixel, [0, 0, 0], "Pixel (0,159) should be Black")

    def test_render_pattern_tile(self):
        # 1. Setup Registers
        self.ppu.LCDC = 0x91
        self.ppu.BGP = 0xE4
        
        # 2. Create a Pattern Tile (Stripe)
        # Line 0: Color 3 (11) -> 0xFF, 0xFF
        # Line 1: Color 0 (00) -> 0x00, 0x00
        tile_data = []
        for _ in range(4):
            tile_data.append(0xFF) # Line N Color 3
            tile_data.append(0xFF)
            tile_data.append(0x00) # Line N+1 Color 0
            tile_data.append(0x00)
            
        for i, byte in enumerate(tile_data):
            self.ppu.vram[i] = byte
            
        # 3. Set Tile Map
        self.ppu.vram[0x1800] = 0x00
        
        # 4. Run PPU for 2 scanlines
        self.ppu.step(456) # Line 0
        self.ppu.step(456) # Line 1
        
        # 5. Verify
        # Line 0 should be Black
        np.testing.assert_array_equal(self.ppu.framebuffer[0, 0], [0, 0, 0], "Line 0 Pixel 0 should be Black")
        
        # Line 1 should be White
        np.testing.assert_array_equal(self.ppu.framebuffer[1, 0], [255, 255, 255], "Line 1 Pixel 0 should be White")

if __name__ == '__main__':
    unittest.main()
