#Project URL for information/contact https://github.com/krixgris/MidiToOSC
#

import mido
import OSC
import json
from datetime import datetime

import configHandler
import httpHandler


configFile = 'oscconfig.json'
conf = configHandler.configHandler(configFile=configFile)

osc = OSC.OSCClient()
http = httpHandler.httpHandler()

def MidiEvent(midiNum, midiType):
	midiNum = str(midiNum)

	if (midiType == 'control_change'):
		midiEvent = configHandler.MidiEvent(conf.control_change.get(midiNum))
	if (midiType == 'note_on'):
		midiEvent = configHandler.MidiEvent(conf.note_on.get(midiNum))
	if (midiType == 'note_off'):
		midiEvent = configHandler.MidiEvent(conf.note_off.get(midiNum))
	return midiEvent

def reloadConfig():
	global conf
	conf = configHandler.configHandler(configFile=configFile)
	reconnectOSC()
	reconnectHTTP()
	print(str(datetime.now()) + " Configuration updated")
	print conf.config_json

def quitViolently():
	print "Quitting violently!"
	quit()

#reconnects the OSC object to ip/port in config
def reconnectOSC():
	osc.connect((str(conf.IP),int(conf.port)))

def reconnectHTTP():
	http.setIP(str(conf.IP))

#depr?
def getMIDIInputDevice():
	#todo: defaults, mido.get_input_names()[0]
	#testing with usb midi dongle 'CME U2MIDI:CME U2MIDI MIDI 1 20:0'
	return str(conf.midiDeviceInput)

#depr?
def getMIDIInputChannel():
	#todo: defaults, 0
	return int(conf.midiChannelInput)-1

def createOscMessage(address, val):
	oscMsg = OSC.OSCMessage()
	oscMsg.setAddress(address)
	oscMsg.append(float(val))
	return oscMsg

def getType(midiNum, midiType):
	mtoType = MidiEvent(midiNum,midiType).type
	if(mtoType is None):
		mtoType = ''
	return mtoType
	#return MidiEvent(midiNum,midiType).type

def getAttribute(midiNum, midiType):
	mtoType = MidiEvent(midiNum,midiType).attribute
	if(mtoType is None):
		mtoType = 'value'
	return mtoType


def mtoAction(midiNum, midiValue, midiType):
	print midiNum, midiValue, midiType
	print getType(midiNum, midiType)
	if(getType(midiNum, midiType) == 'osc'):
		print 'osc'
		mtoOSC(midiNum, midiValue, midiType)
		return 1
	if(getType(midiNum,midiType) == 'command'):
		if(getCommand(midiNum, midiType) == 'reloadConfig'):
			reloadConfig()
		if(getCommand(midiNum, midiType) == 'quitLoop'):
			quitViolently()
		return 2
	if(getType(midiNum, midiType) == 'http'):
		mtoHTTP(midiNum, midiValue, midiType)
		return 1
	return 0

def mtoCommand(midiNum,midiType):
	return 0

def mtoOSC(midiNum, midiValue, midiType):
	#print getOscMessage(midiNum, midiValue, midiType)
	osc.send(getOscMessage(midiNum, midiValue, midiType))
	return 0

def mtoHTTP(midiNum, midiValue, midiType):
	#osc.send(getOscMessage(midiNum, midiValue, midiType))
	#print getHTTPValue(midiNum,midiValue,midiType)
	#print getHTTPValueAttribute(midiNum,midiValue,midiType)
	data = http.getValueList(getHTTPValueAttribute(midiNum,midiValue,midiType), getHTTPValue(midiNum,midiValue,midiType))
	#print data
	#print getHTTPAddress(midiNum,midiType)
	#print "patchdata time here"
	http.patchData(getHTTPAddress(midiNum,midiType), data)
	return 0

#decided against using the cc_OSC as a json-config makes more sense
#repurpose for command-types from json (?)
#keeping it for lazy reference to switchers
def mtoType(argument):
    switcher = {
		"osc": "osc",
		"command": "command",
    	}
    return switcher.get(argument, "None")

def getCommand(midiNum, midiType):
	if(getType(midiNum, midiType) == 'command'):
		return MidiEvent(midiNum,midiType).command
	else:
		return 0

def isCC_OSC(midiNum, midiType):
	if(getType(midiNum, midiType) == 'osc'):
		return 1
	else:
		return 0

def getOSCAddress(midiNum, midiType):
	
	oscaddress = MidiEvent(midiNum,midiType).address
	return oscaddress

def getOSCValue(midiNum, midiValue, midiType):
	oscMin = float(MidiEvent(midiNum,midiType).min)
	oscMax = float(MidiEvent(midiNum,midiType).max)
	return (oscMax-oscMin)/127.0*midiValue+oscMin

def getHTTPAddress(midiNum, midiType):
	#old
	#address = str(config['oscConfig'][str(midiType)][str(midiNum)]['address'])
	#new
	address = MidiEvent(midiNum,midiType).address
	return address

def getHTTPValueAttribute(midiNum, midiValue, midiType):
	valAttr = getAttribute(midiNum, midiType)
	#print valAttr
	if (valAttr is None):
		valAttr = 'value'
	#valMax = float(config['oscConfig'][str(midiType)][str(midiNum)]['max'])
	return valAttr

def getHTTPValue(midiNum, midiValue, midiType):
	valMin = float(MidiEvent(midiNum,midiType).min)
	valMax = float(MidiEvent(midiNum,midiType).max)
	return (valMax-valMin)/127.0*midiValue+valMin

""" 
    float oscVal = (float) oscUIDial.getValue();
    float oscScaled = 4*(1 - (log(oscVal)/log(0.0001)));
   // float oscScaled = 4*(exp(oscVal)-1)/(2.71828-1);
    float pwrOf = 200;
    //oscScaled = 4*oscUIDial.getValue();
    oscScaled = 4*(pow(pwrOf,oscVal)-1)/(pwrOf-1);
    oscSendEditor.send ("/mix/chan/35/matrix/fader", (float) oscScaled); 
"""

def getOscMessage(midiNum, midiValue, midiType):
	oscMsg = OSC.OSCMessage()
	oscMsg.setAddress(getOSCAddress(midiNum, midiType))
	oscMsg.append(getOSCValue(midiNum, midiValue, midiType))
	return oscMsg

def debugCommands():
	print getType(2,'control_change')
	print getType(52,'control_change')
	print getType(50,'control_change')

	print isCC_OSC(50,'control_change')
	print isCC_OSC(52,'control_change')

	print getCommand(60,'note_on')
	print getCommand(61,'note_on')

	mtoAction(22,127,'control_change')
	mtoAction(61,127,'note_on')

	mtoAction(52,127,'control_change')
	mtoAction(22,127,'control_change')

	print MidiEvent(22, 'control_change')
	print MidiEvent(52, 'control_change')
	print MidiEvent(121, 'control_change').max
	#print conf

	print type(conf.debug)
	print type(conf.port)
	print type(conf.IP)

	print type(MidiEvent(22, 'control_change').max)
	print type(MidiEvent(52, 'control_change').max)
	print MidiEvent(52, 'control_change').max
	print type(MidiEvent(121, 'control_change').max)
	midiEvent = configHandler.MidiEvent(conf.control_change.get("52"))
	print midiEvent


reloadConfig()

reconnectOSC()
reconnectHTTP()

#print conf.IP
#print conf.port
#print conf.getConfig()#
#print conf.config_json
#print dir(conf)

#osc.connect((str(conf.IP),int(conf.port)))

print ""
print "Available MIDI Inputs: "
print mido.get_input_names()
print ""

print "Listening on device: "
print conf.midiDeviceInput
print "Listening on channel (0-15), i.e. 0 = midi 1, 15 = midi 16 etc: "
print conf.midiChannelInput

#print MidiEvent(52, 'control_change')

# print type(definedMidi)
# for mtype in definedMidi:
#     if mtype in conf.definedMidi.keys():
#         print mtype
#         for mnum in filter(lambda mnum: mnum in conf.definedMidi[mtype], definedMidi[mtype]):
#             #if mnum in conf.definedMidi[mtype]
#             print type(mnum)
#             print mnum

def isDefinedMidiLookup(midiNum, midiType, midiCh = -1):
    if(midiCh == conf.midiChannelInput or midiCh == -1):
        if(midiType in conf.definedMidi.keys()):
            if(midiNum in conf.definedMidi[midiType]):
                return True
    return False

def getMidiValue(msg):
	if(msg.type == 'control_change'):
		return msg.value
	if(msg.type == 'note_on' or msg.type == 'note_off'):
		return msg.velocity
	return -1

def getMidiNum(msg):
	if(msg.type == 'control_change'):
		return msg.control
	if(msg.type == 'note_on' or msg.type == 'note_off'):
		return msg.note
	return -1

def isDefinedMidi(msg):
	#print getattr(msg, 'channel', None)
	if(getattr(msg, 'channel', None)==getMIDIInputChannel()):
    #if(midiCh == conf.midiChannelInput or midiCh == -1):
		#print msg.type
		if(msg.type in conf.definedMidi.keys()):
			#print getMidiNum(msg)
			#print getMidiValue(msg)
			if(getMidiNum(msg) in conf.definedMidi[msg.type]):
				return True
	return False

#debugCommands()
with mido.open_input(conf.midiDeviceInput) as inport:
	for msg in inport:
		if(isDefinedMidi(msg)):
			mtoAction(getMidiNum(msg), getMidiValue(msg), msg.type)
		#debug handling to control print
		#print(msg)
			