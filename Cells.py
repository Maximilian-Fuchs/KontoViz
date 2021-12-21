from KontoLib import *

def load_records(DATA_DIR):
    # get records as text
    records_raw = get_records_raw(DATA_DIR)
    # load structured sections for each record
    records_structured = list()
    for raw_record in records_raw:
        sections_structured = structure_sections(get_sections(raw_record))
        records_structured.append(sections_structured)
    
    ################
    # SANITY CHECK #
    ################

    # Check if the calculated sum meets the end balance for each record
    # for each record
    for record in records_structured:
        start_balance = record['Start/End Sum']['Start']['Balance']
        end_balance = record['Start/End Sum']['End']['Balance']
        bookings = record['Bookings']
        # sum up bookings
        balance = start_balance
        for booking in bookings:
            balance += booking["Umsatz"]
        # check if summed up amount meets end balance
        assert(round(balance,2) == end_balance)
    print("ok")

    ######

    for record in records_structured:
        all_bookings = list()
        all_bookings_set = set()
        # for each booking
        for booking in record['Bookings']:
            # check if duplicate
            old_set_len = len(set(all_bookings_set))
            all_bookings_set.add(str(booking))
            if len(all_bookings_set) > old_set_len:
                all_bookings.append(booking)
            else:
                print('false')
    # nope. ok.

    ## Eliminate duplicate bookings ##
    all_bookings = eliminate_duplicate_bookings(records_structured)

    # check if sum of all bookings matches my kontostand
    def get_start_date(record):
        return record['Start/End Sum']['Start']['Date']

    def get_earliest_record(records_structured):
        return sorted(records_structured, key=lambda d: get_start_date(d))[0]

    def get_latest_record(records_structured):
        return sorted(records_structured, key=lambda d: get_end_date(d))[-1]

    def get_end_date(record):
        return record['Start/End Sum']['End']['Date']

    # get earliest start balance
    def get_earliest_start_balance(records_structured):
        earliest_record = get_earliest_record(records_structured)
        return earliest_record['Start/End Sum']['Start']['Balance']

    balance = get_earliest_start_balance(records_structured)
    for booking in eliminate_duplicate_bookings(records_structured):
        if booking['Buchungstag'] >= dt(2020, 12, 8, 0, 0):
            balance += booking["Umsatz"]
    print(balance)

    # for booking in bookings:
            # balance += booking["Umsatz"]

    pprint(records_structured[-1]['Start/End Sum'])

    def get_balances(records_structured):
        result = list()
        for record in records_structured:
            result.append(record['Start/End Sum'])
        return result

    def get_documented_daterange(records_structured):
        result = daterange(get_start_date(get_earliest_record(records_structured)),
                        get_end_date(get_latest_record(records_structured)))
        return result

    def daterange(start_date, end_date):
        for n in range(int((end_date - start_date).days) +1 ):
            yield start_date + timedelta(n)

    def get_balance_per_day(records_structured):
        day_dict = defaultdict(lambda: defaultdict(list))
        days = [day for day in get_documented_daterange(records_structured)]
        print(days[-1])

        bookings = eliminate_duplicate_bookings(records_structured)
        for booking in bookings:
            day_dict[booking['Buchungstag']]['bookings'].append(booking)
        balances = get_balances(records_structured)
        for bal in balances:
            day_dict[bal['Start']['Date']]['start_balance'].append(bal['Start']['Balance'])
            day_dict[bal['End']['Date']]['end_balance'].append(bal['End']['Balance'])

        balance_dict = dict()
        balance = get_earliest_start_balance(records_structured)
        for day in days:
            # if there is a start balance on tht day, set balance to this
            try:
                if day_dict[day]['start_balance']:
                    balance = day_dict[day]['start_balance'][-1]
            except KeyError:
                pass
            
            # add all bookings from that day to the balance
            balance += sum(booking["Umsatz"] for booking in day_dict[day]['bookings'])

            # if there is an end balance for that day, set balance to this
            try:
                if day_dict[day]['end_balance']:
                    balance = day_dict[day]['end_balance'][-1]
            except KeyError:
                pass
            balance_dict[day] = balance
        return balance_dict
    # pprint(balance_dict)

    balance_dict = get_balance_per_day(records_structured)

DATA_DIR = "/Users/mfuchs/HiDrive/users/sphere/kontoviznew/KontoViz/data"
load_records(DATA_DIR=DATA_DIR)