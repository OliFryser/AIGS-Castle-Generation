class DynamicCeiling:
    def __init__(self, ceiling = 1, indecies = 9, maximum = 30, floor =0) -> None:
        self.ceiling = ceiling
        self.indecies = indecies
        self.maximum = maximum
        self.floor = floor


    def calcValue(self, value):
        result = round(((value - self.floor)/ (self.ceiling)) * self.indecies)
        return result
    
    def redefineCeiling(self, newCeiling):
        if newCeiling - self.floor < self.maximum and newCeiling -self.floor> self.ceiling:
            self.ceiling = newCeiling - self.floor
            return True
        return False

    def increaseCeiling(self, value):       
        self.indecies = (self.ceiling - value) * (self.indecies/2)