from SingletonBase import *

from Registers import RegByte
from Registers import RegWord
from Registers import Flag
import numpy as np


from Memory import Memory

class CPU(SingletonBase):

    _initialized = False # Flag to ensure __init__ runs only once

    def __init__(self):
        # Initialization Guard
        if hasattr(self, '_initialized') and self._initialized:
            print(f"... Skipping CPU __init__ due to existing initialization {id(self)}")
            return

        print(f"Iniitalizing CPU instance {id(self)}")

        self.Memory = Memory()
        self.CoreReg = RegByte()
        self.Flags = Flag()
        self.CoreWords = RegWord(self.CoreReg,self.Flags)
        self._initialized = True
        self.lr35902_opCodes = {}
        self.init_opCodes()

        self.cycles = 0

    def step(self):
        # Get Current OpCode from memory, via the program counter. 

        currentPC = self.CoreWords.PC

        opCode = self.Memory.readByte(currentPC)

        if opCode in self.lr35902_opCodes:
            opCodeFunc, length, cycles = self.lr35902_opCodes[opCode]

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
            0x10: (self._stop_0,        2,[ 4],       "----"),
            0x18: (self._jr_r8,         2,[12],       "----"),
            0x20: (self._jr_nz_r8,      2,[12,8],     "----"),
            0x30: (self._jr_nc_r8,      2,[12,8],     "----"),
            0x28: (self._jr_z_r8,       2,[12,8],     "----"),
            0x38: (self._jr_c_r8,       2,[12,8],     "----"),
            0x27: (self._daa,           1,[ 4],       "Z-0C"),
            # 0x37: (self._scf,           1,[ 4],       "-001"),
            # 0x2F: (self._cpl,           1,[ 4],       "-11-"),
            # 0x3F: (self._ccf,           1,[ 4],       "-00C"),
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
            # 0x76: (self._halt,          1,[ 4],       "----"),
            0x80: (self._add_a_b,       1,[ 4],       "Z0HC"),
            0x81: (self._add_a_c,       1,[ 4],       "Z0HC"),
            0x82: (self._add_a_d,       1,[ 4],       "Z0HC"),
            0x83: (self._add_a_e,       1,[ 4],       "Z0HC"),
            0x84: (self._add_a_h,       1,[ 4],       "Z0HC"),
            0x85: (self._add_a_l,       1,[ 4],       "Z0HC"),
            0x86: (self._add_a_mhl,     1,[ 8],       "Z0HC"),
            0x87: (self._add_a_a,       1,[ 4],       "Z0HC"),
            0xC6: (self._add_a_d8,      2,[ 8],       "Z0HC"),
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
            0x98: (self._sbc_a_b,       1,[ 4],       "Z1HC"),
            0x99: (self._sbc_a_c,       1,[ 4],       "Z1HC"),
            0x9A: (self._sbc_a_d,       1,[ 4],       "Z1HC"),
            0x9B: (self._sbc_a_e,       1,[ 4],       "Z1HC"),
            0x9C: (self._sbc_a_h,       1,[ 4],       "Z1HC"),
            0x9D: (self._sbc_a_l,       1,[ 4],       "Z1HC"),
            0x9E: (self._sbc_a_mhl,     1,[ 8],       "Z1HC"),
            0x9F: (self._sbc_a_a,       1,[ 4],       "Z1HC"),
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
            0xB0: (self._or_a_b,        1,[ 4],       "Z000"),
            0xB1: (self._or_a_c,        1,[ 4],       "Z000"),
            0xB2: (self._or_a_d,        1,[ 4],       "Z000"),
            0xB3: (self._or_a_e,        1,[ 4],       "Z000"),
            0xB4: (self._or_a_h,        1,[ 4],       "Z000"),
            0xB5: (self._or_a_l,        1,[ 4],       "Z000"),
            0xB6: (self._or_a_mhl,      1,[ 8],       "Z000"),
            0xB7: (self._or_a_a,        1,[ 4],       "Z000"),
            0xB8: (self._cp_a_b,        1,[ 4],       "Z1HC"),
            0xB9: (self._cp_a_c,        1,[ 4],       "Z1HC"),
            0xBA: (self._cp_a_d,        1,[ 4],       "Z1HC"),
            0xBB: (self._cp_a_e,        1,[ 4],       "Z1HC"),
            0xBC: (self._cp_a_h,        1,[ 4],       "Z1HC"),
            0xBD: (self._cp_a_l,        1,[ 4],       "Z1HC"),
            0xBE: (self._cp_a_mhl,      1,[ 8],       "Z1HC"),
            0xBF: (self._cp_a_a,        1,[ 4],       "Z1HC"),
            # 0xC0: (self._ret_nz,        1,[20,8],     "----"),
            # 0xC8: (self._ret_z,         1,[20,8],     "----"),
            # 0xC9: (self._ret,           1,[16],       "----"),
            # 0xC1: (self._pop_bc,        1,[12],       "----"),
            # 0xC2: (self._jp_nz_a16,     3,[16,12],    "----"),
            # 0xC3: (self._jp_a16,        3,[16],       "----"),
            # 0xC4: (self._call_nz_a16,   3,[24,12],    "----"),
            # 0xC5: (self._push_bc,       1,[16],       "----"),
            # 0xC7: (self._rst_00h,       1,[16],       "----"),
            # 0xCA: (self._jp_z_a16,      3,[16,12],    "----"),
            # 0xCB: (self.cb_prefix_table),
            # 0xCC: (self._call_z_a16,    3,[24,12],    "----"),
            # 0xCD: (self._call_a16,      3,[24],       "----"),
            # 0xCF: (self._rst_08h,       1,[16],       "----"),
            # 0xD0: (self._ret_nc,        1,[20/8],     "----"),
            # 0xD1: (self._pop_de,        1,[12],       "----"),
            # 0xD2: (self._jp_nc_a16,     3,[16,12],    "----"),
            # 0xD3: ("N/A"),
            # 0xD4: (self._call_nc_a16,   3,[24,12],    "----"),
            # 0xD5: (self._push_de,       1,[16],       "----"),
            # 0xD6: (self._sub_d8,        2,[8],        "Z1HC"),
            # 0xD7: (self._rst_10h,       1,[16],       "----"),
            # 0xD8: (self._ret_c,         1,[20,8],     "----"),
            # 0xD9: (self._reti,          1,[16],       "----"),
            # 0xDA: (self._jp_c_a16,      3,[16,12],    "----"),
            # 0xDB: ("N/A"),
            # 0xDC: (self._call_c_a16,    3,[24,12],    "----"),
            # 0xDD: ("N/A"),
            # 0xDE: (self._sbc_a_d8,      2,[8],        "Z1HC"),
            # 0xDF: (self._rst_18h,       1,[16],       "----"),
            # 0xE0: (self._ldh_a8_a,      2,[12],       "----"),
            # 0xE1: (self._pop_hl,        1,[12],       "----"),
            # 0xE2: (self._ld_c_a,        2,[8],        "----"),
            # 0xE3: ("N/A"),
            # 0xE4: ("N/A"),
            # 0xE5: (self._push_hl,       1,[16],       "----"),
            # 0xE7: (self._rst_20h,       1,[16],       "----"),
            # 0xE8: (self._add_sp_r8,     2,[16],       "00HC"),
            # 0xE9: (self._jp_hl,         1,[4],        "----"),
            # 0xEA: (self._ld_a16_a,      3,[16],       "----"),
            # 0xEB: ("N/A"),
            # 0xEC: ("N/A"),
            # 0xED: ("N/A"),
            # 0xEE: (self._xor_d8,        2,[8],        "ZOOO"),
            # 0xEF: (self._rst_28h,       1,[16],       "----"),
            # 0xF0: (self._ldh_a_a8,      2,[12],       "----"),
            # 0xF1: (self._pop_af,        1,[12],       "ZNHC"),
            # 0xF2: (self._ld_a_c,        2,[8],        "----"),
            # 0xF3: (self._di,            1,[4],        "----"),
            # 0xF4: ("N/A"),
            # 0xF5: (self._push_af,       1,[16],       "----"),
            # 0xF6: (self._or_d8,         2,[8],        "Z000"),
            # 0xF7: (self._rst_30h,       1,[16],       "----"),
            # 0xF8: (self._ld_hl_spp_r8,  2,[12],       "00HC"),
            # 0xF9: (self._ld_sp_hl,      1,[8],        "----"),
            # 0xFA: (self._ld_a_a16,      3,[16],       "----"),
            # 0xFB: (self._ei,            1,[4],        "----"),
            # 0xFC: ("N/A"),
            # 0xFD: ("N/A"),
            # 0xFE: (self._cp_d8,         2,[8],        "Z1HC"),
            # 0xFF: (self._rst_38h,       1,[16],       "----"),
        }

        # ---  opCode Implementations --- #
        # TODO: Determine overall template for instruction set implementation

    def _nop(self):
        # Program Counters won't do anything. Step Function will increment the cycles correctly
        return None, None

    def _ld_r16_d16(self, operandAddr):
        lsB = self.Memory.readByte(operandAddr)
        msB = self.Memory.readByte(operandAddr+1)
        return (msB << 8) | lsB

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
        return (register + 1) & 0xFFFF

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
        register = (register + 1) & 0xFF

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
        result = (value - 1) & 0xFF # Calculate result with wrap-around

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
        return (register - 1) & 0xFFFF

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
        d8 = self.Memory.readByte(operandAddr)
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
        original = self.Memory.readByte(self.CoreWords.HL)
        result = (original + 1) & 0xFF

        self.Memory.writeByte(result,self.CoreWords.HL)

        self.Flags.z = 1 if (result == 0x00) else 0
        self.Flags.n = 0
        self.Flags.h = 1 if (original & 0xF) == 0xF else 0 # lower nibble of 0 requires a borrow from upper nibble
        return None, None

    def _dec_mhl(self,operandAddr):
        # Decrement Value stored in HL Location
        original = self.Memory.readByte(self.CoreWords.HL)
        result = (original - 1) & 0xFF

        self.Memory.writeByte(result,self.CoreWords.HL)

        self.Flags.z = 1 if result == 0x00 else 0
        self.Flags.n = 1
        self.Flags.h = 1 if (original & 0xF) == 0x0 else 0
        return None, None

    # Adds r16 register to the value stored in hl
    def _add_hl_r16(self, register):
        original = self.CoreWords.HL
        self.CoreWords.HL = (original + register) & 0xFFFF

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
        d8 = self.Memory.readByte(operandAddr)
        self.Memory.writeByte(d8, self.CoreWords.HL)

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
        self.Memory.writeByte(self.CoreReg.A, register)
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
        self.Memory.writeWord(self.CoreWords.SP, operandAddr)
        return None, None

    def _ld_a_mr16(self,register):
        byteValue = self.Memory.readByte(register)
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
        # TODO: Implement this
        pass

    # jump related to provided 8 bit signed value
    #   PC <-- PC + signed 8-bit value
    def _jr_r8(self,operandAddr):
        operandAddr = np.int8(operandAddr)
        self.CoreWords.PC += operandAddr
        return None, 12

    # Jump relative to procided 8 bit signed value if the Zero Flag is not set
    #   PC <-- PC + signed 8-bit value

    def _jr_nz_r8(self,operandAddr):
        operandAddr = np.int8(operandAddr)
        
        if self.Flags.z == 0:
            self.CoreWords.PC += operandAddr
        else:
            return None,8 # Cycle Override
        return None, 12

    # Jump relative to provided 8 bit signed value if the Carry Flag is not set
    def _jr_nc_r8(self,operandAddr):

        operandAddr = np.int8(operandAddr)

        if self.Flags.c == 0:
            self.CoreWords.PC += operandAddr
        else: 
            return None,8
        return None, 12

    # Jump relative to provided 8 bit signed value if the Zero Flag is set
    def _jr_z_r8(self,operandAddr):
        operandAddr = np.int8(operandAddr)

        if self.Flags.z == 1:
            self.CoreWords.PC += operandAddr
        else:
            return None,8
        return None, 12

    # Jump relative to provided 8 bit signed value if the Carry Flag is set
    def _jr_c_r8(self,operandAddr):
        operandAddr = np.int8(operandAddr)

        if self.Flags.c == 1:
            self.CoreWords.PC += operandAddr
        else:
            return None,8
        return None, 12


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
    

    def ld_r8_mhl(self,operandAddr):
        # Load the value stored in the HL register into the provided 8 bit register
        byteValue = self.Memory.readByte(self.CoreWords.HL)
        return byteValue
    
    def _ld_b_mhl(self,operandAddr):
        self.CoreReg.B = self.ld_r8_mhl(operandAddr)
        return None, None
    def _ld_c_mhl(self,operandAddr):
        self.CoreReg.C = self.ld_r8_mhl(operandAddr)
        return None, None
    def _ld_d_mhl(self,operandAddr):
        self.CoreReg.D = self.ld_r8_mhl(operandAddr)
        return None, None
    def _ld_e_mhl(self,operandAddr):
        self.CoreReg.E = self.ld_r8_mhl(operandAddr)
        return None, None
    def _ld_h_mhl(self,operandAddr):
        self.CoreReg.H = self.ld_r8_mhl(operandAddr)
        return None, None
    def _ld_l_mhl(self,operandAddr):
        self.CoreReg.L = self.ld_r8_mhl(operandAddr)
        return None, None
    
    def _ld_mhl_r8(self,register):
        # Load the value of the provided 8 bit register into the location pointed to by HL
        self.Memory.writeByte(register, self.CoreWords.HL)
        return None, None
    
    def _ld_mhl_b(self,operandAddr):
        self._ld_mhl_r8(self.CoreReg.B)
        return None, None
    def _ld_mhl_c(self,operandAddr):
        self._ld_mhl_r8(self.CoreReg.C)
        return None, None
    def _ld_mhl_d(self,operandAddr):
        self._ld_mhl_r8(self.CoreReg.D)
        return None, None
    def _ld_mhl_e(self,operandAddr):
        self._ld_mhl_r8(self.CoreReg.E)
        return None, None
    def _ld_mhl_h(self,operandAddr):
        self._ld_mhl_r8(self.CoreReg.H)
        return None, None
    def _ld_mhl_l(self,operandAddr):
        self._ld_mhl_r8(self.CoreReg.L)
        return None, None
    

    def _add_a_r8(self,register):
        # Add the value of the provided 8 bit register to the accumulator
        original = self.CoreReg.A
        result = (self.CoreReg.A + register) & 0xFF

        # Set flags
        self.Flags.z = 1 if result == 0 else 0
        self.Flags.n = 0
        self.Flags.h = 1 if (original & 0x0F) + (register & 0x0F) > 0x0F else 0 # Carry from bit 3 to 4
        self.Flags.c = 1 if (original + register) > 0xFF else 0


        return result
    
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
        self.CoreReg.A = self._add_a_r8(self.Memory.readByte(self.CoreWords.HL))
        return None, None
    def _add_a_d8(self,operandAddr):
        d8 = self.Memory.readByte(operandAddr)
        self.CoreReg.A = self._add_a_r8(d8)
        return None, None

    def _adc_a_r8(self,register):
        # Add the value of the provided 8 bit register to the accumulator with carry
        original = self.CoreReg.A
        result = (self.CoreReg.A + register + self.Flags.c) & 0xFF

        # Set flags
        self.Flags.z = 1 if result == 0 else 0
        self.Flags.n = 0
        self.Flags.h = 1 if (original & 0x0F) + (register & 0x0F) + self.Flags.c > 0x0F else 0 # Carry from bit 3 to 4
        self.Flags.c = 1 if (original + register + self.Flags.c) > 0xFF else 0

        return result
    
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
        self.CoreReg.A = self._adc_a_r8(self.Memory.readByte(self.CoreWords.HL))
        return None, None
    def _adc_a_d8(self,operandAddr):
        d8 = self.Memory.readByte(operandAddr)
        self.CoreReg.A = self._adc_a_r8(d8)
        return None, None
    

    def _sub_a_r8(self,register):
        # Subtract the value of the provided 8 bit register from the accumulator
        original = self.CoreReg.A
        result = (self.CoreReg.A - register) & 0xFF

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
        self.CoreReg.A = self._sub_a_r8(self.Memory.readByte(self.CoreWords.HL))
        return None, None
    def _sub_a_d8(self,operandAddr):
        d8 = self.Memory.readByte(operandAddr)
        self.CoreReg.A = self._sub_a_r8(d8)
        return None, None
    
    def _sbc_a_r8(self,register):
        # Subtract the value of the provided 8 bit register from the accumulator with carry
        original = self.CoreReg.A
        result = (self.CoreReg.A - register - self.Flags.c) & 0xFF

        # Set flags
        self.Flags.z = 1 if result == 0 else 0
        self.Flags.n = 1
        self.Flags.h = 1 if (original & 0x0F) < (register & 0x0F) else 0
        self.Flags.c = 1 if original < register else 0

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
        self.CoreReg.A = self._sbc_a_r8(self.Memory.readByte(self.CoreWords.HL))
        return None, None
    def _sbc_a_d8(self,operandAddr):
        d8 = self.Memory.readByte(operandAddr)
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
        self._and_a_r8(self.Memory.readByte(self.CoreWords.HL))
        return None, None
    def _and_a_d8(self,operandAddr):
        d8 = self.Memory.readByte(operandAddr)
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
        self.xor_a_r8(self.Memory.readByte(self.CoreWords.HL))
        return None, None
    def _xor_a_d8(self,operandAddr):
        d8 = self.Memory.readByte(operandAddr)
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
        self._or_a_r8(self.Memory.readByte(self.CoreWords.HL))
        return None, None
    def _or_a_d8(self,operandAddr):
        d8 = self.Memory.readByte(operandAddr)
        self._or_a_r8(d8)
        return None, None
    
    def _cp_a_r8(self,register):
        # Compare the value of the provided 8 bit register with the accumulator
        original = self.CoreReg.A
        result = (self.CoreReg.A - register) & 0xFF

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
        self._cp_a_r8(self.Memory.readByte(self.CoreWords.HL))
        return None, None
    def _cp_a_d8(self,operandAddr):
        d8 = self.Memory.readByte(operandAddr)
        self._cp_a_r8(d8)
        return None, None
    

























