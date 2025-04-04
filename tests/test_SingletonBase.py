from SingletonBase import SingletonBase
from Registers import *
from utils import *

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
