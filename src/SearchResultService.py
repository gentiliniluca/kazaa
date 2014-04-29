import SearchResult
import File
import Peer
import sys
import os

class SearchResultService:
    
    @staticmethod
    def insertNewSearchResult(database, ipp2p, pp2p, filemd5, filename, packetid):
        
        try:
            sr = SearchResultService.getSearchResult(database, ipp2p, pp2p, filemd5, filename, packetid)
        
        except:
            sr = SearchResult.SearchResult(None, ipp2p, pp2p, filemd5, filename, packetid)
            sr.insert(database)
        
        return sr
    
    @staticmethod
    def getSearchResult(database, ipp2p, pp2p, filemd5, filename, packetid):
        
        database.execute("""SELECT ipp2p, pp2p, filemd5, filename
                            FROM searchresult
                            WHERE ipp2p = %s AND pp2p = %s AND filemd5 = %s AND filename = %s AND packetid = %s""",
                            (ipp2p, pp2p, filemd5, filename, packetid))
        
        ipp2p, pp2p, filemd5, filename, packetid = database.fetchone()
        
        searchResult = SearchResult.SearchResult(None, ipp2p, pp2p, filemd5, filename, packetid)
        
        return searchResult
    
    @staticmethod
    def getSearchResults(database, packetid, searchString):
        searchResults = []
        
        #costruzione della lista di risultati della ricerca
        
        #file con md5 non presente nel mio cluster
        database.execute("""SELECT ipp2p, pp2p, filemd5, filename
                            FROM searchresult
                            WHERE packetid = %s AND filemd5 NOT IN (SELECT filemd5
                                                                    FROM file)
                            ORDER BY filemd5""",
                            (packetid))
        
        try:
            i = -1
            previous_fileMD5 = ""
            
            while True:
                ipp2p, pp2p, filemd5, filename = database.fetchone()
                
                if filemd5 != previous_fileMD5:
                    searchResults.append(File.File(filemd5, filename))
                    previous_fileMD5 = filemd5
                    i = i + 1
                
                searchResults[i].peers.append(Peer.Peer("0000000000000000", ipp2p, pp2p))
        except:
            pass
        
        #file presenti sul mio e anche su altri cluster
        myFilesIndex = i + 1
        
        searchString = "%" + searchString.upper() + "%"
        database.execute("""SELECT filename, filemd5, ipp2p, pp2p
                            FROM file, peer, peer_has_file
                            WHERE file_filemd5 = filemd5 AND
                                  peer_sessionid = sessionid AND
                                  filename LIKE %s
                            ORDER BY filemd5""",
                            searchString)      
        
        try:            
            previous_fileMD5 = ""
            
            while True:                            
                filename, filemd5, ipp2p, pp2p = database.fetchone()             
                
                if filemd5 != previous_fileMD5:                                                            
                    searchResults.append(File.File(filemd5, filename))                                    
                    previous_fileMD5 = filemd5
                    i = i + 1                        
                
                searchResults[i].peers.append(Peer.Peer("0000000000000000", ipp2p, pp2p))                
        except:            
            pass
        
        j = myFilesIndex
        while j < len(searchResults):             
            database.execute("""SELECT ipp2p, pp2p
                                FROM searchresult
                                WHERE packetid = %s AND filemd5 = %s""", (packetid, searchResults[j].filemd5))
            
            try:                       
                while True:
                    myIpp2p, myPp2p = database.fetchone()                                                        
                    searchResults[j].peers.append(Peer.Peer("0000000000000000", myIpp2p, myPp2p))                          
            except:
                pass
            
            j = j + 1
        
        return searchResults
    
    @staticmethod
    def getSearchResultsDownload(database):
        #print("eseguo query")
        
        database.execute("""SELECT ipp2p, pp2p, filemd5, filename
                            FROM searchresult""")
       
        searchResults = []
        try:
            #print("Entro try")
            
            while True:
                #print("entro cilco")
                ipp2p, pp2p, filemd5, filename = database.fetchone()
                #print("ipp2p: "+ipp2p+" pp2p: "+pp2p+" filemd5: "+filemd5+" filename: "+filename)
                searchResult = SearchResult.SearchResult(None,ipp2p, pp2p, filemd5, filename,None)
                searchResults.append(searchResult)
               
        except:
            #print (sys.exc_info())
            pass
        
        #print("dentro la funzione "+str(len(searchResults)))
        
        return searchResults
    
    
    
    
    @staticmethod
    def delete(database):
        database.execute("""DELETE FROM searchresult""")