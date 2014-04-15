import Packet

class PacketService:
    global EXPIREDTIME 
    EXPIREDTIME = 20
    
    @staticmethod
    def insertNewPacket(database, idpacket):
        packet = Packet.Packet(idpacket, None)
        packet.insert(database)
        return packet
    
    @staticmethod
    def getPacket(database, idpacket):
        database.execute("""SELECT idpacket, created_at
                            FROM packet
                            WHERE idpacket = %s""",
                            idpacket)
        idpacket, created_at = database.fetchone()
        packet = Packet.Packet(idpacket, created_at)
        return packet
    
    @staticmethod
    def deleteExpiredPacket(database):
        database.execute("""DELETE FROM packet
                            WHERE UNIX_TIMESTAMP() - UNIX_TIMESTAMP(created_at) > %s""",
                            (EXPIREDTIME))