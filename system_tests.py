
from cpu import *
from assembler import *

def run_tests():
    print("\n[ INICIANDO TEST DE SISTEMA LOGICA-8 ]\n")
    cpu = CPU()
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