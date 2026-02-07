# STEP 2: Write data blocks
# VERIFY DATA BEFORE PROCEEDING TO STEP 3

hf mf wrbl --force --blk 1 -k FFFFFFFFFFFF -a -d 4130302d573100004746413030000000
hf mf wrbl --force --blk 2 -k FFFFFFFFFFFF -a -d 504c4100000000000000000000000000
hf mf wrbl --force --blk 4 -k FFFFFFFFFFFF -a -d 504c4120426173696300000000000000
hf mf wrbl --force --blk 5 -k FFFFFFFFFFFF -a -d ffffffffe80300000000e03f00000000
hf mf wrbl --force --blk 6 -k FFFFFFFFFFFF -a -d 3700080000000000e600be0000000000
hf mf wrbl --force --blk 8 -k FFFFFFFFFFFF -a -d 34218813f401e8030000003fcdcc4c3e
hf mf wrbl --force --blk 9 -k FFFFFFFFFFFF -a -d 94cd991ad30144149345032350120740
hf mf wrbl --force --blk 10 -k FFFFFFFFFFFF -a -d 00000000e11900000000000000000000
hf mf wrbl --force --blk 12 -k FFFFFFFFFFFF -a -d 323032355f30315f30315f31355f3437
hf mf wrbl --force --blk 13 -k FFFFFFFFFFFF -a -d 32355f30315f30315f31350000000000
hf mf wrbl --force --blk 14 -k FFFFFFFFFFFF -a -d 000000004a0100000000000000000000
hf mf wrbl --force --blk 16 -k FFFFFFFFFFFF -a -d 02000100000000000000000000000000
hf mf wrbl --force --blk 17 -k FFFFFFFFFFFF -a -d 00000000000000000000000000000000
hf mf wrbl --force --blk 18 -k FFFFFFFFFFFF -a -d 00000000000000000000000000000000
hf mf wrbl --force --blk 20 -k FFFFFFFFFFFF -a -d 00000000000000000000000000000000
hf mf wrbl --force --blk 21 -k FFFFFFFFFFFF -a -d 00000000000000000000000000000000
hf mf wrbl --force --blk 22 -k FFFFFFFFFFFF -a -d 00000000000000000000000000000000
hf mf wrbl --force --blk 24 -k FFFFFFFFFFFF -a -d 00000000000000000000000000000000
hf mf wrbl --force --blk 25 -k FFFFFFFFFFFF -a -d 00000000000000000000000000000000
hf mf wrbl --force --blk 26 -k FFFFFFFFFFFF -a -d 00000000000000000000000000000000
hf mf wrbl --force --blk 28 -k FFFFFFFFFFFF -a -d 00000000000000000000000000000000
hf mf wrbl --force --blk 29 -k FFFFFFFFFFFF -a -d 00000000000000000000000000000000
hf mf wrbl --force --blk 30 -k FFFFFFFFFFFF -a -d 00000000000000000000000000000000
hf mf wrbl --force --blk 32 -k FFFFFFFFFFFF -a -d 00000000000000000000000000000000
hf mf wrbl --force --blk 33 -k FFFFFFFFFFFF -a -d 00000000000000000000000000000000
hf mf wrbl --force --blk 34 -k FFFFFFFFFFFF -a -d 00000000000000000000000000000000
hf mf wrbl --force --blk 36 -k FFFFFFFFFFFF -a -d 00000000000000000000000000000000
hf mf wrbl --force --blk 37 -k FFFFFFFFFFFF -a -d 00000000000000000000000000000000
hf mf wrbl --force --blk 38 -k FFFFFFFFFFFF -a -d 00000000000000000000000000000000
hf mf wrbl --force --blk 40 -k FFFFFFFFFFFF -a -d 01000000000000000000000000000000
hf mf wrbl --force --blk 41 -k FFFFFFFFFFFF -a -d 00000000000000000000000000000000
hf mf wrbl --force --blk 42 -k FFFFFFFFFFFF -a -d 6fec9d6905b0e05f7420ab9aa707175f
hf mf wrbl --force --blk 44 -k FFFFFFFFFFFF -a -d 96c444e38c242d1ae3219b0915e0b1d2
hf mf wrbl --force --blk 45 -k FFFFFFFFFFFF -a -d 0e4eb5060e2874574c05132617ce98e6
hf mf wrbl --force --blk 46 -k FFFFFFFFFFFF -a -d 8c55a909f74db83e4fe61b5e76bb51f6
hf mf wrbl --force --blk 48 -k FFFFFFFFFFFF -a -d 528173bcdc7759d6d52896227d0905ac
hf mf wrbl --force --blk 49 -k FFFFFFFFFFFF -a -d 7a374ae56b488e06b297ca667dd52040
hf mf wrbl --force --blk 50 -k FFFFFFFFFFFF -a -d 1c9fe5bdc595b1e790fb3979d9900421
hf mf wrbl --force --blk 52 -k FFFFFFFFFFFF -a -d 2e7437551527929cb7ddb8fcd493af07
hf mf wrbl --force --blk 53 -k FFFFFFFFFFFF -a -d 9e4398a21a293b8e6568c4fd33298f6d
hf mf wrbl --force --blk 54 -k FFFFFFFFFFFF -a -d 5e69cafbce945a1d979b5bbed585828b
hf mf wrbl --force --blk 56 -k FFFFFFFFFFFF -a -d fc741c301e75f4d87413f52c3b5ce6d9
hf mf wrbl --force --blk 57 -k FFFFFFFFFFFF -a -d 852e56d10d5334a60050715a519db75b
hf mf wrbl --force --blk 58 -k FFFFFFFFFFFF -a -d 71b9ad2b9a1698ac825922ba346b341f
hf mf wrbl --force --blk 60 -k FFFFFFFFFFFF -a -d 9f8891dc7de3b38fb80932c39c101cda
hf mf wrbl --force --blk 61 -k FFFFFFFFFFFF -a -d 558ff37a615f8d283fbe93225bdce6dd
hf mf wrbl --force --blk 62 -k FFFFFFFFFFFF -a -d 8c222dc14bb7cb888fea1332b3d18b04

# Optional verification
hf mf dump