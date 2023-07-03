# -*- coding: utf-8 -*-
import geopandas as gpd
from shapely.geometry import Point, Polygon

# Wczytaj warstwę SHP z pliku o podanej ścieżce (plik wejściowy przed generalizcją)
input_shapefile = r"C:\Users\ngaje\Desktop\MAGISTERKA\2\G_COMPARTMENT.shp"
data = gpd.read_file(input_shapefile)

# Połączenie wszystkich poligonów w warstwie wejściowej w jeden poligon.
merged_polygon = data.unary_union

# Tworzenie listy nowych poligonów- (pusta lista, która będzie przechowywać nowe poligony)
new_polygons = []

if merged_polygon.geom_type == 'Polygon':
    merged_polygons = [merged_polygon]
elif merged_polygon.geom_type == 'MultiPolygon':
    merged_polygons = list(merged_polygon.geoms)

# Iteracja przez każdy poligon w merged_polygons. Dla każdego poligonu, tworzy nową
# listę new_vertices, przechowującą nowe wierzchołki obliczone jako średnie współrzędne.
# Następnie tworzy nowy poligon new_polygon na podstawie new_vertices i dodaje go do listy new_polygons.

for polygon in merged_polygons:
    new_vertices = []
    vertices = list(polygon.exterior.coords)

    for i in range(len(vertices) - 1):
        x_avg = (vertices[i][0] + vertices[i + 1][0]) / 2
        y_avg = (vertices[i][1] + vertices[i + 1][1]) / 2
        new_vertices.append((x_avg, y_avg))

    new_polygon = Polygon(new_vertices)
    new_polygons.append(new_polygon)

# Pobiera informacje o CRS z warstwy wejściowej
crs = data.crs

# Tworzenie nowej ramki danych (GeoDataFrame) na podstawie nowych
# poligonów new_polygons i przypisanie CRS.
merged_data = gpd.GeoDataFrame(geometry=new_polygons, crs=crs)

# Zapisanie do nowej warstwy SHP w tym samym CRS
output_shapefile = r"C:\Users\ngaje\Desktop\MAGISTERKA\Testmagisterka\1\average.shp"
merged_data.to_file(output_shapefile, driver='ESRI Shapefile')
