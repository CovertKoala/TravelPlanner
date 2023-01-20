from time import sleep
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import numpy as np
from tqdm import tqdm


# path to chromedriver
chromedriver_path =  "C:/Users/Meshal/Desktop/web-scraping/chromedriver.exe"


# launching the driver
driver = webdriver.Chrome(chromedriver_path)


# get user input for routes
sources = []
destinations = []
print("Please enter -1 when done.")
print("-"*10)
while True:
    sources.append(input("From which city?\n"))
    if "-1" in sources: 
        sources.pop(-1)
        break
    destinations.append(input("Where to?\n"))
    if "-1" in destinations: 
        sources.pop(-1)
        destinations.pop(-1)
        break
    print("-"*10)

print("\nRoutes:")
for i in range(len(sources)):
    print(f"{sources[i]} => {destinations[i]}")


# get user input for period (start and end date)
start_date = np.datetime64(input('Start Date, Please use YYYY-MM-DD format only '))
end_date = np.datetime64(input('End Date, Please use YYYY-MM-DD format only '))
days = end_date - start_date
num_days = days.item().days

def get_airlines(soup):
    airline = []
    airlines = soup.find_all('span',class_='codeshares-airline-names',text=True)
    for i in airlines:
        airline.append(i.text)
    return airline
    
def get_total_stops(soup):
    stops_list = []
    stops = soup.find_all('div',class_='section stops')

    for i in stops:
        for j in i.find_all('span',class_='stops-text'):
               stops_list.append(j.text)
    return stops_list

def get_price(soup):
    prices = []
    price = soup.find_all('div',class_='Flights-Results-FlightPriceSection right-alignment sleek')

    for i in price:
        for j in i.find_all('span', class_='price-text'):
            prices.append(j.text)
    return prices

def get_duration(soup):
    duration_list = []
    duration = soup.find_all('div' , class_='section duration allow-multi-modal-icons')
    for i in duration:
        for j in i.find_all('div',class_='top'):
            duration_list.append(j.text)
    return duration_list


for i in range(len(sources)):
    column_names = ["Airline", "Source", "Destination","Duration" ,"Total stops", "Price","Date"]
    df = pd.DataFrame(columns = column_names)
    for j in tqdm(range(num_days+1)):
        
        # close and open driver every 10 days to avoid captcha
        if j % 10 == 0:
            driver.quit()
            driver = webdriver.Chrome(chromedriver_path)#, chrome_options=chromeOptions)
            
        url = f"https://www.en.kayak.sa/flights/{sources[i]}-{destinations[i]}/{start_date+j}"
        driver.get(url)
        sleep(15)
        
        # click show more button to get all flights
        try:
            show_more_button = driver.find_element_by_xpath('//a[@class = "moreButton"]')
        except:
            
            # in case a captcha appears, require input from user so that the for loop pauses and the user can continue the
            # loop after solving the captcha
            input("Please solve the captcha then enter anything here to resume scraping.")
            
        while True:
            try:
                show_more_button.click()
                driver.implicitly_wait(10)
            except:
                break
    
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        airlines = get_airlines(soup)
        total_stops = get_total_stops(soup)
        prices = get_price(soup)
        duration = get_duration(soup)
        df = df.append(pd.DataFrame({
            'Airline': airlines,
            'Duration': duration,
            'Total stops' : total_stops,
            'Price' : prices,
            'Date' : start_date+j
                                    }))
        
    df['Source'] = sources[i]
    df['Destination'] = destinations[i]
    df = df.replace('\n','', regex=True)
    df = df.reset_index(drop = True)
    
    # save data as csv file for each route
    df.to_csv(f'{sources[i]}_{destinations[i]}.csv',index=False)
    print(f"Succesfully saved {sources[i]} => {destinations[i]} route as {sources[i]}_{destinations[i]}.csv ")
    
driver.quit()