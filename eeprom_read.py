from pyEtherCAT import MasterEtherCAT
import time
import os
import struct

cat = MasterEtherCAT.MasterEtherCAT("eth0")
cat.ADP = 0x000000

cat.EEPROM_SetUp(0x0000)

path = 'read.bin'
f = open(path,"wb")
# EEPROM 読み出し
for i in range(0x0200):
    cat.EEPROM_AddrSet(i)
    cat.EEPROM_Stasus(enable=0x00, command=0x01)
    (DATA, WKC) = cat.EEPROM_Read()
    print("READ[0x{:04x}]= 0x{:04x}".format(i,DATA[0] | DATA[1] << 8 ))
    f.write(struct.pack("H", (DATA[0] | DATA[1] << 8) ))
time.sleep(1)
f.close()

