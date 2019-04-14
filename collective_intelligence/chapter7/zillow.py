import xml.dom.minidom
import urllib.request

zwskey="X1-ZWz185lpdjjkej_af1tq"

def getaddressdata(address,city):
    escad=address.replace(' ','+')

    # Construct the URL
    url='http://www.zillow.com/webservice/GetDeepSearchResults.htm?'
    url+='zws-id=%s&address=%s&citystatezip=%s' % (zwskey,escad,city)

    # Parse resulting XML
    doc=xml.dom.minidom.parseString(urllib.request.urlopen(url).read())
    code=doc.getElementsByTagName('code')[0].firstChild.data

    # Code 0 means success; otherwise, there was an error
    if code!='0': return None

    # Extract the info about this property
    try:
        zipcode=doc.getElementsByTagName('zipcode')[0].firstChild.data
        use=doc.getElementsByTagName('useCode')[0].firstChild.data
        year=doc.getElementsByTagName('yearBuilt')[0].firstChild.data
        bath=doc.getElementsByTagName('bathrooms')[0].firstChild.data
        bed=doc.getElementsByTagName('bedrooms')[0].firstChild.data
        rooms=doc.getElementsByTagName('totalRooms')[0].firstChild.data
        price=doc.getElementsByTagName('amount')[0].firstChild.data
    except:
        return None
    
    return (zipcode,use,int(year),float(bath),int(bed),int(rooms),price)

def getpricelist():
    l1=[]
    for line in open('addresslist.txt'):
        data=getaddressdata(line.strip(),'Cambridge,MA')
        l1.append(data)
    l2=[]
    for i in l1:
        if i!=None:
            l2.append(i)
    return l2