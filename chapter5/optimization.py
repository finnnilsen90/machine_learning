import time
import random
import math

### List of possible solutions to the problem ###
# its the input to the functions.
# each number represents each flight during the day 
# 0 is the first flight 4 is the 5th flight.
# There are 6 people each need an outbound and return flight so there are 12 inputs.
### s = [1, 4, 3, 2, 7, 3, 6, 3, 2, 4, 5, 3] ###

people = [('Seymour','BOS'),
        ('Franny','DAL'),
        ('Zooey','CAK'),
        ('Walt','MIA'),
        ('Buddy','ORD'),
        ('Les','OMA')]

# LaGuardia airport in New York
destination='LGA'

flights={}
# Extract data from text file and put into dictionary
for line in open('schedule.txt'):
    origin,dest,depart,arrive,price=line.strip().split(',')
    flights.setdefault((origin,dest),[])

    # Add details to the list of possible flights
    flights[(origin,dest)].append((depart,arrive,int(price)))

def getminutes(t):
    x=time.strptime(t, '%H:%M')
    return x[3]*60+x[4]

def printschedule(r):

    for d in range(int(len(r)/2)):
        name=people[d][0]
        origin=people[d][1]
        out = flights[(origin,destination)][r[2*d]]
        ret = flights[(origin,destination)][r[2*d+1]]
        print('%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % (name,origin,out[0],out[1],out[2],ret[0],ret[1],ret[2]))

def schedulecost(sol):
    totalprice=0
    latestarrival=0
    earliestdep=24*60

    for d in range(int(len(sol)/2)):
        # get the inbound and outbound flights
        origin=people[d][1]
        outbound = flights[(origin,destination)][int(sol[2*d])]
        print(outbound)
        returnf = flights[(origin,destination)][int(sol[2*d+1])]

        # Total price is the price of all outbound and return flights
        totalprice+=outbound[2]
        totalprice+=returnf[2]

        # Track the latest arrival and earliest departure 
        if latestarrival<getminutes(outbound[1]): latestarrival=getminutes(outbound[1])
        if earliestdep>getminutes(returnf[0]): earliestdep=getminutes(returnf[0])

    # Every person must wait at the airport until the altest person arrives.
    # They also must arrive at the same time and wait for their flights.
    totalwait=0
    for d in range(int(len(sol)/2)):
        origin=people[d][1]
        outbound = flights[(origin,destination)][int(sol[2*d])]
        returnf = flights[(origin,destination)][int(sol[2*d+1])]
        totalwait+=latestarrival-getminutes(outbound[1])
        totalwait+=getminutes(returnf[0])-earliestdep

    # Does this solution require an extra day of car rental? That'll be $50!
    if latestarrival<earliestdep: totalprice+=50

    return totalprice+totalwait