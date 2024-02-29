#definiton of graph class
class Graph:
    def __init__(self):
        self.cities={}

    def addCity(self, city):
        self.cities[city.name] = city   

    def addEdge(self, fromCity, toCity, distance):
        self.cities[fromCity].addNeighbour(self.cities[toCity], distance)
        self.cities[toCity].addNeighbour(self.cities[fromCity], distance)