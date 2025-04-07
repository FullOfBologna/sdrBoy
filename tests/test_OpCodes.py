import pytest

from CPU import CPU
from Memory import Memory

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
        elif "_hl" in method_name:
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


    # @pytest.mark.parametrize("method_name, initial_value, expected_value, expected_flags", memory_operation_test_cases)
    # def test_ld_memory_operations((self, cpu))