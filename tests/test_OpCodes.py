import pytest

from CPU import CPU
from Bus import Bus
import numpy as np

#==========================================
#           PYTEST FIXTURES             
#==========================================

@pytest.fixture(scope="function")
def cpu(bus): # Added bus dependency
    cpu = CPU()
    cpu.Flags.flagReset()
    # cpu.Bus is already the singleton, which 'bus' fixture also uses/resets.
    # We don't strictly need to assign cpu.Bus = bus because it's a singleton,
    # but the dependency ensures 'bus' fixture runs first (init PPU).
    
    yield cpu 

    cpu.reset() # Reset Singleton state for next test

@pytest.fixture(scope="function")
def bus():
    bus = Bus()
    # Ensure PPU is initialized and attached
    from PPU import PPU
    bus.ppu = PPU()
    
    yield bus

    bus.reset()
    if bus.ppu:
        bus.ppu.reset() # Reset PPU singleton too

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
        # reg_name, bus_addr, initial_a, expected_bus_value, id
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
        # bus_addr, initial_sp, expected_lsb, expected_msb, id
        pytest.param(0xC000, 0x1234, 0x34, 0x12, id="LD (a16), SP: Basic"),
        pytest.param(0xD000, 0x0000, 0x00, 0x00, id="LD (a16), SP: Zero"),
        pytest.param(0xE000, 0xFFFF, 0xFF, 0xFF, id="LD (a16), SP: Max"),
        pytest.param(0xC050, 0xABCD, 0xCD, 0xAB, id="LD (a16), SP: Different address"),
    ]
#
    ld_a_mr16_test_cases = [
        # reg_name, bus_addr, initial_bus_value, expected_a, id
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
        # dest_reg, initial_hl, initial_bus_value, expected_dest_value, id
        pytest.param("A", 0xC000, 0x12, 0x12, id="LD A, (HL): Basic"),
        pytest.param("B", 0xC001, 0x34, 0x34, id="LD B, (HL): Basic"),
        pytest.param("C", 0xC002, 0x56, 0x56, id="LD C, (HL): Basic"),
        pytest.param("D", 0xC003, 0x78, 0x78, id="LD D, (HL): Basic"),
        pytest.param("E", 0xC004, 0x9A, 0x9A, id="LD E, (HL): Basic"),
        pytest.param("H", 0xC005, 0xBC, 0xBC, id="LD H, (HL): Basic"),
        pytest.param("L", 0xC006, 0xDE, 0xDE, id="LD L, (HL): Basic"),
    ]

    # Test cases for LD (HL), r8 instructions
    # Format: target_addr, src_reg, initial_src_value (None if derived), expected_bus_value, id
    ld_mhl_r8_test_cases = [
        # For standard registers, we set an initial value and expect it to be written.
        pytest.param(0xC123, "B", 0xAB, 0xAB, id="LD (HL), B: Basic"),
        pytest.param(0xD456, "C", 0xCD, 0xCD, id="LD (HL), C: Basic"),
        pytest.param(0xE789, "D", 0xEF, 0xEF, id="LD (HL), D: Basic"),
        pytest.param(0xF9AB, "E", 0x12, 0x12, id="LD (HL), E: Basic"),
        pytest.param(0xCDEF, "A", 0x34, 0x34, id="LD (HL), A: Basic"),

        # For H and L, the value written is part of the initial HL address itself.
        # We don't need to set a separate initial_src_value.
        pytest.param(0xC123, "H", None, 0xC1, id="LD (HL), H: Basic"),
        pytest.param(0xAB45, "L", None, 0x45, id="LD (HL), L: Basic"),
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
        pytest.param(0x55, 0xA2, 0x55, "0101", id="CP A, r8: Less, Borrow (C=1), No Half Borrow"),
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
        pytest.param("AF", 0xFFFC, 0xAB, 0xCD, 0xAB00, 0xFFFE, "1100", id="POP AF: Basic (F masked)"), # Stack: CD AB -> A=AB, F=C0 (Z=1,N=0,H=1,C=0)
        pytest.param("BC", 0xFFFC, 0x12, 0x34, 0x1234, 0xFFFE, "----", id="POP BC: Basic"),
        pytest.param("DE", 0xFFFC, 0x56, 0x78, 0x5678, 0xFFFE, "----", id="POP DE: Basic"),
        pytest.param("HL", 0xFFFC, 0x9A, 0xBC, 0x9ABC, 0xFFFE, "----", id="POP HL: Basic"),
        pytest.param("BC", 0xC000, 0x00, 0xFF, 0x00FF, 0xC002, "----", id="POP BC: Different SP"),
        pytest.param("AF", 0xC000, 0x01, 0x1F, 0x0100, 0xC002, "0001", id="POP AF: F=10 (C=1)"), # Stack: 1F 01 -> A=01, F=10 (Z=0,N=0,H=0,C=1)
        pytest.param("AF", 0xC000, 0x01, 0x85, 0x0100, 0xC002, "1000", id="POP AF: F=80 (Z=1)"), # Stack: 85 01 -> A=01, F=80 (Z=1,N=0,H=0,C=0)
    ]

    jp_a16_test_cases = [
        # method_name, initial_pc, target_addr, initial_flags, jump_taken, expected_pc_override, expected_cycles, id
        # --- Unconditional JP ---
        pytest.param("_jp_a16", 0xC100, 0x2000, "----", True, 0x2000, 16, id="JP a16: Basic"),
        pytest.param("_jp_a16", 0xC100, 0x0000, "----", True, 0x0000, 16, id="JP a16: To Zero"),
        pytest.param("_jp_a16", 0xC100, 0xFFFF, "----", True, 0xFFFF, 16, id="JP a16: To Max"),

        # --- JP NZ ---
        pytest.param("_jp_nz_a16", 0xC100, 0x2000, "0---", True,  0x2000, 16, id="JP NZ: Condition Met (Z=0)"),
        pytest.param("_jp_nz_a16", 0xC100, 0x2000, "1---", False, None,   12, id="JP NZ: Condition Not Met (Z=1)"),

        # --- JP Z ---
        pytest.param("_jp_z_a16", 0xC100, 0x2000, "1---", True,  0x2000, 16, id="JP Z: Condition Met (Z=1)"),
        pytest.param("_jp_z_a16", 0xC100, 0x2000, "0---", False, None,   12, id="JP Z: Condition Not Met (Z=0)"),

        # --- JP NC ---
        pytest.param("_jp_nc_a16", 0xC100, 0x2000, "---0", True,  0x2000, 16, id="JP NC: Condition Met (C=0)"),
        pytest.param("_jp_nc_a16", 0xC100, 0x2000, "---1", False, None,   12, id="JP NC: Condition Not Met (C=1)"),

        # --- JP C ---
        pytest.param("_jp_c_a16", 0xC100, 0x2000, "---1", True,  0x2000, 16, id="JP C: Condition Met (C=1)"),
        pytest.param("_jp_c_a16", 0xC100, 0x2000, "---0", False, None,   12, id="JP C: Condition Not Met (C=0)"),
    ]

    jp_hl_test_cases = [
        # initial_hl, expected_pc_override, expected_cycles, id
        pytest.param(0x2000, 0x2000, 4, id="JP HL: Basic"),
        pytest.param(0x0000, 0x0000, 4, id="JP HL: To Zero"),
        pytest.param(0xFFFF, 0xFFFF, 4, id="JP HL: To Max"),
        pytest.param(0xC150, 0xC150, 4, id="JP HL: To WRAM"),
    ]

    ret_test_cases = [
        # method_name, initial_sp, stack_ret_addr, initial_flags, ret_taken, expected_pc_override, expected_sp, expected_cycles, id
        # --- Unconditional RET ---
        pytest.param("_ret", 0xFFFC, 0xC200, "----", True, 0xC200, 0xFFFE, 16, id="RET: Basic"),

        # --- RET NZ ---
        pytest.param("_ret_nz", 0xFFFC, 0xC200, "0---", True,  0xC200, 0xFFFE, 20, id="RET NZ: Condition Met (Z=0)"),
        pytest.param("_ret_nz", 0xFFFC, 0xC200, "1---", False, None,   0xFFFC, 8,  id="RET NZ: Condition Not Met (Z=1)"), # SP unchanged

        # --- RET Z ---
        pytest.param("_ret_z", 0xFFFC, 0xC200, "1---", True,  0xC200, 0xFFFE, 20, id="RET Z: Condition Met (Z=1)"),
        pytest.param("_ret_z", 0xFFFC, 0xC200, "0---", False, None,   0xFFFC, 8,  id="RET Z: Condition Not Met (Z=0)"),

        # --- RET NC ---
        pytest.param("_ret_nc", 0xFFFC, 0xC200, "---0", True,  0xC200, 0xFFFE, 20, id="RET NC: Condition Met (C=0)"),
        pytest.param("_ret_nc", 0xFFFC, 0xC200, "---1", False, None,   0xFFFC, 8,  id="RET NC: Condition Not Met (C=1)"),

        # --- RET C ---
        pytest.param("_ret_c", 0xFFFC, 0xC200, "---1", True,  0xC200, 0xFFFE, 20, id="RET C: Condition Met (C=1)"),
        pytest.param("_ret_c", 0xFFFC, 0xC200, "---0", False, None,   0xFFFC, 8,  id="RET C: Condition Not Met (C=0)"),

        # --- RETI --- (Assuming IME enable is not yet implemented)
        pytest.param("_reti", 0xFFFC, 0xC200, "----", True, 0xC200, 0xFFFE, 16, id="RETI: Basic (IME not tested)"),
    ]

    rst_test_cases = [
        # method_name, initial_pc, initial_sp, expected_pc_override, expected_sp, expected_stack_val, expected_cycles, id
        pytest.param("_rst_00h", 0xC100, 0xFFFE, 0x0000, 0xFFFC, 0xC101, 16, id="RST 00H"),
        pytest.param("_rst_08h", 0xC100, 0xFFFE, 0x0008, 0xFFFC, 0xC101, 16, id="RST 08H"),
        pytest.param("_rst_10h", 0xC100, 0xFFFE, 0x0010, 0xFFFC, 0xC101, 16, id="RST 10H"),
        pytest.param("_rst_18h", 0xC100, 0xFFFE, 0x0018, 0xFFFC, 0xC101, 16, id="RST 18H"),
        pytest.param("_rst_20h", 0xC100, 0xFFFE, 0x0020, 0xFFFC, 0xC101, 16, id="RST 20H"),
        pytest.param("_rst_28h", 0xC100, 0xFFFE, 0x0028, 0xFFFC, 0xC101, 16, id="RST 28H"),
        pytest.param("_rst_30h", 0xC100, 0xFFFE, 0x0030, 0xFFFC, 0xC101, 16, id="RST 30H"),
        pytest.param("_rst_38h", 0xC100, 0xFFFE, 0x0038, 0xFFFC, 0xC101, 16, id="RST 38H"),
        pytest.param("_rst_10h", 0x0150, 0xC002, 0x0010, 0xC000, 0x0151, 16, id="RST 10H: Different PC/SP"), # PC=0x0150 (ROM), SP=0xC002 (WRAM)
    ]

    # Test cases for LDH instructions (using 0xFF00 + C or 0xFF00 + a8)
    # Format: method_name, initial_c_or_a8, initial_a, initial_bus_value, expected_a, expected_bus_value, id
    ldh_test_cases = [
        # --- LDH A, (C) ---
        pytest.param("_ldh_a_mc", 0x42, 0x00, 0x55, 0x55, 0x55, id="LDH A, (C): Load 0x55"),
        pytest.param("_ldh_a_mc", 0x00, 0xFF, 0xAA, 0xAA, 0xAA, id="LDH A, (C): C=0x00, Load 0xAA"),

        # --- LDH (C), A ---
        pytest.param("_ldh_mc_a", 0x43, 0x66, 0x00, 0x66, 0x66, id="LDH (C), A: Store 0x66"),
        pytest.param("_ldh_mc_a", 0x01, 0xCC, 0xFF, 0xCC, 0xCC, id="LDH (C), A: C=0x01, Store 0xCC"),

        # --- LDH A, (a8) ---
        pytest.param("_ldh_a_ma8", 0x50, 0x00, 0x77, 0x77, 0x77, id="LDH A, (a8): Load 0x77"),
        pytest.param("_ldh_a_ma8", 0xFF, 0x11, 0x99, 0x99, 0x99, id="LDH A, (a8): a8=0xFF, Load 0x99"),

        # --- LDH (a8), A ---
        pytest.param("_ldh_ma8_a", 0x60, 0xEE, 0x00, 0xEE, 0xEE, id="LDH (a8), A: Store 0xEE"),
        pytest.param("_ldh_ma8_a", 0xFD, 0x2B, 0x11, 0x2B, 0x2B, id="LDH (a8), A: a8=0xFD, Store 0x2B"),
    ]


    #==========================================
    #          CB PREFIX TEST CASES
    #==========================================

    # Test cases for _rlc_r8 helper (Rotate Left Circular)
    # Format: initial_value, expected_result, expected_flags (ZNHC), id
    rlc_r8_test_cases = [
        pytest.param(0x85, 0x0B, "0001", id="RLC 0x85 -> 0x0B, C=1"), # Bit 7=1 becomes new C and bit 0
        pytest.param(0x01, 0x02, "0000", id="RLC 0x01 -> 0x02, C=0"), # Bit 7=0 becomes new C
        pytest.param(0x80, 0x01, "0001", id="RLC 0x80 -> 0x01, C=1"), # Edge case high bit
        pytest.param(0x00, 0x00, "1000", id="RLC 0x00 -> 0x00, Z=1, C=0"), # Zero case
        pytest.param(0xFF, 0xFF, "0001", id="RLC 0xFF -> 0xFF, C=1"), # All ones
        pytest.param(0x4A, 0x94, "0000", id="RLC 0x4A -> 0x94, C=0"), # Mid-range value
    ]


    # Test cases for _rrc_r8 helper (Rotate Right Circular)
    # Format: initial_value, expected_result, expected_flags (ZNHC), id
    rrc_r8_test_cases = [
        pytest.param(0x01, 0x80, "0001", id="RRC 0x01 -> 0x80, C=1"), # Bit 0=1 becomes new C and bit 7
        pytest.param(0x0A, 0x05, "0000", id="RRC 0x0A -> 0x05, C=0"), # Bit 0=0 becomes new C
        pytest.param(0x00, 0x00, "1000", id="RRC 0x00 -> 0x00, Z=1, C=0"), # Zero case
        pytest.param(0xFF, 0xFF, "0001", id="RRC 0xFF -> 0xFF, C=1"), # All ones
        pytest.param(0x95, 0xCA, "0001", id="RRC 0x95 -> 0xCA, C=1"), # Mid-range value
    ]

    # Test cases for _cb_rl_r8 helper (Rotate Left through Carry)
    # Format: initial_value, initial_carry, expected_result, expected_flags (ZNHC), id
    rl_r8_test_cases = [
        pytest.param(0x80, 0, 0x00, "1001", id="RL: Bit 7 to C, C=0 in"), # 1000 0000 -> C=1, 0000 0000
        pytest.param(0x10, 0, 0x20, "0000", id="RL: Basic shift, C=0 in"),
        pytest.param(0x00, 1, 0x01, "0000", id="RL: C=1 into bit 0"),
        pytest.param(0x95, 1, 0x2B, "0001", id="RL: 1001 0101, C=1 -> C=1, 0010 1011"),
        pytest.param(0xFF, 0, 0xFE, "0001", id="RL: 1111 1111, C=0 -> C=1, 1111 1110"),
        pytest.param(0xFF, 1, 0xFF, "0001", id="RL: 1111 1111, C=1 -> C=1, 1111 1111"),
    ]

    # Test cases for _cb_rr_r8 helper (Rotate Right through Carry)
    # Format: initial_value, initial_carry, expected_result, expected_flags (ZNHC), id
    rr_r8_test_cases = [
        pytest.param(0x01, 0, 0x00, "1001", id="RR: Bit 0 to C, C=0 in"), # 0000 0001 -> C=1, 0000 0000
        pytest.param(0x20, 0, 0x10, "0000", id="RR: Basic shift, C=0 in"),
        pytest.param(0x00, 1, 0x80, "0000", id="RR: C=1 into bit 7"),
        pytest.param(0x2B, 1, 0x95, "0001", id="RR: 0010 1011, C=1 -> C=1, 1001 0101"),
        pytest.param(0xFF, 0, 0x7F, "0001", id="RR: 1111 1111, C=0 -> C=1, 0111 1111"),
        pytest.param(0xFF, 1, 0xFF, "0001", id="RR: 1111 1111, C=1 -> C=1, 1111 1111"),
    ]

    # Test cases for _cb_sla_r8 helper (Shift Left Arithmetic)
    # Format: initial_value, expected_result, expected_flags (ZNHC), id
    sla_r8_test_cases = [
        pytest.param(0x80, 0x00, "1001", id="SLA 0x80 -> 0x00, Z=1, C=1"), # Bit 7=1 to C, result 0
        pytest.param(0x01, 0x02, "0000", id="SLA 0x01 -> 0x02, C=0"),
        pytest.param(0x7F, 0xFE, "0000", id="SLA 0x7F -> 0xFE, C=0"), # 0111 1111 -> 1111 1110
        pytest.param(0xFF, 0xFE, "0001", id="SLA 0xFF -> 0xFE, C=1"), # 1111 1111 -> 1111 1110
        pytest.param(0x00, 0x00, "1000", id="SLA 0x00 -> 0x00, Z=1, C=0"),
    ]

    # Test cases for _cb_sra_r8 helper (Shift Right Arithmetic)
    # Format: initial_value, expected_result, expected_flags (ZNHC), id
    sra_r8_test_cases = [
        pytest.param(0x80, 0xC0, "0000", id="SRA 0x80 -> 0xC0, C=0"), # 1000 0000 -> 1100 0000 (bit 7 preserved)
        pytest.param(0x01, 0x00, "1001", id="SRA 0x01 -> 0x00, Z=1, C=1"), # Bit 0=1 to C, result 0
        pytest.param(0x7F, 0x3F, "0001", id="SRA 0x7F -> 0x3F, C=1"), # 0111 1111 -> 0011 1111
        pytest.param(0xFF, 0xFF, "0001", id="SRA 0xFF -> 0xFF, C=1"), # 1111 1111 -> 1111 1111
        pytest.param(0x00, 0x00, "1000", id="SRA 0x00 -> 0x00, Z=1, C=0"),
    ]

    # Test cases for _cb_swap_r8 helper (Swap Nibbles)
    # Format: initial_value, expected_result, expected_flags (ZNHC), id
    swap_r8_test_cases = [
        pytest.param(0xF0, 0x0F, "0000", id="SWAP 0xF0 -> 0x0F"),
        pytest.param(0x0F, 0xF0, "0000", id="SWAP 0x0F -> 0xF0"),
        pytest.param(0xAB, 0xBA, "0000", id="SWAP 0xAB -> 0xBA"),
        pytest.param(0x00, 0x00, "1000", id="SWAP 0x00 -> 0x00, Z=1"),
        pytest.param(0x55, 0x55, "0000", id="SWAP 0x55 -> 0x55"),
    ]

    # Test cases for _cb_srl_r8 helper (Shift Right Logical)
    # Format: initial_value, expected_result, expected_flags (ZNHC), id
    srl_r8_test_cases = [
        pytest.param(0x80, 0x40, "0000", id="SRL 0x80 -> 0x40, C=0"), # 1000 0000 -> 0100 0000 (bit 7 becomes 0)
        pytest.param(0x01, 0x00, "1001", id="SRL 0x01 -> 0x00, Z=1, C=1"), # Bit 0=1 to C, result 0
        pytest.param(0x7F, 0x3F, "0001", id="SRL 0x7F -> 0x3F, C=1"), # 0111 1111 -> 0011 1111
        pytest.param(0xFF, 0x7F, "0001", id="SRL 0xFF -> 0x7F, C=1"), # 1111 1111 -> 0111 1111
        pytest.param(0x00, 0x00, "1000", id="SRL 0x00 -> 0x00, Z=1, C=0"),
    ]

    # Test cases for _cb_bit_b_r8 helper (Test Bit)
    # Format: bit_to_test, initial_value, initial_carry, expected_flags (ZNH-), id
    bit_test_cases = [
        pytest.param(0, 0x01, 0, "001-", id="BIT 0 on 0x01 (bit is 1)"),
        pytest.param(0, 0xFE, 1, "101-", id="BIT 0 on 0xFE (bit is 0)"),
        pytest.param(7, 0x80, 0, "001-", id="BIT 7 on 0x80 (bit is 1)"),
        pytest.param(7, 0x7F, 1, "101-", id="BIT 7 on 0x7F (bit is 0)"),
        pytest.param(4, 0xEF, 0, "101-", id="BIT 4 on 0xEF (bit is 0)"), # 1110 1111
        pytest.param(4, 0x10, 1, "001-", id="BIT 4 on 0x10 (bit is 1)"), # 0001 0000
        pytest.param(2, 0xFF, 0, "001-", id="BIT 2 on 0xFF (bit is 1)"),
        pytest.param(5, 0xDF, 1, "101-", id="BIT 5 on 0xDF (bit is 0)"), # 1101 1111
    ]

    # Test cases for _cb_res_b_r8 helper (Reset Bit)
    # Format: bit_to_reset, initial_value, expected_result, id
    res_test_cases = [
        pytest.param(0, 0x01, 0x00, id="RES 0 on 0x01"),
        pytest.param(7, 0x80, 0x00, id="RES 7 on 0x80"),
        pytest.param(4, 0x1F, 0x0F, id="RES 4 on 0x1F"),
        pytest.param(3, 0x08, 0x00, id="RES 3 on 0x08"),
        pytest.param(7, 0xFF, 0x7F, id="RES 7 on 0xFF"),
        pytest.param(0, 0xFE, 0xFE, id="RES 0 on 0xFE (no change)"),
        pytest.param(2, 0x55, 0x51, id="RES 2 on 0x55"), # 0101 0101 -> 0101 0001
    ]

    # Test cases for _cb_set_b_r8 helper (Set Bit)
    # Format: bit_to_set, initial_value, expected_result, id
    set_test_cases = [
        pytest.param(0, 0x00, 0x01, id="SET 0 on 0x00"),
        pytest.param(7, 0x00, 0x80, id="SET 7 on 0x00"),
        pytest.param(4, 0x0F, 0x1F, id="SET 4 on 0x0F"),
        pytest.param(3, 0xF7, 0xFF, id="SET 3 on 0xF7"),
        pytest.param(7, 0x7F, 0xFF, id="SET 7 on 0x7F"),
        pytest.param(0, 0x01, 0x01, id="SET 0 on 0x01 (no change)"),
        pytest.param(6, 0x81, 0xC1, id="SET 6 on 0x81"), # 1000 0001 -> 1100 0001
    ]

    # Manually expanded Test cases for CB RLC instructions
    cb_rlc_test_cases = []
    _registers = ["B", "C", "D", "E", "H", "L", "A"]
    for _reg in _registers:
        for _param in rlc_r8_test_cases:
            _val, _res, _flags = _param.values
            _tid = _param.id
            cb_rlc_test_cases.append(pytest.param(
                f"_cb_rlc_{_reg.lower()}", _reg, _val, _res, _flags, id=f"RLC {_reg}: {_tid}"
            ))
    for _param in rlc_r8_test_cases:
        _val, _res, _flags = _param.values
        _tid = _param.id
        cb_rlc_test_cases.append(pytest.param(
            "_cb_rlc_mhl", "mhl", _val, _res, _flags, id=f"RLC (HL): {_tid}"
        ))

    # Manually expanded Test cases for CB RRC instructions
    cb_rrc_test_cases = []
    # _registers list defined above
    for _reg in _registers:
        for _param in rrc_r8_test_cases:
            _val, _res, _flags = _param.values
            _tid = _param.id
            cb_rrc_test_cases.append(pytest.param(
                f"_cb_rrc_{_reg.lower()}", _reg, _val, _res, _flags, id=f"RRC {_reg}: {_tid}"
            ))
    for _param in rrc_r8_test_cases:
        _val, _res, _flags = _param.values
        _tid = _param.id
        cb_rrc_test_cases.append(pytest.param(
            "_cb_rrc_mhl", "mhl", _val, _res, _flags, id=f"RRC (HL): {_tid}"
        ))


    # Manually expanded Test cases for CB RL instructions
    cb_rl_test_cases = []
    for _reg in _registers:
        for _param in rl_r8_test_cases:
            _val, _carry, _res, _flags = _param.values
            _tid = _param.id
            cb_rl_test_cases.append(pytest.param(
                f"_cb_rl_{_reg.lower()}", _reg, _val, _carry, _res, _flags, id=f"RL {_reg}: {_tid}"
            ))
    for _param in rl_r8_test_cases:
        _val, _carry, _res, _flags = _param.values
        _tid = _param.id
        cb_rl_test_cases.append(pytest.param(
            "_cb_rl_mhl", "mhl", _val, _carry, _res, _flags, id=f"RL (HL): {_tid}"
        ))

    # Manually expanded Test cases for CB RR instructions
    cb_rr_test_cases = []
    for _reg in _registers:
        for _param in rr_r8_test_cases:
            _val, _carry, _res, _flags = _param.values
            _tid = _param.id
            cb_rr_test_cases.append(pytest.param(
                f"_cb_rr_{_reg.lower()}", _reg, _val, _carry, _res, _flags, id=f"RR {_reg}: {_tid}"
            ))
    for _param in rr_r8_test_cases:
        _val, _carry, _res, _flags = _param.values
        _tid = _param.id
        cb_rr_test_cases.append(pytest.param(
            "_cb_rr_mhl", "mhl", _val, _carry, _res, _flags, id=f"RR (HL): {_tid}"
        ))

    # Manually expanded Test cases for CB SLA instructions
    cb_sla_test_cases = []
    for _reg in _registers:
        for _param in sla_r8_test_cases:
            _val, _res, _flags = _param.values
            _tid = _param.id
            cb_sla_test_cases.append(pytest.param(
                f"_cb_sla_{_reg.lower()}", _reg, _val, _res, _flags, id=f"SLA {_reg}: {_tid}"
            ))
    for _param in sla_r8_test_cases:
        _val, _res, _flags = _param.values
        _tid = _param.id
        cb_sla_test_cases.append(pytest.param(
            "_cb_sla_mhl", "mhl", _val, _res, _flags, id=f"SLA (HL): {_tid}"
        ))

    # Manually expanded Test cases for CB SRA instructions
    cb_sra_test_cases = []
    for _reg in _registers:
        for _param in sra_r8_test_cases:
            _val, _res, _flags = _param.values
            _tid = _param.id
            cb_sra_test_cases.append(pytest.param(
                f"_cb_sra_{_reg.lower()}", _reg, _val, _res, _flags, id=f"SRA {_reg}: {_tid}"
            ))
    for _param in sra_r8_test_cases:
        _val, _res, _flags = _param.values
        _tid = _param.id
        cb_sra_test_cases.append(pytest.param(
            "_cb_sra_mhl", "mhl", _val, _res, _flags, id=f"SRA (HL): {_tid}"
        ))

    # Manually expanded Test cases for CB SWAP instructions
    cb_swap_test_cases = []
    for _reg in _registers:
        for _param in swap_r8_test_cases:
            _val, _res, _flags = _param.values
            _tid = _param.id
            cb_swap_test_cases.append(pytest.param(
                f"_cb_swap_{_reg.lower()}", _reg, _val, _res, _flags, id=f"SWAP {_reg}: {_tid}"
            ))
    for _param in swap_r8_test_cases:
        _val, _res, _flags = _param.values
        _tid = _param.id
        cb_swap_test_cases.append(pytest.param(
            "_cb_swap_mhl", "mhl", _val, _res, _flags, id=f"SWAP (HL): {_tid}"
        ))

    # Manually expanded Test cases for CB SRL instructions
    cb_srl_test_cases = []
    for _reg in _registers:
        for _param in srl_r8_test_cases:
            _val, _res, _flags = _param.values
            _tid = _param.id
            cb_srl_test_cases.append(pytest.param(
                f"_cb_srl_{_reg.lower()}", _reg, _val, _res, _flags, id=f"SRL {_reg}: {_tid}"
            ))
    for _param in srl_r8_test_cases:
        _val, _res, _flags = _param.values
        _tid = _param.id
        cb_srl_test_cases.append(pytest.param(
            "_cb_srl_mhl", "mhl", _val, _res, _flags, id=f"SRL (HL): {_tid}"
        ))

    # Manually expanded Test cases for CB BIT instructions
    cb_bit_test_cases = []
    for _bit in range(8):
        for _reg in _registers + ["mhl"]:
            for _param in bit_test_cases:
                _b, _val, _carry, _flags = _param.values
                _tid = _param.id
                if _b == _bit: # Only add the test case for the correct bit
                    cb_bit_test_cases.append(pytest.param(
                        f"_cb_bit_{_bit}_{_reg.lower()}", _reg, _bit, _val, _carry, _flags, id=f"BIT {_bit}, {_reg}: {_tid}"
                    ))

    # Manually expanded Test cases for CB RES instructions
    cb_res_test_cases = []
    for _bit in range(8):
        for _reg in _registers + ["mhl"]:
            for _param in res_test_cases:
                _b, _val, _res = _param.values
                _tid = _param.id
                if _b == _bit:
                    cb_res_test_cases.append(pytest.param(
                        f"_cb_res_{_bit}_{_reg.lower()}", _reg, _bit, _val, _res, id=f"RES {_bit}, {_reg}: {_tid}"
                    ))

    # Manually expanded Test cases for CB SET instructions
    cb_set_test_cases = []
    for _bit in range(8):
        for _reg in _registers + ["mhl"]:
            for _param in set_test_cases:
                _b, _val, _res = _param.values
                _tid = _param.id
                if _b == _bit:
                    cb_set_test_cases.append(pytest.param(
                        f"_cb_set_{_bit}_{_reg.lower()}", _reg, _bit, _val, _res, id=f"SET {_bit}, {_reg}: {_tid}"
                    ))


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
        cpu.Bus.writeByte(operand_address, d8_value)
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
        cpu.Bus.writeByte(operand_address, lsb)
        cpu.Bus.writeByte(operand_address + 1, msb)
        
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
        cpu.Bus.writeByte(cpu.CoreWords.HL, initial_value)
        cpu.Flags.F = 0x00  # Reset flags for consistent testing
        instruction_method = getattr(cpu, method_name)
        
        # Act
        pc_override, cycle_override = instruction_method(None)
        
        # Assert
        final_value = cpu.Bus.readByte(cpu.CoreWords.HL)
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


    @pytest.mark.parametrize("reg_name, bus_addr, initial_a, expected_bus_value", ld_mr16_a_test_cases)
    def test_ld_mr16_a(self, cpu, reg_name, bus_addr, initial_a, expected_bus_value):
        """Tests load (BC), A / load (DE), A / load (HL), A instructions"""
        # Arrange
        cpu.CoreWords.HL = bus_addr
        initial_hl = cpu.CoreWords.HL
        if reg_name == "HL+":
            cpu.CoreWords.HL = bus_addr
            method_name = "_ld_mhlp_a"
        elif reg_name == "HL-":
            cpu.CoreWords.HL = bus_addr
            method_name = "_ld_mhlm_a"
        else:
            setattr(cpu.CoreWords, reg_name, bus_addr)  # Set r16 to point to memory address
            method_name = f"_ld_m{reg_name.lower()}_a"

        cpu.CoreReg.A = initial_a  # Set initial value of A
        cpu.Bus.writeByte(bus_addr, 0x00)  # Initialize memory location

        instruction_method = getattr(cpu, method_name)

        # Act
        pc_override, cycle_override = instruction_method(None)

        # Assert
        memory_value = cpu.Bus.readByte(bus_addr)
        assert memory_value == expected_bus_value, f"Memory at {bus_addr:04X} expected {expected_bus_value:02X}, got {memory_value:02X}"

        if reg_name == "HL+":
            assert cpu.CoreWords.HL == bus_addr + 1, "HL+ post-increment failed"
        elif reg_name == "HL-":
            assert cpu.CoreWords.HL == bus_addr - 1, "HL- post-decrement failed"
        else:
            assert cpu.CoreWords.HL == initial_hl, "HL should not be modified"

        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None"

    @pytest.mark.parametrize("bus_addr, initial_sp, expected_lsb, expected_msb", ld_m16_sp_test_cases)
    def test_ld_m16_sp(self, cpu, bus_addr, initial_sp, expected_lsb, expected_msb):
        """Tests load (a16), SP instruction"""
        # Arrange
        cpu.CoreWords.SP = initial_sp
        cpu.Bus.writeByte(bus_addr, 0x00)  # Initialize memory location
        cpu.Bus.writeByte(bus_addr + 1, 0x00)  # Initialize memory location + 1

        # Act
        pc_override, cycle_override = cpu._ld_m16_sp(bus_addr)

        # Assert
        memory_lsb = cpu.Bus.readByte(bus_addr)
        memory_msb = cpu.Bus.readByte(bus_addr + 1)
        assert memory_lsb == expected_lsb, f"LSB at {bus_addr:04X} expected {expected_lsb:02X}, got {memory_lsb:02X}"
        assert memory_msb == expected_msb, f"MSB at {bus_addr + 1:04X} expected {expected_msb:02X}, got {memory_msb:02X}"

        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None"

    @pytest.mark.parametrize("reg_name, bus_addr, initial_bus_value, expected_a", ld_a_mr16_test_cases)
    def test_ld_a_mr16(self, cpu, reg_name, bus_addr, initial_bus_value, expected_a):
        """Tests load A, (BC) / load A, (DE) / load A, (HL) instructions"""
        
        # Arrange
        cpu.CoreWords.HL = bus_addr
        initial_hl = cpu.CoreWords.HL
        if reg_name == "HL+":
            cpu.CoreWords.HL = bus_addr
            method_name = "_ld_a_mhlp"
        elif reg_name == "HL-":
            cpu.CoreWords.HL = bus_addr
            method_name = "_ld_a_mhlm"
        else:
            setattr(cpu.CoreWords, reg_name, bus_addr)  # Set r16 to point to memory address
            method_name = f"_ld_a_m{reg_name.lower()}"

        cpu.Bus.writeByte(bus_addr, initial_bus_value)  # Initialize memory location

        instruction_method = getattr(cpu, method_name)

        # Act
        pc_override, cycle_override = instruction_method(None)

        # Assert
        assert cpu.CoreReg.A == expected_a, f"A register expected {expected_a:02X}, got {cpu.CoreReg.A:02X}"

        if reg_name == "HL+":
            assert cpu.CoreWords.HL == bus_addr + 1, "HL+ post-increment failed"
        elif reg_name == "HL-":
            assert cpu.CoreWords.HL == bus_addr - 1, "HL- post-decrement failed"
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

    @pytest.mark.parametrize("dest_reg, initial_hl, initial_bus_value, expected_dest_value", ld_r8_mhl_test_cases)
    def test_ld_r8_mhl(self, cpu, dest_reg, initial_hl, initial_bus_value, expected_dest_value):
        """Tests load register from memory at HL (_ld_X_mhl)"""
        # Arrange
        cpu.CoreWords.HL = initial_hl
        cpu.Bus.writeByte(initial_hl, initial_bus_value)
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

    @pytest.mark.parametrize("target_addr, src_reg, initial_src_value, expected_bus_value", ld_mhl_r8_test_cases)
    def test_ld_mhl_r8(self, cpu, target_addr, src_reg, initial_src_value, expected_bus_value):
        """Tests load memory at HL from register (_ld_mhl_X)"""
        # Arrange
        cpu.CoreWords.HL = target_addr          # Set the target address. This also sets initial H and L.
        cpu.Bus.writeByte(target_addr, 0x00) # Initialize memory location to a known value.

        # If the source register is not H or L, we must set its initial value.
        # If it IS H or L, its value is already correctly set by setting HL, so we do nothing.
        if initial_src_value is not None:
            setattr(cpu.CoreReg, src_reg, initial_src_value)

        initial_flags = cpu.Flags.F
        method_name = f"_ld_mhl_{src_reg.lower()}"
        instruction_method = getattr(cpu, method_name)

        # Act
        pc_override, cycle_override = instruction_method(None)

        # Assert
        memory_value = cpu.Bus.readByte(target_addr)
        assert memory_value == expected_bus_value, f"Memory at {target_addr:04X} expected {expected_bus_value:02X}, got {memory_value:02X}"

        final_flags = cpu.Flags.F
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
        bus_addr = 0xC050 # Default memory address for (HL) and d8

        if source_type == 'r8':
            cpu.CoreReg.B = value # Use B as the representative r8 source
            method_name = f"_{op_type}_a_b"
        elif source_type == 'mhl':
            cpu.CoreWords.HL = bus_addr
            cpu.Bus.writeByte(bus_addr, value)
            method_name = f"_{op_type}_a_mhl"
        elif source_type == 'd8':
            cpu.Bus.writeByte(bus_addr, value) # Simulate fetching d8 from this address
            operand = bus_addr
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
        operand_addr_in_bus = initial_pc + 1
        cpu.Bus.writeWord(operand_addr_in_bus, target_addr)

        # Pre-fill stack location to ensure it gets overwritten if call is taken
        if call_taken:
            cpu.Bus.writeWord(expected_sp, 0x0000) # expected_sp is SP-2

        instruction_method = getattr(cpu, method_name)

        # Act
        # Pass the address where the target address *starts* in memory (PC+1)
        pc_override, cycle_override = instruction_method(operand_addr_in_bus)

        # Assert
        assert cpu.CoreWords.SP == expected_sp, f"SP expected {expected_sp:04X}, got {cpu.CoreWords.SP:04X}"
        assert pc_override == expected_pc_override, f"PC override expected {expected_pc_override}, got {pc_override}"
        assert cycle_override == expected_cycles, f"Cycles expected {expected_cycles}, got {cycle_override}"

        if call_taken:
            stack_val = cpu.Bus.readWord(expected_sp) # Read the pushed return address
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
        cpu.Bus.writeByte(initial_sp - 1, 0x00)
        cpu.Bus.writeByte(initial_sp - 2, 0x00)

        method_name = f"_push_{reg_pair_name.lower()}"
        instruction_method = getattr(cpu, method_name)

        # Act
        pc_override, cycle_override = instruction_method(None)

        # Assert
        assert cpu.CoreWords.SP == expected_sp, f"SP expected {expected_sp:04X}, got {cpu.CoreWords.SP:04X}"

        stack_val_msb = cpu.Bus.readByte(expected_sp + 1) # MSB is pushed first to SP-1
        stack_val_lsb = cpu.Bus.readByte(expected_sp)     # LSB is pushed second to SP-2

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
        cpu.Bus.writeByte(initial_sp, stack_lsb)
        cpu.Bus.writeByte(initial_sp + 1, stack_msb)

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


    @pytest.mark.parametrize("method_name, initial_pc, target_addr, initial_flags, jump_taken, expected_pc_override, expected_cycles", jp_a16_test_cases)
    def test_jp_a16_instructions(self, cpu, method_name, initial_pc, target_addr, initial_flags, jump_taken, expected_pc_override, expected_cycles):
        """Tests JP a16 instructions (conditional and unconditional)"""
        # Arrange
        cpu.CoreWords.PC = initial_pc

        # Set initial flags
        if initial_flags[0] != '-': cpu.Flags.z = int(initial_flags[0])
        if initial_flags[1] != '-': cpu.Flags.n = int(initial_flags[1])
        if initial_flags[2] != '-': cpu.Flags.h = int(initial_flags[2])
        if initial_flags[3] != '-': cpu.Flags.c = int(initial_flags[3])

        # Write the target address into memory where the instruction expects it (PC+1, PC+2)
        operand_addr_in_bus = initial_pc + 1
        cpu.Bus.writeWord(operand_addr_in_bus, target_addr)

        instruction_method = getattr(cpu, method_name)

        # Act
        # Pass the address where the target address *starts* in memory (PC+1)
        pc_override, cycle_override = instruction_method(operand_addr_in_bus)

        # Assert
        assert pc_override == expected_pc_override, f"PC override expected {expected_pc_override}, got {pc_override}"
        assert cycle_override == expected_cycles, f"Cycles expected {expected_cycles}, got {cycle_override}"

    @pytest.mark.parametrize("initial_hl, expected_pc_override, expected_cycles", jp_hl_test_cases)
    def test_jp_hl_instruction(self, cpu, initial_hl, expected_pc_override, expected_cycles):
        """Tests JP HL instruction"""
        # Arrange
        cpu.CoreWords.HL = initial_hl
        cpu.CoreWords.PC = 0xC100 # Set PC to a known state, though it's not directly used by JP HL

        # Act
        pc_override, cycle_override = cpu._jp_hl(None) # operandAddr is not used by JP HL

        # Assert
        assert pc_override == expected_pc_override, f"PC override expected {expected_pc_override:04X}, got {pc_override:04X}"
        assert cycle_override == expected_cycles, f"Cycles expected {expected_cycles}, got {cycle_override}"


    @pytest.mark.parametrize("method_name, initial_sp, stack_ret_addr, initial_flags, ret_taken, expected_pc_override, expected_sp, expected_cycles", ret_test_cases)
    def test_ret_instructions(self, cpu, method_name, initial_sp, stack_ret_addr, initial_flags, ret_taken, expected_pc_override, expected_sp, expected_cycles):
        """Tests RET instructions (conditional, unconditional, RETI)"""
        # Arrange
        cpu.CoreWords.SP = initial_sp
        cpu.CoreWords.PC = 0xC100 # Set PC to a known state, though it's not directly used by RET

        # Set initial flags
        if initial_flags[0] != '-': cpu.Flags.z = int(initial_flags[0])
        if initial_flags[1] != '-': cpu.Flags.n = int(initial_flags[1])
        if initial_flags[2] != '-': cpu.Flags.h = int(initial_flags[2])
        if initial_flags[3] != '-': cpu.Flags.c = int(initial_flags[3])

        # Write the return address to the stack where RET expects it
        # writeWord handles little-endian storage
        cpu.Bus.writeWord(initial_sp, stack_ret_addr)

        instruction_method = getattr(cpu, method_name)

        # Act
        pc_override, cycle_override = instruction_method(None) # operandAddr is not used by RET

        # Assert
        assert cpu.CoreWords.SP == expected_sp, f"SP expected {expected_sp:04X}, got {cpu.CoreWords.SP:04X}"
        assert pc_override == expected_pc_override, f"PC override expected {expected_pc_override}, got {pc_override}"
        assert cycle_override == expected_cycles, f"Cycles expected {expected_cycles}, got {cycle_override}"

        # If RET wasn't taken, ensure the stack wasn't accidentally read/modified
        if not ret_taken:
            stack_val_after = cpu.Bus.readWord(initial_sp)
            assert stack_val_after == stack_ret_addr, f"Stack value at {initial_sp:04X} should be unchanged if RET not taken"

        # TODO: Add check for IME flag being set if/when _reti implements it

    @pytest.mark.parametrize("method_name, initial_pc, initial_sp, expected_pc_override, expected_sp, expected_stack_val, expected_cycles", rst_test_cases)
    def test_rst_instructions(self, cpu, method_name, initial_pc, initial_sp, expected_pc_override, expected_sp, expected_stack_val, expected_cycles):
        """Tests RST instructions"""
        # Arrange
        cpu.CoreWords.PC = initial_pc
        cpu.CoreWords.SP = initial_sp

        # Pre-fill stack location to ensure it gets overwritten
        cpu.Bus.writeWord(expected_sp, 0x0000) # expected_sp is initial_sp - 2

        instruction_method = getattr(cpu, method_name)

        # Act
        pc_override, cycle_override = instruction_method(None) # operandAddr is not used by RST

        # Assert
        assert cpu.CoreWords.SP == expected_sp, f"SP expected {expected_sp:04X}, got {cpu.CoreWords.SP:04X}"
        assert pc_override == expected_pc_override, f"PC override expected {expected_pc_override:04X}, got {pc_override:04X}"
        assert cycle_override == expected_cycles, f"Cycles expected {expected_cycles}, got {cycle_override}"

        # Check the value pushed onto the stack (return address = PC + 1)
        stack_val = cpu.Bus.readWord(expected_sp)
        assert stack_val == expected_stack_val, f"Stack value at {expected_sp:04X} expected {expected_stack_val:04X}, got {stack_val:04X}"

    @pytest.mark.parametrize("method_name, initial_c_or_a8, initial_a, initial_bus_value, expected_a, expected_bus_value", ldh_test_cases)
    def test_ldh_instructions(self, cpu, method_name, initial_c_or_a8, initial_a, initial_bus_value, expected_a, expected_bus_value):
        """Tests LDH instructions: LDH A,(C), LDH (C),A, LDH A,(a8), LDH (a8),A"""
        # Arrange
        cpu.CoreReg.A = initial_a
        target_addr = 0xFF00 + initial_c_or_a8
        cpu.Bus.writeByte(target_addr, initial_bus_value) # Pre-set memory value

        operand = None # Default operand
        is_store_instruction = method_name in ["_ldh_mc_a", "_ldh_ma8_a"]
        is_load_instruction = method_name in ["_ldh_a_mc", "_ldh_a_ma8"]

        if "_mc" in method_name:
            cpu.CoreReg.C = initial_c_or_a8 # Set C register if using (C) addressing
        elif "_ma8" in method_name:
            # For (a8) addressing, the a8 value is the operand
            operand = initial_c_or_a8

        instruction_method = getattr(cpu, method_name)

        # Act
        pc_override, cycle_override = instruction_method(operand) # Pass a8 as operand if needed

        # Assert
        # Check Accumulator value
        if is_load_instruction:
            assert cpu.CoreReg.A == expected_a, f"Accumulator A expected {expected_a:02X}, got {cpu.CoreReg.A:02X}"
        else: # For stores from A, A should remain unchanged
             assert cpu.CoreReg.A == initial_a, f"Accumulator A should be unchanged ({initial_a:02X}), got {cpu.CoreReg.A:02X}"

        # Check Memory value
        final_bus_value = cpu.Bus.readByte(target_addr)
        if is_store_instruction:
            assert final_bus_value == expected_bus_value, f"Memory at {target_addr:04X} expected {expected_bus_value:02X}, got {final_bus_value:02X}"
        else: # For loads into A, memory should remain unchanged
            assert final_bus_value == initial_bus_value, f"Memory at {target_addr:04X} should be unchanged ({initial_bus_value:02X}), got {final_bus_value:02X}"


        # Check C register is unchanged (it's only used for address calculation)
        if "_mc" in method_name:
            assert cpu.CoreReg.C == initial_c_or_a8, f"Register C should be unchanged ({initial_c_or_a8:02X}), got {cpu.CoreReg.C:02X}"

        assert pc_override is None, "PC override should be None"
        # Cycle override might vary (8 for loads, 12 for stores with a8), check specific instruction details if needed
        # assert cycle_override is None, "Cycle override should be None"

    @pytest.mark.parametrize("method_name, register_name, initial_value, expected_result, expected_flags", cb_rlc_test_cases)
    def test_cb_rlc_instructions(self, cpu, method_name, register_name, initial_value, expected_result, expected_flags):
        """Tests the CB-prefixed RLC instructions (RLC r8, RLC (HL))."""
        # Arrange
        instruction_method = getattr(cpu, method_name)
        target_hl_addr = 0xC5A1 # Example address for (HL) tests

        # Set initial value in register or memory
        if register_name == "mhl":
            cpu.CoreWords.HL = target_hl_addr
            cpu.Bus.writeByte(target_hl_addr, initial_value)
        else:
            setattr(cpu.CoreReg, register_name, initial_value)

        # Set initial flags (opposite of expected where possible)
        cpu.Flags.z = 1 if expected_flags[0] == '0' else 0
        cpu.Flags.n = 1 # Expected N is always 0
        cpu.Flags.h = 1 # Expected H is always 0
        cpu.Flags.c = 1 if expected_flags[3] == '0' else 0

        # Act
        pc_override, cycle_override = instruction_method(None) # operandAddr not used by CB rotate

        # Assert
        # Check result in register or memory
        if register_name == "mhl":
            final_value = cpu.Bus.readByte(target_hl_addr)
            assert final_value == expected_result, f"{method_name}: Expected (HL)={expected_result:02X}, got {final_value:02X}"
        else:
            final_value = getattr(cpu.CoreReg, register_name)
            assert final_value == expected_result, f"{method_name}: Expected {register_name}={expected_result:02X}, got {final_value:02X}"

        # Check flags
        assert cpu.Flags.z == int(expected_flags[0]), f"{method_name}: Expected Z={expected_flags[0]}, got {cpu.Flags.z}"
        assert cpu.Flags.n == int(expected_flags[1]), f"{method_name}: Expected N={expected_flags[1]}, got {cpu.Flags.n}"
        assert cpu.Flags.h == int(expected_flags[2]), f"{method_name}: Expected H={expected_flags[2]}, got {cpu.Flags.h}"
        assert cpu.Flags.c == int(expected_flags[3]), f"{method_name}: Expected C={expected_flags[3]}, got {cpu.Flags.c}"

        # Check return values
        assert pc_override is None, f"{method_name}: PC override should be None"
        assert cycle_override is None, f"{method_name}: Cycle override should be None"

    @pytest.mark.parametrize("method_name, register_name, initial_value, expected_result, expected_flags", cb_rrc_test_cases)
    def test_cb_rrc_instructions(self, cpu, method_name, register_name, initial_value, expected_result, expected_flags):
        """Tests the CB-prefixed RRC instructions (RRC r8, RRC (HL))."""
        # Arrange
        instruction_method = getattr(cpu, method_name)
        target_hl_addr = 0xD6B2 # Example address for (HL) tests

        # Set initial value in register or memory
        if register_name == "mhl":
            cpu.CoreWords.HL = target_hl_addr
            cpu.Bus.writeByte(target_hl_addr, initial_value)
        else:
            setattr(cpu.CoreReg, register_name, initial_value)

        # Set initial flags (opposite of expected where possible)
        cpu.Flags.z = 1 if expected_flags[0] == '0' else 0
        cpu.Flags.n = 1 # Expected N is always 0
        cpu.Flags.h = 1 # Expected H is always 0
        cpu.Flags.c = 1 if expected_flags[3] == '0' else 0

        # Act
        pc_override, cycle_override = instruction_method(None) # operandAddr not used by CB rotate

        # Assert
        # Check result in register or memory
        if register_name == "mhl":
            final_value = cpu.Bus.readByte(target_hl_addr)
            assert final_value == expected_result, f"{method_name}: Expected (HL)={expected_result:02X}, got {final_value:02X}"
        else:
            final_value = getattr(cpu.CoreReg, register_name)
            assert final_value == expected_result, f"{method_name}: Expected {register_name}={expected_result:02X}, got {final_value:02X}"

        # Check flags
        assert cpu.Flags.z == int(expected_flags[0]), f"{method_name}: Expected Z={expected_flags[0]}, got {cpu.Flags.z}"
        assert cpu.Flags.n == int(expected_flags[1]), f"{method_name}: Expected N={expected_flags[1]}, got {cpu.Flags.n}"
        assert cpu.Flags.h == int(expected_flags[2]), f"{method_name}: Expected H={expected_flags[2]}, got {cpu.Flags.h}"
        assert cpu.Flags.c == int(expected_flags[3]), f"{method_name}: Expected C={expected_flags[3]}, got {cpu.Flags.c}"

        # Check return values
        assert pc_override is None, f"{method_name}: PC override should be None"
        assert cycle_override is None, f"{method_name}: Cycle override should be None"

    @pytest.mark.parametrize("method_name, register_name, initial_value, initial_carry, expected_result, expected_flags", cb_rl_test_cases)
    def test_cb_rl_instructions(self, cpu, method_name, register_name, initial_value, initial_carry, expected_result, expected_flags):
        """Tests the CB-prefixed RL instructions (RL r8, RL (HL))."""
        # Arrange
        instruction_method = getattr(cpu, method_name)
        target_hl_addr = 0xC7C3 # Example address for (HL) tests

        # Set initial value in register or memory
        if register_name == "mhl":
            cpu.CoreWords.HL = target_hl_addr
            cpu.Bus.writeByte(target_hl_addr, initial_value)
        else:
            setattr(cpu.CoreReg, register_name, initial_value)

        # Set initial flags
        cpu.Flags.z = 1 if expected_flags[0] == '0' else 0
        cpu.Flags.n = 1 # Expected N is always 0
        cpu.Flags.h = 1 # Expected H is always 0
        cpu.Flags.c = initial_carry

        # Act
        pc_override, cycle_override = instruction_method(None)

        # Assert
        # Check result in register or memory
        if register_name == "mhl":
            final_value = cpu.Bus.readByte(target_hl_addr)
            assert final_value == expected_result, f"{method_name}: Expected (HL)={expected_result:02X}, got {final_value:02X}"
        else:
            final_value = getattr(cpu.CoreReg, register_name)
            assert final_value == expected_result, f"{method_name}: Expected {register_name}={expected_result:02X}, got {final_value:02X}"

        # Check flags
        assert cpu.Flags.z == int(expected_flags[0]), f"{method_name}: Expected Z={expected_flags[0]}, got {cpu.Flags.z}"
        assert cpu.Flags.n == int(expected_flags[1]), f"{method_name}: Expected N={expected_flags[1]}, got {cpu.Flags.n}"
        assert cpu.Flags.h == int(expected_flags[2]), f"{method_name}: Expected H={expected_flags[2]}, got {cpu.Flags.h}"
        assert cpu.Flags.c == int(expected_flags[3]), f"{method_name}: Expected C={expected_flags[3]}, got {cpu.Flags.c}"

        # Check return values
        assert pc_override is None, f"{method_name}: PC override should be None"
        assert cycle_override is None, f"{method_name}: Cycle override should be None"


    @pytest.mark.parametrize("method_name, register_name, initial_value, initial_carry, expected_result, expected_flags", cb_rr_test_cases)
    def test_cb_rr_instructions(self, cpu, method_name, register_name, initial_value, initial_carry, expected_result, expected_flags):
        """Tests the CB-prefixed RR instructions (RR r8, RR (HL))."""
        # Arrange
        instruction_method = getattr(cpu, method_name)
        target_hl_addr = 0xD8D4 # Example address for (HL) tests

        # Set initial value in register or memory
        if register_name == "mhl":
            cpu.CoreWords.HL = target_hl_addr
            cpu.Bus.writeByte(target_hl_addr, initial_value)
        else:
            setattr(cpu.CoreReg, register_name, initial_value)

        # Set initial flags
        cpu.Flags.z = 1 if expected_flags[0] == '0' else 0
        cpu.Flags.n = 1 # Expected N is always 0
        cpu.Flags.h = 1 # Expected H is always 0
        cpu.Flags.c = initial_carry

        # Act
        pc_override, cycle_override = instruction_method(None)

        # Assert
        # Check result in register or memory
        if register_name == "mhl":
            final_value = cpu.Bus.readByte(target_hl_addr)
            assert final_value == expected_result, f"{method_name}: Expected (HL)={expected_result:02X}, got {final_value:02X}"
        else:
            final_value = getattr(cpu.CoreReg, register_name)
            assert final_value == expected_result, f"{method_name}: Expected {register_name}={expected_result:02X}, got {final_value:02X}"

        # Check flags
        assert cpu.Flags.z == int(expected_flags[0]), f"{method_name}: Expected Z={expected_flags[0]}, got {cpu.Flags.z}"
        assert cpu.Flags.n == int(expected_flags[1]), f"{method_name}: Expected N={expected_flags[1]}, got {cpu.Flags.n}"
        assert cpu.Flags.h == int(expected_flags[2]), f"{method_name}: Expected H={expected_flags[2]}, got {cpu.Flags.h}"
        assert cpu.Flags.c == int(expected_flags[3]), f"{method_name}: Expected C={expected_flags[3]}, got {cpu.Flags.c}"

        # Check return values
        assert pc_override is None, f"{method_name}: PC override should be None"
        assert cycle_override is None, f"{method_name}: Cycle override should be None"

    @pytest.mark.parametrize("method_name, register_name, initial_value, expected_result, expected_flags", cb_sla_test_cases)
    def test_cb_sla_instructions(self, cpu, method_name, register_name, initial_value, expected_result, expected_flags):
        """Tests the CB-prefixed SLA instructions (SLA r8, SLA (HL))."""
        # Arrange
        instruction_method = getattr(cpu, method_name)
        target_hl_addr = 0xE1E2 # Example address for (HL) tests

        # Set initial value in register or memory
        if register_name == "mhl":
            cpu.CoreWords.HL = target_hl_addr
            cpu.Bus.writeByte(target_hl_addr, initial_value)
        else:
            setattr(cpu.CoreReg, register_name, initial_value)

        # Set initial flags (N and H are always 0 for SLA)
        cpu.Flags.z = 1 if expected_flags[0] == '0' else 0 # Set to inverse for testing
        cpu.Flags.n = 1 # Expected N is always 0
        cpu.Flags.h = 1 # Expected H is always 0
        cpu.Flags.c = 1 if expected_flags[3] == '0' else 0 # Set to inverse for testing

        # Act
        pc_override, cycle_override = instruction_method(None)

        # Assert
        # Check result in register or memory
        if register_name == "mhl":
            final_value = cpu.Bus.readByte(target_hl_addr)
            assert final_value == expected_result, f"{method_name}: Expected (HL)={expected_result:02X}, got {final_value:02X}"
        else:
            final_value = getattr(cpu.CoreReg, register_name)
            assert final_value == expected_result, f"{method_name}: Expected {register_name}={expected_result:02X}, got {final_value:02X}"

        # Check flags
        assert cpu.Flags.z == int(expected_flags[0]), f"{method_name}: Expected Z={expected_flags[0]}, got {cpu.Flags.z}"
        assert cpu.Flags.n == int(expected_flags[1]), f"{method_name}: Expected N={expected_flags[1]}, got {cpu.Flags.n}"
        assert cpu.Flags.h == int(expected_flags[2]), f"{method_name}: Expected H={expected_flags[2]}, got {cpu.Flags.h}"
        assert cpu.Flags.c == int(expected_flags[3]), f"{method_name}: Expected C={expected_flags[3]}, got {cpu.Flags.c}"

        # Check return values
        assert pc_override is None, f"{method_name}: PC override should be None"
        assert cycle_override is None, f"{method_name}: Cycle override should be None"

    @pytest.mark.parametrize("method_name, register_name, initial_value, expected_result, expected_flags", cb_sra_test_cases)
    def test_cb_sra_instructions(self, cpu, method_name, register_name, initial_value, expected_result, expected_flags):
        """Tests the CB-prefixed SRA instructions (SRA r8, SRA (HL))."""
        # Arrange
        instruction_method = getattr(cpu, method_name)
        target_hl_addr = 0xF3F4 # Example address for (HL) tests

        # Set initial value in register or memory
        if register_name == "mhl":
            cpu.CoreWords.HL = target_hl_addr
            cpu.Bus.writeByte(target_hl_addr, initial_value)
        else:
            setattr(cpu.CoreReg, register_name, initial_value)

        # Set initial flags (N and H are always 0 for SRA)
        cpu.Flags.z = 1 if expected_flags[0] == '0' else 0 # Set to inverse for testing
        cpu.Flags.n = 1 # Expected N is always 0
        cpu.Flags.h = 1 # Expected H is always 0
        cpu.Flags.c = 1 if expected_flags[3] == '0' else 0 # Set to inverse for testing

        # Act
        pc_override, cycle_override = instruction_method(None)

        # Assert
        # Check result in register or memory
        if register_name == "mhl":
            final_value = cpu.Bus.readByte(target_hl_addr)
            assert final_value == expected_result, f"{method_name}: Expected (HL)={expected_result:02X}, got {final_value:02X}"
        else:
            final_value = getattr(cpu.CoreReg, register_name)
            assert final_value == expected_result, f"{method_name}: Expected {register_name}={expected_result:02X}, got {final_value:02X}"

        # Check flags
        assert cpu.Flags.z == int(expected_flags[0]), f"{method_name}: Expected Z={expected_flags[0]}, got {cpu.Flags.z}"
        assert cpu.Flags.n == int(expected_flags[1]), f"{method_name}: Expected N={expected_flags[1]}, got {cpu.Flags.n}"
        assert cpu.Flags.h == int(expected_flags[2]), f"{method_name}: Expected H={expected_flags[2]}, got {cpu.Flags.h}"
        assert cpu.Flags.c == int(expected_flags[3]), f"{method_name}: Expected C={expected_flags[3]}, got {cpu.Flags.c}"

        # Check return values
        assert pc_override is None, f"{method_name}: PC override should be None"
        assert cycle_override is None, f"{method_name}: Cycle override should be None"

    @pytest.mark.parametrize("method_name, register_name, initial_value, expected_result, expected_flags", cb_swap_test_cases)
    def test_cb_swap_instructions(self, cpu, method_name, register_name, initial_value, expected_result, expected_flags):
        """Tests the CB-prefixed SWAP instructions (SWAP r8, SWAP (HL))."""
        # Arrange
        instruction_method = getattr(cpu, method_name)
        target_hl_addr = 0xA5A6 # Example address for (HL) tests

        # Set initial value in register or memory
        if register_name == "mhl":
            cpu.CoreWords.HL = target_hl_addr
            cpu.Bus.writeByte(target_hl_addr, initial_value)
        else:
            setattr(cpu.CoreReg, register_name, initial_value)

        # Set initial flags (N, H, C are always 0 for SWAP)
        cpu.Flags.z = 1 if expected_flags[0] == '0' else 0 # Set to inverse for testing
        cpu.Flags.n = 1 # Expected N is always 0
        cpu.Flags.h = 1 # Expected H is always 0
        cpu.Flags.c = 1 # Expected C is always 0

        # Act
        pc_override, cycle_override = instruction_method(None)

        # Assert
        # Check result in register or memory
        if register_name == "mhl":
            final_value = cpu.Bus.readByte(target_hl_addr)
            assert final_value == expected_result, f"{method_name}: Expected (HL)={expected_result:02X}, got {final_value:02X}"
        else:
            final_value = getattr(cpu.CoreReg, register_name)
            assert final_value == expected_result, f"{method_name}: Expected {register_name}={expected_result:02X}, got {final_value:02X}"

        # Check flags
        assert cpu.Flags.z == int(expected_flags[0]), f"{method_name}: Expected Z={expected_flags[0]}, got {cpu.Flags.z}"
        assert cpu.Flags.n == int(expected_flags[1]), f"{method_name}: Expected N={expected_flags[1]}, got {cpu.Flags.n}"
        assert cpu.Flags.h == int(expected_flags[2]), f"{method_name}: Expected H={expected_flags[2]}, got {cpu.Flags.h}"
        assert cpu.Flags.c == int(expected_flags[3]), f"{method_name}: Expected C={expected_flags[3]}, got {cpu.Flags.c}"

        # Check return values
        assert pc_override is None, f"{method_name}: PC override should be None"
        assert cycle_override is None, f"{method_name}: Cycle override should be None"

    @pytest.mark.parametrize("method_name, register_name, initial_value, expected_result, expected_flags", cb_srl_test_cases)
    def test_cb_srl_instructions(self, cpu, method_name, register_name, initial_value, expected_result, expected_flags):
        """Tests the CB-prefixed SRL instructions (SRL r8, SRL (HL))."""
        # Arrange
        instruction_method = getattr(cpu, method_name)
        target_hl_addr = 0xB7B8 # Example address for (HL) tests

        # Set initial value in register or memory
        if register_name == "mhl":
            cpu.CoreWords.HL = target_hl_addr
            cpu.Bus.writeByte(target_hl_addr, initial_value)
        else:
            setattr(cpu.CoreReg, register_name, initial_value)

        # Set initial flags (N and H are always 0 for SRL)
        cpu.Flags.z = 1 if expected_flags[0] == '0' else 0 # Set to inverse for testing
        cpu.Flags.n = 1 # Expected N is always 0
        cpu.Flags.h = 1 # Expected H is always 0
        cpu.Flags.c = 1 if expected_flags[3] == '0' else 0 # Set to inverse for testing

        # Act
        pc_override, cycle_override = instruction_method(None)

        # Assert
        # Check result in register or memory
        if register_name == "mhl":
            final_value = cpu.Bus.readByte(target_hl_addr)
            assert final_value == expected_result, f"{method_name}: Expected (HL)={expected_result:02X}, got {final_value:02X}"
        else:
            final_value = getattr(cpu.CoreReg, register_name)
            assert final_value == expected_result, f"{method_name}: Expected {register_name}={expected_result:02X}, got {final_value:02X}"

        # Check flags
        assert cpu.Flags.z == int(expected_flags[0]), f"{method_name}: Expected Z={expected_flags[0]}, got {cpu.Flags.z}"
        assert cpu.Flags.n == int(expected_flags[1]), f"{method_name}: Expected N={expected_flags[1]}, got {cpu.Flags.n}"
        assert cpu.Flags.h == int(expected_flags[2]), f"{method_name}: Expected H={expected_flags[2]}, got {cpu.Flags.h}"
        assert cpu.Flags.c == int(expected_flags[3]), f"{method_name}: Expected C={expected_flags[3]}, got {cpu.Flags.c}"

        # Check return values
        assert pc_override is None, f"{method_name}: PC override should be None"
        assert cycle_override is None, f"{method_name}: Cycle override should be None"


    @pytest.mark.parametrize("method_name, register_name, bit_to_test, initial_value, initial_carry, expected_flags", cb_bit_test_cases)
    def test_cb_bit_instructions(self, cpu, method_name, register_name, bit_to_test, initial_value, initial_carry, expected_flags):
        """Tests the CB-prefixed BIT instructions (BIT b, r8 / (HL))."""
        # Arrange
        instruction_method = getattr(cpu, method_name)
        target_hl_addr = 0xC1C2 # Example address for (HL) tests

        # Set initial value in register or memory
        if register_name == "mhl":
            cpu.CoreWords.HL = target_hl_addr
            cpu.Bus.writeByte(target_hl_addr, initial_value)
        else:
            setattr(cpu.CoreReg, register_name, initial_value)

        # Set initial flags
        cpu.Flags.z = 1 if expected_flags[0] == '0' else 0 # Set to inverse for testing
        cpu.Flags.n = 1 # Expected N is always 0
        cpu.Flags.h = 0 # Expected H is always 1
        cpu.Flags.c = initial_carry # C should be preserved

        # Act
        pc_override, cycle_override = instruction_method(cpu, None)

        # Assert
        # Check that the register/memory value has NOT changed
        if register_name == "mhl":
            final_value = cpu.Bus.readByte(target_hl_addr)
            assert final_value == initial_value, f"{method_name}: (HL) value should not change"
        else:
            final_value = getattr(cpu.CoreReg, register_name)
            assert final_value == initial_value, f"{method_name}: Register {register_name} should not change"

        # Check flags (Z, N, H are set, C is preserved)
        assert cpu.Flags.z == int(expected_flags[0]), f"{method_name}: Expected Z={expected_flags[0]}, got {cpu.Flags.z}"
        assert cpu.Flags.n == int(expected_flags[1]), f"{method_name}: Expected N={expected_flags[1]}, got {cpu.Flags.n}"
        assert cpu.Flags.h == int(expected_flags[2]), f"{method_name}: Expected H={expected_flags[2]}, got {cpu.Flags.h}"
        assert cpu.Flags.c == initial_carry, f"{method_name}: Carry flag should be preserved"

        # Check return values
        assert pc_override is None, f"{method_name}: PC override should be None"
        assert cycle_override is None, f"{method_name}: Cycle override should be None"

    @pytest.mark.parametrize("method_name, register_name, bit_to_reset, initial_value, expected_result", cb_res_test_cases)
    def test_cb_res_instructions(self, cpu, method_name, register_name, bit_to_reset, initial_value, expected_result):
        """Tests the CB-prefixed RES instructions (RES b, r8 / (HL))."""
        # Arrange
        instruction_method = getattr(cpu, method_name)
        target_hl_addr = 0xC3C4 # Example address for (HL) tests

        # Set initial value in register or memory
        if register_name == "mhl":
            cpu.CoreWords.HL = target_hl_addr
            cpu.Bus.writeByte(target_hl_addr, initial_value)
        else:
            setattr(cpu.CoreReg, register_name, initial_value)

        # Store initial flags to ensure they are not changed
        initial_flags_f = cpu.Flags.F

        # Act
        pc_override, cycle_override = instruction_method(cpu, None)

        # Assert
        # Check result in register or memory
        if register_name == "mhl":
            final_value = cpu.Bus.readByte(target_hl_addr)
            assert final_value == expected_result, f"{method_name}: Expected (HL)={expected_result:02X}, got {final_value:02X}"
        else:
            final_value = getattr(cpu.CoreReg, register_name)
            assert final_value == expected_result, f"{method_name}: Expected {register_name}={expected_result:02X}, got {final_value:02X}"

        # Check that flags are NOT affected
        assert cpu.Flags.F == initial_flags_f, f"{method_name}: Flags should not be affected"

        # Check return values
        assert pc_override is None, f"{method_name}: PC override should be None"
        assert cycle_override is None, f"{method_name}: Cycle override should be None"

    @pytest.mark.parametrize("method_name, register_name, bit_to_set, initial_value, expected_result", cb_set_test_cases)
    def test_cb_set_instructions(self, cpu, method_name, register_name, bit_to_set, initial_value, expected_result):
        """Tests the CB-prefixed SET instructions (SET b, r8 / (HL))."""
        # Arrange
        instruction_method = getattr(cpu, method_name)
        target_hl_addr = 0xC5C6 # Example address for (HL) tests

        # Set initial value in register or memory
        if register_name == "mhl":
            cpu.CoreWords.HL = target_hl_addr
            cpu.Bus.writeByte(target_hl_addr, initial_value)
        else:
            setattr(cpu.CoreReg, register_name, initial_value)

        # Store initial flags to ensure they are not changed
        initial_flags_f = cpu.Flags.F

        # Act
        pc_override, cycle_override = instruction_method(cpu, None)

        # Assert
        # Check result in register or memory
        if register_name == "mhl":
            final_value = cpu.Bus.readByte(target_hl_addr)
            assert final_value == expected_result, f"{method_name}: Expected (HL)={expected_result:02X}, got {final_value:02X}"
        else:
            final_value = getattr(cpu.CoreReg, register_name)
            assert final_value == expected_result, f"{method_name}: Expected {register_name}={expected_result:02X}, got {final_value:02X}"

        # Check that flags are NOT affected
        assert cpu.Flags.F == initial_flags_f, f"{method_name}: Flags should not be affected"

        # Check return values
        assert pc_override is None, f"{method_name}: PC override should be None"
        assert cycle_override is None, f"{method_name}: Cycle override should be None"