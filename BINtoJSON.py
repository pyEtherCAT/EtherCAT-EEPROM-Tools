import time
import os
import struct
import json

#==============================================================================#
#
#==============================================================================#
def word(data,wordaddr):
    return data[wordaddr*2] | data[wordaddr*2+1]<<8
#==============================================================================#
#
#==============================================================================#
def BINtoJSON(inbin,outjson):
    #path = 'omron_read.bin'
    f = open(inbin,"rb")
    data = f.read()
    f.close()
    f = open(outjson,"w")
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
    base = 0x40*2

    print("data length:%d" % len(data))    
    print("base length:%d" % base)

    while(len(data)!=base):
        #print("base length:%d" % base)
       #-----------------------------------------#
        # STRINGS CATEGORIES
        #-----------------------------------------#
        if( '0x{:04X}'.format(word(data,int(base/2))) == "0x000A"):
            print("---- 0x000A ----")
            print('0x{:02X}'.format(data[base-2]))
            print('0x{:02X}'.format(data[base-1]))
            print('0x{:02X}'.format(data[base+0]))
            print('0x{:02X}'.format(data[base+1]))
            print('0x{:02X}'.format(data[base+2]))
            print('0x{:02X}'.format(data[base+3]))
            print('0x{:02X}'.format(data[base+4]))
            print('0x{:02X}'.format(data[base+5]))
            jdata["Categories"]["Strings"] = {}
            jdata["Categories"]["Strings"] ["WORD Length"] = '0x{:04X}'.format(word(data,0x41))
            jdata["Categories"]["Strings"] ["Strings length"] = '0x{:02X}'.format(data[0x42*2])

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
            jdata["Categories"]["Strings"]["DATA"] = DATA
            #print( '0x{:04X}'.format(int(offset)))
            base = offset+1+((offset+1)%2)
        #-----------------------------------------#
        # General CATEGORIES
        #-----------------------------------------#
        elif('0x{:04X}'.format(word(data,int(base/2))) == "0x001E"):
            print("---- 0x001E ----")
            print('0x{:02X}'.format(data[base-2]))
            print('0x{:02X}'.format(data[base-1]))
            print('0x{:02X}'.format(data[base+0]))
            print('0x{:02X}'.format(data[base+1]))
            print('0x{:02X}'.format(data[base+2]))
            print('0x{:02X}'.format(data[base+3]))
            print('0x{:02X}'.format(data[base+4]))
            print('0x{:02X}'.format(data[base+5]))
            jdata["Categories"]["General"] = {}
            jdata["Categories"]["General"]["GroupIdx"] = data[base+2]
            jdata["Categories"]["General"]["ImgIdx"] = data[base+3]
            jdata["Categories"]["General"]["OrderIdx"] = data[base+4]
            jdata["Categories"]["General"]["NameIdx"] = data[base+5]
            jdata["Categories"]["General"]["CoE Details"] = data[base+7]
            jdata["Categories"]["General"]["FoE Details"] = data[base+8]
            jdata["Categories"]["General"]["EoE Details"] = data[base+9]
            jdata["Categories"]["General"]["SoEChannels"] = data[base+10]
            jdata["Categories"]["General"]["DS402Channels"] = data[base+11]
            jdata["Categories"]["General"]["SysmanClass"] = data[base+12]
            jdata["Categories"]["General"]["Flags"] = data[base+13]
            jdata["Categories"]["General"]["CurrentOnEBus"] = data[base+14] | data[base+15]<<8
            jdata["Categories"]["General"]["GroupIdx?"] = data[base+16]
            jdata["Categories"]["General"]["Physical Port"] = data[base+18] | data[base+19]<<8
            jdata["Categories"]["General"]["Physical Memory Address"] = data[base+20] | data[base+21]<<8
            base = base+21
        #-----------------------------------------#
        # FMMU
        #-----------------------------------------#
        elif('0x{:04X}'.format(word(data,int(base/2))) == "0x0028"):
            print("---- 0x0028 ----")
            print('0x{:02X}'.format(data[base-2]))
            print('0x{:02X}'.format(data[base-1]))
            print('0x{:02X}'.format(data[base+0]))
            print('0x{:02X}'.format(data[base+1]))
            print('0x{:02X}'.format(data[base+2]))
            print('0x{:02X}'.format(data[base+3]))
            print('0x{:02X}'.format(data[base+4]))
            print('0x{:02X}'.format(data[base+5]))
            jdata["Categories"]["FMMU"] = {}
            jdata["Categories"]["FMMU"]["FMMU0"]= data[base+2] 
            jdata["Categories"]["FMMU"]["FMMU1"]= data[base+3] 
            jdata["Categories"]["FMMU"]["FMMU2"]= data[base+4] 
            jdata["Categories"]["FMMU"]["FMMU3"]= data[base+5]
            base = base+5
        #-----------------------------------------#
        # SyncM
        #-----------------------------------------#
        elif('0x{:04X}'.format(word(data,int(base/2))) == "0x0029"):
            print("---- 0x0029 ----")
            print('0x{:02X}'.format(data[base-2]))
            print('0x{:02X}'.format(data[base-1]))
            print('0x{:02X}'.format(data[base+0]))
            print('0x{:02X}'.format(data[base+1]))
            print('0x{:02X}'.format(data[base+2]))
            print('0x{:02X}'.format(data[base+3]))
            print('0x{:02X}'.format(data[base+4]))
            print('0x{:02X}'.format(data[base+5]))
            print('0x{:02X}'.format(data[base+6]))

            jdata["Categories"]["SyncM"] = {}
            jdata["Categories"]["SyncM"]["PhysicalStartAddress"]= data[base+2] | data[base+3]<<8
            jdata["Categories"]["SyncM"]["Length"]= data[base+4] | data[base+5]<<8
            jdata["Categories"]["SyncM"]["ControlRegister"]= data[base+6] 
            jdata["Categories"]["SyncM"]["StatusRegister"]= data[base+7] 
            jdata["Categories"]["SyncM"]["EnableSynchManager"]= data[base+8] 
            jdata["Categories"]["SyncM"]["SyncManagerType"]= data[base+9] 
            base = base+9
        #-----------------------------------------#
        # FMMUX
        #-----------------------------------------#
        elif('0x{:04X}'.format(word(data,int(base/2))) == "0x002A"):
            print("---- 0x002A ----")
            print('0x{:02X}'.format(data[base-2]))
            print('0x{:02X}'.format(data[base-1]))
            print('0x{:02X}'.format(data[base+0]))
            print('0x{:02X}'.format(data[base+1]))
            print('0x{:02X}'.format(data[base+2]))
            print('0x{:02X}'.format(data[base+3]))
            print('0x{:02X}'.format(data[base+4]))
            print('0x{:02X}'.format(data[base+5]))
            print('0x{:02X}'.format(data[base+6]))
            jdata["Categories"]["FMMUX"] = {}
            base = base+1
         #-----------------------------------------#
        # SyncUnit
        #-----------------------------------------#
        elif('0x{:04X}'.format(word(data,int(base/2))) == "0x002B"):
            print("---- 0x002B ----")
            print('0x{:02X}'.format(data[base-2]))
            print('0x{:02X}'.format(data[base-1]))
            print('0x{:02X}'.format(data[base+0]))
            print('0x{:02X}'.format(data[base+1]))
            print('0x{:02X}'.format(data[base+2]))
            print('0x{:02X}'.format(data[base+3]))
            print('0x{:02X}'.format(data[base+4]))
            print('0x{:02X}'.format(data[base+5]))
            print('0x{:02X}'.format(data[base+6]))
            jdata["Categories"]["SyncUnit"] = {}
            base = base+1
        #-----------------------------------------#
        # TXPDO
        #-----------------------------------------#
        elif('0x{:04X}'.format(word(data,int(base/2))) == "0x0032"):
            print("---- 0x0032 ----")
            print('0x{:02X}'.format(data[base-2]))
            print('0x{:02X}'.format(data[base-1]))
            print('0x{:02X}'.format(data[base+0]))
            print('0x{:02X}'.format(data[base+1]))
            print('0x{:02X}'.format(data[base+2]))
            print('0x{:02X}'.format(data[base+3]))
            print('0x{:02X}'.format(data[base+4]))
            print('0x{:02X}'.format(data[base+5]))
            print('0x{:02X}'.format(data[base+6]))
            jdata["Categories"]["TXPDO"] = {}
            jdata["Categories"]["TXPDO"]["PDO_Index"]= data[base+2] | data[base+3]<<8
            jdata["Categories"]["TXPDO"]["nEntry"]= data[base+4]
            jdata["Categories"]["TXPDO"]["SyncM"]= data[base+5] 
            jdata["Categories"]["TXPDO"]["Synchronization"]= data[base+6] 
            jdata["Categories"]["TXPDO"]["NameIdx"]= data[base+7] 
            jdata["Categories"]["TXPDO"]["Flags"]= data[base+8] | data[base+9]<<8
            base2 = base+9
            #jdata["Categories"]["TXPDO"]["DATA"]
            """
            jdata["Categories"]["TXPDO"]["DATA"] = [0] * jdata["Categories"]["TXPDO"]["nEntry"]
            jdata["Categories"]["TXPDO"]["DATA"][0] = {}
            for i in range(jdata["Categories"]["TXPDO"]["nEntry"]):
                jdata["Categories"]["TXPDO"]["DATA"][i] = {}
                jdata["Categories"]["TXPDO"]["DATA"][i]["EntryIndex"] = data[base2+0]| data[base2+1]<<8
                jdata["Categories"]["TXPDO"]["DATA"][i]["Subindex"] = data[base2+2]
                jdata["Categories"]["TXPDO"]["DATA"][i]["EntryNameIdx"] = data[base2+3]
                jdata["Categories"]["TXPDO"]["DATA"][i]["DataType"] = data[base2+4]
                jdata["Categories"]["TXPDO"]["DATA"][i]["BitLen"] = data[base2+5]
                jdata["Categories"]["TXPDO"]["DATA"][i]["Flags"] = data[base2+6]
                base2 = base2 + 6
            """
            base = base2
        else:
            base = base+1
    json.dump(jdata, f, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
    f.close()
    
#==============================================================================#



if __name__ == "__main__":
    
    inbin = 'read.bin'
    outjson = "test_read.json"
    BINtoJSON(inbin,outjson)
    print("="*10)
    print("END Thanks.......")
    print("="*10)