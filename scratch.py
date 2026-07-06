import requests

# check if page parameter changes the data
url1 = "https://www.databricks.com/dataaisummit/_next/data/w0UF1m2b28FCTkiLEweK3/en-US/agenda.json?page=1"
url2 = "https://www.databricks.com/dataaisummit/_next/data/w0UF1m2b28FCTkiLEweK3/en-US/agenda.json?page=2"

r1 = requests.get(url1).json()
r2 = requests.get(url2).json()

print(f"Page 1 == Page 2: {r1 == r2}")

# check the custom component
data = r1
page_data = data["pageProps"]["pageData"]
content = page_data["content"]

print(f"\nCustom component:")
custom = content[3]
print(custom)