### Helper to write Gen2 FUID tags
## Written by Shawner18 much help from existing examples
import argparse
import pm3
import time
import os
import re

try:
    # pip install ansicolors
    from colors import color
except ModuleNotFoundError:
    def color(s, fg=None):
        _ = fg
        return str(s)

parser = argparse.ArgumentParser(description='A script to help with raw USCUID-UL commands. Out of everything until -s, only one functionality can be used at a time, prioritised in order listed below.')
parser.add_argument('-f', '--file', nargs='+', help='Path to bin file to write (supports unquoted paths with spaces)')
parser.add_argument('-r', '--retries', type=int, default=3, help='Number of times to attempt writes')
parser.add_argument('--skip-gen2', action='store_true', default=False, help='Skip checking for Gen 2 capability (use with caution)')
parser.add_argument('--echo-trailer', action='store_true', default=False, help='Echo trailer write commands instead of executing them')
parser.add_argument('--keyfile', nargs='+', help='Path to key file to use for final dump (supports unquoted paths with spaces)')

args = parser.parse_args()


# Support file and keyfile passed as multiple tokens (unquoted paths with spaces)
if hasattr(args, 'file') and args.file:
    file = ' '.join(args.file)
else:
    file = "Bambu-Lab-RFID-Library\\PLA\\PLA Basic\\Black\\F41347D4\\hf-mf-F41347D4-dump.bin"
# strip surrounding quotes if present
file = file.strip('"\'')

# Determine keyfile: if not supplied, derive from dump filename
if hasattr(args, 'keyfile') and args.keyfile:
    keyfile = ' '.join(args.keyfile)
else:
    # Use os.path to properly handle relative paths
    base, ext = os.path.splitext(file)
    if base.endswith('-dump'):
        keyfile = base[:-5] + '-key.bin'  # Remove '-dump', add '-key.bin'
    else:
        keyfile = base + '-key.bin'

# strip surrounding quotes if present
keyfile = keyfile.strip('"\'')

# Ensure relative paths are prefixed with .\ for pm3
if not os.path.isabs(keyfile) and not keyfile.startswith('.'):
    keyfile = ".\\" + keyfile


def read_1k_bytes(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    if len(data) != 1024:
        raise ValueError(f"File length is {len(data)} bytes, expected 1024 bytes (1k).")
    return data


def resolve_dump_file(path):
    """Resolve the actual 1k dump file for a given path.

    Accepts:
    - direct path to a file (must be 1024 bytes)
    - base path without extension (will try common suffixes)
    - directory: will search for '*-dump.bin' then any '*.bin' file of 1k size
    Raises FileNotFoundError if no suitable 1k file is found.
    """
    # Exact file path
    if os.path.isfile(path):
        try:
            if os.path.getsize(path) == 1024:
                return path
        except Exception:
            pass

    # Directory: search for dump files
    if os.path.isdir(path):
        # prefer *-dump.bin, then any .bin
        for root, dirs, files in os.walk(path):
            for fname in files:
                if fname.endswith('-dump.bin') or fname.endswith('.bin'):
                    candidate = os.path.join(root, fname)
                    try:
                        if os.path.getsize(candidate) == 1024:
                            return candidate
                    except Exception:
                        continue
        raise FileNotFoundError(f"No suitable dump file (1k) found in directory {path}")

    # Try common filename variants
    candidates = [
        path,
        path + '-dump.bin',
        path + '.bin',
        path + '-dump',
        os.path.join(os.path.dirname(path), os.path.basename(path) + '-dump.bin'),
    ]
    for c in candidates:
        if os.path.isfile(c):
            try:
                if os.path.getsize(c) == 1024:
                    return c
            except Exception:
                continue

    raise FileNotFoundError(f"No suitable 1k dump file found for path {path}")


p = pm3.pm3()

fresh_tag_UIDS = ["3A D8 2D AD", "D5 49 42 1E", "F4 13 47 D4", "DE AD BE EF", "E4 E4 47 D1", "AA 55 C3 96"]
RETRIES = args.retries if hasattr(args, 'retries') else 3
SKIP_GEN2 = args.skip_gen2 if hasattr(args, 'skip_gen2') else True
ECHO_TRAILER = args.echo_trailer if hasattr(args, 'echo_trailer') else False
DEBUG = True
SIMULATE = False

def lprint(s='',  end='\n', flush=False, prompt="[" + color("=", fg="yellow") + "] ", log=True):
    """Print and Log.

    globals:
    - logbuffer (RW)
    - logfile (R)
    """
    s = f"{prompt}" + f"\n{prompt}".join(s.split('\n'))
    safe_s = s.encode('utf-8', errors='ignore').decode('utf-8')
    print(safe_s, end=end, flush=flush)

def format_block_for_compare(block_num, hexstr):
    # hexstr: 32 hex chars (16 bytes)
    spaced = ' '.join(hexstr[i:i+2].upper() for i in range(0, len(hexstr), 2))
    return f"{block_num} | {spaced} |"



def is_trailer(block):
    return (block + 1) % 4 == 0

def write_block_with_retries(blk_num, data_hex, force=False, write_key="FFFFFFFFFFFF", verify_key=None, skip_verify=False):
    """Attempt to write a block up to RETRIES times, verifying after each write.
    
    Args:
        blk_num: Block number to write
        data_hex: 32 hex characters (16 bytes) to write
        force: Whether to use --force flag
        write_key: Key to use for writing (default FFFFFFFFFFFF)
        verify_key: Key to use for reading/verification. If None, uses write_key.
    """
    if verify_key is None:
        verify_key = write_key
    cmd_force = '--force ' if force else ''
    last_out = ''
    for attempt in range(1, RETRIES + 1):
        cmd = f'hf mf wrbl {cmd_force}--blk {blk_num} -k {write_key} -a -d {data_hex}'
        res = p.console(cmd)
        out = p.grabbed_output
        last_out = out
        if SIMULATE:
            lprint("SIMULATE mode enabled, skipping actual write operations.", prompt="[" + color("i", fg="yellow") + "] ")
            return True, "Simulated write success."
        if res == 0 and "Write ( fail )" not in out:
            # After write, optionally verify by reading with the verify_key only
            if skip_verify:
                return True, out + "\n" + "(verification skipped)"
            res_verify = p.console(f'hf mf rdbl --blk {blk_num} -a -k {verify_key}')
            out_verify = p.grabbed_output
            if res_verify == 0 and "Read ( fail )" not in out_verify:
                expected_line = format_block_for_compare(blk_num, data_hex)
                if expected_line in out_verify:
                    return True, out + "\n" + out_verify
                else:
                    lprint(f"Verification mismatch on block {blk_num}. Expected: {expected_line}. Got: {out_verify}", prompt="[" + color("!", fg="red") + "] ")
            else:
                lprint(f"Read failed after write for block {blk_num} with verify key {verify_key}: {out_verify}", prompt="[" + color("!", fg="red") + "] ")
        else:
            lprint(f"Write failed for block {blk_num}: {out}", prompt="[" + color("!", fg="red") + "] ")
        if attempt < RETRIES:
            lprint(f"Retrying block {blk_num} (attempt {attempt+1}/{RETRIES})...", prompt="[" + color("i", fg="yellow") + "] ")
            time.sleep(1)  # brief pause before retry
    return False, last_out


def read_block_with_retries(blk_num, key="FFFFFFFFFFFF", extra_flags='-a'):
    """Attempt to read a block up to RETRIES times.

    By default uses '-a' to include full hex/ascii output and uses the default
    key (FFFFFFFFFFFF). You can pass a different key or set extra_flags to ''
    if you need a different read format.
    """
    last_out = ''
    for attempt in range(1, RETRIES + 1):
        cmd = f'hf mf rdbl --blk {blk_num} {extra_flags} -k {key}' if key or extra_flags else f'hf mf rdbl --blk {blk_num}'
        res = p.console(cmd)
        out = p.grabbed_output
        last_out = out
        if SIMULATE:
            lprint("SIMULATE mode enabled, skipping actual read operations.", prompt="[" + color("i", fg="yellow") + "] ")
            return True, "Simulated read success."
        if res == 0 and "Read ( fail )" not in out:
            return True, out
        lprint(f"Read failed for block {blk_num}: {out}", prompt="[" + color("!", fg="red") + "] ")
        if attempt < RETRIES:
            lprint(f"Retrying read block {blk_num} (attempt {attempt+1}/{RETRIES})...", prompt="[" + color("i", fg="yellow") + "] ")
            time.sleep(0.5)
    return False, last_out


# Color name guessing and swatch output were removed because the
# guessed names were sometimes misleading and the swatch created
# duplicate visual output. We keep only the parsed hex and a link
# to colorhexa for detailed inspection.


def _parse_b4_b5(b4: bytes, b5: bytes):
    """Parse material string and Block 5 fields from raw 16-byte blocks.

    Returns (material_str, color_info, weight_g, diameter_mm, diameter_note, color_link)
    """
    material_str = None
    color_info = None
    weight_g = None
    diameter_mm = None
    diameter_note = None
    color_link = None

    try:
        material_str = b4.decode('ascii', errors='ignore').rstrip('\x00').strip()
    except Exception:
        material_str = None

    try:
        import struct
        if len(b5) >= 16:
            r, g, b, a = b5[0], b5[1], b5[2], b5[3]
            hexstr = f"#{r:02X}{g:02X}{b:02X}"
            color_info = f"{hexstr} (A={a})"
            color_link = f"https://www.colorhexa.com/{hexstr.lstrip('#').lower()}"
            weight_g = int.from_bytes(b5[4:6], 'little')

            # Robust diameter parsing
            try:
                # try float64 LE but only accept plausible filament values (0.5–10 mm)
                if len(b5) >= 16:
                    diam64 = struct.unpack('<d', b5[8:16])[0]
                    if 0.5 <= diam64 <= 10.0:
                        diameter_mm = float(diam64)
                        diameter_note = 'float64 LE'
                # if not found, try float32 LE (same plausible range)
                if diameter_mm is None and len(b5) >= 12:
                    diam32 = struct.unpack('<f', b5[8:12])[0]
                    if 0.5 <= diam32 <= 10.0:
                        diameter_mm = float(diam32)
                        diameter_note = 'float32 LE'
                # last resort: uint16 at offset 8 interpreted as hundredths (val/100)
                if diameter_mm is None and len(b5) >= 10:
                    raw16 = int.from_bytes(b5[8:10], 'little')
                    if 50 <= raw16 <= 10000:
                        candidate = raw16 / 100.0
                        if 0.5 <= candidate <= 10.0:
                            diameter_mm = candidate
                            diameter_note = 'uint16/100'
            except Exception:
                diameter_mm = None
                diameter_note = None

            if diameter_mm is None or diameter_mm == 0:
                if DEBUG:
                    lprint(f"Block 5 raw data: {b5.hex()}", prompt="[" + color("i", fg="yellow") + "] ")
    except Exception:
        color_info = None
        weight_g = None
        diameter_mm = None
        diameter_note = None

    return material_str, color_info, weight_g, diameter_mm, diameter_note, color_link


# Tag-read helper removed: reading Blocks 4/5 directly from a tag requires the correct keys and
# we no longer support direct tag reads via CLI for this script to avoid misleading output or accidental key disclosure.


def get_material_and_color():
    """Read Block 4 and 5 and return parsed material, color, weight, diameter.

    Prefer reading from the source `.bin` file (the provided dump file). If that
    is not available or cannot be parsed, give a warning and return Nones.

    Block decoding (Block 4: material string; Block 5: color/weight/diameter)
    follows the Bambu Lab RFID Tag Guide:
    https://github.com/Bambu-Research-Group/RFID-Tag-Guide/blob/main/BambuLabRfid.md

    Credit: Bambu Research Group and contributors (used with thanks).
    """
    # First, try reading from the source file (preferred)
    try:
        dump_path = resolve_dump_file(file)
        dump_bytes = read_1k_bytes(dump_path)
        blocks = [dump_bytes[i:i+16] for i in range(0, len(dump_bytes), 16)]
        if len(blocks) >= 6:
            return _parse_b4_b5(blocks[4], blocks[5])
        else:
            lprint("Source dump file does not contain enough blocks to parse material/color.", prompt="[" + color("!", fg="red") + "] ")
    except Exception as e:
        lprint(f"Could not read material/color from source file: {e}", prompt="[" + color("i", fg="yellow") + "] ")

    # Could not parse material/color from source dump; do NOT fallback to tag.
    lprint("Could not read material/color from the source dump. Color/material information unavailable; pick a different .bin file or proceed without color metadata.", prompt="[" + color("!", fg="yellow") + "] ")
    return None, None, None, None, None, None


res = p.console('hf mf info')
res_content = p.grabbed_output


found_uid = None
if res == 0 and len(res_content) > 0:
    s = color("ok", fg="green")
    lprint(f" ( {s} )", end='', prompt='')
    lprint(res_content, prompt="[" + color("i", fg="yellow") + "] ")
    for uid in fresh_tag_UIDS:
        if uid in res_content:
            found_uid = uid
            break

    # Distinguish between UID not found and UID found but missing Gen 2 capability (respect SKIP_GEN2)
    if not found_uid:
        lprint(f"None of UIDs {fresh_tag_UIDS} found in `hf mf info` output. Is the tag in range and the reader connected?", prompt="[" + color("!", fg="red") + "] ")
        if DEBUG:
            lprint(f"hf mf info output:\n{res_content}", prompt="[" + color("i", fg="yellow") + "] ")
    elif not SKIP_GEN2 and "Magic capabilities... Write Once / FUID" not in res_content:
        lprint(f"UID {found_uid} found but tag does NOT advertise Gen 2 capabilities. Use --skip-gen2 to override (not recommended). Aborting.", prompt="[" + color("!", fg="red") + "] ")
        if DEBUG:
            lprint(f"hf mf info output:\n{res_content}", prompt="[" + color("i", fg="yellow") + "] ")
    else:
        if SKIP_GEN2:
            lprint(f"UID {found_uid} found in output. Skipping Gen 2 capability check as requested.", prompt="[" + color("i", fg="yellow") + "] ")
        else:
            lprint(f"UID {found_uid} found in output and supports Gen 2.", prompt="[" + color("✓", fg="green") + "] ")

        # Ask user to confirm keyfile before proceeding
        lprint(f"Keyfile to be used for final dump: {keyfile}", prompt="[" + color("i", fg="yellow") + "] ")

        material_str, color_info, weight_g, diameter_mm, diameter_note, color_link = get_material_and_color()

        lprint(f"Material: {material_str if material_str else 'unknown'}", prompt="[" + color("i", fg="yellow") + "] ")
        lprint(f"Color (RGBA): {color_info if color_info else 'unknown'}", prompt="[" + color("i", fg="yellow") + "] ")
        if color_link:
            lprint(f"Color reference: {color_link}", prompt="[" + color("i", fg="yellow") + "] ")
        if weight_g is not None:
            lprint(f"Spool weight: {weight_g} g", prompt="[" + color("i", fg="yellow") + "] ")
        if diameter_mm is not None:
            if diameter_note:
                lprint(f"Filament diameter: {diameter_mm:.3f} mm ({diameter_note})", prompt="[" + color("i", fg="yellow") + "] ")
            else:
                lprint(f"Filament diameter: {diameter_mm:.3f} mm", prompt="[" + color("i", fg="yellow") + "] ")

        # Final user confirmation before writes
        user_confirm = input("Press Enter to proceed with writes, or Ctrl+C to abort: ")

        # Proceed with further operations if needed
        try:
            dump_path = resolve_dump_file(file)
            dump_bytes = read_1k_bytes(dump_path)
            lprint(f"Read {len(dump_bytes)} bytes from {dump_path}", prompt="[" + color("✓", fg="green") + "] ")

            blocks = [dump_bytes[i:i+16].hex() for i in range(0, len(dump_bytes), 16)]

            # Pre-check: ensure all blocks are readable with default key FFFFFFFFFFFF
            lprint("Checking access to all blocks with default key FFFFFFFFFFFF...", prompt="[" + color("i", fg="yellow") + "] ")
            for i in range(len(blocks)):
                success, out = read_block_with_retries(i)
                print(out)
                if success:
                    lprint(f"Can read block {i} with default key.", prompt="[" + color("✓", fg="green") + "] ")
                else:
                    lprint(f"Cannot read block {i} with default key FFFFFFFFFFFF. Aborting. Ensure you have the correct key or adjust the script.", prompt="[" + color("!", fg="red") + "] ")
                    raise Exception(f"Access check failed for block {i}")

            # write block 0 (with retries)
            lprint(f"Writing Block 0 with data: {blocks[0]}", prompt="[" + color("i", fg="yellow") + "] ")
            success, res_block0_ouput = write_block_with_retries(0, blocks[0], force=True)
            print(res_block0_ouput)

            if success:
                lprint(f"Written Block 0: {res_block0_ouput}", prompt="[" + color("✓", fg="green") + "] ")
            else:
                lprint(f"Failed to write Block 0 after {RETRIES} attempts: {res_block0_ouput}", prompt="[" + color("!", fg="red") + "] ")
                raise Exception("Block 0 write failed")

            lprint("Proceeding to write data blocks...", prompt="[" + color("i", fg="yellow") + "] ")

            # Write data blocks
            for i, blk in enumerate(blocks):
                if i == 0 or is_trailer(i):
                    continue
                lprint(f"Writing Data Block {i} with data: {blk}", prompt="[" + color("i", fg="yellow") + "] ")
                success, res_data_block_output = write_block_with_retries(i, blk, force=False)

                print(res_data_block_output)
                if success:
                    lprint(f"Written Data Block {i}: {res_data_block_output}", prompt="[" + color("✓", fg="green") + "] ")
                else:
                    lprint(f"Failed to write Data Block {i} after {RETRIES} attempts: {res_data_block_output}", prompt="[" + color("!", fg="red") + "] ")
                    raise Exception(f"Data Block {i} write failed")

            lprint("Proceeding to write sector trailers...", prompt="[" + color("i", fg="yellow") + "] ")
            # Write sector trailers
            for i, blk in enumerate(blocks):
                if is_trailer(i):
                    # Extract NEW key from trailer block data (first 12 hex chars = 6 bytes)
                    # Write with default FFFFFFFFFFFF, verify read with the new key
                    new_trailer_key = blk[:12].upper()
                    lprint(f"Writing Trailer Block {i} with data: {blk}", prompt="[" + color("i", fg="yellow") + "] ")
                    lprint(f"  New key (extracted from first 12 hex chars): {new_trailer_key}", prompt="[" + color("i", fg="yellow") + "] ")

                    # Build the commands that would be executed
                    write_cmd = f'hf mf wrbl --force --blk {i} -k FFFFFFFFFFFF -a -d {blk}'
                    read_cmd_old = f'hf mf rdbl --blk {i} -a -k FFFFFFFFFFFF'
                    read_cmd_new = f'hf mf rdbl --blk {i} -a -k {new_trailer_key}'

                    if ECHO_TRAILER:
                        lprint("Echo mode enabled for trailer blocks; not executing write. Commands below:", prompt="[" + color("i", fg="yellow") + "] ")
                        lprint(f"WRITE (uses old key FFFFFFFFFFFF): {write_cmd}", prompt="[" + color("=", fg="yellow") + "] ")
                        lprint(f"NOTE: verification will be skipped for trailer writes in this test mode.", prompt="[" + color("=", fg="yellow") + "] ")
                        # Only echo the first trailer for testing
                        break

                    # Perform the write for the first trailer only and skip verification
                    success, res_trailer_block_output = write_block_with_retries(i, blk, force=True, write_key="FFFFFFFFFFFF", verify_key=new_trailer_key, skip_verify=True)

                    print(res_trailer_block_output)
                    if success:
                        lprint(f"Written Trailer Block {i}: {res_trailer_block_output}", prompt="[" + color("✓", fg="green") + "] ")
                    else:
                        lprint(f"Failed to write Trailer Block {i} after {RETRIES} attempts: {res_trailer_block_output}", prompt="[" + color("!", fg="red") + "] ")
                        raise Exception(f"Trailer Block {i} write failed")


            # After successful writes, run final dump using keyfile
            lprint(f"All writes completed successfully. Running final dump with keyfile: {keyfile}", prompt="[" + color("i", fg="yellow") + "] ")
            res_dump = p.console(f'hf mf dump --ns --key "{keyfile}"')
            out_dump = p.grabbed_output
            print(out_dump)
            if res_dump == 0:
                lprint(f"Final dump succeeded using keyfile {keyfile}", prompt="[" + color("✓", fg="green") + "] ")
            else:
                lprint(f"Final dump failed with keyfile {keyfile}: {out_dump}", prompt="[" + color("!", fg="red") + "] ")

        except Exception as e:
            lprint(str(e), prompt="[" + color("!", fg="red") + "] ")
            raise

else:
    lprint(f"`hf mf info` failed (code {res}). Ensure proxmark is connected and a tag is in range.", prompt="[" + color("!", fg="red") + "] ")
    if DEBUG:
        lprint(f"hf mf info output:\n{res_content}", prompt="[" + color("i", fg="yellow") + "] ")
