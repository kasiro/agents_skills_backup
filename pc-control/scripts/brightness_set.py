#!/usr/bin/env python3
import subprocess, sys
val = sys.argv[1] if len(sys.argv) > 1 else "50"
try:
    v = int(val)
    if not 0 <= v <= 100:
        print("Значение должно быть 0-100"); sys.exit(1)
except ValueError:
    print("Значение должно быть числом 0-100"); sys.exit(1)
subprocess.run(["ddcutil", "setvcp", "10", str(v), "--noverify"], check=True)
print(f"Яркость установлена: {v}%")
