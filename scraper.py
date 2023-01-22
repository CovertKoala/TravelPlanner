from time import sleep
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
import random


class FlightScraper:

    # path to EdgeDriver
    driver_path = "/Drivers/msedgedriver.exe"

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


    def scrape_flight_offer_page(self, date:str, departureAirport:str, arrivalAirport:str):
        
        trip_duration_hours = 10
        url = f"http://www.kayak.com/flights/{departureAirport}-{arrivalAirport}/{date}?sort=price_a&fs=legdur=-{trip_duration_hours * 60};cabin=-bfbe"
        self.driver.get(url)
        sleep(20)
        
        # click show more button to get alsl flights
        try:
            show_more_button = self.driver.find_element(By.CLASS_NAME, "moreButton")
            is_show_more_button = True
        except:
            print("All flights fit on one page.")
            is_show_more_button = False
            
        while is_show_more_button:
            try:
                show_more_button.click()
                random_pause = random.randint(5, 10)
                print(f"Loading more flights, then waiting {random_pause} sec.")
                sleep(random_pause)
            except:
                is_show_more_button = False
                print("All flights loaded.")

        return self.driver.page_source

