import numpy as np
from datetime import datetime, date, time
import json

class Flight():

    def __init__(self, departure_date:datetime= datetime(1,1,1), departure_ICAO:str = "XXX", arrival_ICAO:str="YYY", 
                 airline:str = "Airline", start_dt: datetime= datetime(1,1,1), end_dt: datetime = datetime(1,1,1),
                 price:int = 0, duration:str = "0h 0m", layovers:list = []):
        self.departure_date = departure_date
        self.departure_ICAO = departure_ICAO
        self.arrival_ICAO = arrival_ICAO
        self.airline = airline
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.price = price
        self.duration = duration
        self.layovers = layovers
        self.num_stops = len(self.layovers)

    def __str__(self):
        return f"{self.departure_date.strftime('%a %m/%d')} {self.start_dt.strftime('%H%M')}-{self.end_dt.strftime('%H%M')} {self.departure_ICAO}-{self.arrival_ICAO}: {self.airline:9} ${self.price:4}     ** total {self.duration}, thru {self.layovers}"

    # def to_JSON(self):
    #     flight_dictionary = self.__dict__
    #     flight_dictionary["departure_data"] = flight_dictionary["departure_date"].isoformat()
    #     flight_dictionary["start_dt"] = flight_dictionary["start_dt"].isoformat()
    #     flight_dictionary["end_dt"] = flight_dictionary["end_dt"].isoformat()
    #     return json.dumps

class FlightEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Flight):
            return obj.__dict__
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, time):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


class DayFlightTable:

    def __init__(self):
        self.travel_date = None
        self.flight_list = []

    def __init__(self, travel_date:datetime, flight_list:list):
        self.travel_date = travel_date
        self.flight_list = flight_list
        self.__build_table()

    def __build_table(self):
        #Create pd.DataFrame with all flight data
        pass

    def load_table(self, flight_list:list):
        self.flight_list = flight_list
        self.__build_table()
