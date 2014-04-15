import Connessione
import os
import socket
import Util
import sys

from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL)

class Server:
    
    global SIZE
    SIZE = 1024
    
    stringa_ricevuta_server = ""
    
    @staticmethod
    def initServerSocket():
        
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((Util.HOST, Util.PORT))
        s.listen(5)
        return s
    
    @staticmethod
    def expiredPacketHandler():
        
        conn_db = Connessione.Connessione()
        PacketService.PacketService.deleteExpiredPacket(conn_db.crea_cursore())
        conn_db.esegui_commit()
        conn_db.chiudi_connessione()
        
    @staticmethod
    def readSocket(client):
        
        stringa_ricevuta_server = client.recv(SIZE)
        print("\t\t\t\t\t\t\t\t\tlato server ho ricevuto: " + stringa_ricevuta_server)
        if stringa_ricevuta_server == "":
            print("\t\t\t\t\t\t\t\t\t\t\t\tsocket vuota")
        else:      
            print("\n\t\t\t\t\t\t\t\t\tMESSAGGIO RICEVUTO: ")
        return stringa_ricevuta_server
