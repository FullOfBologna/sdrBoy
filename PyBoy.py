from Registers import *
import inspect
import unittest
from utils import *

def main():
    unittest.main()

    pass

class TestCases(unittest.TestCase):

    def test_regByteSingleton(self):

        print_function()
        
        Core = RegByte()
        Core2 = RegByte()

        Core.A = 0x56
        Core2.B = 0x43

        print(f"Check of Core Values: Core1.A: {Core.A}, Core2.A: {Core2.A}, Core.B: {Core.B}, Core2.B: {Core2.B}")
        self.assertEqual(Core is Core2,True, "Error in Singleton. Core1 and 2 are not equivalent")

    def test_flagSingleton(self):
        print_function()

        Flag1 = Flag()
        Flag2 = Flag()
        
        Flag1.c = 1
        Flag2.h = 1

        print(f"Check of Flag Values: Flag1.c: {Flag1.c}, Flag2.c: {Flag2.c}, Flag1.h: {Flag1.h}, Flag2.h: {Flag2.h}")
        self.assertEqual(Flag1 is Flag2,True, "Error in Singleton. Flag1 and Flag2 are not equivalent")

    def test_regByteDestructor(self):

        print_function()

        print("Checking Destructor. Should create a new instance of RegByte\n\n")
        Core = RegByte()
        Core.A = 76



    # def test_all_ones(self):
    #     allOnes = 0xFF

    #     Core = Registers8bit()
    #     Core.write(allOnes)

    #     self.assertEqual(Core.A,1, "A Does not Equal 1")
    #     self.assertEqual(Core.B,1, "B Does not Equal 1")
    #     self.assertEqual(Core.C,1, "C Does not Equal 1")
    #     self.assertEqual(Core.D,1, "D Does not Equal 1")
    #     self.assertEqual(Core.E,1, "E Does not Equal 1")
    #     self.assertEqual(Core.H,1, "H Does not Equal 1")
    #     self.assertEqual(Core.L,1, "L Does not Equal 1")
    #     self.assertEqual(Core.HL,1, "HL Does not Equal 1")
    #     self.assertEqual(Core.read(),0xFF,"Core does not equal 0xFF")

    # def test_A_write(self):
    #     Core = RegByte()
    #     Core.A = 0x45
    #     self.assertEqual(Core.A,0x45,"A Does not Equal 0x45")

    # def test_B_write(self):
    #     Core = Registers8bit()
    #     Core.B = 1
    #     self.assertEqual(Core.B,1,"B Does not Equal 1")

    # def test_C_write(self):
    #     Core = Registers8bit()
    #     Core.C = 1
    #     self.assertEqual(Core.C,1,"C Does not Equal 1")

    # def test_D_write(self):
    #     Core = Registers8bit()
    #     Core.D = 1
    #     self.assertEqual(Core.D,1,"D Does not Equal 1")

    # def test_E_write(self):
    #     Core = Registers8bit()
    #     Core.E = 1
    #     self.assertEqual(Core.E,1,"E Does not Equal 1")

    # def test_L_write(self):
    #     Core = Registers8bit()
    #     Core.L = 1
    #     self.assertEqual(Core.L,1,"L Does not Equal 1")

    # def test_HL_write(self):
    #     Core = Registers8bit()
    #     Core.HL = 1
    #     self.assertEqual(Core.HL,1,"A Does not Equal 1")

    # # def test_reset(self):
    # #     Core = Registers8bit()
    # #     Core.write(0xFF)
    # #     Core.reset()

    # #     self.assertEqual(Core.read(),0,"Core not reset")

if __name__ == '__main__':
    main()