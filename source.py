import random
from collections import deque
from city import City
from graph import Graph
import time
import heapq
import math
import concurrent.futures


cityNames = ["Cairo",  "Luxor", "Aswan", "Port Said", "Suez", "Ismailia", "Faiyum", "Mansoura", "Tanta", "Hurghada", "Petra", "Dahab", "Amman", "Beirut", "Jerusalem",  "Damascus", "Baghdad", "Riyadh", "Ankara", "Aleppo", "Dubai", "Abu Dhabi", "Doha", "Muscat", "Kuwait City", "Manama", "Salalah", "Istanbul", "Tehran", "Alexandria"]    

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
            alienQuota = random.randint(int(explore.alienPop * 0.02), int(explore.alienPop * 0.05))
        
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
                return True

            frontier.append(neighbor)
        
        print(f"{explore.alienPop} aliens have remained in {explore.name}")



def calcHeuristics(city, inventoryExtra):
    #assuming one weapon can kill three aliens
    #select path that utilizes minimum weapons while killing max or all aliens 
    weaponsUtilized = city.alienPop / 3
    ratio = city.alienPop/ city.civilianPop
    
    if weaponsUtilized > city.weaponStockpile :
        return float ("inf"), float("inf")
    else : 
        return weaponsUtilized, ratio    
    
def save_cities(graph, start_city):
    queue = [(0, start_city)]
    costs = {city_name: float('inf') for city_name in graph.cities} #set all costs to infinity except starting city
    parents = {city_name: None for city_name in graph.cities} #set predescessor to null
    costs[start_city] = 0
    visited = set()
    inventoryExta=0
    while queue:
        cost, city_name = heapq.heappop(queue)
        city = graph.cities[city_name]
        if goalTest(city):
                print ('Final Battle going on in Alexandria ! ')
                return costs, parents, visited  
         
        if city_name in visited:
            continue
        visited.add(city_name)
        if city.alienPop > 0:
            print(f"\nBATTLEEE!! Happening in {city.name}:")
            print("We have ", city.weaponStockpile, " weapons here")
            print(f"  Initial alien population: {city.alienPop}")
            city.alienPop = max(0, city.alienPop - (city.weaponStockpile*3))
            print(f"  Alien population after the battle: {city.alienPop}")
            if city.alienPop > 0:
                print(f"   WE NEED {city.alienPop/3} MORE REINFORCEMENTS!!")
                if city.isMilitaryBase:
                    city.alienPop=0
                    print("  Nvm we were saved cuz we had milary base:)")
        for neighbor, distance in city. neighbors.items():
            #heuristic 
            weaponsUtilized, ratio = calcHeuristics(neighbor, inventoryExta)
            total_cost= cost + distance + weaponsUtilized - ratio # h(n) + g(n)
            if (goalTest(neighbor)) :
                total_cost= cost + distance #h(n) should be 0 at goal
            if neighbor.name not in visited and total_cost < costs[neighbor.name]:
                costs[neighbor.name] = total_cost
                parents[neighbor.name] = city_name
                heapq.heappush(queue, (total_cost, neighbor.name))
            
    return None, None, None
    


def runSimulation(graph, start_city):
    print("!---------------------ALERT------------------------!")
    print("~~~~~~~~~~~~~~~Alien ships spotted!!!~~~~~~~~~~~~~~~")
    numLocations= random.randint(2, 5)
    spawnLoc={}
    for i in range (numLocations):
        while True : 
            loc=random.choice(list(graph.cities.values())) #select 5 random locations from the given list where aliens will spawn 
            if loc not in spawnLoc :
                spawnLoc[loc]=random.randint(5,2000)
                print(spawnLoc[loc], "Aliens landed in ", loc.name)
                break
    print("!---------------------ALERT------------------------!")
    print("!-----ALIENS HAVE STARTED MOVING TO ALEXANDRIA-----!")
    for city in spawnLoc:
        bfs(graph, spawnLoc[city], city)
    print("Troops are starting to move from",start_city.name, "to Alexandria!")
    costs, parents, visited = save_cities(graph, start_city.name)
    
    
runSimulation(graph, random.choice(list(graph.cities.values())))


# #idea = aliens should start killing civilians too
# #idea = accumulate all weapons 