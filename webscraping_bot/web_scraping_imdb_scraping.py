"""
Creating a web scraping bot that scrapes data from IMDB movies site.
"""
import numpy as np
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup


# CLASS ASSESSMENT


# define functions
def scrape_info(parser, page_to_scrape_tag, page_to_scrape_class, tag_get_no_pages, class_get_no_pages) -> pd.DataFrame:
    """
    Scrapes information from IMDB movies site.

    Parameters
    ----------
    parser : str
        The parser to be used by BeautifulSoup.
    page_to_scrape_tag : str
        The HTML tag to be searched for on the page containing movie details.
    page_to_scrape_class : str
        The class attribute of the tag to be searched for on the page containing movie details.
    tag_get_no_pages : str
        The HTML tag to be searched for on the page containing the number of pages.
    class_get_no_pages : str
        The class attribute of the tag to be searched for on the page containing the number of pages.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing movie information.
    """
    dataset = pd.DataFrame(columns = ["title", "release_year", "runtime", "genre", "certificate", "rating", "director", "stars", "votes", "gross"])
    url = "https://www.imdb.com/list/ls006266261/?st_dt=&mode=detail&page=1&sort=list_order,asc"
    pages = number_of_pages(
        url = url, 
        parser = parser, 
        tag = tag_get_no_pages,
        class_ = class_get_no_pages)
    
    for number in range(1, (pages + 1)):
        get_url = f"https://www.imdb.com/list/ls006266261/?st_dt=&mode=detail&page={number}&sort=list_order,asc"
        soup, info = get_pages(
            url = get_url, 
            parser = parser, 
            tag = page_to_scrape_tag,
            class_ = page_to_scrape_class)
        
        movies_info = []
        store = []
        for each in info:
            if each.find("h3", class_ ="lister-item-header").find("a") != None:
                title = each.find("h3", class_ ="lister-item-header").find("a").text
                store.append(title)
            else:
                store.append(np.nan)
            if each.find("h3", class_ ="lister-item-header").find("span", class_ ="lister-item-year text-muted unbold") != None:
                release_year = each.find("h3", class_ ="lister-item-header").find("span", class_ ="lister-item-year text-muted unbold").text.replace("(", "").replace(")", "")
                store.append(release_year)
            else:
                store.append(np.nan)
            if each.find("span", class_ = "runtime") != None:
                runtime = each.find("span", class_ = "runtime").text.replace("min", "").strip()
                store.append(runtime)
            else:
                store.append(np.nan)
            if each.find("span", class_ = "genre") != None:
                genre = each.find("span", class_ = "genre").text.strip()
                store.append(genre)
            else:
                store.append(np.nan)
            if each.find("span", class_ = "certificate") != None:
                certificate = each.find("span", class_ = "certificate").text
                store.append(certificate)
            else:
                store.append(np.nan)
            if each.find("span", class_ = "ipl-rating-star__rating") != None:
                rating = each.find("span", class_ = "ipl-rating-star__rating").text
                store.append(rating)
            else:
                store.append(np.nan)
            
            try:
                details_director = each.find_all("p", class_ = "text-muted text-small")[1]
                details_director = details_director.text.replace("Director:", "").replace("Directors:", "").replace("Stars:", "").strip().split("|")[0]
            except:
                details_director = np.nan
            
            try:
                details_stars = each.find_all("p", class_ = "text-muted text-small")[1]
                details_stars = details_stars.text.replace("Director:", "").replace("Directors:", "").replace("Stars:", "").strip().split("|")[1]
                details_stars = details_stars.strip()
            except:
                details_stars = np.nan
            
            try:
                details_votes = each.find_all("p", class_ = "text-muted text-small")[2]
                details_votes = details_votes.text.replace("Votes:", "").replace("Gross:", "").strip().split("|")[0]
                details_votes = details_votes.strip().replace(",", "")
            except:
                details_votes = np.nan
            
            try:
                details_gross = each.find_all("p", class_ = "text-muted text-small")[2]
                details_gross = details_gross.text.replace("Votes:", "").replace("Gross:", "").replace("$", "").replace("M", "").strip().split("|")[1]
                details_gross = details_gross.strip().replace(",", "")
            except:
                details_gross = np.nan
            
            store.extend([details_director, details_stars, details_votes, details_gross])
          
            movies_info.append(store)
            store = []
            
        data = pd.DataFrame(movies_info, columns = ["title", "release_year", "runtime", "genre", "certificate", "rating", "director", "stars", "votes", "gross"])
        dataset = pd.concat([dataset, data]) 
    
    return dataset

def get_pages(url, parser, tag, class_ = None) -> tuple:
    """
    Retrieves the HTML content of a page and extracts specific information.

    Parameters
    ----------
    url : str
        The URL of the page to scrape.
    parser : str
        The parser to be used by BeautifulSoup.
    tag : str
        The HTML tag to be searched for.
    class_ : str, optional
        The class attribute of the tag to be searched for, if any. The default is None.

    Returns
    -------
    tuple
        A tuple containing the BeautifulSoup object representing the parsed HTML and the specific information extracted.
    """
    scraper = requests.get(url)
    response = scraper.text

    soup = BeautifulSoup(response, parser)
    info = soup.find_all(tag, class_ = class_)
    return (soup, info)

def number_of_pages(url, parser, tag, class_ = None) -> int:
    """
    Retrieves the number of pages from the given URL.

    Parameters
    ----------
    url : str
        The URL of the page to scrape.
    parser : str
        The parser to be used by BeautifulSoup.
    tag : str
        The HTML tag to be searched for.
    class_ : str, optional
        The class attribute of the tag to be searched for, if any. The default is None.

    Returns
    -------
    int
        The number of pages found on the webpage.
    """
    scraper = requests.get(url)
    response = scraper.text

    soup = BeautifulSoup(response, parser)
    pages = int(soup.find(tag, class_ = class_).text.replace(",", "").split()[-1])
    return pages

if __name__ == "__main__":
    dataframe = scrape_info(parser = "html.parser", 
                            page_to_scrape_tag = "div", 
                            page_to_scrape_class = "lister-item-content", 
                            tag_get_no_pages = "span", 
                            class_get_no_pages = "pagination-range")
    save_time = time.ctime().replace(" ", "_")
    data_to_save_name = "dataset_" + save_time
    dataframe.to_csv(f"scraped_data/{data_to_save_name}.csv", index = False)
    print("Next scraping will occur in 2hrs... \nThis bot is created by TechLeo")
    time.sleep(3600)
    