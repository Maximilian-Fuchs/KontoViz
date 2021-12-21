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

from datetime import date, timedelta

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

start_date = get_datetime("20.12.2021")
end_date = get_datetime("20.12.2022")
for single_date in daterange(start_date, end_date):
    print(single_date.strftime("%d.%m.%Y"))

