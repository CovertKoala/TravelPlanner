from scraper import FlightScraper
import flightparser
import traveldata
import json

def single_scrape_parse_write(flight_scraper, fligh_options, source='w', log=True):
    # 'f' = source from file; 'w' = source from web; log = True to save web source to file

    # Load source data to parse
    if source == 'w':
        # Load source data from web
        web_source_code = flight_scraper.scrape_flight_offer_page(
                        date=travel_date, departureAirport=departure_ICAO, arrivalAirport = arrival_ICAO)
        print(f"Pulled flight data for {departure_ICAO}-{arrival_ICAO} on {travel_date} from web!! " +'\u30c4')
    elif source == 'f':
        # Load source data from PREVIOUSLY written log file
        with open(filename,'r') as f:
            web_source_code = f.read()
        print(f"Pulled flight data for {departure_ICAO}-{arrival_ICAO} on {travel_date} from file!! " +'\u30c4')
    else:
        # Need to update to pass an error
        print("Invalid source argument!!")

    # Save data to file
    if log:
        filename = f"RawFlightData/kayak_source_{travel_date}_{departure_ICAO}-{arrival_ICAO}.txt"
        with open(filename,'w') as f:
            f.write(ascii(web_source_code))
    
    # Parse flight data from source web or file
    flight_parser = flightparser.FlightParser(travel_date, web_source_code)
    flight_offers = flight_parser.get_flight_offers()

    if log:
        # Save parsed flight data in JSON format for later use
        filename = f"RawFlightData/{travel_date}_{departure_ICAO}-{arrival_ICAO}.txt"
        with open(filename,'w') as f:
            json.dump(obj=flight_offers, fp=f, cls=traveldata.FlightEncoder, indent=4)


def multi_spw(fligh_options, source, log):
    # 'f' = source from file; 'w' = source from web; log = True to save web source to file

    flight_scraper = FlightScraper()
    for departure_ICAO in DC_ICAO:
        for arrival_ICAO in FL_ICAO:
            single_scrape_parse_write(flight_scraper, fligh_options)
    flight_scraper.close_scraper()
    return

if __name__ ==  "__main__":

    outbound_travel_date = "2023-02-03"
    inbound_travel_date = "2023-02-05"
    outbound_times = [1630,2359]
    inbound_times = [1200, 2359]
    DC_ICAO = ["WAS"]
    FL_ICAO = ["PNS","VPS"]

    fligh_options = {'date': 0 , 'times': outbound_times, 'departure ICAOs': , 'arrival ICAOs':}

    # 'f' = source from file; 'w' = source from web; log = True to save web source to file
    multi_spw(fligh_options, source='w', log=True)
