import requests
import string
from bs4 import BeautifulSoup
import pandas as pd

NUMBER_OF_PAGES = 3

def tokenize_question(query):
    tokens = "".join([ch for ch in query if ch not in string.punctuation]).split()
    return tokens


def get_page(tokens):
    headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36", "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"}
    string = "+".join([word for word in tokens])
    #get first "NUMBER_OF_PAGES" pages data 
    for page_no in range(1, NUMBER_OF_PAGES+1): 
        url = 'https://www.amazon.co.in/s?k=' + string + '&page=' + str(page_no)
        raw_data = requests.get(url, headers=headers)
        soup = BeautifulSoup(raw_data.content, 'html5lib')
        web_parser(soup)

def web_parser(soup):

    global dataframe 

    for ele in soup.findAll("div", {'class':"a-section a-spacing-medium"}): 
        try: 
            product_name = ele.h2.span.text
            manufacturer = product_name.split()[0]
            product_link = 'amazon.in' + ele.find('a', {'class':"a-link-normal a-text-normal"})['href']
            discounted_price = ele.find('span', {'class': 'a-offscreen'}).text[1:]         
        
            try: 
                price_details = ele.find('span', {"class":'a-price a-text-price'})
                actual_price = price_details.find('span', {"class": "a-offscreen"}).text[1:]
            except: 
                actual_price = discounted_price


            #remove commas
            discounted_price = discounted_price.replace(",", "")
            actual_price = actual_price.replace(",", "")

            #check for float pricing 
            if "." in discounted_price: 
                discounted_price = float(discounted_price)
            else: 
                discounted_price =int(discounted_price)
            
            if "." in actual_price: 
                actual_price = float(actual_price)
            else:
                actual_price = int(actual_price)
            
            discount_amt = actual_price - discounted_price

            discount_percentage = round(discount_amt*100/actual_price)

            dataframe = dataframe.append({'Manufacturer': manufacturer ,'Specification':product_name, 'Price':discounted_price,  'Discount Percentage': discount_percentage, 'Link': product_link},ignore_index=True)
        except: 
            pass
    return dataframe
    
       
def create_dataframe(): 
    df = pd.DataFrame(None, columns=['Manufacturer','Specification', 'Price', 'Discount Percentage', 'Link'])
    return df 



#create table for data 
dataframe = create_dataframe()

#prompt user to query 
query = input("search term: ")
tokens = tokenize_question(query)
data = get_page(tokens)
dataframe = dataframe.sort_values(['Price', 'Discount Percentage'], ascending=False)
dataframe = dataframe.reset_index(drop=True)
print(dataframe)
save_data = input("Save data to excel file?(Y)")
if "y" in save_data.lower(): 
    file_name = input("filename: ")
    dataframe.to_csv(f"./data/{file_name}.csv")
