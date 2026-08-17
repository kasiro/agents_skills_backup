#!/usr/bin/env python3
import subprocess
out = subprocess.run(["ddcutil", "getvcp", "10"], capture_output=True, text=True)
print(out.stdout.strip() or out.stderr.strip())
