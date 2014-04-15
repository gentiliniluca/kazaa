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
            if(USEMODE=="PEER"):
                print("\n************************\n*  1 - Ricerca File    *\n*  2 - Login           *\n*  3 - Carica File     *\n*  4 - Download File   *\n*  5 - Rimuovi File    *\n*  6 - Logout          *\n*  0 - Fine            *\n************************")
            else:
                print("\n************************\n*  1 - Ricerca File    *\n*  2 - Carica File     *\n*  3 - Carica File     *\n*  4 - Download File   *\n*  5 - Rimuovi File    *\n*  0 - Fine            *\n************************")
            out=raw_input("\n\tOperazione scelta: ")
            if(USEMODE=="PEER" and (int(out) >= 0 and int(out) <= 6 ) or USEMODE=="SUPERPEER" and(int(out) >= 0 and int(out) <= 5) ):
                break
            print("Valore inserito errato!")
        
        return out
    