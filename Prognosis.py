from KontoLib import *

class Prognosis:
    def __init__(self, description, start, amount, category='other', turnus=None, end=None):
        # set properties
        self.description = description
        self.start = get_time(start)
        self.expires = False
        if end:
            self.expires = True
        self.amount = float(amount)
        self.category = category
        self.turnus = turnus
