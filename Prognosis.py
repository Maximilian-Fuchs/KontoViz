from KontoLib import *

class Prognosis:
    def __init__(self, description, start, amount, category='other', turnus=None, end=None):
        # set properties
        self.description = description
        self.start = get_time(start)
        self.expires = False
        self.repeats = False
        if turnus:
            self.repeats = True
        self.end = False
        if end:
            self.expires = True
        self.end = end
        self.amount = float(amount)
        self.category = category
        self.turnus = turnus
