import Connessione
import FileService
import NearService
import PacketService
import os
import SearchResultService
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
        
    @staticmethod
    def nearHandler(stringa_ricevuta_server):
        
        pktid = stringa_ricevuta_server[4:20]
        ipp2p = stringa_ricevuta_server[20:59]
        pp2p = stringa_ricevuta_server[59:64]
        ttl = stringa_ricevuta_server[64:66] 
        
        print ("\t\t\t\t\t\t\t\t\tOperazione Near pktid: " + pktid + " ip: " + ipp2p + " porta: " + pp2p + " ttl: " + ttl)
        
        conn_db = Connessione.Connessione()
        try:            
            pkt = PacketService.PacketService.getPacket(conn_db.crea_cursore(), pktid)
        
        except:
            pkt = PacketService.PacketService.insertNewPacket(conn_db.crea_cursore(), pktid)
                        
            print("\t\t\t\t\t\t\t\t\t Ricerca vinici - pkt non presente, se ttl > 1 invio  * valore ttl= "+str(ttl))
            if(int(ttl) > 1):
                # invio a vicini tranne mittente
                vicini = []
                vicini = NearService.NearService.getNears(conn_db.crea_cursore())
                ttl = int(ttl) - 1
                
                i = 0
                while i < len(vicini):
                    if(vicini[i].ipp2p != ipp2p and vicini[i].pp2p != pp2p):
                        print("\t\t\t\t\t\t\t\t\tinoltro near a vicini****" + " " + vicini[i].pp2p + " " + vicini[i].ipp2p + " con ttl " + str(ttl))
                        try:
                            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                            sock.connect((vicini[i].ipp2p, int(vicini[i].pp2p)))
                            stringa_ricevuta_server = "NEAR" + pktid + ipp2p + Util.Util.adattaStringa(5, str(pp2p)) + Util.Util.adattaStringa(2, str(ttl))
                            sock.send(stringa_ricevuta_server.encode())
                        except:
                            print("Il vicino " +vicini[i].ipp2p+"  "+vicini[i].pp2p + " non e' online")
                    i = i + 1
                    
                stringa_risposta = "ANEA" + pktid + Util.HOST + Util.Util.adattaStringa(5, str(Util.PORT))
                print("\t\t\t\t\t\t\t\t\trispondo con " + stringa_risposta)
                
                sockr = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                sockr.connect((ipp2p, int(pp2p)))
                sockr.send(stringa_risposta.encode())
            else:
                if(int(ttl)==1):
                    stringa_risposta = "ANEA" + pktid + Util.HOST + Util.Util.adattaStringa(5, str(Util.PORT))
                    print("\t\t\t\t\t\t\t\t\trispondo con " + stringa_risposta)
                    sockr = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                    sockr.connect((ipp2p, int(pp2p)))
                    sockr.send(stringa_risposta.encode())
                
        finally:            
            conn_db.esegui_commit()
            conn_db.chiudi_connessione()
            
    @staticmethod
    def addNewNear(stringa_ricevuta_server):
                
        pktid = stringa_ricevuta_server[4:20]
        ipp2p = stringa_ricevuta_server[20:59]
        pp2p = stringa_ricevuta_server[59:64]
        
        print("\t\t\t\t\t\t\t\t\tOperazione Anea pktid: " + pktid + " ip: " + ipp2p + " porta: " + pp2p)
        #inserisco su db il vicino con ipp2p e porta
        
        try:            
            conn_db = Connessione.Connessione()
            if(Util.MAX_NEARS>int(NearService.NearService.getNearsCount(conn_db.crea_cursore()))):
                vicino = NearService.NearService.insertNewNear(conn_db.crea_cursore(), ipp2p, pp2p)
        
        except:            
            print("\t\t\t\t\t\t\t\t\tInserimento di vicino non effettuato")
            
        finally:            
            conn_db.esegui_commit() 
            conn_db.chiudi_connessione()
    
    @staticmethod
    def searchHandler(stringa_ricevuta_server):
        pktid = stringa_ricevuta_server[4:20]
        ipp2p = stringa_ricevuta_server[20:59]
        pp2p = stringa_ricevuta_server[59:64]
        ttl = stringa_ricevuta_server[64:66]
        ricerca_con_spazi = stringa_ricevuta_server[66:86]
        ricerca = Util.Util.elimina_spazi_iniziali_finali(stringa_ricevuta_server[66:86])
        ricerca = Util.Util.elimina_asterischi_iniziali_finali(ricerca)
        
       
        conn_db = Connessione.Connessione()
        try:
            pkt = PacketService.PacketService.getPacket(conn_db.crea_cursore(), pktid)
            
        except:

            pkt = PacketService.PacketService.insertNewPacket(conn_db.crea_cursore(), pktid)
            conn_db.esegui_commit()
            conn_db.chiudi_connessione()
            print("\t\t\t\t\t\t\t\t\t Ricerca file - pkt non presente, se ttl > 1 invio  * valore ttl= "+str(ttl))
            if(int(ttl) > 1):
                conn_db = Connessione.Connessione()
                files = []
                files = FileService.FileService.getFiles(conn_db.crea_cursore(), ricerca)
                i = 0
                ttl = int(ttl) - 1
                while i < len(files):
                    print ("\t\t\t\t\t\t\t\t\tinoltro file al richiedente****" + " " + files[i].filemd5 + " " + files[i].filename)

                    stringa_risposta = "AQUE" + pktid + Util.HOST + Util.Util.adattaStringa(5, str(Util.PORT)) + files[i].filemd5 + files[i].filename
                    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                    sock.connect((ipp2p, int(pp2p)))
                    sock.send(stringa_risposta) #attenzione enconde
                    sock.close()
                    i = i + 1

                conn_db.esegui_commit()
                conn_db.chiudi_connessione()

                conn_db = Connessione.Connessione()
                vicini = []
                vicini = NearService.NearService.getNears(conn_db.crea_cursore())
                i = 0
                while i < len(vicini):
                    if(vicini[i].ipp2p != ipp2p and vicini[i].pp2p != pp2p):
                        print ("\t\t\t\t\t\t\t\t\tinoltro QUER a vicini****" + " " + vicini[i].pp2p + " " + vicini[i].ipp2p)
                        try:
                            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                            sock.connect((vicini[i].ipp2p, int(vicini[i].pp2p)))
                            stringa_ricevuta_server = "QUER" + pktid + ipp2p + Util.Util.adattaStringa(5, str(pp2p)) + Util.Util.adattaStringa(2,str(ttl)) + ricerca_con_spazi
                            sock.send(stringa_ricevuta_server.encode())
                            #chiudere socket????? sock.cloese()
                        except:
                            print("Il vicino " +vicini[i].ipp2p+"  "+vicini[i].pp2p + " non e' online")
                    i = i + 1
            else:
                if(int(ttl)==1):
                    conn_db = Connessione.Connessione()
                    files = []
                    files = FileService.FileService.getFiles(conn_db.crea_cursore(), ricerca)
                    i = 0
                    while i < len(files):
                        print ("\t\t\t\t\t\t\t\t\tinoltro file al richiedente****" + " " + files[i].filemd5 + " " + files[i].filename)

                        stringa_risposta = "AQUE" + pktid + Util.HOST + Util.Util.adattaStringa(5, str(Util.PORT)) + files[i].filemd5 + files[i].filename
                        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                        sock.connect((ipp2p, int(pp2p)))
                        sock.send(stringa_risposta) #attenzione enconde
                        sock.close()
                        i = i + 1
        
        finally:
            conn_db.esegui_commit()
            conn_db.chiudi_connessione()
    
    @staticmethod
    def searchResultHandler(stringa_ricevuta_server):
        print(stringa_ricevuta_server) 
        
        pktid = stringa_ricevuta_server[4:20]
        ipp2p = stringa_ricevuta_server[20:59]
        pp2p = stringa_ricevuta_server[59:64]
        filemd5 = stringa_ricevuta_server[64:80]
        filename = stringa_ricevuta_server[80:180]
        
        filename = Util.Util.elimina_spazi_iniziali_finali(filename)
        filename = Util.Util.elimina_asterischi_iniziali_finali(filename)
        
        conn_db = Connessione.Connessione()
        sr = SearchResultService.SearchResultService.insertNewSearchResult(conn_db.crea_cursore(), ipp2p, pp2p, filemd5, filename)
        
        conn_db.esegui_commit()
        conn_db.chiudi_connessione()
    
    @staticmethod
    def uploadHandler(client, stringa_ricevuta_server):
        
        chunkLength = 1024
        filemd5 = stringa_ricevuta_server[4:20]
        
        try:
            conn_db = Connessione.Connessione()
            
            file = FileService.FileService.getFileMD5(conn_db.crea_cursore(), filemd5)
            
            conn_db.esegui_commit()
            conn_db.chiudi_connessione()

            if os.stat(Util.LOCAL_PATH + file.filename).st_size % chunkLength == 0:
                nChunk = os.stat(Util.LOCAL_PATH + file.filename).st_size // chunkLength
            else:
                nChunk = (os.stat(Util.LOCAL_PATH + file.filename).st_size // chunkLength) + 1
            
            nChunk = str(nChunk).zfill(6)
            sendingString = "ARET".encode()
            sendingString = sendingString + nChunk.encode()
            
            openedFile = open(Util.LOCAL_PATH + file.filename, "rb")

            while True:
                chunk = openedFile.read(chunkLength)
                if len(chunk) == chunkLength:
                    sendingString = sendingString + str(chunkLength).zfill(5).encode()
                    sendingString = sendingString + chunk
                else:
                    sendingString = sendingString + str(len(chunk)).zfill(5).encode()
                    sendingString = sendingString + chunk
                    break
            
#            while True:
#                m = sendingString[:1024] 
#                i = i+1               
#                client.send(m)                    
#                if len(m) < 1024:
#                    break
#                sendingString = sendingString[1024:]
            client.sendall(sendingString)
            
            openedFile.close()
            
        except:
            print sys.exc_info()
            print("File not found!")
