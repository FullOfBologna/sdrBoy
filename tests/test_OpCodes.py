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


    def test_init_PC(self,cpu):
        assert cpu.CoreWords.PC == 0x0100

    # def test_step(self,cpu):
    #     cpu._nop()

    @pytest.mark.parametrize("regName, initVal, expectedVal", inc_r16TestCases)
    def test_inc_r16(self, cpu, regName, initVal, expectedVal):
        setattr(cpu.CoreWords, regName, initVal)
        
        origFlags = cpu.Flags.flag
        if(regName == 'SP'):
            print(f"initVal = 0x{initVal:x}")
            print(f"SP = 0x{cpu.CoreWords.SP:x}")

        methodName = f"_inc_{regName.lower()}"
        method = getattr(cpu, methodName)

        _, __ = method(None)

        assert getattr(cpu.CoreWords,regName) == expectedVal, f"{regName} -> FAILED: {getattr(cpu.CoreWords,regName)} != {expectedVal}"
        assert cpu.Flags.flag == origFlags, f"FAILED: Flags modified for {regName}"
        assert _ is None, "PC override should be None"
        assert __ is None, "Cycle override should be None"

    @pytest.mark.parametrize("regName, initVal, expectedVal", dec_r16TestCases)
    def test_dec_r16(self, cpu, regName, initVal, expectedVal):
        setattr(cpu.CoreWords, regName, initVal)
        
        origFlags = cpu.Flags.flag
        if(regName == 'SP'):
            print(f"initVal = 0x{initVal:x}")
            print(f"SP = 0x{cpu.CoreWords.SP:x}")

        methodName = f"_dec_{regName.lower()}"
        method = getattr(cpu, methodName)

        _, __ = method(None)

        assert getattr(cpu.CoreWords,regName) == expectedVal, f"{regName} -> FAILED: {getattr(cpu.CoreWords,regName)} != {expectedVal}"
        assert cpu.Flags.flag == origFlags, f"FAILED: Flags modified for {regName}"
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