### Helper to write Gen2 FUID tags
## Written by Shawner18 much help from existing examples
import argparse
import pm3
import time

try:
    # pip install ansicolors
    from colors import color
except ModuleNotFoundError:
    def color(s, fg=None):
        _ = fg
        return str(s)

parser = argparse.ArgumentParser(description='A script to help with raw USCUID-UL commands. Out of everything until -s, only one functionality can be used at a time, prioritised in order listed below.')
parser.add_argument('-f', '--file', type=str, help='Path to bin file to write')
parser.add_argument('-r', '--retries', type=int, default=3, help='Number of times to attempt writes')
parser.add_argument('--skip-gen2', action='store_true', default=False, help='Skip checking for Gen 2 capability (use with caution)')

args = parser.parse_args()
file = args.file if args.file else "Bambu-Lab-RFID-Library\\PLA\\PLA Basic\\Black\\F41347D4\\hf-mf-F41347D4-dump.bin"


def read_1k_bytes(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    if len(data) != 1024:
        raise ValueError(f"File length is {len(data)} bytes, expected 1024 bytes (1k).")
    return data


p = pm3.pm3()

fresh_tag_UIDS = ["3A D8 2D AD", "D5 49 42 1E", "F4 13 47 D4"]
RETRIES = args.retries if hasattr(args, 'retries') else 3
SKIP_GEN2 = args.skip_gen2 if hasattr(args, 'skip_gen2') else True
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

def write_block_with_retries(blk_num, data_hex, force=False):
    """Attempt to write a block up to RETRIES times, verifying after each write."""
    cmd_force = '--force ' if force else ''
    last_out = ''
    for attempt in range(1, RETRIES + 1):
        cmd = f'hf mf wrbl {cmd_force}--blk {blk_num} -k FFFFFFFFFFFF -a -d {data_hex}'
        res = p.console(cmd)
        out = p.grabbed_output
        last_out = out
        if SIMULATE:
            lprint("SIMULATE mode enabled, skipping actual write operations.", prompt="[" + color("i", fg="yellow") + "] ")
            return True, "Simulated write success."
        if res == 0 and "Write ( fail )" not in out:
            # verify read back
            res_verify = p.console(f'hf mf rdbl --blk {blk_num}')
            out_verify = p.grabbed_output
            if res_verify == 0 and "Read ( fail )" not in out_verify:
                expected_line = format_block_for_compare(blk_num, data_hex)
                if expected_line in out_verify:
                    return True, out + "\n" + out_verify
                else:
                    lprint(f"Verification mismatch on block {blk_num}. Expected: {expected_line}. Got: {out_verify}", prompt="[" + color("!", fg="red") + "] ")
            else:
                lprint(f"Read failed after write for block {blk_num}: {out_verify}", prompt="[" + color("!", fg="red") + "] ")
        else:
            lprint(f"Write failed for block {blk_num}: {out}", prompt="[" + color("!", fg="red") + "] ")
        if attempt < RETRIES:
            lprint(f"Retrying block {blk_num} (attempt {attempt+1}/{RETRIES})...", prompt="[" + color("i", fg="yellow") + "] ")
            time.sleep(1)  # brief pause before retry
    return False, last_out


def read_block_with_retries(blk_num):
    """Attempt to read a block up to RETRIES times."""
    last_out = ''
    for attempt in range(1, RETRIES + 1):
        res = p.console(f'hf mf rdbl --blk {blk_num}')
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

res = p.console('hf mf info')
print(res)
res_content = p.grabbed_output

if res == 0 and len(res_content) > 0:
    s = color("ok", fg="green")
    lprint(f" ( {s} )", end='', prompt='')
    print(res_content)
    
    # Verify if any fresh_tag_UID is present in grabbed_output
    found_uid = None
    for uid in fresh_tag_UIDS:
        if uid in res_content:
            found_uid = uid
            break

    # Distinguish between UID not found and UID found but missing Gen 2 capability (respect SKIP_GEN2)
    if not found_uid:
        lprint(f"None of UIDs {fresh_tag_UIDS} found in `hf mf info` output. Is the tag in range and the reader connected?", prompt="[" + color("!", fg="red") + "] ")
        if DEBUG:
            lprint(f"hf mf info output:\n{res_content}", prompt="[" + color("i", fg="yellow") + "] ")
    elif not SKIP_GEN2 and "Magic capabilities... Gen 2" not in res_content:
        lprint(f"UID {found_uid} found but tag does NOT advertise Gen 2 capabilities. Use --skip-gen2 to override (not recommended). Aborting.", prompt="[" + color("!", fg="red") + "] ")
        if DEBUG:
            lprint(f"hf mf info output:\n{res_content}", prompt="[" + color("i", fg="yellow") + "] ")
    else:
        if SKIP_GEN2:
            lprint(f"UID {found_uid} found in output. Skipping Gen 2 capability check as requested.", prompt="[" + color("i", fg="yellow") + "] ")
        else:
            lprint(f"UID {found_uid} found in output and supports Gen 2.", prompt="[" + color("✓", fg="green") + "] ")

        # Proceed with further operations if needed
        try:
            dump_bytes = read_1k_bytes(file)
            lprint(f"Read {len(dump_bytes)} bytes from {file}", prompt="[" + color("✓", fg="green") + "] ")

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
                    success, res_trailer_block_output = write_block_with_retries(i, blk, force=True)

                    print(res_trailer_block_output)
                    if success:
                        lprint(f"Written Trailer Block {i}: {res_trailer_block_output}", prompt="[" + color("✓", fg="green") + "] ")
                    else:
                        lprint(f"Failed to write Trailer Block {i} after {RETRIES} attempts: {res_trailer_block_output}", prompt="[" + color("!", fg="red") + "] ")
                        raise Exception(f"Trailer Block {i} write failed")

        except Exception as e:
            lprint(str(e), prompt="[" + color("!", fg="red") + "] ")
            raise

else:
    s = color("fail", fg="red")
    lprint(f" ( {s} ) `hf mf info` returned no output or failed. Ensure proxmark is connected and a tag is in range.", end='', prompt='')
    if DEBUG:
        lprint(f"hf mf info output:\n{res_content}", prompt="[" + color("i", fg="yellow") + "] ")
