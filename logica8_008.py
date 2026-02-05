import os
import time

# --- CONFIGURACIÓN ---
HELP_TEXT = """
LOGICA-8 - AYUDA
----------------------------------
01 [val] : LDA #val - Carga el valor en el Acumulador (A).
02 [val] : ADD #val - Suma el valor al Acumulador.
03 [dir] : STA $dir - Guarda el Acumulador en la dirección RAM.
04 [dir] : JMP $dir - Salta la ejecución a la dirección indicada.
05 [val] : SUB #val - Resta el valor al Acumulador.
06 [dir] : BEQ $dir - Salta a $dir si el Flag ZERO está ON.
07 [val] : AND #val - Operación lógica AND bit a bit.
08 [val] : OR  #val - Operación lógica OR bit a bit.
09 [val] : XOR #val - Operación lógica XOR (OR exclusiva).
0A       : NOT      - Invierte todos los bits del Acumulador.
0B [val] : LDX #val - Carga el valor en el Registro X.
0C       : INX      - Incrementa el Registro X en 1.
0D       : DEX      - Decrementa el Registro X en 1.
FF       : HALT     - Detiene la CPU.

REGLAS Y FLAGS:
- Memoria: 256 celdas ($00 a $FF).
- Registros: A y X son de 8 bits (0-255).
- CARRY: Se activa (ON) si una operación excede los 8 bits.
- ZERO : Se activa (ON) si el resultado de la operación es 0.
"""

PROGRAMS = {
    "1": ("Carga 200, Suma 100, Se detiene.", [0x01, 200, 0x02, 100, 0xFF], 0x00),
    "2": ("Carga 15, Suma 10, Guarda en memoria (en direccion 80), Se detiene.", [0x01, 0x0F, 0x02, 0x0A, 0x03, 0x80, 0xFF], 0x00),
    "3": ("Suma con Overflow (200+100).", [0x01, 200, 0x02, 100, 0xFF], 0x00),
    "4": ("Cuenta Atrás (de 10 a 0). El programa se almacena en la fila 1.", [0x01, 10, 0x05, 1, 0x06, 0x18, 0x04, 0x12, 0xFF], 0x10),
    "5": ("Bucle de incremento en RAM.", [0x01, 0, 0x02, 1, 0x03, 0xFF, 0x04, 0x02], 0x00),
    "6": ("Carga 31, compara mediante XOR (Exclusive-Or) con 74 y muestra en consola resultado en binario y en decimal.", [0x01, 0x1F, 0x09, 0x4A, 0xFF], 0x00),
    "7": ("Multiplicación (5 x 3) usando Registro X como contador.", 
          [
            0x01, 0x00, # 00: LDA #0 (Resultado en A)
            0x0B, 0x03, # 02: LDX #3 (Contador en X)
            0x02, 0x05, # 04: ADD #5 (Bucle: A = A + 5)
            0x0D,       # 06: DEX    (X = X - 1)
            0x06, 0x0B, # 07: BEQ $0C (Si X es 0, salta al STA en la pos 12)
            0x04, 0x04, # 09: JMP $04 (Si no es 0, vuelve al ADD en la pos 4)
            0x03, 0x50, # 0C: STA $50 (Guarda resultado)
            0xFF        # 0E: HALT
          ], 0x00)
}

# Mapeo de instrucciones en ensamblador a OpCodes
ASM_TO_HEX = {
    "LDA": 0x01, "ADD": 0x02, "STA": 0x03, "JMP": 0x04,
    "SUB": 0x05, "BEQ": 0x06, "AND": 0x07, "OR": 0x08,
    "XOR": 0x09, "NOT": 0x0A, "LDX": 0x0B, "INX": 0x0C,
    "DEX": 0x0D, "HALT": 0xFF
}

# Lista de instrucciones que NO llevan valor adicional (solo ocupan 1 byte)
SINGLE_BYTE_INSTR = ["INX", "DEX", "NOT", "HALT"]

# ensamblador
def assembler():
    print("\n--- LOGICA-8 - ENSAMBLADOR ---")
    print("Escribe una instrucción por línea (ej: LDA 0x05).")
    print("Escribe 'FIN' para terminar y cargar.")
    print("-" * 35)
    
    codigo_usuario = []
    bytecode_final = []
    direccion_actual = 0
    
    while True:
        linea = input(f"${direccion_actual:02X} > ").upper().strip()
        if linea == "FIN": break
        if not linea: continue
        
        partes = linea.split()
        mnemonico = partes[0]
        
        if mnemonico in ASM_TO_HEX:
            opcode = ASM_TO_HEX[mnemonico]
            
            # Caso A: Instrucciones simples (1 byte)
            if mnemonico in SINGLE_BYTE_INSTR:
                print(f"      [ TRADUCCIÓN: {opcode:02X} ]")
                bytecode_final.append(opcode)
                direccion_actual += 1
            
            # Caso B: Instrucciones con valor (2 bytes)
            elif len(partes) > 1:
                valor = parse_value(partes[1])
                if valor is not None and 0 <= valor <= 255:
                    print(f"      [ TRADUCCIÓN: {opcode:02X} {valor:02X} ]")
                    bytecode_final.extend([opcode, valor])
                    direccion_actual += 2
                else:
                    print("      [ ERROR: Valor no válido ]")
            else:
                print(f"      [ ERROR: {mnemonico} necesita un valor ]")
        else:
            print(f"      [ ERROR: Instrucción desconocida ]")
            
    return bytecode_final


class Logica8:
    def __init__(self):
        self.ram = bytearray(256)
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

# --- SISTEMA DE MENÚS (Interfaz) ---

def run_tests():
    print("\n[ INICIANDO TEST DE SISTEMA LOGICA-8 ]\n")
    cpu = Logica8()
    tests_passed = 0
    total_tests = 0

    def assert_test(name, condition, details=""):
        nonlocal tests_passed, total_tests
        total_tests += 1
        if condition:
            print(f"  [OK]   {name}")
            tests_passed += 1
        else:
            print(f"  [FAIL] {name} -> {details}")

    # --- TEST 1: Carga y Aritmética básica ---
    cpu.load_program([0x01, 10, 0x02, 5, 0xFF]) # LDA 10, ADD 5
    while cpu.running: cpu.step()
    assert_test("LDA/ADD: 10 + 5 = 15", cpu.A == 15, f"A={cpu.A}")

    # --- TEST 2: Overflow y Carry ---
    cpu.load_program([0x01, 250, 0x02, 10, 0xFF]) # 250 + 10 = 260 (4 mod 256)
    while cpu.running: cpu.step()
    assert_test("CARRY: 250 + 10 produce Carry y A=4", cpu.A == 4 and cpu.carry is True)

    # --- TEST 3: Subtracción y Zero Flag ---
    cpu.load_program([0x01, 20, 0x05, 20, 0xFF]) # 20 - 20 = 0
    while cpu.running: cpu.step()
    assert_test("ZERO: 20 - 20 activa Zero flag", cpu.A == 0 and cpu.zero is True)

    # --- TEST 4: Lógica AND ---
    cpu.load_program([0x01, 0xFF, 0x07, 0x0F, 0xFF]) # 11111111 & 00001111
    while cpu.running: cpu.step()
    assert_test("LOGIC: 0xFF AND 0x0F = 0x0F", cpu.A == 0x0F)

    # --- TEST 5: Saltos (JMP/BEQ) ---
    # LDA 1, BEQ a FIN(HALT), ADD 1, JMP a FIN. 
    # Si BEQ funciona mal, A será 2. Si funciona bien, A será 1.
    cpu.load_program([
        0x01, 0,    # LDA 0 (Activa Zero)
        0x06, 0x06, # BEQ a la dirección 0x06 (el HALT)
        0x02, 0x01, # ADD 1 (No debería ejecutarse)
        0xFF        # HALT en 0x06
    ])
    while cpu.running: cpu.step()
    assert_test("BRANCH: BEQ salta correctamente si Z=ON", cpu.A == 0)

    # --- TEST 6: Parser de Valores ---
    test_val = parse_value("0xFF") == 255 and parse_value("%10") == 2 and parse_value("10") == 10
    assert_test("PARSER: Detección correcta de 0x, % y Dec", test_val)

    # --- TEST 7: Registro X (LDX, INX, DEX) ---
    # Cargamos 255 en X, incrementamos (pasa a 0), cargamos 5 en A
    # Verificamos que A es 5, X es 0 y el flag Zero está ON.
    cpu.load_program([
        0x0B, 255,  # LDX #255
        0x0C,       # INX (X vuelve a 0, activa Zero)
        0x01, 5,    # LDA #5 (A=5, desactiva Zero porque 5 != 0)
        0x0D,       # DEX (A sigue siendo 5, X pasa a 255)
        0xFF        # HALT
    ])
    while cpu.running: cpu.step()
    condicion_x = (cpu.A == 5 and cpu.X == 255 and cpu.zero is False)
    assert_test("REGISTRO X: Independencia de A y gestión de flags", condicion_x, f"A={cpu.A}, X={cpu.X}, Z={cpu.zero}")

    print(f"\nRESULTADO: {tests_passed}/{total_tests} tests superados.")
    input("\nPresiona ENTER para volver...")


def parse_value(s):
    """
    Convierte strings en enteros de 8 bits de forma estricta:
    - 0x... : Hexadecimal
    - %...  : Binario
    - Sin prefijo: Decimal
    """
    s = s.strip().lower()
    try:
        if s.startswith('0x'):
            return int(s[2:], 16)
        elif s.startswith('%'):
            return int(s[1:], 2)
        else:
            # Si no hay prefijo, asumimos DECIMAL puro
            return int(s, 10)
    except ValueError:
        return None

def run_emulator(cpu):
    while cpu.running:
        cpu.render()
        cmd = input("\n[ENTER: Paso | Q: Menú] > ").upper()
        if cmd == "Q": break
        cpu.step()
    cpu.render()
    if not cpu.running: input("\nHALT alcanzado. ENTER para volver...")

def main():
    cpu = Logica8()
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("      █▒▒▒▒▒▒▒▒▒ LOGICA-8: CONTROL PANEL ▒▒▒▒▒▒▒▒▒█")
        print("      1. Ver Ayuda")
        print("      2. Cargar Programa de Ejemplo")
        print("      3. Introducir Programa en código hexadecimal")
        print("      4. Introducir Programa en lenguaje ensamblador")
        print("      5. Ejecutar Tests de Sistema")
        print("      6. Salir")
        print("      " + "─"*43)
        
        opcion = input(" Selecciona una opción > ")
        
        if opcion == "1":
            os.system('cls' if os.name == 'nt' else 'clear')
            print(HELP_TEXT)
            input("Presiona ENTER para volver...")
        
        elif opcion == "2":
            print("\nPROGRAMAS DISPONIBLES:")
            for k, v in PROGRAMS.items():
                print(f"{k}. {v[0]}")
            p_op = input("Seleccionar > ")
            if p_op in PROGRAMS:
                nombre, bytecode, offset = PROGRAMS[p_op]
                cpu.load_program(bytecode, offset)
                cpu.add_log(f"SISTEMA: Cargado '{nombre}'")
                run_emulator(cpu)

        elif opcion == "3":
            print("\nEscribe los bytes separados por espacios.")
            print("Formatos aceptados: 10 (Dec), 0x0A (Hex), %00001010 (Bin)")
            entrada = input("INPUT > ")
            
            partes = entrada.split()
            bytecode = []
            error = False
            
            for p in partes:
                valor = parse_value(p)
                if valor is not None and 0 <= valor <= 255:
                    bytecode.append(valor)
                else:
                    print(f"Error: '{p}' no es un valor de 8 bits válido.")
                    error = True
                    break
            
            if not error and bytecode:
                cpu.load_program(bytecode, 0x00)
                cpu.add_log("SISTEMA: Código manual cargado en $00")
                run_emulator(cpu)
            elif not error:
                print("Error: El programa está vacío.")
                time.sleep(2)
            else:
                time.sleep(2)

        elif opcion == "4":
            nuevo_programa = assembler()
            if nuevo_programa:
                cpu.load_program(nuevo_programa, 0x00)
                cpu.add_log("SISTEMA: Programa ensamblado y cargado en $00")
                run_emulator(cpu)

        elif opcion == "5":
            run_tests()

        elif opcion == "6":
            print("Apagando LOGICA-8...")
            break

if __name__ == "__main__":
    main()
