import SearchResult
import sys

class SearchResultService:
    
    @staticmethod
    def insertNewSearchResult(database, ipp2p, pp2p, filemd5):
        
        try:
            sr = SearchResultService.getSearchResult(database, ipp2p, pp2p, filemd5)
        
        except:
            sr = SearchResult.SearchResult(ipp2p, pp2p, filemd5)
            sr.insert(database)
        
        return sr
    
    @staticmethod
    def getSearchResult(database, ipp2p, pp2p, filemd5):
        
        database.execute("""SELECT ipp2p, pp2p, filemd5
                            FROM searchresult
                            WHERE ipp2p = %s AND pp2p = %s AND filemd5 = %s""",
                            (ipp2p, pp2p, filemd5))
        
        ipp2p, pp2p, filemd5 = database.fetchone()
        
        searchResult = SearchResult.SearchResult(ipp2p, pp2p, filemd5)
        
        return searchResult
    
    @staticmethod
    def getSearchResults(database):
        database.execute("""SELECT ipp2p, pp2p, filemd5
                            FROM searchresult""")
       
        searchResults = []
        try:
            while True:
                ipp2p, pp2p, filemd5 = database.fetchone()
                searchResult = SearchResult.SearchResult(ipp2p, pp2p, filemd5)
                searchResults.append(searchResult)
               
        except:
            pass
        
        return searchResults
    
    @staticmethod
    def delete(database):
        database.execute("""DELETE FROM searchresult""")