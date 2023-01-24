from bs4 import BeautifulSoup as BS
from traveldata import Flight
import datetime

class FlightParser:

    def __init__(self, date, page_source):
        self.soup = BS(page_source, 'html.parser')
        self.date = datetime.date.fromisoformat(date)
        self.daily_flight_list = []

    def get_flight_offers(self):

        flight_data = self.soup.find(name="div", class_="resultInner")
        # print(flight_data)
        while flight_data:
            #Parse start, end, and airline
            div_section_time = flight_data.find(name="div", class_="section times")
            start_dt, end_dt, airline = self.__extract_flight_section_times(div_section_time)

            #Parse start/end ICAOs and total time
            div_section_duration = flight_data.find(name="div", class_="section duration allow-multi-modal-icons")
            duration, departure_ICAO, arrival_ICAO = self.__extract_flight_section_duration(div_section_duration)

            #Parse layovers
            div_section_stops = flight_data.find(name="div", class_="section stops")
            layovers = self.__extract_flight_section_stops(div_section_stops)

            #Parse Price
            price = flight_data.find(name="span", class_="price-text").string.strip()[2:]
            #Southwest flight prices not included
            if airline != "Southwest":
                price = price[1:]
            else:
                price = 0


            new_flight = Flight(departure_date=self.date, airline=airline,start_dt=start_dt, end_dt=end_dt,
                                departure_ICAO=departure_ICAO, arrival_ICAO=arrival_ICAO, duration=duration,
                                price=price,layovers=layovers)

            print(new_flight)
            self.daily_flight_list.append(new_flight)

            flight_data = flight_data.find_next(name="div", class_="resultInner")
        # print(f"Number of flights pulled: {len(self.daily_flight_list)}.")

        return self.daily_flight_list

        
    def __extract_flight_section_times(self, div_section_time):

        #Parse Departure Date/time
        departure_data = div_section_time.find(name = 'span', class_='time-pair')
        departure_time = self.__pull_time(departure_data)
        start_dt = datetime.datetime.combine(self.date, departure_time)

        #Parse Arrival Date/Time
        arrival_data = departure_data.find_next(name = 'span', class_='time-pair')
        arrival_time = self.__pull_time(arrival_data)
        end_dt = datetime.datetime.combine(self.date, arrival_time)

        #Parse Arline
        airline = div_section_time.find(name='div', class_='bottom').string[2:-2].split(' ')[0]

        return start_dt, end_dt, airline


    def __pull_time(self, time_pair):

        time_string = time_pair.find(name='span', class_='base-time').string
        hour, minute = time_string.strip().split(':')
        meridium = time_pair.find_next(name = 'span', class_='time-meridiem meridiem').string
        
        hour = int(hour)
        minute = int(minute)
        if meridium == "pm" and hour < 12:
            hour += 12

        time = datetime.time(hour, minute)

        return time


    def __extract_flight_section_duration(self, div_section_duration):

        #Parse Duration
        duration = div_section_duration.find(name='div', class_='top').string
        duration = duration.strip()[2:]

        #Parse Departure ICAO
        departure_data = div_section_duration.find(name = 'span', class_='airport-name')
        departure_ICAO = departure_data.string.strip()[2:-2]

        #Parse Arrival ICAO
        arrival_data = departure_data.find_next(name = 'span', class_='airport-name')
        arrival_ICAO = arrival_data.string.strip()[2:-2]

        return duration, departure_ICAO, arrival_ICAO

    def __extract_flight_section_stops(self, div_section_stops):

        ICAOs = []
        #Pull connection ICAOs
        ICAO = div_section_stops.find(name='span', class_='js-layover')

        while ICAO:
            ICAOs.append(ICAO.string)
            ICAO = ICAO.find(name='span', class_='js-layover')

        return ICAOs
