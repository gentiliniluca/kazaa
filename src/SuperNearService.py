import SuperNear
import DBException
import Util
import sys

class SuperNearService:
    
    #global MAXSUPERNEARS 
    #MAXSUPERNEARS = 3
    
    @staticmethod
    def insertNewSuperNear(database, ipp2p, pp2p):
        
        try:
            superNear = SuperNearService.getSuperNear(database, ipp2p, pp2p)
        except:            
            if SuperNearService.getSuperNearsCount(database) < Util.MAXSUPERNEARS:
                superNear = SuperNear.SuperNear(None, ipp2p, pp2p)
                superNear.insert(database)
            else:
                raise DBException.DBException("Max nears number reached!")        
        return superNear
    
    @staticmethod
    def getSuperNear(database, ipp2p, pp2p):
        #print("entro")
        database.execute("""SELECT idsupernear, ipp2p, pp2p
                            FROM supernear
                            WHERE ipp2p = %s AND pp2p = %s""",
                            (ipp2p, pp2p))
        
        idsupernear, ipp2p, pp2p = database.fetchone()
        
        superNear = SuperNear.SuperNear(idsupernear, ipp2p, pp2p)
        
        return superNear
    
    @staticmethod
    def getSuperNears(database):
        
        database.execute("""SELECT idsupernear, ipp2p, pp2p
                            FROM supernear""")
        
        superNears = []
        
        try:
            while True:
                idsupernear, ipp2p, pp2p = database.fetchone()
                superNear = SuperNear.SuperNear(idsupernear, ipp2p, pp2p)
                superNears.append(superNear)
        except:
            pass
            #print (sys.exc_info())
                
        return superNears
    
    @staticmethod
    def getSuperNearsCount(database):
        database.execute("""SELECT count(*)
                            FROM supernear""")
        count, = database.fetchone()
        return count