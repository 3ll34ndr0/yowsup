#!/usr/bin/python
# coding: latin-1
# La segunda línea (# coding: latin-1) es necesaria para poder usar acentos y ñ. Para entender el porqué, visitar:
# http://www.python.org/dev/peps/pep-0263/

from yowsup.layers.protocol_messages.protocolentities  import TextMessageProtocolEntity

from yowsup.layers.interface                           import YowInterfaceLayer, ProtocolEntityCallback
import duckduckgo # API site: 
import time
import json
import sqlite3 # Cambiarlo de lugar para que sea mas óptimo (quizás mas arriba)
from yowsup.layers.protocol_chatstate.protocolentities   import *
from dbapi import *
from manager import ManageAppointments
# Por ahora no lo agrego
# Para dar órdenes usando https://github.com/nate-parrott/commanding 
#from commanding import Phrase, parse_phrase 
#from turnos 	import examples, regexes
def jdefault(o):
	return o.__dict__

class AppointmentsLayer(YowInterfaceLayer):
 
    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):

	fileName = messageProtocolEntity.getFrom(False).encode('utf-8')
        logFileName = fileName+".log"
        messagesFileName = fileName+".messages"
        with open(messagesFileName, "r") as file:                            
            messagesBuffer = file.readlines()                                     
                                                                    
	messagesBuffer = map(lambda pl: pl.rstrip('\n').split(','),messagesBuffer)    
	# TODO:test if file is biger than 50 lines and drop the oldest massages to
	#       to avoid the file grow too big.

        if messageProtocolEntity.getType() == 'text':
            mensajeTexto = ""
            mensajeTexto = self.onTextMessage(messageProtocolEntity)
	    print("volvioooo")
        elif messageProtocolEntity.getType() == 'media':
#            mensajeTexto = self.onTextMessage(messageProtocolEntity)
            mensajeTexto = "Nothing defined for media yet..."
            self.onMediaMessage(messageProtocolEntity)
#This was the original echo:
#        self.toLower(messageProtocolEntity.forward(messageProtocolEntity.getFrom()))
        self.toLower(messageProtocolEntity.ack())
        self.toLower(messageProtocolEntity.ack(True))
#end of commented code
# Leo el mensaje en una variable

	respuesta = mensajeTexto
	# De alguna forma tengo que buscar su último mje..."
	#Cuando es admin:
        print("Va a checar si {} es inicio".format(respuesta))
	if respuesta.lower() == "inicio":
		print("Hay inicio")
		textoMenu = """1. Configuraciónes
		2. Acción y
		3. Finalizar"""
		self.humanBehaviour(messageProtocolEntity, textoMenu, 4,logFileName)


# Menu de opciones
#	textoMenu = """1. Reservar turno
#	2. Cancelar turno
#        3. Activa/desactiva recordatorio
#        4. Finalizar"""
#	menuList = ["1","2","3","4"]
#	preguntaMenu = "Qué desea hacer?"
#	ans = respuesta in menuList
#        if not ans:
#    	    self.humanBehaviour(messageProtocolEntity, textoMenu, 4,logFileName)
#	    self.humanBehaviour(messageProtocolEntity, preguntaMenu, 4,logFileName)
#        elif respuesta == "1":
#	    self.humanBehaviour(messageProtocolEntity, "Ok, estos son los horarios disponibles: cri cri ...", 4,logFileName)
#        elif respuesta == "2":
#	    self.humanBehaviour(messageProtocolEntity, "Ok, turno cancelado", 4,logFileName)
#        elif respuesta == "3":
#	    self.humanBehaviour(messageProtocolEntity, "Recordatorio activado/desactivado", 4,logFileName)
#        elif respuesta == "4":
#	    self.humanBehaviour(messageProtocolEntity, "Ok, adios.", 4,logFileName)
#        else:
#	    self.humanBehaviour(messageProtocolEntity, "Opción no válida", 4,logFileName)





    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        print("Entra al receipt de :")
	print str(entity._id) # It seems to be a short usage of: entity.getId()
	print(json.dumps(entity,default=jdefault))
	## Log receipt and read
	if entity.getType()==None: #Could be better than this, but I needed the "receipt" text to appear instead of "None"
		mstate="receipt"
	else:
		mstate="read"
	with open(entity.getFrom(False).encode('utf-8')+".log",'a') as file: #filename
		file.write(str(entity._id)+","
				+mstate+","
				+"@"+str(entity._getCurrentTimestamp())+"\n"+
				json.dumps(entity,default=jdefault)+"\n")
	##
        self.toLower(entity.ack())

# Text message received, need special treatment:
    def onTextMessage(self,messageProtocolEntity):
        # just print info
	import time #revisar
	try:
	   mensajeEnUTF = messageProtocolEntity.getBody().encode('utf-8')
	   print("Repitiendo %s to %s" % (mensajeEnUTF, messageProtocolEntity.getFrom(False)))
	   mad = ManageAppointments(messageProtocolEntity.getFrom(False))
	   print("La cuenta es {} de {}".format(mad.accountType,mad.activity))
#	   return mensajeEnUTF
        except AttributeError as e:
	   print(e)
	   print("Vamo laj bandaaaa!")
# Abro/creo archivo para loguear conversación basado en número de celular
        logFileName = messageProtocolEntity.getFrom(False).encode('utf-8')+".log"
        print("Log file is: {}".format(logFileName))
        try:
		print("Va a tratar ...")
		with open(logFileName,'a') as file:
			file.write(mensajeEnUTF+"@"+str(time.time())+"\n"
					+json.dumps(messageProtocolEntity,default=jdefault)+"\n")
	except IOError as e:  
		print("File "+messageProtocolEntity.getFrom(False).encode('utf-8')+".log does not exist!") #Nunca falla, esta al dope
		print("Creating file ...")
		with open(messageProtocolEntity.getFrom(False).encode('utf-8')+".log",'w') as file:
			file.write("#Log file for "
					+messageProtocolEntity.getFrom(False).encode('utf-8')
					+"\n"
					+time.asctime()
					+","+mensajeTexto)

	return mensajeEnUTF
			
######################################



# Detecto órdenes:



#	quienMasAlias = str(messageProtocolEntity.getNotify())+"("+str(messageProtocolEntity.getAuthor(False))+")" 
       	quienMasAlias = str(messageProtocolEntity.getNotify()) 
        algoDicho = parse_phrase(mensajeTexto, examples, regexes)
	print algoDicho.intent

	if algoDicho.intent == 'make_an_appointment':
		textoRespuesta = str(quienMasAlias) + " quiere ir a las " + algoDicho.items[1][1].encode('utf-8')
		print textoRespuesta
	elif algoDicho.intent == 'cancel_an_appointment':
		textoRespuesta =  str(quienMasAlias) + " cancela el turno" 
		print textoRespuesta
	
#	elif algoDicho.intent == 'search': # Busca en duckduckgo
#               ddgresponde = duckduckgo.get_zci(messageProtocolEntity.getBody(), kad='es_ES').encode('utf-8')
#		print ddgresponde
#		textoRespuesta = quienMasAlias + ": " + ddgresponde
	elif algoDicho.intent == 'help':
		textoRespuesta =  quienMasAlias + ": sin respuestas, todavia."  
	elif algoDicho.intent == 'confirmation':
		textoRespuesta = 'Confirmacion'
	elif algoDicho.intent == 'negation':
		textoRespuesta = 'Negacion'
	else:
		textoRespuesta = "nada por aqui..."



# Construyo el mensaje de respuesta: 
# Arma objeto con respuesta
# Lo desactivo mientras pruebo el menu de opciones:
        
        """outgoingMessageProtocolEntity = TextMessageProtocolEntity(
	        textoRespuesta,
                to = messageProtocolEntity.getAuthor())
# Envia respuesta
	if messageProtocolEntity.getAuthor(False) == '5493515193486':
            entity = OutgoingChatstateProtocolEntity(			#Mando un "escribiendo"
			    ChatstateProtocolEntity.STATE_TYPING,
			    messageProtocolEntity.getAuthor())
            self.toLower(entity)
	    time.sleep(4)
	    self.toLower(outgoingMessageProtocolEntity)
        else:
	    print messageProtocolEntity.getFrom()
            entity = OutgoingChatstateProtocolEntity(			#Mando un "escribiendo"
			    ChatstateProtocolEntity.STATE_TYPING,
			    messageProtocolEntity.getAuthor())
            self.toLower(entity)
	    time.sleep(4)
	    self.toLower(outgoingMessageProtocolEntity)
	    time.sleep(1)"""

##############
# Mando un "recibido" y un "leido"
#        self.toLower(messageProtocolEntity.forward(messageProtocolEntity.getFrom())) # original
        self.toLower(messageProtocolEntity.ack())
	print("duerme unn segundo...........")
	time.sleep(1)
        self.toLower(messageProtocolEntity.ack(True))

    def onMediaMessage(self, messageProtocolEntity):
        # just print info
        if messageProtocolEntity.getMediaType() == "image":
            print("Echoing image %s to %s" % (messageProtocolEntity.url, messageProtocolEntity.getFrom(False)))

        elif messageProtocolEntity.getMediaType() == "location":
            print("Echoing location (%s, %s) to %s" % (messageProtocolEntity.getLatitude(), messageProtocolEntity.getLongitude(), messageProtocolEntity.getFrom(False)))

        elif messageProtocolEntity.getMediaType() == "vcard":
	    contactName=messageProtocolEntity.getName().encode('utf-8')
            vcardData=messageProtocolEntity.getCardData()
            print("Voy a crear una vcard   ... {}".format(vcardData.encode('utf-8')))
            createUserRegisterFromVCard('test.db',vcardData)
	    numero=messageProtocolEntity.getFrom(False).encode('utf-8')
	    print(dir(messageProtocolEntity))
#	    print(messageProtocolEntity.getParticipant())
#	    print(messageProtocolEntity.getParticipant())
#	    print(messageProtocolEntity.getNotify())
#            print("Haciendo Eco de vcard (%s, %s) to %s" % (contactName, vcardData, numero)))
	    with open('contactos.txt','a') as file:
		    file.write("\n"+numero+","+contactName+","+vcardData.encode('utf-8'))



    def humanBehaviour(self, messageProtocolEntity, textoSalida, typingTime,fileName:
	"""By now it only sends some "typing" signal.
	It is expected to emulate the human behaviour
	while writing and reading messages. It also save a log file and a message file.
	""" 
	import time
	def jdefault(o):
		return o.__dict__

        logFileName = fileName+".log"
	messagesFileName = fileName+".messages"
	# First I create the 'Mensaje' object
	print(textoSalida)
	entity = OutgoingChatstateProtocolEntity(   #Mando un "escribiendo" durante "typingTime"
			ChatstateProtocolEntity.STATE_TYPING,	
			messageProtocolEntity.getAuthor())
	outgoingMessageProtocolEntity = TextMessageProtocolEntity(
			    textoSalida,
			    to = messageProtocolEntity.getAuthor())
	sendingId = outgoingMessageProtocolEntity._id.encode('utf-8')
        self.toLower(entity)
	time.sleep(typingTime)
	print("Imprimo el ID del mje saliente: %s" % sendingId)
	with open(logFileName,'a') as file: #filename
		file.write(json.dumps(outgoingMessageProtocolEntity,default=jdefault)+"\n")
	self.toLower(outgoingMessageProtocolEntity)
	with (open(messagesFileName,'a') as file:
		file.write(self.onTextMessage(messageProtocolEntity)+"\")
	"""
	Delivery Notification:
	message_id 	A unique ID assigned to a message.
	timestamp 	The time of receiving a delivery notification from a mobile operator, in Unix time format.
	status 		The delivery status.

	Incoming message:
	message_id	A unique ID assigned to an incoming message.
	timestamp 	The time of receiving the message, in Unix time format.
	from 		The sender’s phone number.
	text 		The message’s text, in the UTF-8 character set.
	"""




