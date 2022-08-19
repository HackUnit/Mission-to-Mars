
# Import Splinter, BeautifulSoup, and Pandas

import pandas as pd

import datetime as dt

from splinter import Browser

from bs4 import BeautifulSoup as soup

from webdriver_manager.chrome import ChromeDriverManager

#from selenium import webdriver

#from webbrowser import Chrome

manager = ChromeDriverManager()
manager.install()



# ## Scrape All
def scrape_all():

    executable_path = {'executable_path': ChromeDriverManager().install()}
    # Initiate headless driver for deployment
    browser = Browser('chrome', **executable_path, headless=True)
    news_title, news_paragraph = mars_news(browser)
    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemisphere_data": hemisphere_scrape(browser)

    }
    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')


    # Add try/except for error handling
    try:
    
        slide_elem = news_soup.select_one('div.list_text')

        #slide_elem.find('div', class_='content_title')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()


        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None
    
    return news_title, news_p



# ## JPL Space Images Featured Image

def featured_image(browser):

    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)


    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()


    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')


    # Add try/except for error handling
    try:

        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')


    except AttributeError:
        return None


    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'


    return img_url

# ## Mars Facts

def mars_facts():

    # Add try/except for error handling
    try:

        # use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com/')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")


# ## Mars Hemisphere Scraping
def hemisphere_scrape(browser) :
    # 1. Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)
    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []
    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    html = browser.html
    hemisphere_soup = soup(html, 'html.parser')

    hemisphere_links = hemisphere_soup.find_all('h3')

    # loop through each hemisphere link
    for hemispheres in hemisphere_links:
        # Navigate and click the link of the hemisphere
        img_page = browser.find_by_text(hemispheres.text)
        img_page.click()
        html= browser.html
        img_soup = soup(html, 'html.parser')
        img_url = 'https://astrogeology.usgs.gov/' + str(img_soup.find('img', class_='wide-image')['src'])
        title = img_soup.find('h2', class_='title').text
        hemisphere = {'img_url': img_url,'title': title}
        hemisphere_image_urls.append(hemisphere)
        browser.back()

    return hemisphere_image_urls

#----------------Ending Code ------------------------------------------
if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())