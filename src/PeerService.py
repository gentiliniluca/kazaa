import Peer

class PeerService:
    
    @staticmethod
    def insertNewPeer(database, ipp2p, pp2p):
        peer = Peer.Peer(None, ipp2p, pp2p)
        peer.insert(database)
        return peer
    
    @staticmethod
    def getPeer(database, sessionid):
        database.execute("""SELECT sessionid, ipp2p, pp2p
                            FROM peer
                            WHERE sessionid = %s""",
                            sessionid)
        sessionid, ipp2p, pp2p = database.fetchone()
        peer = Peer.Peer(sessionid, ipp2p, pp2p)
        return peer
    
    @staticmethod
    def getCountFile(database, sessionid):
        
        database.execute("""SELECT count(*)
                            FROM peer_has_file
                            WHERE peer_sessionid = %s""",
                            sessionid)
        
        count, = database.fetchone()
        
        return count