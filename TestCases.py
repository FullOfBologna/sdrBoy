from Registers import *
import inspect
import sys
# import unittest
import pytest
import CPU
import Memory
from utils import *

def main():
    print("Running Test Cases...")
    exit_code = pytest.main(['-v', 'tests/']) # Example: run tests verbosely
    print(f"Pytest finished with exit code: {exit_code}")
    
    # Exit with the pytest status code
    sys.exit(int(exit_code))

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
#       BASE FOUNDATION TEST CASES            
#==========================================

class TestSingletonBehavior:
    def test_regByteSingleton(self):

        print_function()

        Core = RegByte()
        Core2 = RegByte()

        Core.A = 0x56
        Core2.B = 0x43

        print(f"Check of Core Values: Core1.A: {Core.A}, Core2.A: {Core2.A}, Core.B: {Core.B}, Core2.B: {Core2.B}")
        assert (Core is Core2) == True, "FAILED: Error in Singleton. Core1 and 2 are not equivalent"

        Core.reset()
 
    def test_flagSingleton(self):
        print_function()

        Flag1 = Flag()
        Flag2 = Flag()
        
        Flag1.c = 1
        Flag2.h = 1

        assert (Flag1 is Flag2) == True, "FAILED: Error in Singleton. Flag1 and Flag2 are not equivalent"

        Flag1.reset()

 
    def test_regWordSingleton(self):
        print_function()

        CoreReg = RegByte()
        flags = Flag()
        Word1 = RegWord(CoreReg, flags)
        Word2 = RegWord(CoreReg, flags)

        Word1.AF = 0x65
        Word2.BC = 0x57

        assert (Word1 is Word2) == True, f"FAILED: Error in Singleton. Word1 and Word2 are not equivalent"
        
        CoreReg.reset()
        flags.reset()
        Word1.reset()


#==========================================
#        MEMORY BANK TEST CASES            
#==========================================

class TestMemory:
    pass

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

    def test_init_PC(self,cpu):
        assert cpu.CoreWords.PC == 0x0100

    def test_step(self,cpu):
        cpu._nop()

    @pytest.mark.parametrize("regName, initVal, expectedVal", inc_r16TestCases)
    def test_arithmetic_r16(self, cpu, regName, initVal, expectedVal):
        setattr(cpu.CoreWords, regName.toUpper(), initVal)
        
        origFlags = cpu.Flags.flag

        methodName = f"_inc_{regName.lower()}"
        method = getattr(cpu, methodName)

        _, __ = method(None)

        assert getattr(cpu.CoreWords,regName) == expectedVal, f"{regName} -> FAILED: {getattr(cpu.CoreWords,regName)} != {expectedVal}"
        assert cpu.Flags.flag == origFlags, f"FAILED: Flags modified for {regName}"
        assert _ is None, "PC override should be None"
        assert __ is None, "Cycle override should be None"

if __name__ == '__main__':
    main()