import requests
from bs4 import BeautifulSoup as bs4
import csv
import re
import time
from random import randint

# Dictionary to store processed item data
processed_item = {}

# Scraped craigslist for each page details and constructed the product page urls
url = "https://sapi.craigslist.org/web/v8/postings/search/batch?batch=11-0-1080-1-0-1701831697-1701833025&cacheId=MToByjtx0oBBiwzLYU1lne6ShR5A55eejcOi_OjN4XM5fTNhr7ThHfLgeSPmWbN6c4ZbYs4A4zWMqvwZyEwtZxvpdXSsB78yBjFg-H-8tlF20B44WspEmR_GzSCpIEEe05QQAzAQa8pxe2B-ZTfGLuryS9ADO0I2&cc=US&lang=en"
response = requests.get(url)

# Parse JSON response
di = response.json()
url_li = []
base_url = 'https://chicago.craigslist.org/nwc/sys/d/'

# Construct URLs from JSON data
for i in di['data']['batch']:
  url = base_url+i[3][1]+'/'+str(i[0]+7673972389)+'.html'
  url_li.append(url)

print(len(url_li))

# Saved the product urls into txt and csv files for backup
with open('links.txt', 'w') as file:
    # Write each element of the list to a new line in the file
    for item in url_li:
        file.write(item + '\n')

with open('links.csv', 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    for item in url_li:
      csv_writer.writerow([item])

def timetosleep(url):
  time.sleep(900)
  response = requests.get(url)
  return response

# Loop through URLs and scrape content
for index, url in enumerate(url_li, start=1):
  if url not in processed_item:
    response = requests.get(url)
    print(response.status_code)
    while response.status_code == 403:
      print("Sleeping for 15 mins ...")
      response = timetosleep(url)
    if response.status_code == 200:
      # Parse HTML content
      soup = bs4(response.text, 'html.parser')
      result_body = soup.find('section', id='postingbody')
      result = soup.find('span', class_='postingtitletext')
      content_body = ' '.join([str(i) for i in result_body.contents[2:]])
      content = ' '.join([str(i) for i in result.contents[:]])
      # Remove HTML tags and newlines
      text_without_tags_body = re.sub(r'<.*?>|\n', '', content_body)
      text_without_tags = re.sub(r'<.*?>|\n', '', content)
      processed_item[url] = [text_without_tags_body, text_without_tags]
      if index % 3 == 0:
        time.sleep(randint(1,5))

# Store the dictionary of url and content in a csv file
with open('extract_processed.csv', 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Product_Url', 'Content', 'Header'])
    for key, value in processed_item.items():
      csv_writer.writerow([key, value[0], value[1]])

