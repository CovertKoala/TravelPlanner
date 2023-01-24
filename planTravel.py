from scraper import FlightScraper
import flightparser
import traveldata
import json
import copy
import argparse
import re
from datetime import date

def get_commandline_reqeust():
    '''Example outputs:
            {'outbound': ['2023-02-03', 'DCA', 'PNS'], 'outbound_times': ['1630,2359'],
                'inbound': None, 'inbound_times': None, 
                'log': True, 'silent': True, 'file': False}
            {'outbound': ['2023-02-03', 'DCA', 'PNS'], 'outbound_times': ['1630,2359'],
                'inbound': ['2023-02-03', 'DCA', 'PNS'], 'inbound_times': ['1630,2359'], 
                'log': True, 'silent': True, 'file': False}
    '''
    parser = argparse.ArgumentParser(
                prog="python planTravel.py",
                description='''Returns all flight options to/from a destination.  Outbound flight required. 
                               Inbound flight optional.''')
    outbound_group = parser.add_argument_group("Outbound Flight Information")
    outbound_group.add_argument('-o','--outbound', nargs=3, required=True, metavar=("YYYY-MM-DD", "AAA(,BBB)?(,CCC)?", "XXX(,YYY)?(,ZZZ)?"),
                        help='''REQUIRED. Must contain three arguments (date departure_ICAOs arrival_ICAOs)
                                with up to three, three letter ICAOs separated by a comma and date in YYYY-MM-DD:
                                ex: 2023-02-03 BWI,DCA,IAD PNS,VPS''')
    outbound_group.add_argument('-ot','--outbound_times', nargs=1, metavar="HHMM,HHMM",
                        help='''Constrain flight search to flights which depart/arrive during this window.
                                Must be two times in 24 hour format separated only by a ','. ''')
    inbound_group = parser.add_argument_group("Inbound Flight Information")
    inbound_group.add_argument('-i','--inbound',  nargs=3, metavar=("YYYY-MM-DD", "AAA,BBB,CCC", "XXX,YYY,ZZZ"),
                        help='''OPTIONAL.  Must contain three arguments (date departure_ICAOs arrival_ICAOs)
                                with up to three, three letter ICAOs separated by a comma and date in YYYY-MM-DD:
                                ex: 2023-02-03 BWI,DCA,IAD PNS,VPS''')
    inbound_group.add_argument('-it','--inbound_times', nargs=1, metavar="HHMM,HHMM",
                        help='''Constrain flight search to flights which depart/arrive during this window.
                                Must be two times in 24 hour format separated only by a ','. ''')
    parser.add_argument('-l','--log', action='store_true', default=True,
                        help='''Writes raw source data to file and parsed flight information (in JSON format) to file. 
                                Default is to write logs.''')
    parser.add_argument('-s','--silent', action='store_true', default=True,
                        help='''Prevents results from printing to screen.  Scraping/Parsing/Writing progress still printed.''')
    parser.add_argument('-f','--file', action='store_true', default=False,
                        help='''Pulls data for planTravel.py from a previous run that logged results.
                                If the log file for the requested flight offer does not exist, planTravel will revert
                                to pulling info from the web.  Default is to pull from web.''')    
    args = parser.parse_args()
    requested_options = vars(args)

    ICAO_regex = re.compile(r'^[A-Z]{3}(,[A-Z]{3}){0,2}$', re.IGNORECASE) 
    date_regex = re.compile(r'202\d-(0\d|1[0-2])-([01]\d|3[01])')
    time_regex = re.compile(r'^([01]\d|2[0-3])[0-5][0-9],([01]\d|2[0-3])[0-5]\d$')
    error = False

    # Check outbound flight entries for errors
    if not date_regex.search(requested_options["outbound"][0]):
        print("Outbound date incorrectly input. Must be YYYY-MM-DD.")
        error = True
    try:
        if date.fromisoformat(requested_options["outbound"][0]) < date.today():
            print("Outbound date must be today or in the future.")
            error = True
    except ValueError:
        print("Outbound date is not a valid date.")
        error = True
    if not ICAO_regex.search(requested_options["outbound"][1]):
        print("Outbound departure ICAO(s) incorrectly input.  Must be XXX(,YYY){0,2}.")
        error = True
    if not ICAO_regex.search(requested_options["outbound"][2]):
        print("Outbound arrival ICAO(s) incorrectly input.  Must be XXX(,YYY){0,2}.")
        error = True
    if requested_options["outbound_times"]:
        if not time_regex.search(requested_options["outbound_times"][0]):
            print("Outbound time window incorrectly input.  Must be HHMM,HHMM.")
            error = True

    # Check inbound flight entries for errors
    if requested_options["inbound"]:
        if not date_regex.search(requested_options["inbound"][0]):
            print("Inbound date incorrectly input. Must be YYYY-MM-DD.")
            error = True
        try:
            if date.fromisoformat(requested_options["inbound"][0]) < date.today():
                print("Inbound date must be today or in the future.")
                error = True
        except ValueError:
            print("Inbound date is not a valid date.")
            error = True

        if not ICAO_regex.search(requested_options["inbound"][1]):
            print("Inbound departure ICAO(s) incorrectly input.  Must be XXX(,YYY){0,2}.")
            error = True
        if not ICAO_regex.search(requested_options["inbound"][2]):
            print("Inbound arrival ICAO(s) incorrectly input.  Must be XXX(,YYY){0,2}.")
            error = True
        if requested_options["inbound_times"]:
            if not time_regex.search(requested_options["inbound_times"][0]):
                print("Inbound time window incorrectly input.  Must be HHMM,HHMM.")
                error = True
    elif requested_options["inbound_times"]:
        print("Inbound time window provided without inbound flight options.")
        error = True

    if error:
        exit()

    return requested_options


def scrape_parse_write(flight_options:dict, source_from_file=False, log=True):
    '''flight_options' dict must have the following:
            {
                'travel date': "YYYY-MM-DD",          <- single string date
                'travel times': "HHMM,HHMM"           <- Single string of "earliest,latest" times
                'departure ICAOs': "ICAO #1,ICAO#2",  <- string of three letter ICAOs
                'arrival ICAOs': "ICAO #1,ICAO#2"     <- string of three letter ICAOs
            }

        If source_from_file = True then load from file.
        If log = True then save web source/flights to file.
        '''
    if not source_from_file:
        flight_scraper = FlightScraper()
    travel_date = flight_options["travel date"]
    departure_ICAO = flight_options["departure ICAOs"]
    arrival_ICAO = flight_options["arrival ICAOs"]

    source_file = f"RawFlightData/kayak_source_{travel_date}_{departure_ICAO}-{arrival_ICAO}.txt"
    json_file = f"RawFlightData/{travel_date}_{departure_ICAO}-{arrival_ICAO}.txt"
    # Load source data to parse
    if source_from_file:
        # Load source data from PREVIOUSLY written log file
        with open(source_file,'r') as f:
            web_source_code = f.read()
        print(f"Pulled flight data for {departure_ICAO}-{arrival_ICAO} on {travel_date} from file!! " +'\u30c4')
    else:
        # Load source data from web
        web_source_code = flight_scraper.scrape_flight_offer_page(flight_options)
        print(f"Pulled flight data for {departure_ICAO}-{arrival_ICAO} on {travel_date} from web!! " +'\u30c4')
    
    # Parse flight data
    flight_parser = flightparser.FlightParser(travel_date, web_source_code)
    flight_offers = flight_parser.get_flight_offers()

    if log:
        # Save raw source data to file
        with open(source_file,'w') as f:
            f.write(ascii(web_source_code))
        # Save parsed flight data in JSON format
        with open(json_file,'w') as f:
            json.dump(obj=flight_offers, fp=f, cls=traveldata.FlightEncoder, indent=4)
        
        if not source_from_file:
            flight_scraper.close_scraper()


# Not needed since Kayak allos pulling multiple departure/arrival ICAOs on one page
# def multi_scrape_parse_write(flight_options, source='w', log=True):
#     '''Use input 'flight_options' dict to scrape data off of Kayak.  Dict must have the following:
#         {
#             'travel date': "YYYY-MM-DD",              <- single string
#             'travel times': ["earliest", "latest"],   <- list of two strings
#             'departure ICAOs': ["ICAO #1", "ICAO#2"], <- list of three letter strings
#             'arrival ICAOs': FL_ICAO                  <- list of three letter strings
#         }
#         source = 'f' (source from file); 'w' (source from web).
#         log = True to save web source to file.'''
#     # 'f' = source from file; 'w' = source from web; log = True to save web source to file

#     temp_flight_options = copy.deepcopy(flight_options)
#     flight_scraper = FlightScraper()
#     for departure_ICAO in flight_options["departure ICAOs"]:
#         for arrival_ICAO in flight_options["arrival ICAOs"]:
#             temp_flight_options["departure ICAOs"] = [departure_ICAO]
#             temp_flight_options["arrival ICAOs"] = [arrival_ICAO]
#             single_scrape_parse_write(flight_scraper, temp_flight_options, source='w', log=True)
#     flight_scraper.close_scraper()
#     return





if __name__ ==  "__main__":

    requested_options = get_commandline_reqeust()

    # Get outbound flight data
    outbound_flight_options = {
        'travel date': requested_options["outbound"][0],
        'departure ICAOs': requested_options["outbound"][1],
        'arrival ICAOs': requested_options["outbound"][2]}
    if requested_options["outbound_times"]:
        outbound_flight_options['travel times'] = requested_options["outbound_times"][0]
    else:
        outbound_flight_options['travel times'] = requested_options["outbound_times"]
    scrape_parse_write(outbound_flight_options, source_from_file=requested_options["file"], log=requested_options["log"])

    # Get inbound flight data
    if requested_options["inbound"]:
        print("inbound")
        inbound_flight_options = {
            'travel date': requested_options["inbound"][0],
            'departure ICAOs': requested_options["inbound"][1],
            'arrival ICAOs': requested_options["inbound"][2]}
        if requested_options["inbound_times"]:
            inbound_flight_options['travel times'] = requested_options["inbound_times"][0]
        else:
            inbound_flight_options['travel times'] = requested_options["inbound_times"]
        scrape_parse_write(inbound_flight_options, source_from_file=requested_options["file"], log=requested_options["log"])
    