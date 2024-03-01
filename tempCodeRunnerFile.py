import random
from collections import deque
from city import City
from graph import Graph

import heapq


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
        for _ in range(random.randint(0, 2)):  # Assign 0-2 additional neighbors to each city
            neighbor = random.choice(list(graph.cities.values()))
            if neighbor == city or neighbor in city.neighbors:  # Avoid self-loops and duplicate edges
                continue
            distance = random.randint(10, 100)
            graph.addEdge(city.name, neighbor.name, distance)  #bidirectional edge

    return graph

graph = createGraph(cityNames)


def printGraph(graph):
    print(f"Total number of cities: {len(graph.cities)}")
    for city in graph.cities.values():
        print(f"{city.name} is connected to:")
        for neighbor, distance in city.neighbors.items():
            print(f"  {neighbor.name} with distance {distance}")
            


#printGraph(graph)

# Goal Test to see if current node is Alexandria i.e. Goal Node
def goalTest(node):
    if node.name == "Alexandria":
        return True
    return False

#BFS On graph to allocate alien quota etc. 
def bfs(graph, total_aliens):
    # Random source city
    source_city = random.choice(list(graph.cities.values()))
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
        neighborsToInvade = [neighbor for neighbor in explore.neighbors if neighbor not in frontier and neighbor not in explored and neighbor.alienPop == 0]

        #aliens get divided in neighboring cities
        aliensToDisperse = totalDispersable // len(neighborsToInvade) if neighborsToInvade else 0

        for neighbor in neighborsToInvade:
            #  move to the neighboring city
            if aliensToDisperse > 0:
                neighbor.alienArrival(aliensToDisperse)
                print(f"From {explore.name} : {aliensToDisperse} aliens have reached {neighbor.name} ")
                explore.alienPop -= aliensToDisperse

            if goalTest(neighbor) == True:
                print("ALIENS HAVE REACHED ALEXANDRIA!!")
                return True

            frontier.append(neighbor)
        
        print(f"{explore.alienPop} aliens have remained in {explore.name}")
#total aliens=100
bfs(graph, 1000)




def save_cities(graph, start_city_name):
    # Create a priority queue and a dictionary to store the minimum number of weapons used to reach each city
    queue = [(0, start_city_name)]
    min_weapons = {city_name: float('inf') for city_name in graph.cities}
    min_weapons[start_city_name] = 0
    visited = set()

    while queue:
        weapons_used, city_name = heapq.heappop(queue)
        city = graph.cities[city_name]

        if city_name in visited:
            continue
        visited.add(city_name)

        if city.isMilitaryBase:
            weapons_used += city.weaponStockpile

        # If this path uses fewer weapons than the current minimum, update the minimum
        if weapons_used < min_weapons[city_name]:
            min_weapons[city_name] = weapons_used

            # Add the city's neighbors to the queue
            for neighbor, distance in city.neighbors.items():
                total_weapons = weapons_used + distance  # The cost of the path is the number of weapons used plus the distance
                if neighbor.name not in visited:
                    heapq.heappush(queue, (total_weapons, neighbor.name))

    return min_weapons

min_weapons = save_cities(graph, "Cairo")
for city_name, weapons in min_weapons.items():
    print(f"The minimum number of weapons to save {city_name} is {weapons}")