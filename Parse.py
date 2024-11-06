import requests
from bs4 import BeautifulSoup

def fetch_recipe(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        raise ValueError("Could not fetch the webpage. Please check the URL.")

# test
soup = fetch_recipe("https://www.allrecipes.com/recipe/218091/classic-and-simple-meat-lasagna/")
print(soup)