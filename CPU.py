from SingletonBase import *

from Registers import Byte
from Registers import Word
from Registers import RegByte
from Registers import RegWord
from Registers import Flag
from Registers import InterruptMask
import numpy as np


from Bus import Bus

# from Memory import Memory

class CPU(SingletonBase):

    _initialized = False # Flag to ensure __init__ runs only once

    def __init__(self):
        # Initialization Guard
        if hasattr(self, '_initialized') and self._initialized:
            print(f"... Skipping CPU __init__ due to existing initialization {id(self)}")
            return

        print(f"Iniitalizing CPU instance {id(self)}")

        # self.Memory = Memory()
        self.Bus = Bus()
        self.CoreReg = RegByte()
        self.Flags = Flag()
        self.CoreWords = RegWord(self.CoreReg,self.Flags)
        self.InterruptMask = InterruptMask(self.Bus)

        self._initialized = True
        self.scheduleIMEEnabled = False 
        self.Halted = False
        self.Stopped = False
        self.lr35902_opCodes = {}

        self.init_opCodes()

        self.cycles = 0
        
        self.reset()

    def reset(self):
        # Registers (Post-Boot ROM values)
        self.CoreReg.A = 0x11
        self.Flags.F = 0x80
        self.CoreWords.BC = 0x0000
        self.CoreWords.DE = 0xFF56
        self.CoreWords.HL = 0x000D
        self.CoreWords.SP = 0xFFFE
        self.CoreWords.PC = 0x0100

        # State
        self.cycles = 0
        self.Halted = False
        self.Stopped = False
        self.scheduleIMEEnabled = False
        self.InterruptMask.IME = 0

    def step(self):
        # Handle Stopped State first
        if self.Stopped:
            # The CPU is in a low-power state and does nothing until a Joypad
            # button press wakes it up. The main emulation loop is responsible
            # for detecting this and setting self.Stopped = False.
            # We consume a minimal number of cycles to keep timing consistent.
            self.cycles += 4
            return 4

        # Handle Halted State first
        if self.Halted:
            # Check for pending interrupts to exit HALT
            if (self.InterruptMask.IE & self.InterruptMask.IF) != 0:
                self.Halted = False
            else:
                # Remain halted, consume 4 cycles
                self.cycles += 4
                return 4
        
        # Get Current OpCode from memory, via the program counter. 
        currentPC = self.CoreWords.PC

        opCode = self.Bus.readByte(currentPC)

        if opCode in self.lr35902_opCodes:
            opCodeFunc, length, cycles, _ = self.lr35902_opCodes[opCode]

            #Address of potential immediate operand
            operandAddress = (currentPC + 1) & 0xFFFF

            nextPcOverride, cycleCountOverride = opCodeFunc(operandAddress)

            # Update State of CPU

            actualCycles = cycles[0]

            if cycleCountOverride is not None:
                actualCycles = cycleCountOverride

            currentPC = (currentPC + length) & 0xFFFF

            if nextPcOverride is not None: 
                currentPC = nextPcOverride

            self.CoreWords.PC = currentPC
            self.cycles += actualCycles

            #Return number of cycles taken
            return actualCycles

    # Call interrupt handler at the end of each execution of step
    def interruptHandler(self, interruptByte):
        # # Check if IME is scheduled to be enabled
        if self.scheduleIMEEnabled:
            self.InterruptMask.IME = 1
            self.scheduleIMEEnabled = False

            return # Do not process interrupt if IME is scheduled to be enabled wait for cycle delay to begin processing interrupts
        
        ie_reg = self.InterruptMask._IE
        if_reg = self.InterruptMask._IF

        # Interrupt priorities and their handler addresses
        interrupt_priorities = [
            (self.InterruptMask.VBLANK_POS, 0x40),  # VBLANK
            (self.InterruptMask.LCD_STAT_POS, 0x48),  # LCD STAT
            (self.InterruptMask.TIMER_POS, 0x50),  # TIMER
            (self.InterruptMask.SERIAL_POS, 0x58),  # SERIAL
            (self.InterruptMask.JOYPAD_POS, 0x60),  # JOYPAD
        ]

        pendingAndEnable = ie_reg & if_reg
        if pendingAndEnable == 0:
            return
        
        for interruptBit, handlerAddress in interrupt_priorities:
            if (pendingAndEnable & interruptBit) != 0:

                self.Halted = False  # Exit HALT state if in it

                if self.Stopped and (interruptBit == self.InterruptMask.JOYPAD_POS):
                    self.Stopped = False  # Exit STOP state on JOYPAD interrupt

                if self.Stopped:
                    return  # Do not process other interrupts if in STOP state

                # Clear the interrupt flag
                if_reg &= ~interruptBit
                self.InterruptMask._IF = if_reg

                # Push the current PC onto the stack
                self.Bus.writeWord(self.CoreWords.SP - 2, self.CoreWords.SP)
                self.Bus.writeWord(self.CoreWords.SP, self.CoreWords.PC)

                # Set the PC to the handler address
                self.CoreWords.PC = handlerAddress

                # Set IME to 0 to disable further interrupts until re-enabled
                self.InterruptMask.IME = 0

                break
        
 
    # Maps opcode hex value to a tuple: (handler_method, instruction_length_bytes, base_cycles)
    def init_opCodes(self):
        self.lr35902_opCodes = {
            0x00: (self._nop,           1,[ 4],       "----"),
            0x01: (self._ld_bc_d16,     3,[12],       "----"),
            0x11: (self._ld_de_d16,     3,[12],       "----"),
            0x21: (self._ld_hl_d16,     3,[12],       "----"),
            0x31: (self._ld_sp_d16,     3,[12],       "----"),
            0x03: (self._inc_bc,        1,[ 8],       "----"),
            0x13: (self._inc_de,        1,[ 8],       "----"),
            0x23: (self._inc_hl,        1,[ 8],       "----"),
            0x33: (self._inc_sp,        1,[ 8],       "----"),
            0x0B: (self._dec_bc,        1,[ 8],       "----"),
            0x1B: (self._dec_de,        1,[ 8],       "----"),
            0x2B: (self._dec_hl,        1,[ 8],       "----"),
            0x3B: (self._dec_sp,        1,[ 8],       "----"),
            0x3C: (self._inc_a,         1,[ 4],       "Z0H-"),
            0x04: (self._inc_b,         1,[ 4],       "Z0H-"),
            0x0C: (self._inc_c,         1,[ 4],       "Z0H-"),
            0x14: (self._inc_d,         1,[ 4],       "Z0H-"),
            0x1C: (self._inc_e,         1,[ 4],       "Z0H-"),
            0x2C: (self._inc_l,         1,[ 4],       "Z0H-"),
            0x24: (self._inc_h,         1,[ 4],       "Z0H-"),
            0x3D: (self._dec_a,         1,[ 4],       "Z1H-"),
            0x05: (self._dec_b,         1,[ 4],       "Z1H-"),
            0x0D: (self._dec_c,         1,[ 4],       "Z1H-"),
            0x15: (self._dec_d,         1,[ 4],       "Z1H-"),
            0x1D: (self._dec_e,         1,[ 4],       "Z1H-"),
            0x25: (self._dec_h,         1,[ 4],       "Z1H-"),
            0x2D: (self._dec_l,         1,[ 4],       "Z1H-"),
            0x3E: (self._ld_a_d8,       2,[ 8],       "----"),
            0x06: (self._ld_b_d8,       2,[ 8],       "----"),
            0x0E: (self._ld_c_d8,       2,[ 8],       "----"),
            0x16: (self._ld_d_d8,       2,[ 8],       "----"),
            0x1E: (self._ld_e_d8,       2,[ 8],       "----"),
            0x26: (self._ld_h_d8,       2,[ 8],       "----"),
            0x2E: (self._ld_l_d8,       2,[ 8],       "----"),
            0x34: (self._inc_mhl,       1,[ 12],      "Z0H-"),
            0x35: (self._dec_mhl,       1,[ 12],      "Z1H-"),
            0x09: (self._add_hl_bc,     1,[ 8],       "-0HC"),
            0x19: (self._add_hl_de,     1,[ 8],       "-0HC"),
            0x29: (self._add_hl_hl,     1,[ 8],       "----"),
            0x39: (self._add_hl_sp,     1,[ 8],       "-0HC"),
            0x36: (self._ld_mhl_d8,     2,[ 12],      "----"),
            0x07: (self._rlca,          1,[ 4],       "000C"),
            0x0F: (self._rrca,          1,[ 4],       "000C"),
            0x17: (self._rla,           1,[ 4],       "000C"),
            0x1F: (self._rra,           1,[ 4],       "000C"),
            0x02: (self._ld_mbc_a,      1,[ 8],       "----"),
            0x12: (self._ld_mde_a,      1,[ 8],       "----"),
            0x22: (self._ld_mhlp_a,     1,[ 8],       "----"),
            0x32: (self._ld_mhlm_a,     1,[ 8],       "----"),
            0x77: (self._ld_mhl_a,      1,[ 8],       "----"),
            0x08: (self._ld_m16_sp,     3,[20],       "----"),
            0x0A: (self._ld_a_mbc,      1,[ 8],       "----"),
            0x1A: (self._ld_a_mde,      1,[ 8],       "----"),
            0x2A: (self._ld_a_mhlp,     1,[ 8],       "----"),
            0x3A: (self._ld_a_mhlm,     1,[ 8],       "----"),
            0x7E: (self._ld_a_mhl,      1,[ 8],       "----"),
            0x18: (self._jr_r8,         2,[12],       "----"),
            0x20: (self._jr_nz_r8,      2,[12,8],     "----"),
            0x30: (self._jr_nc_r8,      2,[12,8],     "----"),
            0x28: (self._jr_z_r8,       2,[12,8],     "----"),
            0x38: (self._jr_c_r8,       2,[12,8],     "----"),
            0x27: (self._daa,           1,[ 4],       "Z-0C"),
            0x37: (self._scf,           1,[ 4],       "-001"),
            0x2F: (self._cpl,           1,[ 4],       "-11-"),
            0x3F: (self._ccf,           1,[ 4],       "-00C"),
            0x40: (self._ld_b_b,        1,[ 4],       "----"),
            0x41: (self._ld_b_c,        1,[ 4],       "----"),
            0x42: (self._ld_b_d,        1,[ 4],       "----"),
            0x43: (self._ld_b_e,        1,[ 4],       "----"),
            0x44: (self._ld_b_h,        1,[ 4],       "----"),
            0x45: (self._ld_b_l,        1,[ 4],       "----"),
            0x47: (self._ld_b_a,        1,[ 4],       "----"),
            0x48: (self._ld_c_b,        1,[ 4],       "----"),
            0x49: (self._ld_c_c,        1,[ 4],       "----"),
            0x4A: (self._ld_c_d,        1,[ 4],       "----"),
            0x4B: (self._ld_c_e,        1,[ 4],       "----"),
            0x4C: (self._ld_c_h,        1,[ 4],       "----"),
            0x4D: (self._ld_c_l,        1,[ 4],       "----"),
            0x4F: (self._ld_c_a,        1,[ 4],       "----"),
            0x50: (self._ld_d_b,        1,[ 4],       "----"),
            0x51: (self._ld_d_c,        1,[ 4],       "----"),
            0x52: (self._ld_d_d,        1,[ 4],       "----"),
            0x53: (self._ld_d_e,        1,[ 4],       "----"),
            0x54: (self._ld_d_h,        1,[ 4],       "----"),
            0x55: (self._ld_d_l,        1,[ 4],       "----"),
            0x57: (self._ld_d_a,        1,[ 4],       "----"),
            0x58: (self._ld_e_b,        1,[ 4],       "----"),
            0x59: (self._ld_e_c,        1,[ 4],       "----"),
            0x5A: (self._ld_e_d,        1,[ 4],       "----"),
            0x5B: (self._ld_e_e,        1,[ 4],       "----"),
            0x5C: (self._ld_e_h,        1,[ 4],       "----"),
            0x5D: (self._ld_e_l,        1,[ 4],       "----"),
            0x5F: (self._ld_e_a,        1,[ 4],       "----"),
            0x60: (self._ld_h_b,        1,[ 4],       "----"),
            0x61: (self._ld_h_c,        1,[ 4],       "----"),
            0x62: (self._ld_h_d,        1,[ 4],       "----"),
            0x63: (self._ld_h_e,        1,[ 4],       "----"),
            0x64: (self._ld_h_h,        1,[ 4],       "----"),
            0x65: (self._ld_h_l,        1,[ 4],       "----"),
            0x67: (self._ld_h_a,        1,[ 4],       "----"),
            0x68: (self._ld_l_b,        1,[ 4],       "----"),
            0x69: (self._ld_l_c,        1,[ 4],       "----"),
            0x6A: (self._ld_l_d,        1,[ 4],       "----"),
            0x6B: (self._ld_l_e,        1,[ 4],       "----"),
            0x6C: (self._ld_l_h,        1,[ 4],       "----"),
            0x6D: (self._ld_l_l,        1,[ 4],       "----"),
            0x6F: (self._ld_l_a,        1,[ 4],       "----"),
            0x78: (self._ld_a_b,        1,[ 4],       "----"),
            0x79: (self._ld_a_c,        1,[ 4],       "----"),
            0x7A: (self._ld_a_d,        1,[ 4],       "----"),
            0x7B: (self._ld_a_e,        1,[ 4],       "----"),
            0x7C: (self._ld_a_h,        1,[ 4],       "----"),
            0x7D: (self._ld_a_l,        1,[ 4],       "----"),
            0x7F: (self._ld_a_a,        1,[ 4],       "----"),
            0x46: (self._ld_b_mhl,      1,[ 8],       "----"),
            0x4E: (self._ld_c_mhl,      1,[ 8],       "----"),
            0x56: (self._ld_d_mhl,      1,[ 8],       "----"),
            0x5E: (self._ld_e_mhl,      1,[ 8],       "----"),
            0x66: (self._ld_h_mhl,      1,[ 8],       "----"),
            0x6E: (self._ld_l_mhl,      1,[ 8],       "----"),
            0x70: (self._ld_mhl_b,      1,[ 8],       "----"),
            0x71: (self._ld_mhl_c,      1,[ 8],       "----"),
            0x72: (self._ld_mhl_d,      1,[ 8],       "----"),
            0x73: (self._ld_mhl_e,      1,[ 8],       "----"),
            0x74: (self._ld_mhl_h,      1,[ 8],       "----"),
            0x75: (self._ld_mhl_l,      1,[ 8],       "----"),
            0x80: (self._add_a_b,       1,[ 4],       "Z0HC"),
            0x81: (self._add_a_c,       1,[ 4],       "Z0HC"),
            0x82: (self._add_a_d,       1,[ 4],       "Z0HC"),
            0x83: (self._add_a_e,       1,[ 4],       "Z0HC"),
            0x84: (self._add_a_h,       1,[ 4],       "Z0HC"),
            0x85: (self._add_a_l,       1,[ 4],       "Z0HC"),
            0x86: (self._add_a_mhl,     1,[ 8],       "Z0HC"),
            0x87: (self._add_a_a,       1,[ 4],       "Z0HC"),
            0xC6: (self._add_a_d8,      2,[ 8],       "Z0HC"),
            0xE8: (self._add_sp_r8,     2,[16],       "00HC"),
            0x88: (self._adc_a_b,       1,[ 4],       "Z0HC"),
            0x89: (self._adc_a_c,       1,[ 4],       "Z0HC"),
            0x8A: (self._adc_a_d,       1,[ 4],       "Z0HC"),
            0x8B: (self._adc_a_e,       1,[ 4],       "Z0HC"),
            0x8C: (self._adc_a_h,       1,[ 4],       "Z0HC"),
            0x8D: (self._adc_a_l,       1,[ 4],       "Z0HC"),
            0x8E: (self._adc_a_mhl,     1,[ 8],       "Z0HC"),
            0x8F: (self._adc_a_a,       1,[ 4],       "Z0HC"),
            0xCE: (self._adc_a_d8,      2,[ 8],       "Z0HC"),
            0x90: (self._sub_a_b,       1,[ 4],       "Z1HC"),
            0x91: (self._sub_a_c,       1,[ 4],       "Z1HC"),
            0x92: (self._sub_a_d,       1,[ 4],       "Z1HC"),
            0x93: (self._sub_a_e,       1,[ 4],       "Z1HC"),
            0x94: (self._sub_a_h,       1,[ 4],       "Z1HC"),
            0x95: (self._sub_a_l,       1,[ 4],       "Z1HC"),
            0x96: (self._sub_a_mhl,     1,[ 8],       "Z1HC"),
            0x97: (self._sub_a_a,       1,[ 4],       "Z1HC"),
            0xD6: (self._sub_a_d8,      2,[8],        "Z1HC"),
            0x98: (self._sbc_a_b,       1,[ 4],       "Z1HC"),
            0x99: (self._sbc_a_c,       1,[ 4],       "Z1HC"),
            0x9A: (self._sbc_a_d,       1,[ 4],       "Z1HC"),
            0x9B: (self._sbc_a_e,       1,[ 4],       "Z1HC"),
            0x9C: (self._sbc_a_h,       1,[ 4],       "Z1HC"),
            0x9D: (self._sbc_a_l,       1,[ 4],       "Z1HC"),
            0x9E: (self._sbc_a_mhl,     1,[ 8],       "Z1HC"),
            0x9F: (self._sbc_a_a,       1,[ 4],       "Z1HC"),
            0xDE: (self._sbc_a_d8,      2,[8],        "Z1HC"),
            0xA0: (self._and_a_b,       1,[ 4],       "Z010"),
            0xA1: (self._and_a_c,       1,[ 4],       "Z010"),
            0xA2: (self._and_a_d,       1,[ 4],       "Z010"),
            0xA3: (self._and_a_e,       1,[ 4],       "Z010"),
            0xA4: (self._and_a_h,       1,[ 4],       "Z010"),
            0xA5: (self._and_a_l,       1,[ 4],       "Z010"),
            0xA6: (self._and_a_mhl,     1,[ 8],       "Z010"),
            0xA7: (self._and_a_a,       1,[ 4],       "Z010"),
            0xE6: (self._and_a_d8,      2,[8],        "Z010"),
            0xA8: (self._xor_a_b,       1,[ 4],       "Z000"),
            0xA9: (self._xor_a_c,       1,[ 4],       "Z000"),
            0xAA: (self._xor_a_d,       1,[ 4],       "Z000"),
            0xAB: (self._xor_a_e,       1,[ 4],       "Z000"),
            0xAC: (self._xor_a_h,       1,[ 4],       "Z000"),
            0xAD: (self._xor_a_l,       1,[ 4],       "Z000"),
            0xAE: (self._xor_a_mhl,     1,[ 8],       "Z000"),
            0xAF: (self._xor_a_a,       1,[ 4],       "Z000"),
            0xEE: (self._xor_a_d8,      2,[8],        "ZOOO"),
            0xB0: (self._or_a_b,        1,[ 4],       "Z000"),
            0xB1: (self._or_a_c,        1,[ 4],       "Z000"),
            0xB2: (self._or_a_d,        1,[ 4],       "Z000"),
            0xB3: (self._or_a_e,        1,[ 4],       "Z000"),
            0xB4: (self._or_a_h,        1,[ 4],       "Z000"),
            0xB5: (self._or_a_l,        1,[ 4],       "Z000"),
            0xB6: (self._or_a_mhl,      1,[ 8],       "Z000"),
            0xB7: (self._or_a_a,        1,[ 4],       "Z000"),
            0xF6: (self._or_a_d8,       2,[8],        "Z000"),
            0xB8: (self._cp_a_b,        1,[ 4],       "Z1HC"),
            0xB9: (self._cp_a_c,        1,[ 4],       "Z1HC"),
            0xBA: (self._cp_a_d,        1,[ 4],       "Z1HC"),
            0xBB: (self._cp_a_e,        1,[ 4],       "Z1HC"),
            0xBC: (self._cp_a_h,        1,[ 4],       "Z1HC"),
            0xBD: (self._cp_a_l,        1,[ 4],       "Z1HC"),
            0xBE: (self._cp_a_mhl,      1,[ 8],       "Z1HC"),
            0xBF: (self._cp_a_a,        1,[ 4],       "Z1HC"),
            0xFE: (self._cp_a_d8,       2,[8],        "Z1HC"),
            0xCD: (self._call_a16,      3,[24],       "----"),
            0xC4: (self._call_nz_a16,   3,[24,12],    "----"),
            0xCC: (self._call_z_a16,    3,[24,12],    "----"),
            0xDC: (self._call_c_a16,    3,[24,12],    "----"),
            0xD4: (self._call_nc_a16,   3,[24,12],    "----"),
            0xF5: (self._push_af,       1,[16],       "----"),
            0xC5: (self._push_bc,       1,[16],       "----"),
            0xD5: (self._push_de,       1,[16],       "----"),
            0xE5: (self._push_hl,       1,[16],       "----"),
            0xC1: (self._pop_bc,        1,[12],       "----"),
            0xD1: (self._pop_de,        1,[12],       "----"),
            0xF1: (self._pop_af,        1,[12],       "ZNHC"),
            0xE1: (self._pop_hl,        1,[12],       "----"),
            0xC2: (self._jp_nz_a16,     3,[16,12],    "----"),
            0xC3: (self._jp_a16,        3,[16],       "----"),
            0xD2: (self._jp_nc_a16,     3,[16,12],    "----"),
            0xCA: (self._jp_z_a16,      3,[16,12],    "----"),
            0xDA: (self._jp_c_a16,      3,[16,12],    "----"),
            0xE9: (self._jp_hl,         1,[4],        "----"),
            0xC0: (self._ret_nz,        1,[20,8],     "----"),
            0xC8: (self._ret_z,         1,[20,8],     "----"),
            0xD8: (self._ret_c,         1,[20,8],     "----"),
            0xD0: (self._ret_nc,        1,[20,8],     "----"),
            0xC9: (self._ret,           1,[16],       "----"),
            0xD9: (self._reti,          1,[16],       "----"),
            0xC7: (self._rst_00h,       1,[16],       "----"),
            0xCF: (self._rst_08h,       1,[16],       "----"),
            0xD7: (self._rst_10h,       1,[16],       "----"),
            0xDF: (self._rst_18h,       1,[16],       "----"),
            0xE7: (self._rst_20h,       1,[16],       "----"),
            0xEF: (self._rst_28h,       1,[16],       "----"),
            0xF7: (self._rst_30h,       1,[16],       "----"),
            0xFF: (self._rst_38h,       1,[16],       "----"),
            0xF2: (self._ldh_a_mc,      2,[8],        "----"),
            0xE2: (self._ldh_mc_a,      2,[8],        "----"),
            0xE0: (self._ldh_ma8_a,     2,[12],       "----"),
            0xF0: (self._ldh_a_ma8,     2,[12],       "----"),
            0xEA: (self._ld_ma16_a,     3,[16],       "----"),
            0xFA: (self._ld_a_ma16,     3,[16],       "----"),
            0xF8: (self._ld_hl_sp_r8,   2,[12],       "00HC"),
            0xF9: (self._ld_sp_hl,      1,[8],        "----"),
            0xF3: (self._di,            1,[4],        "----"),
            0xFB: (self._ei,            1,[4],        "----"),
            # 0xCB: (self.cb_prefix_table),
            0x76: (self._halt,          1,[ 4],       "----"),
            0x10: (self._stop_0,        2,[ 4],       "----"),
            # 0xDB: ("N/A"),
            # 0xF4: ("N/A"),
            # 0xD3: ("N/A"),
            # 0xFC: ("N/A"),
            # 0xFD: ("N/A"),
            # 0xDD: ("N/A"),
            # 0xE3: ("N/A"),
            # 0xE4: ("N/A"),
            # 0xEB: ("N/A"),
            # 0xEC: ("N/A"),
            # 0xED: ("N/A"),
        }

        # --- Dynamically generate BIT, RES, SET methods ---
        registers = ['B', 'C', 'D', 'E', 'H', 'L', 'mhl', 'A']
        for bit in range(8):
            for reg_name in registers:
                # --- BIT ---
                method_name_bit = f"_cb_bit_{bit}_{reg_name.lower()}"
                if reg_name == 'mhl':
                    def handler_bit_mhl(s, opAddr, b=bit):
                        s._cb_bit_b_r8(b, s.Bus.readByte(s.CoreWords.HL))
                        return None, None
                    setattr(self, method_name_bit, handler_bit_mhl)
                else:
                    def handler_bit_reg(s, opAddr, b=bit, r=reg_name):
                        s._cb_bit_b_r8(b, getattr(s.CoreReg, r))
                        return None, None
                    setattr(self, method_name_bit, handler_bit_reg)

                # --- RES ---
                method_name_res = f"_cb_res_{bit}_{reg_name.lower()}"
                if reg_name == 'mhl':
                    def handler_res_mhl(s, opAddr, b=bit):
                        val = s.Bus.readByte(s.CoreWords.HL)
                        res = s._cb_res_b_r8(b, val)
                        s.Bus.writeByte(s.CoreWords.HL, res)
                        return None, None
                    setattr(self, method_name_res, handler_res_mhl)
                else:
                    def handler_res_reg(s, opAddr, b=bit, r=reg_name):
                        val = getattr(s.CoreReg, r)
                        res = s._cb_res_b_r8(b, val)
                        setattr(s.CoreReg, r, res)
                        return None, None
                    setattr(self, method_name_res, handler_res_reg)

                # --- SET ---
                method_name_set = f"_cb_set_{bit}_{reg_name.lower()}"
                if reg_name == 'mhl':
                    def handler_set_mhl(s, opAddr, b=bit):
                        val = s.Bus.readByte(s.CoreWords.HL)
                        res = s._cb_set_b_r8(b, val)
                        s.Bus.writeByte(s.CoreWords.HL, res)
                        return None, None
                    setattr(self, method_name_set, handler_set_mhl)
                else:
                    def handler_set_reg(s, opAddr, b=bit, r=reg_name):
                        val = getattr(s.CoreReg, r)
                        res = s._cb_set_b_r8(b, val)
                        setattr(s.CoreReg, r, res)
                        return None, None
                    setattr(self, method_name_set, handler_set_reg)

        self.cb_prefix_table = {
            # RLC r8 / (HL)
            0x00: (self._cb_rlc_b,   2, [8],  "Z00C"), # RLC B
            0x01: (self._cb_rlc_c,   2, [8],  "Z00C"), # RLC C
            0x02: (self._cb_rlc_d,   2, [8],  "Z00C"), # RLC D
            0x03: (self._cb_rlc_e,   2, [8],  "Z00C"), # RLC E
            0x04: (self._cb_rlc_h,   2, [8],  "Z00C"), # RLC H
            0x05: (self._cb_rlc_l,   2, [8],  "Z00C"), # RLC L
            0x06: (self._cb_rlc_mhl, 2, [16], "Z00C"), # RLC (HL)
            0x07: (self._cb_rlc_a,   2, [8],  "Z00C"), # RLC A
            # RRC r8 / (HL)
            0x08: (self._cb_rrc_b,   2, [8],  "Z00C"), # RRC B
            0x09: (self._cb_rrc_c,   2, [8],  "Z00C"), # RRC C
            0x0A: (self._cb_rrc_d,   2, [8],  "Z00C"), # RRC D
            0x0B: (self._cb_rrc_e,   2, [8],  "Z00C"), # RRC E
            0x0C: (self._cb_rrc_h,   2, [8],  "Z00C"), # RRC H
            0x0D: (self._cb_rrc_l,   2, [8],  "Z00C"), # RRC L
            0x0E: (self._cb_rrc_mhl, 2, [16], "Z00C"), # RRC (HL)
            0x0F: (self._cb_rrc_a,   2, [8],  "Z00C"), # RRC A
            # RL r8 / (HL)
            0x10: (self._cb_rl_b,    2, [8],  "Z00C"), # RL B
            0x11: (self._cb_rl_c,    2, [8],  "Z00C"), # RL C
            0x12: (self._cb_rl_d,    2, [8],  "Z00C"), # RL D
            0x13: (self._cb_rl_e,    2, [8],  "Z00C"), # RL E
            0x14: (self._cb_rl_h,    2, [8],  "Z00C"), # RL H
            0x15: (self._cb_rl_l,    2, [8],  "Z00C"), # RL L
            0x16: (self._cb_rl_mhl,  2, [16], "Z00C"), # RL (HL)
            0x17: (self._cb_rl_a,    2, [8],  "Z00C"), # RL A
            # # RR r8 / (HL)
            0x18: (self._cb_rr_b,    2, [8],  "Z00C"), # RR B
            0x19: (self._cb_rr_c,    2, [8],  "Z00C"), # RR C
            0x1A: (self._cb_rr_d,    2, [8],  "Z00C"), # RR D
            0x1B: (self._cb_rr_e,    2, [8],  "Z00C"), # RR E
            0x1C: (self._cb_rr_h,    2, [8],  "Z00C"), # RR H
            0x1D: (self._cb_rr_l,    2, [8],  "Z00C"), # RR L
            0x1E: (self._cb_rr_mhl,  2, [16], "Z00C"), # RR (HL)
            0x1F: (self._cb_rr_a,    2, [8],  "Z00C"), # RR A
            # # SLA r8 / (HL)
            0x20: (self._cb_sla_b,   2, [8],  "Z00C"), # SLA B
            0x21: (self._cb_sla_c,   2, [8],  "Z00C"), # SLA C
            0x22: (self._cb_sla_d,   2, [8],  "Z00C"), # SLA D
            0x23: (self._cb_sla_e,   2, [8],  "Z00C"), # SLA E
            0x24: (self._cb_sla_h,   2, [8],  "Z00C"), # SLA H
            0x25: (self._cb_sla_l,   2, [8],  "Z00C"), # SLA L
            0x26: (self._cb_sla_mhl, 2, [16], "Z00C"), # SLA (HL)
            0x27: (self._cb_sla_a,   2, [8],  "Z00C"), # SLA A
            # # SRA r8 / (HL)
            0x28: (self._cb_sra_b,   2, [8],  "Z000"), # SRA B - Note: C flag IS affected, ZNHC = Z00C
            0x29: (self._cb_sra_c,   2, [8],  "Z000"), # SRA C
            0x2A: (self._cb_sra_d,   2, [8],  "Z000"), # SRA D
            0x2B: (self._cb_sra_e,   2, [8],  "Z000"), # SRA E
            0x2C: (self._cb_sra_h,   2, [8],  "Z000"), # SRA H
            0x2D: (self._cb_sra_l,   2, [8],  "Z000"), # SRA L
            0x2E: (self._cb_sra_mhl, 2, [16], "Z000"), # SRA (HL)
            0x2F: (self._cb_sra_a,   2, [8],  "Z000"), # SRA A
            # # SWAP r8 / (HL)
            0x30: (self._cb_swap_b,  2, [8],  "Z000"), # SWAP B
            0x31: (self._cb_swap_c,  2, [8],  "Z000"), # SWAP C
            0x32: (self._cb_swap_d,  2, [8],  "Z000"), # SWAP D
            0x33: (self._cb_swap_e,  2, [8],  "Z000"), # SWAP E
            0x34: (self._cb_swap_h,  2, [8],  "Z000"), # SWAP H
            0x35: (self._cb_swap_l,  2, [8],  "Z000"), # SWAP L
            0x36: (self._cb_swap_mhl,2, [16], "Z000"), # SWAP (HL)
            0x37: (self._cb_swap_a,  2, [8],  "Z000"), # SWAP A
            # # SRL r8 / (HL)
            0x38: (self._cb_srl_b,   2, [8],  "Z00C"), # SRL B
            0x39: (self._cb_srl_c,   2, [8],  "Z00C"), # SRL C
            0x3A: (self._cb_srl_d,   2, [8],  "Z00C"), # SRL D
            0x3B: (self._cb_srl_e,   2, [8],  "Z00C"), # SRL E
            0x3C: (self._cb_srl_h,   2, [8],  "Z00C"), # SRL H
            0x3D: (self._cb_srl_l,   2, [8],  "Z00C"), # SRL L
            0x3E: (self._cb_srl_mhl, 2, [16], "Z00C"), # SRL (HL)
            0x3F: (self._cb_srl_a,   2, [8],  "Z00C"), # SRL A
            # # BIT 0, r8 / (HL)
            0x40: (self._cb_bit_0_b,   2, [8],  "Z01-"), # BIT 0, B
            0x41: (self._cb_bit_0_c,   2, [8],  "Z01-"), # BIT 0, C
            0x42: (self._cb_bit_0_d,   2, [8],  "Z01-"), # BIT 0, D
            0x43: (self._cb_bit_0_e,   2, [8],  "Z01-"), # BIT 0, E
            0x44: (self._cb_bit_0_h,   2, [8],  "Z01-"), # BIT 0, H
            0x45: (self._cb_bit_0_l,   2, [8],  "Z01-"), # BIT 0, L
            0x46: (self._cb_bit_0_mhl, 2, [12], "Z01-"), # BIT 0, (HL)
            0x47: (self._cb_bit_0_a,   2, [8],  "Z01-"), # BIT 0, A
            # # BIT 1, r8 / (HL)
            0x48: (self._cb_bit_1_b,   2, [8],  "Z01-"), # BIT 1, B
            0x49: (self._cb_bit_1_c,   2, [8],  "Z01-"), # BIT 1, C
            0x4A: (self._cb_bit_1_d,   2, [8],  "Z01-"), # BIT 1, D
            0x4B: (self._cb_bit_1_e,   2, [8],  "Z01-"), # BIT 1, E
            0x4C: (self._cb_bit_1_h,   2, [8],  "Z01-"), # BIT 1, H
            0x4D: (self._cb_bit_1_l,   2, [8],  "Z01-"), # BIT 1, L
            0x4E: (self._cb_bit_1_mhl, 2, [12], "Z01-"), # BIT 1, (HL)
            0x4F: (self._cb_bit_1_a,   2, [8],  "Z01-"), # BIT 1, A
            # # BIT 2, r8 / (HL)
            0x50: (self._cb_bit_2_b,   2, [8],  "Z01-"), # BIT 2, B
            0x51: (self._cb_bit_2_c,   2, [8],  "Z01-"), # BIT 2, C
            0x52: (self._cb_bit_2_d,   2, [8],  "Z01-"), # BIT 2, D
            0x53: (self._cb_bit_2_e,   2, [8],  "Z01-"), # BIT 2, E
            0x54: (self._cb_bit_2_h,   2, [8],  "Z01-"), # BIT 2, H
            0x55: (self._cb_bit_2_l,   2, [8],  "Z01-"), # BIT 2, L
            0x56: (self._cb_bit_2_mhl, 2, [12], "Z01-"), # BIT 2, (HL)
            0x57: (self._cb_bit_2_a,   2, [8],  "Z01-"), # BIT 2, A
            # # BIT 3, r8 / (HL)
            0x58: (self._cb_bit_3_b,   2, [8],  "Z01-"), # BIT 3, B
            0x59: (self._cb_bit_3_c,   2, [8],  "Z01-"), # BIT 3, C
            0x5A: (self._cb_bit_3_d,   2, [8],  "Z01-"), # BIT 3, D
            0x5B: (self._cb_bit_3_e,   2, [8],  "Z01-"), # BIT 3, E
            0x5C: (self._cb_bit_3_h,   2, [8],  "Z01-"), # BIT 3, H
            0x5D: (self._cb_bit_3_l,   2, [8],  "Z01-"), # BIT 3, L
            0x5E: (self._cb_bit_3_mhl, 2, [12], "Z01-"), # BIT 3, (HL)
            0x5F: (self._cb_bit_3_a,   2, [8],  "Z01-"), # BIT 3, A
            # # BIT 4, r8 / (HL)
            0x60: (self._cb_bit_4_b,   2, [8],  "Z01-"), # BIT 4, B
            0x61: (self._cb_bit_4_c,   2, [8],  "Z01-"), # BIT 4, C
            0x62: (self._cb_bit_4_d,   2, [8],  "Z01-"), # BIT 4, D
            0x63: (self._cb_bit_4_e,   2, [8],  "Z01-"), # BIT 4, E
            0x64: (self._cb_bit_4_h,   2, [8],  "Z01-"), # BIT 4, H
            0x65: (self._cb_bit_4_l,   2, [8],  "Z01-"), # BIT 4, L
            0x66: (self._cb_bit_4_mhl, 2, [12], "Z01-"), # BIT 4, (HL)
            0x67: (self._cb_bit_4_a,   2, [8],  "Z01-"), # BIT 4, A
            # # BIT 5, r8 / (HL)
            0x68: (self._cb_bit_5_b,   2, [8],  "Z01-"), # BIT 5, B
            0x69: (self._cb_bit_5_c,   2, [8],  "Z01-"), # BIT 5, C
            0x6A: (self._cb_bit_5_d,   2, [8],  "Z01-"), # BIT 5, D
            0x6B: (self._cb_bit_5_e,   2, [8],  "Z01-"), # BIT 5, E
            0x6C: (self._cb_bit_5_h,   2, [8],  "Z01-"), # BIT 5, H
            0x6D: (self._cb_bit_5_l,   2, [8],  "Z01-"), # BIT 5, L
            0x6E: (self._cb_bit_5_mhl, 2, [12], "Z01-"), # BIT 5, (HL)
            0x6F: (self._cb_bit_5_a,   2, [8],  "Z01-"), # BIT 5, A
            # # BIT 6, r8 / (HL)
            0x70: (self._cb_bit_6_b,   2, [8],  "Z01-"), # BIT 6, B
            0x71: (self._cb_bit_6_c,   2, [8],  "Z01-"), # BIT 6, C
            0x72: (self._cb_bit_6_d,   2, [8],  "Z01-"), # BIT 6, D
            0x73: (self._cb_bit_6_e,   2, [8],  "Z01-"), # BIT 6, E
            0x74: (self._cb_bit_6_h,   2, [8],  "Z01-"), # BIT 6, H
            0x75: (self._cb_bit_6_l,   2, [8],  "Z01-"), # BIT 6, L
            0x76: (self._cb_bit_6_mhl, 2, [12], "Z01-"), # BIT 6, (HL)
            0x77: (self._cb_bit_6_a,   2, [8],  "Z01-"), # BIT 6, A
            # # BIT 7, r8 / (HL)
            0x78: (self._cb_bit_7_b,   2, [8],  "Z01-"), # BIT 7, B
            0x79: (self._cb_bit_7_c,   2, [8],  "Z01-"), # BIT 7, C
            0x7A: (self._cb_bit_7_d,   2, [8],  "Z01-"), # BIT 7, D
            0x7B: (self._cb_bit_7_e,   2, [8],  "Z01-"), # BIT 7, E
            0x7C: (self._cb_bit_7_h,   2, [8],  "Z01-"), # BIT 7, H
            0x7D: (self._cb_bit_7_l,   2, [8],  "Z01-"), # BIT 7, L
            0x7E: (self._cb_bit_7_mhl, 2, [12], "Z01-"), # BIT 7, (HL) - Note: (HL) takes 12 cycles
            0x7F: (self._cb_bit_7_a,   2, [8],  "Z01-"), # BIT 7, A
            # # RES b, r8 / (HL)
            0x80: (self._cb_res_0_b,   2, [8],  "----"), # RES 0, B
            0x81: (self._cb_res_0_c,   2, [8],  "----"), # RES 0, C
            0x82: (self._cb_res_0_d,   2, [8],  "----"), # RES 0, D
            0x83: (self._cb_res_0_e,   2, [8],  "----"), # RES 0, E
            0x84: (self._cb_res_0_h,   2, [8],  "----"), # RES 0, H
            0x85: (self._cb_res_0_l,   2, [8],  "----"), # RES 0, L
            0x86: (self._cb_res_0_mhl, 2, [16], "----"), # RES 0, (HL)
            0x87: (self._cb_res_0_a,   2, [8],  "----"), # RES 0, A
            # # RES 1, r8 / (HL)
            0x88: (self._cb_res_1_b,   2, [8],  "----"), # RES 1, B
            0x89: (self._cb_res_1_c,   2, [8],  "----"), # RES 1, C
            0x8A: (self._cb_res_1_d,   2, [8],  "----"), # RES 1, D
            0x8B: (self._cb_res_1_e,   2, [8],  "----"), # RES 1, E
            0x8C: (self._cb_res_1_h,   2, [8],  "----"), # RES 1, H
            0x8D: (self._cb_res_1_l,   2, [8],  "----"), # RES 1, L
            0x8E: (self._cb_res_1_mhl, 2, [16], "----"), # RES 1, (HL)
            0x8F: (self._cb_res_1_a,   2, [8],  "----"), # RES 1, A
            # # RES 2, r8 / (HL)
            0x90: (self._cb_res_2_b,   2, [8],  "----"), # RES 2, B
            0x91: (self._cb_res_2_c,   2, [8],  "----"), # RES 2, C
            0x92: (self._cb_res_2_d,   2, [8],  "----"), # RES 2, D
            0x93: (self._cb_res_2_e,   2, [8],  "----"), # RES 2, E
            0x94: (self._cb_res_2_h,   2, [8],  "----"), # RES 2, H
            0x95: (self._cb_res_2_l,   2, [8],  "----"), # RES 2, L
            0x96: (self._cb_res_2_mhl, 2, [16], "----"), # RES 2, (HL)
            0x97: (self._cb_res_2_a,   2, [8],  "----"), # RES 2, A
            # # RES 3, r8 / (HL)
            0x98: (self._cb_res_3_b,   2, [8],  "----"), # RES 3, B
            0x99: (self._cb_res_3_c,   2, [8],  "----"), # RES 3, C
            0x9A: (self._cb_res_3_d,   2, [8],  "----"), # RES 3, D
            0x9B: (self._cb_res_3_e,   2, [8],  "----"), # RES 3, E
            0x9C: (self._cb_res_3_h,   2, [8],  "----"), # RES 3, H
            0x9D: (self._cb_res_3_l,   2, [8],  "----"), # RES 3, L
            0x9E: (self._cb_res_3_mhl, 2, [16], "----"), # RES 3, (HL)
            0x9F: (self._cb_res_3_a,   2, [8],  "----"), # RES 3, A
            # # RES 4, r8 / (HL)
            0xA0: (self._cb_res_4_b,   2, [8],  "----"), # RES 4, B
            0xA1: (self._cb_res_4_c,   2, [8],  "----"), # RES 4, C
            0xA2: (self._cb_res_4_d,   2, [8],  "----"), # RES 4, D
            0xA3: (self._cb_res_4_e,   2, [8],  "----"), # RES 4, E
            0xA4: (self._cb_res_4_h,   2, [8],  "----"), # RES 4, H
            0xA5: (self._cb_res_4_l,   2, [8],  "----"), # RES 4, L
            0xA6: (self._cb_res_4_mhl, 2, [16], "----"), # RES 4, (HL)
            0xA7: (self._cb_res_4_a,   2, [8],  "----"), # RES 4, A
            # # RES 5, r8 / (HL)
            0xA8: (self._cb_res_5_b,   2, [8],  "----"), # RES 5, B
            0xA9: (self._cb_res_5_c,   2, [8],  "----"), # RES 5, C
            0xAA: (self._cb_res_5_d,   2, [8],  "----"), # RES 5, D
            0xAB: (self._cb_res_5_e,   2, [8],  "----"), # RES 5, E
            0xAC: (self._cb_res_5_h,   2, [8],  "----"), # RES 5, H
            0xAD: (self._cb_res_5_l,   2, [8],  "----"), # RES 5, L
            0xAE: (self._cb_res_5_mhl, 2, [16], "----"), # RES 5, (HL)
            0xAF: (self._cb_res_5_a,   2, [8],  "----"), # RES 5, A
            # # RES 6, r8 / (HL)
            0xB0: (self._cb_res_6_b,   2, [8],  "----"), # RES 6, B
            0xB1: (self._cb_res_6_c,   2, [8],  "----"), # RES 6, C
            0xB2: (self._cb_res_6_d,   2, [8],  "----"), # RES 6, D
            0xB3: (self._cb_res_6_e,   2, [8],  "----"), # RES 6, E
            0xB4: (self._cb_res_6_h,   2, [8],  "----"), # RES 6, H
            0xB5: (self._cb_res_6_l,   2, [8],  "----"), # RES 6, L
            0xB6: (self._cb_res_6_mhl, 2, [16], "----"), # RES 6, (HL)
            0xB7: (self._cb_res_6_a,   2, [8],  "----"), # RES 6, A
            # # RES 7, r8 / (HL)
            0xB8: (self._cb_res_7_b,   2, [8],  "----"), # RES 7, B
            0xB9: (self._cb_res_7_c,   2, [8],  "----"), # RES 7, C
            0xBA: (self._cb_res_7_d,   2, [8],  "----"), # RES 7, D
            0xBB: (self._cb_res_7_e,   2, [8],  "----"), # RES 7, E
            0xBC: (self._cb_res_7_h,   2, [8],  "----"), # RES 7, H
            0xBD: (self._cb_res_7_l,   2, [8],  "----"), # RES 7, L
            0xBE: (self._cb_res_7_mhl, 2, [16], "----"), # RES 7, (HL)
            0xBF: (self._cb_res_7_a,   2, [8],  "----"), # RES 7, A
            # # SET b, r8 / (HL)
            0xC0: (self._cb_set_0_b,   2, [8],  "----"), # SET 0, B
            0xC1: (self._cb_set_0_c,   2, [8],  "----"), # SET 0, C
            0xC2: (self._cb_set_0_d,   2, [8],  "----"), # SET 0, D
            0xC3: (self._cb_set_0_e,   2, [8],  "----"), # SET 0, E
            0xC4: (self._cb_set_0_h,   2, [8],  "----"), # SET 0, H
            0xC5: (self._cb_set_0_l,   2, [8],  "----"), # SET 0, L
            0xC6: (self._cb_set_0_mhl, 2, [16], "----"), # SET 0, (HL)
            0xC7: (self._cb_set_0_a,   2, [8],  "----"), # SET 0, A
            # # SET 1, r8 / (HL)
            0xC8: (self._cb_set_1_b,   2, [8],  "----"), # SET 1, B
            0xC9: (self._cb_set_1_c,   2, [8],  "----"), # SET 1, C
            0xCA: (self._cb_set_1_d,   2, [8],  "----"), # SET 1, D
            0xCB: (self._cb_set_1_e,   2, [8],  "----"), # SET 1, E
            0xCC: (self._cb_set_1_h,   2, [8],  "----"), # SET 1, H
            0xCD: (self._cb_set_1_l,   2, [8],  "----"), # SET 1, L
            0xCE: (self._cb_set_1_mhl, 2, [16], "----"), # SET 1, (HL)
            0xCF: (self._cb_set_1_a,   2, [8],  "----"), # SET 1, A
            # # SET 2, r8 / (HL)
            0xD0: (self._cb_set_2_b,   2, [8],  "----"), # SET 2, B
            0xD1: (self._cb_set_2_c,   2, [8],  "----"), # SET 2, C
            0xD2: (self._cb_set_2_d,   2, [8],  "----"), # SET 2, D
            0xD3: (self._cb_set_2_e,   2, [8],  "----"), # SET 2, E
            0xD4: (self._cb_set_2_h,   2, [8],  "----"), # SET 2, H
            0xD5: (self._cb_set_2_l,   2, [8],  "----"), # SET 2, L
            0xD6: (self._cb_set_2_mhl, 2, [16], "----"), # SET 2, (HL)
            0xD7: (self._cb_set_2_a,   2, [8],  "----"), # SET 2, A
            # # SET 3, r8 / (HL)
            0xD8: (self._cb_set_3_b,   2, [8],  "----"), # SET 3, B
            0xD9: (self._cb_set_3_c,   2, [8],  "----"), # SET 3, C
            0xDA: (self._cb_set_3_d,   2, [8],  "----"), # SET 3, D
            0xDB: (self._cb_set_3_e,   2, [8],  "----"), # SET 3, E
            0xDC: (self._cb_set_3_h,   2, [8],  "----"), # SET 3, H
            0xDD: (self._cb_set_3_l,   2, [8],  "----"), # SET 3, L
            0xDE: (self._cb_set_3_mhl, 2, [16], "----"), # SET 3, (HL)
            0xDF: (self._cb_set_3_a,   2, [8],  "----"), # SET 3, A
            # # SET 4, r8 / (HL)
            0xE0: (self._cb_set_4_b,   2, [8],  "----"), # SET 4, B
            0xE1: (self._cb_set_4_c,   2, [8],  "----"), # SET 4, C
            0xE2: (self._cb_set_4_d,   2, [8],  "----"), # SET 4, D
            0xE3: (self._cb_set_4_e,   2, [8],  "----"), # SET 4, E
            0xE4: (self._cb_set_4_h,   2, [8],  "----"), # SET 4, H
            0xE5: (self._cb_set_4_l,   2, [8],  "----"), # SET 4, L
            0xE6: (self._cb_set_4_mhl, 2, [16], "----"), # SET 4, (HL)
            0xE7: (self._cb_set_4_a,   2, [8],  "----"), # SET 4, A
            # # SET 5, r8 / (HL)
            0xE8: (self._cb_set_5_b,   2, [8],  "----"), # SET 5, B
            0xE9: (self._cb_set_5_c,   2, [8],  "----"), # SET 5, C
            0xEA: (self._cb_set_5_d,   2, [8],  "----"), # SET 5, D
            0xEB: (self._cb_set_5_e,   2, [8],  "----"), # SET 5, E
            0xEC: (self._cb_set_5_h,   2, [8],  "----"), # SET 5, H
            0xED: (self._cb_set_5_l,   2, [8],  "----"), # SET 5, L
            0xEE: (self._cb_set_5_mhl, 2, [16], "----"), # SET 5, (HL)
            0xEF: (self._cb_set_5_a,   2, [8],  "----"), # SET 5, A
            # # SET 6, r8 / (HL)
            0xF0: (self._cb_set_6_b,   2, [8],  "----"), # SET 6, B
            0xF1: (self._cb_set_6_c,   2, [8],  "----"), # SET 6, C
            0xF2: (self._cb_set_6_d,   2, [8],  "----"), # SET 6, D
            0xF3: (self._cb_set_6_e,   2, [8],  "----"), # SET 6, E
            0xF4: (self._cb_set_6_h,   2, [8],  "----"), # SET 6, H
            0xF5: (self._cb_set_6_l,   2, [8],  "----"), # SET 6, L
            0xF6: (self._cb_set_6_mhl, 2, [16], "----"), # SET 6, (HL)
            0xF7: (self._cb_set_6_a,   2, [8],  "----"), # SET 6, A
            # # SET 7, r8 / (HL)
            0xF8: (self._cb_set_7_b,   2, [8],  "----"), # SET 7, B
            0xF9: (self._cb_set_7_c,   2, [8],  "----"), # SET 7, C
            0xFA: (self._cb_set_7_d,   2, [8],  "----"), # SET 7, D
            0xFB: (self._cb_set_7_e,   2, [8],  "----"), # SET 7, E
            0xFC: (self._cb_set_7_h,   2, [8],  "----"), # SET 7, H
            0xFD: (self._cb_set_7_l,   2, [8],  "----"), # SET 7, L
            0xFE: (self._cb_set_7_mhl, 2, [16], "----"), # SET 7, (HL)
            0xFF: (self._cb_set_7_a,   2, [8],  "----"), # SET 7, A
        }

        # ---  opCode Implementations --- #

    def _nop(self, operandAddr):
        # Program Counters won't do anything. Step Function will increment the cycles correctly
        return None, None

    def _ld_r16_d16(self, operandAddr):
        lsB = self.Bus.readByte(operandAddr)
        msB = self.Bus.readByte(operandAddr+1)
        return (msB.astype(Word) << 8) | lsB

    # Load Immediate d16 value into BC Register
    def _ld_bc_d16(self, operandAddr):
        self.CoreWords.BC = self._ld_r16_d16(operandAddr)
        return None, None
    def _ld_de_d16(self, operandAddr):
        self.CoreWords.DE = self._ld_r16_d16(operandAddr)
        return None, None

    def _ld_hl_d16(self, operandAddr):
        self.CoreWords.HL = self._ld_r16_d16(operandAddr)
        return None, None
    def _ld_sp_d16(self, operandAddr):
        self.CoreWords.SP = self._ld_r16_d16(operandAddr)
        return None, None
    # Increment 16 bit register by 1
    def _inc_r16(self,register):
        return (int(register) + 1) & 0xFFFF

    def _inc_bc(self, operandAddr):
        self.CoreWords.BC = self._inc_r16(self.CoreWords.BC)
        return None, None
    def _inc_de(self, operandAddr):
        self.CoreWords.DE = self._inc_r16(self.CoreWords.DE)
        return None, None
    def _inc_hl(self, operandAddr):
        self.CoreWords.HL = self._inc_r16(self.CoreWords.HL)
        return None, None
    def _inc_sp(self, operandAddr):
        self.CoreWords.SP = self._inc_r16(self.CoreWords.SP)
        return None, None
            
    # Increment 8 bit register by 1
    def _inc_reg8(self,register):
        original = register
        register = (Word(register) + 1) & 0xFF

        self.Flags.z = 1 if register == 0 else 0
        self.Flags.n = 0
        self.Flags.h = 1 if (original & 0x0F) == 0xF else 0

        return register
        
    def _inc_a(self,operandAddr):
        self.CoreReg.A = self._inc_reg8(self.CoreReg.A)
        return None, None
    def _inc_b(self,operandAddr):
        self.CoreReg.B = self._inc_reg8(self.CoreReg.B)
        return None, None
    def _inc_c(self,operandAddr):
        self.CoreReg.C = self._inc_reg8(self.CoreReg.C)
        return None, None
    def _inc_d(self,operandAddr):
        self.CoreReg.D = self._inc_reg8(self.CoreReg.D)
        return None, None
    def _inc_e(self,operandAddr):
        self.CoreReg.E = self._inc_reg8(self.CoreReg.E)
        return None, None
    def _inc_l(self,operandAddr):
        self.CoreReg.L = self._inc_reg8(self.CoreReg.L)
        return None, None
    def _inc_h(self,operandAddr):
        self.CoreReg.H = self._inc_reg8(self.CoreReg.H)
        return None, None

     # Helper: Decrement 8 bit value, set flags, return result
    def _dec_reg8(self, value):
        original = value
        result = (int(value) - 1) & 0xFF # Calculate result with wrap-around

        # Set flags
        self.Flags.n = 1 # N is always set for DEC
        self.Flags.z = 1 if result == 0 else 0
        # H is set if borrow from bit 4 (i.e., lower nibble was 0x0 before dec)
        self.Flags.h = 1 if (original & 0x0F) == 0 else 0 
        # C is not affected by DEC r8

        return result

    # Opcode Implementations
    def _dec_a(self, operandAddr):
        self.CoreReg.A = self._dec_reg8(self.CoreReg.A)
        return None, None # Standard return for PC/cycle overrides

    def _dec_b(self, operandAddr):
        self.CoreReg.B = self._dec_reg8(self.CoreReg.B)
        return None, None

    def _dec_c(self, operandAddr):
        self.CoreReg.C = self._dec_reg8(self.CoreReg.C)
        return None, None

    def _dec_d(self, operandAddr):
        self.CoreReg.D = self._dec_reg8(self.CoreReg.D)
        return None, None

    def _dec_e(self, operandAddr):
        self.CoreReg.E = self._dec_reg8(self.CoreReg.E)
        return None, None

    def _dec_h(self, operandAddr):
        self.CoreReg.H = self._dec_reg8(self.CoreReg.H)
        return None, None

    def _dec_l(self, operandAddr):
        self.CoreReg.L = self._dec_reg8(self.CoreReg.L)
        return None, None
    
    def _dec_r16(self,register):
        return (int(register) - 1) & 0xFFFF

    def _dec_bc(self, operandAddr):
        self.CoreWords.BC = self._dec_r16(self.CoreWords.BC)
        return None, None    
    def _dec_de(self, operandAddr):
        self.CoreWords.DE = self._dec_r16(self.CoreWords.DE)
        return None, None    
    def _dec_hl(self, operandAddr):
        self.CoreWords.HL = self._dec_r16(self.CoreWords.HL)
        return None, None    
    def _dec_sp(self, operandAddr):
        self.CoreWords.SP = self._dec_r16(self.CoreWords.SP)
        return None,None
    
    def _ld_r8_d8(self, operandAddr):
        # Read Operand Data and return
        d8 = self.Bus.readByte(operandAddr)
        return d8
    def _ld_a_d8(self,operandAddr):
        self.CoreReg.A = self._ld_r8_d8(operandAddr)
        return None, None
    def _ld_b_d8(self,operandAddr):
        self.CoreReg.B = self._ld_r8_d8(operandAddr)
        return None, None
    def _ld_c_d8(self,operandAddr):
        self.CoreReg.C = self._ld_r8_d8(operandAddr)
        return None, None
    def _ld_d_d8(self,operandAddr):
        self.CoreReg.D = self._ld_r8_d8(operandAddr)
        return None, None
    def _ld_e_d8(self,operandAddr):
        self.CoreReg.E = self._ld_r8_d8(operandAddr)
        return None, None
    def _ld_l_d8(self,operandAddr):
        self.CoreReg.L = self._ld_r8_d8(operandAddr)
        return None, None
    def _ld_h_d8(self,operandAddr):
        self.CoreReg.H = self._ld_r8_d8(operandAddr)
        return None, None

    def _inc_mhl(self,operandAddr):
        # Increment Value stored in HL Location
        original = self.Bus.readByte(self.CoreWords.HL)
        result = (Word(original) + 1) & 0xFF

        self.Bus.writeByte(self.CoreWords.HL, result)

        self.Flags.z = 1 if (result == 0x00) else 0
        self.Flags.n = 0
        self.Flags.h = 1 if (original & 0xF) == 0xF else 0 # lower nibble of 0 requires a borrow from upper nibble
        return None, None

    def _dec_mhl(self,operandAddr):
        # Decrement Value stored in HL Location
        original = self.Bus.readByte(self.CoreWords.HL)
        result = (int(original) - 1) & 0xFF

        self.Bus.writeByte(self.CoreWords.HL, result)

        self.Flags.z = 1 if result == 0x00 else 0
        self.Flags.n = 1
        self.Flags.h = 1 if (original & 0xF) == 0x0 else 0
        return None, None

    # Adds r16 register to the value stored in hl
    def _add_hl_r16(self, register):
        original = self.CoreWords.HL
        self.CoreWords.HL = (int(original) + int(register)) & 0xFFFF

        # Half-carry: Carry from bit 11 to 12
        self.Flags.h = 1 if ((original ^ register ^ self.CoreWords.HL) & 0x1000) else 0
        # Full-carry: Carry from bit 15 to 16
        self.Flags.c = 1 if register > (0xFFFF - original) else 0
        self.Flags.n = 0

    def _add_hl_bc(self,operandAddr):
        self._add_hl_r16(self.CoreWords.BC)
        return None, None
    def _add_hl_de(self,operandAddr):
        self._add_hl_r16(self.CoreWords.DE)
        return None, None
    def _add_hl_hl(self,operandAddr):
        self._add_hl_r16(self.CoreWords.HL)
        return None, None
    def _add_hl_sp(self,operandAddr):
        self._add_hl_r16(self.CoreWords.SP)
        return None, None

    def _ld_mhl_d8(self,operandAddr):
        d8 = self.Bus.readByte(operandAddr)
        self.Bus.writeByte(self.CoreWords.HL, d8)

    # Rotates Accumulator Register to the left by 1 and sets bit 7 to bit 0
    def _rlca(self,operandAddr):
        original = self.CoreReg.A

        bit7 = (original & 0x80) >> 7
        self.CoreReg.A = ((self.CoreReg.A << 1) & 0xFE) | bit7

        self.Flags.z = 0
        self.Flags.h = 0
        self.Flags.n = 0
        self.Flags.c = bit7
        return None, None

        # Rotates Accumulator Register to the right by 1 and sets bit 0 to bit 7
    def _rrca(self,operandAddr):
        original = self.CoreReg.A

        bit0 = (original & 0x01)
        self.CoreReg.A = ((self.CoreReg.A >> 1) & 0x7F) | (bit0 << 7)

        self.Flags.z = 0
        self.Flags.h = 0
        self.Flags.n = 0
        self.Flags.c = bit0
        return None, None


    # Rotates Accumulator to the left. Setting bit0 of the accumulator to the original Carry Flag value,
    # and setting the new Carry Flag value to bit 7
    # C Flag <-- [ b7 <-- b6 <-- ... <-- b1 <-- b0 <-- C Flag ]
    #        Accumulator (Register A)

    def _rla(self,operandAddr):
        originalCarry = self.Flags.c 
        orignal = self.CoreReg.A

        bit7 = (orignal & 0x80) >> 7
        self.CoreReg.A = ((self.CoreReg.A << 1) & 0xFE) | originalCarry # set bit 0 to originalCarry Value

        self.Flags.z = 0
        self.Flags.h = 0
        self.Flags.n = 0
        self.Flags.c = bit7
        return None, None

    # Rotates Accumulator to the right. Setting bit7 of the accumulator to the original Carry Flag value,
    # and setting the new Carry Flag value to bit 0
    # C Flag <-- [ b7 <-- b6 <-- ... <-- b1 <-- b0 <-- C Flag ]
    #        Accumulator (Register A)

    def _rra(self,operandAddr):
        originalCarry = self.Flags.c 
        orignal = self.CoreReg.A

        bit0 = (orignal & 0x1)
        self.CoreReg.A = ((self.CoreReg.A >> 1) & 0x7F) | (originalCarry << 7) # set bit 7 to originalCarry Value

        self.Flags.z = 0
        self.Flags.h = 0
        self.Flags.n = 0
        self.Flags.c = bit0
        return None, None

        # Load A into address pointed to by memory location in register pair
#    #   BC, DE, HL+, HL-, SP
    #   HL+ increments the HL register after writing the value
    #   HL- decrements the HL register after writing the value

    def _ld_mr16_a(self, register):
        self.Bus.writeByte(register, self.CoreReg.A)
        return None, None

    def _ld_mbc_a(self, operandAddr):
        self._ld_mr16_a(self.CoreWords.BC)
        return None, None

    def _ld_mde_a(self, operandAddr):
        self._ld_mr16_a(self.CoreWords.DE)
        return None, None

    def _ld_mhlp_a(self, operandAddr):
        self._ld_mr16_a(self.CoreWords.HL)
        self.CoreWords.HL = (self.CoreWords.HL + 1) & 0xFFFF
        return None, None

    def _ld_mhlm_a(self, operandAddr):
        self._ld_mr16_a(self.CoreWords.HL)
        self.CoreWords.HL = (self.CoreWords.HL - 1) & 0xFFFF
        return None, None
    
    def _ld_mhl_a(self, operandAddr):
        self._ld_mr16_a(self.CoreWords.HL)
        return None, None

    def _ld_m16_sp(self, operandAddr):
        self.Bus.writeWord(operandAddr, self.CoreWords.SP)
        return None, None

    def _ld_a_mr16(self,register):
        byteValue = self.Bus.readByte(register)
        self.CoreReg.A = byteValue
        return None, None

    def _ld_a_mbc(self,operandAddr):
        self._ld_a_mr16(self.CoreWords.BC)
        return None, None

    def _ld_a_mde(self,operandAddr):
        self._ld_a_mr16(self.CoreWords.DE)
        return None, None

    def _ld_a_mhlp(self,operandAddr):
        self._ld_a_mr16(self.CoreWords.HL)
        self.CoreWords.HL = (self.CoreWords.HL + 1) & 0xFFFF
        return None, None

    def _ld_a_mhlm(self,operandAddr):
        self._ld_a_mr16(self.CoreWords.HL)
        self.CoreWords.HL = (self.CoreWords.HL - 1) & 0xFFFF
        return None, None

    def _ld_a_mhl(self,operandAddr):
        self._ld_a_mr16(self.CoreWords.HL)
        return None, None

    def _stop_0(self,operandAddr):
        # STOP the CPU and screen until a button is pressed.
        # This is a 2-byte instruction, the step function will advance PC by 2.
        self.Stopped = True
        # TODO: The PPU should also be notified to turn off the LCD.
        return None, None

    # jump related to provided 8 bit signed value
    #   PC <-- PC + signed 8-bit value
    def _jr_r8(self,operandAddr):
        offset = np.int8(self.Bus.readByte(operandAddr))
        target_pc = (self.CoreWords.PC + 2 + offset) & 0xFFFF
        return target_pc, 12

    # Jump relative to provided 8 bit signed value if the Zero Flag is not set
    #   PC <-- PC + signed 8-bit value

    def _jr_nz_r8(self,operandAddr):
        if self.Flags.z == 0:
            offset = np.int8(self.Bus.readByte(operandAddr))
            target_pc = (self.CoreWords.PC + 2 + offset) & 0xFFFF
            return target_pc, 12
        else:
            return None, 8 # Cycle Override

    # Jump relative to provided 8 bit signed value if the Carry Flag is not set
    def _jr_nc_r8(self,operandAddr):
        if self.Flags.c == 0:
            offset = np.int8(self.Bus.readByte(operandAddr))
            target_pc = (self.CoreWords.PC + 2 + offset) & 0xFFFF
            return target_pc, 12
        else: 
            return None, 8

    # Jump relative to provided 8 bit signed value if the Zero Flag is set
    def _jr_z_r8(self,operandAddr):
        if self.Flags.z == 1:
            offset = np.int8(self.Bus.readByte(operandAddr))
            target_pc = (self.CoreWords.PC + 2 + offset) & 0xFFFF
            return target_pc, 12
        else:
            return None, 8

    # Jump relative to provided 8 bit signed value if the Carry Flag is set
    def _jr_c_r8(self,operandAddr):
        if self.Flags.c == 1:
            offset = np.int8(self.Bus.readByte(operandAddr))
            target_pc = (self.CoreWords.PC + 2 + offset) & 0xFFFF
            return target_pc, 12
        else:
            return None, 8


    # Decimal Adjust Accumulator
    #   Used for adjusting accumulator value to Binary Coded Decimal when desired
    def _daa(self, operandAddr):

        adjust = 0
        if self.Flags.h or (self.CoreReg.A & 0x0F) > 9:
            adjust |= 0x06  # Add 6 to the lower nibble if half-carry is set or lower nibble > 9
        if self.Flags.c or self.CoreReg.A > 0x99:
            adjust |= 0x60  # Add 6 to the upper nibble if carry is set or A > 99
            self.Flags.c = 1  # Set carry flag if upper nibble adjustment is applied

        if self.Flags.n:
            self.CoreReg.A = (self.CoreReg.A - adjust) & 0xFF  # Subtract adjustment if in subtraction mode
        else:
            self.CoreReg.A = (self.CoreReg.A + adjust) & 0xFF  # Add adjustment if in addition mode

        self.Flags.z = 1 if self.CoreReg.A == 0 else 0  # Set zero flag if result is zero
        self.Flags.h = 0  # Half-carry flag is always cleared after DAA

    # load 8 bit register with value of another 8 bit register
    #   r8 <-- r8
    def _ld_a_b(self,operandAddr):  
        self.CoreReg.A = self.CoreReg.B
        return None, None
    def _ld_a_c(self,operandAddr):  
        self.CoreReg.A = self.CoreReg.C
        return None, None
    def _ld_a_d(self,operandAddr):  
        self.CoreReg.A = self.CoreReg.D
        return None, None
    def _ld_a_e(self,operandAddr):  
        self.CoreReg.A = self.CoreReg.E
        return None, None
    def _ld_a_h(self,operandAddr):  
        self.CoreReg.A = self.CoreReg.H
        return None, None
    def _ld_a_l(self,operandAddr):  
        self.CoreReg.A = self.CoreReg.L
        return None, None
    def _ld_b_b(self,operandAddr):  
        self.CoreReg.B = self.CoreReg.B
        return None, None
    def _ld_b_c(self,operandAddr):  
        self.CoreReg.B = self.CoreReg.C
        return None, None
    def _ld_b_d(self,operandAddr):  
        self.CoreReg.B = self.CoreReg.D
        return None, None
    def _ld_b_e(self,operandAddr):  
        self.CoreReg.B = self.CoreReg.E
        return None, None
    def _ld_b_h(self,operandAddr):  
        self.CoreReg.B = self.CoreReg.H
        return None, None
    def _ld_b_l(self,operandAddr):  
        self.CoreReg.B = self.CoreReg.L
        return None, None
    def _ld_c_b(self,operandAddr):  
        self.CoreReg.C = self.CoreReg.B
        return None, None
    def _ld_c_c(self,operandAddr):  
        self.CoreReg.C = self.CoreReg.C
        return None, None
    def _ld_c_d(self,operandAddr):  
        self.CoreReg.C = self.CoreReg.D
        return None, None
    def _ld_c_e(self,operandAddr):  
        self.CoreReg.C = self.CoreReg.E
        return None, None
    def _ld_c_h(self,operandAddr):  
        self.CoreReg.C = self.CoreReg.H
        return None, None
    def _ld_c_l(self,operandAddr):  
        self.CoreReg.C = self.CoreReg.L
        return None, None
    def _ld_d_b(self,operandAddr):  
        self.CoreReg.D = self.CoreReg.B
        return None, None
    def _ld_d_c(self,operandAddr):  
        self.CoreReg.D = self.CoreReg.C
        return None, None
    def _ld_d_d(self,operandAddr):  
        self.CoreReg.D = self.CoreReg.D
        return None, None
    def _ld_d_e(self,operandAddr):  
        self.CoreReg.D = self.CoreReg.E
        return None, None
    def _ld_d_h(self,operandAddr):  
        self.CoreReg.D = self.CoreReg.H
        return None, None
    def _ld_d_l(self,operandAddr):  
        self.CoreReg.D = self.CoreReg.L
        return None, None
    def _ld_e_b(self,operandAddr):  
        self.CoreReg.E = self.CoreReg.B
        return None, None
    def _ld_e_c(self,operandAddr):  
        self.CoreReg.E = self.CoreReg.C
        return None, None
    def _ld_e_d(self,operandAddr):  
        self.CoreReg.E = self.CoreReg.D
        return None, None
    def _ld_e_e(self,operandAddr):  
        self.CoreReg.E = self.CoreReg.E
        return None, None
    def _ld_e_h(self,operandAddr):  
        self.CoreReg.E = self.CoreReg.H
        return None, None
    def _ld_e_l(self,operandAddr):  
        self.CoreReg.E = self.CoreReg.L
        return None, None
    def _ld_h_b(self,operandAddr):  
        self.CoreReg.H = self.CoreReg.B
        return None, None
    def _ld_h_c(self,operandAddr):  
        self.CoreReg.H = self.CoreReg.C
        return None, None
    def _ld_h_d(self,operandAddr):  
        self.CoreReg.H = self.CoreReg.D
        return None, None
    def _ld_h_e(self,operandAddr):  
        self.CoreReg.H = self.CoreReg.E
        return None, None
    def _ld_h_h(self,operandAddr):  
        self.CoreReg.H = self.CoreReg.H
        return None, None
    def _ld_h_l(self,operandAddr):  
        self.CoreReg.H = self.CoreReg.L
        return None, None
    def _ld_l_b(self,operandAddr):  
        self.CoreReg.L = self.CoreReg.B
        return None, None
    def _ld_l_c(self,operandAddr):  
        self.CoreReg.L = self.CoreReg.C
        return None, None
    def _ld_l_d(self,operandAddr):  
        self.CoreReg.L = self.CoreReg.D
        return None, None
    def _ld_l_e(self,operandAddr):  
        self.CoreReg.L = self.CoreReg.E
        return None, None
    def _ld_l_h(self,operandAddr):  
        self.CoreReg.L = self.CoreReg.H
        return None, None
    def _ld_l_l(self,operandAddr):  
        self.CoreReg.L = self.CoreReg.L
        return None, None
    def _ld_a_a(self,operandAddr):
        self.CoreReg.A = self.CoreReg.A
        return None, None
    def _ld_b_a(self,operandAddr):  
        self.CoreReg.B = self.CoreReg.A
        return None, None
    def _ld_c_a(self,operandAddr):  
        self.CoreReg.C = self.CoreReg.A
        return None, None
    def _ld_d_a(self,operandAddr):  
        self.CoreReg.D = self.CoreReg.A
        return None, None
    def _ld_e_a(self,operandAddr):  
        self.CoreReg.E = self.CoreReg.A
        return None, None
    def _ld_h_a(self,operandAddr):  
        self.CoreReg.H = self.CoreReg.A
        return None, None
    def _ld_l_a(self,operandAddr):  
        self.CoreReg.L = self.CoreReg.A
        return None, None

    #======================================================================
    # LD r, (HL)
    #======================================================================
    def _ld_a_mhl(self, operandAddr): self.CoreReg.A = self.Bus.readByte(self.CoreWords.HL); return None, None
    def _ld_b_mhl(self, operandAddr): self.CoreReg.B = self.Bus.readByte(self.CoreWords.HL); return None, None
    def _ld_c_mhl(self, operandAddr): self.CoreReg.C = self.Bus.readByte(self.CoreWords.HL); return None, None
    def _ld_d_mhl(self, operandAddr): self.CoreReg.D = self.Bus.readByte(self.CoreWords.HL); return None, None
    def _ld_e_mhl(self, operandAddr): self.CoreReg.E = self.Bus.readByte(self.CoreWords.HL); return None, None
    def _ld_h_mhl(self, operandAddr):
        mhl_value = self.Bus.readByte(self.CoreWords.HL)
        self.CoreReg.H = mhl_value
        return None, None
    def _ld_l_mhl(self, operandAddr): 
        mhl_value = self.Bus.readByte(self.CoreWords.HL)
        self.CoreReg.L = mhl_value
        return None, None

    #======================================================================
    # LD (HL), r
    #======================================================================
    def _ld_mhl_a(self, operandAddr): self.Bus.writeByte(self.CoreWords.HL, self.CoreReg.A); return None, None
    def _ld_mhl_b(self, operandAddr): self.Bus.writeByte(self.CoreWords.HL, self.CoreReg.B); return None, None
    def _ld_mhl_c(self, operandAddr): self.Bus.writeByte(self.CoreWords.HL, self.CoreReg.C); return None, None
    def _ld_mhl_d(self, operandAddr): self.Bus.writeByte(self.CoreWords.HL, self.CoreReg.D); return None, None
    def _ld_mhl_e(self, operandAddr): self.Bus.writeByte(self.CoreWords.HL, self.CoreReg.E); return None, None
    def _ld_mhl_h(self, operandAddr): self.Bus.writeByte(self.CoreWords.HL, self.CoreReg.H); return None, None
    def _ld_mhl_l(self, operandAddr): self.Bus.writeByte(self.CoreWords.HL, self.CoreReg.L); return None, None
    
    def _add_a_r8(self,register):
        # Add the value of the provided 8 bit register to the accumulator
        original = int(self.CoreReg.A)
        reg = int(register)
        total = original + reg
        result = total & 0xFF

        # Set flags
        self.Flags.z = 1 if result == 0 else 0
        self.Flags.n = 0
        self.Flags.h = 1 if (original & 0x0F) + (register & 0x0F) > 0x0F else 0 # Carry from bit 3 to 4
        
        #Cast original as uint16 to prevent overflow during addition
        self.Flags.c = 1 if total > 0xFF else 0

        return Byte(result)
    
    def _add_a_a(self,operandAddr):
        self.CoreReg.A = self._add_a_r8(self.CoreReg.A)
        return None, None
    def _add_a_b(self,operandAddr):
        self.CoreReg.A = self._add_a_r8(self.CoreReg.B)
        return None, None
    def _add_a_c(self,operandAddr):
        self.CoreReg.A = self._add_a_r8(self.CoreReg.C)
        return None, None
    def _add_a_d(self,operandAddr):
        self.CoreReg.A = self._add_a_r8(self.CoreReg.D)
        return None, None
    def _add_a_e(self,operandAddr):
        self.CoreReg.A = self._add_a_r8(self.CoreReg.E)
        return None, None
    def _add_a_h(self,operandAddr):
        self.CoreReg.A = self._add_a_r8(self.CoreReg.H)
        return None, None
    def _add_a_l(self,operandAddr):
        self.CoreReg.A = self._add_a_r8(self.CoreReg.L)
        return None, None
    def _add_a_mhl(self,operandAddr):
        self.CoreReg.A = self._add_a_r8(self.Bus.readByte(self.CoreWords.HL))
        return None, None
    def _add_a_d8(self,operandAddr):
        d8 = self.Bus.readByte(operandAddr)
        self.CoreReg.A = self._add_a_r8(d8)
        return None, None

    def _adc_a_r8(self,register):
        # Add the value of the provided 8 bit register to the accumulator with carry\
        # Cast to ints for intermediate arithmentic to prevent overflow
        original = int(self.CoreReg.A)
        reg = int(register)
        total = original + reg + self.Flags.c
        result = (total & 0xFF)

        # Set flags
        self.Flags.z = 1 if result == 0 else 0
        self.Flags.n = 0
        self.Flags.h = 1 if (original & 0x0F) + (register & 0x0F) + self.Flags.c > 0x0F else 0 # Carry from bit 3 to 4
        self.Flags.c = 1 if total > 0xFF else 0

        return Byte(result)
    
    def _adc_a_a(self,operandAddr):
        self.CoreReg.A = self._adc_a_r8(self.CoreReg.A)
        return None, None
    def _adc_a_b(self,operandAddr):
        self.CoreReg.A = self._adc_a_r8(self.CoreReg.B)
        return None, None
    def _adc_a_c(self,operandAddr):
        self.CoreReg.A = self._adc_a_r8(self.CoreReg.C)
        return None, None
    def _adc_a_d(self,operandAddr):
        self.CoreReg.A = self._adc_a_r8(self.CoreReg.D)
        return None, None
    def _adc_a_e(self,operandAddr):
        self.CoreReg.A = self._adc_a_r8(self.CoreReg.E)
        return None, None
    def _adc_a_h(self,operandAddr):
        self.CoreReg.A = self._adc_a_r8(self.CoreReg.H)
        return None, None
    def _adc_a_l(self,operandAddr):
        self.CoreReg.A = self._adc_a_r8(self.CoreReg.L)
        return None, None
    def _adc_a_mhl(self,operandAddr):
        self.CoreReg.A = self._adc_a_r8(self.Bus.readByte(self.CoreWords.HL))
        return None, None
    def _adc_a_d8(self,operandAddr):
        d8 = self.Bus.readByte(operandAddr)
        self.CoreReg.A = self._adc_a_r8(d8)
        return None, None


    def _sub_a_r8(self,register):
        # Subtract the value of the provided 8 bit register from the accumulator
        original = self.CoreReg.A
        result = (int(self.CoreReg.A) - int(register)) & 0xFF

        # Set flags
        self.Flags.z = 1 if result == 0 else 0
        self.Flags.n = 1
        self.Flags.h = 1 if (original & 0x0F) < (register & 0x0F) else 0
        self.Flags.c = 1 if original < register else 0
        return result
    
    def _sub_a_a(self,operandAddr):
        self.CoreReg.A = self._sub_a_r8(self.CoreReg.A)
        return None, None
    def _sub_a_b(self,operandAddr):
        self.CoreReg.A = self._sub_a_r8(self.CoreReg.B)
        return None, None
    def _sub_a_c(self,operandAddr):
        self.CoreReg.A = self._sub_a_r8(self.CoreReg.C)
        return None, None
    def _sub_a_d(self,operandAddr):
        self.CoreReg.A = self._sub_a_r8(self.CoreReg.D)
        return None, None
    def _sub_a_e(self,operandAddr):
        self.CoreReg.A = self._sub_a_r8(self.CoreReg.E)
        return None, None
    def _sub_a_h(self,operandAddr):
        self.CoreReg.A = self._sub_a_r8(self.CoreReg.H)
        return None, None
    def _sub_a_l(self,operandAddr):
        self.CoreReg.A = self._sub_a_r8(self.CoreReg.L)
        return None, None
    def _sub_a_mhl(self,operandAddr):
        self.CoreReg.A = self._sub_a_r8(self.Bus.readByte(self.CoreWords.HL))
        return None, None
    def _sub_a_d8(self,operandAddr):
        d8 = self.Bus.readByte(operandAddr)
        self.CoreReg.A = self._sub_a_r8(d8)
        return None, None
    
    def _sbc_a_r8(self,register):
        # Subtract the value of the provided 8 bit register from the accumulator with carry
        original = self.CoreReg.A
        result = (int(self.CoreReg.A) - int(register) - int(self.Flags.c)) & 0xFF

        # Set flags
        self.Flags.z = 1 if result == 0 else 0
        self.Flags.n = 1
        self.Flags.h = 1 if (int(original & 0x0F) - int(register & 0x0F) - int(self.Flags.c)) < 0 else 0
        self.Flags.c = 1 if (int(original) - int(register) - int(self.Flags.c)) < 0 else 0

        return result
    
    def _sbc_a_a(self,operandAddr):
        self.CoreReg.A = self._sbc_a_r8(self.CoreReg.A)
        return None, None
    def _sbc_a_b(self,operandAddr):
        self.CoreReg.A = self._sbc_a_r8(self.CoreReg.B)
        return None, None
    def _sbc_a_c(self,operandAddr):
        self.CoreReg.A = self._sbc_a_r8(self.CoreReg.C)
        return None, None
    def _sbc_a_d(self,operandAddr):
        self.CoreReg.A = self._sbc_a_r8(self.CoreReg.D)
        return None, None
    def _sbc_a_e(self,operandAddr):
        self.CoreReg.A = self._sbc_a_r8(self.CoreReg.E)
        return None, None
    def _sbc_a_h(self,operandAddr):
        self.CoreReg.A = self._sbc_a_r8(self.CoreReg.H)
        return None, None
    def _sbc_a_l(self,operandAddr):
        self.CoreReg.A = self._sbc_a_r8(self.CoreReg.L)
        return None, None
    def _sbc_a_mhl(self,operandAddr):
        self.CoreReg.A = self._sbc_a_r8(self.Bus.readByte(self.CoreWords.HL))
        return None, None
    def _sbc_a_d8(self,operandAddr):
        d8 = self.Bus.readByte(operandAddr)
        self.CoreReg.A = self._sbc_a_r8(d8)
        return None, None
    
    def _and_a_r8(self,register):
        # AND the value of the provided 8 bit register with the accumulator
        self.CoreReg.A &= register

        # Set flags
        self.Flags.z = 1 if self.CoreReg.A == 0 else 0
        self.Flags.n = 0
        self.Flags.h = 1
        self.Flags.c = 0

        return None, None
    
    def _and_a_a(self,operandAddr):
        self._and_a_r8(self.CoreReg.A)
        return None, None
    def _and_a_b(self,operandAddr):
        self._and_a_r8(self.CoreReg.B)
        return None, None
    def _and_a_c(self,operandAddr):
        self._and_a_r8(self.CoreReg.C)
        return None, None
    def _and_a_d(self,operandAddr):
        self._and_a_r8(self.CoreReg.D)
        return None, None
    def _and_a_e(self,operandAddr):
        self._and_a_r8(self.CoreReg.E)
        return None, None
    def _and_a_h(self,operandAddr):
        self._and_a_r8(self.CoreReg.H)
        return None, None
    def _and_a_l(self,operandAddr):
        self._and_a_r8(self.CoreReg.L)
        return None, None
    def _and_a_mhl(self,operandAddr):
        self._and_a_r8(self.Bus.readByte(self.CoreWords.HL))
        return None, None
    def _and_a_d8(self,operandAddr):
        d8 = self.Bus.readByte(operandAddr)
        self._and_a_r8(d8)
        return None, None

    def xor_a_r8(self,register):
        # XOR the value of the provided 8 bit register with the accumulator
        self.CoreReg.A ^= register

        # Set flags
        self.Flags.z = 1 if self.CoreReg.A == 0 else 0
        self.Flags.n = 0
        self.Flags.h = 0
        self.Flags.c = 0

        return None, None
    
    def _xor_a_a(self,operandAddr):
        self.xor_a_r8(self.CoreReg.A)
        return None, None
    def _xor_a_b(self,operandAddr):
        self.xor_a_r8(self.CoreReg.B)
        return None, None
    def _xor_a_c(self,operandAddr):
        self.xor_a_r8(self.CoreReg.C)
        return None, None
    def _xor_a_d(self,operandAddr):
        self.xor_a_r8(self.CoreReg.D)
        return None, None
    def _xor_a_e(self,operandAddr):
        self.xor_a_r8(self.CoreReg.E)
        return None, None
    def _xor_a_h(self,operandAddr):
        self.xor_a_r8(self.CoreReg.H)
        return None, None
    def _xor_a_l(self,operandAddr):
        self.xor_a_r8(self.CoreReg.L)
        return None, None
    def _xor_a_mhl(self,operandAddr):
        self.xor_a_r8(self.Bus.readByte(self.CoreWords.HL))
        return None, None
    def _xor_a_d8(self,operandAddr):
        d8 = self.Bus.readByte(operandAddr)
        self.xor_a_r8(d8)
        return None, None
    
    def _or_a_r8(self,register):
        # OR the value of the provided 8 bit register with the accumulator
        self.CoreReg.A |= register

        # Set flags
        self.Flags.z = 1 if self.CoreReg.A == 0 else 0
        self.Flags.n = 0
        self.Flags.h = 0
        self.Flags.c = 0

        return None, None
    def _or_a_a(self,operandAddr):
        self._or_a_r8(self.CoreReg.A)
        return None, None
    def _or_a_b(self,operandAddr):
        self._or_a_r8(self.CoreReg.B)
        return None, None
    def _or_a_c(self,operandAddr):
        self._or_a_r8(self.CoreReg.C)
        return None, None
    def _or_a_d(self,operandAddr):
        self._or_a_r8(self.CoreReg.D)
        return None, None
    def _or_a_e(self,operandAddr):
        self._or_a_r8(self.CoreReg.E)
        return None, None
    def _or_a_h(self,operandAddr):
        self._or_a_r8(self.CoreReg.H)
        return None, None
    def _or_a_l(self,operandAddr):
        self._or_a_r8(self.CoreReg.L)
        return None, None
    def _or_a_mhl(self,operandAddr):
        self._or_a_r8(self.Bus.readByte(self.CoreWords.HL))
        return None, None
    def _or_a_d8(self,operandAddr):
        d8 = self.Bus.readByte(operandAddr)
        self._or_a_r8(d8)
        return None, None
    
    def _cp_a_r8(self,register):
        # Compare the value of the provided 8 bit register with the accumulator
        original = self.CoreReg.A
        result = (int(self.CoreReg.A) - int(register)) & 0xFF

        # Set flags
        self.Flags.z = 1 if result == 0 else 0
        self.Flags.n = 1
        self.Flags.h = 1 if (original & 0x0F) < (register & 0x0F) else 0
        self.Flags.c = 1 if original < register else 0

        return None, None

    def _cp_a_a(self,operandAddr):
        self._cp_a_r8(self.CoreReg.A)
        return None, None
    def _cp_a_b(self,operandAddr):
        self._cp_a_r8(self.CoreReg.B)
        return None, None
    def _cp_a_c(self,operandAddr):
        self._cp_a_r8(self.CoreReg.C)
        return None, None
    def _cp_a_d(self,operandAddr):
        self._cp_a_r8(self.CoreReg.D)
        return None, None
    def _cp_a_e(self,operandAddr):
        self._cp_a_r8(self.CoreReg.E)
        return None, None
    def _cp_a_h(self,operandAddr):
        self._cp_a_r8(self.CoreReg.H)
        return None, None
    def _cp_a_l(self,operandAddr):
        self._cp_a_r8(self.CoreReg.L)
        return None, None
    def _cp_a_mhl(self,operandAddr):
        self._cp_a_r8(self.Bus.readByte(self.CoreWords.HL))
        return None, None
    def _cp_a_d8(self,operandAddr):
        d8 = self.Bus.readByte(operandAddr)
        self._cp_a_r8(d8)
        return None, None
    

    def _add_sp_r8(self,operandAddr):
        # Add the signed 8-bit value to the stack pointer (SP)
        signed_value = np.int8(operandAddr)
        self.CoreWords.SP = (self.CoreWords.SP + signed_value) & 0xFFFF

        # Set flags
        self.Flags.z = 0
        self.Flags.n = 0
        self.Flags.h = 1 if ((self.CoreWords.SP & 0x0F) + (signed_value & 0x0F)) > 0x0F else 0
        self.Flags.c = 1 if ((self.CoreWords.SP & 0xFF00) + (signed_value & 0xFF00)) > 0xFF else 0

    # STACK MANIPULATION INSTRUCTIONS

    # Push to stack memory, data from register pair
    def _perform_push(self, register_pair):
        msB = (register_pair >> 8) & 0xFF  # Most significant byte
        lsB = register_pair & 0xFF

        # TODO: Can I decrement SP by 2, and then write the full register pair word to SP?
        # Or do I need to decrement by 1, write the first byte, then decrement by 1 again and write the second byte?
        
        self.CoreWords.SP = (self.CoreWords.SP - 1) & 0xFFFF
        self.Bus.writeByte(self.CoreWords.SP, msB)
        self.CoreWords.SP = (self.CoreWords.SP - 1) & 0xFFFF
        self.Bus.writeByte(self.CoreWords.SP, lsB)

    def _push_af(self,operandAddr):
        # Push AF register pair onto stack
        self._perform_push(self.CoreWords.AF)
        return None, None

    def _push_bc(self,operandAddr):
        # Push BC register pair onto stack
        self._perform_push(self.CoreWords.BC)
        return None, None
    
    def _push_de(self,operandAddr):
        # Push DE register pair onto stack
        self._perform_push(self.CoreWords.DE)
        return None, None
    
    def _push_hl(self,operandAddr):
        # Push HL register pair onto stack
        self._perform_push(self.CoreWords.HL)
        return None, None
    
    def _perform_pop(self):
        # Pop two bytes from stack into register pair
        lsB = self.Bus.readByte(self.CoreWords.SP)
        self.CoreWords.SP = (self.CoreWords.SP + 1) & 0xFFFF
        msB = self.Bus.readByte(self.CoreWords.SP)
        self.CoreWords.SP = (self.CoreWords.SP + 1) & 0xFFFF

        # Combine the two bytes into a single word
        return (msB.astype(Word) << 8) | lsB
    
    def _pop_af(self,operandAddr):
        # Pop stack into AF register pair
        self.CoreWords.AF = self._perform_pop()

        return None, None
    
    def _pop_bc(self,operandAddr):
        # Pop stack into BC register pair
        self.CoreWords.BC = self._perform_pop()
        return None, None
    
    def _pop_de(self,operandAddr):
        # Pop stack into DE register pair
        self.CoreWords.DE = self._perform_pop()
        return None, None
    
    def _pop_hl(self,operandAddr):
        # Pop stack into HL register pair
        self.CoreWords.HL = self._perform_pop()
        return None, None
    

    # Helper for pushing return address and jumping
    def _perform_call(self, target_addr):
        # Calculate return address (instruction AFTER the 3-byte CALL)
        return_addr = (self.CoreWords.PC + 3) & 0xFFFF
        # Decrement SP by 2
        self.CoreWords.SP = (self.CoreWords.SP - 2) & 0xFFFF
        # Push return address onto stack (writeWord handles little-endian)
        self.Bus.writeWord(self.CoreWords.SP, return_addr)
        # Return the target address as the PC override and cycle count
        return target_addr, 24

    def _call_a16(self, operandAddr):
        # operandAddr is PC+1 here. Read the 16-bit target address from memory.
        target_addr = self.Bus.readWord(operandAddr)
        return self._perform_call(target_addr)

    def _call_nz_a16(self, operandAddr):
        if self.Flags.z == 0:
            target_addr = self.Bus.readWord(operandAddr)
            return self._perform_call(target_addr)
        else:
            # Call not taken, PC advances normally in step(), return cycle override
            return None, 12

    def _call_z_a16(self, operandAddr):
        if self.Flags.z == 1:
            target_addr = self.Bus.readWord(operandAddr)
            return self._perform_call(target_addr)
        else:
            return None, 12

    def _call_nc_a16(self, operandAddr):
        if self.Flags.c == 0:
            target_addr = self.Bus.readWord(operandAddr)
            return self._perform_call(target_addr)
        else:
            return None, 12

    def _call_c_a16(self, operandAddr):
        if self.Flags.c == 1:
            target_addr = self.Bus.readWord(operandAddr)
            return self._perform_call(target_addr)
        else:
            return None, 12


    def _perform_jump(self, target_addr):
        # Return the target address as the PC override and cycle count
        return target_addr, 16

    def _jp_a16(self, operandAddr):
        # Read the 16-bit target address from memory
        target_addr = self.Bus.readWord(operandAddr)
        return self._perform_jump(target_addr)
    
    def _jp_nz_a16(self, operandAddr):
        if self.Flags.z == 0:
            target_addr = self.Bus.readWord(operandAddr)
            return self._perform_jump(target_addr)
        else:
            return None, 12

    def _jp_z_a16(self, operandAddr):
        if self.Flags.z == 1:
            target_addr = self.Bus.readWord(operandAddr)
            return self._perform_jump(target_addr)
        else:
            return None, 12
        
    def _jp_nc_a16(self, operandAddr):
        if self.Flags.c == 0:
            target_addr = self.Bus.readWord(operandAddr)
            return self._perform_jump(target_addr)
        else:
            return None, 12
        
    def _jp_c_a16(self, operandAddr):
        if self.Flags.c == 1:
            target_addr = self.Bus.readWord(operandAddr)
            return self._perform_jump(target_addr)
        else:
            return None, 12
        
    def _jp_hl(self, operandAddr):
        # Return the address in HL as the PC override and cycle count
        target_addr = self.CoreWords.HL & 0xFFFF
        return target_addr, 4


    def _perform_ret(self):
        lsB = self.Bus.readByte(self.CoreWords.SP)
        self.CoreWords.SP = (self.CoreWords.SP + 1) & 0xFFFF
        msB = self.Bus.readByte(self.CoreWords.SP)
        self.CoreWords.SP = (self.CoreWords.SP + 1) & 0xFFFF

        target_addr = (msB.astype(Word) << 8) | lsB
        return target_addr
    
    def _ret(self, operandAddr):
        return self._perform_ret(), 16
    
    def _ret_nz(self, operandAddr):
        if self.Flags.z == 0:
            return self._perform_ret(), 20
        else:
            return None, 8
        
    def _ret_z(self, operandAddr):
        if self.Flags.z == 1:
            return self._perform_ret(), 20
        else:
            return None, 8
        
    def _ret_nc(self, operandAddr):
        if self.Flags.c == 0:
            return self._perform_ret(), 20
        else:
            return None, 8
        
    def _ret_c(self, operandAddr):
        if self.Flags.c == 1:
            return self._perform_ret(), 20
        else:
            return None, 8
        
    def _reti(self, operandAddr):
        return_addr = self._perform_ret()
        self.InterruptMask.IME = 1  # Re-enable interrupts
        return return_addr, 16


    # Helper specifically for RST instructions
    def _perform_rst(self, target_addr):
        # Calculate return address (instruction AFTER the 1-byte RST)
        return_addr = (self.CoreWords.PC + 1) & 0xFFFF
        # Decrement SP by 2
        # TODO - Verify SP can be decremented by 2, and then the word can be written to SP
        # Or do I need to decrement by 1, write the first byte, then decrement by 1 again and write the second byte?
        self.CoreWords.SP = (self.CoreWords.SP - 2) & 0xFFFF
        # Push return address onto stack
        self.Bus.writeWord(self.CoreWords.SP, return_addr)
        # Return the target address as the PC override and cycle count
        return target_addr, 16

    # Renamed methods for clarity (e.g., _rst_00h)
    def _rst_00h(self, operandAddr):
        return self._perform_rst(0x0000)

    def _rst_08h(self, operandAddr):
        return self._perform_rst(0x0008)

    def _rst_10h(self, operandAddr):
        return self._perform_rst(0x0010)

    def _rst_18h(self, operandAddr):
        return self._perform_rst(0x0018)

    def _rst_20h(self, operandAddr):
        return self._perform_rst(0x0020)

    def _rst_28h(self, operandAddr):
        return self._perform_rst(0x0028)

    def _rst_30h(self, operandAddr):
        return self._perform_rst(0x0030)

    def _rst_38h(self, operandAddr):
        return self._perform_rst(0x0038)


    def _ld_ma16_a(self, operandAddr):
        # Load the accumulator into the memory location pointed to by the 16-bit address in operandAddr
        self.Bus.writeByte(operandAddr, self.CoreReg.A)
        return None, None

    def _ld_a_ma16(self, operandAddr):
        # Load the value from the memory location pointed to by the 16-bit address in operandAddr into the accumulator
        self.CoreReg.A = self.Bus.readByte(operandAddr)
        return None, None
    

    #======================================================================
    # LDH: Load to/from 0xFF00 + n
    #======================================================================
    def _ldh_ma8_a(self, operandAddr):
        # LDH (a8), A - operandAddr is the immediate a8 value
        address = 0xFF00 + Word(operandAddr)
        self.Bus.writeByte(address, self.CoreReg.A)
        return None, None

    def _ldh_a_ma8(self, operandAddr):
        # LDH A, (a8) - operandAddr is the immediate a8 value
        address = 0xFF00 + Word(operandAddr)
        self.CoreReg.A = self.Bus.readByte(address)
        return None, None

    def _ldh_mc_a(self, operandAddr):
        # LDH (C), A - operandAddr is ignored
        address = 0xFF00 + self.CoreReg.C.astype(Word)
        self.Bus.writeByte(address, self.CoreReg.A)
        return None, None

    def _ldh_a_mc(self, operandAddr):
        # LDH A, (C) - operandAddr is ignored
        address = 0xFF00 + self.CoreReg.C.astype(Word)
        self.CoreReg.A = self.Bus.readByte(address)
        return None, None
    

    def _ld_sp_hl(self, operandAddr):
        # Load the value of the HL register pair into the stack pointer (SP)
        self.CoreWords.SP = self.CoreWords.HL
        return None, None

    def _ld_hl_sp_r8(self, operandAddr):
        # Load the value of the stack pointer (SP) plus a signed 8-bit value into the HL register pair
        signed_value = np.int8(operandAddr)
        self.CoreWords.HL = (self.CoreWords.SP + signed_value) & 0xFFFF

        # Set flags
        self.Flags.z = 0
        self.Flags.n = 0
        self.Flags.h = 1 if ((self.CoreWords.SP & 0x0F) + (signed_value & 0x0F)) > 0x0F else 0
        self.Flags.c = 1 if ((self.CoreWords.SP & 0xFF00) + (signed_value & 0xFF00)) > 0xFF else 0

        return None, None

            # 0x37: (self._scf,           1,[ 4],       "-001"),
            # 0x2F: (self._cpl,           1,[ 4],       "-11-"),
            # 0x3F: (self._ccf,           1,[ 4],       "-00C"),

    def _scf(self, operandAddr):
        # Set the carry flag (C) to 1 and clear the half-carry flag (H)
        self.Flags.c = 1
        self.Flags.h = 0
        self.Flags.n = 0
        return None, None
    
    def _ccf(self, operandAddr):
        # Complement the carry flag (C)
        self.Flags.c = 1 if self.Flags.c == 0 else 0
        self.Flags.h = 0
        self.Flags.n = 0
        return None, None
    
    def _cpl(self, operandAddr):
        # Complement the accumulator (A) and set the half-carry flag (H)
        self.CoreReg.A = ~self.CoreReg.A & 0xFF
        self.Flags.h = 1
        self.Flags.n = 1
        return None, None
    
    def _halt(self, operandAddr):
        # HALT the CPU until an interrupt occurs
        if self.InterruptMask.IME == 1:
            self.Halted = True
        else:
            # Check for HALT bug
            if (self.InterruptMask.IE & self.InterruptMask.IF) != 0:
                # HALT bug: PC fails to increment.
                # To emulate, we'll just execute the next instruction by not halting
                # and letting the PC increment normally in the step function.
                # The bug effectively makes HALT a NOP in this case.
                pass
            else:
                # IME is 0 and no pending interrupts, halt normally.
                self.Halted = True
        return None, None
    
    def _di(self, operandAddr):
        # Disable interrupts
        self.scheduleIMEEnabled = False
        self.InterruptMask.IME = 0
        return None, None
    
    def _ei(self, operandAddr):
        # Enable interrupts and schedule the IME flag to be set after this instruction
        # completes. 
        # This is to ensure that the EI instruction does not take effect until the next instruction.
        self.scheduleIMEEnabled = True
        return None, None
    

#======================================================================
# CB Prefix Instructions
#======================================================================
    
    def _rlc_r8(self, register):
        # Rotate the provided 8-bit register left. Bit 7 is copied to Carry and to bit 0.
        original = register
        register = ((original << 1) | (original >> 7)) & 0xFF

        # Set flags
        self.Flags.z = 1 if register == 0 else 0
        self.Flags.n = 0
        self.Flags.h = 0
        self.Flags.c = 1 if original & 0x80 else 0

        return register

    def _cb_rlc_b(self, operandAddr): self.CoreReg.B = self._rlc_r8(self.CoreReg.B); return None, None
    def _cb_rlc_c(self, operandAddr): self.CoreReg.C = self._rlc_r8(self.CoreReg.C); return None, None
    def _cb_rlc_d(self, operandAddr): self.CoreReg.D = self._rlc_r8(self.CoreReg.D); return None, None
    def _cb_rlc_e(self, operandAddr): self.CoreReg.E = self._rlc_r8(self.CoreReg.E); return None, None
    def _cb_rlc_h(self, operandAddr): self.CoreReg.H = self._rlc_r8(self.CoreReg.H); return None, None
    def _cb_rlc_l(self, operandAddr): self.CoreReg.L = self._rlc_r8(self.CoreReg.L); return None, None
    def _cb_rlc_mhl(self, operandAddr):
        original = self.Bus.readByte(self.CoreWords.HL)
        result = self._rlc_r8(original)
        self.Bus.writeByte(self.CoreWords.HL, result)

        return None, None
    def _cb_rlc_a(self, operandAddr): self.CoreReg.A = self._rlc_r8(self.CoreReg.A); return None, None
    
    def _rrc_r8(self, register):
        # Rotate the provided 8-bit register right. Bit 0 is copied to Carry and to bit 7.
        original = register
        register = ((original >> 1) | (original << 7)) & 0xFF

        # Set flags
        self.Flags.z = 1 if register == 0 else 0
        self.Flags.n = 0
        self.Flags.h = 0
        self.Flags.c = 1 if original & 0x01 else 0

        return register
    
    def _cb_rrc_b(self, operandAddr): self.CoreReg.B = self._rrc_r8(self.CoreReg.B); return None, None
    def _cb_rrc_c(self, operandAddr): self.CoreReg.C = self._rrc_r8(self.CoreReg.C); return None, None
    def _cb_rrc_d(self, operandAddr): self.CoreReg.D = self._rrc_r8(self.CoreReg.D); return None, None
    def _cb_rrc_e(self, operandAddr): self.CoreReg.E = self._rrc_r8(self.CoreReg.E); return None, None
    def _cb_rrc_h(self, operandAddr): self.CoreReg.H = self._rrc_r8(self.CoreReg.H); return None, None
    def _cb_rrc_l(self, operandAddr): self.CoreReg.L = self._rrc_r8(self.CoreReg.L); return None, None
    def _cb_rrc_mhl(self, operandAddr):
        original = self.Bus.readByte(self.CoreWords.HL)
        result = self._rrc_r8(original)
        self.Bus.writeByte(self.CoreWords.HL, result)
        return None, None
    def _cb_rrc_a(self, operandAddr): self.CoreReg.A = self._rrc_r8(self.CoreReg.A); return None, None
    
    def _cb_rl_r8(self, register):
        # Rotate the provided 8-bit register left through carry flag
        original = register
        carry_in = self.Flags.c
        
        # The new carry is the value of the original bit 7
        new_carry = 1 if (original & 0x80) else 0
        
        # Shift left and bring the old carry into bit 0
        register = ((original << 1) | carry_in) & 0xFF

        # Set flags
        self.Flags.z = 1 if register == 0 else 0
        self.Flags.n = 0
        self.Flags.h = 0
        self.Flags.c = new_carry

        return register
    
    def _cb_rl_b(self, operandAddr): self.CoreReg.B = self._cb_rl_r8(self.CoreReg.B); return None, None
    def _cb_rl_c(self, operandAddr): self.CoreReg.C = self._cb_rl_r8(self.CoreReg.C); return None, None
    def _cb_rl_d(self, operandAddr): self.CoreReg.D = self._cb_rl_r8(self.CoreReg.D); return None, None
    def _cb_rl_e(self, operandAddr): self.CoreReg.E = self._cb_rl_r8(self.CoreReg.E); return None, None
    def _cb_rl_h(self, operandAddr): self.CoreReg.H = self._cb_rl_r8(self.CoreReg.H); return None, None
    def _cb_rl_l(self, operandAddr): self.CoreReg.L = self._cb_rl_r8(self.CoreReg.L); return None, None
    def _cb_rl_mhl(self, operandAddr):
        original = self.Bus.readByte(self.CoreWords.HL)
        result = self._cb_rl_r8(original)
        self.Bus.writeByte(self.CoreWords.HL, result)
        return None, None
    def _cb_rl_a(self, operandAddr): self.CoreReg.A = self._cb_rl_r8(self.CoreReg.A); return None, None
    

    def _cb_rr_r8(self, register):
        # Rotate the provided 8-bit register right through carry flag
        original = register
        carry_in = self.Flags.c

        # The new carry is the value of the original bit 0
        new_carry = 1 if (original & 0x01) else 0

        # Shift right and bring the old carry into bit 7
        register = ((original >> 1) | (carry_in << 7)) & 0xFF

        # Set flags
        self.Flags.z = 1 if register == 0 else 0
        self.Flags.n = 0
        self.Flags.h = 0
        self.Flags.c = new_carry

        return register
    
    def _cb_rr_b(self, operandAddr): self.CoreReg.B = self._cb_rr_r8(self.CoreReg.B); return None, None
    def _cb_rr_c(self, operandAddr): self.CoreReg.C = self._cb_rr_r8(self.CoreReg.C); return None, None
    def _cb_rr_d(self, operandAddr): self.CoreReg.D = self._cb_rr_r8(self.CoreReg.D); return None, None
    def _cb_rr_e(self, operandAddr): self.CoreReg.E = self._cb_rr_r8(self.CoreReg.E); return None, None
    def _cb_rr_h(self, operandAddr): self.CoreReg.H = self._cb_rr_r8(self.CoreReg.H); return None, None
    def _cb_rr_l(self, operandAddr): self.CoreReg.L = self._cb_rr_r8(self.CoreReg.L); return None, None
    def _cb_rr_mhl(self, operandAddr):
        original = self.Bus.readByte(self.CoreWords.HL)
        result = self._cb_rr_r8(original)
        self.Bus.writeByte(self.CoreWords.HL, result)
        return None, None
    def _cb_rr_a(self, operandAddr): self.CoreReg.A = self._cb_rr_r8(self.CoreReg.A); return None, None
    
    #======================================================================
    # CB Prefix: SLA, SRA, SWAP, SRL
    #======================================================================

    def _cb_sla_r8(self, register):
        # Shift Left Arithmetic for an 8-bit register
        original = register
        result = (original << 1) & 0xFF

        # Set flags
        self.Flags.z = 1 if result == 0 else 0
        self.Flags.n = 0
        self.Flags.h = 0
        self.Flags.c = 1 if (original & 0x80) else 0 # Carry is old bit 7

        return result

    def _cb_sla_b(self, operandAddr): self.CoreReg.B = self._cb_sla_r8(self.CoreReg.B); return None, None
    def _cb_sla_c(self, operandAddr): self.CoreReg.C = self._cb_sla_r8(self.CoreReg.C); return None, None
    def _cb_sla_d(self, operandAddr): self.CoreReg.D = self._cb_sla_r8(self.CoreReg.D); return None, None
    def _cb_sla_e(self, operandAddr): self.CoreReg.E = self._cb_sla_r8(self.CoreReg.E); return None, None
    def _cb_sla_h(self, operandAddr): self.CoreReg.H = self._cb_sla_r8(self.CoreReg.H); return None, None
    def _cb_sla_l(self, operandAddr): self.CoreReg.L = self._cb_sla_r8(self.CoreReg.L); return None, None
    def _cb_sla_a(self, operandAddr): self.CoreReg.A = self._cb_sla_r8(self.CoreReg.A); return None, None
    def _cb_sla_mhl(self, operandAddr):
        val = self.Bus.readByte(self.CoreWords.HL)
        res = self._cb_sla_r8(val)
        self.Bus.writeByte(self.CoreWords.HL, res)
        return None, None

    def _cb_sra_r8(self, register):
        # Shift Right Arithmetic for an 8-bit register (MSB is preserved)
        original = register
        result = (original >> 1) | (original & 0x80) # Preserve bit 7

        # Set flags
        self.Flags.z = 1 if result == 0 else 0
        self.Flags.n = 0
        self.Flags.h = 0
        self.Flags.c = 1 if (original & 0x01) else 0 # Carry is old bit 0

        return result

    def _cb_sra_b(self, operandAddr): self.CoreReg.B = self._cb_sra_r8(self.CoreReg.B); return None, None
    def _cb_sra_c(self, operandAddr): self.CoreReg.C = self._cb_sra_r8(self.CoreReg.C); return None, None
    def _cb_sra_d(self, operandAddr): self.CoreReg.D = self._cb_sra_r8(self.CoreReg.D); return None, None
    def _cb_sra_e(self, operandAddr): self.CoreReg.E = self._cb_sra_r8(self.CoreReg.E); return None, None
    def _cb_sra_h(self, operandAddr): self.CoreReg.H = self._cb_sra_r8(self.CoreReg.H); return None, None
    def _cb_sra_l(self, operandAddr): self.CoreReg.L = self._cb_sra_r8(self.CoreReg.L); return None, None
    def _cb_sra_a(self, operandAddr): self.CoreReg.A = self._cb_sra_r8(self.CoreReg.A); return None, None
    def _cb_sra_mhl(self, operandAddr):
        val = self.Bus.readByte(self.CoreWords.HL)
        res = self._cb_sra_r8(val)
        self.Bus.writeByte(self.CoreWords.HL, res)
        return None, None

    def _cb_swap_r8(self, register):
        # Swap upper and lower nibbles of an 8-bit register
        result = ((register & 0x0F) << 4) | ((register & 0xF0) >> 4)

        # Set flags
        self.Flags.z = 1 if result == 0 else 0
        self.Flags.n = 0
        self.Flags.h = 0
        self.Flags.c = 0

        return result

    def _cb_swap_b(self, operandAddr): self.CoreReg.B = self._cb_swap_r8(self.CoreReg.B); return None, None
    def _cb_swap_c(self, operandAddr): self.CoreReg.C = self._cb_swap_r8(self.CoreReg.C); return None, None
    def _cb_swap_d(self, operandAddr): self.CoreReg.D = self._cb_swap_r8(self.CoreReg.D); return None, None
    def _cb_swap_e(self, operandAddr): self.CoreReg.E = self._cb_swap_r8(self.CoreReg.E); return None, None
    def _cb_swap_h(self, operandAddr): self.CoreReg.H = self._cb_swap_r8(self.CoreReg.H); return None, None
    def _cb_swap_l(self, operandAddr): self.CoreReg.L = self._cb_swap_r8(self.CoreReg.L); return None, None
    def _cb_swap_a(self, operandAddr): self.CoreReg.A = self._cb_swap_r8(self.CoreReg.A); return None, None
    def _cb_swap_mhl(self, operandAddr):
        val = self.Bus.readByte(self.CoreWords.HL)
        res = self._cb_swap_r8(val)
        self.Bus.writeByte(self.CoreWords.HL, res)
        return None, None

    def _cb_srl_r8(self, register):
        # Shift Right Logical for an 8-bit register (MSB becomes 0)
        original = register
        result = (original >> 1) & 0x7F # Ensure bit 7 is 0

        # Set flags
        self.Flags.z = 1 if result == 0 else 0
        self.Flags.n = 0
        self.Flags.h = 0
        self.Flags.c = 1 if (original & 0x01) else 0 # Carry is old bit 0

        return result

    def _cb_srl_b(self, operandAddr): self.CoreReg.B = self._cb_srl_r8(self.CoreReg.B); return None, None
    def _cb_srl_c(self, operandAddr): self.CoreReg.C = self._cb_srl_r8(self.CoreReg.C); return None, None
    def _cb_srl_d(self, operandAddr): self.CoreReg.D = self._cb_srl_r8(self.CoreReg.D); return None, None
    def _cb_srl_e(self, operandAddr): self.CoreReg.E = self._cb_srl_r8(self.CoreReg.E); return None, None
    def _cb_srl_h(self, operandAddr): self.CoreReg.H = self._cb_srl_r8(self.CoreReg.H); return None, None
    def _cb_srl_l(self, operandAddr): self.CoreReg.L = self._cb_srl_r8(self.CoreReg.L); return None, None
    def _cb_srl_a(self, operandAddr): self.CoreReg.A = self._cb_srl_r8(self.CoreReg.A); return None, None
    def _cb_srl_mhl(self, operandAddr):
        val = self.Bus.readByte(self.CoreWords.HL)
        res = self._cb_srl_r8(val)
        self.Bus.writeByte(self.CoreWords.HL, res)
        return None, None

    #======================================================================
    # CB Prefix: BIT b, r8
    #======================================================================

    def _cb_bit_b_r8(self, bit, register_value):
        # Test bit 'b' of an 8-bit register value
        # Flags: Z is set if bit is 0, N=0, H=1, C is not affected.
        mask = 1 << bit
        if (register_value & mask) == 0:
            self.Flags.z = 1
        else:
            self.Flags.z = 0
        
        self.Flags.n = 0
        self.Flags.h = 1
        # Carry flag is not affected by BIT instructions

    def _cb_res_b_r8(self, bit, register_value):
        # Reset (clear) bit 'b' of an 8-bit register value
        mask = 0xFF ^ (1 << bit) # Clear bit 'b' with 0xff xor'ed with shifted 1
        return register_value & mask

    def _cb_set_b_r8(self, bit, register_value):
        # Set bit 'b' of an 8-bit register value
        mask = 1 << bit
        return register_value | mask
