# STEP 3: WRITE SECTOR TRAILERS
# WARNING: THIS LOCKS KEYS & ACCESS BITS
# MAKE SURE STEPS 1 AND 2 WERE VERIFIED

hf mf wrbl --force --blk 3 -k FFFFFFFFFFFF -a -d 324ac23fe39b87878769ac6610915ee6
hf mf wrbl --force --blk 7 -k FFFFFFFFFFFF -a -d 2d4270474ee387878769ea9137842357
hf mf wrbl --force --blk 11 -k FFFFFFFFFFFF -a -d 86465faf39a68787876993855f3d5b72
hf mf wrbl --force --blk 15 -k FFFFFFFFFFFF -a -d bed4f3041c8787878769989da79b6aa1
hf mf wrbl --force --blk 19 -k FFFFFFFFFFFF -a -d d1876ab32c1187878769a63b2b576447
hf mf wrbl --force --blk 23 -k FFFFFFFFFFFF -a -d 7c971eaf06978787876913ec7e19e829
hf mf wrbl --force --blk 27 -k FFFFFFFFFFFF -a -d aefa413a987087878769a4518f830d8e
hf mf wrbl --force --blk 31 -k FFFFFFFFFFFF -a -d acbc5b2071f487878769b948ea84df3b
hf mf wrbl --force --blk 35 -k FFFFFFFFFFFF -a -d 9b9d35294acb87878769bc7815ec1539
hf mf wrbl --force --blk 39 -k FFFFFFFFFFFF -a -d ba1b8bb9dffe87878769db87d6faefa2
hf mf wrbl --force --blk 43 -k FFFFFFFFFFFF -a -d 6beeee4ddf39878787696a07b42e7094
hf mf wrbl --force --blk 47 -k FFFFFFFFFFFF -a -d 1e44b794414087878769674ccdbca6ac
hf mf wrbl --force --blk 51 -k FFFFFFFFFFFF -a -d 2ac86f6ae83987878769b8d6c418b546
hf mf wrbl --force --blk 55 -k FFFFFFFFFFFF -a -d a09511c4666e87878769304d1138f88d
hf mf wrbl --force --blk 59 -k FFFFFFFFFFFF -a -d 9de3e43e55ed878787699a5915dc4318
hf mf wrbl --force --blk 63 -k FFFFFFFFFFFF -a -d 20cb1ace211b87878769943a4f5a9ff5