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

    inc_r16TestCases = [
        pytest.param("BC", 0x2000, 0x2001, id="Basic INC: BC"),
        pytest.param("DE", 0x2000, 0x2001, id="Basic INC: DE"),
        pytest.param("HL", 0x2000, 0x2001, id="Basic INC: HL"),
        pytest.param("SP", 0x2000, 0x2001, id="Basic INC: SP"),
        pytest.param("BC", 0xFFFF, 0x0000, id="Wrap Around INC: BC"),
        pytest.param("DE", 0xFFFF, 0x0000, id="Wrap Around INC: DE"),
        pytest.param("HL", 0xFFFF, 0x0000, id="Wrap Around INC: HL"),
        pytest.param("SP", 0xFFFF, 0x0000, id="Wrap Around INC: SP"),
    ]

    dec_r16TestCases = [
        pytest.param("BC", 0x2001, 0x2000, id="Basic DEC: BC"),
        pytest.param("DE", 0x2001, 0x2000, id="Basic DEC: DE"),
        pytest.param("HL", 0x2001, 0x2000, id="Basic DEC: HL"),
        pytest.param("SP", 0x2001, 0x2000, id="Basic DEC: SP"),
        pytest.param("BC", 0x0000, 0xFFFF, id="Wrap Around DEC: BC"),
        pytest.param("DE", 0x0000, 0xFFFF, id="Wrap Around DEC: DE"),
        pytest.param("HL", 0x0000, 0xFFFF, id="Wrap Around DEC: HL"),
        pytest.param("SP", 0x0000, 0xFFFF, id="Wrap Around DEC: SP"),
    ]

    inc_r8TestCases = [
        pytest.param("A", 0x2000, 0x2001, id="Basic INC: BC"),
        pytest.param("B", 0x2000, 0x2001, id="Basic INC: DE"),
        pytest.param("C", 0x2000, 0x2001, id="Basic INC: HL"),
        pytest.param("D", 0x2000, 0x2001, id="Basic INC: SP"),
        pytest.param("E", 0xFFFF, 0x0000, id="Wrap Around INC: BC"),
        pytest.param("L", 0xFFFF, 0x0000, id="Wrap Around INC: DE"),
        pytest.param("H", 0xFFFF, 0x0000, id="Wrap Around INC: HL"),
    ]

    # --- 8-BIT TEST CASES ---
    # Format: pytest.param(regName, initVal, expectedVal, expectedFlags(Z,N,H), id)
    # Note: Carry flag (C) is unaffected and should retain its initial value.

    inc_r8TestCases = [
        #                 Reg  Init  Expect Flags(Z,N,H) ID
        pytest.param("A", 0x33, 0x34, (0, 0, 0), id="INC A: Basic"),
        pytest.param("B", 0x00, 0x01, (0, 0, 0), id="INC B: Zero -> One"),
        pytest.param("C", 0xFE, 0xFF, (0, 0, 0), id="INC C: -> Max"),
        pytest.param("D", 0xFF, 0x00, (1, 0, 1), id="INC D: Wrap Around (causes Z, H)"), # FF+1=00, H set
        pytest.param("E", 0x4F, 0x50, (0, 0, 1), id="INC E: Half Carry Set"), # 0F+1=10
        pytest.param("H", 0x5A, 0x5B, (0, 0, 0), id="INC H: No Half Carry"),
        pytest.param("L", 0xAF, 0xB0, (0, 0, 1), id="INC L: Half Carry Set High Nibble"), # 0F+1=10
    ]

    dec_r8TestCases = [
        #                 Reg  Init  Expect Flags(Z,N,H) ID
        pytest.param("A", 0x34, 0x33, (0, 1, 0), id="DEC A: Basic"),
        pytest.param("B", 0x01, 0x00, (1, 1, 0), id="DEC B: One -> Zero (causes Z)"),
        pytest.param("C", 0x00, 0xFF, (0, 1, 1), id="DEC C: Wrap Around (causes H)"), # 00-1=FF, H set (borrow)
        pytest.param("D", 0xFF, 0xFE, (0, 1, 0), id="DEC D: Max -> Max-1"),
        pytest.param("E", 0x50, 0x4F, (0, 1, 1), id="DEC E: Half Carry Set (Borrow)"), # 10-1=0F
        pytest.param("H", 0x5B, 0x5A, (0, 1, 0), id="DEC H: No Half Carry"),
        pytest.param("L", 0xB0, 0xAF, (0, 1, 1), id="DEC L: Half Carry Set High Nibble (Borrow)"), # 10-1=0F
    ]
    # --- END 8-BIT TEST CASES ---

    ld_r8_d8_method_test_cases = [
        # Reg, d8 Value, Method Name, Test ID
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

    ld_r16_d16_method_test_cases = [
        # Reg Pair, d16 Value, Method Name, Test ID
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

    def test_init_PC(self,cpu):
        assert cpu.CoreWords.PC == 0x0100

    # def test_step(self,cpu):
    #     cpu._nop()

    @pytest.mark.parametrize("regName, initVal, expectedVal", inc_r16TestCases)
    def test_inc_r16(self, cpu, regName, initVal, expectedVal):
        setattr(cpu.CoreWords, regName, initVal)
        
        origFlags = cpu.Flags.F
        if(regName == 'SP'):
            print(f"initVal = 0x{initVal:x}")
            print(f"SP = 0x{cpu.CoreWords.SP:x}")

        methodName = f"_inc_{regName.lower()}"
        method = getattr(cpu, methodName)

        _, __ = method(None)

        assert getattr(cpu.CoreWords,regName) == expectedVal, f"{regName} -> FAILED: {getattr(cpu.CoreWords,regName)} != {expectedVal}"
        assert cpu.Flags.F == origFlags, f"FAILED: Flags modified for {regName}"
        assert _ is None, "PC override should be None"
        assert __ is None, "Cycle override should be None"

    @pytest.mark.parametrize("regName, initVal, expectedVal", dec_r16TestCases)
    def test_dec_r16(self, cpu, regName, initVal, expectedVal):
        setattr(cpu.CoreWords, regName, initVal)
        
        origFlags = cpu.Flags.F
        if(regName == 'SP'):
            print(f"initVal = 0x{initVal:x}")
            print(f"SP = 0x{cpu.CoreWords.SP:x}")

        methodName = f"_dec_{regName.lower()}"
        method = getattr(cpu, methodName)

        _, __ = method(None)

        assert getattr(cpu.CoreWords,regName) == expectedVal, f"{regName} -> FAILED: {getattr(cpu.CoreWords,regName)} != {expectedVal}"
        assert cpu.Flags.F == origFlags, f"FAILED: Flags modified for {regName}"
        assert _ is None, "PC override should be None"
        assert __ is None, "Cycle override should be None"


    @pytest.mark.parametrize("regName, initVal, expectedVal, expectedFlags", inc_r8TestCases)
    def test_inc_r8(self, cpu, regName, initVal, expectedVal, expectedFlags):
        setattr(cpu.CoreReg, regName, initVal)

        # Set initial flags (opposite of expected where possible) to test changes. N=1 initially.
        expected_Z, expected_N, expected_H = expectedFlags
        cpu.Flags.z = 0 if expected_Z else 1
        cpu.Flags.n = 1 # INC should clear N
        cpu.Flags.h = 0 if expected_H else 1
        cpu.Flags.c = 0 # Test with C=0 initially
        init_C = cpu.Flags.c # Store initial C to verify it's unchanged

        method = getattr(cpu, f"_inc_{regName.lower()}")
        pc_override, cycle_override = method(None)

        assert getattr(cpu.CoreReg, regName) == expectedVal, f"INC {regName} Value"
        assert cpu.Flags.z == expected_Z, f"INC {regName} Flag Z"
        assert cpu.Flags.n == expected_N, f"INC {regName} Flag N" # N must be 0
        assert cpu.Flags.h == expected_H, f"INC {regName} Flag H"
        assert cpu.Flags.c == init_C, f"INC {regName} Flag C (unaffected)" # C must not change

        assert pc_override is None, "PC override"
        assert cycle_override is None, "Cycle override"

    @pytest.mark.parametrize("regName, initVal, expectedVal, expectedFlags", dec_r8TestCases)
    def test_dec_r8(self, cpu, regName, initVal, expectedVal, expectedFlags):
        setattr(cpu.CoreReg, regName, initVal)

        # Set initial flags (opposite of expected where possible) to test changes. N=0 initially.
        expected_Z, expected_N, expected_H = expectedFlags
        cpu.Flags.z = 0 if expected_Z else 1
        cpu.Flags.n = 0 # DEC should set N
        cpu.Flags.h = 0 if expected_H else 1
        cpu.Flags.c = 1 # Test with C=1 initially
        init_C = cpu.Flags.c # Store initial C to verify it's unchanged

        method = getattr(cpu, f"_dec_{regName.lower()}")
        pc_override, cycle_override = method(None)

        assert getattr(cpu.CoreReg, regName) == expectedVal, f"DEC {regName} Value"
        assert cpu.Flags.z == expected_Z, f"DEC {regName} Flag Z"
        assert cpu.Flags.n == expected_N, f"DEC {regName} Flag N" # N must be 1
        assert cpu.Flags.h == expected_H, f"DEC {regName} Flag H"
        assert cpu.Flags.c == init_C, f"DEC {regName} Flag C (unaffected)" # C must not change

        assert pc_override is None, "PC override"
        assert cycle_override is None, "Cycle override"


    @pytest.mark.parametrize("reg_name, d8_value, method_name", ld_r8_d8_method_test_cases)
    def test_ld_r8_d8_methods(self, cpu, reg_name, d8_value, method_name):
        """Tests 8-bit immediate load methods (_ld_X_d8)"""
        # Arrange
        operand_address = 0xC051 # Example address for d8 (WRAM)
        cpu.Memory.writeByte(d8_value, operand_address)
        print(f"Memory Read: {cpu.Memory.readByte(operand_address)}")
        initial_flags = cpu.Flags.F # Assumes combined flag register byte
        instruction_method = getattr(cpu, method_name)

        # 
        print(f"Method Name: {instruction_method}")
        pc_override, cycle_override = instruction_method(operand_address)

        # Assert
        final_reg_value = getattr(cpu.CoreReg, reg_name)
        assert final_reg_value == d8_value, f"Reg {reg_name} value mismatch"

        final_flags = cpu.Flags.F
        assert final_flags == initial_flags, "Flags changed unexpectedly"

        assert pc_override is None, "PC override should be None"
        assert cycle_override is None, "Cycle override should be None"

  
    @pytest.mark.parametrize("reg_name, d16_value, method_name", ld_r16_d16_method_test_cases)
    def test_ld_r16_d16_methods(self,cpu, reg_name, d16_value, method_name):
        """Tests 16-bit immediate load methods (_ld_XX_d16)"""
        # Arrange
        # Address where the 16-bit immediate value starts (LSB first)
        operand_address = 0xC050 # Example writable address
        lsb = d16_value & 0xFF
        msb = (d16_value >> 8) & 0xFF

        # Write LSB and MSB to memory (Little Endian)
        cpu.Memory.writeByte(lsb, operand_address)
        cpu.Memory.writeByte(msb, operand_address + 1)

        # Verify memory write if needed (optional)
        assert cpu.Memory.readByte(operand_address) == lsb
        assert cpu.Memory.readByte(operand_address + 1) == msb
        # Or verify using readWord
        assert cpu.Memory.readWord(operand_address) == d16_value

        initial_flags = cpu.Flags.F # Assumes combined flag register byte
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
