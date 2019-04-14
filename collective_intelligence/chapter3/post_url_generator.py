import feedparser
import re
    
def generate_blog_post(url):
    out=open('postfeedlist.txt','w')

    d=feedparser.parse(url)

    for e in d.entries:
        out.write(str(e['wfw_commentrss']))
        out.write('\n')




