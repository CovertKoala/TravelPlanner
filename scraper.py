from time import sleep
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
import random
from datetime import date, timedelta
import tqdm

class FlightScraper:

    # path to EdgeDriver
    driver_path = "Drivers/msedgedriver.exe"

    def __init__(self):
        self.__set_options()
        self.driver = self.__make_scraper()

    def __set_options(self):
        # set driver options
        self.options = EdgeOptions()
        #self.options.add_argument("--disable-usb-keyboard-detect ")
        #self.options.add_argument("--disable-gpu ")
        # self.options.add_argument("--disable-angle-features ")
        # self.options.add_argument("--disable-gl-extensions ")
        # self.options.add_argument("--disable-logging ")
        # self.options.add_argument("--disable-hang-monitor ")
        # self.options.add_argument("--log-level=3 ")
        # self.options.add_argument("--noerrdialogs ")
        self.options.add_argument("--disable-extentions ")
        self.options.add_experimental_option("excludeSwitches", ["enable-logging"])
        # print(options.arguments)


    def __make_scraper(self):
        # Start web driver executable
        driver = webdriver.Edge(executable_path=self.driver_path, options=self.options, verbose=False)
        driver.implicitly_wait(25)
        return driver

        
    def close_scraper(self):
        # Close web driver executable
        self.driver.quit()

    def __wait_bar(self, time):
        # widgets = [ 
        #             ' [', progressbar.Timer(format= 'elapsed time: %(elapsed)s'), '] ',
        #                   progressbar.Bar('-'),
        #             ' (', progressbar.ETA(), ') \n',
        #           ]
        # bar = progressbar.ProgressBar(initial_value=0, max_value=time*10-1, widgets=widgets).start()
        
        # widgets = ['Loading: ', progressbar.AnimatedMarker()]
        # bar = progressbar.ProgressBar(widgets=widgets).start()

        # for i in range(0,time*10-1):
        #     sleep(0.1)
        #     bar.update(i)
        
        # return ""

        bar_format = "{elapsed}|{bar}|{remaining}"
        with tqdm.tqdm(total = time*10*10, bar_format=bar_format, leave=True, colour='green',position=0) as pbar:
            for i in range(time*10):
                sleep(0.1)
                pbar.update(10)


    def scrape_flight_offer_page(self, flight_options:dict):
        '''Use input 'flight_options' dict to scrape data off of Kayak.  Dict must have the following:
            {
                'travel date': "YYYY-MM-DD",          <- single string date
                'travel times': "HHMM,HHMM"           <- Single string of "earliest,latest" times
                'departure ICAOs': "ICAO #1,ICAO#2",  <- string of three letter ICAOs
                'arrival ICAOs': "ICAO #1,ICAO#2"     <- string of three letter ICAOs
            }'''
        
        ### Build Kayak URL###
        # Pulled out "trip duration", because this is loosely implied by earliest/latest times.
        # Excluding "Basic Economy" tickets, since they can't be rescheduled.

        # example url:  https://www.kayak.com/flights/WAS,LGA-PNS,VPS/2023-02-03?sort=price_a&fs=landing=0930,0204@0200;takeoff=1630,2300;legdur=-600;cabin=-bfbe"
        # play url to ctl-click: https://www.kayak.com/flights/WAS-PNS/2023-02-03?sort=price_a&fs=landing=1630,0204@0200;takeoff=1630,2359;cabin=-bfbe"
        # trip_duration = "legdur=-600"
        departure_ICAOs = flight_options['departure ICAOs']
        arrival_ICAOs = flight_options['arrival ICAOs']
        travel_date = flight_options['travel date']
        if flight_options['travel times']:
            travel_times = flight_options['travel times']

            start, end = travel_times.split(',')
            # See if end time is the following morning
            if int(start) > int(end):
                # Add one to the day
                next_day = date.fromisoformat(travel_date) + timedelta(days=1)
                month_day_str = next_day.isoformat().replace('-','')[-4:]
                end = month_day_str + '@' + end

            landing = f"landing={start},{end};"
            takeoff = f"takeoff={start},2359;"
        else:
            landing = ""
            takeoff = ""

        url = f"http://www.kayak.com/flights/{departure_ICAOs}-{arrival_ICAOs}/{travel_date}?sort=price_a&fs={landing}{takeoff}cabin=-bfbe"
        
        self.driver.get(url)
        print("\nWaiting to ensure page load.")
        self.__wait_bar(20) # Ensure page has initially loaded completely
        
        # "click" show more button to get all flights
        try:
            show_more_button = self.driver.find_element(By.CLASS_NAME, "moreButton")
            is_show_more_button = True
        except:
            print("All flights fit on one page.")
            is_show_more_button = False
            
        while is_show_more_button:
            try:
                show_more_button.click()
                random_pause = random.randint(5, 10) # Adding random delay to clicks to prevent captchas
                print(f"Loading more flights, then waiting {random_pause} sec.")
                sleep(random_pause)
            except:
                is_show_more_button = False
                print("All flights loaded.")

        return self.driver.page_source

