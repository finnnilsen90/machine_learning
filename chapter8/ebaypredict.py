import http.client
from xml.dom.minidom import parse, parseString  , Node

devKey = 'ec15e7f6-4404-485c-b68c-74512746e37e'
appKey = 'FinnNils-testpyth-SBX-4393cab4a-39c4adfc'
certKey = 'SBX-393cab4ae771-2e27-4267-8638-f113'
userToken = 'AgAAAA**AQAAAA**aAAAAA**g09RXA**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wFk4ajAZiFowWdj6x9nY+seQ**tOQEAA**AAMAAA**XVSdeHAFtlxw88knpQsMj0WjjFVSjdKg1S7Ve5YioOCrneOZfN6SYwbAOtx8jHxL/dFf9DcYKiA0bWmf7SvfFVLlHA/HRfKFbhryQYrTQ0vO2e6FnQUp1XaTrefXd0cVKWDjK6wSrNUc+8gGjNhpH51/SDfZLEroACtFALIrt4OEuIDsJa0jBLkBRh7lL2LrQmR5RW7si3VRPvPZ9mYPbcrEX7MAgFAA1urKMZWEH2MD7/Wj9X3VE/bgklucf2gRfGiIy5AYl/0MANEueUqI+zxbkyOplibwd9xL7Je/UhMZDIAYviUO9k6COf0Yon5vpuu/uv8SZJmpjMqnf8nK4TAvKBgNPj2hnOPd5JNUxNJSTOux9U4Oi8hPGmZ0qgGQ4prC1Hpe0qyC8xV35HG9E3v8EYaAbOLQWPDRHDVi7X9XYntbaBqn2VDWFgbJFVqDPHDym2N3SvcTRK29RRc8ofW+Wi/hgYbIkk0SN674mXs3zmnlyFFVMVSZ+fino7YNb/0FQOFcYvxQd/PZiNSoewD3O2yI8K9plJ7Y6yGzIcJfO4Kr+R93kowLdU2F1XD9sBxWzv8Kn3SfzWsEcPnqSvplUA1gWUS6eknAfOLCgBOKdy2eqbvdrTqu5EFgQS3imvQU/ZPh3b7lagTIFnS/uDLMXKNOiwZAQ1jhBA5ginktI5/WPvMVa94fvLQnd68xmebursOjct4ijfkH0OWKjwkmYUtT6Y5kWWUP3kwNU6VYJJgKyL0OzaLy0l0etcTy'
serverUrl = 'api.ebay.com'

def getHeaders(apicall,siteID="0",compatabilityLevel="433"):
    headers = {"X-EBAY-API-COMPATIBILITY-LEVEL": compatabilityLevel,
                "X-EBAY-API-DEV-NAME": devKey,
                "X-EBAY-API-APP-NAME": appKey,
                "X-EBAY-API-CERT-NAME": certKey,
                "X-EBAY-API-CALL-NAME": apicall,
                "X-EBAY-API-SITEID": siteID,
                "Content-Type": "text/xml"}
    return headers

def sendRequest(apicall,xmlparameters):
    connection = http.client.HTTPSConnection(serverUrl)
    connection.request("POST", '/ws/api.dll', xmlparameters, getHeaders(apicall))
    response=connection.getresponse()
    if response.status != 200:
        print('Error sending request:' +response.reason)
    else:
        data = response.read()
        connection.close()
    return data

def getSingleValue(node,tag):
    n1=node.getElementsByTagName(tag)
    if len(n1)>0:
        tagNode=n1[0]
        if tagNode.hasChildNodes():
            return tagNode.firstChild.nodeValue
    return '-1'

def doSearch(query,categoryID=None,page=1):
    xml = "<?xml version='1.0' encoding='utf-8'?>"+\
            "<GetSearchResultsRequest xmlns=\"urn:ebay:apis:eBLBaseComponents\">"+\
            "<RequesterCredentials><eBayAuthToken>" +\
            userToken +\
            "</eBayAuthToken></RequesterCredentials>" + \
            "<Pagination>"+\
            "<EntriesPerPage>200</EntriesPerPage>"+\
            "<PageNumber>"+str(page)+"</PageNumber>"+\
            "</Pagination>"+\
            "<Query>" + query + "</Query>"
    if categoryID!=None:
        xml+="<CategoryID>"+str(categoryID)+"</CategoryID>"
    xml+="</GetSearchResultsRequest>"
    
    data=sendRequest('GetSearchResults',xml)
    response = parseString(data)
    itemNodes = response.getElementsByTagName('Item');
    results = []
    for item in itemNodes:
        itemId=getSingleValue(item,'ItemID')
        itemTitle=getSingleValue(item,'Title')
        itemPrice=getSingleValue(item,'CurrentPrice')
        itemEnds=getSingleValue(item,'EndTime')
        results.append((itemId,itemTitle,itemPrice,itemEnds))
    return results

def getCategory(query='',parentID=None,siteID='0'):
  lquery=query.lower()
  xml = "<?xml version='1.0' encoding='utf-8'?>"+\
        "<GetCategoriesRequest xmlns=\"urn:ebay:apis:eBLBaseComponents\">"+\
        "<RequesterCredentials><eBayAuthToken>" +\
        userToken +\
        "</eBayAuthToken></RequesterCredentials>"+\
        "<DetailLevel>ReturnAll</DetailLevel>"+\
        "<ViewAllNodes>true</ViewAllNodes>"+\
        "<CategorySiteID>"+siteID+"</CategorySiteID>"
  if parentID==None:
    xml+="<LevelLimit>1</LevelLimit>"
  else:
    xml+="<CategoryParent>"+str(parentID)+"</CategoryParent>"
  xml += "</GetCategoriesRequest>"
  data=sendRequest('GetCategories',xml)
  categoryList=parseString(data)
  catNodes=categoryList.getElementsByTagName('Category')
  for node in catNodes:
    catid=getSingleValue(node,'CategoryID')
    name=getSingleValue(node,'CategoryName')
    if name.lower().find(lquery)!=-1:
      print(catid,name)
