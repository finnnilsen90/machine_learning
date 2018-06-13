import feedparser
import re

# Returns title and dictionary of word counts for an RSS feed
def getwordcounts(url):
    # Parse the feed
    d=feedparser.parse(url)
    wc={}

    # Loop over all the entries
    for e in d.entries:
        if 'summary' in e: summary=e.summary
        else: summary=e.description

        # Extract a list of words
        words=getwords(e.title+' '+summary)
        for word in words:
            wc.setdefault(word,0)
            wc[word]+=1
    return getattr(d.feed, 'title', 'Unknown title'), wc
    # return d.feed.title,wc

def getwords(html):
    # Remove all the HTML tags
    txt=re.compile(r'<[^>]+>').sub('',html)

    # Split words by all non-alpha characters
    words=re.compile(r'[^A-Z^a-z]+').split(txt)

    # Convert to lowercase
    return [word.lower() for word in words if word!='']

apcount={}
wordcounts={}
feedlist=[]
for feedurl in open('feedlist.txt'):
    feedlist.append(feedurl)
    title,wc=getwordcounts(feedurl)
    wordcounts[title]=wc
    for word,count in wc.items():
        apcount.setdefault(word,0)
        if count>1:
            apcount[word]+=1

wordlist=[]
for w,bc in apcount.items():
    frac=float(bc)/len(feedlist)
    if frac>0.1 and frac<0.5: wordlist.append(w)

out=open('blogdata.txt','w')
out.write('Blog')
for word in wordlist: out.write('\t%s' % word)
out.write('\n')
for blog,wc in wordcounts.items():
    #deal with unicode outside the ascii range
    blog = blog.encode('ascii','ignore')

    out.write(str(blog))
    for word in wordlist:
        if word in wc: out.write('\t%d' % wc[word])
    out.write('\n')


# def readfile(filname):
#     lines=[line for line in file(filname)]

#     # First line is the column titles
#     colnames=lines[0].strip().split('\t')[1:]
#     rownames=[]
#     data=[]
#     for line in lines[1:]:
#         p=line.strip().split('\t')
#         # First column in each row is the rowname
#         rownames.append(p[0])
#         # The data for this row is the remainder of the row
#         data.append([float(x) for x in p[1:]])
#     return rownames,colnames,data

# from math import sqrt
# def person(v1,v2):
#     # Simple sums
#     sum1=sum(v1)
#     sum2=sum(v2)

#     # Sum of the squares
#     sum1Sq=sum([pow(v,2) for v in v1])
#     sum2Sq=sum([pow(v,2) for v in v2])

#     # Sum of the products
#     pSum=sum([v1[i]*v2[i] for i in range(len(v1))])

#     # Calculate r (Pearson score)
#     num=pSum-(sum1*sum2/len(v1))
#     den=sqrt((sumSq-pow(sum1,2)/len(v1))*(sum2Sq-pow(sum2,2)/len(v1)))
#     if den==0: return 0

#     return 1.0-num/den
