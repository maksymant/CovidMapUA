import requests
import time
import json
import folium as fl
import branca.colormap as cm
import re
from bs4 import BeautifulSoup
from citymapper import get_city_name


def get_city_data():
    url = 'https://index.minfin.com.ua/reference/coronavirus/ukraine/'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    city_table = soup.find('div', class_='sort1-table').find('div').find('table').findAll('tr')

    cases_date = soup.find('table', class_='line main-table').find('caption')
    date = re.search(r'\d{1,2}\.\d{2}\.\d{4}\b', str(cases_date)).group(0)

    cases = soup.find('table', class_='line main-table').findAll('tr')
    total_cases = str(cases[0].find('strong', class_='black').contents[0])
    current_cases = str(cases[3].find('strong', class_='blue').contents[0])

    data_for_navbar = {
        'curr_date': date,
        'total_cases': total_cases,
        'curr_cases': current_cases
    }

    data = {}
    for i in range(1, len(city_table) - 1):
        city = city_table[i].contents[0].text
        infected = city_table[i].contents[1].text
        data[city] = infected
        time.sleep(0.05)

    return data, data_for_navbar


def update_geojson(data: dict):
    with open("UA.geojson", 'r+', encoding='utf-8') as read_file:
        js = json.load(read_file)

        data_to_append = {}
        for city in data:
            latin_city = get_city_name(city)
            data_to_append[latin_city] = data[city]

        read_file.seek(0)
        for i in js['features']:
            city = i['properties']['name']
            if city in data_to_append:
                i['properties'].update({'infected': data_to_append[city]})
            else:
                i['properties'].update({'infected': 0})
        json.dump(js, read_file)
        read_file.truncate()


def generate_map(data: dict):
    ua_map = fl.Map(location=[48.6992149, 31.2844733], zoom_start=6)
    fg = fl.FeatureGroup(name='Ukraine COVID-19 map')

    infected_max = max([int(x) for x in data.values()])
    infected_min = min([int(x) for x in data.values()])
    colormap = cm.linear.Reds_09.scale(infected_min, infected_max)

    fg.add_child(fl.GeoJson(data=open('UA.geojson', 'r').read(),
                            popup=fl.GeoJsonPopup(fields=['name', 'infected'], aliases=['Region', 'Infected']),
                            style_function=lambda x: {'fillColor': colormap(int(x['properties']['infected'])),
                                                      'fillOpacity': 0.7},
                            highlight_function=lambda x: {'stroke': True, 'color': 'Blue', 'opacity': 0.2,
                                                          'fillOpacity': 1}))

    ua_map.add_child(fg)
    ua_map.add_child(fl.LayerControl())
    ua_map.save('templates/map.html', close_file=True)
