import random
from collections import deque
from city import City
from graph import Graph
import time
import heapq
import math
import concurrent.futures

WEAPON_STRENGTH = 3 #Number of aliens that can be killed by 1 weapon 
cityNames = ["Cairo",  "Luxor", "Aswan", "Port Said", "Suez", "Ismailia", "Faiyum", "Mansoura", "Tanta", "Hurghada", "Petra", "Dahab", "Amman", "Beirut", "Jerusalem",  "Damascus", "Baghdad", "Riyadh", "Ankara", "Aleppo", "Dubai", "Abu Dhabi", "Doha", "Muscat", "Kuwait City", "Manama", "Salalah", "Istanbul", "Tehran", "Alexandria"]    
totalAliensInWorld=0

def createGraph(cityNames):
    graph = Graph()
    # add cities with random properti
    for name in cityNames:
        civilianPop = random.randint(1000, 5000)
        weaponStockpile = random.randint(10, 100)
        isMilitaryBase = bool(random.getrandbits(1))

        city = City(name, 0, civilianPop, isMilitaryBase, weaponStockpile)
        graph.addCity(city)
        
    # assign random neighbors to each city
    for city in graph.cities.values():
        while True: #ensure atleast one neighbour is added
            neighbor = random.choice(list(graph.cities.values()))
            if neighbor != city and neighbor not in city.neighbors:
                distance = random.randint(10, 100)
                graph.addEdge(city.name, neighbor.name, distance)  #bidirectional edge
                break
        
        #assign some additional neighbors
        for _ in range(random.randint(0, 4)):  # Assign 0-2 additional neighbors to each city
            neighbor = random.choice(list(graph.cities.values()))
            if neighbor == city or neighbor in city.neighbors:  # Avoid self-loops and duplicate edges
                continue
            distance = random.randint(10, 100)
            graph.addEdge(city.name, neighbor.name, distance)  #bidirectional edge
    return graph

graph = createGraph(cityNames)

#printGraph(graph)
def printGraph(graph):
    print(f"Total number of cities: {len(graph.cities)}")
    for city in graph.cities.values():
        print(f"{city.name} is connected to:")
        for neighbor, distance in city.neighbors.items():
            print(f"  {neighbor.name} with distance {distance}")
            

# Goal Test to see if current node is Alexandria i.e. Goal Node
def goalTest(node):
    if node.name == "Alexandria":
        return True
    return False

def saveCitiesGoalTest():
    if totalAliensInWorld == 0:
        return True
    return False

#BFS On graph to allocate alien quota etc. 
def bfs(graph, total_aliens, source_city):
    # Random source city
    source_city.alienArrival(total_aliens) # Update alien population
    print(f"{total_aliens} aliens have landed in {source_city.name}")

    if goalTest(source_city) == True:
        print("ALIENS HAVE REACHED ALEXANDRIA!!")
        return

    frontier=deque()
    explored=set()
    frontier.append(source_city)

    while (len(frontier)!=0): 
        explore=frontier.popleft()
        explored.add(explore)
        # no. of aliens to leave behind (2% - 5% of the current population)
        alienQuota=0
        while(alienQuota == 0): 
            lower_bound = int(explore.alienPop * 0.02)
            upper_bound = int(explore.alienPop * 0.05)
            if lower_bound > upper_bound:
                lower_bound, upper_bound = upper_bound, lower_bound #swap incase of invalid value
            
            if lower_bound == 0 and upper_bound == 0:
                continue

            alienQuota = random.randint(lower_bound, upper_bound) #randomly selecting alien quota
        
        #explore.alienPop -= alienQuota
        totalDispersable = explore.alienPop - alienQuota

        # eligible to invade 
        neighborsToInvade = [neighbor for neighbor in explore.neighbors if neighbor not in frontier and neighbor not in explored] #neighbor.alienPop doesnt have to be zero - does it. Invade all possible cities

        #aliens get divided in neighboring cities
        aliensToDisperse = totalDispersable // len(neighborsToInvade) if neighborsToInvade else 0


        for neighbor in neighborsToInvade:
            #  move to the neighboring city
            if aliensToDisperse > 0:
                neighbor.alienArrival(aliensToDisperse)
                print(f"From {explore.name} : {aliensToDisperse} aliens have reached {neighbor.name} ")
                explore.alienPop -= aliensToDisperse

            if goalTest(neighbor) == True:
                neighbor.alienArrival(aliensToDisperse)
                explore.alienPop-=aliensToDisperse
                print(aliensToDisperse,"ALIENS HAVE REACHED ALEXANDRIA!!")
                print(f"(!) There are now {neighbor.alienPop} aliens in Alexandria")
                return True
            if neighbor not in explored:
                frontier.append(neighbor)

            #print(f">> aliens in {explore.name} : {explore.alienPop} ")
        
        print(f"{explore.alienPop} aliens have remained in {explore.name}")



def calcHeuristics(city, inventoryExtra):
    #assuming one weapon can kill three aliens
    #select path that utilizes minimum weapons while killing max or all aliens 
    weaponsNeeded = city.alienPop / WEAPON_STRENGTH
    ratio = city.alienPop / city.civilianPop
    if weaponsNeeded > city.weaponStockpile :
        return city.weaponStockpile, ratio
    else : 
        return weaponsNeeded, ratio    
    
def save_cities(graph, start_city):
    global totalAliensInWorld  #global scope
    queue = [(0, start_city)]
    costs = {city_name: float('inf') for city_name in graph.cities} #set all costs to infinity except starting city
    parents = {city_name: None for city_name in graph.cities} #set predescessor to null
    costs[start_city] = 0
    visited = set()
    inventoryExta = 0
    sequence = [] # to store the sequence of cities visited
    alexandria = None

    while queue and not saveCitiesGoalTest():
        cost, city_name = heapq.heappop(queue)
        city = graph.cities[city_name]

        if(goalTest(city)):
            alexandria=city
            continue
        
        print(f"Distance travelled to reach {city_name}: {costs[city_name]}")
        if city_name in visited: 
            continue

        visited.add(city_name)
        sequence.append(city_name) 
     

        if city.alienPop > 0:
            print(f"\nBATTLEEE!! Happening in {city.name}:")
            print("We have ", city.weaponStockpile, " weapons here")
            print(f"  Initial alien population: {city.alienPop}")
            
            defeatedAliens = (city.weaponStockpile*WEAPON_STRENGTH)
            if defeatedAliens > city.alienPop:
                defeatedAliens = city.alienPop #there were more weapons than needed, so all aliens died.

            city.alienPop = city.alienPop - defeatedAliens
            totalAliensInWorld -= defeatedAliens
            
            print(f"  Alien population after the battle: {city.alienPop}")

            if city.alienPop > 0:
                print(f"   WE NEED {math.ceil(city.alienPop/WEAPON_STRENGTH)} MORE REINFORCEMENTS!!")
                if city.isMilitaryBase:
                    city.alienPop=0
                    print("Nvm we were saved cuz we had milary base:)")
        for neighbor, distance in city. neighbors.items():
            #heuristic 
            weaponsNeeded, ratio = calcHeuristics(neighbor, inventoryExta)
            total_cost= cost + distance + weaponsNeeded - ratio #h(n) + g(n)
            if neighbor.name not in visited and total_cost < costs[neighbor.name]:
                costs[neighbor.name] = total_cost
                parents[neighbor.name] = city_name
                heapq.heappush(queue, (total_cost, neighbor.name))
            
    return sequence,alexandria, parents
    
def reconstruct_path(parents, start_city, end_city):
    path = [end_city.name]
    while path[-1] != start_city.name:
        path.append(parents[path[-1]])
    path.reverse()
    return path

def finalBattle(finalCity):
    print(f"== Location: {finalCity.name} ")
    print(f"== Alien Pop: {finalCity.alienPop} ")
    print(f"== Weapons: {finalCity.weaponStockpile} ")
    print(f"== Civilian Pop: {finalCity.civilianPop} ")

    round = 1
    while finalCity.alienPop > 0 and finalCity.civilianPop > 0:
        print(f"\nRound {round}:")
        finalCity.alienPop = max(0, (finalCity.alienPop - finalCity.weaponStockpile * WEAPON_STRENGTH))
        print(f"After the battle: Remaining aliens are {finalCity.alienPop}")

        if finalCity.alienPop > 0:
            finalCity.civilianPop = max(0, (finalCity.civilianPop - finalCity.alienPop))
            print(f"After the alien attack: Remaining civilians are {finalCity.civilianPop}")

        round += 1

    if finalCity.alienPop == 0:
        print("\n* * * CONGRATS! * * * \n The civilians have won.")
    
    else: 
        if finalCity.civilianPop == 0:
            print("\n* * * DAMN! * * * \n The Aliens have won.")


def runSimulation(graph, start_city):
    global totalAliensInWorld  #global scope
    print("!---------------------ALERT------------------------!")
    print("~~~~~~~~~~~~~~~ALIEN SHIPS SPOTTED!!!~~~~~~~~~~~~~~~")
    numLocations= random.randint(2, 5)
    spawnLoc={}
    for i in range (numLocations):
        while True : 
            loc=random.choice(list(graph.cities.values())) #select  random locations from the given list where aliens will spawn 
            if loc not in spawnLoc :
                spawnLoc[loc]=random.randint(5,2000)
                print(spawnLoc[loc], "Aliens landed in ", loc.name)
                totalAliensInWorld += spawnLoc[loc]
                break
   
    print("!---------------------ALERT------------------------!")
    print("!-----ALIENS HAVE STARTED MOVING TO ALEXANDRIA-----!")
    for city in spawnLoc:
        bfs(graph, spawnLoc[city], city)
    
    print("!---------------------ALERT------------------------!")
    print("!-----TROOPS HAVE STARTED MOVING TO SAVE THE WORLD-----!")
    print("Troops are starting to move from",start_city.name, "to Alexandria!")
    sequence, finalCity, parents = save_cities(graph, start_city.name)
    # path = reconstruct_path(parents, start_city, finalCity)
    # for p in path:
    #     print (p, "->")

    print("Optimum sequence of cities visited:")
    print(" -> ".join(sequence)) #

    print("!---------------------ALERT------------------------!")
    print("!-----FINAL BATTLE HAS BEGUN IN ALEXANDRIA-----!")
    finalBattle(finalCity)
    
runSimulation(graph, random.choice(list(graph.cities.values())))


# #idea = aliens should start killing civilians too
# #idea = accumulate all weapons 