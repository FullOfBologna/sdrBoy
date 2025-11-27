import tkinter as tk
from tkinter import ttk
from Disassembler import Disassembler
from Registers import Word

class GUI:
    def __init__(self, cpu, bus):
        self.cpu = cpu
        self.bus = bus
        
        self.root = tk.Tk()
        self.root.title("SDRBoy - Game Boy Emulator")
        self.root.geometry("800x600")
        self.root.configure(bg="#202020")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.running = True

        # Main Layout
        self.main_frame = tk.Frame(self.root, bg="#202020")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Side: Screen and Buttons
        self.left_frame = tk.Frame(self.main_frame, bg="#202020")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Game Boy Screen
        self.screen_frame = tk.Frame(self.left_frame, bg="#000000", width=160*3, height=144*3)
        self.screen_frame.pack(pady=20)
        self.screen_frame.pack_propagate(False) # Prevent resizing
        
        self.canvas = tk.Canvas(self.screen_frame, width=160*3, height=144*3, bg="#9bbc0f", highlightthickness=0)
        self.canvas.pack()

        # Buttons Area
        self.buttons_frame = tk.Frame(self.left_frame, bg="#202020")
        self.buttons_frame.pack(pady=20, fill=tk.X)
        
        self.create_buttons()

        # Right Side: Debug Pane
        self.right_frame = tk.Frame(self.main_frame, bg="#303030", width=300)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        # self.right_frame.pack_propagate(False)

        self.create_debug_pane()
        self.create_memory_view()
        
        self.disassembler = Disassembler(cpu, bus)

    def create_buttons(self):
        # D-Pad
        self.dpad_frame = tk.Frame(self.buttons_frame, bg="#202020")
        self.dpad_frame.pack(side=tk.LEFT, padx=30)
        
        self.btn_up = self.create_visual_button(self.dpad_frame, "UP", 1, 0)
        self.btn_left = self.create_visual_button(self.dpad_frame, "LEFT", 0, 1)
        self.btn_right = self.create_visual_button(self.dpad_frame, "RIGHT", 2, 1)
        self.btn_down = self.create_visual_button(self.dpad_frame, "DOWN", 1, 2)

        # A/B Buttons
        self.ab_frame = tk.Frame(self.buttons_frame, bg="#202020")
        self.ab_frame.pack(side=tk.RIGHT, padx=30)

        self.btn_b = self.create_visual_button(self.ab_frame, "B", 0, 1, color="#8b0000")
        self.btn_a = self.create_visual_button(self.ab_frame, "A", 1, 0, color="#8b0000")

        # Start/Select
        self.ss_frame = tk.Frame(self.buttons_frame, bg="#202020")
        self.ss_frame.pack(side=tk.BOTTOM, pady=10)

        self.btn_select = self.create_visual_button(self.ss_frame, "SELECT", 0, 0, width=8, height=1, color="#505050")
        self.btn_start = self.create_visual_button(self.ss_frame, "START", 1, 0, width=8, height=1, color="#505050")

    def create_visual_button(self, parent, text, col, row, width=4, height=2, color="#303030"):
        btn = tk.Button(parent, text=text, width=width, height=height, bg=color, fg="white", font=("Arial", 8, "bold"), relief="raised")
        btn.grid(column=col, row=row, padx=5, pady=5)
        return btn

    def create_debug_pane(self):
        # Registers
        tk.Label(self.right_frame, text="Registers", bg="#303030", fg="#00ff00", font=("Courier", 12, "bold")).pack(pady=(10, 5))
        
        self.reg_labels = {}
        regs = ["AF", "BC", "DE", "HL", "SP", "PC"]
        
        self.reg_frame = tk.Frame(self.right_frame, bg="#303030")
        self.reg_frame.pack(fill=tk.X, padx=10)

        for i, reg in enumerate(regs):
            frame = tk.Frame(self.reg_frame, bg="#303030")
            frame.pack(fill=tk.X, pady=2)
            tk.Label(frame, text=f"{reg}:", bg="#303030", fg="white", font=("Courier", 10), width=4, anchor="w").pack(side=tk.LEFT)
            val_label = tk.Label(frame, text="0000", bg="#303030", fg="#00ff00", font=("Courier", 10))
            val_label.pack(side=tk.RIGHT)
            self.reg_labels[reg] = val_label

        # Flags
        self.flag_frame = tk.Frame(self.right_frame, bg="#303030")
        self.flag_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        self.flag_vars = {}
        flags = ["Z", "N", "H", "C"]
        
        for flag in flags:
            frame = tk.Frame(self.flag_frame, bg="#303030")
            frame.pack(fill=tk.X, pady=1)
            
            var = tk.BooleanVar()
            self.flag_vars[flag] = var
            
            # Custom checkbox style using Label and Button or Checkbutton with custom image/style is hard in pure tkinter without images
            # Using standard Checkbutton but trying to style it to look decent
            chk = tk.Checkbutton(frame, text=flag, variable=var, bg="#303030", fg="white", selectcolor="#f0ad4e", activebackground="#303030", activeforeground="white", font=("Courier", 10, "bold"), state="disabled", disabledforeground="white")
            chk.pack(side=tk.LEFT)

        # Memory View
        tk.Label(self.right_frame, text="Disassembly", bg="#303030", fg="#00ff00", font=("Courier", 12, "bold")).pack(pady=(20, 5))
        
        self.mem_text = tk.Text(self.right_frame, height=15, width=30, bg="black", fg="#00ff00", font=("Courier", 9), state="disabled")
        self.mem_text.pack(padx=10, pady=5)

        # Execution Control
        self.control_frame = tk.Frame(self.right_frame, bg="#303030")
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=10)

        self.btn_pause = tk.Button(self.control_frame, text="Resume", command=self.toggle_pause, bg="#008000", fg="white", width=8)
        self.btn_pause.pack(side=tk.LEFT, padx=5)

        self.btn_step = tk.Button(self.control_frame, text="Step", command=self.step_cpu, bg="#505050", fg="white", width=8, state="normal")
        self.btn_step.pack(side=tk.RIGHT, padx=5)

        self.btn_reset = tk.Button(self.control_frame, text="Reset", command=self.reset_cpu, bg="#8b0000", fg="white", width=8)
        self.btn_reset.pack(side=tk.RIGHT, padx=5)

        self.paused = True
        self.step_requested = False

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.btn_pause.config(text="Resume", bg="#008000")
            self.btn_step.config(state="normal")
        else:
            self.btn_pause.config(text="Pause", bg="#505050")
            self.btn_step.config(state="disabled")

    def step_cpu(self):
        self.step_requested = True

    def reset_cpu(self):
        self.cpu.reset()
        self.bus.reset()
        self.paused = True
        self.btn_pause.config(text="Resume", bg="#008000")
        self.btn_step.config(state="normal")
        self.update()

    def on_closing(self):
        self.running = False
        self.root.destroy()

    def update(self):
        if not self.running:
            return
        # Update Registers
        if self.cpu:
            af = (self.cpu.CoreReg.A.astype(Word) << 8) | self.cpu.Flags.F
            self.reg_labels["AF"].config(text=f"{af:04X}")
            self.reg_labels["BC"].config(text=f"{self.cpu.CoreWords.BC:04X}")
            self.reg_labels["DE"].config(text=f"{self.cpu.CoreWords.DE:04X}")
            self.reg_labels["HL"].config(text=f"{self.cpu.CoreWords.HL:04X}")
            self.reg_labels["SP"].config(text=f"{self.cpu.CoreWords.SP:04X}")
            self.reg_labels["PC"].config(text=f"{self.cpu.CoreWords.PC:04X}")

            # Update Flags
            f = self.cpu.Flags.F
            self.flag_vars["Z"].set(bool(f & 0x80))
            self.flag_vars["N"].set(bool(f & 0x40))
            self.flag_vars["H"].set(bool(f & 0x20))
            self.flag_vars["C"].set(bool(f & 0x10))

            # Update Disassembly View
            pc = int(self.cpu.CoreWords.PC)
            # We want to show some lines before PC if possible, but disassembly is variable length.
            # Simple approach: Show from PC onwards.
            # Better approach: Disassemble a block starting from PC.
            
            lines = self.disassembler.disassemble(pc, 15)
            
            dis_str = ""
            for line in lines:
                dis_str += f"{line}\n"
            
            self.mem_text.config(state="normal")
            self.mem_text.delete(1.0, tk.END)
            self.mem_text.insert(tk.END, dis_str)
            
            # Highlight the first line (current PC)
            self.mem_text.tag_add("current", "1.0", "1.end")
            self.mem_text.tag_config("current", background="#404040", foreground="#ffffff")
            
            self.mem_text.config(state="disabled")

            # Update Memory View
            self.update_memory_view()

        self.root.update_idletasks()
        self.root.update()

    def handle_input(self):
        pass

    def create_memory_view(self):
        tk.Label(self.right_frame, text="Memory Viewer", bg="#303030", fg="#00ff00", font=("Courier", 12, "bold")).pack(pady=(20, 5))
        
        # Address Input Frame
        input_frame = tk.Frame(self.right_frame, bg="#303030")
        input_frame.pack(fill=tk.X, padx=10)
        
        tk.Label(input_frame, text="Addr:", bg="#303030", fg="white", font=("Courier", 10)).pack(side=tk.LEFT)
        self.mem_addr_entry = tk.Entry(input_frame, width=6, bg="#505050", fg="white", font=("Courier", 10))
        self.mem_addr_entry.pack(side=tk.LEFT, padx=5)
        self.mem_addr_entry.insert(0, "C000")
        
        btn_go = tk.Button(input_frame, text="Go", command=self.refresh_memory_view, bg="#505050", fg="white", font=("Arial", 8), width=3)
        btn_go.pack(side=tk.LEFT)

        # Quick Jump Buttons
        jump_frame = tk.Frame(self.right_frame, bg="#303030")
        jump_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(jump_frame, text="WRAM", command=lambda: self.set_mem_addr("C000"), bg="#404040", fg="white", font=("Arial", 7), width=5).pack(side=tk.LEFT, padx=2)
        tk.Button(jump_frame, text="ECHO", command=lambda: self.set_mem_addr("E000"), bg="#404040", fg="white", font=("Arial", 7), width=5).pack(side=tk.LEFT, padx=2)
        tk.Button(jump_frame, text="HRAM", command=lambda: self.set_mem_addr("FF80"), bg="#404040", fg="white", font=("Arial", 7), width=5).pack(side=tk.LEFT, padx=2)

        # Hex Dump View
        self.hex_text = tk.Text(self.right_frame, height=8, width=30, bg="black", fg="#00ff00", font=("Courier", 9), state="disabled")
        self.hex_text.pack(padx=10, pady=5)
        
        self.current_mem_addr = 0xC000

    def set_mem_addr(self, addr_str):
        self.mem_addr_entry.delete(0, tk.END)
        self.mem_addr_entry.insert(0, addr_str)
        self.refresh_memory_view()

    def refresh_memory_view(self):
        try:
            addr_str = self.mem_addr_entry.get()
            self.current_mem_addr = int(addr_str, 16)
        except ValueError:
            pass
        self.update_memory_view()

    def update_memory_view(self):
        if not self.cpu:
            return
            
        start_addr = self.current_mem_addr
        lines = []
        
        # Display 8 lines of 8 bytes
        for i in range(8):
            row_addr = start_addr + (i * 8)
            if row_addr > 0xFFFF:
                break
                
            hex_bytes = []
            ascii_chars = ""
            
            for j in range(8):
                addr = row_addr + j
                if addr > 0xFFFF:
                    break
                
                try:
                    val = self.bus.readByte(addr)
                    hex_bytes.append(f"{val:02X}")
                    
                    # ASCII representation (replace non-printable with .)
                    if 32 <= val <= 126:
                        ascii_chars += chr(val)
                    else:
                        ascii_chars += "."
                except Exception:
                    hex_bytes.append("??")
                    ascii_chars += "."
            
            hex_str = " ".join(hex_bytes)
            lines.append(f"{row_addr:04X}  {hex_str:<23}  {ascii_chars}")
            
        view_str = "\n".join(lines)
        
        self.hex_text.config(state="normal")
        self.hex_text.delete(1.0, tk.END)
        self.hex_text.insert(tk.END, view_str)
        self.hex_text.config(state="disabled")

