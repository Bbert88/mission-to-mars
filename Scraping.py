# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    #Set up splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    news_title, news_paragraph = mars_news(browser)
    
    # Run all scraping functions and store results in dictionary
    data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "last_modified": dt.datetime.now(),
      "hemispheres": mars_hemispheres(browser)
    }
    
    #stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)


    #Convert browser html to a soup object
    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:
        slide_elem = news_soup.select_one('div.list_text')
        #use parent element to find 1st 'a' tag
        news_title = slide_elem.find("div", class_="content_title").get_text()
        #find paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()
    except AttributeError:
        return None, None

    return news_title, news_p


# Featured Images

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

    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    except AttributeError:
        return None

    #Add base url
    img_url = f"https://spaceimages-mars.com/{img_url_rel}"

    return img_url

#Mars Facts
def mars_facts():

    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None

    #assign columns and set index of df
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    #convert df to html, add bootstrap
    return df.to_html(classes="table table-striped")
    
def mars_hemispheres(browser):
    url = 'https://marshemispheres.com/'
    browser.visit(url)
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    hem_html = browser.html
    hem_soup = soup(hem_html, 'html.parser')

    items = hem_soup.find_all("div", class_="item")

    for i in items:
        #ectract title for each hemisphere
        title = i.find("h3").get_text()
    
        #get url of each hemisphere image item and visit that url
        tn_url = i.find("a")['href']
        full_tn_url = url + tn_url
        browser.visit(full_tn_url)
    
        #create new soup object to parse html
        img_html=browser.html
        img_soup=soup(img_html, 'html.parser')
    
        #extract partial url of full resolution jpg image
        dloads_url = img_soup.find("div", class_="downloads").find("a")['href']

        #construct full url to full resolution jpb image
        jpg_url = url + dloads_url
    
        #save in to dictionary to be added to list of hemispheres
        hemispheres = {
            "img_url": jpg_url,
            "title": title
        
        }
        hemisphere_image_urls.append(hemispheres)
    return hemisphere_image_urls

if __name__ == "__main__":
    print(scrape_all())



