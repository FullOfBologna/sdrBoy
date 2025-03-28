from CPU import Registers8bit
from CPU import Byte
import unittest



def main():
    # unittest.main()



    pass

class TestCases(unittest.TestCase):
    def test_all_ones(self):
        allOnes = 0xFF

        Core = Registers8bit()
        Core.write(allOnes)

        self.assertEqual(Core.A,1, "A Does not Equal 1")
        self.assertEqual(Core.B,1, "B Does not Equal 1")
        self.assertEqual(Core.C,1, "C Does not Equal 1")
        self.assertEqual(Core.D,1, "D Does not Equal 1")
        self.assertEqual(Core.E,1, "E Does not Equal 1")
        self.assertEqual(Core.H,1, "H Does not Equal 1")
        self.assertEqual(Core.L,1, "L Does not Equal 1")
        self.assertEqual(Core.HL,1, "HL Does not Equal 1")
        self.assertEqual(Core.read(),0xFF,"Core does not equal 0xFF")

    def test_A_write(self):
        Core = Registers8bit()
        Core.write(0)
        Core.A = 1
        self.assertEqual(Core.A,1,"A Does not Equal 1")

    def test_B_write(self):
        Core = Registers8bit()
        Core.write(0x00)
        Core.B = 1
        self.assertEqual(Core.B,1,"B Does not Equal 1")

    def test_C_write(self):
        Core = Registers8bit()
        Core.write(0x00)
        Core.C = 1
        self.assertEqual(Core.C,1,"C Does not Equal 1")

    def test_D_write(self):
        Core = Registers8bit()
        Core.write(0x00)
        Core.D = 1
        self.assertEqual(Core.D,1,"D Does not Equal 1")

    def test_E_write(self):
        Core = Registers8bit()
        Core.write(0x00)
        Core.E = 1
        self.assertEqual(Core.E,1,"E Does not Equal 1")

    def test_L_write(self):
        Core = Registers8bit()
        Core.write(0x00)
        Core.L = 1
        self.assertEqual(Core.L,1,"L Does not Equal 1")

    def test_HL_write(self):
        Core = Registers8bit()
        Core.write(0x00)
        Core.HL = 1
        self.assertEqual(Core.HL,1,"A Does not Equal 1")

    def test_reset(self):
        Core = Registers8bit()
        Core.write(0xFF)
        Core.reset()

        self.assertEqual(Core.read(),0,"Core not reset")

if __name__ == '__main__':
    main()