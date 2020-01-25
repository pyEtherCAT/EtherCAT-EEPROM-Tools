
import struct
import json


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

path = "eeprom_config.json"
f = open(path,"r")
jdata = json.load(f) 

print(jdata["Lisence"])

d = [
    # PDI 制御レジスタ[0x0140]
    int(jdata["ESC Info"]["PDI Control"]["PDI ControlRegister"],16), 
    # ESC コンフィグレーション レジスタ [0x0141]
    int(jdata["ESC Info"]["PDI Control"]["ESC Configuration Register"],16), 
    # PDI コンフィグレーション レジスタ デジタル I/O モード [0x0150]
    int(jdata["ESC Info"]["PDI Configuration"]["PDI Configuration Register"],16), 
    # SYNC/LATCH PDI コンフィグレーション レジスタ [0982h-0983h)]
    int(jdata["ESC Info"]["PDI Configuration"]["Sync/Latch PDI Configuration Register"],16), 
    # SyncSignal パルス長レジスタ [0982h-0983h]
    (0x00FF & int(jdata["ESC Info"]["Pulse Length of SyncSignals Register"],16))>>0, 
    (0xFF00 & int(jdata["ESC Info"]["Pulse Length of SyncSignals Register"],16))>>8, 
    # 拡張 PDI コンフィグレーション レジスタ [0152h-0153h] SPI モード
    (0x00FF & int(jdata["ESC Info"]["Extended PDI Configuration Register"],16))>>0, 
    (0xFF00 & int(jdata["ESC Info"]["Extended PDI Configuration Register"],16))>>8, 
    # 構成済みステーション エイリアス レジスタ [0012h-0013h]
    (0x00FF & int(jdata["ESC Info"]["Configured Station Alias Register"],16))>>0, 
    (0xFF00 & int(jdata["ESC Info"]["Configured Station Alias Register"],16))>>8, 
    # MII 管理制御 / ステータス レジスタ [0510h-0511h]
    int(jdata["ESC Info"]["Other INFO"]["MII Management Control/Status Register"],16), 
    # ASIC コンフィグレーション レジスタ [0142h-0143h]
    int(jdata["ESC Info"]["Other INFO"]["ASIC Configuration Register"],16), 
    # 予約レジスタ [0114h-0145h]
    0x00, 0x00
]

path = 'out.bin'
f = open(path,"wb")
for i in range(len(d)):
    f.write(struct.pack("B", d[i]))
f.write(struct.pack("H",CRC(d)))
print('CRC:0x{:04X}'.format(CRC(d)))

# Vendor ID [0x08-0x09]
f.write(struct.pack("I",int(jdata["ESC Info"]["Vendor ID"],16)))
# Product Code [0x0A-0x0B]
f.write(struct.pack("I",(int(jdata["ESC Info"]["Product Code"],16))))
# Revision Number [0x0C-0x0D]
f.write(struct.pack("I",(int(jdata["ESC Info"]["Revision Number"],16))))
# Serial Number [0x0E-0x0F]
f.write(struct.pack("I",(int(jdata["ESC Info"]["Serial Number"],16))))
# Reserved [0x10-0x13]
for i in range(2):
    f.write(struct.pack("H",0x0000))
# Bootstrap Receive Mailbox Offset [0x14]
f.write(struct.pack("I",(int(jdata["ESC Info"]["Bootstrap Receive Mailbox Offset"],16))))
# Bootstrap Receive Mailbox Size [0x15]
f.write(struct.pack("I",(int(jdata["ESC Info"]["Bootstrap Receive Mailbox Size"],16))))
# Bootstrap Send Mailbox Offset [0x16]
f.write(struct.pack("I",(int(jdata["ESC Info"]["Bootstrap Send Mailbox Offset"],16))))
# Bootstrap Send Mailbox Size [0x17]
f.write(struct.pack("I",(int(jdata["ESC Info"]["Bootstrap Send Mailbox Size"],16))))
# Standard Receive Mailbox Offset [0x18]
f.write(struct.pack("I",(int(jdata["ESC Info"]["Standard Receive Mailbox Offset"],16))))
# Standard Receive Mailbox Size [0x19]
f.write(struct.pack("I",(int(jdata["ESC Info"]["Standard Receive Mailbox Size"],16))))
# Standard Send Mailbox Offset [0x1A]
f.write(struct.pack("I",(int(jdata["ESC Info"]["Standard Send Mailbox Offset"],16))))
# Standard Send Mailbox Size [0x1B]
f.write(struct.pack("I",(int(jdata["ESC Info"]["Standard Send Mailbox Size"],16))))
# Mailbox Protocol [0x1C]
f.write(struct.pack("I",(int(jdata["ESC Info"]["Mailbox Protocol"],16))))
# Reserved [0x1D-0x1F]
for i in range(2):
    f.write(struct.pack("H",0x0000))
# Vendor specific [0x20-0x22]
for i in range(2):
    f.write(struct.pack("H",0x0000))
# Reserved [0x23-0x27]
for i in range(4):
    f.write(struct.pack("H",0x0000))
# Additional ESC configuration [0x28-0x2F]
for i in range(6):
    f.write(struct.pack("H",0x0000))
# Reserved [0x30-0x3D]
for i in range(12):
    f.write(struct.pack("H",0x0000))
# Size [0x3E]
f.write(struct.pack("H",(int(jdata["ESC Info"]["EEPROM Size"],16))))
# Version [0x3F]EEPROM 
f.write(struct.pack("H",(int(jdata["ESC Info"]["Version"],16))))


#-----------------------------------------#
# STRINGS CATEGORIES
#-----------------------------------------#
#DATA = [b"ArtifactNoise-DIGIO",b"ArtifactNoise",b"Output x16"]
DATA = jdata["Categories"]["Strings"]
for i in range(len(jdata["Categories"]["Strings"])):
    DATA[i] = jdata["Categories"]["Strings"][i].encode('utf-8')
f.write(struct.pack("H",10))            # STRINGS TYPE
Size = 1
for i in range(len(DATA)):
    Size += len(DATA[i])+1
print("WORD Length:0x%04X" % Size)
print("Strings length:0x%02X" % len(DATA))
f.write(struct.pack("H",Size))          # WORD Length
f.write(struct.pack("B",len(DATA)))     # Strings length
for n in range(len(DATA)):
    f.write(struct.pack("B",len(DATA[n])))    # String length
    print("String length:0x%02X" % len(DATA[n]))
    for i in range(0,len(DATA[n])):
        f.write(struct.pack("B",DATA[n][i]))    # String Data

#-----------------------------------------#
# General CATEGORIES
#-----------------------------------------#

f.write(struct.pack("H",30))            # GENERAL TYPE
f.write(struct.pack("H",0x0F))          # WORD Length

f.write(struct.pack("B",int(jdata["Categories"]["General"]["GroupIdx"],10)))     # GroupIdx
f.write(struct.pack("B",int(jdata["Categories"]["General"]["ImgIdx"],10)))     # ImgIdx
f.write(struct.pack("B",int(jdata["Categories"]["General"]["OrderIdx"],10)))     # OrderIdx
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



