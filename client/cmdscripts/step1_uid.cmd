# STEP 1: Unlock magic card and write block 0
# VERIFY UID/BCC AFTER THIS STEP

hf mf csetuid -u
hf mf wrbl --force --blk 0 -k FFFFFFFFFFFF -a -d e4e447d19608040004520ae14f5a2890
hf mf rdbl --blk 0