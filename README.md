Covid Map UA (https://covidmapua.herokuapp.com/)

Simple project on Flask with BeautifulSoup4 and Bokeh that visually represents COVID spread and weight around Ukraine regions.

Python script scrapes data from https://index.minfin.com.ua/reference/coronavirus/ukraine/ (quantity of COVID infected people per region in Ukraine) and generates html file with Bokeh map based on GeoJson data.

Region color (shades of red) is based on relative quantity of infected - normalized from 0 to maximum infected region.
