# Class Bid

class Bid():
    INSTANCES = 1

    def __init__(self, values, discount=1, us_index=None, domain=None):
        self.domain = domain
        self.values = values
        self.discount = discount
        self.index = us_index
        self.id = Bid.INSTANCES
        Bid.INSTANCES += 1

    def get_value(self, index):
        return self.values[index]
