import numpy as np

class Disassembler:
    def __init__(self, cpu, bus):
        self.cpu = cpu
        self.bus = bus

    def get_mnemonic(self, func_name, operands_bytes):
        name = func_name.lstrip('_')
        parts = name.split('_')
        
        mnemonic = parts[0].upper()
        operands = parts[1:]
        
        # Handle CB prefix
        if parts[0] == 'cb':
            mnemonic = parts[1].upper()
            operands = parts[2:]
            
        formatted_operands = []
        
        for op in operands:
            if op == 'd16':
                val = (operands_bytes[1].astype(np.uint16) << 8) | operands_bytes[0]
                formatted_operands.append(f"${val:04X}")
            elif op == 'd8':
                val = operands_bytes[0]
                formatted_operands.append(f"${val:02X}")
            elif op == 'a16':
                val = (operands_bytes[1].astype(np.uint16) << 8) | operands_bytes[0]
                formatted_operands.append(f"${val:04X}")
            elif op == 'r8':
                val = int(operands_bytes[0])
                # Signed 8-bit offset
                if val & 0x80:
                    val -= 0x100
                formatted_operands.append(f"{val:+d}") # e.g. -5 or +10
            elif op == 'mhl':
                formatted_operands.append("(HL)")
            elif op == 'mbc':
                formatted_operands.append("(BC)")
            elif op == 'mde':
                formatted_operands.append("(DE)")
            elif op == 'mhlp':
                formatted_operands.append("(HL+)")
            elif op == 'mhlm':
                formatted_operands.append("(HL-)")
            elif op == 'ma8':
                val = operands_bytes[0]
                formatted_operands.append(f"($FF{val:02X})")
            elif op == 'ma16':
                val = (operands_bytes[1].astype(np.uint16) << 8) | operands_bytes[0]
                formatted_operands.append(f"(${val:04X})")
            elif op == 'mc':
                formatted_operands.append("(C)")
            elif op == '00h':
                formatted_operands.append("$00")
            elif op == '08h':
                formatted_operands.append("$08")
            elif op == '10h':
                formatted_operands.append("$10")
            elif op == '18h':
                formatted_operands.append("$18")
            elif op == '20h':
                formatted_operands.append("$20")
            elif op == '28h':
                formatted_operands.append("$28")
            elif op == '30h':
                formatted_operands.append("$30")
            elif op == '38h':
                formatted_operands.append("$38")
            else:
                formatted_operands.append(op.upper())
                
        return f"{mnemonic} {','.join(formatted_operands)}"

    def disassemble(self, start_addr, count):
        lines = []
        addr = start_addr
        
        for _ in range(count):
            if addr > 0xFFFF:
                break
                
            try:
                opcode = self.bus.readByte(addr)
                
                length = 1
                func = None
                
                if opcode == 0xCB:
                    cb_opcode = self.bus.readByte(addr + 1)
                    if cb_opcode in self.cpu.cb_prefix_table:
                        func, length, _, _ = self.cpu.cb_prefix_table[cb_opcode]
                        # CB instructions are 2 bytes long (Prefix CB + Opcode)
                        # The table says length 2, which is correct.
                    else:
                        lines.append(f"{addr:04X}: CB {cb_opcode:02X} ???")
                        addr += 2
                        continue
                elif opcode in self.cpu.lr35902_opCodes:
                    func, length, _, _ = self.cpu.lr35902_opCodes[opcode]
                else:
                    lines.append(f"{addr:04X}: {opcode:02X} ???")
                    addr += 1
                    continue
                
                # Read operands
                operands_bytes = []
                raw_bytes_str = f"{opcode:02X}"
                
                if opcode == 0xCB:
                     raw_bytes_str += f"{self.bus.readByte(addr+1):02X}"
                
                for i in range(1, length):
                    # For CB, the length is 2, so we read 1 more byte (the opcode).
                    # But wait, the operands are AFTER the instruction.
                    # For normal ops: Opcode (1 byte) + Operands (length - 1 bytes)
                    # For CB ops: CB (1 byte) + Opcode (1 byte) -> Total 2 bytes. 
                    # The table says length 2. But CB instructions don't have immediate operands usually?
                    # BIT b, r is 2 bytes. 
                    # So operands_bytes should be empty for CB instructions unless they have immediate data?
                    # Actually, my get_mnemonic logic assumes operands_bytes contains immediate data like d16/d8.
                    # CB instructions don't have d16/d8.
                    
                    if opcode != 0xCB:
                         val = self.bus.readByte(addr + i)
                         operands_bytes.append(val)
                         raw_bytes_str += f"{val:02X}"
                
                mnemonic = self.get_mnemonic(func.__name__, operands_bytes)
                
                lines.append(f"{addr:04X} {raw_bytes_str:<8} {mnemonic}")
                
                addr += length
                
            except Exception as e:
                lines.append(f"{addr:04X}: Error {e}")
                addr += 1
                
        return lines
