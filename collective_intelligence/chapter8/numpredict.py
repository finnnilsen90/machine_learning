from random import random,randint
from pylab import *
import math

#### GENERATE DATA SET ####

def wineprice(rating,age):
    peak_age=rating-50

    # Calculate price based on rating
    price=rating/2
    if age>peak_age:
        # Past its peak, goes bad in 5 years
        price=price*(5-(age-peak_age))
    else:
        # Increases to 5x original value as it
        # approaches its peak
        price=price*(5*((age+1)/peak_age))
    if price<0: price=0
    return price

def wineset1():
    rows=[]
    for i in range(300):
        # Create a random age and rating
        rating=random()*50+50
        age=random()*50

        # Get reference price
        price=wineprice(rating,age)

        # Add some noise
        price*=(random()*0.4+0.8)

        # Add to the dataset
        rows.append({'input':(rating,age),
                     'result':price})

    return rows

def wineset2():
    rows=[]
    for i in range(300):
        # Create a random age and rating
        rating=random()*50+50
        age=random()*50
        aisle=float(randint(1,20))
        bottlesize=[375.0,750.0,1500.0,3000.0][randint(0,3)]

        # Get reference price
        price=wineprice(rating,age)
        price*=(bottlesize/750)

        # Add some noise
        price*=(random()*0.9+0.)

        # Add to the dataset
        rows.append({'input':(rating,age,aisle,bottlesize),
                     'result':price})

    return rows

def wineset3():
    rows=wineset1()
    for row in rows:
        if random()<0.5:
            # Wine was bout at a discount store
            row['result']*=0.6
    return rows

#### K-NEAREST NEIGHBOR ####

def euclidean(v1,v2):
    d=0.0
    for i in range(len(v1)):
        d+=(v1[i]-v2[i])**2
    return math.sqrt(d)

def getdistances(data,vec1):
    distancelist=[]
    for i in range(len(data)):
        vec2=data[i]['input']
        distancelist.append((euclidean(vec1,vec2),i))
    distancelist.sort()
    return distancelist

def knnestimate(data,vec1,k=5):
    #Get sorted distances
    dlist=getdistances(data,vec1)
    avg=0.0

    # Take the average of the top k results
    for i in range(k):
        idx=dlist[i][1]
        avg+=data[idx]['result']
    avg=avg/k 
    return avg 

#### WEIGHTED NEIGHBORS ####

## INVERSE FUNCTION ##

def inverseweight(dist,num=1.0,const=0.1):
    return num/(dist+const)

## SUBTRACTION FUNCTION ##

def subtractweight(dist,const=1.0):
    if dist>const:
        return 0
    else:
        return const-dist

## GUASSIAN FUNCTION ##

def gaussian(dist,sigma=10.0):
    return math.e**(-dist**2/(2*sigma**2))

#### WEIGHTEDD KNN ####

def weightedknn(data,vec1,k=5,weightf=gaussian):
    # Get distances
    dlist=getdistances(data,vec1)
    avg=0.0
    totalweight=0.0

    # Get weighted average 
    for i in range(k):
        dist=dlist[i][0]
        idx=dlist[i][1]
        weight=weightf(dist)
        avg+=weight*data[idx]['result']
        totalweight+=weight
    avg=avg/totalweight
    return avg

#### CROSS-VALIDATION ####

def dividedata(data,test=0.05):
    trainset=[]
    testset=[]
    for row in data:
        if random()<test:
            testset.append(row)
        else:
            trainset.append(row)
    return trainset,testset

def testalgorithim(algf,trainset,testset):
    error=0.0
    for row in testset:
        guess=algf(trainset,row['input'])
        error+=(row['result']-guess)**2
    return error/len(testset)

def crossvalidate(algf,data,trials=100,test=0.05):
    error=0.0
    for i in range(trials):
        trainset,testset=dividedata(data,test)
        error+=testalgorithim(algf,trainset,testset)
    return error/trials


#### SCALING DIMENSIONS ####

def rescale(data,scale):
    scaledata=[]
    for row in data:
        scaled=[scale[i]*row['input'][i] for i in range(len(scale))]
        scaledata.append({'input':scaled,'result':row['result']})
    return scaledata

#### OPTIMIZE SCALE ####

def createcostfunction(algf,data):
    def costf(scale):
        sdata=rescale(data,scale)
        return crossvalidate(algf,sdata,trials=10)
    return costf

weightdomain=[(0,20)]*4

#### ESTIMATE PROBABILITY DENSITY ####

def probguess(data,vec1,low,high,k=5,weightf=gaussian):
    dlist=getdistances(data,vec1)
    nweight=0.0
    tweight=0.0

    for i in range(k):
        dist=dlist[i][0]
        idx=dlist[i][1]
        weight=weightf(dist)
        v=data[idx]['result']

        # Is this point in the range?
        if v>=low and v<=high:
            nweight+=weight
        tweight+=weight
    if tweight==0: return 0

    # The probability is the weights in the range
    # divided by all the weights
    return nweight/tweight

def cumulativegraph(data,vec1,high,k=5,weightf=gaussian):
    t1=arange(0.0,high,0.1)
    cprob=array([probguess(data,vec1,0,v,k,weightf) for v in t1])
    plot(t1,cprob)
    show()

def probabilitygraph(data,vec1,high,k=5,weightf=gaussian,ss=5.0):
    # Make a range for the prices
    t1=arange(0.0,high,0.1)

    # Get the probabilities for the entire range
    probs=[probguess(data,vec1,v,v+0.1,k,weightf) for v in t1]

    # Smooth them by adding the gaussian of the nerby probabilities
    smoothed=[]
    for i in range(len(probs)):
        sv=0.0
        for j in range(0,len(probs)):
            dist=abs(i-j)*0.1
            weight=gaussian(dist,sigma=ss)
            sv+=weight*probs[j]
        smoothed.append(sv)
    smoothed=array(smoothed)

    plot(t1,smoothed)
    show()