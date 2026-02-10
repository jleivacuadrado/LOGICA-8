
from memory import Memory
from bus import Bus
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
    def load_program(self, program, offset=0):
        self.memory = Memory()
        self.bus.attach_memory(self.memory)
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
        if self.PC + 1 >= 256:
            raise IndexError("LDA: fetch de operando fuera de memoria")
        val = self.bus.read(self.PC + 1)
        self.A = val
        self.zero = (self.A == 0)
        self.add_log(f"LDA #{val:03d}")
        self.PC += 2  # OPCODE + OPERANDO

    # 0x02
    def _add(self):
        if self.PC + 1 >= 256:
            raise IndexError("ADD: fetch de operando fuera de memoria")
        val = self.bus.read(self.PC + 1)
        res = self.A + val
        self.carry = res > 255
        self.A = res % 256
        self.zero = (self.A == 0)
        self.add_log(f"ADD #{val:03d} -> A={self.A}")
        self.PC += 2

    # 0x03
    def _sta(self):
        if self.PC + 1 >= 256:
            raise IndexError("STA: fetch de operando fuera de memoria")
        addr = self.bus.read(self.PC + 1)
        self.bus.write(addr, self.A)
        self.add_log(f"STA ${addr:02X}")
        self.PC += 2

    # 0x04
    def _jmp(self):
        if self.PC + 1 >= 256:
            raise IndexError("JMP: fetch de operando fuera de memoria")
        addr = self.bus.read(self.PC + 1)
        self.PC = addr

        # 0x05
    def _sub(self):
        if self.PC + 1 >= 256:
            raise IndexError("ADD: fetch de operando fuera de memoria")
        val = self.bus.read(self.PC + 1)
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
        if self.PC + 1 >= 256:
            raise IndexError("ADD: fetch de operando fuera de memoria")
        addr = self.bus.read(self.PC + 1)
        self.add_log(f"FETCH: 06 {addr:02X} -> BEQ ${addr:02X}")
        if self.zero:
            self.add_log(f"BRANCH: Z=ON. Saltando a {addr:02X}...")
            self.PC = addr
        else:
            self.add_log(f"BRANCH: Z=OFF. No hay salto.")
            self.PC += 2

    # 0x07 - AND
    def _and(self):
        if self.PC + 1 >= 256:
            raise IndexError("ADD: fetch de operando fuera de memoria")
        val = self.bus.read(self.PC + 1)
        old_a = self.A
        self.add_log(f"FETCH: 07 {val:02X} -> AND #{val:03d}")
        self.A &= val
        self.zero = (self.A == 0)
        self.add_log(f"  LOGIC: %{old_a:08b} & %{val:08b}")
        self.add_log(f"    RES: %{self.A:08b} (Hex: {self.A:02X} | Dec: {self.A:03d})")
        self.PC += 2

    # 0x08 - OR
    def _or(self):
        if self.PC + 1 >= 256:
            raise IndexError("ADD: fetch de operando fuera de memoria")
        val = self.bus.read(self.PC + 1)
        old_a = self.A
        self.add_log(f"FETCH: 08 {val:02X} -> OR #{val:03d}")
        self.A |= val
        self.zero = (self.A == 0)
        self.add_log(f"  LOGIC: %{old_a:08b} | %{val:08b}")
        self.add_log(f"    RES: %{self.A:08b} (Hex: {self.A:02X} | Dec: {self.A:03d})")
        self.PC += 2

    # 0x09 - XOR
    def _xor(self):
        if self.PC + 1 >= 256:
            raise IndexError("ADD: fetch de operando fuera de memoria")
        val = self.bus.read(self.PC + 1)
        old_a = self.A
        self.add_log(f"FETCH: 09 {val:02X} -> XOR #{val:03d}")
        self.A ^= val
        self.zero = (self.A == 0)
        self.add_log(f"  LOGIC: %{old_a:08b} ^ %{val:08b}")
        self.add_log(f"    RES: %{self.A:08b} (Hex: {self.A:02X} | Dec: {self.A:03d})")
        self.PC += 2

    # 0x0A - NOT
    def _not(self):
        if self.PC + 1 >= 256:
            raise IndexError("ADD: fetch de operando fuera de memoria")
        old_a = self.A
        self.add_log(f"FETCH: 0A -> NOT")
        self.A = (~self.A) & 0xFF
        self.zero = (self.A == 0)
        self.add_log(f"  LOGIC: ~ %{old_a:08b}")
        self.add_log(f"    RES: %{self.A:08b} (Hex: {self.A:02X} | Dec: {self.A:03d})")
        self.PC += 1

    # 0x0B: LDX #val
    def _ldx(self):
        if self.PC + 1 >= 256:
            raise IndexError("ADD: fetch de operando fuera de memoria")
        val = self.bus.read(self.PC + 1)
        self.add_log(f"FETCH: 0B {val:02X} -> LDX #{val:03d}")
        self.X = val
        self.zero = (self.X == 0)
        self.PC += 2

    # 0x0C: INX
    def _inx(self):
        if self.PC + 1 >= 256:
            raise IndexError("ADD: fetch de operando fuera de memoria")
        self.add_log(f"FETCH: 0C -> INX")
        old_x = self.X
        self.X = (self.X + 1) % 256
        self.zero = (self.X == 0)
        self.add_log(f"  REG: X incrementado ({old_x:02X} -> {self.X:02X})")
        self.PC += 1

    # 0x0D: DEX
    def _dex(self):
        if self.PC + 1 >= 256:
            raise IndexError("ADD: fetch de operando fuera de memoria")
        self.add_log(f"FETCH: 0D -> DEX")
        old_x = self.X
        self.X = (self.X - 1) % 256
        self.zero = (self.X == 0)
        self.add_log(f"  REG: X decrementado ({old_x:02X} -> {self.X:02X})")
        self.PC += 1

    # 0xFF
    def _halt(self):
        if self.PC + 1 >= 256:
            raise IndexError("ADD: fetch de operando fuera de memoria")
        self.add_log("HALT")
        self.running = False


    # --- CICLO DE EJECUCIÓN ---
    def step(self):
        if not self.running:
            return

        # Ejecutar micro-op si hay
        if self.micro_ops:
            micro = self.micro_ops.pop(0)
            micro()
            return

        # Fetch opcode
        if self.PC >= 256:
            self.running = False
            return
        self.IR = self.bus.read(self.PC)

        # Dispatch
        instr = self.instructions.get(self.IR)
        if instr:
            instr()
        else:
            self.add_log(f"SKIP opcode {self.IR:02X}")
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
                v = self.bus.read(idx)
                if idx == self.PC: line += f"\033[42m\033[30m{v:02X}\033[0m "
                elif v != 0: line += f"\033[36m{v:02X}\033[0m "
                else: line += f"\033[90m{v:02X}\033[0m "
            if i < len(self.log): line += f"   │ {self.log[i]}"
            print(line)
        print("═"*105)