import geopandas as gpd
from shapely.geometry import Point, Polygon

# Ścieżka do pliku wejściowego
input_shapefile = r"C:\Users\ngaje\Desktop\MAGISTERKA\2\G_COMPARTMENT.shp"
data = gpd.read_file(input_shapefile)

# Połącz wszystkie poligony w jeden
merged_polygon = data.unary_union

new_polygons = []

# Sprawdź typ połączonego poligonu
if merged_polygon.geom_type == 'Polygon':
    merged_polygons = [merged_polygon]
elif merged_polygon.geom_type == 'MultiPolygon':
    merged_polygons = list(merged_polygon.geoms)

# Przejdź przez wszystkie poligony
for polygon in merged_polygons:
    new_vertices = []
    vertices = list(polygon.exterior.coords)

    # Jeśli poligon ma mniej niż 10 wierzchołków
    if len(vertices) < 10:
        # Przejdź przez wierzchołki
        for i in range(len(vertices) - 1):
            # Wybierz co drugi wierzchołek
            if i % 2 == 0:
                x_avg = vertices[i][0]
                y_avg = (vertices[i][1] + vertices[i + 1][1]) / 2
                new_vertices.append((x_avg, y_avg))
    else:
        # Jeśli poligon ma 10 lub więcej wierzchołków
        for i in range(len(vertices) - 1):
            # Wybierz co dziesiąty wierzchołek
            if i % 10 == 0:
                x_avg = vertices[i][0]
                y_avg = (vertices[i][1] + vertices[i + 1][1]) / 2
                new_vertices.append((x_avg, y_avg))

    # Jeśli nowy poligon ma co najmniej 4 wierzchołki, dodaj go do listy
    if len(new_vertices) >= 4:
        new_polygon = Polygon(new_vertices)
        new_polygons.append(new_polygon)

crs = data.crs

# Utwórz nową ramkę danych przestrzennych
merged_data = gpd.GeoDataFrame(geometry=new_polygons, crs=crs)

# Ścieżka do pliku wyjściowego
output_shapefile = r"C:\Users\ngaje\Desktop\MAGISTERKA\Testmagisterka\1\average10_2.shp"
merged_data.to_file(output_shapefile, driver='ESRI Shapefile')

