
from memory import Memory
from bus import Bus
from microops import *
import os

class CPU:
    def __init__(self):
        self.memory = Memory()
        self.bus = Bus()
        self.bus.attach_memory(self.memory)

        # Registros
        self.A = 0x00
        self.X = 0x00
        self.PC = 0x00
        self.IR = 0x00
        self.carry = False
        self.zero = False
        self.running = True
        self.log = []

        # Micro-ops pendientes
        self.micro_ops = []

        # Tabla de instrucciones
        self.instructions = {
            0x01: self._lda,
            0x02: self._add,
            0x03: self._sta,
            0x04: self._jmp,
            0x05: self._sub,
            0x06: self._beq,
            0x07: self._and,
            0x08: self._or,
            0x09: self._xor,
            0x0A: self._not,
            0x0B: self._ldx,
            0x0C: self._inx,
            0x0D: self._dex,
            0xFF: self._halt
        }

    # --- MÉTODOS DE SOPORTE ---

    def fetch_byte(self):
        byte = self.bus.read(self.PC)
        self.PC += 1
        return byte

    def load_program(self, program, offset=0):
        #self.memory = Memory()
        #self.bus.attach_memory(self.memory)
        self.A = 0x00
        self.X = 0x00
        self.PC = offset
        self.carry = False
        self.zero = False
        self.running = True
        self.log = []
        self.micro_ops = []

        for i, byte in enumerate(program):
            addr = offset + i
            if addr >= 256:
                raise ValueError(f"Programa demasiado largo para memoria: {addr}")
            self.bus.write(addr, byte & 0xFF)

    def add_log(self, msg):
        self.log.append(msg)
        if len(self.log) > 15:
            self.log.pop(0)

    # --- INSTRUCCIONES ---

	# 0x01
    def _lda(self):
        self.micro_ops.append(lambda: fetch_operand(self))
        self.micro_ops.append(lambda: load_A(self))

	# 0x02
    def _add(self):
        def do_add():
            old_a = self.A
            self.A = (self.A + self.operand) % 256
            self.carry = (old_a + self.operand) > 255
            self.zero = (self.A == 0)
            self.add_log(f"ADD: {old_a:02X}+{self.operand:02X}={self.A:02X}")
        self.micro_ops.append(lambda: fetch_operand(self))
        self.micro_ops.append(do_add)

	# 0x03
    def _sub(self):
        def do_sub():
            old_a = self.A
            res = self.A - self.operand
            self.A = res % 256
            self.carry = res < 0
            self.zero = (self.A == 0)
            self.add_log(f"SUB: {old_a:02X}-{self.operand:02X}={self.A:02X}")
        self.micro_ops.append(lambda: fetch_operand(self))
        self.micro_ops.append(do_sub)

	# 0x04
    def _sta(self):
        def do_sta():
            self.bus.write(self.operand, self.A)
            self.add_log(f"STA: {self.A:02X} -> ${self.operand:02X}")
        self.micro_ops.append(lambda: fetch_operand(self))
        self.micro_ops.append(do_sta)

	# 0x05
    def _jmp(self):
        def do_jmp():
            self.PC = self.operand
            self.add_log(f"JMP -> ${self.operand:02X}")
        self.micro_ops.append(lambda: fetch_operand(self))
        self.micro_ops.append(do_jmp)

	# 0x06
    def _beq(self):
        def do_beq():
            if self.zero:
                self.PC = self.operand
                self.add_log(f"BEQ Z=ON -> PC=${self.operand:02X}")
            else:
                self.add_log(f"BEQ Z=OFF, no salto")
        self.micro_ops.append(lambda: fetch_operand(self))
        self.micro_ops.append(do_beq)

	# 0x07
    def _and(self):
        def do_and():
            old_a = self.A
            self.A &= self.operand
            self.zero = (self.A == 0)
            self.add_log(f"AND: {old_a:02X} & {self.operand:02X} = {self.A:02X}")
        self.micro_ops.append(lambda: fetch_operand(self))
        self.micro_ops.append(do_and)

	# 0x08
    def _or(self):
        def do_or():
            old_a = self.A
            self.A |= self.operand
            self.zero = (self.A == 0)
            self.add_log(f"OR: {old_a:02X} | {self.operand:02X} = {self.A:02X}")
        self.micro_ops.append(lambda: fetch_operand(self))
        self.micro_ops.append(do_or)

	# 0x09
    def _xor(self):
        def do_xor():
            old_a = self.A
            self.A ^= self.operand
            self.zero = (self.A == 0)
            self.add_log(f"XOR: {old_a:02X} ^ {self.operand:02X} = {self.A:02X}")
        self.micro_ops.append(lambda: fetch_operand(self))
        self.micro_ops.append(do_xor)

    # 0x0A
    def _not(self):
        def do_not():
            old_a = self.A
            self.A = (~self.A) & 0xFF
            self.zero = (self.A == 0)
            self.add_log(f"NOT: ~{old_a:02X} = {self.A:02X}")
        self.micro_ops.append(do_not)

    # 0x0B
    def _ldx(self):
        def do_ldx():
            self.X = self.operand
            self.zero = (self.X == 0)
            self.add_log(f"LDX: {self.X:02X}")
        self.micro_ops.append(lambda: fetch_operand(self))
        self.micro_ops.append(do_ldx)

    # 0x0C
    def _inx(self):
        def do_inx():
            old_x = self.X
            self.X = (self.X + 1) % 256
            self.zero = (self.X == 0)
            self.add_log(f"INX: {old_x:02X} -> {self.X:02X}")
        self.micro_ops.append(do_inx)

    # 0x0D
    def _dex(self):
        def do_dex():
            old_x = self.X
            self.X = (self.X - 1) % 256
            self.zero = (self.X == 0)
            self.add_log(f"DEX: {old_x:02X} -> {self.X:02X}")
        self.micro_ops.append(do_dex)

    # 0xFF
    def _halt(self):
        def do_halt():
            self.running = False
            self.add_log("HALT ejecutado")
        self.micro_ops.append(do_halt)


    # --- CICLO DE EJECUCIÓN ---
    
    def step(self):
        print(f"STEP: PC={self.PC:02X}, running={self.running}, micro_ops={len(self.micro_ops)}")

        if not self.running:
            return

        # 1 Si hay micro-ops pendientes, ejecutar una
        if self.micro_ops:
            micro = self.micro_ops.pop(0)
            micro()
            return

        # 2️ FETCH (opcode)
        if self.PC >= 256:
            self.running = False
            return
        
        self.IR = self.fetch_byte()
        print(f"FETCH: PC={self.PC:02X} ir={self.IR:02X}")

        # 3️ DECODIFICACIÓN
        instr = self.instructions.get(self.IR)
        if instr:
            instr()
        else:
            self.add_log(f"SKIP: Opcode {self.IR:02X}")


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
                v = self.bus.read(idx)
                if idx == self.PC: line += f"\033[42m\033[30m{v:02X}\033[0m "
                elif v != 0: line += f"\033[36m{v:02X}\033[0m "
                else: line += f"\033[90m{v:02X}\033[0m "
            if i < len(self.log): line += f"   │ {self.log[i]}"
            print(line)
        print("═"*105)