from Registers import *
from utils import *
from CPU import CPU
from Bus import Bus
from PPU import PPU
from GUI import GUI
import sys
import os

def main():

    print("=============================\nStarting Game Boy\n=============================\n")

    print("Initializing Core registers\n")
    CoreRegisters = RegByte()
    CoreFlags = Flag()
    CoreWords = RegWord(CoreRegisters, CoreFlags)

    print("Initializing Core components\n")
    print("Initializing Memory\n")
    Bus_instance = Bus()
    CPU_instance = CPU()
    PPU_instance = PPU()
    
    # Link PPU to Bus
    Bus_instance.ppu = PPU_instance

    # Load ROM
    base_dir = os.path.dirname(os.path.abspath(__file__))
    rom_path = os.path.join(base_dir, "gb-test-roms/cpu_instrs/individual/06-ld r,r.gb")
    
    if len(sys.argv) > 1:
        rom_path = sys.argv[1]
    
    print(f"Loading ROM: {rom_path}")
    try:
        with open(rom_path, "rb") as f:
            rom_data = f.read()
            Bus_instance.loadROM(rom_data)
    except FileNotFoundError:
        print(f"Error: ROM file not found: {rom_path}")
        return

    print("Initializing GUI\n")
    gui = GUI(CPU_instance, Bus_instance)

    print("Starting Main Loop\n")
    try:
        while gui.running:
            # Handle Execution Control
            if not gui.paused or gui.step_requested:
                # Step CPU
                cycles = CPU_instance.step()
                gui.step_requested = False
            
            # Update GUI
            gui.update()
            
            # Handle GUI events (handled within gui.update/root.update for Tkinter)
            
    except KeyboardInterrupt:
        pass
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"An error occurred: {e}")

    print("======================\nShutting down Game Boy\n======================")

if __name__ == '__main__':
    main()