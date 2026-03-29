from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np 
from requests import get

# fonction pour scraper les villas
def scrap_villas(nbre_pages):
    data = {
        "type annonce": [],
        "nombre pieces": [],
        "prix": [],
        "adresse": [],
        "image lien": []
    }
    
    for i in range(nbre_pages):
    
        url = 'https://sn.coinafrique.com/categorie/villas?page={n}'
        
        res = get(url)
        soup = bs(res.text, 'html.parser')
        containers = soup.find_all('div', class_ = "col s6 m4 l3")
        
        for container in containers:
            img_link = container.find('img', class_ = "ad__card-img")['src']
            inner_link = container.find('a', class_ = "card-image ad__card-image waves-block waves-light")["href"]
            url_enfant = 'https://sn.coinafrique.com' + inner_link
            
            res1 = get(url_enfant)
            soup1 = bs(res1.text, 'html.parser')
            container_1 = soup1.find('div', class_ = "card round slide proffer z-depth-0 remove-background-white")
            try:
                type_annonce = container_1.find('h1', class_ = 'title title-ad hide-on-large-and-down').text.split()[0].capitalize()
                nombre_pieces = int(container_1.find('span', class_ = 'qt').text)
                prix = int(container_1.find('p', class_ = 'price').text.replace('CFA', '').replace(' ', '').strip())
                adresse = container_1.find_all('span', class_ = 'valign-wrapper')[1].text
            except Exception as e:
                continue
            
            
            dico = {
                "type annonce": type_annonce,
                "nombre pieces": nombre_pieces,
                "prix": prix,
                "adresse": adresse,
                "image lien": img_link
            }
            
            for key, value in dico.items():
                data[key].append(value)
        
    df = pd.DataFrame(data)
    return df

# fonction pour scraper les terrains
def scrap_terrains(nbre_page):
    
    df1 = pd.DataFrame()
    
    for i in range(nbre_page):
        
        url = 'https://sn.coinafrique.com/categorie/terrains?page={i}'
        
        data = []
        
        res = get(url)
        soup = bs(res.text, 'html.parser')
        containers = soup.find_all("div",class_ = "col s6 m4 l3")
        
        for container in containers:
            try:
                img_link = container.find("img", class_="ad__card-img")["src"]
                prix = int(container.find("p", class_="ad__card-price").text.replace(" ", "").replace("CFA", ""))
                adresse = container.find("p", class_="ad__card-location").text.replace("location_on","")
                inner_link = container.find("a", class_="card-image ad__card-image waves-block waves-light")["href"]
                url_enfant = 'https://sn.coinafrique.com' + inner_link
                
                resa = get(url_enfant)
                soup = bs(resa.text, 'html.parser')
                container__ = soup.find("div", class_="ad__info")
                superficie = int(container__.find("span", class_="qt").text.replace(" ", "").replace("m2", ""))
                
                infos = {
                    "superficie": superficie,
                    "prix": prix,
                    "adresse": adresse,
                    "img_link": img_link,
                }
                
                data.append(infos)
            except:
                pass
        DF = pd.DataFrame(data)
        
        df1 = pd.concat([df1,DF],axis=0).reset_index(drop = True)


    return df1

# variable pour les formulaires
google_forms = '<iframe src="https://docs.google.com/forms/d/e/1FAIpQLScIINigJlApa3cAGiSv4cmZMRUvjxyms6HmKoIdOQcrEeuSvA/viewform?embedded=true" width="700" height="650" frameborder="0" marginheight="0" marginwidth="0">Chargement…</iframe>'
kobo_forms = '<iframe src=https://ee.kobotoolbox.org/i/j9qkSiwi width="700" height="600"></iframe>'

# autres variables
mot_inspirant = """Explorez, collectez, analysez.
Le web à portée de main, vos données en action.
Scraping, visualisation, décision – en un clic !"""

streamdata_logo = "./images/StreamData-logo.webp"



    
    