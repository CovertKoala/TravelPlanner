from bs4 import BeautifulSoup as BS
from traveldata import Flight
import datetime

class KayakFlightParser:


    def __init__(self, date, page_source):
        self.soup = BS(page_source, 'html.parser')
        self.date = datetime.date.fromisoformat(date)
        self.daily_flight_list = []
        self.chars_to_strip = '\n n$\\'

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
            price = flight_data.find(name="span", class_="price-text").string
            price = price.strip(self.chars_to_strip)
            
            #Southwest flight prices not included
            if airline == "Southwest":
                continue

            new_flight = Flight(departure_date=self.date, airline=airline,start_dt=start_dt, end_dt=end_dt,
                                departure_ICAO=departure_ICAO, arrival_ICAO=arrival_ICAO, duration=duration,
                                price=price,layovers=layovers)

            print(new_flight)
            self.daily_flight_list.append(new_flight)

            flight_data = flight_data.find_next(name="div", class_="resultInner")

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

        #Parse Airline
        airline = div_section_time.find(name='div', class_='bottom').string
        airline = airline.strip(self.chars_to_strip).split(' ')
        airline = airline[0]

        return start_dt, end_dt, airline


    def __pull_time(self, time_pair):

        time_string = time_pair.find(name='span', class_='base-time').string
        hour, minute = time_string.strip(self.chars_to_strip).split(':')
        meridium = time_pair.find_next(name = 'span', class_='time-meridiem meridiem').string
        
        hour = int(hour)
        minute = int(minute)
        if meridium == "pm" and hour < 12:
            hour += 12

        time = datetime.time(hour, minute)

        return time


    def __extract_flight_section_duration(self, div_section_duration):

        #Parse Duration
        duration_data = div_section_duration.find(name='div', class_='top')
        duration_text = duration_data.string.strip(self.chars_to_strip)

        bottom = duration_data.find_next(name='div', class_='bottom')
        #Parse Departure ICAO
        departure_data = bottom.find(name = 'span', class_='airport-name')
        departure_ICAO = departure_data.string
        departure_ICAO = departure_ICAO.strip(self.chars_to_strip)

        #Parse Arrival ICAO
        arrival_data = departure_data.find_next(name = 'span', class_='airport-name')
        arrival_ICAO = arrival_data.string.strip(self.chars_to_strip)

        return duration_text, departure_ICAO, arrival_ICAO

    def __extract_flight_section_stops(self, div_section_stops):

        ICAOs = []
        #Pull connection ICAOs
        ICAO = div_section_stops.find(name='span', class_='js-layover')

        while ICAO:
            ICAOs.append(ICAO.string)
            ICAO = ICAO.find(name='span', class_='js-layover')

        return ICAOs



class SouthwestFlightParser:


    def __init__(self, date, departure_ICAO, arrival_ICAO, page_source):
        self.soup = BS(page_source, 'html.parser')
        self.date = datetime.date.fromisoformat(date)
        self.departure_ICAO = departure_ICAO
        self.arrival_ICAO = arrival_ICAO
        self.daily_flight_list = []
        self.chars_to_strip = '\n n$\\ \"'

    def get_flight_offers(self):

        flight_data = self.soup.find(name="li", class_="air-booking-select-detail")
        airline = "Southwest"
        # print(flight_data)
        while flight_data:
            #Parse start, end
            div_section_time = flight_data.find(name="div", class_="time--value")
            start_dt  = self.__extract_flight_section_times(div_section_time)
            div_section_time = div_section_time.find_next(name="div", class_="time--value")
            end_dt = self.__extract_flight_section_times(div_section_time)

            #Parse layovers
            div_number_of_stops = flight_data.find(name="div", class_="select-detail--number-of-stops")
            layovers = self.__extract_flight_section_stops(div_number_of_stops)

            #Parse total time
            div_flight_duration = flight_data.find(name="div", class_="select-detail--flight-duration")
            duration = div_flight_duration.string

            #Parse Price
            price = flight_data.find(name="div", class_="select-detail--fares")
            price = self.__extract__div_fares(price)

            if price > 0:

                new_flight = Flight(departure_date=self.date, airline=airline, start_dt=start_dt, end_dt=end_dt,
                                    departure_ICAO=self.departure_ICAO, arrival_ICAO=self.arrival_ICAO, duration=duration,
                                    price=price, layovers=layovers)

                print(new_flight)
                self.daily_flight_list.append(new_flight)

            flight_data = flight_data.find_next(name="li", class_="air-booking-select-detail")

        return self.daily_flight_list

        
    def __extract_flight_section_times(self, div_section_time):
        '''<span class="time--value">
                <span class="swa-g-screen-reader-only">Departs </span>
                    "6:35"
                <span class="time--period">AM</span>
            </span>'''

        #Parse Departure Date/time
        departure_time = self.__pull_time(div_section_time)
        start_dt = datetime.datetime.combine(self.date, departure_time)

        return date_time_pair


    def __pull_time(self, time_pair):
        '''<span class="time--value">
                <span class="swa-g-screen-reader-only">Departs </span>
                    "6:35"
                <span class="time--period">AM</span>
            </span>'''

        time_data = time_pair.string
        time_string = time_data.split(':')
            # ['... \span> "6'  ,  '35" <span...']
        time_string = time_string[0][-2:] + ':' + time_string[1][0:2]
            # '"6:35"' or '12:35"'
        hour, minute = time_string.strip(self.chars_to_strip).split(':')
        meridium = time_pair.find_next(name = 'span', class_='time--period').string
        
        hour = int(hour)
        minute = int(minute)
        if meridium == "PM" and hour < 12:
            hour += 12

        time = datetime.time(hour, minute)

        return time


    # def __extract_flight_section_duration(self, div_section_duration):

    #     #Parse Duration
    #     duration_data = div_section_duration.find(name='div', class_='top')
    #     duration_text = duration_data.string.strip(self.chars_to_strip)

    #     bottom = duration_data.find_next(name='div', class_='bottom')
    #     #Parse Departure ICAO
    #     departure_data = bottom.find(name = 'span', class_='airport-name')
    #     departure_ICAO = departure_data.string
    #     departure_ICAO = departure_ICAO.strip(self.chars_to_strip)

    #     #Parse Arrival ICAO
    #     arrival_data = departure_data.find_next(name = 'span', class_='airport-name')
    #     arrival_ICAO = arrival_data.string.strip(self.chars_to_strip)

    #     return duration_text

    def __extract_flight_section_stops(self, div_number_of_stops):
        ''' <div class="select-detail--number-of-stops">
                <div class="flyout-trigger">
                    <button aria-expanded="false" class="actionable actionable_button actionable_light button" type="button" data-a="select-detail-flyout" fdprocessedid="9vc7q">
                        <span class="actionable--text">
                            <div class="flight-stops-badge select-detail--flight-stops-badge">
                                1 stop
                            </div>
                        </span>
                        <span class="swa-g-screen-reader-only">&nbsp;Opens flyout.</span>
                    </button>
                </div>
                <div class="select-detail--change-planes">
                    "Change planes" "HOU"
                </div>
            </div>'''
        number_of_stops = div_number_of_stops.find(name="div", class_="flight-stops-badge select-detail--flight-stops-badge")
        number_of_stops = number_of_stops.string[0:2].strip(self.chars_to_strip)
        
        ICAOs = []
        #Pull connection ICAOs
        ICAO = number_of_stops.find_next(name='div', class_='select-detail--change-planes').string
        ICAO = ICAO.replace("Change planes", '').strip(self.chars_to_strip)
        ICAOs.append(ICAO)

        for i in range(int(number_of_stops)):
            ICAOs.append('???') # Only the first layover is easily displayed on the Southwest site...

        return ICAOs

    def __extract__div_fares(self, price):
        '''<div class="select-detail--fares" id="air-booking-fares-0-3">
                <div data-test="fare-button--business-select" class="fare-button fare-button_fare-type-color select-detail--fare">
                    <button class="actionable actionable_button fare-button--button" aria-label="Business Select fare $470, earn 4854 poi... " fdprocessedid="9vy6xe">
                        <span class="actionable--text">
                            <span class="fare-button--text">
                                <span class="fare-button--value">
                                    <span class="currency currency_dollars">
                                        <span class="swa-g-screen-reader-only">470 Dollars</span>
                                        <span aria-hidden="true">
                                            <span class="currency--symbol">$</span>
                                            <span>
                                                470
                                            </span></span></span></span>
                                <span class=""></span></span></span></button></div>
                <div data-test="fare-button--anytime" class="fare-button fare-button_fare-type-color select-detail--fare">
                    <button class="actionable actionable_button fare-button--button" aria-label="Anytime fare $420, earn 3580 poi..." fdprocessedid="arrb7o">
                        <span class="actionable--text">
                            <span class="fare-button--text">
                                <span class="fare-button--value">
                                    Unavailable
                                </span>
                            </span></span></button></div>
                <div data-test="fare-button--wanna-get-away-plus"... '''
        
        prices = []

        fare = price.find(name="span", class_="fare-button--text")
        for i in range(3):
            if fare.string.find("Unavailable"):
                pass
            else:
                price = fare.find(name="span", class_="swa-g-screen-reader-only").string
                price = price.replace(" Dollars", '')
                price = int(price)
                prices.append(price)
            fare = fare.find_next(name="span", class_="fare-button--text")

        if len(prices) == 0:
            price = 0
        else:
            price = min(prices)
        
        return price