import Connessione
import random
import socket
import string
import Util

from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL)

class Client:
    
    @staticmethod
    def visualizza_menu_principale():
        
        while True:
            if(Util.USEMODE=="PEER"):
                print("\n************************\n*  1 - Ricerca File    *\n*  2 - Login           *\n*  3 - Carica File     *\n*  4 - Download File   *\n*  5 - Rimuovi File    *\n*  6 - Logout          *\n*  0 - Fine            *\n************************")
            else:
                print("\n************************\n*  1 - Ricerca File    *\n*  2 - Carica File     *\n*  3 - Download File   *\n*  4 - Rimuovi File    *\n*  0 - Fine            *\n************************")
            out=raw_input("\n\tOperazione scelta: ")
            if(Util.USEMODE=="PEER" and (int(out) >= 0 and int(out) <= 6 ) or Util.USEMODE=="SUPERPEER" and(int(out) >= 0 and int(out) <= 4) ):
                break
            print("Valore inserito errato!")
        
        return out
    
    
    @staticmethod
    def login(SessionID):
        stringa_da_trasmettere="LOGI"+Util.HOST+Util.Util.adattaStringa(5,str(Util.PORT) )
        try:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            sock.connect((Util.IPSuperPeer, int(Util.PORTSuperPeer) ))
            sock.send(stringa_da_trasmettere.encode())
            risposta=sock.recv(21)
            print(risposta)
            nuovosessionid=risposta[4:20]
            sock.close()
        except Exception as e:
            print e
            print "Errore login"
        if(nuovosessionid=="0000000000000000"):
            return SessionID
        else:
            return nuovosessionid
            
    @staticmethod
    def logout(SessionID):
        print(SessionID+"nel logout")
        if(SessionID != "" and SessionID != "0000000000000000"):
            stringa_da_trasmettere="LOGO"+SessionID
            print("str da trasmeteer" +stringa_da_trasmettere)
            try:
                sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                sock.connect((Util.IPSuperPeer, int(Util.PORTSuperPeer) ))
                sock.send(stringa_da_trasmettere.encode())
                sock.close()
            except Exception as e:
                print e
                print "Errore logout"
        return ""
    