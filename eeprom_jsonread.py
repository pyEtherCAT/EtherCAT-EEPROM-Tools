
from pyEtherCAT import MasterEtherCAT
import time
import os


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


def word(data,wordaddr):
    return data[wordaddr*2] | data[wordaddr*2+1]<<8

path = 'read.bin'
#path = 'omron_read.bin'
f = open(path,"rb")
data = f.read()
f.close()

path = "eeprom_read.json"
f = open(path,"w")

jdata = {}

jdata["ESC Info"] = {}
jdata["ESC Info"]["PDI Control"] = {}
jdata["ESC Info"]["PDI Configuration"] = {}
jdata["ESC Info"]["Other INFO"] = {}
# PDI 制御レジスタ[0x0140]
jdata["ESC Info"]["PDI Control"]["PDI ControlRegister"] = '0x{:02X}'.format(data[0])
# ESC コンフィグレーション レジスタ [0x0141]
jdata["ESC Info"]["PDI Control"]["ESC Configuration Register"] = '0x{:02X}'.format(data[1])
# PDI コンフィグレーション レジスタ デジタル I/O モード [0x0150]
jdata["ESC Info"]["PDI Configuration"]["PDI Configuration Register"] = '0x{:02X}'.format(data[2])
# SYNC/LATCH PDI コンフィグレーション レジスタ [0982h-0983h)]
jdata["ESC Info"]["PDI Configuration"]["Sync/Latch PDI Configuration Register"] = '0x{:02X}'.format(data[3])
# SyncSignal パルス長レジスタ [0982h-0983h]
jdata["ESC Info"]["Pulse Length of SyncSignals Register"] = '0x{:04X}'.format(data[4]|data[5]<<8)
# 拡張 PDI コンフィグレーション レジスタ [0152h-0153h] SPI モード
jdata["ESC Info"]["Extended PDI Configuration Register"] = '0x{:04X}'.format(data[6]|data[7]<<8)
# 構成済みステーション エイリアス レジスタ [0012h-0013h]
jdata["ESC Info"]["Configured Station Alias Register"] = '0x{:04X}'.format(data[8]|data[9]<<8)
# MII 管理制御 / ステータス レジスタ [0510h-0511h]
jdata["ESC Info"]["Other INFO"]["MII Management Control/Status Register"] = '0x{:02X}'.format(data[10])
# ASIC コンフィグレーション レジスタ [0142h-0143h]
jdata["ESC Info"]["Other INFO"]["ASIC Configuration Register"] = '0x{:02X}'.format(data[11])
# 予約レジスタ [0114h-0145h]
# data[12] 0x00,data[13] 0x00

# CRCデータ
jdata["ESC Info"]["CRC"] = '0x{:04X}'.format(data[14]|data[15]<<8)
# Vendor ID [0x08-0x09]
jdata["ESC Info"]["Vendor ID"] = '0x{:08X}'.format(word(data,0x08)|word(data,0x09)<<16)
# Product Code [0x0A-0x0B]
jdata["ESC Info"]["Product Code"] = '0x{:08X}'.format(word(data,0x0A)|word(data,0x0B)<<16)
# Revision Number [0x0C-0x0D]
jdata["ESC Info"]["Revision Number"] = '0x{:08X}'.format(word(data,0x0C)|word(data,0x0D)<<16)
# Serial Number [0x0E-0x0F]
jdata["ESC Info"]["Serial Number"] = '0x{:08X}'.format(word(data,0x0E)|word(data,0x0F)<<16)
# Bootstrap Receive Mailbox Offset [0x14]
jdata["ESC Info"]["Bootstrap Receive Mailbox Offset"] = '0x{:04X}'.format(word(data,0x14))
# Bootstrap Receive Mailbox Size [0x15]
jdata["ESC Info"]["Bootstrap Receive Mailbox Size"] = '0x{:04X}'.format(word(data,0x15))
# Bootstrap Send Mailbox Offset [0x16]
jdata["ESC Info"]["Bootstrap Send Mailbox Offset"] = '0x{:04X}'.format(word(data,0x16))
# Bootstrap Send Mailbox Size [0x17]
jdata["ESC Info"]["Bootstrap Send Mailbox Size"] = '0x{:04X}'.format(word(data,0x17))
# Standard Receive Mailbox Offset [0x18]
jdata["ESC Info"]["Standard Receive Mailbox Offset"] = '0x{:04X}'.format(word(data,0x18))
# Standard Receive Mailbox Size [0x19]
jdata["ESC Info"]["Standard Receive Mailbox Size"] = '0x{:04X}'.format(word(data,0x19))
# Standard Send Mailbox Offset [0x1A]
jdata["ESC Info"]["Standard Send Mailbox Offset"] = '0x{:04X}'.format(word(data,0x1A))
# Standard Send Mailbox Size [0x1B]
jdata["ESC Info"]["Standard Send Mailbox Size"] = '0x{:04X}'.format(word(data,0x1B))
# Mailbox Protocol [0x1C]
jdata["ESC Info"]["Mailbox Protocol"] = '0x{:04X}'.format(word(data,0x1C))
# Size [0x3E]
jdata["ESC Info"]["EEPROM Size"] = '0x{:04X}'.format(word(data,0x3E))
# Version [0x3F]EEPROM 
jdata["ESC Info"]["Version"] = '0x{:04X}'.format(word(data,0x3F))


jdata["Categories"] = {}
jdata["Categories"]["General"] = {}
base = 0x40*2
#-----------------------------------------#
# STRINGS CATEGORIES
#-----------------------------------------#
if( '0x{:04X}'.format(word(data,int(base/2))) == "0x000A"):
    jdata["Categories"]["WORD Length"] = '0x{:04X}'.format(word(data,0x41))
    jdata["Categories"]["Strings length"] = '0x{:02X}'.format(data[0x42*2])

    StringsLen = data[0x42*2]
    DATA = [0]*int(StringsLen)
    offset = 0x42*2
    for n in range(StringsLen):
        Len = data[offset+1]
        DATA[n] = [n]*(Len)
        for i in range(0,Len,1):
            DATA[n][i] = chr(data[offset+2+i])
        offset = offset+1+Len
        DATA[n] = ''.join(DATA[n])
    print(DATA)
    jdata["Categories"]["Strings"] = DATA
    #print( '0x{:04X}'.format(int(offset)))
    base = offset+1+((offset+1)%2)
#-----------------------------------------#
# General CATEGORIES
#-----------------------------------------#
if('0x{:04X}'.format(word(data,int(base/2))) == "0x001E"):
    jdata["Categories"]["General"]["GroupIdx"] = data[base+4]
    jdata["Categories"]["General"]["ImgIdx"] = data[base+5]
    jdata["Categories"]["General"]["OrderIdx"] = data[base+6]
    jdata["Categories"]["General"]["NameIdx"] = data[base+7]
    jdata["Categories"]["General"]["CoE Details"] = data[base+9]
    jdata["Categories"]["General"]["FoE Details"] = data[base+10]
    jdata["Categories"]["General"]["EoE Details"] = data[base+11]
    jdata["Categories"]["General"]["SoEChannels"] = data[base+12]
    jdata["Categories"]["General"]["DS402Channels"] = data[base+13]
    jdata["Categories"]["General"]["SysmanClass"] = data[base+14]
    jdata["Categories"]["General"]["Flags"] = data[base+15]
    jdata["Categories"]["General"]["CurrentOnEBus"] = data[base+16]
    jdata["Categories"]["General"]["GroupIdx?"] = data[base+17]
    jdata["Categories"]["General"]["Physical Port"] = data[base+20] | data[base+21]<<8
    jdata["Categories"]["General"]["Physical Memory Address"] = data[base+23] | data[base+24]<<8
    base = base+24+12+1
json.dump(jdata, f, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
f.close()

