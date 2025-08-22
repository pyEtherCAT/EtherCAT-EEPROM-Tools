
import struct
import json
from pyEtherCAT import MasterEtherCAT
import time
import os
#import fire

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
def JSONtoBIN(injson,outbin):
	f = open(injson,"r")
	jdata = json.load(f) 
	#print(jdata["Lisence"])
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
	f = open(outbin,"wb")
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
	print("0x{:02X}".format(f.tell()))


    #-----------------------------------------#
    # CATEGORIES HEADER
    #-----------------------------------------#
	if "STRINGS" in jdata["Categories"]:
		DATA = jdata["Categories"]["STRINGS"]
		#print(DATA)
		Categorie_STRINGS(f,jdata)
	if "General" in jdata["Categories"]:
		DATA = jdata["Categories"]["General"]
		#print(DATA)
		Categorie_GENERAL(f,jdata)
	if "FMMU" in jdata["Categories"]:
		DATA = jdata["Categories"]["FMMU"]
		Categorie_FMMU(f,jdata)
		#print(DATA)
	if "SyncM" in jdata["Categories"]:
		DATA = jdata["Categories"]["SyncM"]
		Categorie_SYNCM(f,jdata)
		#print(DATA)
	if "TXPDO" in jdata["Categories"]:
		DATA = jdata["Categories"]["TXPDO"]
		Categorie_TXPDO(f,jdata)
		#print(DATA)
	if "RXPDO" in jdata["Categories"]:
		DATA = jdata["Categories"]["RXPDO"]
		Categorie_RXPDO(f,jdata)
		#print(DATA)
	if "DC" in jdata["Categories"]:
		DATA = jdata["Categories"]["DC"]
		Categorie_DC(f,jdata)
		#print(DATA)
	f.close()

#==============================================================================#
#
#==============================================================================#	
def Categorie_STRINGS(f,jdata):
	#-----------------------------------------#
	# STRINGS CATEGORIES
	#-----------------------------------------#
	#DATA = [b"ArtifactNoise-DIGIO",b"ArtifactNoise",b"Output x16"]
	#DATA = jdata["Categories"]["STRINGS"]
	f.write(struct.pack("H",10))            # STRINGS TYPE
	csize = 1
	for i in range(len(jdata["Categories"]["STRINGS"]["Index"])):
		length  = len(jdata["Categories"]["STRINGS"]["Index"][str(i)]["string"].encode('utf-8'))
		csize = csize + length+1
	f.write(struct.pack("H",int(csize/2)+1)) 
	addr = f.tell()
	f.write(struct.pack("B",int(jdata["Categories"]["STRINGS"]["WORD Length"],16)))            # STRINGS 
	#print(len(jdata["Categories"]["STRINGS"]["Index"]))
	DATA = [0]*len(jdata["Categories"]["STRINGS"]["Index"])
	for i in range(len(jdata["Categories"]["STRINGS"]["Index"])):
		length  = len(jdata["Categories"]["STRINGS"]["Index"][str(i)]["string"].encode('utf-8'))
		f.write(struct.pack("B",length))          # STRINGS TYPE
		for n in range(length):
			f.write(struct.pack("B",jdata["Categories"]["STRINGS"]["Index"][str(i)]["string"].encode('utf-8')[n]))            # STRINGS TYPE
	if((f.tell()-addr)%2 == 1):
		f.write(struct.pack("B",0x00))
#==============================================================================#
#
#==============================================================================#
def Categorie_GENERAL(f,jdata):
	#-----------------------------------------#
	# General CATEGORIES
	#-----------------------------------------#
	f.write(struct.pack("H",30))            # STRINGS TYPE
	f.write(struct.pack("H",int((0x14+12)/2)))            # GENERAL TYPE
	f.write(struct.pack("B",jdata["Categories"]["General"]["GroupIdx"]))     # GroupIdx
	f.write(struct.pack("B",jdata["Categories"]["General"]["ImgIdx"]) )    # ImgIdx
	f.write(struct.pack("B",jdata["Categories"]["General"]["OrderIdx"]))     # OrderIdx
	f.write(struct.pack("B",jdata["Categories"]["General"]["NameIdx"]))     # NameIdx
	f.write(struct.pack("B",0x00))     # Reserved
	f.write(struct.pack("B",0x00))     # CoE Details
	f.write(struct.pack("B",0x00))     # FoE Details
	f.write(struct.pack("B",0x00))     # EoE Details
	f.write(struct.pack("B",0x00))     # SoEChannels
	f.write(struct.pack("B",0x00))     # DS402Channels
	f.write(struct.pack("B",0x00))     # SysmanClass
	f.write(struct.pack("B",0x00))     # Flags
	f.write(struct.pack("H",0x00))     # CurrentOnEBus
	f.write(struct.pack("B",jdata["Categories"]["General"]["GroupIdx2"]))     # GroupIdx
	f.write(struct.pack("H",0x00))     # Reserved1
	f.write(struct.pack("H",int(jdata["Categories"]["General"]["Physical Port"],16)))     # Physical Port
	f.write(struct.pack("H",int(jdata["Categories"]["General"]["Physical Memory Address"],16)))     # Physical Memory Address
	for i in range(12-1):
		f.write(struct.pack("B",0x00))     # Reserved2
#==============================================================================#
#
#==============================================================================#
def Categorie_FMMU(f,jdata):
	f.write(struct.pack("H",40))
	size = len(jdata["Categories"]["FMMU"])            
	f.write(struct.pack("H",size-1))
	for i in range(size):
		if(jdata["Categories"]["FMMU"][str(i)]=="None"):
			f.write(struct.pack("B",0))
		if(jdata["Categories"]["FMMU"][str(i)]=="Output"):
			f.write(struct.pack("B",1))
		if(jdata["Categories"]["FMMU"][str(i)]=="Input"):
			f.write(struct.pack("B",2))
		if(jdata["Categories"]["FMMU"][str(i)]=="SyncM"):
			f.write(struct.pack("B",3))
#==============================================================================#
#
#==============================================================================#			
def Categorie_SYNCM(f,jdata):
	f.write(struct.pack("H",41))
	index = len(jdata["Categories"]["SyncM"])
	f.write(struct.pack("H",(index-1)*8))
	for i in range(index):
		f.write(struct.pack("H",int(jdata["Categories"]["SyncM"][str(i)]["PhysicalStartAddress"],16)))
		f.write(struct.pack("H",int(jdata["Categories"]["SyncM"][str(i)]["Length"],16)))
		f.write(struct.pack("B",int(jdata["Categories"]["SyncM"][str(i)]["ControlRegister"],16)))
		f.write(struct.pack("B",int(jdata["Categories"]["SyncM"][str(i)]["StartRegister"],16)))
		f.write(struct.pack("B",int(jdata["Categories"]["SyncM"][str(i)]["EnableSyncManager"],16)))
		f.write(struct.pack("B",int(jdata["Categories"]["SyncM"][str(i)]["SyncManagerType"],16)))

#==============================================================================#
#
#==============================================================================#
def Categorie_TXPDO(f,jdata):
	f.write(struct.pack("H",50))
	index = len(jdata["Categories"]["TXPDO"])
	f.write(struct.pack("H",7+(index-7)))
	print(index)
	f.write(struct.pack("H",int(jdata["Categories"]["TXPDO"]["PDOIndex"],16)))
	f.write(struct.pack("B",int(jdata["Categories"]["TXPDO"]["nEntry"],16)))
	f.write(struct.pack("B",int(jdata["Categories"]["TXPDO"]["SyncM"],16)))
	f.write(struct.pack("B",int(jdata["Categories"]["TXPDO"]["Synchronization"],16)))
	f.write(struct.pack("B",int(jdata["Categories"]["TXPDO"]["NameIdx"],16)))
	f.write(struct.pack("H",int(jdata["Categories"]["TXPDO"]["Flags"],16)))
	for i in range(index-7):
		f.write(struct.pack("H",int(jdata["Categories"]["TXPDO"][str(i)]["EntryIndex"],16)))
		f.write(struct.pack("B",int(jdata["Categories"]["TXPDO"][str(i)]["SubIndex"],16)))
		f.write(struct.pack("B",int(jdata["Categories"]["TXPDO"][str(i)]["EntryNameIndex"],16)))
		f.write(struct.pack("B",int(jdata["Categories"]["TXPDO"][str(i)]["DataType"],16)))
		f.write(struct.pack("B",int(jdata["Categories"]["TXPDO"][str(i)]["BitLen"],16)))
		f.write(struct.pack("H",int(jdata["Categories"]["TXPDO"][str(i)]["Flags"],16)))
#==============================================================================#
#
#==============================================================================#
def Categorie_RXPDO(f,jdata):
	f.write(struct.pack("H",51))
	index = len(jdata["Categories"]["RXPDO"])
	f.write(struct.pack("H",7+(index-7)))
	print(index)
	f.write(struct.pack("H",int(jdata["Categories"]["RXPDO"]["PDOIndex"],16)))
	f.write(struct.pack("B",int(jdata["Categories"]["RXPDO"]["nEntry"],16)))
	f.write(struct.pack("B",int(jdata["Categories"]["RXPDO"]["SyncM"],16)))
	f.write(struct.pack("B",int(jdata["Categories"]["RXPDO"]["Synchronization"],16)))
	f.write(struct.pack("B",int(jdata["Categories"]["RXPDO"]["NameIdx"],16)))
	f.write(struct.pack("H",int(jdata["Categories"]["RXPDO"]["Flags"],16)))
	for i in range(index-7):
		f.write(struct.pack("H",int(jdata["Categories"]["RXPDO"][str(i)]["EntryIndex"],16)))
		f.write(struct.pack("B",int(jdata["Categories"]["RXPDO"][str(i)]["SubIndex"],16)))
		f.write(struct.pack("B",int(jdata["Categories"]["RXPDO"][str(i)]["EntryNameIndex"],16)))
		f.write(struct.pack("B",int(jdata["Categories"]["RXPDO"][str(i)]["DataType"],16)))
		f.write(struct.pack("B",int(jdata["Categories"]["RXPDO"][str(i)]["BitLen"],16)))
		f.write(struct.pack("H",int(jdata["Categories"]["RXPDO"][str(i)]["Flags"],16)))
#==============================================================================#
#
#==============================================================================#
def Categorie_DC(f,jdata):
	f.write(struct.pack("H",60))
	index = len(jdata["Categories"]["DC"])
	print(index)
	f.write(struct.pack("H",(index-1)*24))
	for i in range(index):
		f.write(struct.pack("<I",int(jdata["Categories"]["DC"][str(i)]["CycleTime0"],16)))
		f.write(struct.pack("<I",int(jdata["Categories"]["DC"][str(i)]["ShiftTime0"],16)))
		f.write(struct.pack("<I",int(jdata["Categories"]["DC"][str(i)]["ShiftTime1"],16)))
		f.write(struct.pack("H",int(jdata["Categories"]["DC"][str(i)]["Sync1CycleFactor"],16)))
		f.write(struct.pack("H",int(jdata["Categories"]["DC"][str(i)]["assignActivate"],16)))
		f.write(struct.pack("H",int(jdata["Categories"]["DC"][str(i)]["Sync0CycleFactor"],16)))
		f.write(struct.pack("B",int(jdata["Categories"]["DC"][str(i)]["NameIdx"],16)))
		f.write(struct.pack("B",int(jdata["Categories"]["DC"][str(i)]["DescIdx"],16)))
		f.write(struct.pack("<I",int(jdata["Categories"]["DC"][str(i)]["Reserved"],16)))


#==============================================================================#
#
#==============================================================================#
def WriteEEPROM(nicname,outbin,ADPaddr):
	cat = MasterEtherCAT.MasterEtherCAT(nicname)
	cat.ADP = ADPaddr
	cat.EEPROM_SetUp(0x0000)
	# EEPROM ゼロクリア
	print("EEPROM Zero Clear")
	for i in range(0x0FF):
		cat.EEPROM_AddrSet(i)
		cat.EEPROM_Write(0)
		cat.EEPROM_Stasus(enable=0x01, command=0x02)
		time.sleep(0.01)
	f = open(outbin,"rb")
	data = f.read()
	wordaddr = 0
	print("EEPROM Write ....")
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
	#for i in range(0x0050):
	#	cat.EEPROM_AddrSet(i)
	#	cat.EEPROM_Stasus(enable=0x00, command=0x01)
	#	(DATA, WKC) = cat.EEPROM_Read()
	#	print("READ[0x{:04x}]= 0x{:04x}".format(i, DATA[0] | DATA[1] << 8))
	cat.EthereCAT_Reset()
	time.sleep(1)
#==============================================================================#
#
#==============================================================================#
if __name__ == "__main__":

    nicname = "eno2"
    injson = "eeprom_read_costom.json"
    outbin = "out.bin"
    ADPaddr = 0x0000
    print("="*10)
    print("JSON -> BIN File.....")
    print("="*10)
    JSONtoBIN(injson,outbin)
    print("="*10)

    yorn = input("Can you really write?:(y/n) ")
    if(yorn=='y'):
        print("="*10)
        print("BIN File -> EtherCAT_EEPROM writing.....")
        print("="*10)
        WriteEEPROM(nicname,outbin,ADPaddr)
    print("="*10)
    print("END Thanks.......")
    print("="*10)
