import geopandas as gpd
import numpy as np
from rdp import rdp
from shapely.geometry import Point, Polygon

input_shapefile = r"C:\Users\ngaje\Desktop\MAGISTERKA\2\G_COMPARTMENT.shp"
data = gpd.read_file(input_shapefile)

merged_polygon = data.unary_union

new_polygons = []

if merged_polygon.geom_type == 'Polygon':
    merged_polygons = [merged_polygon]
elif merged_polygon.geom_type == 'MultiPolygon':
    merged_polygons = list(merged_polygon.geoms)

for polygon in merged_polygons:
    new_vertices = []
    vertices = list(polygon.exterior.coords)

    if polygon.area < 5000:  # Usuwa poligony o powierzchni mniejszej niż x
        continue

    simplified_vertices = rdp(np.array(vertices), epsilon=50) # epsilon to minimalna wartość jaką muszą wynosić odległości w algorytmie

    if len(simplified_vertices) >= 4:  # Sprawdza czy liczba wierzchołków jest wystarczająca
        new_polygon = Polygon(simplified_vertices)
        new_polygons.append(new_polygon)

crs = data.crs

merged_data = gpd.GeoDataFrame(geometry=new_polygons, crs=crs)

output_shapefile = r"C:\Users\ngaje\Desktop\MAGISTERKA\testmagisterka2\warstwytestowe\rdp_polygon3.shp"
merged_data.to_file(output_shapefile, driver='ESRI Shapefile')
