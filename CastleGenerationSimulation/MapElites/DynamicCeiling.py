class DynamicCeiling:
    def __init__(self, ceiling = 1, indices = 9, maximum = 30) -> None:
        self.ceiling = ceiling
        self.indices = indices
        self.maximum = maximum


    def calcValue(self, value):
        return round((value / (self.ceiling)) * self.indices)
    
    def redefineCeiling(self, newCeiling):
        if newCeiling < self.maximum and newCeiling > self.ceiling:
            self.ceiling = newCeiling
            return True
        return False

    def increaseCeiling(self, value):       
        self.indices = (self.ceiling - value) * (self.indices/2)
       