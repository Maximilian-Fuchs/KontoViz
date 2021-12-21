# temp cell for KontoLib Contents
import os
from pprint import pprint
from datetime import timedelta
from datetime import datetime as dt
from collections import defaultdict
import matplotlib.pyplot as plt

plt.style.use('ggplot')

#############
# Read Data #
#############

def read_text(file_path, encoding='utf-8'):
    """Reads a file of the specified encoding to a python string"""
    with open(file_path, 'rb') as f:
        text = f.read().decode(encoding)
    return text

def get_records_raw(data_dir, encoding='utf-8'):
    """Returns list of records as strings from the data director"""
    records_raw = list()
    for filename in sorted(os.listdir(data_dir)):
        if filename.endswith(".csv"):
            records_raw.append(read_text(os.path.join(data_dir, filename), 'cp1252'))
    
    return records_raw

#####################
# Structure Records #
#####################

def get_sections(auszug_raw):
    """Splits a record into its entries and adds descriptions"""
    sections_list = auszug_raw.split("\r\n\r\n")
    # assert that the document is structured as expected
    assert(len(sections_list) == 6)
    
    # create dictionary that names the sections
    named_sections = dict()
    # create section names
    section_names = ["Bank name", "Document Description", "Document Info", "Start Date", "Bookings", "Start/End Sum"]
    # name the sections
    for index in range(len(sections_list)):
        named_sections[section_names[index]] = sections_list[index]

    return named_sections

def get_datetime(date_str):
    """Structures the german date notation into a datetime object"""
    
    # dirty bugfix
    if date_str == "30.02.2021":
        date_str = "28.02.2021"
        
    result = dt.strptime(date_str, "%d.%m.%Y")
    
    return result

def get_time(time_str):
    return dt.strptime(time_str, "%H:%M:%S")

def get_balance(balance_string, haben_soll):
    """Returns a float from a balance string and a Haben_Soll indicator"""
    betrag = float(balance_string.replace(".", "").replace(",", "."))
    if haben_soll == "H":
        return betrag
    if haben_soll == "S":
        return betrag*-1
    else:
        raise ValueError

def extract_header_atts(header_line):
    """Parses Header attributes from bookings section"""
    attributes = list()
    for field in header_line.replace('" "', "Haben/Soll").split(";"):
        attributes.append(field.replace('"', ''))
    return attributes

def structure_document_info(doc_info_raw):
    """Structures the information from the "Document Info" section"""
    doc_info = '{' + doc_info_raw.replace(';;', ',').replace(':";', '":').replace('\r\n', ',') + '}'
    doc_info = eval(doc_info)
    doc_info['BLZ'] = int(doc_info['BLZ'])
    doc_info['Datum'] = get_datetime(doc_info['Datum'])
    doc_info['Konto'] = int(doc_info['Konto'])
    doc_info['Uhrzeit'] = get_time(doc_info['Uhrzeit']).replace(
        year=doc_info['Datum'].year,
        month=doc_info['Datum'].month,
        day=doc_info['Datum'].day)
    return doc_info

def structure_start_end_section(se_section):
    """Structures the Start/End Section"""
    # split into start and end info
    se_section_dict = dict()
    se_sections = se_section.split('\r\n')

    # split info into fields
    start_fields = [field.replace('"', '') for field in se_sections[0].split(';')]
    assert(start_fields[-4] == "Anfangssaldo")
    end_fields = [field.replace('"', '') for field in se_sections[1].split(';')]
    assert(end_fields[-4] == "Endsaldo")

    # parse information from fields into dictionary
    se_section_dict["Start"] = dict()
    se_section_dict["End"] = dict()
    se_section_dict["Start"]["Date"] = get_datetime(start_fields[0])
    se_section_dict["Start"]["Balance"] = get_balance(start_fields[-2], start_fields[-1])
    se_section_dict["End"]["Date"] = get_datetime(end_fields[0])
    se_section_dict["End"]["Balance"] = get_balance(end_fields[-2], end_fields[-1])


    return se_section_dict

######################
# Structure Bookings #
######################

def structure_bookings(bookings_raw):
    # extract attributes from first line
    attributes = extract_header_atts(bookings_raw.split('\r\n')[0])

    # split bookings
    raw_bookings_list = bookings_raw.split('\r\n')[1:]
    
    # remove linebreaks
    raw_bookings_list = [raw_booking.replace("\n", "") for raw_booking in raw_bookings_list]

    # create list to hold dictionary representations of bookings
    structured_bookings = list()
    # iterate over bookings
    for raw_booking in raw_bookings_list:
        # create dict to store structured booking data
        bdict = dict()
        # extract info from fields
        raw_booking_values = raw_booking.replace('"','').split(";")
        # connect attributes with values
        att_val_touples = list(zip(attributes, raw_booking_values))
        # convert tuples into dict entries
        for att, val in att_val_touples:
            bdict[att] = val
        # set datatypes for booking values
        bdict['Valuta'] = get_datetime(bdict['Valuta'])
        bdict['Buchungstag'] = get_datetime(bdict['Buchungstag'])
        bdict['Umsatz'] = get_balance(bdict['Umsatz'], bdict['Haben/Soll'])
        # add dictionary to structured bookings list
        structured_bookings.append(bdict)
    return structured_bookings


def structure_sections(named_sections):
    """Structures the data in the different sections of a record"""
    # initialize dict to hold structured information
    sections_structured = dict()
    
    # structure Bank name
    sections_structured["Bank name"] = named_sections["Bank name"].replace('"', '')

    # structure Document Description
    sections_structured["Document Description"] = named_sections["Document Description"].replace('"', '')
    # assert that content is as expected
    assert(sections_structured["Document Description"] == "Umsatzanzeige")

    # structure "Document Info"
    sections_structured["Document Info"] = structure_document_info(named_sections["Document Info"])

    # structure Start Date
    # skip this section as it is not of importance anyways and it will throw an error if all bookings are loaded (and not from a 4weeks period for example)

    # structure bookings
    sections_structured["Bookings"] = structure_bookings(named_sections["Bookings"])

    # structure Start/End Sum
    sections_structured["Start/End Sum"] = structure_start_end_section(named_sections["Start/End Sum"])
    
    return sections_structured

def eliminate_duplicate_bookings(records_structured):
    """Collects bookings from all records and eliminates duplicates"""
    all_bookings = list()
    all_bookings_set = set()
    # for each record
    for record in records_structured:
        # for each booking
        for booking in record['Bookings']:
            # check if duplicate
            old_set_len = len(set(all_bookings_set))
            all_bookings_set.add(str(booking))
            if len(all_bookings_set) > old_set_len:
                all_bookings.append(booking)
    return all_bookings
    
    