#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getopt
import os
import signal
import sys
import EsPeEs
from SOAPpy import SOAPServer

global EsPeEsSOAPServer
global EsPeEsServer

class P(object):
    EsPeEsSOAPServer = None
    EsPeEsServer = None

def usage():
    usage = '\nUsage of EsPeEs-Server:\n\n'
    usage += 'EsPeEs-Server [--port=number] [--help]\n\n'
    usage += '           --port=number        - Sets the port-number of the server.\n'
    usage += '                                  Default is 9999.\n'
    usage += '           --help               - Shows this help.\n'
    print usage

def OnCtrlC(signal, frame):
    print '\rServer shutdown request received. Please wait.\n'
    kill()
    sys.exit()
    
def run(port):
    try:
        saveLastUsedPort(port)
        P.EsPeEsSOAPServer = SOAPServer(('', port))
        P.EsPeEsServer = EsPeEs.Server()
        P.EsPeEsSOAPServer.registerObject(P.EsPeEsServer)
        P.EsPeEsSOAPServer.serve_forever()
    except Exception, e:
        kill()
        sys.exit()
        
def kill():
    try:
        P.EsPeEsServer.stopPLC()
        P.EsPeEsSOAPServer = None
    except Exception, e:
        pass
    
def saveLastUsedPort(port):
    espees_plc = os.path.join(EsPeEs.getSaveFolder(), 'lastUsedPort.xml')   #/home/USER/.EsPeEs/lastUsedPLC.xml
    if not os.path.exists(EsPeEs.getSaveFolder()):
        EsPeEs.Utilities.makeDirectory(EsPeEs.getSaveFolder())
    EsPeEs.Utilities.writeToFile(EsPeEs.Utilities.objectToJson(port), espees_plc)

if __name__ == '__main__':    
    if not (len(sys.argv[1:]) == 1):
        signal.signal(signal.SIGINT, OnCtrlC)
        print '\nPress Ctrl + C to shutdown the server.\n'
        run(EsPeEs.Preferences.DefaultPort)
        while True:
            pass
    try:
        opts, argv = getopt.getopt(sys.argv[1:], "hp", ['help', 'port='])
    except getopt.GetoptError, err:
        print '\nUnknown parameters set.'
        usage()
        sys.exit(2)
    for o, a in opts:
        if o in ("-p", "--port"):
            if not (a == None):
                try:
                    port = int(a)
                    signal.signal(signal.SIGINT, OnCtrlC)
                    print '\nPress Ctrl + C to shutdown the server.'
                    print 'Port: ' + a + '\n'
                    run(port)
                except ValueError:
                    print '\nNo port set.'
                    usage()
                    sys.exit()
            else:
                print '\nNo port set.'
                usage()
                sys.exit()
        if o in ("-h", "--help"):
            usage()
            sys.exit()
