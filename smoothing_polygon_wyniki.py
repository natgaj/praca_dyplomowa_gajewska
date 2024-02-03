# import bibliotek
import os
import geopandas as gpd
from rdp import rdp
from shapely.geometry import Polygon, LineString
import numpy as np
import matplotlib.pyplot as plt

# Naprawa niepoprawnych geometrii poligonów.
def repair_geometries(data):
    repaired = data.copy()
    repaired['geometry'] = data.geometry.apply(lambda geom: geom.buffer(0) if not geom.is_valid else geom)
    return repaired

# Obliczanie obwodu i liczby wierzchołków dla poligonów.
def calculate_perimeter_and_vertices(polygons):
    perimeter = sum(polygon.length for polygon in polygons)
    vertex_count = sum(len(polygon.exterior.coords) for polygon in polygons)
    return perimeter, vertex_count

# Obliczanie zmiany procentowej między dwoma wartościami.
def percentage_change(original, new):
    return (new - original) / original * 100 if original != 0 else 0

# Zapisywanie początkowych statystyk do pliku.
def write_initial_stats(data, stats_file):
    perimeter, vertices = calculate_perimeter_and_vertices(data.geometry)
    total_area = data['Area'].sum()
    with open(stats_file, 'w') as file:
        file.write("Referencyjne wartości warstwy:\n")
        file.write("Całkowite pole powierzchni: " + str(total_area) + "\n")
        file.write("Całkowity obwód: " + str(perimeter) + "\n")
        file.write("Całkowita liczba wierzchołków: " + str(vertices) + "\n\n")

# Tworzenie wizualizacji warstwy wejściowej.
def plot_original_layer(data, image_directory):
    fig, ax = plt.subplots(figsize=(100, 100))
    data.plot(ax=ax, color='lightgreen', edgecolor='black')
    ax.set_title('Warstwa wejściowa')
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_xlabel('Współrzędna X')
    ax.set_ylabel('Współrzędna Y')
    plt.savefig(os.path.join(image_directory, '1Warstwa_wejsciowa.jpeg'), format='jpeg')
    plt.close()

# Wygładzanie poligonów za pomocą metody Chaikina.
def chaikin_smoothing(coords, iterations=2): #<------- ile iteracji służących do wygładzania ( im większa liczba tym bardziej wygłądzone poligony)
    for _ in range(iterations):
        new_coords = []
        for i in range(len(coords)):
            p0 = coords[i]
            p1 = coords[(i + 1) % len(coords)]  # Wrap around at the end
            q = [0.75 * p0[0] + 0.25 * p1[0], 0.75 * p0[1] + 0.25 * p1[1]]
            r = [0.25 * p0[0] + 0.75 * p1[0], 0.25 * p0[1] + 0.75 * p1[1]]
            new_coords.extend([q, r])
        coords = new_coords
    return coords

# Utworzenie uproszczonego poligonu z wygładzeniem Chaikina.
def smooth_polygon_with_chaikin(polygon):
    exterior_coords = list(polygon.exterior.coords)
    smoothed_coords = chaikin_smoothing(exterior_coords)
    return Polygon(smoothed_coords)

# Główna funkcja do tworzenia uproszczonych poligonów, zapisywania statystyk i generowania wizualizacji.
def create_simplified_polygons_plot_save_stats_and_shp(data, point_distance, rdp_epsilon, stats_file, image_directory, shp_directory):
    merged_polygon = data.unary_union
    new_polygons = []

    if merged_polygon.geom_type == 'Polygon':
        merged_polygons = [merged_polygon]
    elif merged_polygon.geom_type == 'MultiPolygon':
        merged_polygons = list(merged_polygon.geoms)

    for polygon in merged_polygons:
        new_vertices = []
        polygon_line = LineString(polygon.exterior.coords)

        if polygon.area < 40000:
            continue

        distance_along_line = 0
        while distance_along_line <= polygon_line.length:
            new_point = polygon_line.interpolate(distance_along_line)
            new_vertices.append(new_point)
            distance_along_line += point_distance

        if len(new_vertices) >= 4:
            new_polygon = Polygon(new_vertices)
            new_polygons.append(new_polygon)
        else:
            print(f"Zbyt mała liczba wierzchołków dla poligonu: {len(new_vertices)} wierzchołków")

    simplified_polygons = []
    for polygon in new_polygons:
        simplified_vertices = rdp(np.array(polygon.exterior.coords), epsilon=rdp_epsilon)
        simplified_polygon = Polygon(simplified_vertices)
        smoothed_polygon = smooth_polygon_with_chaikin(simplified_polygon)
        simplified_polygons.append(smoothed_polygon)

    gdf = gpd.GeoDataFrame(geometry=simplified_polygons, crs=data.crs)

    total_area_before = round(data['Area'].sum(), 2)
    total_area_after = round(gdf.geometry.area.sum(), 2)
    difference = round(total_area_before - total_area_after, 2)
    percentage_change_area = percentage_change(total_area_before, total_area_after)

    perimeter_before, vertices_before = calculate_perimeter_and_vertices(new_polygons)
    perimeter_after, vertices_after = calculate_perimeter_and_vertices(simplified_polygons)
    perimeter_change = percentage_change(perimeter_before, perimeter_after)
    vertices_change = percentage_change(vertices_before, vertices_after)

    with open(stats_file, 'a') as file:
        file.write(f'rdp_epsilon: {rdp_epsilon}, point_distance: {point_distance}\n')
        file.write("Łączne pole powierzchni w warstwie wejściowej: " + str(total_area_before) + "\n")
        file.write("Łączne pole powierzchni w warstwie po zastosowaniu algorytmu RDP: " + str(total_area_after) + "\n")
        file.write("Różnica w polu powierzchni: " + str(difference) + "\n")
        file.write("Zmiana procentowa w polu powierzchni: " + str(round(percentage_change_area, 2)) + "%\n")
        file.write("Obwód przed RDP: " + str(perimeter_before) + "\n")
        file.write("Ilość wierzchołków przed RDP: " + str(vertices_before) + "\n")
        file.write("Obwód po RDP: " + str(perimeter_after) + "\n")
        file.write("Ilość wierzchołków po RDP: " + str(vertices_after) + "\n")
        file.write("Zmiana procentowa obwodu: " + str(round(perimeter_change, 2)) + "%\n")
        file.write("Zmiana procentowa liczby wierzchołków: " + str(round(vertices_change, 2)) + "%\n\n")

    fig, ax = plt.subplots(figsize=(100, 100))
    gdf.plot(ax=ax, color='lightgreen', edgecolor='green')
    data.plot(ax=ax, facecolor='none', edgecolor='grey', linestyle='--', linewidth=1.0)
    title = f'Poligony_rdp_epsilon_{rdp_epsilon}_point_distance_{point_distance}'
    ax.set_title(title)
    ax.set_xlabel('Współrzędna X')
    ax.set_ylabel('Współrzędna Y')
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    plt.savefig(os.path.join(image_directory, title + '.jpeg'), format='jpeg')
    plt.close()

    shp_file_path = os.path.join(shp_directory, title + '.shp')
    gdf.to_file(shp_file_path, driver='ESRI Shapefile')

# Przygotowanie danych wejściowych i parametrów.
input_shapefile = r"C:\Users\ngaje\Desktop\MAGISTERKA\praca_magisterska\Dane_vmap\lastest2.shp"
data = gpd.read_file(input_shapefile)
data = data.to_crs('EPSG:32634') # ukąłd współrzędnych
data = repair_geometries(data)
data['Area'] = data.geometry.area

# Lokalizacje plików wyjściowych.
stats_file = r"C:\Users\ngaje\Desktop\MAGISTERKA\praca_magisterska\Wyniki_matplotlib\smoothing_pisz13.txt"
image_directory = r"C:\Users\ngaje\Desktop\MAGISTERKA\praca_magisterska\Wyniki_matplotlib\smoothing_pisz_rys13"
shp_directory = r"C:\Users\ngaje\Desktop\MAGISTERKA\praca_magisterska\Wyniki_matplotlib\smoothing_pisz_shp13"

# Sprawdzenie istnienia katalogów i ich utworzenie w razie potrzeby.
for directory in [image_directory, shp_directory]:
    if not os.path.exists(directory):
        os.makedirs(directory)

write_initial_stats(data, stats_file)
plot_original_layer(data, image_directory)

# Iteracja przez różne wartości parametrów dla algorytmu uproszczenia i wygładzenia.
#                     (od../ do../ co ile)
for rdp_epsilon in range(50, 1001, 50):
    for point_distance in range(50, 1001, 50):
        create_simplified_polygons_plot_save_stats_and_shp(data, point_distance, rdp_epsilon, stats_file, image_directory, shp_directory)
