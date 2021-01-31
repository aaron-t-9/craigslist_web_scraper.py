"""
Craigslist Web Scraper

Aaron T.
December 14, 2020.
"""

import datetime
import requests
import statistics as stats
from bs4 import BeautifulSoup as Soup


def MAX_LISTINGS_PER_PAGE():
    """A constant. The maximum number of listings of a given Craigslist search result.

    :return: An integer.
    """
    return 120


class CraigslistWebScraper:
    def __init__(self, city, raw_search_query):
        self.city = city
        self.raw_search_query = raw_search_query

        self.url, self.search_query = self.get_url()
        self.html_soup = self.fetch_html_soup(self.url)
        self.list_elements_soup = self.get_html_list_elements(self.html_soup)

        self.filename = self.get_CSV_filename()
        self.csv_headers = self.get_CSV_headers()

    def get_url(self):
        """
        Gets the user's specified city and their search query. Returns a URL containing the user
        specified city and search query.

        :return: A tuple. The tuple contains strings, the craigslist URL containing the user
                specified city and search query, as well as their search query.
        """
        search_query = self.raw_search_query.replace(" ", "+")
        self.city = self.city.strip()
        url = "https://" + self.city + ".craigslist.org/d/for-sale/search/sss?query=" + search_query + "&sort=rel"

        return url, search_query

    def get_incremented_url(self, current_increment: int) -> str:
        """
        Gets the user's specified city and their search query. Returns a URL containing the user
        specified city and search query, along with the number of the increment representing the
        current page of results.

        :return: A string. The set contains the craigslist URL containing the user specified city
                 and search query, their search query, and current page of results.
        """
        search_query = self.raw_search_query.replace(" ", "+")
        self.city = self.city.strip()
        url_with_increment = "https://" + self.city + ".craigslist.org/d/for-sale/search/sss?s=" + str(
            current_increment) + "&query=" + search_query + "&sort=rel"

        return url_with_increment

    @staticmethod
    def fetch_html_soup(url: str):
        """
        Makes the call to the craigslist server and gets the HTML code for the page for the provided
        URL. Returns a Soup class element of the provided HTML code. Uses the Soup function from
        the BeautifulSoup4 (BS4) module.

        :param url: A string. The craigslist URL containing the user specified city and search query.
        :return: A Soup class. Contains the HTML elements, is the output of the Soup function from BS4.
        """
        proxy = {'http': '192.109.165.108'}
        craigslist_html = requests.get(url, proxies=proxy).text
        html_soup = Soup(craigslist_html, "html.parser")

        return html_soup

    def get_html_list_elements(self, html_soup):
        """
        Returns a list containing all of the list HTML elements from the provided Craigslist URL. If
        there are more than one page of listings, then the other pages of the listings are fetched
        and returned.

        :param html_soup: The output from the "Soup" function from the BS4 module. Contains the HTML
                          code of the provided Craigslist URL.
        :return: A list. Contains a list of all of the list HTML elements of the specified
                 Craigslist search.
        """
        list_elements_soup = html_soup.find_all("li", {"class": "result-row"})
        total_listings = int(''.join(self.html_soup.find('span', {'class': 'total'})))

        # Checks if there is more than a single page of results
        if total_listings > MAX_LISTINGS_PER_PAGE():
            required_repetitions = total_listings // MAX_LISTINGS_PER_PAGE()  # Number of pages of results

            # Loops through all of the pages, gets a list of their list HTML elements, appends these lists together
            for page in range(1, required_repetitions + 1):
                current_increment = page * MAX_LISTINGS_PER_PAGE()
                url_with_increment = self.get_incremented_url(current_increment)
                html_soup_with_increment = self.fetch_html_soup(url_with_increment)
                incremented_soup_list_elements = html_soup_with_increment.find_all("li", {
                    "class": "result-row"})
                list_elements_soup += incremented_soup_list_elements  # Appends the pages of results together

            return list_elements_soup

        else:
            return list_elements_soup

    def get_CSV_filename(self):
        """
        Creates the name for the CSV file, which consists of the current date and the user's search
        query.

        :return: A string. The name of the CSV file.
        """
        # Grabs date and creates file name with the date
        date = str(datetime.date.today())
        filename = f"{date}_{self.search_query}.csv"

        return filename

    @staticmethod
    def get_CSV_headers():
        """
        Creates the headings for the CSV file.

        :return: A string.
        """
        csv_headers = "Number, Date, Listing_Name, Price, URL\n"

        return csv_headers

    def write_CSV(self):
        """
        Gets the number, date, name, price, and URL for all of the listings and writes
        this information to a spreadsheet file. The average and median prices of the listings are
        also included in the spreadsheet.

        :return: Nothing is returned.
        """
        list_of_prices = []
        total_listings = len(self.list_elements_soup)

        f = open(self.filename, "w", encoding='utf-8')
        f.write(f'TOTAL LISTINGS: {total_listings}\n\n{self.csv_headers}')

        # Main loop for pulling attribute values and writing the CSV file
        listing_number = 1
        for container in self.list_elements_soup:
            # Gets the specified attributes to be written to the CSV file
            listing_date = ''.join(container.time['datetime'].split(' ')[0]).replace(',', '|')
            listing_name = ''.join(container.find('a', {'class': 'result-title hdrlnk'})).replace(
                ',',
                '|')
            listing_price = ''.join(container.find('span', {'class': 'result-price'})).replace(',',
                                                                                               '')
            listing_url = container.a['href']

            f.write(
                f'{listing_number}, {listing_date}, {listing_name}, {listing_price}, {listing_url}\n')
            listing_number += 1

            # List of all of the listing prices
            list_of_prices.append(int(listing_price.replace("$", "")))

        mean_price = round(stats.mean(list_of_prices), 2)
        median_price = stats.median(list_of_prices)

        f.write(f'\nAverage price: {mean_price}\n')
        f.write(f'Median price: {median_price}\n')

        f.close()

        print("File successfully written.")


def driver():
    """
    Handles the user input and runs the program. Nothing is returned. Writes a CSV file containing
    the listings of the user's search query within the specified city.

    :return: Nothing is returned. A CSV file containing the user specified listings within the user
             specified city is written.
    """
    try:
        city = input("Please enter the desired city: ").lower().strip()
        raw_search_query = input("Enter your search query: ").lower().strip()

        instance = CraigslistWebScraper(city, raw_search_query)
        instance.write_CSV()
    except:
        print("Something is broken!")


def main():
    """Executes the program."""
    driver()


if __name__ == '__main__':
    main()
