import time
import random
import math


def randomoptimize(domain,costf):
    best=999999999
    bestr=None
    for i in range(1000):
        # Create a random solution
        r=[random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))]
        # Get the cost
        cost=costf(r)

        # Compare it to the best one so far
        if cost<best:
            best=cost
            bestr=r
    return r

def hillclimb(domain,costf):
    # Create a random solution
    sol=[random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))]

    # Main loop
    while 1:

        # Create list of neighboring solutions
        neighbors=[]
        for j in range(len(domain)):

            # One away in each direction
            if sol[j]>domain[j][0]:
                neighbors.append(sol[0:j]+[sol[j]-1]+sol[j+1:])
            if sol[j]<domain[j][1]:
                neighbors.append(sol[0:j]+[sol[j]+1]+sol[j+1:])

        # See what the best solution amongst the neighbors is 
        current=costf(sol)
        best=current
        for j in range(len(neighbors)):
            cost=costf(neighbors[j])
            if cost<best:
                best=cost
                sol=neighbors[j]
            # If there's no improvement, then we've reached the top
            if best==current:
                break
        return sol

def annealingoptimize(domain,costf,T=10000.0,cool=0.95,step=1):
    # Initialize the values randomly
    vec=[float(random.randint(domain[i][0],domain[i][1])) for i in range(len(domain))]

    while T>0.1:
        # Choose one of the indices
        i=random.randint(0,len(domain)-1)

        # Choose a direction to change it
        dir=step*(-1)**int(round(random.random()))

        # Create a new list with one of the values changed
        vecb=vec[:]
        vecb[i]+=dir
        if vecb[i]<domain[i][0]: vecb[i]=domain[i][0]
        elif vecb[i]>domain[i][1]: vecb[i]=domain[i][1]

        # Calculate the current cost and the new cost
        ea=costf(vec)
        eb=costf(vecb)

        # Is it better, or does it make the probability
        # cutoff?
        if eb<ea:
            vec=vecb
        else:
            p=pow(math.e,(-eb-ea)//T) # // indicates floor division so float is not returned.
            if random.random()<p:
                vec=vecb

        # Decrease teh temperature
        T=T*cool
    for i in range(len(vec)):
        vec[i]=int(vec[i])

    return vec

def geneticoptimize(domain,costf,popsize=50,step=1,mutprob=0.2,elite=0.2,maxiter=100):

    # Mutation Operation
    def mutate(vec):
        i=random.randint(0,len(domain)-1)
        if random.random()<0.5 and vec[i]>domain[i][0]:
            return vec[0:i]+[vec[i]-step]+vec[i+1:] 
        elif vec[i]<domain[i][1]:
            return vec[0:i]+[vec[i]+step]+vec[i+1:]

    # Crossover Operation
    def crossover(r1,r2):
        i=random.randint(1,len(domain)-2)
        return r1[0:i]+r2[i:]

    # Build the initial population
    pop=[]
    for i in range(popsize):
        vec=[random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))]
        pop.append(vec)
    # How many winners from each generation?
    topelite=int(elite*popsize)

    # Main loop 
    for i in range(maxiter):
        scores=[(costf(v),v) for v in pop]
        scores.sort()
        ranked=[v for (s,v) in scores]

        # Start with the pure winners
        pop=ranked[0:topelite]
    
        # Add mutated and bred forms of the winners
        while len(pop)<popsize:
            if random.random()<mutprob:

                # Mutation
                c=random.randint(0,topelite)
                pop.append(mutate(ranked[c]))
            else:

                # Crossover
                c1=random.randint(0,topelite)
                c2=random.randint(0,topelite)
                pop.append(crossover(ranked[c1],ranked[c2]))

        # print current best score
        print(scores[0][0])

    return scores[0][1]

def twogeneticoptimize(domain,costf,popsize=50,step=1,mutprob=0.2,elite=0.2,maxiter=100):
    # Mutation Operation
    def mutate(vec):
        i=random.randint(0,len(domain)-1)
        if random.random()<0.5 and vec[i]>domain[i][0]:
            return vec[0:i]+[vec[i]-step]+vec[i+1:] 
        elif vec[i]<domain[i][1]:
            return vec[0:i]+[vec[i]+step]+vec[i+1:]
  
    # Crossover Operation
    def crossover(r1,r2):
        i=random.randint(1,len(domain)-2)
        return r1[0:i]+r2[i:]

    # Build the initial population
    pop=[]
    for i in range(popsize):
        vec=[random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))]
        pop.append(vec)

    # How many winners from each generation?
    topelite=int(elite*popsize)

    # Main loop 
    for i in range(maxiter):
        scores=[(costf(v),v) for v in pop]
        scores.sort()
        ranked=[v for (s,v) in scores]

        # Start with the pure winners
        pop=ranked[0:topelite]

        # Add mutated and bred forms of the winners
        while len(pop)<popsize:
            if random.random()<mutprob:

                # Mutation
                c=random.randint(0,topelite)
                res=mutate(ranked[c])
                if res!=None:
                    pop.append(res)

            else:
            
                # Crossover
                c1=random.randint(0,topelite)
                c2=random.randint(0,topelite)
                res=crossover(ranked[c1],ranked[c2])
                if res!=None:
                    pop.append(res)

        # Print current best score
        print(scores[0][0])

    return scores[0][1]