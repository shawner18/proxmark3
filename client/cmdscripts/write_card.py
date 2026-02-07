import subprocess
from pathlib import Path

BASE_DIR = Path.cwd()

DUMP = BASE_DIR / "./../../Bambu-Lab-RFID-Library/PLA/PLA Basic/White/E4E447D1/hf-mf-E4E447D1-dump.bin"
KEY = "FFFFFFFFFFFF"

STEP1 = BASE_DIR / "step1_uid.cmd"
STEP2 = BASE_DIR / "step2_data.cmd"
STEP3 = BASE_DIR / "step3_trailer.cmd"

def is_trailer(block):
    return (block + 1) % 4 == 0

data = DUMP.read_bytes()
if len(data) != 1024:
    raise ValueError("Dump must be exactly 1024 bytes (MIFARE Classic 1K)")

blocks = [data[i:i+16].hex() for i in range(0, len(data), 16)]

# -------------------------
# STEP 1: UID / Block 0
# -------------------------
step1 = [
    "# STEP 1: Unlock magic card and write block 0",
    "# VERIFY UID/BCC AFTER THIS STEP",
    "",
    "hf mf csetuid -u",
    f"hf mf wrbl --force --blk 0 -k {KEY} -a -d {blocks[0]}",
    "hf mf rdbl --blk 0",
]

STEP1.write_text("\n".join(step1))

# -------------------------
# STEP 2: DATA BLOCKS
# -------------------------
step2 = [
    "# STEP 2: Write data blocks",
    "# VERIFY DATA BEFORE PROCEEDING TO STEP 3",
    ""
]

for i, blk in enumerate(blocks):
    if i == 0 or is_trailer(i):
        continue
    step2.append(
        f"hf mf wrbl --force --blk {i} -k {KEY} -a -d {blk}"
    )

step2.append("")
step2.append("# Optional verification")
step2.append("hf mf dump")

STEP2.write_text("\n".join(step2))

# -------------------------
# STEP 3: SECTOR TRAILERS
# -------------------------
step3 = [
    "# STEP 3: WRITE SECTOR TRAILERS",
    "# WARNING: THIS LOCKS KEYS & ACCESS BITS",
    "# MAKE SURE STEPS 1 AND 2 WERE VERIFIED",
    ""
]

for i, blk in enumerate(blocks):
    if is_trailer(i):
        step3.append(
            f"hf mf wrbl --force --blk {i} -k {KEY} -a -d {blk}"
        )

STEP3.write_text("\n".join(step3))

print("[+] Proxmark scripts generated:")
print(f" - {STEP1.name}")
print(f" - {STEP2.name}")
print(f" - {STEP3.name}")
print()
print("Run them INSIDE pm3 in this order:")
print(f"  script run {STEP1.name}")
print(f"  script run {STEP2.name}")
print(f"  script run {STEP3.name}")
