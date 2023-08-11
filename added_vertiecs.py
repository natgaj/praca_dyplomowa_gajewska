import geopandas as gpd
from shapely.geometry import Point, Polygon, LineString

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

    if polygon.area < 100000:  # Usuwa poligony o powierzchni mniejszej niż 10000
        continue

    for vertex in vertices:
        new_vertices.append(vertex)
        p = Point(vertex)

        if p.within(polygon):  # Sprawdza, czy punkt znajduje się wewnątrz połączonego poligonu
            line_segment = LineString([polygon.centroid, p])

            distance_along_segment = 0
            while distance_along_segment < line_segment.length:
                new_point = line_segment.interpolate(distance_along_segment)
                new_vertices.append((new_point.x, new_point.y))
                distance_along_segment += 1000

    if len(new_vertices) >= 4:  # Sprawdza, czy liczba wierzchołków jest wystarczająca
        new_polygon = Polygon(new_vertices)
        new_polygons.append(new_polygon)

crs = data.crs

merged_data = gpd.GeoDataFrame(geometry=new_polygons, crs=crs)

output_shapefile = r"C:\Users\ngaje\Desktop\MAGISTERKA\testmagisterka2\warstwytestowe2\dodane1000.shp"
merged_data.to_file(output_shapefile, driver='ESRI Shapefile')

# Wyświetl łączne pole powierzchni w warstwie wejściowej
total_area_before = round(data.geometry.area.sum(), 2)
print("Łączne pole powierzchni w warstwie wejściowej:", total_area_before)

# Wyświetl łączne pole powierzchni w warstwie po zastosowaniu algorytmów
total_area_after = round(merged_data.geometry.area.sum(), 2)
print("Łączne pole powierzchni w warstwie po zastosowaniu algorytmów:", total_area_after)

# Wyświetl różnicę między łącznym polem powierzchni przed i po zastosowaniu algorytmów
difference = round(total_area_before - total_area_after, 2)
print("Różnica w polu powierzchni po zastosowaniu algorytmów:", difference)

# Oblicz procentową zmianę poligonu w warstwie wyjściowej w porównaniu do warstwy wejściowej
percentage_change = (difference / total_area_before) * 100
print("Zmniejszenie poligonu w warstwie wyjściowej w porównaniu do warstwy wejściowej: {}%".format(round(percentage_change, 2)))
