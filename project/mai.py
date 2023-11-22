import folium
import json

with open('us-states.json') as f:
    geojson_data = json.load(f)

m = folium.Map(location=[37, -95], zoom_start=3)

legend_html = """
<div style="position: fixed; 
            bottom: 50px; left: 50px; width: 100px; height: 250px; 
            border:2px solid grey; z-index:9999; font-size:14px;
            background-color:white; opacity:0.7">
<p style="margin:10px">Number of immigrants</p>
"""

def color_state(feature):
    state_name = feature['properties']['name']
    if state_name in ['California', 'Texas', 'New York', 'Florida']:
        return {'fillColor': 'red', 'weight': 2, 'color': 'black'}

    if state_name in ['Washington', 'Nevada', 'Arizona', 'Colorado', 'Illinois', 'Pennsylvania', 'Virginia',
                      'North Carolina', 'Georgia']:
        return {'fillColor': 'orange', 'weight': 2, 'color': 'black'}

    if state_name in ['Oregon', 'Utah', 'Minnesota', 'Michigan', 'Indiana', 'Tennessee']:
        return {'fillColor': 'yellow', 'weight': 2, 'color': 'black'}

    if state_name in ['Idaho', 'Nebraska', 'Kansas', 'Oklahoma', 'Arkansas', 'Mississippi']:
        return {'fillColor': 'green', 'weight': 2, 'color': 'black'}

    if state_name in ['Montana', 'Wyoming', 'North Dakota', 'South Dakota', 'Maine']:
        return {'fillColor': 'blue', 'weight': 2, 'color': 'black'}

    return {'fillColor': 'white', 'weight': 2, 'color': 'black'}

folium.GeoJson(geojson_data, style_function=color_state).add_to(m)

color_dict = {
    'A lot': 'red',
    'Many': 'orange',
    'Moderate': 'yellow',
    'Few': 'green',
    'Very Few': 'blue'
}

for label, color in color_dict.items():
    legend_html += (f"<p style='margin:10px'><span style='background-color:{color};'>&nbsp;&nbsp;&nbsp;&nbsp;"
                    f"</span> {label}</p>")

legend_html += "</div>"

html_legend = folium.Html(legend_html, script=True)
legend_popup = folium.Popup(html_legend, max_width=300)

legend_icon = folium.DivIcon(html=legend_html, icon_size=(150, 100), icon_anchor=(0, 0))
legend_marker = folium.Marker(location=[35, -70], icon=legend_icon, popup=legend_popup)
legend_marker.add_to(m)

m.save('templates/us_illegal_with_legend.html')
