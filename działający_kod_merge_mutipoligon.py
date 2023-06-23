#Importowanie niezbędnych modułów geopandas i shapely.geometry.
import geopandas as gpd
from shapely.geometry import Point, Polygon

# Wczytaj warstwę SHP z pliku o podanej ścieżce (plik wejściowy przed generalizcją)
input_shapefile = r"C:\Users\ngaje\Desktop\MAGISTERKA\2\G_COMPARTMENT.shp"
data = gpd.read_file(input_shapefile)

#Połączenie wszystkich poligonów w warstwie wejściowej w jeden poligon.
merged_polygon = data.unary_union

# Tworzenie listy nowych poligonów- (pusta lista, która będzie przechowywać nowe poligony)
new_polygons = []

if merged_polygon.geom_type == 'Polygon':
    merged_polygons = [merged_polygon]
elif merged_polygon.geom_type == 'MultiPolygon':
    merged_polygons = list(merged_polygon.geoms)

# Sprawdzenie typu geometrii połączonego poligonu.
# Jeśli jest to pojedynczy poligon (Polygon), dodaje go do listy merged_polygons.
# Jeśli jest to wielokrotny poligon (MultiPolygon), tworzy listę z podpoligonami.


#Iteracja przez każdy poligon w merged_polygons. Dla każdego poligonu, tworzy nową
# listę new_vertices, przechowującą nowe wierzchołki spełniające warunek odległości większej
# lub równej 100. Następnie tworzy nowy poligon new_polygon na podstawie new_vertices i dodaje
# go do listy new_polygons.

# Zasada działania algorytmu:  usunięcie współrzędnych wierzchołków o odległości mniejszej niż 100m(dowolna liczba).
# Tworzy nową listę wierzchołków poligonu bez wierzchołków o odległości mniejszej niż 100m. Pętla przechodzi przez każdą
# parę sąsiednich wierzchołków i oblicza odległość między nimi za pomocą funkcji Shapely distance().
# Jeśli odległość jest większa lub równa 100m, wierzchołek zostaje dodany do nowej listy nowe_wierzcholki. Dodaje ostatni
# wierzchołek z pierwotnej listy wierzcholki, aby utworzyć zamknięty poligon.
for polygon in merged_polygons:
    new_vertices = []
    vertices = list(polygon.exterior.coords)

    for i in range(len(vertices) - 1):
        p1 = Point(vertices[i])
        p2 = Point(vertices[i + 1])
        distance = p1.distance(p2)

        if distance >= 100: #----> tu należy wprowadzić wartość odległości między wierzchołkami!
            new_vertices.append(vertices[i])

    new_vertices.append(vertices[-1])

    if len(new_vertices) >= 4:  # Sprawdza czy liczba wierzchołków jest wystarczająca
        new_polygon = Polygon(new_vertices)
        new_polygons.append(new_polygon)

# Pobiera informacje o CRS z warstwy wejściowej
crs = data.crs

# Tworzenie nowej ramki danych (GeoDataFrame) na podstawie nowych
# poligonów new_polygons i przypisanie CRS.
merged_data = gpd.GeoDataFrame(geometry=new_polygons, crs=crs)

# Zapsanie do nowej warstwy SHP w tym samym CRS
output_shapefile = r"C:\Users\ngaje\Desktop\MAGISTERKA\Testmagisterka\1\zmodyfikowana_figura17.shp"
merged_data.to_file(output_shapefile, driver='ESRI Shapefile')
