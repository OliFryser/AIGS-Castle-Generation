class DynamicDiscreteKey:
    def __init__(self, ceiling = 1, indeces = 9) -> None:
        self.ceiling = ceiling
        self.indeces = indeces

    def calcValue(self, value):
        return round((value / (self.ceiling)) * self.indeces)
    
    def redefineCeiling(self, newCeiling):
        self.ceiling = newCeiling

    def increaseCeiling(self, value):
        while self.ceiling < value:
            self.ceiling += self.indeces +1
       