from playwright.sync_api import sync_playwright
import pandas as pd


def main():
    with sync_playwright() as p:
        # inputs for wanderu.com
        departure_city = 'Cleveland, OH'
        arrival_city = 'Chicago, IL'
        departure_date = '2025-01-16'
        
        # page url w/inputs
        page_url = f'https://www.wanderu.com/en-us/depart/{departure_city}/{arrival_city}/{departure_date}/?cur=USD'

        # launching browser
        browser = p.chromium.launch(headless=False)  
        page = browser.new_page()
        
        # navigating, load waiting time
        print("Navigating to page...")
        page.goto(page_url, timeout=60000) 
        print("Page loaded successfully.")

        # wait for see more button to ensure all trips scraped
        see_more_button = 'button:has-text("See more")'
        
        # visibility for see more
        page.locator(see_more_button).wait_for(state="visible", timeout=6000)
        print("Found 'See more' button.")

        # click see more until no longer available on page
        while True:
            see_more_locator = page.locator(see_more_button)
            if see_more_locator.is_visible():
                print("Clicking 'See more' button...")
                see_more_locator.click()
                page.wait_for_timeout(5000)  
            else:
                print("No more 'See more' buttons found.")
                break

        # all bus trip elements
        bus_trips = page.locator('div[data-id="Select-mobile"]').all()
        print(f'There are: {len(bus_trips)} bus trips.')

        # list to store sscraped information
        bus_list = []

        # iteraring over each trip, adding to dictionary
        for bus in bus_trips:
            bus_dict = {}

            # price
            bus_dict['price'] = bus.locator('span[aria-label="Price"]').inner_text(timeout=3000)

            # dep time
            bus_dict['departure_time'] = bus.locator('div[aria-label="depart"]').inner_text(timeout=3000)

            # arr time
            bus_dict['arrival_time'] = bus.locator('div[aria-label="arrive"]').inner_text(timeout=3000)

            # duration
            bus_dict['duration'] = bus.locator('span[aria-label="Duration"]').inner_text(timeout=3000)

            # carrier.. if availble? this is a little funky
            carrier_locator = bus.locator('div._2nswdy5H41iJ')
            if carrier_locator.count() > 0:  
                try:
                    
                    if carrier_locator.is_visible():
                        bus_dict['carrier'] = carrier_locator.inner_text(timeout=5000)
                    else:
                        bus_dict['carrier'] = 'N/A'  
                except Exception as e:
                    bus_dict['carrier'] = 'N/A' 
            else:
                bus_dict['carrier'] = 'N/A' 

            # rating scraper
            try:
                rating_locator = bus.locator('span._67xXmWzVqs2e')
                if rating_locator.is_visible():
                    bus_dict['rating'] = rating_locator.inner_text(timeout=3000) 
                else:
                    bus_dict['rating'] = 'N/A'
            except Exception as e:
                print(f"Error scraping rating: {e}")
                bus_dict['rating'] = 'N/A'
            
            # Store the dictionary in the list
            bus_list.append(bus_dict)
        
        # create df from our list of dictionaries
        df = pd.DataFrame(bus_list)
        
        # saving df
        df.to_excel('bus_trips_list.xlsx', index=False)
        df.to_csv('bus_trips_list.csv', index=False)
        
        # close chromium browser
        browser.close()


if __name__ == '__main__':
    main()
