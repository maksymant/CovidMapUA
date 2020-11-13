from flask import Flask, render_template, url_for
from process import get_city_data, update_geojson, generate_map
app = Flask(__name__)


@app.route('/')
def render_map():
    data, bar_data = get_city_data()

    update_geojson(data)

    # generate_map(data)
    generate_map(bar_data)



    return render_template('map.html')


if __name__ == '__main__':
    app.run()
