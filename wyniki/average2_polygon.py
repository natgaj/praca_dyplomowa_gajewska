import geopandas as gpd
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

    for i in range(len(vertices) - 1):
        x_avg = vertices[i][0]
        y_avg = (vertices[i][1] + vertices[i + 1][1]) / 2
        new_vertices.append((x_avg, y_avg))

    new_polygon = Polygon(new_vertices)
    new_polygons.append(new_polygon)

crs = data.crs

merged_data = gpd.GeoDataFrame(geometry=new_polygons, crs=crs)

output_shapefile = r"C:\Users\ngaje\Desktop\MAGISTERKA\Testmagisterka\1\average.shp"
merged_data.to_file(output_shapefile, driver='ESRI Shapefile')
