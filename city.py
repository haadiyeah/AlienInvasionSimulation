class City: 
    def __init__(self, name, alienPop, civilianPop, isMilitaryBase, weaponStockpile):
        self.name=name
        self.alienPop=alienPop
        self.civilianPop=civilianPop
        self.isMilitaryBase=isMilitaryBase
        self.weaponStockpile=weaponStockpile
        self.neighbors={}

    def addNeighbour(self, city, distance):
        self.neighbors[city] = distance

    def connectedCities(self):
        return self.neighbors.keys()   
    
    def alienArrival(self, num_aliens):
        self.alienPop += num_aliens