import requests
from bs4 import BeautifulSoup4
import re
import pandas as pd

url = "https://www.proshop.no/DEALS?pn=1"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

## Extract last page of 'deadls' page
pagination = soup.find('ul', class_='pagination').text
urlLastPage = re.findall(r'(\d+)', pagination)[-1]
urlLastPage = int(urlLastPage)


product_all = []

i = 2
## Loops through all sites to get products
while i-1 <= urlLastPage:
    response = requests.get(url, headers=headers)
    
    url = 'https://www.proshop.no/DEALS?pn=' + str(i)
    
    i = i + 1  

    if response.status_code == 200:

        soup = BeautifulSoup(response.text, "html.parser")    

        for product in soup.find_all('li', class_='row toggle'):  
            product_info_name = product.find(class_='col-xs-12').a.h2.text

            product_info_productId = product.find_all(class_='col-xs-12')
            product_id = product.find('input', {'name': 'productId'})
            product_id_value = product_id.get('value')


            try:
                badges = product.find('div', class_='site-image-badge-container-lg').text.strip()
                badgeList = []
                badgeList.append(badges)
                badgeList = badgeList[0].split('\n')

                if 'DEALS' in badgeList:
                    containKeyword = True

                else:
                    containKeyword = None

            except Exception as e:
                product_info_badges = None


            product_info_price = product.find(class_='col-xs-12 col-sm-12 price-container')
            product_info_currentPrice = product_info_price.select_one('span.site-currency-lg').string
            product_info_currentPrice = product_info_currentPrice.replace(u'\xa0', u' ')

            
            try:
                priceExpired = product.find('div', string="Kampanjen er utløpt").string
                if priceExpired == "Kampanjen er utløpt":
                    priceExpired = True

                if priceExpired == True:

                    product_info_preSalePrice = product_info_price.select_one('div.site-currency-pre').text
                    product_info_preSalePrice = product_info_preSalePrice.replace(u'\xa0', u' ')       
            
            except Exception as e:
                priceExpired = None


            try:
                if priceExpired == None:
                    product_info_preSalePrice = product_info_price.select_one('span.site-currency-pre').text
                    product_info_preSalePrice = product_info_preSalePrice.replace(u'\xa0', u' ')


            except Exception as e:
                product_info_preSalePrice = None            

          
            
            product_list = []
            product_list.append(product_info_name)
            product_list.append(product_id_value)
            product_list.append(badgeList)
            product_list.append(product_info_currentPrice)
            product_list.append(product_info_preSalePrice)
            product_list.append(priceExpired)
            product_list.append(containKeyword)
            product_list.append('https://proshop.no/' + product_id_value)
            product_list.append(url)

            product_all.append(product_list)
     

        response.close()

    else:
        print("Failed to retrieve the webpage")

## prints total products found on all sites
print(len(product_all))
df = pd.DataFrame(product_all, columns = ['Product', 'Product ID', 'Badges', 'CurrentPrice', 'OldPrice', 'PriceExpired', 'ContainKeyword', 'ProductURL', 'DealsPageURL'])


## Export to excel
#df.to_excel(r'PATH\Proshop.xlsx', index=False, sheet_name='Sheet1')
