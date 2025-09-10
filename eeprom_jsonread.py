
from pyEtherCAT import MasterEtherCAT
import time
import os
import struct
import json

#==============================================================================#
#
#==============================================================================#
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
#==============================================================================#
#
#==============================================================================#
def word(data,wordaddr):
    if  wordaddr * 2 + 1 >= len(data):
        return 0
    return data[ wordaddr * 2] | (data[ wordaddr * 2+1] << 8)   # little-endian
#==============================================================================#
#
#==============================================================================#
def ReadEEPROM(nicname,inbin,ADPaddr):
    cat = MasterEtherCAT.MasterEtherCAT(nicname)
    cat.ADP = ADPaddr
    cat.EthereCAT_Reset()
    time.sleep(1)
    cat.EEPROM_SetUp(0x0000)
    f = open(inbin,"wb")
    # EEPROM 読み出し
    for i in range(0x200):
        cat.EEPROM_AddrSet(i)
        cat.EEPROM_Stasus(enable=0x00, command=0x01)
        (DATA, WKC) = cat.EEPROM_Read()
        print("READ[0x{:04x}]= 0x{:04x}".format(i,DATA[0] | DATA[1] << 8 ))
        f.write(struct.pack("H", (DATA[0] | DATA[1] << 8) ))
        if((DATA[0] | DATA[1] << 8) == 0xFFFF):
            break
        time.sleep(0.01)
    f.close()
#==============================================================================#
#
#==============================================================================#
def BINtoJSON(inbin,outjson):
    #path = 'omron_read.bin'
    f = open(inbin,"rb")
    data = f.read()
    size = len(data)
    print( '0x{:02X}'.format(size))
    f.close()
    f = open(outjson,"w")
    jdata = {}
    jdata["ESC Info"] = {}
    jdata["ESC Info"]["PDI Control"] = {}
    jdata["ESC Info"]["PDI Configuration"] = {}
    jdata["ESC Info"]["Other INFO"] = {}
    # PDI 制御レジスタ[0x0140]
    jdata["ESC Info"]["PDI Control"]["PDI ControlRegister"] = '0x{:02X}'.format(word(data,0x00)&0xFF)
    # ESC コンフィグレーション レジスタ [0x0141]
    jdata["ESC Info"]["PDI Control"]["ESC Configuration Register"] = '0x{:02X}'.format((word(data,0x00)>>8)&0xFF)
    # PDI コンフィグレーション レジスタ デジタル I/O モード [0x0150]
    jdata["ESC Info"]["PDI Configuration"]["PDI Configuration Register"] = '0x{:02X}'.format(word(data,0x01)&0xFF)
    # SYNC/LATCH PDI コンフィグレーション レジスタ [0982h-0983h)]
    jdata["ESC Info"]["PDI Configuration"]["Sync/Latch PDI Configuration Register"] = '0x{:02X}'.format((word(data,0x01)>>8)&0xFF)
    # SyncSignal パルス長レジスタ [0982h-0983h]
    jdata["ESC Info"]["Pulse Length of SyncSignals Register"] = '0x{:04X}'.format(word(data,0x02))
    # 拡張 PDI コンフィグレーション レジスタ [0152h-0153h] SPI モード
    jdata["ESC Info"]["Extended PDI Configuration Register"] = '0x{:04X}'.format(word(data,0x03))
    # 構成済みステーション エイリアス レジスタ [0012h-0013h]
    jdata["ESC Info"]["Configured Station Alias Register"] = '0x{:04X}'.format(word(data,0x04))
    # MII 管理制御 / ステータス レジスタ [0510h-0511h]
    jdata["ESC Info"]["Other INFO"]["MII Management Control/Status Register"] = '0x{:02X}'.format((word(data,0x05)>>0)&0xFF)
    # ASIC コンフィグレーション レジスタ [0142h-0143h]
    jdata["ESC Info"]["Other INFO"]["ASIC Configuration Register"] = '0x{:02X}'.format((word(data,0x05)>>8)&0xFF)
    # 予約レジスタ [0114h-0145h]
    # data[12] 0x00,data[13] 0x00
    # CRCデータ
    jdata["ESC Info"]["CRC"] = '0x{:04X}'.format(word(data,0x07))
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


    base = 0x40
    #-----------------------------------------#
    # CATEGORIES HEADER
    #-----------------------------------------#
    jdata["Categories"] = {}

    for i in range(20):

        Categories = word(data,base)
        CategpriesSize = word(data,base+1)
        
        if(Categories==00):
            print("---------------------------")
            print("NOP")
            print('0x{:02X} : 0x{:04X} {:02d}'.format(base-1,word(data,base-1),word(data,base-1)))
            print('0x{:02X} : 0x{:04X} {:02d}'.format(base,word(data,base),word(data,base)))
            print('0x{:02X} : 0x{:04X} {:02d}'.format(base+1,word(data,base+1),word(data,base+1)))
            print("---------------------------")
        if(Categories==10):
            print("---------------------------")
            print("STRINGS")
            print('Categories 0x{:02X} : 0x{:04X} {:02d}'.format(base,Categories,Categories))
            print('CategpriesSize 0x{:02X} : 0x{:04X} {:02d}'.format(base+1,CategpriesSize,CategpriesSize))
            Categorie_STRINGS(data, base+2, jdata)
            print('0x{:02X} : 0x{:04X} {:02d}'.format(base,Categories,Categories))
            print("---------------------------")
        if(Categories==20):
            print("---------------------------")
            print("DATATYPES")
            print('0x{:02X} : 0x{:04X} {:02d}'.format(base,Categories,Categories))
            print("---------------------------")
        if(Categories==30):
            print("---------------------------")
            print("GENERAL")
            print('Categories 0x{:02X} : 0x{:04X} {:02d}'.format(base,Categories,Categories))
            print('CategpriesSize 0x{:02X} : 0x{:04X} {:02d}'.format(base+1,CategpriesSize,CategpriesSize))
            Categorie_GENERAL(data, base+2, jdata)
            print('0x{:02X} : 0x{:04X} {:02d}'.format(base,Categories,Categories))
            print("---------------------------")
        if(Categories==40):
            print("---------------------------")
            print("FMMU")
            print('Categories 0x{:02X} : 0x{:04X} {:02d}'.format(base,Categories,Categories))
            print('CategpriesSize 0x{:02X} : 0x{:04X} {:02d}'.format(base+1,CategpriesSize,CategpriesSize))
            Categorie_FMMU(data, base+2, jdata)
            print("---------------------------")
        if(Categories==41):
            print("---------------------------")
            print("SYNCM")
            print('Categories 0x{:02X} : 0x{:04X} {:02d}'.format(base,Categories,Categories))
            print('CategpriesSize 0x{:02X} : 0x{:04X} {:02d}'.format(base+1,CategpriesSize,CategpriesSize))
            Categorie_SYNCM(data, base+2, jdata)
            print('0x{:02X} : 0x{:04X} {:02d}'.format(base,Categories,Categories))
            print("---------------------------")
        if(Categories==42):
            print("---------------------------")
            print("FMMUX")
            print('0x{:02X} : 0x{:04X} {:02d}'.format(base,Categories,Categories))
            print("---------------------------")
        if(Categories==43):
            print("---------------------------")
            print("SYNCUNIT")
            print('0x{:02X} : 0x{:04X} {:02d}'.format(base,Categories,Categories))
            print("---------------------------")
        if(Categories==50):
            print("---------------------------")
            print("TXPDO")
            print('Categories 0x{:02X} : 0x{:04X} {:02d}'.format(base,Categories,Categories))
            print('CategpriesSize 0x{:02X} : 0x{:04X} {:02d}'.format(base+1,CategpriesSize,CategpriesSize))
            Categorie_TXPDO(data, base+2, jdata)
            print('0x{:02X} : 0x{:04X} {:02d}'.format(base,Categories,Categories))
            print("---------------------------")
        if(Categories==51):
            print("---------------------------")
            print("RXPDO")
            print('Categories 0x{:02X} : 0x{:04X} {:02d}'.format(base,Categories,Categories))
            print('CategpriesSize 0x{:02X} : 0x{:04X} {:02d}'.format(base+1,CategpriesSize,CategpriesSize))
            Categorie_RXPDO(data, base+2, jdata)
            print('0x{:02X} : 0x{:04X} {:02d}'.format(base,Categories,Categories))
            print("---------------------------")
        if(Categories==60):
            print("---------------------------")
            print("DC")
            print('Categories 0x{:02X} : 0x{:04X} {:02d}'.format(base,Categories,Categories))
            print('CategpriesSize 0x{:02X} : 0x{:04X} {:02d}'.format(base+1,CategpriesSize,CategpriesSize))
            Categorie_DC(data, base+2, jdata)
            print('0x{:02X} : 0x{:04X} {:02d}'.format(base,Categories,Categories))
            print("---------------------------")
        if(Categories==70):
            print("---------------------------")
            print("TIMEOUTS")
            print('0x{:02X} : 0x{:04X} {:02d}'.format(base,Categories,Categories))
            print("---------------------------")
        
        #if(word(data,base+1)==0x00):
        #    break
        if(size <= base+1) :
            break
        base = base + word(data,base+1)+2
    
    print(jdata)
    json.dump(jdata, f, ensure_ascii=False, indent=4, sort_keys=False, separators=(',', ': '))
    f.close()
#==============================================================================#
#
#==============================================================================#
def Categorie_STRINGS(data, base, jdata):
    jdata["Categories"]["STRINGS"] = {}
    base = base*2
    nStrings = data[base]
    DATA = [0]*int(nStrings)
    jdata["Categories"]["STRINGS"]["WORD Length"] = '0x{:04X}'.format(nStrings)
    jdata["Categories"]["STRINGS"]["Index"] = {}
    for n in range(nStrings):
        jdata["Categories"]["STRINGS"]["Index"][str(n)]= {}
        #jdata["Categories"]["STRINGS"]["Index"][str(n)]["length"] = data[base+1]
        stringsLen = data[base+1]
        DATA[n] = [n]*(stringsLen)
        for i in range(0,stringsLen,1):
            DATA[n][i] = chr(data[base+2+i])  
        base = base+1+stringsLen
        stringsLen = data[base+1]
        s = "".join(DATA[n])
        print('{:d} : {:s}'.format(n,s))
        jdata["Categories"]["STRINGS"]["Index"][str(n)]["string"] = s
    #print(jdata)
    return jdata
#==============================================================================#
#
#==============================================================================#
def Categorie_GENERAL(data, base, jdata):
    jdata["Categories"]["General"] = {}
    
    base = base*2
    Reserved = 0
    jdata["Categories"]["General"]["GroupIdx"] = data[base+0]
    jdata["Categories"]["General"]["GroupStrings"] = jdata["Categories"]["STRINGS"]["Index"][str(data[base+0]-1)]["string"]
    jdata["Categories"]["General"]["ImgIdx"] = data[base+1]
    jdata["Categories"]["General"]["OrderIdx"] = data[base+2]
    jdata["Categories"]["General"]["OrderStrings"] = jdata["Categories"]["STRINGS"]["Index"][str(data[base+2]-1)]["string"]
    jdata["Categories"]["General"]["NameIdx"] = data[base+3]
    jdata["Categories"]["General"]["NameStrings"] = jdata["Categories"]["STRINGS"]["Index"][str(data[base+3]-1)]["string"]
    Reserved = data[base+4]
    jdata["Categories"]["General"]["CoE Details"] = data[base+5]
    jdata["Categories"]["General"]["FoE Details"] = data[base+6]
    jdata["Categories"]["General"]["EoE Details"] = data[base+7]
    jdata["Categories"]["General"]["SoE Channels"] = data[base+8]
    jdata["Categories"]["General"]["DS402 Channels"] = data[base+9]
    jdata["Categories"]["General"]["SysmanClass"] = data[base+10]
    jdata["Categories"]["General"]["Flags"] = data[base+11]
    jdata["Categories"]["General"]["CurrentOnEBus"] = data[base+12] | data[base+13]<<8 
    jdata["Categories"]["General"]["GroupIdx2"] = data[base+14]
    jdata["Categories"]["General"]["GroupStrings2"] = jdata["Categories"]["STRINGS"]["Index"][str(data[base+14]-1)]["string"]
    Reserved = data[base+15]
    jdata["Categories"]["General"]["Physical Port"] = '0x{:04X}'.format(data[base+16] | data[base+17]<<8)
    jdata["Categories"]["General"]["Physical Memory Address"] = '0x{:04X}'.format(data[base+18] | data[base+19]<<8)
    #print(jdata)
    return jdata
#==============================================================================#
#
#==============================================================================#
def Categorie_FMMU(data, base, jdata):
    jdata["Categories"]["FMMU"] = {}
    size = word(data,base-1)
    base = base*2
    for i in range(size+1):
        if( data[base+i]==0):
           jdata["Categories"]["FMMU"][str(i)] = "None"
        if( data[base+i]==1):
           jdata["Categories"]["FMMU"][str(i)] = "Output"
        if( data[base+i]==2):
           jdata["Categories"]["FMMU"][str(i)] = "Input"
        if( data[base+i]==3):
           jdata["Categories"]["FMMU"][+str(i)] = "SyncM"
    return jdata
#==============================================================================#
#
#==============================================================================#
def Categorie_SYNCM(data, base, jdata):
    size = word(data,base-1)
    base = base*2
    jdata["Categories"]["SyncM"] = {}
    n = 0
    for i in range(int(size/8)+1):
        jdata["Categories"]["SyncM"][str(i)] = {}
        #print('0x{:02X} : 0x{:04X}'.format(base+0,data[base+0]))
        #print('0x{:02X} : 0x{:04X}'.format(base+1,data[base+1]))
        jdata["Categories"]["SyncM"][str(i)]["PhysicalStartAddress"] = '0x{:04X}'.format(data[base+0]|data[base+1]<<8)
        jdata["Categories"]["SyncM"][str(i)]["Length"] = '0x{:04X}'.format(data[base+2]|data[base+3]<<8)
        jdata["Categories"]["SyncM"][str(i)]["ControlRegister"] = '0x{:02X}'.format(data[base+4])
        jdata["Categories"]["SyncM"][str(i)]["StartRegister"] = '0x{:02X}'.format(data[base+5])
        jdata["Categories"]["SyncM"][str(i)]["EnableSyncManager"] = '0x{:02X}'.format(data[base+6])
        jdata["Categories"]["SyncM"][str(i)]["SyncManagerType"] = '0x{:02X}'.format(data[base+7])
        base = base+8
    return jdata
#==============================================================================#
#
#==============================================================================#
def Categorie_TXPDO(data, base, jdata):
    size = word(data,base-1)
    base = base*2
    jdata["Categories"]["TXPDO"] = {}
    n = 0
    jdata["Categories"]["TXPDO"]["PDOIndex"] = '0x{:04X}'.format(data[base+0]|data[base+1]<<8)
    jdata["Categories"]["TXPDO"]["nEntry"] = '0x{:02X}'.format(data[base+2])
    jdata["Categories"]["TXPDO"]["SyncM"] = '0x{:02X}'.format(data[base+3])
    jdata["Categories"]["TXPDO"]["Synchronization"] = '0x{:02X}'.format(data[base+4])
    jdata["Categories"]["TXPDO"]["NameIdx"] = '0x{:02X}'.format(data[base+5])
    jdata["Categories"]["TXPDO"]["NameStrings"] = jdata["Categories"]["STRINGS"]["Index"][str(data[base+5]-1)]["string"] 
    jdata["Categories"]["TXPDO"]["Flags"] = '0x{:04X}'.format(data[base+6]|data[base+7]<<8)
    index = int(data[base+2])
    base = base+8
    for i in range(index):
        jdata["Categories"]["TXPDO"][str(i)] = {}
        jdata["Categories"]["TXPDO"][str(i)]["EntryIndex"] = '0x{:04X}'.format(data[base+0]|data[base+1]<<8)
        jdata["Categories"]["TXPDO"][str(i)]["SubIndex"] = '0x{:02X}'.format(data[base+2])
        jdata["Categories"]["TXPDO"][str(i)]["EntryNameIndex"] = '0x{:02X}'.format(data[base+3])
        jdata["Categories"]["TXPDO"][str(i)]["EntryNameStrings"] = jdata["Categories"]["STRINGS"]["Index"][str(data[base+3]-1)]["string"] 
        jdata["Categories"]["TXPDO"][str(i)]["DataType"] = '0x{:02X}'.format(data[base+4])
        jdata["Categories"]["TXPDO"][str(i)]["BitLen"] = '0x{:02X}'.format(data[base+5])
        jdata["Categories"]["TXPDO"][str(i)]["Flags"] = '0x{:04X}'.format(data[base+6]|data[base+7]<<8)
        base = base+8

    return jdata
#==============================================================================#
#
#==============================================================================#
def Categorie_RXPDO(data, base, jdata):
    size = word(data,base-1)
    base = base*2
    jdata["Categories"]["RXPDO"] = {}
    n = 0
    jdata["Categories"]["RXPDO"]["PDOIndex"] = '0x{:04X}'.format(data[base+0]|data[base+1]<<8)
    jdata["Categories"]["RXPDO"]["nEntry"] = '0x{:02X}'.format(data[base+2])
    jdata["Categories"]["RXPDO"]["SyncM"] = '0x{:02}'.format(data[base+3])
    jdata["Categories"]["RXPDO"]["Synchronization"] = '0x{:02X}'.format(data[base+4])
    jdata["Categories"]["RXPDO"]["NameIdx"] = '0x{:02X}'.format(data[base+5])
    jdata["Categories"]["RXPDO"]["NameStrings"] = jdata["Categories"]["STRINGS"]["Index"][str(data[base+5]-1)]["string"] 
    jdata["Categories"]["RXPDO"]["Flags"] = '0x{:04X}'.format(data[base+6]|data[base+7]<<8)
    index = int(data[base+2])
    base = base+8
    for i in range(index):
        jdata["Categories"]["RXPDO"][str(i)] = {}
        jdata["Categories"]["RXPDO"][str(i)]["EntryIndex"] = '0x{:04X}'.format(data[base+0]|data[base+1]<<8)
        jdata["Categories"]["RXPDO"][str(i)]["SubIndex"] = '0x{:02X}'.format(data[base+2])
        jdata["Categories"]["RXPDO"][str(i)]["EntryNameIndex"] = '0x{:02X}'.format(data[base+3])
        jdata["Categories"]["RXPDO"][str(i)]["EntryNameStrings"] = jdata["Categories"]["STRINGS"]["Index"][str(data[base+3]-1)]["string"]
        jdata["Categories"]["RXPDO"][str(i)]["DataType"] = '0x{:02X}'.format(data[base+4])
        jdata["Categories"]["RXPDO"][str(i)]["BitLen"] = '0x{:02X}'.format(data[base+5])
        jdata["Categories"]["RXPDO"][str(i)]["Flags"] = '0x{:04X}'.format(data[base+6]|data[base+7]<<8)
        base = base+8

    return jdata
#==============================================================================#
#
#==============================================================================#
def Categorie_DC(data, base, jdata):
    size = word(data,base-1)
    base = base*2
    print('0x{:02X} : 0x{:04X}'.format(base+0,data[base+0]))
    print('0x{:02X} : 0x{:04X}'.format(base+1,data[base+1]))
    print('0x{:02X} : 0x{:04X}'.format(base+2,data[base+2]))
    print('0x{:02X} : 0x{:04X}'.format(base+3,data[base+3]))
    print('0x{:02X} : 0x{:04X}'.format(base+4,data[base+4]))
    print('0x{:02X} : 0x{:04X}'.format(base+5,data[base+5]))
    print('0x{:02X} : 0x{:04X}'.format(base+6,data[base+6]))
    print('0x{:02X} : 0x{:04X}'.format(base+7,data[base+7]))

    jdata["Categories"]["DC"] = {}
    for i in range(int(size/24)+1):
        jdata["Categories"]["DC"][str(i)] = {}
        #print('0x{:02X} : 0x{:04X}'.format(base+0,data[base+0]))
        #print('0x{:02X} : 0x{:04X}'.format(base+1,data[base+1]))
        jdata["Categories"]["DC"][str(i)]["CycleTime0"] = '0x{:08X}'.format(data[base+0]| data[base+1]<<8| data[base+2]<<8|data[base+3]<<24)
        jdata["Categories"]["DC"][str(i)]["ShiftTime0"] = '0x{:08X}'.format(data[base+4]|data[base+5]<<8|data[base+6]<<16|data[base+7]<<24)
        jdata["Categories"]["DC"][str(i)]["ShiftTime1"] = '0x{:08X}'.format(data[base+8]|data[base+9]<<8|data[base+10]<<16|data[base+11]<<24)
        jdata["Categories"]["DC"][str(i)]["Sync1CycleFactor"] = '0x{:02X}'.format(data[base+12]|data[base+13]<<8)
        jdata["Categories"]["DC"][str(i)]["assignActivate"] = '0x{:02X}'.format(data[base+14]|data[base+15]<<8)
        jdata["Categories"]["DC"][str(i)]["Sync0CycleFactor"] = '0x{:02X}'.format(data[base+16]|data[base+17]<<8)
        jdata["Categories"]["DC"][str(i)]["NameIdx"] = '0x{:02X}'.format(data[base+18])
        jdata["Categories"]["DC"][str(i)]["NameStrings"] = jdata["Categories"]["STRINGS"]["Index"][str(data[base+18]-1)]["string"]
        jdata["Categories"]["DC"][str(i)]["DescIdx"] = '0x{:02X}'.format(data[base+19])
        jdata["Categories"]["DC"][str(i)]["DescStrings"] = jdata["Categories"]["STRINGS"]["Index"][str(data[base+19]-1)]["string"]
        jdata["Categories"]["DC"][str(i)]["Reserved"] = '0x{:02X}'.format(data[base+20]|data[base+21]<<8|data[base+22]<<16|data[base+23]<<24)
        base = base+24
#==============================================================================#
#
#==============================================================================#
if __name__ == "__main__":
    
    nicname = "eno1"
    inbin = 'out.bin'
    outjson = "eeprom_read_out.json"
    ADPaddr = 0x0000
    print("="*10)
    print("EtherCAT_EEPROM Read -> BIN File .....")
    print("="*10)

    ReadEEPROM(nicname,inbin,ADPaddr)
    print("="*10)
    print("BIN File -> JSON .....")
    print("="*10)
    BINtoJSON(inbin,outjson)
    print("="*10)
    print("END Thanks.......")
    print("="*10)
 
