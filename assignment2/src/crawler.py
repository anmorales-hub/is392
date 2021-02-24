import queue
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import ssl
import os

# ==========
# Declare Variables
# ==========

queue = []          #queue of URLs
visitedUrlList = [] #prevent a single url from entering queue repeatedly
pageCounter = 0
savedUrlList = []
crawlCount = 0

# ==========
# Functions
# ==========

# Gets content from pages
def get_page_content(url):
    try:
        html_response_text = urlopen(url).read()
        page_content = html_response_text.decode('utf-8')
        return page_content
    except Exception as e:
        return None

# Gets rid of any unusable characters in the title
def clean_title(title):
    invalid_characters = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for c in invalid_characters:
        title = title.replace(c, '')
    return title

# Extract outgoing(inner) URLs from page content
def get_urls(soup):
    links = soup.find_all('a')
    urls=[]
    for link in links:
        urls.append(link.get('href'))
    return urls

# Check if URL is valid
def is_url_valid(url):
    if url is None:
        return False
    if re.search('#', url):
        return False
    match = re.search('^/wiki/', url)
    if match:
        return True
    else:
        return False

# Reformat URL / change relative URL into full URL
def reformat_url(url):
    match=re.search('^/wiki/', url)
    if match:
        return "https://en.wikipedia.org" + url
    else:
        return url

# Save a page
def save(text, path):
    f = open(path, 'w', encoding = 'utf-8', errors = 'ignore')
    f.write(text)
    f.close()

# ==========
# Crawling begins
# ==========
def crawler(seedUrls, relatedTerms):
    queue = []          #queue of URLs
    visitedUrlList = [] #prevent a single url from entering queue repeatedly
    pageCounter = 0
    savedUrlList = []
    crawlCount = 0

     # Set up SSL Environment
    try:
            _create_unverified_https_context = ssl.create_unverified_context
    except AttributeError:
            pass
    else:
            ssl._create_default_https_context = _create_unverified_https_context

    for url in seedUrls:
        #url = reformat_url(url)
        queue.append(url)
        visitedUrlList.append(url)

    while len(queue) > 0:
        urlCurr = queue.pop(0)           # Get the URL in front of the queue and remove it
        urlCurr = reformat_url(urlCurr)
        crawlCount += 1
        content = get_page_content(urlCurr)            # Get the page content via HTTP
        if content is None:
            continue

        termCounter = 0
        soup = BeautifulSoup(content,'html.parser')      # Parse page content
        page_text = soup.get_text()        # Extract main text of a page

        for term in relatedTerms:
            if re.search(term, page_text, re.I):         # If page contains a (related) term
                termCounter += 1
                if termCounter >= 2:        # If a page is topical/relevant
                    title = soup.title.string
                    title = clean_title(title)
                    path = "../savedSites/" + title      # Path to saved links file
                    save(str(soup), path)            # Save web page
                    savedUrlList.append(urlCurr)
                    pageCounter += 1
                    print("Page # " + str(pageCounter) + ": " + urlCurr )
                    break
        if pageCounter >= 500:
            break

        outGoingUrls = get_urls(soup)
        for outGoingUrl in outGoingUrls:
            if is_url_valid(outGoingUrl) and outGoingUrl not in visitedUrlList:
                queue.append(outGoingUrl)
                visitedUrlList.append(outGoingUrl)

        # Save the saved Url list
    f = open("crawled_urls.txt", "w")
    f.write("Pages Crawled: " + str(crawlCount) + "\n")
    i = 1
    for url in savedUrlList:
        f.write(str(i) + ': ' + url + '\n' )
        i += 1
    f.close()


seedUrls =['https://en.wikipedia.org/wiki/Chess_opening', 'https://en.wikipedia.org/wiki/Gambit' ]
relatedTerms = ['bobby fischer', 'magnus carlsen', 'levy rozman', 'chess', 'grandmaster', 'FIDE', 'gambit', 'defense', 'attack', 'gambit', 'variation', 'pawn structure', 'e4', 'd4', 'chess theory' ]

crawler(seedUrls, relatedTerms)
