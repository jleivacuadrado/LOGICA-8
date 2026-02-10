
from memory import Memory
from bus import Bus

class CPU:
    def __init__(self):
        self.memory = Memory()
        self.bus = Bus()
        self.bus.attach_memory(self.memory)
        
        self.A = 0x00
        self.X = 0x00
        self.PC = 0
        self.carry = False
        self.zero = False
        self.running = True
        self.log = []
       
        # TABLA DE DESPACHO (Mapping de Opcodes a Métodos)
        self.instructions = {
            0x01: self._lda,
            0x02: self._add,
            0x03: self._sta,
            0x04: self._jmp,
            0x05: self._sub,
            0x06: self._beq,
            0x07: self._and,  
            0x08: self._or,
            0X09: self._xor,
            0x0A: self._not,
            0x0B: self._ldx,
            0x0C: self._inx,
            0x0D: self._dex,
            0xFF: self._halt
        }

    # --- MÉTODOS DE SOPORTE ---

    def load_program(self, program, offset=0):
        self.ram = bytearray(256)
        self.A = 0x00
        self.PC = offset
        self.carry = False
        self.zero = False
        self.log = []
        self.running = True
        for i, byte in enumerate(program):
            if offset + i < 256: self.ram[offset + i] = byte

    def add_log(self, message):
        self.log.append(message)
        if len(self.log) > 15: self.log.pop(0)

    # --- IMPLEMENTACIÓN MODULAR DE INSTRUCCIONES ---

    # 0x01
    def _lda(self):
        val = self.ram[self.PC + 1]
        self.add_log(f"FETCH: 01 {val:02X} -> LDA #{val:03d}")
        self.A = val
        self.zero = (self.A == 0)
        self.PC += 2

    # 0x02
    def _add(self):
        val = self.ram[self.PC + 1]
        old_a = self.A
        res = self.A + val
        self.add_log(f"FETCH: 02 {val:02X} -> ADD #{val:03d}")
        self.A = res % 256
        self.carry = res > 255
        self.zero = (self.A == 0)
        msg = f"  MATH: {old_a:02X}+{val:02X}={self.A:02X} ({old_a:03d}+{val:03d}={res:03d})"
        if self.carry: msg += " !CARRY"
        self.add_log(msg)
        self.PC += 2

    # 0x03
    def _sta(self):
        addr = self.ram[self.PC + 1]
        self.add_log(f"FETCH: 03 {addr:02X} -> STA ${addr:02X}")
        self.ram[addr] = self.A
        self.add_log(f"MEM: {self.A:02X} guardado en ${addr:02X}")
        self.PC += 2

    # 0x04
    def _jmp(self):
        addr = self.ram[self.PC + 1]
        self.add_log(f"FETCH: 04 {addr:02X} -> JMP ${addr:02X}")
        self.PC = addr

    # 0x05
    def _sub(self):
        val = self.ram[self.PC + 1]
        old_a = self.A
        res = self.A - val
        self.add_log(f"FETCH: 05 {val:02X} -> SUB #{val:03d}")
        self.A = (256 + res) % 256 if res < 0 else res
        self.carry = res < 0
        self.zero = (self.A == 0)
        self.add_log(f"  MATH: {old_a:02X}-{val:02X}={self.A:02X} ({old_a:03d}-{val:03d}={res:03d})")
        self.PC += 2

    # 0x06
    def _beq(self):
        addr = self.ram[self.PC + 1]
        self.add_log(f"FETCH: 06 {addr:02X} -> BEQ ${addr:02X}")
        if self.zero:
            self.add_log(f"BRANCH: Z=ON. Saltando a {addr:02X}...")
            self.PC = addr
        else:
            self.add_log(f"BRANCH: Z=OFF. No hay salto.")
            self.PC += 2

    # 0x07 - AND
    def _and(self):
        val = self.ram[self.PC + 1]
        old_a = self.A
        self.add_log(f"FETCH: 07 {val:02X} -> AND #{val:03d}")
        self.A &= val
        self.zero = (self.A == 0)
        self.add_log(f"  LOGIC: %{old_a:08b} & %{val:08b}")
        self.add_log(f"    RES: %{self.A:08b} (Hex: {self.A:02X} | Dec: {self.A:03d})")
        self.PC += 2

    # 0x08 - OR
    def _or(self):
        val = self.ram[self.PC + 1]
        old_a = self.A
        self.add_log(f"FETCH: 08 {val:02X} -> OR #{val:03d}")
        self.A |= val
        self.zero = (self.A == 0)
        self.add_log(f"  LOGIC: %{old_a:08b} | %{val:08b}")
        self.add_log(f"    RES: %{self.A:08b} (Hex: {self.A:02X} | Dec: {self.A:03d})")
        self.PC += 2

    # 0x09 - XOR
    def _xor(self):
        val = self.ram[self.PC + 1]
        old_a = self.A
        self.add_log(f"FETCH: 09 {val:02X} -> XOR #{val:03d}")
        self.A ^= val
        self.zero = (self.A == 0)
        self.add_log(f"  LOGIC: %{old_a:08b} ^ %{val:08b}")
        self.add_log(f"    RES: %{self.A:08b} (Hex: {self.A:02X} | Dec: {self.A:03d})")
        self.PC += 2

    # 0x0A - NOT
    def _not(self):
        old_a = self.A
        self.add_log(f"FETCH: 0A -> NOT")
        self.A = (~self.A) & 0xFF
        self.zero = (self.A == 0)
        self.add_log(f"  LOGIC: ~ %{old_a:08b}")
        self.add_log(f"    RES: %{self.A:08b} (Hex: {self.A:02X} | Dec: {self.A:03d})")
        self.PC += 1

    # 0x0B: LDX #val
    def _ldx(self):
        val = self.ram[self.PC + 1]
        self.add_log(f"FETCH: 0B {val:02X} -> LDX #{val:03d}")
        self.X = val
        self.zero = (self.X == 0)
        self.PC += 2

    # 0x0C: INX
    def _inx(self):
        self.add_log(f"FETCH: 0C -> INX")
        old_x = self.X
        self.X = (self.X + 1) % 256
        self.zero = (self.X == 0)
        self.add_log(f"  REG: X incrementado ({old_x:02X} -> {self.X:02X})")
        self.PC += 1

    # 0x0D: DEX
    def _dex(self):
        self.add_log(f"FETCH: 0D -> DEX")
        old_x = self.X
        self.X = (self.X - 1) % 256
        self.zero = (self.X == 0)
        self.add_log(f"  REG: X decrementado ({old_x:02X} -> {self.X:02X})")
        self.PC += 1

    # 0xFF
    def _halt(self):
        self.add_log("FETCH: FF -> HALT")
        self.running = False

    # --- CICLO DE EJECUCIÓN Y RENDER ---

    def step(self):
        if not self.running or self.PC >= 256: return
        opcode = self.ram[self.PC]
        
        # El Dispatcher busca la función
        instr_func = self.instructions.get(opcode)
        
        if instr_func:
            instr_func()
        else:
            self.add_log(f"SKIP: OpCode {opcode:02X} desconocido")
            self.PC += 1

    def render(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        c_f = "ON" if self.carry else "OFF"
        z_f = "ON" if self.zero else "OFF"
        
        # Cabecera estandarizada: HEX (DEC)
        header_text = f" LOGICA-8 | A: {self.A:02X} ({self.A:03d}) | X: {self.X:02X} ({self.X:03d}) | PC:${self.PC:02X} | CARRY:{c_f} | ZERO:{z_f} "
        border = "═" * len(header_text)
        print(f"╔{border}╗")
        print(f"║{header_text}║")
        print(f"╚{border}╝")
        print("     0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F        HISTORIAL")
        for i in range(16):
            line = f"{i*16:02X}: "
            for j in range(16):
                idx = i*16 + j
                v = self.ram[idx]
                if idx == self.PC: line += f"\033[42m\033[30m{v:02X}\033[0m "
                elif v != 0: line += f"\033[36m{v:02X}\033[0m "
                else: line += f"\033[90m{v:02X}\033[0m "
            if i < len(self.log): line += f"   │ {self.log[i]}"
            print(line)
        print("═"*105)