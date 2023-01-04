import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
import branca
import folium


def geotag(latitude, longitude):

    lat_min, long_min = 52.486692, 13.270979
    lat_max, long_max = 52.520097, 13.385214
    lat_highway, long_highway = 52.510075, 13.300602
    lat_tun_min, long_tun_max = 52.494548, 13.286002    # Tunnel entrance
    lat_tun_max, long_tun_min = 52.496066, 13.283980    # Tunnel exit
    long_park = 13.336380

    not_ = np.logical_not
    and_ = np.logical_and

    def between(min_val, val, max_val):
        return and_(min_val <= val, val < max_val)

    in_box = and_(between(lat_min, latitude, lat_max), between(long_min, longitude, long_max))
    out_box = not_(in_box)
    in_tunnel = and_(between(lat_min, latitude, lat_tun_max),
                     between(long_min, longitude, long_tun_max))
    in_park = and_(in_box, long_park <= longitude)
    in_avenue = and_(between(lat_highway, latitude, lat_max),
                     between(long_min, longitude, long_park))
    in_resi = and_(between(lat_min, latitude, lat_highway),
                   between(long_highway, longitude, long_park))
    in_hw = and_(between(lat_min, latitude, lat_highway),
                 between(long_min, longitude, long_highway),
                 not_(in_tunnel))

    conds = [out_box, in_avenue, in_park, in_resi, in_tunnel, in_hw, ]
    choices = ["UNKNOWN", "Avenue", "Park", "Residential", "Tunnel", "Highway"]

    return np.select(conds, choices)


def plot_tiles(latitudes, longitudes, values, tile_size, caption, opacity_value=0.7,
               shape='rectangle', colormap=None, cmax=None, aggfunc='mean',):
    center_coords = ((min(latitudes) + max(latitudes)) / 2, (min(longitudes) + max(longitudes)) / 2)
    map_ = folium.Map(location=center_coords, zoom_start=14, control_scale=True)

    # use approximate tile sizes, that assumes the earth is a perfect spere. This should be accurate for small areas.
    earth_radius = 6378137
    tile_size_lat = np.degrees(tile_size / earth_radius)
    tile_size_long = np.degrees(tile_size / (earth_radius * np.cos(np.radians(center_coords[0]))))

    df = pd.DataFrame({'latitude': latitudes, 'longitude': longitudes, 'value': values})
    df['latitude'] = round(df['latitude'] / tile_size_lat) * tile_size_lat
    df['longitude'] = round(df['longitude'] / tile_size_long) * tile_size_long
    df = df.groupby(['latitude', 'longitude']).aggregate(aggfunc).reset_index()

    if not cmax:
        cmax = max(df['value'])
    if colormap is None:
        cm = branca.colormap.LinearColormap(['blue', 'red'], vmin=0, vmax=cmax)
    else:
        cm = colormap
    if shape == 'rectangle':
        def map_shape(s):
            return folium.Rectangle([(s['latitude'] - tile_size_lat / 2, s['longitude'] - tile_size_long / 2),
                                     (s['latitude'] + tile_size_lat / 2, s['longitude'] + tile_size_long / 2)],
                                    weight=0, fill=True, fill_color=cm(s['value']), fill_opacity=opacity_value
                                    )
    elif shape == 'circle':
        def map_shape(s):
            radius = tile_size / np.sqrt(2)
            return folium.Circle(location=(s['latitude'], s['longitude']),
                                 radius=radius, weight=0, fill=True,
                                 fill_color=cm(s['value']), fill_opacity=opacity_value
                                 )
    else:
        raise ValueError("Unknown shape")

    for index, row in df.iterrows():
        map_shape(row).add_to(map_)
    cm.caption = caption
    map_.add_child(cm)
    return map_


def spherical_coords_to_planar_coords(latitude, longitude, ref_latitude, ref_longitude):
    x = 111111 * np.cos(np.radians(latitude)) * (longitude - ref_longitude)
    y = -111111 * (latitude - ref_latitude)
    return x, y


def generate_reference_dataset(df, location_window_size=10):
    latitude = df['Latitude'].rolling(location_window_size, center=True, min_periods=1).mean()
    longitude = df['Longitude'].rolling(location_window_size, center=True, min_periods=1).mean()
    ref_latitude = (min(latitude) + max(latitude)) / 2
    ref_longitude = (min(longitude) + max(longitude)) / 2
    x, y = spherical_coords_to_planar_coords(latitude, longitude, ref_latitude, ref_longitude)
    
    diff_x = x.diff()
    diff_y = y.diff()
    diff = np.sqrt(diff_x ** 2 + diff_y ** 2)
    distance_traveled = diff.cumsum()
    distance_traveled.iloc[0] = 0  # First entry of cumsum is NaN by default
    
    return pd.DataFrame({'x': x, 'y': y, 'Pos in Ref Round': distance_traveled}), ref_latitude, ref_longitude


def add_pos_in_ref_round(df, df_ref, ref_latitude, ref_longitude, cutoff_distance=20):
    x, y = spherical_coords_to_planar_coords(df['Latitude'], df['Longitude'], ref_latitude, ref_longitude)
    dists = cdist(np.array(df_ref[['x', 'y']]), np.array([x, y]).T)
    dist_traveled = df_ref['Pos in Ref Round'].iloc[np.argmin(dists, 0)]
    dist_traveled.loc[np.amin(dists, 0) > cutoff_distance] = np.nan
    df['Pos in Ref Round'] = dist_traveled.values

    
def write_meta(df_xy, filename, index=None):
    nancount = df_xy.isna().sum()
    nanperc = 100-((nancount/len(df_xy))*100)  # percent of available data
    zerocount = (df_xy == 0).sum(axis=0)  # how many zeros per col
    nanmeta = pd.concat([df_xy.dtypes, nancount, nanperc], axis=1)
    nanmeta = pd.concat([nanmeta, zerocount], axis=1)
    nanmeta.columns = ['dtype', 'Nancount', 'DataPerc', 'Zerocount']
    stats = df_xy.describe().T
    meta_df = pd.concat([nanmeta, stats], axis=1)
    if index is None:
        df_index = df_xy
    else:
        df_index = df_xy.set_index(index)
    df_index = df_index.sort_index().index
    index_row = pd.DataFrame({'dtype': [str(df_index.dtype)], 'Nancount': 0, 'DataPerc': 100.0, 'Zerocount': 0,
                              'count': len(df_index), 'min': df_index[0], 'max': df_index[-1]},
                             index=[df_index.name])
    meta_df = pd.concat([meta_df, index_row])
    meta_df.to_csv(filename)
