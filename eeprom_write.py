from pyEtherCAT import MasterEtherCAT
import time
import os

cat = MasterEtherCAT.MasterEtherCAT("eth0")
cat.ADP = 0x000000

cat.EEPROM_SetUp(0x0000)
# EEPROM ゼロクリア
print("EEPROM Zero Clear")
for i in range(0x0200):
    cat.EEPROM_AddrSet(i)
    cat.EEPROM_Write(0)
    cat.EEPROM_Stasus(enable=0x01, command=0x02)
    time.sleep(0.01)

path = 'out.bin'
f = open(path,"rb")
data = f.read()
wordaddr = 0
for i in range(0,len(data),2):
    cat.EEPROM_AddrSet(wordaddr)
    try:
        print("0x%02X:0x%04X" % (wordaddr,data[i]|data[i+1]<<8))
        cat.EEPROM_Write(data[i]|data[i+1]<<8)
    except IndexError :
        print("0x%02X:0x%04X" % (wordaddr,data[i]))
        cat.EEPROM_Write(data[i])
    cat.EEPROM_Stasus(enable=0x01, command=0x02)
    wordaddr = wordaddr+1
    time.sleep(0.01)

f.close()

# EEPROM 読み出し
for i in range(0x0050):
    cat.EEPROM_AddrSet(i)
    cat.EEPROM_Stasus(enable=0x00, command=0x01)
    (DATA, WKC) = cat.EEPROM_Read()
    print("READ[0x{:04x}]= 0x{:04x}".format(i, DATA[0] | DATA[1] << 8))

cat.EthereCAT_Reset()
time.sleep(1)

