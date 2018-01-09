#!/usr/bin/python

import argparse
import sys
import os
import io
import StringIO
import gzip
from socket import *
from thread import *

#Section of flags and globak variable declarations
#These items are to be set and passed to various functions
#Many of then are used in the logging section in particular

#flags to implemented speed functions if requested
isProxyCompres = False
isThreading = False
#set to X by default and changed to O if user set flag
mul = 'X'
cp = 'X'
#header derived logging info
isOK = None 
myme = None
sizu = 0

#driver-like functioned called by multithread
#This function receives the client socket and information
#It then calls the method that extracts header info and sorts it
#it then calls the method that sends that info to the server, receives it
#and sends it back to the client
#it then prints the logs to the terminal

def wholeProg(clientConSock, clientAddr, count1, clientInfo):
#make sure the client isn't empty
	if clientInfo != "":
#pass correct info to formatting method
		host, port, formattedClientInfo = sortReqData(clientConSock, clientInfo, clientAddr)	
#pass correct info to send to server method
		proxyToInt(host, port, formattedClientInfo, clientConSock, clientAddr)	

#initialize empty string to append in order	
#refer to global variables used in logs
#all logs
		finalLog=""
		global mul
		global cp
		v1= ("starting proxy server on port " + str(clientAddr[1]))
		v18=("[" + mul + "]"  + " " + "MT"  + " " +  "|"  + " " + "["  + cp  + "]"  + " " + "COMP"  + " " + "|" + " "  + "[" + "X" + "]" + " "  + "CHUNK" + " "  +  "|" + " "  + "[" + "X" + "]" + " "  + "PC")
		v2= "-------------------------------------------"
		v3= str(count1)	
		v4=("[CLI connected to " + str(clientAddr[0]) + ":" + str(clientAddr[1]) + "]")
		v5=("[CLI ==> PRX --- SRV]")
		v6=(" > " + str(typu) + " ")
		v7=("[CLI connected to " + str(host) + ":80" + "]")	
		v8=("[CLI --- PRX ==> SRV]")
		v9=(" > " + str(host) + " ")
		v10=("[CLI --- PRX <== SRV]")
		v11=(" > " + str(isOK) + " ")
		v12=(" > " + str(myme) + " " + str(sizu) + "bytes ")
		v13=("[CLI <== PRX --- SRV]")
		v14=(" > " + str(isOK) + " ")
		v15=(" > "  + str(myme) + " " + str(sizu) + "bytes ")
		v16=("[CLI disconnected]")
		v17=("[SRV disconnected]")
#append all of the strings
		finalLog+=v1
		finalLog+='\n'
		finalLog+=v18
		finalLog+='\n'
		finalLog+=v2	
		finalLog+='\n'
		finalLog+=v3	
		finalLog+='\n'
		finalLog+=v4	
		finalLog+='\n'
		finalLog+=v5	
		finalLog+='\n'
		finalLog+=v6
		finalLog+='\n'
		finalLog+=v7
		finalLog+='\n'
		finalLog+=v8
		finalLog+='\n'
		finalLog+=v9
		finalLog+='\n'
		finalLog+=v10
		finalLog+='\n'
		finalLog+=v11
		finalLog+='\n'
		finalLog+=v12
		finalLog+='\n'
		finalLog+=v13
		finalLog+='\n'
		finalLog+=v14
		finalLog+='\n'
		finalLog+=v15
		finalLog+='\n'
		finalLog+=v16
		finalLog+='\n'
		finalLog+=v17
		finalLog+='\n'
#print them all at once
		print finalLog

#Beginning is the method that deals with all of the system args, it also opens 
#the client sockets so that they may send requests to the proxy.
def Begin():
	try:
#inititalize the socket
		print 'initializing'
		global isThreading 
		global isProxyCompres
		global mul
		global cp
		if len(sys.argv) > 1:
#if the user has to 	
			for i in sys.argv[1:]:
				if i.isdigit():
					serverPort = int(i)
				if "mt" in i or "MT" in i: 
					isThreading = True
					mul = 'O'
				if "comp" in i or "COMP" in i: 
					isProxyCompres = True
					cp = 'O'
#make sure they've entered a port
		if len(sys.argv) <= 1:
			print('please enter a port address arg')
			sys.exit(2)
#get and save the port for later
#initialize the socket
		myS = socket(AF_INET, SOCK_STREAM)
#allow the same address to be reused
		myS.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
#bind the port
		myS.bind(('', serverPort))
#begin listening for requests 
		myS.listen(1)
		print 'server is ready to recieve'
	except Exception, e: 
		print e
		sys.exit(2)
#initialize the count variable for connections
	count1 = 1
#this loop continuously takes in new requests, within this loop it 
#also continuously calls the threading function if it is turned on 
#otherwise it just calls the driver function as a normal,
#sequential method
#the loops accepts the information from the socket, recieves it and decodes it
#it then sends that info to the wholeProj function/method.
	while True:
		try:
#get Client info in new socket
			clientConSock,clientAddr = myS.accept()
			clientInfo = clientConSock.recv(1040).decode()
#if the boolean is set from the opt being requested
			if isThreading:
#start a new thread with my function correctly sorting the client request data
 				start_new_thread(wholeProg, (clientConSock, clientAddr, count1, clientInfo))
#call it like noromal if threading not turned on
			else: wholeProg(clientConSock, clientAddr, count1, clientInfo)
			count1+=1
		except KeyboardInterrupt:	
			myS.close()
			sys.exit(1)

#the function that takes in the clients socket information and address
#This method makes sure the header and body info is correctly sorted, and
#parses through the headers to check or extract desired info like the host
#and port, accept encoding and to remove hop by hop headers
def sortReqData(clientConSock, clientInfo, clientAddr):
	try:
#split the client information 
		splitInfo = clientInfo.split('\r\n')
#variable declarations for edited headers and header info		
		formattedClientInfo = ""
		host=""
		port=""
		global typu
		global isProxyCompres
#loop through each line in splitInfo
		for line in splitInfo:		
			typu = splitInfo[0]
#split by sections devided by colons and if there are three seperate ones there is a non default port
#correctly get the post and host name without spaces
			if "Host: " in line:
				item = line.split(":")	
#take the host as the first element forward	
				host = item[1]
				host = host[1:]
				if len(item) > 2:
					port = item[2]	
				else:
#default port 80
					port = 80
#remove the headers that a proxy should
			if (not "Upgrade"in line) and (not "Keep-Alive: "in line) and (not "TE: "in line) and (not "Connection: " in line) and (not "Trailer: "in line) :
				formattedClientInfo+=line+'\r\n'

			if "Accept-Encoding: gzip" not in line:
#if the client doesn't except zipz don't send it
				proxyCompress = False
#make sure theres two spaces at the end
		formattedClientInfo+='\r\n'
#display it 
		print formattedClientInfo
		return host, port, formattedClientInfo
		
	except KeyboardInterrupt:	
		print 'you have chosen to stop the proxy'
		myS.close()
		sys.exit(1)

#This method is also called by the wholeProg, it creates a socket to the server and sends the clients information and requests
#it also determines weather or not the clients that accept encoding have received back their zip file and appropriate headers
def proxyToInt(host, port, formattedClientInfo, clientConSock, clientAddr):
#init, connect and send the client info over second socket
	secondS = socket(AF_INET, SOCK_STREAM)
	secondS.connect((host, 80))
	secondS.send(formattedClientInfo)
#variables that store logging data
	global isOK
	global myme
	global sizu
	global isProxyCompres
	bodyReply = None
	isFirst = True
#continueously receive the requested data from the server, then send it back through the socket to the client
	while True:
#get the reply from the internet
		intReply = secondS.recv(8192)
#only do header things upon first request
		if isFirst:
			encodedReply = ""
			insertContHead = False
			dontInsert = False
			headerReply = intReply.split('\r\n\r\n')[0]
#headers split line by line
			splitBodyReply = headerReply.split('\r\n')
#body seperated from headers
			bodyReply = intReply.split('\r\n\r\n')[1]
			for line in splitBodyReply:
#find the line with the Status code
				if "HTTP/1.1" in line:
					isOK = line[9:]
#find the line with the myme type
				if "Content-Type" in line:
					myme = line[14:]
#if the flag is still set bc client accepts zipz
				if isProxyCompres:
#if this content header is in the response, the file is zipped and can be sent to the client that requested it
					if "Content-Encoding: gzip" in line:
#if the header is not in the response it is not zipped and should be
						insertContHead = False
					if "Content-Encoding: gzip" not in line:
						insertContHead = True
#if the proxy requests encoding, client is accepting, and the file is not zip	
				if insertContHead:
#add content if its not already there
					encodedReply+=line+'\r\n'
#after looping through the header if we should insert the header
			if insertContHead:
#amake a new header string with the encoding at the end 
				encodedReply+='Content-Encoding: gzip'+'\r\n'
				encodedReply+='\r\n'
#never do it touch header info for the rest of the body
			isFirst = False
		zipped =None
		out = None
		FILENAME= None
#if we're done looping through the headers, attach first body from first response to the rest of the responses (which only have body data)		
		if not isFirst:
			bodyReply+=intReply
#should zip only the bodies of the rest
			out = StringIO.StringIO()
			with gzip.GzipFile(fileobj=out, mode="w") as zipped:
				zipped.write(bodyReply)
#make sure that the reply is not empty to get len and send
		if (len(intReply) > 0):
			sizu = len(intReply)
#if the user turned on compress data
			if isProxyCompres:
				if insertContHead:
#send correctly adjusted header
					clientConSock.send(encodedReply)
#send correctly zipped value			
					print encodedReply
					clientConSock.send(out.getvalue())
				if not insertContHead:
#send the reply zipped and unseperated as it normally is
					clientConSock.send(intReply)
#if the user didn't request compression send it as normal
			else: clientConSock.send(intReply)
#if the reply no longer has any size close the sockets and end the prog	
		else:
			secondS.close()
			clientConSock.close()
			break
#start here
Begin()

