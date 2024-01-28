import requests
from bs4 import BeautifulSoup
import time
import csv
import logging

# Configure logging
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_file = 'scraper.log'

file_handler = logging.FileHandler(log_file, mode='w')
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

# Constants
NOMINATIM_API_URL = "https://nominatim.openstreetmap.org/search"
SLEEP_INTERVAL = 0.1  # seconds

# Function to scrape event details
def scrape_event_details(url):
    time.sleep(SLEEP_INTERVAL)  # Sleep before making a request
    res = requests.get(url)
    if res.status_code == 200:
        soup = BeautifulSoup(res.text, 'html.parser')
        name = soup.select_one('div.medium-6.columns.event-top > h1').get_text(strip=True)
        date = soup.select_one('div.medium-6.columns.event-top > h4 > span:nth-child(1)').get_text(strip=True)
        location = soup.select_one('div.medium-6.columns.event-top > h4 > span:nth-child(2)').get_text(strip=True)
        event_type = soup.select_one('div.medium-6.columns.event-top > a:nth-child(3)').get_text(strip=True)
        region = soup.select_one('div.medium-6.columns.event-top > a:nth-child(4)').get_text(strip=True)
        logger.info(f"Scraped event details from {url}")
        return [name, date, location, event_type, region]

    else:
        logger.error(f"Failed to retrieve data from {url}")
        return ['N/A', 'N/A', 'N/A', 'N/A', 'N/A']

# Function to get location coordinates
def get_location_coordinates(location_name, location_cache):
    if location_name in location_cache:
        return location_cache[location_name]
    params = {"q": location_name, "format": "jsonv2"}
    time.sleep(SLEEP_INTERVAL)
    res = requests.get(NOMINATIM_API_URL, params=params)
    if res.status_code == 200:
        data = res.json()
        if data:
            location_cache[location_name] = (data[0]['lat'], data[0]['lon'])
            logger.info(f"Retrieved coordinates for {location_name}")
            return data[0]['lat'], data[0]['lon']
        else:
            location_cache[location_name] = ('Not Found', 'Not Found')
            return 'Not Found', 'Not Found'
    else:
        location_cache[location_name] = ('Not Found', 'Not Found')
        return 'Not Found', 'Not Found'

# Function to get weather data using the grid point
def get_weather_for_location(lat, lon, weather_cache):
    cache_key = f"{lat},{lon}"
    if cache_key in weather_cache:
        return weather_cache[cache_key]
    time.sleep(SLEEP_INTERVAL)
    gridpoint_url = f"https://api.weather.gov/points/{lat},{lon}"
    res = requests.get(gridpoint_url)
    if res.status_code == 200:
        data = res.json()
        grid_id = data['properties']['gridId']
        grid_x = data['properties']['gridX']
        grid_y = data['properties']['gridY']
        forecast_url = f"https://api.weather.gov/gridpoints/{grid_id}/{grid_x},{grid_y}/forecast"
        res = requests.get(forecast_url)
        if res.status_code == 200:
            forecast_data = res.json()
            for period in forecast_data['properties']['periods']:
                if period['isDaytime']:
                    daytime_forecast = period['shortForecast']
                    weather_cache[cache_key] = daytime_forecast
                    logger.info(f"Retrieved weather for coordinates {lat}, {lon}")
                    return daytime_forecast
            return 'Daytime weather not found'
        else:
            return 'Forecast data not found'
    else:
        return 'Gridpoint not found'

# Main scraping and processing logic
def main():
    logger.info("Starting to scrape event data")
    data = []
    for page in range(1, 41):
        url = f"http://visitseattle.org/events/?page={page}"
        res = requests.get(url)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            event_links = soup.select('div > div.container-event > h4 > a')
            for event_link in event_links:
                event_url = event_link['href']
                event_details = scrape_event_details(event_url)
                data.append(event_details)
    # Writing data to CSV
    with open('events.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Date', 'Location', 'Type', 'Region'])
        writer.writerows(data)
    logger.info("Data written to events.csv")
    print("Scraper has finished execution.")  # Add this line

    # Processing location coordinates and weather information
    location_cache = {}
    weather_cache = {}
    data_with_coords_weather = []

    with open('events.csv', mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = list(reader)

    for row in data:
        lat, lon = get_location_coordinates(row['Location'], location_cache)
        weather = get_weather_for_location(lat, lon, weather_cache)
        row['Latitude'] = lat
        row['Longitude'] = lon
        row['Weather'] = weather
        data_with_coords_weather.append(row)

    # Writing data with coordinates and weather to a new CSV
    with open('events_fullinfo.csv', 'w', newline='', encoding='utf-8') as file:
        fieldnames = reader.fieldnames + ['Latitude', 'Longitude', 'Weather']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data_with_coords_weather)
    logger.info("Data with coordinates and weather written to events_fullinfo.csv")

if __name__ == "__main__":
    main()