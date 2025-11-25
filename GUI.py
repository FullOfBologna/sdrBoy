import tkinter as tk
from tkinter import ttk

class GUI:
    def __init__(self, cpu, bus):
        self.cpu = cpu
        self.bus = bus
        
        self.root = tk.Tk()
        self.root.title("SDRBoy - Game Boy Emulator")
        self.root.geometry("800x600")
        self.root.configure(bg="#202020")

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
        self.right_frame.pack_propagate(False)

        self.create_debug_pane()

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
        btn = tk.Label(parent, text=text, width=width, height=height, bg=color, fg="white", font=("Arial", 8, "bold"), relief="raised")
        btn.grid(column=col, row=row, padx=5, pady=5)
        return btn

    def create_debug_pane(self):
        # Registers
        tk.Label(self.right_frame, text="Registers", bg="#303030", fg="#00ff00", font=("Courier", 12, "bold")).pack(pady=(10, 5))
        
        self.reg_labels = {}
        regs = ["A", "F", "B", "C", "D", "E", "H", "L", "SP", "PC"]
        
        self.reg_frame = tk.Frame(self.right_frame, bg="#303030")
        self.reg_frame.pack(fill=tk.X, padx=10)

        for i, reg in enumerate(regs):
            frame = tk.Frame(self.reg_frame, bg="#303030")
            frame.pack(fill=tk.X, pady=2)
            tk.Label(frame, text=f"{reg}:", bg="#303030", fg="white", font=("Courier", 10), width=3, anchor="w").pack(side=tk.LEFT)
            val_label = tk.Label(frame, text="00", bg="#303030", fg="#00ff00", font=("Courier", 10))
            val_label.pack(side=tk.RIGHT)
            self.reg_labels[reg] = val_label

        # Memory View
        tk.Label(self.right_frame, text="Memory", bg="#303030", fg="#00ff00", font=("Courier", 12, "bold")).pack(pady=(20, 5))
        
        self.mem_text = tk.Text(self.right_frame, height=15, width=30, bg="black", fg="#00ff00", font=("Courier", 9), state="disabled")
        self.mem_text.pack(padx=10, pady=5)

        # Execution Control
        self.control_frame = tk.Frame(self.right_frame, bg="#303030")
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=10)

        self.btn_pause = tk.Button(self.control_frame, text="Pause", command=self.toggle_pause, bg="#505050", fg="white", width=8)
        self.btn_pause.pack(side=tk.LEFT, padx=5)

        self.btn_step = tk.Button(self.control_frame, text="Step", command=self.step_cpu, bg="#505050", fg="white", width=8, state="disabled")
        self.btn_step.pack(side=tk.RIGHT, padx=5)

        self.paused = False
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

    def update(self):
        # Update Registers
        if self.cpu:
            self.reg_labels["A"].config(text=f"{self.cpu.CoreReg.A:02X}")
            self.reg_labels["F"].config(text=f"{self.cpu.Flags.F:02X}")
            self.reg_labels["B"].config(text=f"{self.cpu.CoreReg.B:02X}")
            self.reg_labels["C"].config(text=f"{self.cpu.CoreReg.C:02X}")
            self.reg_labels["D"].config(text=f"{self.cpu.CoreReg.D:02X}")
            self.reg_labels["E"].config(text=f"{self.cpu.CoreReg.E:02X}")
            self.reg_labels["H"].config(text=f"{self.cpu.CoreReg.H:02X}")
            self.reg_labels["L"].config(text=f"{self.cpu.CoreReg.L:02X}")
            self.reg_labels["SP"].config(text=f"{self.cpu.CoreWords.SP:04X}")
            self.reg_labels["PC"].config(text=f"{self.cpu.CoreWords.PC:04X}")

            # Update Memory View (around PC)
            pc = self.cpu.CoreWords.PC
            start_addr = max(0, pc - 4)
            end_addr = min(0xFFFF, pc + 4)
            
            mem_str = ""
            for addr in range(start_addr, end_addr + 1):
                val = self.bus.readByte(addr)
                prefix = "-> " if addr == pc else "   "
                mem_str += f"{prefix}{addr:04X}: {val:02X}\n"
            
            self.mem_text.config(state="normal")
            self.mem_text.delete(1.0, tk.END)
            self.mem_text.insert(tk.END, mem_str)
            self.mem_text.config(state="disabled")

        self.root.update_idletasks()
        self.root.update()

    def handle_input(self):
        pass

    def animate_button(self, button_name, pressed):
        # Change relief or color based on pressed state
        pass
