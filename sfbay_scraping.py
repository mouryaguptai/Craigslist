import requests
from bs4 import BeautifulSoup as bs4
import csv
import re
import time
from random import randint
processed_item = {}

# Scraped craigslist for each page details and constructed the product page urls
url = "https://sapi.craigslist.org/web/v8/postings/search/batch?batch=1-0-1080-1-0-1701907124-1701907192&cacheId=MToBnwTtJa7P_jrIHaW76OVdc48T0CDMOBAym3KE1_Q5ihnJnWusixwrO8Z50dy4EZ2E58lQ1Oxnt_97Bd-OfSlGIMGVVgypWfzansda-u9jU2kKZ7sBiodeSWg56fyGB-tOKq-0aQQvRlA5pQIGw9XNOUwy&cc=US&lang=en"
response = requests.get(url)

di = response.json()
url_li = []
base_url = 'https://sfbay.craigslist.org/sby/sys/d/'
for i in di['data']['batch']:
  url = base_url+i[3][1]+'/'+str(i[0]+7674373602)+'.html'
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

for index, url in enumerate(url_li, start=1):
  if url not in processed_item:
    response = requests.get(url)
    print(response.status_code)
    while response.status_code == 403:
      print("Sleeping for 15 mins ...")
      response = timetosleep(url)
    if response.status_code == 200:
      soup = bs4(response.text, 'html.parser')
      result_body = soup.find('section', id='postingbody')
      result = soup.find('span', class_='postingtitletext')
      content_body = ' '.join([str(i) for i in result_body.contents[2:]])
      content = ' '.join([str(i) for i in result.contents[:]])
      text_without_tags_body = re.sub(r'<.*?>|\n', '', content_body)
      text_without_tags = re.sub(r'<.*?>|\n', '', content)
      processed_item[url] = [text_without_tags_body, text_without_tags]
      if index % 3 == 0:
        time.sleep(randint(1,5))

# Store the dictionary of url and content in a csv file
with open('extract_processed_sfbay.csv', 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Product_Url', 'Content', 'Header'])
    for key, value in processed_item.items():
      csv_writer.writerow([key, value[0], value[1]])

