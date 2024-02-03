# Importowanie modułu os do interakcji z systemem operacyjnym, np. do tworzenia ścieżek dostępu do plików.
import os

# Importowanie biblioteki geopandas, która jest rozszerzeniem pandas umożliwiającym łatwe pracę z danymi przestrzennymi w Pythonie.
import geopandas as gpd

# Importowanie modułu rdp z biblioteki o tej samej nazwie. Moduł ten implementuje algorytm Ramer-Douglas-Peucker do upraszczania geometrii (np. linii lub poligonów) przez redukcję liczby punktów.
from rdp import rdp

# Importowanie klas Polygon i LineString z biblioteki shapely, która służy do manipulacji i analizy danych przestrzennych (planarnych kształtów).
from shapely.geometry import Polygon, LineString

# Importowanie biblioteki numpy, która jest podstawową biblioteką w Pythonie służącą do obliczeń naukowych. Umożliwia ona pracę z wielowymiarowymi tablicami i macierzami oraz zawiera szeroki zakres funkcji matematycznych.
import numpy as np

# Importowanie biblioteki matplotlib.pyplot do tworzenia statycznych, interaktywnych i animowanych wizualizacji w Pythonie. plt jest standardowym aliasem dla tej biblioteki.
import matplotlib.pyplot as plt


# Definicja funkcji repair_geometries, która przyjmuje jeden argument:
# data - GeoDataFrame z biblioteki geopandas zawierający dane przestrzenne.
def repair_geometries(data):
    # Tworzenie głębokiej kopii danych wejściowych, aby uniknąć modyfikacji oryginalnego GeoDataFrame.
    repaired = data.copy()

    # Zastosowanie metody .apply na kolumnie 'geometry' GeoDataFrame.
    # Dla każdego obiektu geometrycznego (geom) w kolumnie 'geometry' wykonuje następującą funkcję lambda.
    repaired['geometry'] = data.geometry.apply(
        lambda geom:
        # Jeśli geometria nie jest poprawna (geom.is_valid zwraca False),
        # stosuje metodę .buffer(0), która jest powszechnie używaną sztuczką do "naprawy" niepoprawnych geometrii.
        # Metoda ta tworzy bufor o zerowym promieniu wokół geometrii, często skutecznie korygując drobne błędy.
        geom.buffer(0) if not geom.is_valid
        # Jeśli geometria jest poprawna, zwraca ją bez zmian.
        else geom
    )

    # Zwraca GeoDataFrame 'repaired' z naprawionymi geometriami.
    return repaired


# Definicja funkcji, która przyjmuje jeden argument:
# polygons - lista lub inny iterowalny zbiór obiektów poligonowych (np. z biblioteki Shapely).
def calculate_perimeter_and_vertices(polygons):
    # Obliczanie sumy długości (obwodu) wszystkich poligonów w przekazanym zbiorze.
    # Używane jest wyrażenie list comprehension wraz z atrybutem .length,
    # który zwraca długość obwodu każdego poligonu.
    perimeter = sum(polygon.length for polygon in polygons)

    # Obliczanie sumy liczby wierzchołków dla wszystkich poligonów w zbiorze.
    # Dla każdego poligonu, polygon.exterior.coords zwraca kolekcję współrzędnych tworzących zewnętrzny obwód poligonu.
    # Funkcja len() jest używana do policzenia liczby tych współrzędnych (wierzchołków) dla każdego poligonu,
    # a następnie sumowane są te liczby dla wszystkich poligonów.
    vertex_count = sum(len(polygon.exterior.coords) for polygon in polygons)

    # Zwracanie obliczonego obwodu i liczby wierzchołków.
    # Funkcja zwraca krotkę dwóch wartości: łącznego obwodu i całkowitej liczby wierzchołków dla przekazanych poligonów.
    return perimeter, vertex_count

# Definicja funkcji, która oblicza zmianę procentową między dwiema wartościami.
# Argumenty funkcji:
# original - wartość początkowa, od której obliczamy zmianę.
# new - nowa wartość, której zmianę porównujemy do wartości początkowej.
def percentage_change(original, new):
    # Wyrażenie warunkowe sprawdza, czy wartość początkowa nie jest równa 0, aby uniknąć dzielenia przez zero.
    # Jeśli wartość początkowa jest różna od zera, wykonane zostaje obliczenie zmiany procentowej.
    # Obliczenie to polega na odjęciu wartości początkowej od nowej wartości, podzieleniu różnicy przez wartość początkową,
    # a następnie pomnożeniu wyniku przez 100, aby uzyskać zmianę wyrażoną w procentach.
    return (new - original) / original * 100 if original != 0 else 0
    # W przypadku, gdy wartość początkowa jest równa 0, zwracana jest wartość 0.
    # Jest to zabezpieczenie przed dzieleniem przez zero, które mogłoby spowodować błąd wykonania.
    # Zwracanie 0 w takim przypadku może być interpretowane jako brak zmiany procentowej lub niemożność jej obliczenia.


# Definicja funkcji write_initial_stats, która przyjmuje dwa argumenty:
# data - GeoDataFrame z biblioteki geopandas zawierający dane przestrzenne,
# stats_file - ścieżka do pliku, do którego mają być zapisane statystyki.
def write_initial_stats(data, stats_file):
    # Wywołanie funkcji calculate_perimeter_and_vertices do obliczenia całkowitego obwodu
    # i liczby wierzchołków dla geometrii zawartych w GeoDataFrame 'data'.
    perimeter, vertices = calculate_perimeter_and_vertices(data.geometry)

    # Obliczenie całkowitej powierzchni wszystkich poligonów w zbiorze danych
    # poprzez zsumowanie wartości w kolumnie 'Area'.
    total_area = data['Area'].sum()

    # Otwarcie pliku określonego przez 'stats_file' w trybie zapisu ('w'),
    # co oznacza, że zawartość pliku zostanie zastąpiona, jeśli plik już istnieje.
    with open(stats_file, 'w') as file:
        # Zapisanie wstępu do pliku.
        file.write("Referencyjne wartości warstwy:\n")
        # Zapisanie całkowitej powierzchni poligonów.
        file.write("Całkowite pole powierzchni: " + str(total_area) + "\n")
        # Zapisanie całkowitego obwodu poligonów.
        file.write("Całkowity obwód: " + str(perimeter) + "\n")
        # Zapisanie całkowitej liczby wierzchołków poligonów.
        file.write("Całkowita liczba wierzchołków: " + str(vertices) + "\n\n")


# Importowanie bibliotek (zakładam, że wcześniej zostały zaimportowane, np. matplotlib.pyplot jako plt, pandas oraz os)

def plot_original_layer(data, image_directory):
    # Tworzenie nowego wykresu i osi z określonym rozmiarem
    fig, ax = plt.subplots(figsize=(100, 100))

    # Rysowanie danych na osiach, kolor wypełnienia to jasnozielony, a kolor krawędzi to czarny
    data.plot(ax=ax, color='lightgreen', edgecolor='black')

    # Ustawienie tytułu wykresu
    ax.set_title('Warstwa wejściowa')

    # Usunięcie etykiet z osi X i Y (zostaną zastąpione pustymi listami, co skutkuje ich niewyświetlaniem)
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # Dodanie etykiet do osi X i Y
    ax.set_xlabel('Współrzędna X')
    ax.set_ylabel('Współrzędna Y')

    # Zapisanie wykresu do pliku JPEG w określonym katalogu. Nazwa pliku to '1Warstwa_wejsciowa.jpeg'
    plt.savefig(os.path.join(image_directory, '1Warstwa_wejsciowa.jpeg'), format='jpeg')

    # Zamknięcie obiektu wykresu, aby zwolnić pamięć
    plt.close()


def chaikin_smoothing(coords, iterations=2):
    # Wykonanie określonej liczby iteracji wygładzania
    for _ in range(iterations):
        new_coords = []  # Lista na nowe współrzędne po wygładzeniu

        # Przetwarzanie każdej pary punktów w ciągu współrzędnych
        for i in range(len(coords)):
            p0 = coords[i]  # Aktualny punkt
            p1 = coords[(i + 1) % len(coords)]  # Następny punkt, z cyklicznym powrotem na początek

            # Obliczenie nowych punktów Q i R przez zastosowanie wag do współrzędnych punktów P0 i P1
            # Q jest bliżej P0, a R jest bliżej P1
            q = [0.75 * p0[0] + 0.25 * p1[0], 0.75 * p0[1] + 0.25 * p1[1]]
            r = [0.25 * p0[0] + 0.75 * p1[0], 0.25 * p0[1] + 0.75 * p1[1]]

            # Dodanie nowych punktów Q i R do listy nowych współrzędnych
            new_coords.extend([q, r])

        # Aktualizacja oryginalnej listy współrzędnych nowymi współrzędnymi po wygładzeniu
        coords = new_coords

    # Zwrócenie wygładzonej listy współrzędnych
    return coords


# Definicja funkcji do wygładzania poligonu przy użyciu algorytmu Chaikina
def smooth_polygon_with_chaikin(polygon):
    # Pobranie współrzędnych zewnętrznego obramowania poligonu i konwersja ich na listę
    exterior_coords = list(polygon.exterior.coords)

    # Wywołanie funkcji chaikin_smoothing z listą współrzędnych obramowania
    # do wygładzenia kształtu poligonu. Funkcja ta jest wywoływana z domyślną liczbą iteracji,
    # chyba że zostanie określona inaczej podczas wywołania.
    smoothed_coords = chaikin_smoothing(exterior_coords)

    # Tworzenie nowego poligonu z wygładzonych współrzędnych i zwrócenie tego poligonu.
    # Nowy poligon ma bardziej zaokrąglone krawędzie w porównaniu do oryginalnego, dzięki zastosowaniu
    # algorytmu wygładzania Chaikina.
    return Polygon(smoothed_coords)

# Połączenie wszystkich poligonów w jedną strukturę, aby ułatwić ich przetwarzanie
merged_polygon = data.unary_union
new_polygons = []  # Lista na nowe, uproszczone poligony

# Sprawdzenie typu geometrycznego połączonego obiektu
if merged_polygon.geom_type == 'Polygon':
    # Jeśli wynik to pojedynczy poligon, umieszczenie go w liście
    merged_polygons = [merged_polygon]
elif merged_polygon.geom_type == 'MultiPolygon':
    # Jeśli wynik to wielopoligon, konwersja na listę pojedynczych poligonów
    merged_polygons = list(merged_polygon.geoms)

# Iteracja przez każdy poligon w liście poligonów połączonych
for polygon in merged_polygons:
    new_vertices = []  # Lista na nowe wierzchołki dla uproszczonego poligonu
    # Konwersja zewnętrznej granicy poligonu na obiekt LineString
    polygon_line = LineString(polygon.exterior.coords)

    # Pomijanie poligonów o małym obszarze (mniejszym niż 40000 jednostek kwadratowych)
    if polygon.area < 40000:
        continue

# Inicjalizacja zmiennej przechowującej odległość wzdłuż linii obramowania poligonu
distance_along_line = 0

# Pętla działa, dopóki odległość wzdłuż linii obramowania nie przekroczy całkowitej długości linii
while distance_along_line <= polygon_line.length:
    # Interpolacja nowego punktu na linii obramowania poligonu w miejscu określonym przez distance_along_line
    new_point = polygon_line.interpolate(distance_along_line)

    # Dodanie nowego punktu do listy nowych wierzchołków
    new_vertices.append(new_point)

    # Zwiększenie distance_along_line o zdefiniowaną odległość między punktami,
    # co pozwala na równomierne rozmieszczenie punktów na linii obramowania
    distance_along_line += point_distance

# Sprawdzenie, czy uzyskano wystarczającą liczbę wierzchołków do utworzenia poligonu
if len(new_vertices) >= 4:
    # Jeśli tak, tworzenie nowego poligonu z uzyskanych wierzchołków
    new_polygon = Polygon(new_vertices)

    # Dodanie nowo utworzonego poligonu do listy nowych poligonów
    new_polygons.append(new_polygon)
else:
    # W przypadku, gdy liczba wierzchołków jest mniejsza niż 4, wyświetlenie komunikatu o błędzie
    # informującego, że nie można utworzyć poligonu z tak małej liczby wierzchołków
    print(f"Zbyt mała liczba wierzchołków dla poligonu: {len(new_vertices)} wierzchołków")

# Lista na uproszczone poligony
simplified_polygons = []

# Przechodzimy przez każdy z nowych poligonów
for polygon in new_polygons:
    # Używamy algorytmu Ramer-Douglas-Peucker (RDP) do uproszczenia kształtu poligonu.
    # Konwertujemy współrzędne zewnętrzne poligonu na tablicę numpy i stosujemy algorytm RDP
    # 'epsilon' jest parametrem decydującym o stopniu uproszczenia; mniejsze wartości oznaczają mniej uproszczeń.
    simplified_vertices = rdp(np.array(polygon.exterior.coords), epsilon=rdp_epsilon)

    # Tworzymy nowy poligon na podstawie uproszczonych wierzchołków
    simplified_polygon = Polygon(simplified_vertices)

    # Wygładzamy poligon za pomocą algorytmu Chaikina
    smoothed_polygon = smooth_polygon_with_chaikin(simplified_polygon)

    # Dodajemy wygładzony poligon do listy uproszczonych poligonów
    simplified_polygons.append(smoothed_polygon)

# Tworzymy GeoDataFrame z biblioteki geopandas, przekazując listę uproszczonych poligonów
# jako geometrie oraz zachowujemy system odniesienia przestrzennego (CRS) danych wejściowych
gdf = gpd.GeoDataFrame(geometry=simplified_polygons, crs=data.crs)


# Obliczenie całkowitego obszaru przed przeprowadzeniem uproszczenia poligonów.
# 'data['Area']' prawdopodobnie odnosi się do kolumny w DataFrame, która przechowuje wartości obszarów dla poszczególnych poligonów.
# Sumujemy te wartości, a następnie zaokrąglamy wynik do dwóch miejsc po przecinku.
total_area_before = round(data['Area'].sum(), 2)

# Obliczenie całkowitego obszaru po uproszczeniu poligonów.
# 'gdf.geometry.area.sum()' oblicza sumę obszarów wszystkich poligonów w GeoDataFrame 'gdf' po ich uproszczeniu.
# Wynik również zaokrąglamy do dwóch miejsc po przecinku.
total_area_after = round(gdf.geometry.area.sum(), 2)

# Obliczenie różnicy w obszarze przed i po uproszczeniu poligonów.
difference = round(total_area_before - total_area_after, 2)

# Obliczenie procentowej zmiany obszaru.
# Funkcja 'percentage_change' prawdopodobnie oblicza, jak duża jest zmiana obszaru w stosunku do wartości początkowej,
# jednak bez dostępu do jej dokładnej implementacji trudno jest podać szczegóły działania.
percentage_change_area = percentage_change(total_area_before, total_area_after)

# Obliczenie obwodu i liczby wierzchołków dla poligonów przed ich uproszczeniem.
# Funkcja 'calculate_perimeter_and_vertices' prawdopodobnie iteruje przez listę poligonów, obliczając ich obwód i licząc wierzchołki.
perimeter_before, vertices_before = calculate_perimeter_and_vertices(new_polygons)

# Powtórzenie obliczenia dla poligonów po uproszczeniu.
perimeter_after, vertices_after = calculate_perimeter_and_vertices(simplified_polygons)

# Obliczenie procentowej zmiany obwodu i liczby wierzchołków przed i po uproszczeniu.
# Te obliczenia dają informację o tym, jak bardzo geometria poligonów została uproszczona.
perimeter_change = percentage_change(perimeter_before, perimeter_after)
vertices_change = percentage_change(vertices_before, vertices_after)

# Otworzenie pliku do zapisu statystyk w trybie dopisywania ('a'), co oznacza, że nowe dane będą dopisywane na końcu pliku,
# zamiast nadpisywać jego zawartość. 'stats_file' to ścieżka do pliku, gdzie mają zostać zapisane statystyki.
with open(stats_file, 'a') as file:
    # Zapisanie wartości parametrów 'rdp_epsilon' i 'point_distance', które były użyte w procesie upraszczania poligonów.
    file.write(f'rdp_epsilon: {rdp_epsilon}, point_distance: {point_distance}\n')

    # Zapisanie łącznego pola powierzchni dla warstwy wejściowej.
    file.write("Łączne pole powierzchni w warstwie wejściowej: " + str(total_area_before) + "\n")

    # Zapisanie łącznego pola powierzchni po zastosowaniu algorytmu Ramer-Douglas-Peucker (RDP) i wygładzeniu.
    file.write("Łączne pole powierzchni w warstwie po zastosowaniu algorytmu RDP: " + str(total_area_after) + "\n")

    # Zapisanie różnicy w polu powierzchni przed i po przeprowadzeniu upraszczania.
    file.write("Różnica w polu powierzchni: " + str(difference) + "\n")

    # Zapisanie zmiany procentowej pola powierzchni.
    file.write("Zmiana procentowa w polu powierzchni: " + str(round(percentage_change_area, 2)) + "%\n")

    # Zapisanie obwodu poligonów przed przeprowadzeniem upraszczania.
    file.write("Obwód przed RDP: " + str(perimeter_before) + "\n")

    # Zapisanie liczby wierzchołków poligonów przed przeprowadzeniem upraszczania.
    file.write("Ilość wierzchołków przed RDP: " + str(vertices_before) + "\n")

    # Zapisanie obwodu poligonów po przeprowadzeniu upraszczania.
    file.write("Obwód po RDP: " + str(perimeter_after) + "\n")

    # Zapisanie liczby wierzchołków poligonów po przeprowadzeniu upraszczania.
    file.write("Ilość wierzchołków po RDP: " + str(vertices_after) + "\n")

    # Zapisanie zmiany procentowej obwodu poligonów.
    file.write("Zmiana procentowa obwodu: " + str(round(perimeter_change, 2)) + "%\n")

    # Zapisanie zmiany procentowej liczby wierzchołków poligonów.
    file.write("Zmiana procentowa liczby wierzchołków: " + str(round(vertices_change, 2)) + "%\n\n")

# Tworzenie nowego wykresu i osi z określonym rozmiarem.
# 'figsize=(100, 100)' określa rozmiar wykresu na 100x100 cali, co jest bardzo duże i może być przydatne
# do uzyskania wysokiej jakości obrazu podczas zapisywania do pliku.
fig, ax = plt.subplots(figsize=(100, 100))

# Rysowanie uproszczonych poligonów na wykresie.
# 'gdf' to GeoDataFrame zawierający uproszczone poligony. Poligony są rysowane kolorem jasnozielonym z zielonymi krawędziami.
gdf.plot(ax=ax, color='lightgreen', edgecolor='green')

# Dodanie na wykresie oryginalnych danych poligonowych dla porównania.
# Używane są do tego dane przed uproszczeniem ('data'), z niewypełnionymi wnętrzami (facecolor='none')
# i szarymi krawędziami przerywanymi (linestyle='--'), aby łatwo odróżnić od uproszczonych poligonów.
data.plot(ax=ax, facecolor='none', edgecolor='grey', linestyle='--', linewidth=1.0)

# Ustawienie tytułu wykresu, który zawiera wartości parametrów użytych do uproszczenia poligonów ('rdp_epsilon' i 'point_distance').
title = f'Poligony_rdp_epsilon_{rdp_epsilon}_point_distance_{point_distance}'
ax.set_title(title)

# Dodanie etykiet do osi X i Y.
ax.set_xlabel('Współrzędna X')
ax.set_ylabel('Współrzędna Y')

# Usunięcie etykiet z osi X i Y, aby wykres był bardziej przejrzysty, zwłaszcza przy dużej ilości danych.
ax.set_xticklabels([])
ax.set_yticklabels([])

# Zapisanie wykresu do pliku JPEG, używając jako nazwy tytułu wykresu.
# 'os.path.join(image_directory, title + '.jpeg')' tworzy pełną ścieżkę do pliku w określonym katalogu.
plt.savefig(os.path.join(image_directory, title + '.jpeg'), format='jpeg')

# Zamknięcie wykresu po zapisaniu, aby zwolnić zasoby.
plt.close()

# Ustawienie ścieżki do pliku shapefile, który będzie używany jako dane wejściowe.
# Plik shapefile zawiera dane przestrzenne, które będą poddane analizie i przetwarzaniu.
input_shapefile = r"C:\Users\ngaje\Desktop\MAGISTERKA\praca_magisterska\Dane_vmap\pisz.shp"

# Wczytanie danych z pliku shapefile do GeoDataFrame za pomocą biblioteki GeoPandas.
# GeoDataFrame 'data' będzie przechowywać dane przestrzenne w postaci, która umożliwia łatwe przetwarzanie i analizę.
data = gpd.read_file(input_shapefile)

# Zmiana układu współrzędnych danych do 'EPSG:3857' (Web Mercator).
# Jest to powszechnie używany układ współrzędnych dla map internetowych, który umożliwia lepszą kompatybilność
# z różnymi narzędziami i platformami do wizualizacji danych przestrzennych.
data = data.to_crs('EPSG:3857')

# Naprawa geometrii w danych przestrzennych.
# Funkcja 'repair_geometries' prawdopodobnie koryguje ewentualne błędy w geometriach, takie jak samoprzecinające się poligony,
# które mogą powodować problemy w dalszym przetwarzaniu. Dokładne działanie tej funkcji zależy od jej implementacji.
data = repair_geometries(data)

# Obliczenie i dodanie do GeoDataFrame kolumny 'Area', która przechowuje wartości powierzchni dla każdego poligonu.
# Obliczenia wykonane są w aktualnym układzie współrzędnych (EPSG:3857), co może być przydatne do analizy wielkości obszarów.
data['Area'] = data.geometry.area

# Ustawienie ścieżki do pliku tekstowego, w którym będą zapisywane statystyki dotyczące przetwarzania danych.
stats_file = r"C:\Users\ngaje\Desktop\MAGISTERKA\praca_magisterska\Wyniki_matplotlib\smoothing_pisz.txt"

# Ustawienie ścieżki do katalogu, w którym będą zapisywane wygenerowane obrazy przedstawiające wyniki analizy.
image_directory = r"C:\Users\ngaje\Desktop\MAGISTERKA\praca_magisterska\Wyniki_matplotlib\smoothing_pisz_rys"

# Ustawienie ścieżki do katalogu, w którym będą zapisywane wyniki analizy w formacie shapefile.
shp_directory = r"C:\Users\ngaje\Desktop\MAGISTERKA\praca_magisterska\Wyniki_matplotlib\smoothing_pisz_shp"

# Sprawdzenie, czy katalogi na obrazy i pliki shapefile (shp) istnieją. Jeśli nie, są one tworzone.
# To zapobiega błędom podczas próby zapisania plików do nieistniejących lokalizacji.
for directory in [image_directory, shp_directory]:
    if not os.path.exists(directory):
        os.makedirs(directory)  # Tworzenie katalogu, jeśli nie istnieje.

# Zapisanie początkowych statystyk danych do pliku. Funkcja 'write_initial_stats' musi być zdefiniowana gdzie indziej.
# Zakłada się, że funkcja ta analizuje dane wejściowe i zapisuje wybrane statystyki do wskazanego pliku statystyk.
write_initial_stats(data, stats_file)

# Tworzenie wizualizacji oryginalnej warstwy danych i zapisanie jej jako obraz.
# Funkcja 'plot_original_layer' również musi być zdefiniowana gdzie indziej.
# Przyjmuje ona dane przestrzenne i ścieżkę do katalogu, gdzie ma zostać zapisany obraz.
plot_original_layer(data, image_directory)

# Pętla wykonująca uproszczenie geometrii poligonów z różnymi parametrami i zapisująca wyniki.
# 'rdp_epsilon' to parametr określający tolerancję błędu dla algorytmu Ramer-Douglas-Peucker, używanego do upraszczania.
# 'point_distance' określa odległość między punktami na uproszczonym poligonie.
for rdp_epsilon in range(50, 1001, 50):
    for point_distance in range(50, 1001, 50):
        # Wywołanie funkcji, która przeprowadza uproszczenie, tworzy wizualizacje, zapisuje statystyki i eksportuje wyniki do plików shapefile.
        # Funkcja ta przyjmuje dane przestrzenne, parametry uproszczenia, ścieżki do plików statystyk, obrazów i plików shapefile.
        create_simplified_polygons_plot_save_stats_and_shp(data, point_distance, rdp_epsilon, stats_file, image_directory, shp_directory)
