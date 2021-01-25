"""
Craigslist Web Scraper

Aaron T.
December 14, 2020.
"""

import datetime
import requests
import statistics as stats
from bs4 import BeautifulSoup as Soup


def getURL() -> tuple:
    """
    Gets the user's specified city and their search query. Returns a URL containing the user
    specified city and search query.

    :return: A tuple. The set contains the craigslist URL containing the user specified city and
             search query, as well as their search query.
    """
    city = input("Please enter your city: ")
    raw_search_query = input("Please enter your search query: ")

    search_query = raw_search_query.replace(" ", "+")
    url = "https://" + city + ".craigslist.org/d/for-sale/search/sss?query=" + search_query + "&sort=rel"

    return url, search_query


def get_html_elements(url: str) -> list:
    """
    Makes the call to the craigslist server and gets the HTML code for the page for the provided
    URL. Returns a list of all of the list HTML elements that makes up each Craigslist listing.

    :param url: A string. The craigslist URL containing the user specified city and search query.
    :return: A list. Contains a list of the list HTML elements.
    """
    proxy = {'http': '192.109.165.108'}
    cl_html = requests.get(url, proxies=proxy).text
    clsoup = Soup(cl_html, 'html.parser')
    clsoup_list = clsoup.find_all('li', {'class': 'result-row'})

    return clsoup_list


def write_CSV(clsoup_list: list, user_search_query: str):
    """
    Gets the number, date, name, price, and URL for all of the listings and writes
    this information to a spreadsheet file. The average and median prices of the listings are
    also included in the spreadsheet.

    :param clsoup_list: A list containing the list HTML elements.
    :param user_search_query: A string containing the user's search query.
    :return: Nothing is returned.
    """
    list_of_prices = []

    # Grabs date and creates file name with the date
    date = str(datetime.date.today())
    filename = f"{date}_{user_search_query}.csv"

    # Defines the headers in Excel, and writes the headers into the file
    csv_headers = "Number, Date, Listing_Name, Price, URL\n"

    # Adds total number of listings at very top of file, writes headers to the Excel file
    total_listings = len(clsoup_list)
    f = open(filename, "w", encoding='utf-8')
    f.write(f'TOTAL LISTINGS: {total_listings}\n\n{csv_headers}')

    # Main loop for pulling attribute values and writing the csv file
    number = 1
    for container in clsoup_list:
        listing_date = ''.join(container.time['datetime'].split(' ')[0]).replace(',', '|')
        listing_name = ''.join(container.find('a', {'class': 'result-title hdrlnk'})).replace(',',
                                                                                              '|')
        listing_price = ''.join(container.find('span', {'class': 'result-price'})).replace(',', '')
        listing_url = container.a['href']

        f.write(f'{number}, {listing_date}, {listing_name}, {listing_price}, {listing_url}\n')
        number += 1

        # List of all of the listing prices
        list_of_prices.append(int(listing_price.replace("$", "")))

    mean_price = round(stats.mean(list_of_prices), 2)
    median_price = stats.median(list_of_prices)

    f.write(f'\nAverage price: {mean_price}\n')
    f.write(f'Median price: {median_price}\n')

    f.close()

    print("File successfully written!")


def main():
    """Executes the program."""

    url_search_query = getURL()
    url = url_search_query[0]
    user_search_query = url_search_query[1]

    clsoup_list = get_html_elements(url)
    write_CSV(clsoup_list, user_search_query)


if __name__ == '__main__':
    main()
