import re

import requests
import json
from bs4 import BeautifulSoup

import requests
from bs4 import BeautifulSoup


response = requests.get("https://paper.people.com.cn/rmrb/pc/content/202506/04/content_30077088.html", headers={"User-Agent": "Mozilla/5.0"})
response.encoding = response.apparent_encoding  # 自动识别编码
soup = BeautifulSoup(response.text, 'html.parser')
#print(soup)

#elements = soup.find_all(['body'])
elements = soup.find('div',attrs={'id':'ozoom'})
elements = elements.find_all(['body'])
elements = re.findall("\w*",str(elements))
print(elements)


