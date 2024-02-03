import geopandas as gpd  # Import biblioteki GeoPandas do pracy z danymi przestrzennymi (GDF)
import numpy as np  # Import biblioteki NumPy do operacji na tablicach
from rdp import rdp  # Import algorytmu Ramer-Douglas-Peucker do upraszczania geometrii
from shapely.geometry import Polygon, LineString, MultiPolygon  # Import klas geometrii


# Definicja funkcji wygładzania Chaikina
def chaikin_smoothing(coords, iterations=2):
    for _ in range(iterations):  # Pętla iteracyjna dla liczby iteracji wygładzania
        new_coords = []  # Lista na nowe współrzędne po wygładzeniu
        for i in range(len(coords) - 1):  # Iteracja przez współrzędne z wyjątkiem ostatniej pary
            p0 = coords[i]  # Punkt początkowy segmentu
            p1 = coords[i + 1]  # Punkt końcowy segmentu
            q = [0.75 * p0[0] + 0.25 * p1[0], 0.75 * p0[1] + 0.25 * p1[1]]  # Obliczenie punktu Q
            r = [0.25 * p0[0] + 0.75 * p1[0], 0.25 * p0[1] + 0.75 * p1[1]]  # Obliczenie punktu R
            new_coords.extend([q, r])  # Dodanie punktów Q i R do listy nowych współrzędnych
        new_coords.append(new_coords[0])  # Zamknięcie poligonu przez dodanie pierwszego punktu na końcu listy
        coords = new_coords  # Aktualizacja listy współrzędnych do następnej iteracji
    return coords  # Zwrócenie wygładzonej listy współrzędnych


# Wczytywanie danych przestrzennych z pliku shapefile
input_shapefile = r"C:\Users\ngaje\Desktop\MAGISTERKA\praca_magisterska\Dane_vmap\lastest2.shp"
data = gpd.read_file(input_shapefile)  # Użycie GeoPandas do wczytania danych

# Konwersja danych do określonego układu współrzędnych
projected_crs = 'EPSG:32634'  # Definicja układu współrzędnych
data = data.to_crs(projected_crs)  # Konwersja danych do układu EPSG:3857

# Obliczenie i dodanie kolumny 'Area' z powierzchnią każdego poligonu
data['Area'] = data.geometry.area

# Wyświetlenie sumy powierzchni wszystkich poligonów w danych wejściowych
print("Całkowita powierzchnia w warstwie wejściowej:", round(data['Area'].sum(), 2))

# Scalanie wszystkich poligonów w jeden obiekt
merged_polygon = data.unary_union

# Sprawdzenie typu zwróconego obiektu i odpowiednia jego obsługa
if isinstance(merged_polygon, Polygon):  # Jeśli wynikiem jest pojedynczy poligon
    merged_polygons = [merged_polygon]  # Umieszczenie poligonu w liście
elif isinstance(merged_polygon, MultiPolygon):  # Jeśli wynikiem są wielokrotne poligony
    merged_polygons = list(merged_polygon.geoms)  # Konwersja MultiPolygon na listę poligonów
else:  # W przypadku innego typu obiektu
    raise TypeError("Typ geometrii nie jest Polygonem ani MultiPolygonem.")  # Wygenerowanie wyjątku

new_polygons = []  # Lista na nowe, przetworzone poligony

# Przetwarzanie każdego poligonu z listy
for polygon in merged_polygons:
    if polygon.area < 40000:  # Pominięcie poligonów o powierzchni mniejszej niż 400000
        continue  # Przejście do kolejnego poligonu

    # Konwersja obrysu poligonu na obiekt LineString
    polygon_line = LineString(polygon.exterior.coords)

    # Ustawienie odległości między punktami do interpolacji
    point_distance = 100  # Ustawienie odległości między nowymi punktami

    # Interpolacja punktów wzdłuż linii obrysu
    distance_along_line = 0  # Zmienna do śledzenia przebytej odległości wzdłuż linii
    new_vertices = []  # Lista na nowe punkty
    while distance_along_line <= polygon_line.length:  # Dopóki nie przejdziemy całej długości linii
        new_point = polygon_line.interpolate(distance_along_line)  # Interpolacja nowego punktu
        new_vertices.append((new_point.x, new_point.y))  # Dodanie współrzędnych nowego punktu do listy
        distance_along_line += point_distance  # Zwiększenie przebytej odległości o zdefiniowaną wartość

    # Użycie algorytmu RDP do uproszczenia geometrii
    simplified_vertices = rdp(new_vertices, epsilon=50)  # Uproszczenie wierzchołków z zachowaniem kształtu

    # Wygładzenie uproszczonych wierzchołków przy użyciu algorytmu Chaikina
    smoothed_vertices = chaikin_smoothing(simplified_vertices, iterations=10)  # Wygładzenie wierzchołków

    # Utworzenie nowego poligonu z wygładzonych wierzchołków
    simplified_polygon = Polygon(smoothed_vertices)
    new_polygons.append(simplified_polygon)  # Dodanie nowego poligonu do listy

# Utworzenie GeoDataFrame dla uproszczonych i wygładzonych poligonów
crs = data.crs  # Pobranie układu współrzędnych z danych wejściowych
merged_data = gpd.GeoDataFrame(geometry=new_polygons, crs=crs)  # Utworzenie GeoDataFrame

# Obliczenie powierzchni dla przetworzonych danych
merged_data['Area'] = merged_data.geometry.area  # Dodanie kolumny 'Area' z powierzchnią każdego poligonu

# Wyświetlenie sumy powierzchni wszystkich poligonów po przetworzeniu
print("Całkowita powierzchnia w warstwie po przetworzeniu:", round(merged_data['Area'].sum(), 2))

# Zapisanie przetworzonych danych do nowego pliku shapefile
output_shapefile = r"C:\Users\ngaje\Desktop\MAGISTERKA\praca_magisterska\Wyniki_arcgis\4.shp"
merged_data.to_file(output_shapefile, driver='ESRI Shapefile')  # Zapis

# Informacja o zakończeniu przetwarzania i zapisie danych
print("Przetwarzanie zakończone. Wyniki zapisano w:", output_shapefile)
