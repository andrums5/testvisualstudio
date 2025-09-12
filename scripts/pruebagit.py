from datetime import datetime
import platform
import sys


def main() -> None:
    print("Hola desde scripts/pruebagit.py 👋")
    print(f"Versión de Python: {sys.version.split()[0]}")
    print(f"Sistema: {platform.system()} {platform.release()}")

    numeros = [1, 2, 3, 4]
    print(f"Números: {numeros}")
    print(f"Suma: {sum(numeros)}")

    for i in range(3):
        ahora = datetime.now().strftime('%H:%M:%S')
        print(f"Contador {i + 1} de 3 - {ahora}")

    print("Listo. ¡Esto era solo para tener algo de código!")

    print("Segunda prueba")


if __name__ == "__main__":
    main()
