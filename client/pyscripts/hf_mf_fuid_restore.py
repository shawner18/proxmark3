### Crappy helper script for USCUID-UL, v0.2.4.2
## Written and tested by Eltrick
# It is recommended that you are able to backdoor read main blocks
# in case changing from one type to another messes up keys/pwd
# unless you know what you're doing.

## For the uninitiated, the keys are stored in the following locations
## per the corresponding datasheets
# UL11     - PWD - page 18d
# UL21     - PWD - page 39d
# UL-C     - KEY - pages 44d to 47d
# NTAG 213 - PWD - page 43d
# NTAG 215 - PWD - page 133d
# NTAG 216 - PWD - page 229d

import argparse
import pm3

try:
    # pip install ansicolors
    from colors import color
except ModuleNotFoundError:
    def color(s, fg=None):
        _ = fg
        return str(s)

print('test')

HEX_DIGITS = "0123456789ABCDEF"
MEMORY_CONFIG = { "C3": "UL11", "3C": "UL21", "00": "UL-C", "A5": "NTAG 213", "5A": "NTAG 215", "AA": "NTAG 216", "55": "Unknown IC with 238 pages" }
KNOWN_CONFIGS = ["C30004030101000B03", "3C0004030101000E03", "000000000000000000", "A50004040201000F03", "5A0004040201001103", "AA0004040201001303"]

parser = argparse.ArgumentParser(description='A script to help with raw USCUID-UL commands. Out of everything until -s, only one functionality can be used at a time, prioritised in order listed below.')
parser.add_argument('-r', '--read', action='store_true', help='Read and parse config from card')
parser.add_argument('-t', '--type', help='Type to change to: 1-UL11; 2-UL21; 3-UL-C; 4-NTAG213; 5-NTAG215; 6-NTAG216')
parser.add_argument('-c', '--cfg', help='Config to write')
parser.add_argument('-p', '--parse', help='Config to parse')
parser.add_argument('-b', '--bdr', help='Page num to read with backdoor')
parser.add_argument('-w', '--wbd', help='First page num to write with backdoor')
parser.add_argument('-u', '--uid', help='New UID to write')
parser.add_argument('-d', '--data', help='Page data to write if using -w, multiple of 4 bytes')
parser.add_argument('-s', '--sig', help='Signature to write with backdoor')
parser.add_argument('--gen1a', action='store_true', help='Use gen1a (40/43) magic wakeup')
parser.add_argument('--gdm', action='store_true', help='Use gdm alt (20/23) magic wakeup')

args = parser.parse_args()
card_config = args.read
ul_type = args.type
config = args.cfg
parse = args.parse
backdoor_block = args.bdr
write_backdoor = args.wbd
data = args.data
signature = args.sig
gen1a = args.gen1a
alt = args.gdm
uid = args.uid

field_on = False
p = pm3.pm3()

ERROR = "[" + color("-", "red") + "] "
SUCCESS = "[" + color("+", "green") + "] "

def lprint(s='',  end='\n', flush=False, prompt="[" + color("=", fg="yellow") + "] ", log=True):
    """Print and Log.

    globals:
    - logbuffer (RW)
    - logfile (R)
    """
    s = f"{prompt}" + f"\n{prompt}".join(s.split('\n'))
    safe_s = s.encode('utf-8', errors='ignore').decode('utf-8')
    print(safe_s, end=end, flush=flush)


res = p.console('hw status', True)
print(res)

if res == 0:
    s = color("ok", fg="green")
    lprint(f" ( {s} )", end='', prompt='hw status')
else:
    s = color("fail", fg="red")
    lprint(f" ( {s} )", end='', prompt='hw status')

res = p.console('hf mf info', True)
print(res)

if res == 0:
    s = color("ok", fg="green")
    lprint(f" ( {s} )", end='', prompt='')
else:
    s = color("fail", fg="red")
    lprint(f" ( {s} )", end='', prompt='')
