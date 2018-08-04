from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sqlite3 as sql
from sqlite3 import Error
import re

import nn
mynet=nn.searchnet('nn.db') # Connect to neural network database

# Create a list of words to ifnore
ignorewords=set(['the','of','to','and','a','in','is','it'])

# DB connection function

def connect(db_file):

    try:
        conn=sql.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None



class crawler:
    # Initialize the crawler with the name of database
    def __init__(self,dbname):
        self.con=sql.connect(dbname)

    def __del_(self):
        self.con.close()
    
    def dbcommit(self):
        self.con.commit()

    # Auxilliary function for getting an entry id and adding
    # if it's not present
    def getentryid(self,table,field,value,createnew=True):
        cur=self.con.execute("select rowid from %s where %s='%s'" % (table,field,value))
        res=cur.fetchone()
        if res==None:
            cur=self.con.execute("insert into %s (%s) values ('%s')" % (table,field,value))
            return cur.lastrowid
        else:
            return res[0]

    # Index an individual page
    def addtoindex(self,url,soup):
        if self.isindexed(url): return # Checks if it has been crawled. 
        print('Indexing '+url)

        # Get the individual words
        text=self.gettextonly(soup)
        words=self.separatewords(text)

        # Get the URL id
        urlid=self.getentryid('urllist','url',url)

        # Link each word to this url
        for i in range(len(words)):
            word=words[i]
            if word in ignorewords: continue
            wordid=self.getentryid('wordlist','word',word)
            self.con.execute("insert into wordlocation(urlid,wordid,location) values (%d,%d,%d)" % (urlid,wordid,i))

    # Extract the text from an HTML page (no tags)
    def gettextonly(self,soup):
        v=soup.string 
        if v==None:
            c=soup.contents
            resulttext=''
            for t in c:
                subtext=self.gettextonly(t)
                resulttext+=subtext+'\n'
            return resulttext
        else:
            return v.strip()

    # Separate the words by any whitespace character
    def separatewords(self,text):
        splitter=re.compile('\\W*')
        return [s.lower() for s in splitter.split(text) if s!='']

    # Return true if this url is already indexed
    def isindexed(self,url):
        u=self.con.execute \
        ("select rowid from urllist where url='%s'" % url).fetchone()
        if u!=None:
            # Check if it has actually been crawled
            v=self.con.execute('select * from wordlocation where urlid=%d' % u[0]).fetchone()
            if v!=None: return True 
        return False 

    # Add a link between two pages
    def addlinkref(self,urlFrom,urlTo,linkText):
        words=self.separatewords(linkText)
        fromid=self.getentryid('urllist','url',urlFrom)
        toid=self.getentryid('urllist','url',urlTo)
        if fromid==toid: return 
        cur=self.con.execute("insert into link(fromid,toid) values (%d,%d)" % 
        (fromid,toid))
        linkid=cur.lastrowid
        for word in words:
            if word in ignorewords: continue
            wordid=self.getentryid('wordlist','word',word)
            self.con.execute('insert into linkwords(linkid,wordid) values (%d,%d)' % (linkid,wordid))
    
    # Starting with a list of pages, do a breadth
    # first search to the given depth, indexing pages 
    # as we go
    def crawl(self,pages,depth=2):
        # First loop goes through links on a page with a depth of 2.
        # The depth parameters stops the crawler from overflowing the stack. 
        for i in range(depth):
            newpages=set() # sort new pages

            # Loops through pages and adds their contents to index
            for page in pages:
                try:
                    c=urlopen(page)
                except:
                    print('Could not open %s' % page)
                    continue
                soup=BeautifulSoup(c.read(), 'html.parser')
                self.addtoindex(page,soup)

                # Loops through links on a page. 
                links=soup('a')
                for link in links:
                    if('href' in dict(link.attrs)):
                        url=urljoin(page,link['href'])
                        if url.find("'")!=-1: continue
                        url=url.split('#')[0] # remove location portion
                        if url[0:4]=='http' and not self.isindexed(url):
                            newpages.add(url)
                        linkText=self.gettextonly(link)
                        self.addlinkref(page,url,linkText)

                    self.dbcommit()

                pages=newpages

    def calculatepagerank(self,iterations=20):
        # clear out the  current PageRank tables
        self.con.execute('drop table if exists pagerank')
        self.con.execute('create table pagerank(urlid primary key,score)')

        # initialize every url with a PageRank of 1
        self.con.execute('insert into pagerank select rowid, 1.0 from urllist')
        self.dbcommit()

        for i in range(iterations):
            print("Iteration %d" % (i))
            for (urlid,) in self.con.execute('select rowid from urllist'):
                pr=0.15

                # Loop through all the pages that link to this one
                for (linker,) in self.con.execute('select distinct fromid from link where toid=%d' % urlid):
                    # Get the PageRank of the linker
                    linkingpr=self.con.execute('select score from pagerank where urlid=%d' % linker).fetchone()[0]

                    # Get the total number of links from the linker
                    linkingcount=self.con.execute('select count(*) from link where fromid=%d' % linker).fetchone()[0]
                    pr+=0.85*(linkingpr/linkingcount)
                    self.con.execute('update pagerank set score=%f where urlid=%d' % (pr,urlid))
                    self.dbcommit()

    # Create the database tables

    # Create Table
    # crate table TABLE_Name

    # Create Index
    # create index INDEX_NAME on TABLE_NAME
    def createindextables(self):
        self.con.execute('create table urllist(url)')
        self.con.execute('create table wordlist(word)')
        self.con.execute('create table wordlocation(urlid,wordid,location)')
        self.con.execute('create table link(fromid integer,toid integer)')
        self.con.execute('create table linkwords(wordid,linkid)')
        self.con.execute('create index wordidx on wordlist(word)')
        self.con.execute('create index urlidx on urllist(url)')
        self.con.execute('create index wordurlidx on wordlocation(wordid)')
        self.con.execute('create index urltoidx on link(toid)')
        self.con.execute('create index urlfromidx on link(fromid)')
        self.dbcommit()

class searcher:
    # Connect to database to create the instance. 
    def __init__(self,dbname):
        self.con=sql.connect(dbname)

    def __del__(self):
        self.con.close()

    # Allows the ability to query multiple words.
    def getmatchrows(self,q):
        # Strings to build the query
        fieldlist='w0.urlid'
        tablelist=''  
        clauselist=''
        wordids=[]

        # Split the words by spaces from the query
        words=q.split(' ')  
        tablenumber=0

        for word in words:
        # Get the word ID
            wordrow=self.con.execute(
            "select rowid from wordlist where word='%s'" % word).fetchone()
            if wordrow!=None:
                wordid=wordrow[0]
                wordids.append(wordid)
                if tablenumber>0:
                    tablelist+=','
                    clauselist+=' and '
                    clauselist+='w%d.urlid=w%d.urlid and ' % (tablenumber-1,tablenumber)
                fieldlist+=',w%d.location' % tablenumber
                tablelist+='wordlocation w%d' % tablenumber      
                clauselist+='w%d.wordid=%d' % (tablenumber,wordid)
                tablenumber+=1

        # Create the query from the separate parts
        fullquery='select %s from %s where %s' % (fieldlist,tablelist,clauselist)
        # print(fullquery)
        cur=self.con.execute(fullquery)
        rows=[row for row in cur]

        return rows,wordids

    # Creates a scored list of links based off of a variety of scoring functions. 
    def getscoredlist(self,rows,wordids):
        totalscores=dict([(row[0],0) for row in rows]) # Puts urls in a dictionary.

        # # # # # SCORING FUNCTIONS # # # # #
        weights=[(1.0,self.locationscore(rows)),(1.0,self.frequencyscore(rows)),(1.0,self.pagerankscore(rows))]

        # Loop through each scoring function and applies a score for each url, based off of the query. 
        for (weight,scores) in weights:
            for url in totalscores:
                totalscores[url]+=weight*scores[url]

        return totalscores

    # Gets the url name based off of the id. 
    def geturlname(self,id):
        return self.con.execute(
            "select url from urllist where rowid=%d" % id).fetchone()[0]
        
    def query(self,q):
        rows,wordids=self.getmatchrows(q)
        scores=self.getscoredlist(rows,wordids)
        rankedscores=sorted([(score,url) for (url,score) in scores.items()],reverse=1)
        for (score,urlid) in rankedscores[0:10]:
            # print('score => '+str(score))
            print('%f\t%s' % (score,self.geturlname(urlid)))
        return wordids,[r[1] for r in rankedscores[0:10]]

    # Normalizes the score to make each score from each funtion consistent.
    def normalizescores(self,scores,smallIsBetter=0):
        vsmall=0.0001 # Avoid division by zero errors
        if smallIsBetter:
            minscore=min(scores.values())
            return dict([(u,float(minscore)/max(vsmall,l)) for (u,l) in scores.items()])
        else:
            maxscore=max(scores.values())
            if maxscore==0: maxscore=vsmall
            return dict([(u,float(c)/maxscore) for (u,c) in scores.items()])

    # Makes a score based off how times a word appears on a page. 
    def frequencyscore(self,rows):
        counts=dict([(row[0],0) for row in rows])
        for row in rows: counts[row[0]]+=1
        return self.normalizescores(counts)

    def wordfrequency(self,q):
        wrows,wordids=self.getmatchrows(q)
        # Counts number of words in a row.
       
        wordrow=self.con.execute("select * from wordlist").fetchall()
        
        # Get numerator
        word_count=self.frequencyscore(wrows)
        num=len(word_count.keys())
    
        # Get denominator = total words in the query
        den=len(wordrow)
        result=float(num/den)
        return result*100

    # Scores based off of how high a search term appears in a page. 
    def locationscore(self,rows):
        locations=dict([(row[0],1000000) for row in rows])
        for row in rows:
            loc=sum(row[1:])
            if loc<locations[row[0]]: locations[row[0]]=loc

        return self.normalizescores(locations,smallIsBetter=1)

    # Determines how close search terms are to one another. 
    def distancescore(self,rows):
        # If there's only one word, everyone wins!
        if len(rows[0])<=2: return dict([(row[0],1.0) for row in rows])

        # Initialize the dictionary with large values
        mindistance=dict([(row[0],1000000) for row in rows])

        for row in rows:
            dist=sum([abs(row[i]-row[i-1]) for i in range(2,len(row))])
            if dist<mindistance[row[0]]: mindistance[row[0]]=dist
        return self.normalizescores(mindistance,smallIsBetter=1)

    # Counts how many inbound links there are. 
    def inboundlinkscore(self,rows):
        uniqueurls=set([row[0] for row in rows])
        inboundcount=dict([(u,self.con.execute('select count(*) from link where toid=%d' % u).fetchone()[0]) for u in uniqueurls])
        return self.normalizescores(inboundcount)

    # Retrieves page ranks from the database
    def pagerankscore(self,rows):

        pageranks=dict([(row[0],self.con.execute('select score from pagerank where urlid=%d' % row[0]).fetchone()[0]) for row in rows])

        maxrank=max(pageranks.values())
        normalizedscores=dict([(u,float(1)/maxrank) for (u,l) in pageranks.items()])
        return normalizedscores 

    # Determines how relevant the text is in the url to the query. 
    def linktextscore(self,rows,wordids):
        vsmall=0.0001 # Avoid division by zero errors
        linkscores=dict([(row[0],0) for row in rows])
        for wordid in wordids:
            cur=self.con.execute('select link.fromid,link.toid from linkwords,link where wordid=%d and linkwords.linkid=link.rowid' % wordid)
            for (fromid,toid) in cur:
                if toid in linkscores:
                    pr=self.con.execute('select score from pagerank where urlid=%d' % fromid).fetchone()[0]
                    linkscores[toid]+=pr
        maxscore=max(linkscores.values())
        print('score => '+str(maxscore))
        if maxscore==0: maxscore=vsmall
        normalizedscores=dict([(u,float(1)/maxscore) for (u,l) in linkscores.items()])
        return normalizedscores 

    # Scores from your neural network
    # ***Note: do not include in the weighted function until the networks has been trained***
    def nnscore(self,rows,wordids):
        #Get unique URL IDs as an ordered list
        urlids=[urlid for urlid in set([row[0] for row in rows])]
        nnres=mynet.getresult(wordids,urlids)
        scores=dict([(urlids[i],nnres[i]) for i in range(len(urlids))])
        return self.normalizedscores(scores)