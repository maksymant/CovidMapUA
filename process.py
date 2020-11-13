import requests
import time
import json
import re
from bs4 import BeautifulSoup
from citymapper import get_city_name
from bokeh.models import ColorBar, LinearColorMapper, NumeralTickFormatter
from bokeh.palettes import OrRd9
from bokeh.plotting import figure, output_file, save


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


def generate_map(bar_data: dict):
    output_file("templates/map.html", title='Covid-19 UA Map')

    geodata = json.load(open("UA.geojson", 'r+', encoding='utf-8'))

    ua_xs = []
    for region in geodata['features']:
        if region['geometry']['type'] == "Polygon":
            ua_xs.append([x[0] for x in region['geometry']['coordinates'][0]])
        if region['geometry']['type'] == "MultiPolygon":
            temp_lst = []
            for nest in region['geometry']['coordinates']:
                mult_ua_xs = [x[0] for x in nest[0]]
                mult_ua_xs.append('nan')
                temp_lst.append(mult_ua_xs)
            flat_list = [item for sublist in temp_lst for item in sublist]
            ua_xs.append(flat_list)

    ua_ys = []
    for region in geodata['features']:
        if region['geometry']['type'] == "Polygon":
            ua_ys.append([x[1] for x in region['geometry']['coordinates'][0]])
        if region['geometry']['type'] == "MultiPolygon":
            temp_lst = []
            for nest in region['geometry']['coordinates']:
                mult_ua_ys = [x[1] for x in nest[0]]
                mult_ua_ys.append('nan')
                temp_lst.append(mult_ua_ys)
            flat_list = [item for sublist in temp_lst for item in sublist]
            ua_ys.append(flat_list)

    region_names = [name['properties']['name'].replace("'", "") for name in geodata['features']]
    region_infected = [int(infected['properties']['infected']) for infected in geodata['features']]

    palette = tuple(reversed(OrRd9))
    color_mapper = LinearColorMapper(palette=palette, low=min(region_infected), high=max(region_infected))

    color_bar = ColorBar(color_mapper=color_mapper,
                         label_standoff=10,
                         formatter=NumeralTickFormatter(format='0,0'),
                         width=10,
                         border_line_color=None,
                         location=(0, 0))

    data = dict(
        x=ua_xs,
        y=ua_ys,
        name=region_names,
        infected=region_infected
    )

    tools = "pan,wheel_zoom,reset,hover,save"

    p = figure(
        tools=tools,
        tooltips=[("Name", "@name" + " region"), ("Currently infected", "@infected")],
        x_axis_location=None, y_axis_location=None,
        toolbar_location='above'
    )
    p.aspect_ratio = 1.5
    p.sizing_mode = 'scale_height'

    p.title.text = f"Covid19 UA Regions  |  Info date: {bar_data['curr_date']}  |  Total cases: {bar_data['total_cases']}  |  Current cases: {bar_data['curr_cases']}"
    p.title.align = "left"
    p.title.text_color = '#355070'
    p.title.text_font_size = "15px"

    p.grid.grid_line_color = None

    p.patches(xs='x', ys='y', source=data, line_color="black", line_width=0.5,
              fill_color={'field': 'infected',
                          'transform': color_mapper},
              fill_alpha=1
              )

    p.add_layout(color_bar, 'right')
    save(p)
