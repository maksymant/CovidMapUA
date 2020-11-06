Covid Map UA (https://covidmapua.herokuapp.com/)

Simple project on Flask with BeautifulSoup4 and Folium that visually represents COVID spread and weight around Ukraine regions.

Python script scrapes data from https://index.minfin.com.ua/reference/coronavirus/ukraine/ (quantity of COVID infected people per region in Ukraine) and generates html file with Folium map based on GeoJson data.

Region color is based on relative quantity of infected - normalized from 0 to maximum infected region, where 0 is full transparent and infected_max is full red.
