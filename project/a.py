import folium
from geopy.distance import great_circle
import random
import mysql.connector

def calculate_distance(coord1, coord2):
    return great_circle(coord1, coord2).kilometers

db = mysql.connector.connect(
    user='root',
    password='11111111',
    host='localhost',
    database='cities',
    buffered=True
)

cursor = db.cursor()

def get_safety_index(city):
    query = f"SELECT safety_index FROM danger_latam WHERE city_name = '{city}'"
    cursor.execute(query)
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

def get_latam_coordinates(city):
    query = f"SELECT latitude, longitude FROM latam_cities WHERE city_name = '{city}'"
    cursor.execute(query)
    result = cursor.fetchone()
    return (result[0], result[1])

def get_coordinates(city):
    query = f"SELECT latitude, longitude FROM other_cities WHERE city = '{city}'"
    cursor.execute(query)
    result = cursor.fetchone()
    return (result[0], result[1])

def get_farthest_city(city):
    query = f"SELECT city_name FROM latam_cities WHERE city_name != '{city}' ORDER BY ABS(latitude - (SELECT latitude FROM latam_cities WHERE city_name = '{city}')) + ABS(longitude - (SELECT longitude FROM latam_cities WHERE city_name = '{city}')) DESC LIMIT 1"
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0]

def get_nearest_city(coord, latam_cities):
    nearest_city = min(latam_cities, key=lambda x: calculate_distance(coord, (x[1], x[2])))
    return nearest_city[0], (nearest_city[1], nearest_city[2])

def get_random_latam_city():
    query = "SELECT city_name, latitude, longitude FROM latam_cities ORDER BY RAND() LIMIT 1"
    cursor.execute(query)
    result = cursor.fetchone()
    if result:
        return result[0], (result[1], result[2])
    else:
        return None, None

def get_random_mexico_city():
    mexico_cities = ['Mexicali', 'Tijuana', 'Ciudad Juarez', 'Nuevo Laredo', 'Reynosa', 'Matamoros']
    return random.choice(mexico_cities)

def get_random_us_city(coord):
    query = f"SELECT city_name, latitude, longitude FROM us_cities ORDER BY ABS(latitude - {coord[0]}) + ABS(longitude - {coord[1]}) LIMIT 1"
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0], (result[1], result[2])

def add_extra_us_city():
    query = "SELECT city_name, latitude, longitude FROM us_cities ORDER BY RAND() LIMIT 1"
    cursor.execute(query)
    result = cursor.fetchone()
    return result[0], (result[1], result[2])

mymap = folium.Map(location=[51.1694, 71.4491], zoom_start=2)

city1 = "Astana"
city2 = random.choice(['Moscow', 'Dubai', 'Istanbul', 'Frankfurt'])
coord1 = get_coordinates(city1)
coord2 = get_coordinates(city2)
folium.Marker(coord1, popup=city1).add_to(mymap)
folium.Marker(coord2, popup=city2).add_to(mymap)
folium.PolyLine([coord1, coord2], color="blue").add_to(mymap)

city3 = get_farthest_city(city2)
coord3 = get_latam_coordinates(city3)
folium.Marker(coord3, popup=city3).add_to(mymap)
folium.PolyLine([coord2, coord3], color="blue").add_to(mymap)

query_latam_cities_safety = "SELECT city_name, latitude, longitude FROM latam_cities"
cursor.execute(query_latam_cities_safety)
latam_cities_safety = cursor.fetchall()

num_latam_cities = random.randint(3, 7)
prev_coord = coord3
latam_city_coords = []
total_safety_index = 0

for _ in range(num_latam_cities):
    random_latam_city, random_latam_coord = get_random_latam_city()
    if random_latam_city and random_latam_coord:
        latam_city_coords.append((random_latam_city, random_latam_coord))
        safety_index = get_safety_index(random_latam_city)
        if safety_index is not None:
            total_safety_index += safety_index

latam_city_coords.sort(key=lambda x: calculate_distance(prev_coord, x[1]))

for random_latam_city, random_latam_coord in latam_city_coords:
    folium.Marker(random_latam_coord, popup=f"{random_latam_city} - Safety Index: {get_safety_index(random_latam_city)}").add_to(mymap)
    folium.PolyLine([prev_coord, random_latam_coord], color="blue").add_to(mymap)
    prev_coord = random_latam_coord

overall_safety_index = total_safety_index / num_latam_cities

if 80 <= overall_safety_index:
    safety_category = "Very High Safety"
elif 70 <= overall_safety_index < 80:
    safety_category = "High Safety"
elif 60 <= overall_safety_index < 70:
    safety_category = "Moderate Safety"
elif 50 <= overall_safety_index < 60:
    safety_category = "Low Safety"
else:
    safety_category = "Very Low Safety"

with open("safety_info.txt", "w") as f:
    f.write(f"Overall Safety Index: {overall_safety_index:.2f} - Category: {safety_category}")

random_mexico_city = get_random_mexico_city()
random_mexico_coord = get_coordinates(random_mexico_city)
nearest_city_mexico, nearest_coord_mexico = get_nearest_city(random_mexico_coord, latam_cities_safety)
folium.Marker(random_mexico_coord, popup=f"{random_mexico_city} - Safety Index: {get_safety_index(random_mexico_city)}").add_to(mymap)
folium.PolyLine([prev_coord, nearest_coord_mexico], color="blue").add_to(mymap)
prev_coord = nearest_coord_mexico

random_us_city, random_us_coord = get_random_us_city(random_mexico_coord)
folium.Marker(random_us_coord, popup=f"{random_us_city} - Safety Index: {get_safety_index(random_us_city)}").add_to(mymap)
folium.PolyLine([prev_coord, random_us_coord], color="blue").add_to(mymap)

folium.PolyLine([nearest_coord_mexico, random_us_coord], color="blue").add_to(mymap)

extra_us_city, extra_us_coord = add_extra_us_city()
folium.Marker(extra_us_coord, popup=f"{extra_us_city} - Safety Index: {get_safety_index(extra_us_city)}").add_to(mymap)
folium.PolyLine([random_us_coord, extra_us_coord], color="blue").add_to(mymap)

mymap.save("templates/map.html")