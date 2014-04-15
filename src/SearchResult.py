class SearchResult:
    
    def __init__(self, idsearchresult, ipp2p, pp2p, filemd5):
        self.idsearchresult = idsearchresult
        self.ipp2p = ipp2p
        self.pp2p = pp2p 
        self.filemd5 = filemd5            
        
    def insert(self, database):
        database.execute("""INSERT INTO searchresult
                            (ipp2p, pp2p, filemd5)
                            VALUES (%s, %s, %s)""",
                            (self.ipp2p, self.pp2p, self.filemd5))