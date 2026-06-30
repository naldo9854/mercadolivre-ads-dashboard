import re
import glob

files = glob.glob("*.py")
for fn in files:
    print(f"\n=== File: {fn} ===")
    with open(fn, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            if "acos" in line.lower():
                print(f"{idx}: {line.strip()}")
