from KontoLib import *

class Prognosis:
    def __init__(self, description, start, amount, category='other', turnus=None, end=None):
        # set properties
        self.description = description
        self.start = get_datetime(start)
        self.amount = float(amount)
        self.category = category

        
        self.repeats = False
        if turnus:
            self.repeats = True
        self.expires = False
        if end:
            self.expires = True
            self.end = get_datetime(end)

        if not turnus:
            self.turnus = None
        elif turnus.lower() == 'monthly':
            self.turnus = lambda dt_obj: dt_obj.day == self.start.day
        elif turnus.lower() == 'weekly':
            self.turnus = lambda dt_obj: dt_obj.weekday() == self.start.weekday()
        elif turnus.lower() == 'daily':
            self.turnus = lambda dt_obj: True
        elif turnus.lower() == 'yearly':
            self.turnus = lambda dt_obj: dt_obj.day == self.start.day and dt_obj.month == self.start.month


    def counts(self, dt_obj):
        # check if prognosis counts on that day
        same_day = self.start.day == dt_obj.day 
        same_month = self.start.month == dt_obj.month
        same_year = self.start.year == dt_obj.year
        same_date = all([same_day, same_month, same_year])
        if same_date:
            return True
        elif not self.repeats:
            return False
        elif self.expires and dt_obj > self.end:
            return False
        elif self.start > dt_obj:
            return False
        elif self.turnus(dt_obj):
            return True
        else:
            return False
