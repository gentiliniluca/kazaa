class SuperNear:
    
    def __init__(self, idsupernear, ipp2p, pp2p):
        self.idsupernear = idsupernear
        self.ipp2p = ipp2p
        self.pp2p = pp2p
    
    def insert(self, database):
        database.execute("""INSERT INTO supernear
                            (ipp2p, pp2p)
                            VALUES (%s, %s)""",
                            (self.ipp2p, self.pp2p))
    
    def delete(self, database):
        database.execute("""DELETE FROM supernear
                            WHERE idsupernear = %s""",
                            (self.idsupernear))