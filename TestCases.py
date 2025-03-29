from Registers import *
import inspect
import unittest
from utils import *

def main():
    unittest.main()

class TestCases(unittest.TestCase):

    def test_regByteSingleton(self):

        print_function()

        Core = RegByte()
        Core2 = RegByte()

        Core.A = 0x56
        Core2.B = 0x43

        print(f"Check of Core Values: Core1.A: {Core.A}, Core2.A: {Core2.A}, Core.B: {Core.B}, Core2.B: {Core2.B}")
        self.assertEqual(Core is Core2,True, "FAILED: Error in Singleton. Core1 and 2 are not equivalent")

        Core.reset()

        print(f"===================================================\nPASSED\n===================================================")


    def test_flagSingleton(self):
        print_function()

        Flag1 = Flag()
        Flag2 = Flag()
        
        Flag1.c = 1
        Flag2.h = 1

        print(f"Check of Flag Values: Flag1.c: {Flag1.c}, Flag2.c: {Flag2.c}, Flag1.h: {Flag1.h}, Flag2.h: {Flag2.h}")
        self.assertEqual(Flag1 is Flag2,True, "FAILED: Error in Singleton. Flag1 and Flag2 are not equivalent")

        Flag1.reset()

        print(f"===================================================\nPASSED\n===================================================")

    def test_regWordSingleton(self):
        print_function()

        CoreReg = RegByte()
        flags = Flag()
        Word1 = RegWord(CoreReg, flags)
        Word2 = RegWord(CoreReg, flags)

        Word1.AF = 0x65
        Word2.BC = 0x57

        self.assertEqual(Word1 is Word2, True, f"FAILED: Error in Singleton. Word1 and Word2 are not equivalent")
        
        CoreReg.reset()
        flags.reset()
        Word1.reset()

        print(f"===================================================\nPASSED\n===================================================")

if __name__ == '__main__':
    main()