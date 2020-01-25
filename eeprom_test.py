
import struct

def CRC(data):
    crc = 0xFF
    for i in range(len(data)):
        crc ^= data[i]
        for j in range(8):
            if(crc & 0x80):
                crc = (crc << 1) ^ 0x07
            else:
                crc = (crc << 1)
    return (0xFF & crc)

path = 'out.bin'
d = [
    # PDI 制御レジスタ[0x0140]
    0x80, 
    # ESC コンフィグレーション レジスタ [0x0141]
    0x01, 
    # PDI コンフィグレーション レジスタ デジタル I/O モード [0x0150]
    0x00, 
    # SYNC/LATCH PDI コンフィグレーション レジスタ [0982h-0983h)]
    0xFF, 
    # SyncSignal パルス長レジスタ [0982h-0983h]
    0x00, 
    0x00, 
    # 拡張 PDI コンフィグレーション レジスタ [0152h-0153h]
    # SPI モード
    0xFF,
    0x00,
    # 構成済みステーション エイリアス レジスタ [0012h-0013h]
    0x00, 
    0x00, 
    # MII 管理制御 / ステータス レジスタ [0510h-0511h]
    0x00, 
    # ASIC コンフィグレーション レジスタ [0142h-0143h]
    0x00, 
    # 予約レジスタ [0114h-0145h]
    0x00, 
    0x00
]


f = open(path,"wb")
for i in range(len(d)):
    f.write(struct.pack("B", d[i]))
f.write(struct.pack("H",CRC(d)))


# Vendor ID [0x08-0x09]
f.write(struct.pack("H",0x0A68))
f.write(struct.pack("H",0x0000))
# Product Code [0x0A-0x0B]
f.write(struct.pack("H",0x0001))
f.write(struct.pack("H",0x0000))
# Revision Number [0x0C-0x0D]
f.write(struct.pack("H",0x0001))
f.write(struct.pack("H",0x0000))
# Serial Number [0x0E-0x0F]
f.write(struct.pack("H",0x0001))
f.write(struct.pack("H",0x0000))
# Reserved [0x10-0x13]
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
# Bootstrap Receive Mailbox Offset [0x14]
f.write(struct.pack("H",0x0000))
# Bootstrap Receive Mailbox Size [0x15]
f.write(struct.pack("H",0x0000))
# Bootstrap Send Mailbox Offset [0x16]
f.write(struct.pack("H",0x0000))
# Bootstrap Send Mailbox Size [0x17]
f.write(struct.pack("H",0x0000))

# Standard Receive Mailbox Offset [0x18]
f.write(struct.pack("H",0x0000))
# Standard Receive Mailbox Size [0x19]
f.write(struct.pack("H",0x0000))
# Standard Send Mailbox Offset [0x1A]
f.write(struct.pack("H",0x0000))
# Standard Send Mailbox Size [0x1B]
f.write(struct.pack("H",0x0000))
# Mailbox Protocol [0x1C]
f.write(struct.pack("H",0x0000))

# Reserved [0x1D-0x1F]
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))

# Vendor specific [0x20-0x22]
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))

# Reserved [0x23-0x27]
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))

# Additional ESC configuration [0x28-0x2F]
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))

# Reserved [0x30-0x3D]
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
f.write(struct.pack("H",0x0000))
# Size [0x3E]
f.write(struct.pack("H",0x000F))
# Version [0x3F]
f.write(struct.pack("H",0x0001))


#-----------------------------------------#
# STRINGS CATEGORIES
#-----------------------------------------#
DATA = [b"ArtifactNoise-DIGIO",b"ArtifactNoise",b"Output x16"]

f.write(struct.pack("H",10))            # STRINGS TYPE
Size = 1
for i in range(len(DATA)):
    Size += len(DATA[i])+1
f.write(struct.pack("H",Size))          # WORD Length
f.write(struct.pack("B",len(DATA)))     # Strings length
for n in range(len(DATA)):
    f.write(struct.pack("B",len(DATA[n])))    # String length
    for i in range(0,len(DATA[n])):
        f.write(struct.pack("B",DATA[n][i]))    # String Data

#-----------------------------------------#
# General CATEGORIES
#-----------------------------------------#

f.write(struct.pack("H",30))            # GENERAL TYPE
f.write(struct.pack("H",0x0F))          # WORD Length

f.write(struct.pack("B",0x01))     # GroupIdx
f.write(struct.pack("B",0x02))     # ImgIdx
f.write(struct.pack("B",0x01))     # OrderIdx
f.write(struct.pack("B",0x00))     # NameIdx
f.write(struct.pack("B",0x00))     # Reserved
f.write(struct.pack("B",0x00))     # CoE Details
f.write(struct.pack("B",0x00))     # FoE Details
f.write(struct.pack("B",0x00))     # EoE Details
f.write(struct.pack("B",0x00))     # SoEChannels
f.write(struct.pack("B",0x00))     # DS402Channels
f.write(struct.pack("B",0x00))     # SysmanClass

f.write(struct.pack("B",0x00))     # Flags
f.write(struct.pack("B",0x00))     # CurrentOnEBus
f.write(struct.pack("B",0x00))     # GroupIdx
f.write(struct.pack("B",0x00))     # Reserved1
f.write(struct.pack("B",0x00))     # Reserved1
f.write(struct.pack("H",0x00))     # Physical Port
f.write(struct.pack("H",0x00))     # Physical Memory Address
for i in range(12):
    f.write(struct.pack("B",0x00))     # Reserved2

f.close()


path = 'out.bin'
f = open(path,"rb")
data = f.read()
wordaddr = 0
addr = 0
for i in range(0,len(data),2):
    try:
        print("0x%02X:0x%04X" % (wordaddr,data[i]|data[i+1]<<8))
    except IndexError :
        print("0x%02X:0x%04X" % (wordaddr,data[i]))
    wordaddr = wordaddr+1
    addr = addr+2
f.close()
    