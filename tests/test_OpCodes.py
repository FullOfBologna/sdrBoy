import pytest

from CPU import CPU
from Memory import Memory
import numpy as np

#==========================================
#           PYTEST FIXTURES             
#==========================================

@pytest.fixture(scope="function")
def cpu():
    cpu = CPU()
    cpu.Flags.flagReset()

    yield cpu 

    cpu.reset() # Reset Singleton state for next test

@pytest.fixture(scope="function")
def mem():
    mem = Memory()

    yield mem

    mem.reset()

#==========================================
#           OP CODE TEST CASES            
#==========================================

class TestOpCodes:

    #==========================================
    #           TEST CASE DEFINITIONS        
    #==========================================

    # 16-bit register increment test cases
    inc_r16_test_cases = [
        # reg_name, initial_value, expected_value, id
        pytest.param("BC", 0x2000, 0x2001, id="Basic INC: BC"),
        pytest.param("DE", 0x2000, 0x2001, id="Basic INC: DE"),
        pytest.param("HL", 0x2000, 0x2001, id="Basic INC: HL"),
        pytest.param("SP", 0x2000, 0x2001, id="Basic INC: SP"),
        pytest.param("BC", 0xFFFF, 0x0000, id="Wrap Around INC: BC"),
        pytest.param("DE", 0xFFFF, 0x0000, id="Wrap Around INC: DE"),
        pytest.param("HL", 0xFFFF, 0x0000, id="Wrap Around INC: HL"),
        pytest.param("SP", 0xFFFF, 0x0000, id="Wrap Around INC: SP"),
    ]

    # 16-bit register decrement test cases
    dec_r16_test_cases = [
        # reg_name, initial_value, expected_value, id
        pytest.param("BC", 0x2001, 0x2000, id="Basic DEC: BC"),
        pytest.param("DE", 0x2001, 0x2000, id="Basic DEC: DE"),
        pytest.param("HL", 0x2001, 0x2000, id="Basic DEC: HL"),
        pytest.param("SP", 0x2001, 0x2000, id="Basic DEC: SP"),
        pytest.param("BC", 0x0000, 0xFFFF, id="Wrap Around DEC: BC"),
        pytest.param("DE", 0x0000, 0xFFFF, id="Wrap Around DEC: DE"),
        pytest.param("HL", 0x0000, 0xFFFF, id="Wrap Around DEC: HL"),
        pytest.param("SP", 0x0000, 0xFFFF, id="Wrap Around DEC: SP"),
    ]

    # 8-bit register increment test cases
    inc_r8_test_cases = [
        # reg_name, initial_value, expected_value, expected_flags(Z,N,H), id
        pytest.param("A", 0x33, 0x34, (0, 0, 0), id="INC A: Basic"),
        pytest.param("B", 0x00, 0x01, (0, 0, 0), id="INC B: Zero -> One"),
        pytest.param("C", 0xFE, 0xFF, (0, 0, 0), id="INC C: -> Max"),
        pytest.param("D", 0xFF, 0x00, (1, 0, 1), id="INC D: Wrap Around (causes Z, H)"), # FF+1=00, H set
        pytest.param("E", 0x4F, 0x50, (0, 0, 1), id="INC E: Half Carry Set"), # 0F+1=10
        pytest.param("H", 0x5A, 0x5B, (0, 0, 0), id="INC H: No Half Carry"),
        pytest.param("L", 0xAF, 0xB0, (0, 0, 1), id="INC L: Half Carry Set High Nibble"), # 0F+1=10
    ]

    # 8-bit register decrement test cases
    dec_r8_test_cases = [
        # reg_name, initial_value, expected_value, expected_flags(Z,N,H), id
        pytest.param("A", 0x34, 0x33, (0, 1, 0), id="DEC A: Basic"),
        pytest.param("B", 0x01, 0x00, (1, 1, 0), id="DEC B: One -> Zero (causes Z)"),
        pytest.param("C", 0x00, 0xFF, (0, 1, 1), id="DEC C: Wrap Around (causes H)"), # 00-1=FF, H set (borrow)
        pytest.param("D", 0xFF, 0xFE, (0, 1, 0), id="DEC D: Max -> Max-1"),
        pytest.param("E", 0x50, 0x4F, (0, 1, 1), id="DEC E: Half Carry Set (Borrow)"), # 10-1=0F
        pytest.param("H", 0x5B, 0x5A, (0, 1, 0), id="DEC H: No Half Carry"),
        pytest.param("L", 0xB0, 0xAF, (0, 1, 1), id="DEC L: Half Carry Set High Nibble (Borrow)"), # 10-1=0F
    ]

    # Load 8-bit immediate value into register test cases
    ld_r8_d8_test_cases = [
        # reg_name, d8_value, method_name, id
        pytest.param("A", 0x7F, "_ld_a_d8", id="LD A, 0x7F"),
        pytest.param("A", 0x00, "_ld_a_d8", id="LD A, 0x00"),
        pytest.param("B", 0x5A, "_ld_b_d8", id="LD B, 0x5A"),
        pytest.param("B", 0xFF, "_ld_b_d8", id="LD B, 0xFF"),
        pytest.param("C", 0x12, "_ld_c_d8", id="LD C, 0x12"),
        pytest.param("C", 0x00, "_ld_c_d8", id="LD C, 0x00"),
        pytest.param("D", 0xAB, "_ld_d_d8", id="LD D, 0xAB"),
        pytest.param("E", 0xCD, "_ld_e_d8", id="LD E, 0xCD"),
        pytest.param("H", 0x42, "_ld_h_d8", id="LD H, 0x42"),
        pytest.param("L", 0x99, "_ld_l_d8", id="LD L, 0x99"),
        pytest.param("L", 0x00, "_ld_l_d8", id="LD L, 0x00"),
    ]

    # Load 16-bit immediate value into register pair test cases
    ld_r16_d16_test_cases = [
        # reg_name, d16_value, method_name, id
        pytest.param("BC", 0x1234, "_ld_bc_d16", id="LD BC, 0x1234"),
        pytest.param("BC", 0x0000, "_ld_bc_d16", id="LD BC, 0x0000"),
        pytest.param("BC", 0xFFFF, "_ld_bc_d16", id="LD BC, 0xFFFF"),
        pytest.param("DE", 0xABCD, "_ld_de_d16", id="LD DE, 0xABCD"),
        pytest.param("DE", 0xFF00, "_ld_de_d16", id="LD DE, 0xFF00"),
        pytest.param("HL", 0x8001, "_ld_hl_d16", id="LD HL, 0x8001"),
        pytest.param("HL", 0x00FF, "_ld_hl_d16", id="LD HL, 0x00FF"),
        pytest.param("SP", 0xFFFE, "_ld_sp_d16", id="LD SP, 0xFFFE"),
        pytest.param("SP", 0xC000, "_ld_sp_d16", id="LD SP, 0xC000"),
    ]

    # Rotate left carry accumulator test cases
    rlca_test_cases = [
        # initial_a, initial_c, expected_a, expected_flags(Z,N,H,C), id
        pytest.param(0x55, 1, 0xAA, (0, 0, 0, 0), id="RLCA: Basic, Bit7=0, InitC=1"),
        pytest.param(0xAA, 0, 0x55, (0, 0, 0, 1), id="RLCA: Basic, Bit7=1, InitC=0"),
        pytest.param(0x00, 1, 0x00, (0, 0, 0, 0), id="RLCA: Zero A, Bit7=0, InitC=1"),
        pytest.param(0x80, 0, 0x01, (0, 0, 0, 1), id="RLCA: Only Bit7 set, InitC=0"),
        pytest.param(0xFF, 0, 0xFF, (0, 0, 0, 1), id="RLCA: All bits set, InitC=0"),
        pytest.param(0x01, 1, 0x02, (0, 0, 0, 0), id="RLCA: Bit0 set, Bit7=0, InitC=1"),
        pytest.param(0x40, 1, 0x80, (0, 0, 0, 0), id="RLCA: Bit6 set, Bit7=0, InitC=1"),
        pytest.param(0x85, 0, 0x0B, (0, 0, 0, 1), id="RLCA: Example 1 (Bit7=1), InitC=0"), # 1000 0101 -> 0000 1011, C=1
        pytest.param(0x7F, 1, 0xFE, (0, 0, 0, 0), id="RLCA: Example 2 (Bit7=0), InitC=1"), # 0111 1111 -> 1111 1110, C=0
    ]

    # Memory operations test cases (inc/dec at HL address)
    memory_operation_test_cases = [
        # method_name, initial_value, expected_value, expected_flags, id
        pytest.param("_inc_mhl", 0x0F, 0x10, "0010", id="INC (HL): Half-carry boundary"),
        pytest.param("_inc_mhl", 0xFF, 0x00, "1010", id="INC (HL): Wrap to zero"),
        pytest.param("_inc_mhl", 0x34, 0x35, "0000", id="INC (HL): Regular increment"),
        pytest.param("_dec_mhl", 0x10, 0x0F, "0110", id="DEC (HL): Half-carry boundary"),
        pytest.param("_dec_mhl", 0x01, 0x00, "1100", id="DEC (HL): Decrement to zero"),
        pytest.param("_dec_mhl", 0x35, 0x34, "0100", id="DEC (HL): Regular decrement"),
    ]

    # Register rotation test cases
    rotation_test_cases = [
        # method_name, initial_a, initial_flags, expected_a, expected_flags, id
        pytest.param("_rlca", 0x80, "0000", 0x01, "0001", id="RLCA: Rotate left with bit 7 set"),
        pytest.param("_rlca", 0x01, "0000", 0x02, "0000", id="RLCA: Rotate left without carry"),
        pytest.param("_rrca", 0x01, "0000", 0x80, "0001", id="RRCA: Rotate right with bit 0 set"),
        pytest.param("_rrca", 0x02, "0000", 0x01, "0000", id="RRCA: Rotate right without carry"),
        pytest.param("_rla",  0x80, "0000", 0x00, "0001", id="RLA: Rotate left through carry, initial carry 0"),
        pytest.param("_rla",  0x80, "0001", 0x01, "0001", id="RLA: Rotate left through carry, initial carry 1"),
        pytest.param("_rra",  0x01, "0000", 0x00, "0001", id="RRA: Rotate right through carry, initial carry 0"),
        pytest.param("_rra",  0x01, "0001", 0x80, "0001", id="RRA: Rotate right through carry, initial carry 1"),
    ]

    # Add HL, r16 test cases
    add_hl_test_cases = [
        # method_name, register_value, initial_hl, expected_hl, expected_flags, id
        pytest.param("_add_hl_bc", 0x0234, 0x0100, 0x0334, "0000", id="ADD HL, BC: Simple addition"),
        pytest.param("_add_hl_bc", 0x0FFF, 0x0001, 0x1000, "0010", id="ADD HL, BC: Half-carry case"),
        pytest.param("_add_hl_bc", 0xFFFF, 0x0001, 0x0000, "0011", id="ADD HL, BC: Full carry case"),
        pytest.param("_add_hl_de", 0x0234, 0x0100, 0x0334, "0000", id="ADD HL, DE: Simple addition"),
        pytest.param("_add_hl_hl", 0x0800, 0x0800, 0x1000, "0010", id="ADD HL, HL: Half-carry"),
        pytest.param("_add_hl_sp", 0x1000, 0xF000, 0x0000, "0001", id="ADD HL, SP: Full carry"),
    ]

    # Load (BC), A / Load (DE), A / Load (HL), A test cases
    ld_mr16_a_test_cases = [
        # reg_name, mem_addr, initial_a, expected_mem_value, id
        pytest.param("BC", 0xC000, 0x55, 0x55, id="LD (BC), A: Basic"),
        pytest.param("DE", 0xC001, 0x00, 0x00, id="LD (DE), A: Zero"),
        pytest.param("HL", 0xC002, 0xFF, 0xFF, id="LD (HL), A: Max"),
        pytest.param("BC", 0xD000, 0x12, 0x12, id="LD (BC), A: Different address"),
        pytest.param("DE", 0xD001, 0x34, 0x34, id="LD (DE), A: Different address"),
        pytest.param("HL", 0xD002, 0x78, 0x78, id="LD (HL), A: Different address"),
        pytest.param("HL+", 0xC003, 0xAA, 0xAA, id="LD (HL+), A: Basic"),
        pytest.param("HL-", 0xC004, 0xBB, 0xBB, id="LD (HL-), A: Basic"),
    ]

    ld_m16_sp_test_cases = [
        # mem_addr, initial_sp, expected_lsb, expected_msb, id
        pytest.param(0xC000, 0x1234, 0x34, 0x12, id="LD (a16), SP: Basic"),
        pytest.param(0xD000, 0x0000, 0x00, 0x00, id="LD (a16), SP: Zero"),
        pytest.param(0xE000, 0xFFFF, 0xFF, 0xFF, id="LD (a16), SP: Max"),
        pytest.param(0xC050, 0xABCD, 0xCD, 0xAB, id="LD (a16), SP: Different address"),
    ]
#
    ld_a_mr16_test_cases = [
        # reg_name, mem_addr, initial_mem_value, expected_a, id
        pytest.param("BC", 0xC000, 0x55, 0x55, id="LD A, (BC): Basic"),
        pytest.param("DE", 0xC001, 0x00, 0x00, id="LD A, (DE): Zero"),
        pytest.param("HL", 0xC002, 0xFF, 0xFF, id="LD A, (HL): Max"),
        pytest.param("BC", 0xD000, 0x12, 0x12, id="LD A, (BC): Different address"),
        pytest.param("DE", 0xD001, 0x34, 0x34, id="LD A, (DE): Different address"),
        pytest.param("HL", 0xD002, 0x78, 0x78, id="LD A, (HL): Different address"),
        pytest.param("HL+", 0xC003, 0xAA, 0xAA, id="LD A, (HL+): Basic"),
        pytest.param("HL-", 0xC004, 0xBB, 0xBB, id="LD A, (HL-): Basic"),
    ]

    jump_test_cases = [
        # mnemonic, initial_flags, offset, expected_pc, cycles, id
        pytest.param("_jr_r8", "----", 5, 0x0105, 12, id="JR +5"),
        pytest.param("_jr_r8", "----", -5, 0x00FB, 12, id="JR -5"),
        pytest.param("_jr_nz_r8", "0---", 5, 0x0105, 12, id="JR NZ, Z=0, +5"),
        pytest.param("_jr_nz_r8", "1---", 5, 0x0100, 8, id="JR NZ, Z=1, +5"),
        pytest.param("_jr_z_r8", "1---", 5, 0x0105, 12, id="JR Z, Z=1, +5"),
        pytest.param("_jr_z_r8", "0---", 5, 0x0100, 8, id="JR Z, Z=0, +5"),
        pytest.param("_jr_nc_r8", "---0", 5, 0x0105, 12, id="JR NC, C=0, +5"),
        pytest.param("_jr_nc_r8", "---1", 5, 0x0100, 8, id="JR NC, C=1, +5"),
        pytest.param("_jr_c_r8", "---1", 5, 0x0105, 12, id="JR C, C=1, +5"),
        pytest.param("_jr_c_r8", "---0", 5, 0x0100, 8, id="JR C, C=0, +5"),
    ]

    ld_r8_r8_test_cases = [
        # dest_reg, src_reg, initial_src_value, expected_dest_value, id
        pytest.param("A", "B", 0x12, 0x12, id="LD A, B"),
        pytest.param("A", "C", 0x34, 0x34, id="LD A, C"),
        pytest.param("A", "D", 0x56, 0x56, id="LD A, D"),
        pytest.param("A", "E", 0x78, 0x78, id="LD A, E"),
        pytest.param("A", "H", 0x9A, 0x9A, id="LD A, H"),
        pytest.param("A", "L", 0xBC, 0xBC, id="LD A, L"),
        pytest.param("B", "A", 0xDE, 0xDE, id="LD B, A"),
        pytest.param("B", "C", 0x12, 0x12, id="LD B, C"),
        pytest.param("B", "D", 0x34, 0x34, id="LD B, D"),
        pytest.param("B", "E", 0x56, 0x56, id="LD B, E"),
        pytest.param("B", "H", 0x78, 0x78, id="LD B, H"),
        pytest.param("B", "L", 0x9A, 0x9A, id="LD B, L"),
        pytest.param("C", "A", 0xBC, 0xBC, id="LD C, A"),
        pytest.param("C", "B", 0xDE, 0xDE, id="LD C, B"),
        pytest.param("C", "D", 0x12, 0x12, id="LD C, D"),
        pytest.param("C", "E", 0x34, 0x34, id="LD C, E"),
        pytest.param("C", "H", 0x56, 0x56, id="LD C, H"),
        pytest.param("C", "L", 0x78, 0x78, id="LD C, L"),
        pytest.param("D", "A", 0x9A, 0x9A, id="LD D, A"),
        pytest.param("D", "B", 0xBC, 0xBC, id="LD D, B"),
        pytest.param("D", "C", 0xDE, 0xDE, id="LD D, C"),
        pytest.param("D", "E", 0x12, 0x12, id="LD D, E"),
        pytest.param("D", "H", 0x34, 0x34, id="LD D, H"),
        pytest.param("D", "L", 0x56, 0x56, id="LD D, L"),
        pytest.param("E", "A", 0x78, 0x78, id="LD E, A"),
        pytest.param("E", "B", 0x9A, 0x9A, id="LD E, B"),
        pytest.param("E", "C", 0xBC, 0xBC, id="LD E, C"),
        pytest.param("E", "D", 0xDE, 0xDE, id="LD E, D"),
        pytest.param("E", "H", 0x12, 0x12, id="LD E, H"),
        pytest.param("E", "L", 0x34, 0x34, id="LD E, L"),
        pytest.param("H", "A", 0x56, 0x56, id="LD H, A"),
        pytest.param("H", "B", 0x78, 0x78, id="LD H, B"),
        pytest.param("H", "C", 0x9A, 0x9A, id="LD H, C"),
        pytest.param("H", "D", 0xBC, 0xBC, id="LD H, D"),
        pytest.param("H", "E", 0xDE, 0xDE, id="LD H, E"),
        pytest.param("H", "L", 0x12, 0x12, id="LD H, L"),
        pytest.param("L", "A", 0x34, 0x34, id="LD L, A"),
        pytest.param("L", "B", 0x56, 0x56, id="LD L, B"),
        pytest.param("L", "C", 0x78, 0x78, id="LD L, C"),
        pytest.param("L", "D", 0x9A, 0x9A, id="LD L, D"),
        pytest.param("L", "E", 0xBC, 0xBC, id="LD L, E"),
        pytest.param("L", "H", 0xDE, 0xDE, id="LD L, H"),
        pytest.param("A", "A", 0x12, 0x12, id="LD A, A"),
        pytest.param("B", "B", 0x34, 0x34, id="LD B, B"),
        pytest.param("C", "C", 0x56, 0x56, id="LD C, C"),
        pytest.param("D", "D", 0x78, 0x78, id="LD D, D"),
        pytest.param("E", "E", 0x9A, 0x9A, id="LD E, E"),
        pytest.param("H", "H", 0xBC, 0xBC, id="LD H, H"),
        pytest.param("L", "L", 0xDE, 0xDE, id="LD L, L"),
    ]


    ld_r8_mhl_test_cases = [
        # dest_reg, initial_hl, initial_mem_value, expected_dest_value, id
        pytest.param("A", 0xC000, 0x12, 0x12, id="LD A, (HL): Basic"),
        pytest.param("B", 0xC001, 0x34, 0x34, id="LD B, (HL): Basic"),
        pytest.param("C", 0xC002, 0x56, 0x56, id="LD C, (HL): Basic"),
        pytest.param("D", 0xC003, 0x78, 0x78, id="LD D, (HL): Basic"),
        pytest.param("E", 0xC004, 0x9A, 0x9A, id="LD E, (HL): Basic"),
        pytest.param("H", 0xC005, 0xBC, 0xBC, id="LD H, (HL): Basic"),
        pytest.param("L", 0xC006, 0xDE, 0xDE, id="LD L, (HL): Basic"),
    ]

    ld_mhl_r8_test_cases = [
        # initial_hl, src_reg, initial_src_value, expected_mem_value, id
        pytest.param(0xC000, "A", 0x12, 0x12, id="LD (HL), A: Basic"),
        pytest.param(0xC001, "B", 0x34, 0x34, id="LD (HL), B: Basic"),
        pytest.param(0xC002, "C", 0x56, 0x56, id="LD (HL), C: Basic"),
        pytest.param(0xC003, "D", 0x78, 0x78, id="LD (HL), D: Basic"),
        pytest.param(0xC004, "E", 0x9A, 0x9A, id="LD (HL), E: Basic"),
        pytest.param(0xC005, "H", 0xBC, 0xBC, id="LD (HL), H: Basic"),
        pytest.param(0xC006, "L", 0xDE, 0xDE, id="LD (HL), L: Basic"),
    ]

    add_a_r8_test_cases = [
        # initial_a, r8_value, initial_flags, expected_a, expected_flags, id
        pytest.param(0x05, 0x0A, "0000", 0x0F, "0000", id="ADD A, r8: Basic"),
        pytest.param(0x3A, 0xC6, "0000", 0x00, "1010", id="ADD A, r8: Carry and half-carry"),
        pytest.param(0x3C, 0x04, "0000", 0x40, "0010", id="ADD A, r8: Half-carry"),
        pytest.param(0x80, 0x80, "0000", 0x00, "1001", id="ADD A, r8: Carry"),
        pytest.param(0xFF, 0x01, "0000", 0x00, "1010", id="ADD A, r8: Wrap-around"),
    ]

    adc_a_r8_test_cases = [
        # initial_a, r8_value, initial_flags, expected_a, expected_flags, id
        pytest.param(0x05, 0x0A, "0000", 0x0F, "0000", id="ADC A, r8: Basic, no carry"),
        pytest.param(0x05, 0x0A, "0001", 0x10, "0000", id="ADC A, r8: Basic, with carry"),
        pytest.param(0x3A, 0xC6, "0001", 0x01, "0011", id="ADC A, r8: Carry and half-carry, with carry"),
        pytest.param(0x3C, 0x04, "0001", 0x41, "0010", id="ADC A, r8: Half-carry, with carry"),
        pytest.param(0x80, 0x80, "0001", 0x01, "0001", id="ADC A, r8: Carry, with carry"),
        pytest.param(0xFF, 0x00, "0001", 0x00, "1011", id="ADC A, r8: Wrap-around, with carry"),
    ]

    sub_a_r8_test_cases = [
        # initial_a, r8_value, initial_flags, expected_a, expected_flags, id
        pytest.param(0x0F, 0x0A, "0000", 0x05, "0100", id="SUB A, r8: Basic"),
        pytest.param(0x00, 0x01, "0000", 0xFF, "0111", id="SUB A, r8: Borrow"),
        pytest.param(0x3C, 0x0F, "0000", 0x2D, "0100", id="SUB A, r8: No borrow"),
        pytest.param(0x10, 0x08, "0000", 0x08, "0100", id="SUB A, r8: No half-borrow"),
        pytest.param(0x3A, 0x2F, "0000", 0x0B, "0100", id="SUB A, r8: No carry or half-carry"),
    ]

    sbc_a_r8_test_cases = [
        # initial_a, r8_value, initial_flags, expected_a, expected_flags, id
        pytest.param(0x0F, 0x0A, "0000", 0x05, "0100", id="SBC A, r8: Basic, no carry"),
        pytest.param(0x0F, 0x0A, "0001", 0x04, "0100", id="SBC A, r8: Basic, with carry"),
        pytest.param(0x00, 0x01, "0001", 0xFE, "0111", id="SBC A, r8: Borrow, with carry"),
        pytest.param(0x3C, 0x0F, "0001", 0x2C, "0100", id="SBC A, r8: No borrow, with carry"),
        pytest.param(0x10, 0x08, "0001", 0x07, "0100", id="SBC A, r8: No half-borrow, with carry"),
        pytest.param(0x3A, 0x2F, "0001", 0x0A, "0100", id="SBC A, r8: No carry or half-carry, with carry"),
    ]

    and_a_r8_test_cases = [
        # initial_a, r8_value, expected_a, expected_flags, id
        pytest.param(0x55, 0x33, 0x11, "0010", id="AND A, r8: Basic"),
        pytest.param(0xFF, 0x00, 0x00, "1010", id="AND A, r8: Zero result"),
        pytest.param(0x0F, 0xF0, 0x00, "1010", id="AND A, r8: Zero result 2"),
        pytest.param(0xA5, 0xA5, 0xA5, "0010", id="AND A, r8: Same value"),
        pytest.param(0x00, 0xFF, 0x00, "1010", id="AND A, r8: A is zero"),
    ]

# ... existing test cases ...

    # Combined Arithmetic Test Cases (ADD, ADC, SUB, SBC)
    # Format: op_type, source_type, initial_a, value, initial_flags, expected_a, expected_flags, id
    arithmetic_a_test_cases = [
        # --- ADD ---
        pytest.param("add", "r8", 0x05, 0x0A, "0000", 0x0F, "0000", id="ADD A, r8: Basic"),
        pytest.param("add", "r8", 0x3A, 0xC6, "0000", 0x00, "1011", id="ADD A, r8: Carry and half-carry"),
        pytest.param("add", "r8", 0x3C, 0x04, "0000", 0x40, "0010", id="ADD A, r8: Half-carry"),
        pytest.param("add", "r8", 0x80, 0x80, "0000", 0x00, "1001", id="ADD A, r8: Carry"),
        pytest.param("add", "r8", 0xFF, 0x01, "0000", 0x00, "1011", id="ADD A, r8: Wrap-around"),
        pytest.param("add", "mhl", 0x05, 0x0A, "0000", 0x0F, "0000", id="ADD A, (HL): Basic"),
        pytest.param("add", "mhl", 0x3A, 0xC6, "0000", 0x00, "1011", id="ADD A, (HL): Carry and half-carry"),
        pytest.param("add", "d8", 0x05, 0x0A, "0000", 0x0F, "0000", id="ADD A, d8: Basic"),
        pytest.param("add", "d8", 0xFF, 0x01, "0000", 0x00, "1011", id="ADD A, d8: Wrap-around"),

        # --- ADC ---
        pytest.param("adc", "r8", 0x05, 0x0A, "0000", 0x0F, "0000", id="ADC A, r8: Basic, no carry"),
        pytest.param("adc", "r8", 0x05, 0x0A, "0001", 0x10, "0010", id="ADC A, r8: Basic, with carry"),
        pytest.param("adc", "r8", 0x3A, 0xC6, "0001", 0x01, "0011", id="ADC A, r8: Carry and half-carry, with carry"), # Corrected expected flags
        pytest.param("adc", "r8", 0x3C, 0x04, "0001", 0x41, "0010", id="ADC A, r8: Half-carry, with carry"),
        pytest.param("adc", "r8", 0x80, 0x80, "0001", 0x01, "0001", id="ADC A, r8: Carry, with carry"), # Corrected expected flags
        pytest.param("adc", "r8", 0xFF, 0x00, "0001", 0x00, "1011", id="ADC A, r8: Wrap-around, with carry"),
        pytest.param("adc", "mhl", 0x05, 0x0A, "0001", 0x10, "0010", id="ADC A, (HL): Basic, with carry"),
        pytest.param("adc", "mhl", 0x3A, 0xC6, "0001", 0x01, "0011", id="ADC A, (HL): Carry and half-carry, with carry"), # Corrected expected flags
        pytest.param("adc", "d8", 0x05, 0x0A, "0001", 0x10, "0010", id="ADC A, d8: Basic, with carry"),
        pytest.param("adc", "d8", 0xFF, 0x00, "0001", 0x00, "1011", id="ADC A, d8: Wrap-around, with carry"),

        # --- SUB ---
        pytest.param("sub", "r8", 0x0F, 0x0A, "0000", 0x05, "0100", id="SUB A, r8: Basic"),
        pytest.param("sub", "r8", 0x00, 0x01, "0000", 0xFF, "0111", id="SUB A, r8: Borrow"),
        pytest.param("sub", "r8", 0x3C, 0x0F, "0000", 0x2D, "0110", id="SUB A, r8: Half Borrow"), # Corrected expected flags
        # pytest.param("sub", "r8", 0x10, 0x08, "0000", 0x08, "0100", id="SUB A, r8: No half-borrow"),
        pytest.param("sub", "r8", 0x3A, 0x2F, "0000", 0x0B, "0110", id="SUB A, r8: Half Borrow 2"), # Corrected expected flags
        pytest.param("sub", "mhl", 0x0F, 0x0A, "0000", 0x05, "0100", id="SUB A, (HL): Basic"),
        pytest.param("sub", "mhl", 0x00, 0x01, "0000", 0xFF, "0111", id="SUB A, (HL): Borrow"),
        pytest.param("sub", "d8", 0x0F, 0x0A, "0000", 0x05, "0100", id="SUB A, d8: Basic"),
        pytest.param("sub", "d8", 0x00, 0x01, "0000", 0xFF, "0111", id="SUB A, d8: Borrow"),

        # --- SBC ---
        pytest.param("sbc", "r8", 0x0F, 0x0A, "0000", 0x05, "0100", id="SBC A, r8: Basic, no carry"),
        pytest.param("sbc", "r8", 0x0F, 0x0A, "0001", 0x04, "0100", id="SBC A, r8: Basic, with carry"),
        pytest.param("sbc", "r8", 0x00, 0x01, "0001", 0xFE, "0111", id="SBC A, r8: Borrow, with carry"),
        pytest.param("sbc", "r8", 0x3C, 0x0F, "0001", 0x2C, "0110", id="SBC A, r8: Half Borrow, with carry"), # Corrected expected flags
        pytest.param("sbc", "r8", 0x10, 0x08, "0001", 0x07, "0110", id="SBC A, r8: Half Borrow 2, with carry"), # Corrected expected flags
        pytest.param("sbc", "r8", 0x3A, 0x2F, "0001", 0x0A, "0110", id="SBC A, r8: Half Borrow 3, with carry"), # Corrected expected flags
        pytest.param("sbc", "mhl", 0x0F, 0x0A, "0001", 0x04, "0100", id="SBC A, (HL): Basic, with carry"),
        pytest.param("sbc", "mhl", 0x00, 0x01, "0001", 0xFE, "0111", id="SBC A, (HL): Borrow, with carry"),
        pytest.param("sbc", "d8", 0x0F, 0x0A, "0001", 0x04, "0100", id="SBC A, d8: Basic, with carry"),
        pytest.param("sbc", "d8", 0x00, 0x01, "0001", 0xFE, "0111", id="SBC A, d8: Borrow, with carry"),
    ]

    xor_a_r8_test_cases = [
        # initial_a, r8_value, expected_a, expected_flags, id
        pytest.param(0x55, 0x33, 0x66, "0000", id="XOR A, r8: Basic"),
        pytest.param(0xFF, 0x0F, 0xF0, "0000", id="XOR A, r8: Clear lower nibble"),
        pytest.param(0xAA, 0xAA, 0x00, "1000", id="XOR A, r8: Zero result (Z=1)"),
        pytest.param(0x00, 0xFF, 0xFF, "0000", id="XOR A, r8: A is zero"),
        pytest.param(0xA5, 0x00, 0xA5, "0000", id="XOR A, r8: r8 is zero"),
        pytest.param(0xFF, 0xFF, 0x00, "1000", id="XOR A, r8: All bits set -> Zero"),
    ]

    or_a_r8_test_cases = [
        # initial_a, r8_value, expected_a, expected_flags, id
        pytest.param(0x55, 0x33, 0x77, "0000", id="OR A, r8: Basic"),
        pytest.param(0xF0, 0x0F, 0xFF, "0000", id="OR A, r8: Combine nibbles"),
        pytest.param(0x00, 0x00, 0x00, "1000", id="OR A, r8: Zero result (Z=1)"),
        pytest.param(0x00, 0xFF, 0xFF, "0000", id="OR A, r8: A is zero"),
        pytest.param(0xA5, 0x00, 0xA5, "0000", id="OR A, r8: r8 is zero"),
        pytest.param(0xAA, 0x55, 0xFF, "0000", id="OR A, r8: Complementary bits -> All set"),
    ]

    cp_a_test_cases = [
        # initial_a, value, expected_a, expected_flags (ZNHC), id
        pytest.param(0x3A, 0x3A, 0x3A, "1100", id="CP A, r8: Equal (Z=1)"),
        pytest.param(0x3A, 0x2F, 0x3A, "0110", id="CP A, r8: Greater, Half Borrow (H=1)"),
        pytest.param(0x3A, 0x40, 0x3A, "0101", id="CP A, r8: Less (C=1)"),
        pytest.param(0x00, 0x01, 0x00, "0111", id="CP A, r8: Less, Borrow, Half Borrow (C=1, H=1)"),
        pytest.param(0xFF, 0x00, 0xFF, "0100", id="CP A, r8: Greater, Max A"),
        pytest.param(0x00, 0x00, 0x00, "1100", id="CP A, r8: Zero vs Zero (Z=1)"),
        pytest.param(0x10, 0x08, 0x10, "0110", id="CP A, r8: Half Borrow (H=1)"),
        pytest.param(0x0F, 0x10, 0x0F, "0101", id="CP A, r8: Less, Borrow (C=1)"),
        pytest.param(0x55, 0xAA, 0x55, "0101", id="CP A, r8: Less, Borrow (C=1), No Half Borrow"),
        pytest.param(0xAA, 0x55, 0xAA, "0100", id="CP A, r8: Greater, No Borrow, No Half Borrow"),
    ]

    #==========================================
    #          STAC MANIPULATIONS TEST CASES
    #==========================================

    call_test_cases = [
        # method_name, initial_pc, target_addr, initial_sp, initial_flags, call_taken, expected_pc_override, expected_sp, expected_stack_val, expected_cycles, id
        pytest.param("_call_a16", 0xC100, 0x2000, 0xFFFE, "----", True, 0x2000, 0xFFFC, 0xC103, 24, id="CALL a16: Basic"), # PC=0xC100, Return=0xC103
        pytest.param("_call_nz_a16", 0xC100, 0x2000, 0xFFFE, "0---", True,  0x2000, 0xFFFC, 0xC103, 24, id="CALL NZ: Condition Met (Z=0)"),
        pytest.param("_call_nz_a16", 0xC100, 0x2000, 0xFFFE, "1---", False, None,   0xFFFE, 0x0000, 12, id="CALL NZ: Condition Not Met (Z=1)"),
        pytest.param("_call_z_a16", 0xC100, 0x2000, 0xFFFE, "1---", True,  0x2000, 0xFFFC, 0xC103, 24, id="CALL Z: Condition Met (Z=1)"),
        pytest.param("_call_z_a16", 0xC100, 0x2000, 0xFFFE, "0---", False, None,   0xFFFE, 0x0000, 12, id="CALL Z: Condition Not Met (Z=0)"),
        pytest.param("_call_nc_a16", 0xC100, 0x2000, 0xFFFE, "---0", True,  0x2000, 0xFFFC, 0xC103, 24, id="CALL NC: Condition Met (C=0)"),
        pytest.param("_call_nc_a16", 0xC100, 0x2000, 0xFFFE, "---1", False, None,   0xFFFE, 0x0000, 12, id="CALL NC: Condition Not Met (C=1)"),
        pytest.param("_call_c_a16", 0xC100, 0x2000, 0xFFFE, "---1", True,  0x2000, 0xFFFC, 0xC103, 24, id="CALL C: Condition Met (C=1)"),
        pytest.param("_call_c_a16", 0xC100, 0x2000, 0xFFFE, "---0", False, None,   0xFFFE, 0x0000, 12, id="CALL C: Condition Not Met (C=0)"),
    ]

    push_test_cases = [
        # reg_pair_name, initial_value, initial_sp, expected_sp, expected_stack_msb, expected_stack_lsb, id
        pytest.param("AF", 0xABCD, 0xFFFE, 0xFFFC, 0xAB, 0xC0, id="PUSH AF: Basic"), # Note: F lower nibble ignored on POP, but pushed as is
        pytest.param("BC", 0x1234, 0xFFFE, 0xFFFC, 0x12, 0x34, id="PUSH BC: Basic"),
        pytest.param("DE", 0x5678, 0xFFFE, 0xFFFC, 0x56, 0x78, id="PUSH DE: Basic"),
        pytest.param("HL", 0x9ABC, 0xFFFE, 0xFFFC, 0x9A, 0xBC, id="PUSH HL: Basic"),
        pytest.param("BC", 0x00FF, 0xC002, 0xC000, 0x00, 0xFF, id="PUSH BC: Different SP"),
        pytest.param("HL", 0xFF00, 0xC002, 0xC000, 0xFF, 0x00, id="PUSH HL: Different SP"),
    ]

    pop_test_cases = [
        # reg_pair_name, initial_sp, stack_msb, stack_lsb, expected_value, expected_sp, expected_flags_after (ZNHC), id
        # Note: For POP AF, expected_value checks A, expected_flags_after checks F (masked)
        pytest.param("AF", 0xFFFC, 0xAB, 0xCD, 0xAB00, 0xFFFE, "1011", id="POP AF: Basic (F masked)"), # Stack: CD AB -> A=AB, F=C0 (Z=1,N=0,H=1,C=0)
        pytest.param("BC", 0xFFFC, 0x12, 0x34, 0x1234, 0xFFFE, "----", id="POP BC: Basic"),
        pytest.param("DE", 0xFFFC, 0x56, 0x78, 0x5678, 0xFFFE, "----", id="POP DE: Basic"),
        pytest.param("HL", 0xFFFC, 0x9A, 0xBC, 0x9ABC, 0xFFFE, "----", id="POP HL: Basic"),
        pytest.param("BC", 0xC000, 0x00, 0xFF, 0x00FF, 0xC002, "----", id="POP BC: Different SP"),
        pytest.param("AF", 0xC000, 0x01, 0x1F, 0x0100, 0xC002, "0001", id="POP AF: F=10 (C=1)"), # Stack: 1F 01 -> A=01, F=10 (Z=0,N=0,H=0,C=1)
        pytest.param("AF", 0xC000, 0x01, 0x85, 0x0100, 0xC002, "1000", id="POP AF: F=80 (Z=1)"), # Stack: 85 01 -> A=01, F=80 (Z=1,N=0,H=0,C=0)
    ]

    #==========================================
    #           TEST IMPLEMENTATIONS          
    #==========================================

    def test_init_pc(self, cpu):
        """Test initial Program Counter value"""
        assert cpu.CoreWords.PC == 0x0100

    @pytest.mark.parametrize("reg_name, initial_value, expected_value", inc_r16_test_cases)
    def test_inc_r16(self, cpu, reg_name, initial_value, expected_value):
        """Tests 16-bit register increment methods (_inc_XX)"""
        # Arrange
        setattr(cpu.CoreWords, reg_name, initial_value)
        initial_flags = cpu.Flags.F
        method_name = f"_inc_{reg_name.lower()}"
        instruction_method = getattr(cpu, method_name)
        
        # Act
        pc_override, cycle_override = instruction_method(None)
        
        # Assert
        final_value = getattr(cpu.CoreWords, reg_name)
        assert final_value == expected_value, f"Reg {reg_name} expected {expected_value:04X}, got {final_value:04X}"
        
        final_flags = cpu.Flags.F
        assert final_flags == initial_flags, f"Flags changed unexpectedly ({initial_flags:02X} -> {final_flags:02X})"
        
        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None"

    @pytest.mark.parametrize("reg_name, initial_value, expected_value", dec_r16_test_cases)
    def test_dec_r16(self, cpu, reg_name, initial_value, expected_value):
        """Tests 16-bit register decrement methods (_dec_XX)"""
        # Arrange
        setattr(cpu.CoreWords, reg_name, initial_value)
        initial_flags = cpu.Flags.F
        method_name = f"_dec_{reg_name.lower()}"
        instruction_method = getattr(cpu, method_name)
        
        # Act
        pc_override, cycle_override = instruction_method(None)
        
        # Assert
        final_value = getattr(cpu.CoreWords, reg_name)
        assert final_value == expected_value, f"Reg {reg_name} expected {expected_value:04X}, got {final_value:04X}"
        
        final_flags = cpu.Flags.F
        assert final_flags == initial_flags, f"Flags changed unexpectedly ({initial_flags:02X} -> {final_flags:02X})"
        
        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None"

    @pytest.mark.parametrize("reg_name, initial_value, expected_value, expected_flags", inc_r8_test_cases)
    def test_inc_r8(self, cpu, reg_name, initial_value, expected_value, expected_flags):
        """Tests 8-bit register increment methods (_inc_X)"""
        # Arrange
        setattr(cpu.CoreReg, reg_name, initial_value)
        
        # Set initial flags (opposite of expected where possible) to test changes
        expected_z, expected_n, expected_h = expected_flags
        cpu.Flags.z = 0 if expected_z else 1
        cpu.Flags.n = 1  # INC should clear N
        cpu.Flags.h = 0 if expected_h else 1
        cpu.Flags.c = 0  # Set initial C to verify it's unchanged
        initial_c = cpu.Flags.c
        
        method_name = f"_inc_{reg_name.lower()}"
        instruction_method = getattr(cpu, method_name)
        
        # Act
        pc_override, cycle_override = instruction_method(None)
        
        # Assert
        final_value = getattr(cpu.CoreReg, reg_name)
        assert final_value == expected_value, f"Reg {reg_name} expected {expected_value:02X}, got {final_value:02X}"
        
        assert cpu.Flags.z == expected_z, f"Z flag mismatch for {reg_name}"
        assert cpu.Flags.n == expected_n, f"N flag mismatch for {reg_name}"
        assert cpu.Flags.h == expected_h, f"H flag mismatch for {reg_name}"
        assert cpu.Flags.c == initial_c, f"C flag should remain unchanged"
        
        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None"

    @pytest.mark.parametrize("reg_name, initial_value, expected_value, expected_flags", dec_r8_test_cases)
    def test_dec_r8(self, cpu, reg_name, initial_value, expected_value, expected_flags):
        """Tests 8-bit register decrement methods (_dec_X)"""
        # Arrange
        setattr(cpu.CoreReg, reg_name, initial_value)
        
        # Set initial flags (opposite of expected where possible) to test changes
        expected_z, expected_n, expected_h = expected_flags
        cpu.Flags.z = 0 if expected_z else 1
        cpu.Flags.n = 0  # DEC should set N
        cpu.Flags.h = 0 if expected_h else 1
        cpu.Flags.c = 1  # Set initial C to verify it's unchanged
        initial_c = cpu.Flags.c
        
        method_name = f"_dec_{reg_name.lower()}"
        instruction_method = getattr(cpu, method_name)
        
        # Act
        pc_override, cycle_override = instruction_method(None)
        
        # Assert
        final_value = getattr(cpu.CoreReg, reg_name)
        assert final_value == expected_value, f"Reg {reg_name} expected {expected_value:02X}, got {final_value:02X}"
        
        assert cpu.Flags.z == expected_z, f"Z flag mismatch for {reg_name}"
        assert cpu.Flags.n == expected_n, f"N flag mismatch for {reg_name}"
        assert cpu.Flags.h == expected_h, f"H flag mismatch for {reg_name}"
        assert cpu.Flags.c == initial_c, f"C flag should remain unchanged"
        
        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None"

    @pytest.mark.parametrize("reg_name, d8_value, method_name", ld_r8_d8_test_cases)
    def test_ld_r8_d8_methods(self, cpu, reg_name, d8_value, method_name):
        """Tests 8-bit immediate load methods (_ld_X_d8)"""
        # Arrange
        operand_address = 0xC051  # Example address for d8 (WRAM)
        cpu.Memory.writeByte(d8_value, operand_address)
        initial_flags = cpu.Flags.F
        instruction_method = getattr(cpu, method_name)
        
        # Act
        pc_override, cycle_override = instruction_method(operand_address)
        
        # Assert
        final_reg_value = getattr(cpu.CoreReg, reg_name)
        assert final_reg_value == d8_value, f"Reg {reg_name} expected {d8_value:02X}, got {final_reg_value:02X}"
        
        final_flags = cpu.Flags.F
        assert final_flags == initial_flags, f"Flags changed unexpectedly ({initial_flags:02X} -> {final_flags:02X})"
        
        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None"

    @pytest.mark.parametrize("reg_name, d16_value, method_name", ld_r16_d16_test_cases)
    def test_ld_r16_d16_methods(self, cpu, reg_name, d16_value, method_name):
        """Tests 16-bit immediate load methods (_ld_XX_d16)"""
        # Arrange
        operand_address = 0xC050  # Example writable address
        lsb = d16_value & 0xFF
        msb = (d16_value >> 8) & 0xFF
        
        # Write LSB and MSB to memory (Little Endian)
        cpu.Memory.writeByte(lsb, operand_address)
        cpu.Memory.writeByte(msb, operand_address + 1)
        
        initial_flags = cpu.Flags.F
        instruction_method = getattr(cpu, method_name)
        
        # Act
        pc_override, cycle_override = instruction_method(operand_address)
        
        # Assert
        final_reg_value = getattr(cpu.CoreWords, reg_name)
        assert final_reg_value == d16_value, f"Reg {reg_name} expected {d16_value:04X}, got {final_reg_value:04X}"
        
        final_flags = cpu.Flags.F
        assert final_flags == initial_flags, f"Flags changed unexpectedly ({initial_flags:02X} -> {final_flags:02X})"
        
        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None"

    @pytest.mark.parametrize("initial_a, initial_c, expected_a, expected_flags", rlca_test_cases)
    def test_rlca(self, cpu, initial_a, initial_c, expected_a, expected_flags):
        """Tests rotate left carry accumulator (_rlca)"""
        # Arrange
        cpu.CoreReg.A = initial_a
        cpu.Flags.flagReset()
        cpu.Flags.c = initial_c
        
        expected_z, expected_n, expected_h, expected_c = expected_flags
        
        # Act
        pc_override, cycle_override = cpu._rlca(None)
        
        # Assert
        final_a = cpu.CoreReg.A
        assert final_a == expected_a, f"Accumulator A expected {expected_a:02X}, got {final_a:02X}"
        
        assert cpu.Flags.z == expected_z, f"Z flag mismatch"
        assert cpu.Flags.n == expected_n, f"N flag mismatch"
        assert cpu.Flags.h == expected_h, f"H flag mismatch"
        assert cpu.Flags.c == expected_c, f"C flag mismatch"
        
        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None"

    @pytest.mark.parametrize("method_name, initial_value, expected_value, expected_flags", memory_operation_test_cases)
    def test_memory_operations(self, cpu, method_name, initial_value, expected_value, expected_flags):
        """Tests memory operations at the HL address (_inc_mhl, _dec_mhl)"""
        # Arrange
        cpu.CoreWords.HL = 0xC051  # Example memory location
        cpu.Memory.writeByte(initial_value, cpu.CoreWords.HL)
        cpu.Flags.F = 0x00  # Reset flags for consistent testing
        instruction_method = getattr(cpu, method_name)
        
        # Act
        pc_override, cycle_override = instruction_method(None)
        
        # Assert
        final_value = cpu.Memory.readByte(cpu.CoreWords.HL)
        assert final_value == expected_value, f"Memory value expected {expected_value:02X}, got {final_value:02X}"
        
        # Parse expected flag string into individual flag expectations
        z_expected = 1 if expected_flags[0] == '1' else 0
        n_expected = 1 if expected_flags[1] == '1' else 0
        h_expected = 1 if expected_flags[2] == '1' else 0
        c_expected = 1 if expected_flags[3] == '1' else 0
        
        assert cpu.Flags.z == z_expected, f"Z flag mismatch"
        assert cpu.Flags.n == n_expected, f"N flag mismatch"
        assert cpu.Flags.h == h_expected, f"H flag mismatch"
        assert cpu.Flags.c == c_expected, f"C flag mismatch"
        
        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None"

    @pytest.mark.parametrize("method_name, initial_a, initial_flags, expected_a, expected_flags", rotation_test_cases)
    def test_rotation_operations(self, cpu, method_name, initial_a, initial_flags, expected_a, expected_flags):
        """Tests accumulator rotation operations (_rlca, _rrca, _rla, _rra)"""
        # Arrange
        cpu.CoreReg.A = initial_a
        
        # Set initial flags
        z_flag = 1 if initial_flags[0] == '1' else 0
        n_flag = 1 if initial_flags[1] == '1' else 0
        h_flag = 1 if initial_flags[2] == '1' else 0
        c_flag = 1 if initial_flags[3] == '1' else 0
        
        cpu.Flags.z = z_flag
        cpu.Flags.n = n_flag
        cpu.Flags.h = h_flag
        cpu.Flags.c = c_flag
        
        instruction_method = getattr(cpu, method_name)
        
        # Act
        pc_override, cycle_override = instruction_method(None)
        
        # Assert
        final_a = cpu.CoreReg.A
        assert final_a == expected_a, f"Accumulator value expected {expected_a:02X}, got {final_a:02X}"
        
        # Parse expected flag string into individual flag expectations
        z_expected = 1 if expected_flags[0] == '1' else 0
        n_expected = 1 if expected_flags[1] == '1' else 0
        h_expected = 1 if expected_flags[2] == '1' else 0
        c_expected = 1 if expected_flags[3] == '1' else 0
        
        assert cpu.Flags.z == z_expected, f"Z flag mismatch"
        assert cpu.Flags.n == n_expected, f"N flag mismatch"
        assert cpu.Flags.h == h_expected, f"H flag mismatch"
        assert cpu.Flags.c == c_expected, f"C flag mismatch"
        
        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None"

    @pytest.mark.parametrize("method_name, register_value, initial_hl, expected_hl, expected_flags", add_hl_test_cases)
    def test_add_hl_operations(self, cpu, method_name, register_value, initial_hl, expected_hl, expected_flags):
        """Tests operations that add values to HL register (_add_hl_*)"""
        # Arrange
        cpu.CoreWords.HL = initial_hl
        cpu.Flags.F = 0x00  # Reset flags for consistent testing
            
        instruction_method = getattr(cpu, method_name)

        operand_address = cpu.CoreWords.HL # Placeholder for operand address

        # Set up the appropriate register with the test value
        if "_bc" in method_name:
            cpu.CoreWords.BC = register_value
            # operand_address = cpu.CoreWords.BC
        elif "_de" in method_name:
            cpu.CoreWords.DE = register_value
            # operand_address = cpu.CoreWords.DE
        elif "hl_hl" in method_name: # Check for unique method of add_hl_hl
            cpu.CoreWords.HL = register_value
            # operand_address = cpu.CoreWords.HL
        elif "_sp" in method_name:
            cpu.CoreWords.SP = register_value
            # operand_address = cpu.CoreWords.SP

        # Act
        pc_override, cycle_override = instruction_method(None)
        
        # Assert
        assert cpu.CoreWords.HL == expected_hl, f"HL value expected {expected_hl:04X}, got {cpu.CoreWords.HL:04X}"
        
        # Parse expected flag string into individual flag expectations
        z_expected = 1 if expected_flags[0] == '1' else 0
        n_expected = 1 if expected_flags[1] == '1' else 0
        h_expected = 1 if expected_flags[2] == '1' else 0
        c_expected = 1 if expected_flags[3] == '1' else 0
        
        assert cpu.Flags.z == z_expected, f"Z flag mismatch"
        assert cpu.Flags.n == n_expected, f"N flag mismatch"
        assert cpu.Flags.h == h_expected, f"H flag mismatch"
        assert cpu.Flags.c == c_expected, f"C flag mismatch"
        
        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None"


    @pytest.mark.parametrize("reg_name, mem_addr, initial_a, expected_mem_value", ld_mr16_a_test_cases)
    def test_ld_mr16_a(self, cpu, reg_name, mem_addr, initial_a, expected_mem_value):
        """Tests load (BC), A / load (DE), A / load (HL), A instructions"""
        # Arrange
        cpu.CoreWords.HL = mem_addr
        initial_hl = cpu.CoreWords.HL
        if reg_name == "HL+":
            cpu.CoreWords.HL = mem_addr
            method_name = "_ld_mhlp_a"
        elif reg_name == "HL-":
            cpu.CoreWords.HL = mem_addr
            method_name = "_ld_mhlm_a"
        else:
            setattr(cpu.CoreWords, reg_name, mem_addr)  # Set r16 to point to memory address
            method_name = f"_ld_m{reg_name.lower()}_a"

        cpu.CoreReg.A = initial_a  # Set initial value of A
        cpu.Memory.writeByte(0x00, mem_addr)  # Initialize memory location

        instruction_method = getattr(cpu, method_name)

        # Act
        pc_override, cycle_override = instruction_method(None)

        # Assert
        memory_value = cpu.Memory.readByte(mem_addr)
        assert memory_value == expected_mem_value, f"Memory at {mem_addr:04X} expected {expected_mem_value:02X}, got {memory_value:02X}"

        if reg_name == "HL+":
            assert cpu.CoreWords.HL == mem_addr + 1, "HL+ post-increment failed"
        elif reg_name == "HL-":
            assert cpu.CoreWords.HL == mem_addr - 1, "HL- post-decrement failed"
        else:
            assert cpu.CoreWords.HL == initial_hl, "HL should not be modified"

        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None"

    @pytest.mark.parametrize("mem_addr, initial_sp, expected_lsb, expected_msb", ld_m16_sp_test_cases)
    def test_ld_m16_sp(self, cpu, mem_addr, initial_sp, expected_lsb, expected_msb):
        """Tests load (a16), SP instruction"""
        # Arrange
        cpu.CoreWords.SP = initial_sp
        cpu.Memory.writeByte(0x00, mem_addr)  # Initialize memory location
        cpu.Memory.writeByte(0x00, mem_addr + 1)  # Initialize memory location + 1

        # Act
        pc_override, cycle_override = cpu._ld_m16_sp(mem_addr)

        # Assert
        memory_lsb = cpu.Memory.readByte(mem_addr)
        memory_msb = cpu.Memory.readByte(mem_addr + 1)
        assert memory_lsb == expected_lsb, f"LSB at {mem_addr:04X} expected {expected_lsb:02X}, got {memory_lsb:02X}"
        assert memory_msb == expected_msb, f"MSB at {mem_addr + 1:04X} expected {expected_msb:02X}, got {memory_msb:02X}"

        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None"

    @pytest.mark.parametrize("reg_name, mem_addr, initial_mem_value, expected_a", ld_a_mr16_test_cases)
    def test_ld_a_mr16(self, cpu, reg_name, mem_addr, initial_mem_value, expected_a):
        """Tests load A, (BC) / load A, (DE) / load A, (HL) instructions"""
        
        # Arrange
        cpu.CoreWords.HL = mem_addr
        initial_hl = cpu.CoreWords.HL
        if reg_name == "HL+":
            cpu.CoreWords.HL = mem_addr
            method_name = "_ld_a_mhlp"
        elif reg_name == "HL-":
            cpu.CoreWords.HL = mem_addr
            method_name = "_ld_a_mhlm"
        else:
            setattr(cpu.CoreWords, reg_name, mem_addr)  # Set r16 to point to memory address
            method_name = f"_ld_a_m{reg_name.lower()}"

        cpu.Memory.writeByte(initial_mem_value, mem_addr)  # Initialize memory location

        instruction_method = getattr(cpu, method_name)

        # Act
        pc_override, cycle_override = instruction_method(None)

        # Assert
        assert cpu.CoreReg.A == expected_a, f"A register expected {expected_a:02X}, got {cpu.CoreReg.A:02X}"

        if reg_name == "HL+":
            assert cpu.CoreWords.HL == mem_addr + 1, "HL+ post-increment failed"
        elif reg_name == "HL-":
            assert cpu.CoreWords.HL == mem_addr - 1, "HL- post-decrement failed"
        else:
            assert cpu.CoreWords.HL == initial_hl, "HL should not be modified"

        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None"

    @pytest.mark.parametrize("mnemonic, initial_flags, offset, expected_pc, cycles", jump_test_cases)
    def test_jump_routines(self, cpu, mnemonic, initial_flags, offset, expected_pc, cycles):
        """Tests relative jump routines"""
        # Arrange
        cpu.CoreWords.PC = 0x0100  # Initial PC value

        # Set initial flag values based on the initial_flags string
        if initial_flags[0] != "-":
            cpu.Flags.z = int(initial_flags[0])
        if initial_flags[1] != "-":
            cpu.Flags.n = int(initial_flags[1])
        if initial_flags[2] != "-":
            cpu.Flags.h = int(initial_flags[2])
        if initial_flags[3] != "-":
            cpu.Flags.c = int(initial_flags[3])

        instruction_method = getattr(cpu, mnemonic)
        operand_address = np.int8(offset)

        # Act
        pc_override, cycle_override = instruction_method(operand_address)

        # Assert
        assert cpu.CoreWords.PC == expected_pc, f"PC expected {expected_pc:04X}, got {cpu.CoreWords.PC:04X}"
        assert cycle_override == cycles, f"Cycles expected {cycles}, got {cycle_override}"
        assert pc_override is None, "PC override should be None"

    @pytest.mark.parametrize("dest_reg, src_reg, initial_src_value, expected_dest_value", ld_r8_r8_test_cases)
    def test_ld_r8_r8(self, cpu, dest_reg, src_reg, initial_src_value, expected_dest_value):
        """Tests 8-bit register load methods (_ld_X_Y)"""
        # Arrange
        setattr(cpu.CoreReg, src_reg, initial_src_value)
        initial_flags = cpu.Flags.F  # Save initial flag state

        method_name = f"_ld_{dest_reg.lower()}_{src_reg.lower()}"
        instruction_method = getattr(cpu, method_name)

        # Act
        pc_override, cycle_override = instruction_method(None)

        # Assert
        final_dest_value = getattr(cpu.CoreReg, dest_reg)
        assert final_dest_value == expected_dest_value, f"Reg {dest_reg} expected {expected_dest_value:02X}, got {final_dest_value:02X}"

        final_flags = cpu.Flags.F  # Get final flag state
        assert final_flags == initial_flags, f"Flags changed unexpectedly ({initial_flags:02X} -> {final_flags:02X})"

        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None"

    @pytest.mark.parametrize("dest_reg, initial_hl, initial_mem_value, expected_dest_value", ld_r8_mhl_test_cases)
    def test_ld_r8_mhl(self, cpu, dest_reg, initial_hl, initial_mem_value, expected_dest_value):
        """Tests load register from memory at HL (_ld_X_mhl)"""
        # Arrange
        cpu.CoreWords.HL = initial_hl
        cpu.Memory.writeByte(initial_mem_value, initial_hl)
        initial_flags = cpu.Flags.F  # Save initial flag state

        method_name = f"_ld_{dest_reg.lower()}_mhl"
        instruction_method = getattr(cpu, method_name)

        # Act
        pc_override, cycle_override = instruction_method(None)

        # Assert
        final_dest_value = getattr(cpu.CoreReg, dest_reg)
        assert final_dest_value == expected_dest_value, f"Reg {dest_reg} expected {expected_dest_value:02X}, got {final_dest_value:02X}"

        final_flags = cpu.Flags.F  # Get final flag state
        assert final_flags == initial_flags, f"Flags changed unexpectedly ({initial_flags:02X} -> {final_flags:02X})"

        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None"

# TODO - FIXME - Need to update how HL is accessed in the CPU class to first grab the initial value of HL, then do any manipulations on it

    @pytest.mark.parametrize("initial_hl, src_reg, initial_src_value, expected_mem_value", ld_mhl_r8_test_cases)
    def test_ld_mhl_r8(self, cpu, initial_hl, src_reg, initial_src_value, expected_mem_value):
        """Tests load memory at HL from register (_ld_mhl_X)"""
        # Arrange
        cpu.CoreWords.HL = initial_hl
        setattr(cpu.CoreReg, src_reg, initial_src_value)
        cpu.Memory.writeByte(0x00, initial_hl)  # Initialize memory location
        initial_flags = cpu.Flags.F  # Save initial flag state

        method_name = f"_ld_mhl_{src_reg.lower()}"
        instruction_method = getattr(cpu, method_name)

        # Act
        pc_override, cycle_override = instruction_method(None)

        # Assert
        memory_value = cpu.Memory.readByte(initial_hl)
        assert memory_value == expected_mem_value, f"Memory at {initial_hl:04X} expected {expected_mem_value:02X}, got {memory_value:02X}"

        final_flags = cpu.Flags.F  # Get final flag state
        assert final_flags == initial_flags, f"Flags changed unexpectedly ({initial_flags:02X} -> {final_flags:02X})"

        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None"

    @pytest.mark.parametrize("initial_a, r8_value, expected_a, expected_flags", and_a_r8_test_cases)
    def test_and_a_r8(self, cpu, initial_a, r8_value, expected_a, expected_flags):
        """Tests AND A, r8 instructions"""
        # Arrange
        cpu.CoreReg.A = initial_a
        cpu.CoreReg.B = r8_value  # Use B as the source register for testing
        cpu.Flags.z = 0  # Initialize Z to opposite of expected
        cpu.Flags.n = 1  # Initialize N to opposite of expected
        cpu.Flags.h = 0  # Initialize H to opposite of expected
        cpu.Flags.c = 1  # Initialize C to opposite of expected

        # Act
        pc_override, cycle_override = cpu._and_a_b(None)

        # Assert
        assert cpu.CoreReg.A == expected_a, f"A register expected {expected_a:02X}, got {cpu.CoreReg.A:02X}"
        assert cpu.Flags.z == int(expected_flags[0]), "Z flag mismatch"
        assert cpu.Flags.n == int(expected_flags[1]), "N flag mismatch"
        assert cpu.Flags.h == int(expected_flags[2]), "H flag mismatch"
        assert cpu.Flags.c == int(expected_flags[3]), "C flag mismatch"

        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None"

    @pytest.mark.parametrize("op_type, source_type, initial_a, value, initial_flags, expected_a, expected_flags", arithmetic_a_test_cases)
    def test_arithmetic_a(self, cpu, op_type, source_type, initial_a, value, initial_flags, expected_a, expected_flags):
        """Tests ADD A, ADC A, SUB A, SBC A instructions for r8, (HL), and d8 sources."""
        # Arrange
        cpu.CoreReg.A = initial_a
        cpu.Flags.z = int(initial_flags[0])
        cpu.Flags.n = int(initial_flags[1])
        cpu.Flags.h = int(initial_flags[2])
        cpu.Flags.c = int(initial_flags[3])

        operand = None
        mem_addr = 0xC050 # Default memory address for (HL) and d8

        if source_type == 'r8':
            cpu.CoreReg.B = value # Use B as the representative r8 source
            method_name = f"_{op_type}_a_b"
        elif source_type == 'mhl':
            cpu.CoreWords.HL = mem_addr
            cpu.Memory.writeByte(value, mem_addr)
            method_name = f"_{op_type}_a_mhl"
        elif source_type == 'd8':
            cpu.Memory.writeByte(value, mem_addr) # Simulate fetching d8 from this address
            operand = mem_addr
            method_name = f"_{op_type}_a_d8"
        else:
            pytest.fail(f"Invalid source_type: {source_type}")

        instruction_method = getattr(cpu, method_name)

        # Act
        pc_override, cycle_override = instruction_method(operand) # Pass operand address for d8

        # Assert
        assert cpu.CoreReg.A == expected_a, f"A register expected {expected_a:02X}, got {cpu.CoreReg.A:02X}"
        assert cpu.Flags.z == int(expected_flags[0]), "Z flag mismatch"
        assert cpu.Flags.n == int(expected_flags[1]), "N flag mismatch"
        assert cpu.Flags.h == int(expected_flags[2]), "H flag mismatch"
        assert cpu.Flags.c == int(expected_flags[3]), "C flag mismatch"

        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None"


    @pytest.mark.parametrize("initial_a, r8_value, expected_a, expected_flags", xor_a_r8_test_cases)
    def test_xor_a_r8(self, cpu, initial_a, r8_value, expected_a, expected_flags):
        """Tests XOR A, r8 instructions"""
        # Arrange
        cpu.CoreReg.A = initial_a
        cpu.CoreReg.B = r8_value  # Use B as the source register for testing
        cpu.Flags.z = 0  # Initialize Z to opposite of expected
        cpu.Flags.n = 1  # Initialize N to opposite of expected
        cpu.Flags.h = 1  # Initialize H to opposite of expected
        cpu.Flags.c = 1  # Initialize C to opposite of expected

        # Act
        pc_override, cycle_override = cpu._xor_a_b(None) # Assuming _xor_a_b calls the core xor_a_r8 logic

        # Assert
        assert cpu.CoreReg.A == expected_a, f"A register expected {expected_a:02X}, got {cpu.CoreReg.A:02X}"
        assert cpu.Flags.z == int(expected_flags[0]), "Z flag mismatch"
        assert cpu.Flags.n == int(expected_flags[1]), "N flag mismatch"
        assert cpu.Flags.h == int(expected_flags[2]), "H flag mismatch"
        assert cpu.Flags.c == int(expected_flags[3]), "C flag mismatch"

        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None"

    @pytest.mark.parametrize("initial_a, r8_value, expected_a, expected_flags", or_a_r8_test_cases)
    def test_or_a_r8(self, cpu, initial_a, r8_value, expected_a, expected_flags):
        """Tests OR A, r8 instructions"""
        # Arrange
        cpu.CoreReg.A = initial_a
        cpu.CoreReg.B = r8_value  # Use B as the source register for testing
        cpu.Flags.z = 0  # Initialize Z to opposite of expected
        cpu.Flags.n = 1  # Initialize N to opposite of expected
        cpu.Flags.h = 1  # Initialize H to opposite of expected
        cpu.Flags.c = 1  # Initialize C to opposite of expected

        # Act
        pc_override, cycle_override = cpu._or_a_b(None) # Assuming _or_a_b calls the core or_a_r8 logic

        # Assert
        assert cpu.CoreReg.A == expected_a, f"A register expected {expected_a:02X}, got {cpu.CoreReg.A:02X}"
        assert cpu.Flags.z == int(expected_flags[0]), "Z flag mismatch"
        assert cpu.Flags.n == int(expected_flags[1]), "N flag mismatch"
        assert cpu.Flags.h == int(expected_flags[2]), "H flag mismatch"
        assert cpu.Flags.c == int(expected_flags[3]), "C flag mismatch"

        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None"

    @pytest.mark.parametrize("initial_a, value, expected_a, expected_flags", cp_a_test_cases)
    def test_cp_a(self, cpu, initial_a, value, expected_a, expected_flags):
        """Tests CP A, r8/d8/(HL) instructions"""
        # Arrange
        cpu.CoreReg.A = initial_a
        cpu.CoreReg.B = value  # Use B as the representative source for r8
        cpu.Flags.z = 0  # Initialize Z to opposite of expected
        cpu.Flags.n = 0  # Initialize N to opposite of expected
        cpu.Flags.h = 0  # Initialize H to opposite of expected
        cpu.Flags.c = 0  # Initialize C to opposite of expected

        # Act - Test using CP A, B as the representative
        pc_override, cycle_override = cpu._cp_a_b(None)

        # Assert
        assert cpu.CoreReg.A == expected_a, f"A register should not change! Expected {expected_a:02X}, got {cpu.CoreReg.A:02X}"
        assert cpu.Flags.z == int(expected_flags[0]), "Z flag mismatch"
        assert cpu.Flags.n == int(expected_flags[1]), "N flag mismatch"
        assert cpu.Flags.h == int(expected_flags[2]), "H flag mismatch"
        assert cpu.Flags.c == int(expected_flags[3]), "C flag mismatch"

        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None"


    @pytest.mark.parametrize("method_name, initial_pc, target_addr, initial_sp, initial_flags, call_taken, expected_pc_override, expected_sp, expected_stack_val, expected_cycles", call_test_cases)
    def test_call_instructions(self, cpu, method_name, initial_pc, target_addr, initial_sp, initial_flags, call_taken, expected_pc_override, expected_sp, expected_stack_val, expected_cycles):
        """Tests CALL instructions (conditional and unconditional)"""
        # Arrange
        cpu.CoreWords.PC = initial_pc
        cpu.CoreWords.SP = initial_sp

        # Set initial flags
        if initial_flags[0] != '-': cpu.Flags.z = int(initial_flags[0])
        if initial_flags[1] != '-': cpu.Flags.n = int(initial_flags[1])
        if initial_flags[2] != '-': cpu.Flags.h = int(initial_flags[2])
        if initial_flags[3] != '-': cpu.Flags.c = int(initial_flags[3])

        # Write the target address into memory where the instruction expects it (PC+1, PC+2)
        # writeWord handles little-endian storage
        operand_addr_in_mem = initial_pc + 1
        cpu.Memory.writeWord(target_addr, operand_addr_in_mem)

        # Pre-fill stack location to ensure it gets overwritten if call is taken
        if call_taken:
            cpu.Memory.writeWord(0x0000, expected_sp) # expected_sp is SP-2

        instruction_method = getattr(cpu, method_name)

        # Act
        # Pass the address where the target address *starts* in memory (PC+1)
        pc_override, cycle_override = instruction_method(operand_addr_in_mem)

        # Assert
        assert cpu.CoreWords.SP == expected_sp, f"SP expected {expected_sp:04X}, got {cpu.CoreWords.SP:04X}"
        assert pc_override == expected_pc_override, f"PC override expected {expected_pc_override}, got {pc_override}"
        assert cycle_override == expected_cycles, f"Cycles expected {expected_cycles}, got {cycle_override}"

        if call_taken:
            stack_val = cpu.Memory.readWord(expected_sp) # Read the pushed return address
            assert stack_val == expected_stack_val, f"Stack value at {expected_sp:04X} expected {expected_stack_val:04X}, got {stack_val:04X}"
        else:
            # If call not taken, PC should not be overridden by the instruction method itself
            # (it will be incremented by step() later)
            assert pc_override is None


    @pytest.mark.parametrize("reg_pair_name, initial_value, initial_sp, expected_sp, expected_stack_msb, expected_stack_lsb", push_test_cases)
    def test_push_instructions(self, cpu, reg_pair_name, initial_value, initial_sp, expected_sp, expected_stack_msb, expected_stack_lsb):
        """Tests PUSH instructions"""
        # Arrange
        cpu.CoreWords.SP = initial_sp
        setattr(cpu.CoreWords, reg_pair_name, initial_value) # Set initial register value

        # Pre-clear stack locations
        cpu.Memory.writeByte(0x00, initial_sp - 1)
        cpu.Memory.writeByte(0x00, initial_sp - 2)

        method_name = f"_push_{reg_pair_name.lower()}"
        instruction_method = getattr(cpu, method_name)

        # Act
        pc_override, cycle_override = instruction_method(None)

        # Assert
        assert cpu.CoreWords.SP == expected_sp, f"SP expected {expected_sp:04X}, got {cpu.CoreWords.SP:04X}"

        stack_val_msb = cpu.Memory.readByte(expected_sp + 1) # MSB is pushed first to SP-1
        stack_val_lsb = cpu.Memory.readByte(expected_sp)     # LSB is pushed second to SP-2

        assert stack_val_msb == expected_stack_msb, f"Stack MSB at {expected_sp + 1:04X} expected {expected_stack_msb:02X}, got {stack_val_msb:02X}"
        assert stack_val_lsb == expected_stack_lsb, f"Stack LSB at {expected_sp:04X} expected {expected_stack_lsb:02X}, got {stack_val_lsb:02X}"

        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None (uses default 16)" # PUSH is always 16 cycles

    @pytest.mark.parametrize("reg_pair_name, initial_sp, stack_msb, stack_lsb, expected_value, expected_sp, expected_flags_after", pop_test_cases)
    def test_pop_instructions(self, cpu, reg_pair_name, initial_sp, stack_msb, stack_lsb, expected_value, expected_sp, expected_flags_after):
        """Tests POP instructions"""
        # Arrange
        cpu.CoreWords.SP = initial_sp
        # Write values to the stack (LSB at SP, MSB at SP+1)
        cpu.Memory.writeByte(stack_lsb, initial_sp)
        cpu.Memory.writeByte(stack_msb, initial_sp + 1)

        # Store initial flags if we need to check they weren't changed (for non-AF pops)
        initial_flags_val = cpu.Flags.F

        method_name = f"_pop_{reg_pair_name.lower()}"
        instruction_method = getattr(cpu, method_name)

        # Act
        pc_override, cycle_override = instruction_method(None)

        # Assert
        assert cpu.CoreWords.SP == expected_sp, f"SP expected {expected_sp:04X}, got {cpu.CoreWords.SP:04X}"

        if reg_pair_name == "AF":
            # For POP AF, expected_value holds the expected A * 0x100
            # We check A and F separately
            assert cpu.CoreReg.A == (expected_value >> 8), f"Register A expected {(expected_value >> 8):02X}, got {cpu.CoreReg.A:02X}"
            # Check flags based on expected_flags_after string
            assert cpu.Flags.z == int(expected_flags_after[0]), "Z flag mismatch after POP AF"
            assert cpu.Flags.n == int(expected_flags_after[1]), "N flag mismatch after POP AF"
            assert cpu.Flags.h == int(expected_flags_after[2]), "H flag mismatch after POP AF"
            assert cpu.Flags.c == int(expected_flags_after[3]), "C flag mismatch after POP AF"
            # Verify the F register byte itself has lower bits zero
            assert (cpu.Flags.F & 0x0F) == 0, f"Lower nibble of F should be zero after POP AF, got {cpu.Flags.F:02X}"
        else:
            final_value = getattr(cpu.CoreWords, reg_pair_name)
            assert final_value == expected_value, f"Register {reg_pair_name} expected {expected_value:04X}, got {final_value:04X}"
            # Check flags unchanged for non-AF pops
            assert cpu.Flags.F == initial_flags_val, f"Flags changed unexpectedly for POP {reg_pair_name}"

        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None (uses default 12)" # POP is always 12 cycles
