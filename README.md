# TECHIN5 10 lab2_Web Scrapers_Wanling

## Overview
This is the assignment about Accessing Web Resources with Python.
**What are Included:**
- Scrape the list page of Seattle events
- Scrape the Name, Date, Location, Type and Region of Seattle events
- Integrate the Latitude and Longitude info
- Integrate the Daytime Weather info
- Store the data as csv files

## How to run

## Lessons learned

## Future improvements
**My Modifications**  
To save time, I optimized the code to reduces API calls and speeds up the script.

The underlying logic is to simultaneously fill longitude, latitude, as well as weather information for one same locations (Since different activities are held in on same location frequently) in the CSV file, avoiding repetitive API data retrievals. 

To achieve this, the code utilizes two caches: `location_cache` for storing each location's latitude and longitude, and `weather_cache` for weather data of each latitude-longitude pair.

**Bonus:**  
There is a screenshot of Azure Storage in the repo.

events_fullinfo.csv and scraper.log is created by scraper.py to ensure that it can run smoothly.  
.github/workflows and corresponding actions.yml are created to achieve run the scraper.py periodically.

## Questions
