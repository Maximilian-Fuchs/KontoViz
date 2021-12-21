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

        if turnus.lower() == 'monthly':
            self.turnus = lambda dt_obj: dt_obj.day == self.start.day
        if turnus.lower() == 'weekly':
            self.turnus = lambda dt_obj: dt_obj.weekday() == self.start.weekday()
        if turnus.lower() == 'daily':
            self.turnus = lambda dt_obj: True


    def counts(self, dt_obj):
        # check if prognosis counts on that day
        if self.start.day == dt_obj.day and self.start.month == dt_obj.month :
            return True
        elif not self.repeats:
            return False
        elif self.expires and dt_obj > self.end:
            return False
        elif self.turnus(dt_obj):
            return True
        else:
            return False


########
# TEST #
########

lohn = Prognosis(
            description="Lohn bis Juni",
            start="20.12.2021",
            amount=6000,
            category='Gains', 
            turnus='monthly',
            end="01.06.2022")

prognosis_list = [lohn]

from datetime import date, timedelta

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

start_date = get_datetime("20.12.2021")
end_date = get_datetime("20.12.2022")
for single_date in daterange(start_date, end_date):
    for prog in prognosis_list:
        if prog.counts(single_date):
            res = prog.description + " " + single_date.strftime("%d.%m.%Y")
            print(res)

##########
# TEST 2 #
##########

d = dict()
d["description"] = "Lohn bis Juni"
d["start"] = "20.12.2021"
d["amount"] = 6000
d["category"] = 'Gains'
d["turnus"] = 'monthly'
d["end"] = "01.06.2022"
l = [d, d]
import json
PROG_JSON = "/Users/mfuchs/HiDrive/users/sphere/kontoviznew/KontoViz/data/Prognosen.json"
with open(PROG_JSON, 'w') as f:
    json.dump(l, f)
