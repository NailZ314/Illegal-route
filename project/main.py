from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import numpy as np
import subprocess

app = Flask(__name__)
bootstrap = Bootstrap(app)
CKEditor(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about/')
def about():
    return render_template('about.html')

@app.route('/generate_map')
def generate_map():
    subprocess.run(['python', 'a.py'])
    with open('templates/map.html', 'r') as f:
        map_content = f.read()
    return map_content

@app.route('/safety')
def safety():
    subprocess.run(['python', 'a.py'])
    with open('safety_info.txt', 'r') as f:
        safety_info = f.read()
    return safety_info

@app.route('/generate_map2')
def generate_map2():
    subprocess.run(['python', 'mai.py'])
    with open('templates/us_illegal_with_legend.html', 'r') as f:
        map_content = f.read()
    return map_content

@app.route('/methods/')
def methods():
    return render_template('methods.html')

@app.route('/partnership/')
def partnership():
    return render_template('partnership.html')

@app.route('/statistics/')
def statistics():
    years = np.array([1985, 1990, 1995, 2000, 2005, 2010, 2013])
    illegal_immigrants_overstay = np.array([100, 175, 150, 250, 300, 200, 175])
    illegal_immigrants_border_crossing = np.array([75, 125, 100, 225, 175, 200, 225])

    plt.plot(years, illegal_immigrants_overstay, label="Overstay")
    plt.plot(years, illegal_immigrants_border_crossing, label="Перебрались через границу с Мексикой")

    plt.title("Growth in the Number of Illegal Immigrants from Mexico to the U.S.")
    plt.xlabel("Year")
    plt.ylabel("Number of Illegal Immigrants (Thousands)")

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template('statistics.html',plot_url=plot_url)

@app.route('/howtogetUS/')
def howtogetUS():
    return render_template('howtogetUS.html')

if __name__ == '__main__':
    app.run(debug=True)