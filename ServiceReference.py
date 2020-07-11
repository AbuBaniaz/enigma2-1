from enigma import eServiceReference, eServiceCenter, getBestPlayableServiceReference
import NavigationInstance

def getPlayingRef():
	playingref = None
	if NavigationInstance.instance:
		playingref = NavigationInstance.instance.getCurrentlyPlayingServiceReference()
	return playingref or eServiceReference()

def isPlayableForCur(serviceref):
	info = eServiceCenter.getInstance().info(serviceref)
	return info and info.isPlayable(serviceref, getPlayingRef())

def resolveAlternate(serviceref):
	nref = None
	if serviceref.flags & eServiceReference.isGroup:
		nref = getBestPlayableServiceReference(serviceref, getPlayingRef())
		if not nref:
			nref = getBestPlayableServiceReference(serviceref, eServiceReference(), True)
	return nref


# These 2 methods can be moved into eServiceReference at some point
eServiceReference.isRecordable = lambda serviceref: serviceref.flags & eServiceReference.isGroup or (serviceref.type == eServiceReference.idDVB or serviceref.type == eServiceReference.idDVB + 0x100 or serviceref.type == 0x2000 or serviceref.type == eServiceReference.idServiceMP3)
eServiceReference.isPlayback = lambda serviceref: "0:0:0:0:0:0:0:0:0" in serviceref.toCompareString()

# Apply ServiceReference method proxies to the eServiceReference object so the two classes can be used interchangeably
# Extensions to eServiceReference
eServiceReference.__str__ = eServiceReference.toString

def __getServiceName(serviceref):
	info = eServiceCenter.getInstance().info(serviceref)
	return info and info.getName(serviceref) or ""
eServiceReference.getServiceName = __getServiceName

# Compatibility proxies for obsolete ServiceReference class methods
def __info(serviceref):
	return eServiceCenter.getInstance().info(serviceref)
eServiceReference.info = __info

def __list(serviceref):
	return eServiceCenter.getInstance().list(serviceref)
eServiceReference.list = __list

def __getRef(serviceref):
	return serviceref

def __setRef(self, serviceref):
	eServiceReference.__init__(self, serviceref)
eServiceReference.ref = property(__getRef, __setRef,)

def __getType(serviceref):
	return serviceref.type
eServiceReference.getType = __getType

def __getFlags(serviceref):
	return serviceref.flags
eServiceReference.getFlags = __getFlags


# Wrapper class for eServiceReference, kept for compatibility
# Don't use this for new code. eServiceReference now supports everything in one single type
class ServiceReference(eServiceReference):
	def __new__(cls, ref, reftype=eServiceReference.idInvalid, flags=0, path=''):
		# if trying to copy an eServiceReference object, turn it into a ServiceReference type and return it
		if reftype == eServiceReference.idInvalid and isinstance(ref, eServiceReference):
			new = ref
			new.__class__ = ServiceReference
			return new
		return object.__new__(cls, ref, reftype, flags, path)

	def __init__(self, ref, reftype=eServiceReference.idInvalid, flags=0, path=''):
		if reftype != eServiceReference.idInvalid:
			eServiceReference.__init__(self, reftype, flags, path)
		elif not isinstance(ref, eServiceReference):
			eServiceReference.__init__(self, ref or "")
