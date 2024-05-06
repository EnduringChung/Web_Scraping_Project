from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from numerizer import numerize

header = {
    "User-Agent": "Chrome/124.0.6367.63",
    "Accept-Language": "en-US"
}

URL = 'https://www.slickcharts.com/sp500'

#Geting the data from Slickcharts.com on S&P 500
response = requests.get(URL, headers = header)
website_html = response.text
soup = BeautifulSoup(website_html, "html.parser")
table = soup.find("table", class_="table table-hover table-borderless table-sm")
table_headers =[]
data = []
for th in table.find_all('th'):
    table_headers.append(th.text.strip())
for row in table.find_all('tr'):
    row_data = []
    for td in row.find_all('td'):
        row_data.append(td.text.strip())
    if row_data:
        data.append(row_data)

df = pd.DataFrame(data, columns= table_headers)
df

#Get Information from Wiki about the various background of the companies.
URL2 = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
response = requests.get(URL2, headers = header)
response.status_code
website_html2 = response.text
soup2 = BeautifulSoup(website_html2, "html.parser")
table2 = soup2.find("table", id = "constituents")

wiki_table_headers = []
for th in table2.find_all('th'):
    wiki_table_headers.append(th.text.strip())

wiki_data = []
for row in table2.find_all('tr'):
    row_data = []
    for td in row.find_all('td'):
        row_data.append(td.text.strip())
    if row_data:
        wiki_data.append(row_data)

df2 = pd.DataFrame(wiki_data, columns= wiki_table_headers)
df2

#Combine the information into one big list
merged_df = pd.merge(df,df2, on="Symbol", sort=True)
merged_df = merged_df.drop(['#'], axis=1)

#Get Market Cap
URL3 = 'https://www.slickcharts.com/sp500/marketcap'
response = requests.get(URL3, headers = header)
response.status_code
website_html3 = response.text
soup3 = BeautifulSoup(website_html3, "html.parser")
market_cap = soup3.find("h2", class_="text-center")

market_cap = market_cap.getText()
market_cap_number = numerize(market_cap)
market_cap_number = int(market_cap_number.replace('$',''))
market_cap_number

portfolio_percentage = list(merged_df['Portfolio%'])

#Do some analysis

#mean Price
merged_df['Price'] = pd.to_numeric(merged_df['Price'], errors= 'coerce')
mean_price = np.nanmean(merged_df['Price'])

#Mean Change
merged_df['Chg'] = pd.to_numeric(merged_df['Chg'], errors='coerce')
mean_change = np.nanmean(merged_df['Chg'])

#Number of Unique Industries
unique_industries = np.unique(merged_df['GICS Sector'])
unique_industries_list = np.unique(merged_df['GICS Sector'])
#unique_industries_list = list(unique_industries_list)
num_unique_industries = len(unique_industries)

#Count number of Companies in each industry
stats_industries = []
for i in range(num_unique_industries):
    count = np.count_nonzero(merged_df['GICS Sector'] ==unique_industries_list[i])
    stats_industries.append(count)

#Number of Unique Sub-Industries
unique_sub_industries = np.unique(merged_df['GICS Sub-Industry'])
num_unique_sub_industries = len(unique_sub_industries)

stats_industries

#Creating Pie Chart
fig= plt.figure(figsize=(10,7))
color = ("lightcoral", "darkorange", "gold", "yellowgreen", "limegreen", "aquamarine", "teal", "deepskyblue","skyblue", "slateblue", "mediumpurple")
plt.title("Percentage of different industry within the S&P 500 Company List")
plt.pie(stats_industries, labels = unique_industries_list, autopct='%1.1f%%', colors= color)
plt.show()

#Scatterplot

categories = list(unique_industries_list)
price_list = list(merged_df['Price'])
changes_list = list(merged_df['Chg'])

fig, ax = plt.subplots(figsize=(10,7))
ax = sns.stripplot(merged_df, x="Price", y='Chg', hue ='GICS Sector',native_scale=True)
plt.legend(bbox_to_anchor = (1.05, 1.0), loc ='upper left')
plt.grid()
plt.show()

#BotPlot
fig, ax = plt.subplots(figsize=(10,7))
sns.boxplot(merged_df, x='Price', y="GICS Sector" , fill= True, native_scale=True)
plt.show()

basic_info = {
    'Price' : mean_price ,
    'Change': mean_change,
    'Number of Industries': num_unique_industries,
    'Number of Sub-Industries' : num_unique_sub_industries,
    'Market Capitalization' : market_cap_number
}

df4 = pd.DataFrame(data=basic_info, index=[0])

#Output the data to Excel
filename = 'S&P500file3.xlsx'
relative_path = "./30 April 2024/" + filename
with pd.ExcelWriter(filename, mode='w', engine ='openpyxl') as writer:
    merged_df.to_excel(writer, sheet_name="marged_df", index= False)
    df4.to_excel(writer, sheet_name="Basic Info", index=False)