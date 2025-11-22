from Registers import *

from utils import *

def main():

    print("=============================\nStarting Game Boy\n=============================\n")

    print("Initializing Core registers\n")
from Registers import *

from utils import *

def main():

    print("=============================\nStarting Game Boy\n=============================\n")

    print("Initializing Core registers\n")
    CoreRegisters = RegByte()
    CoreFlags = Flag()
    CoreWords = RegWord(CoreRegisters, CoreFlags)

    print("Initializing Core components\n")
    print("Initializing Memory\n")
    Bus = Bus()
    CPU = CPU()
    PPU = PPU()

    

    print("======================\nShutting down Game Boy\n======================")

if __name__ == '__main__':
    main()