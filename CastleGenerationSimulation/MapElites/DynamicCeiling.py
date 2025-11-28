class DynamicCeiling:
    def __init__(self, ceiling = 1, indices = 9) -> None:
        self.ceiling = ceiling
        self.indices = indices

    def calcValue(self, value):
        return round((value / (self.ceiling)) * self.indices)
    
    def redefineCeiling(self, newCeiling):
        self.ceiling = newCeiling

    def increaseCeiling(self, value):       
        self.indices = (self.ceiling - value) * (self.indices/2)
       