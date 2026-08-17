#!/usr/bin/env python3
import subprocess, re
out = subprocess.run(["ddcutil", "getvcp", "10"], capture_output=True, text=True).stdout
m = re.search(r"current value =\s*(\d+)", out)
cur = int(m.group(1)) if m else 0
new = max(0, cur - 10)
subprocess.run(["ddcutil", "setvcp", "10", str(new), "--noverify"], check=True)
print(f"Яркость: {cur}% → {new}%")
