from pylab import *

def plotagematches(rows):
    xdm,ydm=[r.data[0] for r in rows if r.match==1],\
            [r.data[1] for r in rows if r.match==1]
    xdn,ydn=[r.data[0] for r in rows if r.match==0],\
            [r.data[1] for r in rows if r.match==0]

    plot(xdm,ydm,'go')
    plot(xdn,ydn,'ro')

    show()



class matchrow:
    def __init__(self,row,allnum=False):
        if allnum:
            self.data=[float(row[i]) for i in range(len(row)-1)]
        else:
            self.data=row[0:len(row)-1]
        self.match=int(row[len(row)-1])

def loadmatch(f,allnum=False):
    rows=[]
    for line in open(f):
        rows.append(matchrow(line.split(','),allnum))
    return rows

### BASIC LINEAR CLASSIFICATION ###

def lineartrain(rows):

    averages={}
    counts={}


    for row in rows:
        # Get teh class of this point
        cl=row.match
        averages.setdefault(cl,[0.0]*(len(row.data)))
        counts.setdefault(cl,0)

        # Add this point to the averages
        for i in range(len(row.data)):
            averages[cl][i]+=float(row.data[i])

        # Keep track of how many points in each class
        counts[cl]+=1

    # Divide sums by counts to get the averages
    for cl,avg in averages.items():
        for i in range(len(avg)):
            avg[i]/=counts[cl]

    return averages

def dotproduct(v1,v2):
    return sum(v1[i]*v2[i] for i in range(len(v1)))

def dpclassify(point,avgs):
    b=(dotproduct(avgs[1],avgs[1])-dotproduct(avgs[0],avgs[0]))/2
    y=dotproduct(point,avgs[0])-dotproduct(point,avgs[1])+b
    if y>0: return 0
    else: return 1

### CATEGORICAL FEATURES ###

def yesno(v):
    if v == 'yes': return 1
    if v == 'no': return -1
    else: return 0

# Lists of interest 

def matchcount(interest1,interest2):
    l1=interest1.split(':')
    l2=interest2.split(':')
    x=0
    for v in l1:
        if v in l2: x+=1
    return x

### DETERMINE DISTANCE USING YAHOO MAPS ###

### API IS DEPERCATED ###

### SCALE DATA ###

def scaledata(rows):
    low=[999999999.0]*len(rows[0].data)
    high=[-999999999.0]*len(rows[0].data)
    # Find the lowest and highest values
    for row in rows:
        d=row.data
        for i in range(len(d)):
            if d[i]<low[i]: low[i]=d[i]
            if d[i]>high[i]: high[i]=d[i]
    # Create a functin that scales data
    def scaleinput(d):
        return [(d.data[i])/(high[i]-low[i]) for row in rows]

    # Scale all the data
    newrows=[matchrow(scaleinput(row.data)+[row.match]) for row in rows]

    # Return the new data and the funtion
    return newrows,scaleinput