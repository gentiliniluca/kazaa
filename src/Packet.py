class Packet:
    
    def __init__(self, idpacket, created_at):
        self.idpacket = idpacket
        self.created_at = created_at
    
    def insert(self, database):
        
#        self.idpacket = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        
        database.execute("""INSERT INTO packet
                            (idpacket)
                            VALUES (%s)""",
                            (self.idpacket))
    
#    def update(self, database):
#        pass
    
    def delete(self, database):
        database.execute("""DELETE FROM packet
                            WHERE idpacket = %s""",
                            (self.idpacket))