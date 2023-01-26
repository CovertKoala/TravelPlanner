from time import sleep
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import random
from datetime import date, timedelta
import tqdm

class FlightScraper:

    # path to EdgeDriver
    #driver_path = "Drivers/msedgedriver.exe"
    driver_path = "Drivers/chromedriver.exe"

    def __init__(self):
        self.__set_options()
        self.driver = self.__make_scraper()

    def __set_options(self):
        # set driver options
        #self.options = EdgeOptions()
        #self.options.add_argument("--disable-usb-keyboard-detect ")
        #self.options.add_argument("--disable-gpu ")
        # self.options.add_argument("--disable-angle-features ")
        # self.options.add_argument("--disable-gl-extensions ")
        # self.options.add_argument("--disable-logging ")
        # self.options.add_argument("--disable-hang-monitor ")
        # self.options.add_argument("--log-level=3 ")
        # self.options.add_argument("--noerrdialogs ")
        
        #Edge Specific
        #self.options.add_argument("--disable-extentions ")
        #self.options.add_experimental_option("excludeSwitches", ["enable-logging"])

        self.options = ChromeOptions()
        # self.options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.options.add_experimental_option("excludeSwitches", ['enable-automation'])
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
        self.options.add_argument("--remote-debugging-port=9222")

        return

    def __make_scraper(self):
        # Start web driver executable
        #driver = webdriver.Edge(executable_path=self.driver_path, options=self.options)
        driver = webdriver.Chrome(executable_path=self.driver_path)
        driver.implicitly_wait(25)
        driver.maximize_window()
        return driver

        
    def close_scraper(self):
        # Close web driver executable
        self.driver.quit()

    def __wait_bar(self, time):

        bar_format = "{elapsed}|{bar}|{remaining}"
        with tqdm.tqdm(total = time*10*10, bar_format=bar_format, leave=True, colour='green',position=0) as pbar:
            for i in range(time*10):
                sleep(0.1)
                pbar.update(10)

    def __load_url_to_driver(self, url, wait):
        self.driver.get(url)
        print("\nWaiting to ensure page load.")
        self.__wait_bar(wait) # Ensure page has initially loaded completely


    def __make_kayak_url(self, flight_options:dict):
        '''Use input 'flight_options' dict to scrape data.  Dict must have the following:
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
        trip_duration = "legdur=-720;"
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

        kayak_url = f"http://www.kayak.com/flights/{departure_ICAOs}-{arrival_ICAOs}/{travel_date}?sort=price_a&fs={landing}{takeoff}price=-1000;{trip_duration}cabin=-bfbe"
        print(kayak_url)
        return kayak_url


    def __make_southwest_url(self, flight_options:dict):
        '''Use input 'flight_options' dict to scrape data.  Dict must have the following:
            {
                'travel date': "YYYY-MM-DD",          <- single string date
                'travel times': "HHMM,HHMM"           <- Single string of "earliest,latest" times
                'departure ICAOs': "ICAO #1,ICAO#2",  <- string of three letter ICAOs
                'arrival ICAOs': "ICAO #1,ICAO#2"     <- string of three letter ICAOs
            }'''
        
        #https://www.southwest.com/air/booking/select.html?int=HOMEQBOMAIR&adultPassengersCount=1&departureDate=2023-01-25&destinationAirportCode=PNS&fareType=USD&originationAirportCode=BWI&passengerType=ADULT&returnDate=&tripType=oneway&from=&to=&adultsCount=1&departureTimeOfDay=ALL_DAY&reset=true&returnTimeOfDay=ALL_DAY
        
        
        departure_ICAO = flight_options['departure ICAOs']
        arrival_ICAO = flight_options['arrival ICAOs']
        travel_date = flight_options['travel date']
        
        #southwest_url = f'https://www.southwest.com/air/booking/select.html?int=HOMEQBOMAIR&adultPassengersCount=1&departureDate={travel_date}&destinationAirportCode={arrival_ICAO}&fareType=USD&originationAirportCode={departure_ICAO}&passengerType=ADULT&returnDate=&tripType=oneway&from=&to=&adultsCount=1&departureTimeOfDay=ALL_DAY&reset=true&returnTimeOfDay=ALL_DAY'
        southwest_url = f'https://www.southwest.com/air/booking/?clk=GSUBNAV-AIR-BOOK'
        print(southwest_url)
        return southwest_url



    def scrape_kayak_offer_page(self, flight_options:dict):
         
        print("Scraping Kayak.com")
        kayak_url = self.__make_kayak_url(flight_options)
        self.__load_url_to_driver(kayak_url, wait=20)
        
        # "click" show more button to get all flights
        try:
            show_more_button = self.driver.find_element(By.CLASS_NAME, "moreButton")
            print('Found "Show more results" button.')
            #Previous method above was more susceptible to Kayak.com code changes
            # show_more_button = driver.find_element(By.PARTIAL_LINK_TEXT, "Show more results")
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


    def scrape_southwest_offer_page(self, flight_options:dict):
         
        print("Sraping Southwest.com\n")
        southwest_url = self.__make_southwest_url(flight_options)
        self.__load_url_to_driver(southwest_url, wait = 5)
        
        tripType_radios = self.driver.find_elements(By.NAME, "tripType")
        tripType_radios[2].click()
        random_pause = random.randint(2, 5)
        sleep(random_pause)

        departure_ICAO_box = self.driver.find_element(By.ID, "originationAirportCode")
        departure_ICAO_box.click()
        departure_ICAO_box.send_keys(flight_options["departure ICAOs"] +'\t')
        random_pause = random.randint(2, 5)
        sleep(random_pause)

        date_box = self.driver.find_element(By.ID, "departureDate")
        travel_date = date.fromisoformat(flight_options["travel date"])
        month = travel_date.month
        day = travel_date.day
        date_input = str(month) + '/' + str(day) + '\t' + '\t' + '\t'
        date_box.send_keys(date_input)
        random_pause = random.randint(2, 6)
        sleep(random_pause)

        arrival_ICAO_box = self.driver.find_element(By.ID, "destinationAirportCode")
        #arrival_ICAO_box.click()
        arrival_ICAO_box.send_keys(flight_options["arrival ICAOs"])
        random_pause = random.randint(2, 5)
        sleep(random_pause)

        # action = ActionChains(self.driver)
        # search_button = self.driver.find_element(By.ID, "form-mixin--submit-button")
        # action.move_to_element(search_button)
        # action.click()
        # action.perform()
        
        # search_button.send_keys(' ')
        # random_pause = random.randint(2, 7)
        # sleep(random_pause)

        sleep(20)

        print("All flights loaded.")

        return self.driver.page_source
