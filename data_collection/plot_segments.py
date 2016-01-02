import json
import requests
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes, mark_inset


def get_access_token():
    with open('./.strava.json') as f:
        data = json.loads(f.read())
        access_token = data["TOKEN"]
    return access_token


def get_segment_info(segments):
    header =  {'Authorization' : 'Bearer %s' % get_access_token()}
    url = 'https://www.strava.com/api/v3/segments/{}'
    segment_info = [requests.get(url.format(segment), headers=header).json() for segment in segments]
    return segment_info


def get_np_array_seg_coords(seg_info):
    lats, lons = [], []
    for seg in seg_info:
        lats.append(seg['start_latitude'])
        lons.append(seg['start_longitude'])
    return np.array(lats), np.array(lons)


def plot_us(lats, lons, save_name=None):
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111)
    big_map = Basemap(resolution='h',
                      lat_0=36, lon_0=-107.5,
                      llcrnrlat=32, llcrnrlon=-125,
                      urcrnrlat=43, urcrnrlon=-110)
    big_map.drawcoastlines()
    big_map.drawstates()
    big_map.drawcountries()
    big_map.drawmapboundary(fill_color='#7777ff')
    big_map.fillcontinents(color='#ddaa66', lake_color='#7777ff', zorder=0)
    x, y = big_map(lons, lats)
    big_map.plot(x[0], y[0], 'ro', markersize=2)

    axins = zoomed_inset_axes(ax, 20, loc=1)
    ll_lat, ll_lon = 37.8, -122.78
    ur_lat, ur_lon = 38.08, -122.43

    axins.set_xlim(ll_lon, ur_lon)
    axins.set_ylim(ur_lon, ur_lat)

    small_map = Basemap(resolution='h',
                        llcrnrlat=ll_lat, llcrnrlon=ll_lon,
                        urcrnrlat=ur_lat, urcrnrlon=ur_lon,
                        ax=axins)
    small_map.drawcoastlines()
    small_map.drawmapboundary(fill_color='#7777ff')
    small_map.fillcontinents(color='#ddaa66', lake_color='#7777ff', zorder=0)
    x, y = small_map(lons, lats)
    small_map.plot(x, y, 'ro', markersize=3)

    mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="0.5")
    if save_name: 
        fig.savefig(save_name)


def make_dat_map(segments):
    segment_info = get_segment_info(segments)
    lats, lons = get_np_array_seg_coords(segment_info)
    


if __name__ == '__main__':
    segments = {125, 5642079, 5857327, 4793848, 6048743, 118, 3305098, 356635, 4173351, 4062646, 
                640981, 6135256, 1173191, 4783121, 1723, 6366843, 8429549, 7481858, 651728, 1521, 
                4259807, 6875972, 5611730, 2707292, 7883627, 622149, 2451142, 5836703, 2858097,
                634332, 1077, 8411114, 881888, 3545515, 5099924, 3066267, 3066267, 934409, 633435,
                1003240, 866902, 835833, 8042617, 8727433, 4599878, 6325954, 1759580, 1105154, 
                806005, 1451654, 7531032, 4779241, 2435434, 841251, 2958707, 9008146, 2188435, 
                2627, 6838822, 5079282, 8594904, 7615757, 7615757, 2350753, 2687319, 2350791, 
                2339624, 2687221, 8727940, 844654, 1213534, 5831003, 5134503, 8050750, 798887, 
                7074191, 975395, 612159, 7969432, 1745022, 5292307, 180, 6768781, 5292307, 
                4178476, 925819, 925819, 6173812, 6458467, 4367683, 821934, 866323, 8800675, 
                666315, 2665113, 7186902, 6546684, 2234914, 747045, 8239228, 905184, 3200333, 
                1329495, 814196, 991174, 852755, 8692386, 8285294, 3559004, 6478150, 1042514,
                774591, 351211}
    #make_dat_map(segments)
