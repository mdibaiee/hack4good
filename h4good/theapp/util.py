import csv
from collections import OrderedDict
import struct

from django.conf import settings
import pycountry


def convert_country_code(alpha3):
    country = pycountry.countries.get(alpha3=alpha3)
    return country.alpha2

cols_to_replace = {
    'Country Name,Country'
}


def get_columns(reader):
    next(reader)
    next(reader)
    return [i.lower().replace(" ", "_") for i in next(reader)]


def _transorm(a, b, ab_diff, x_diff, x_min, value):
    new_value = a + ((ab_diff) / (x_diff)) * (value - x_min)
    new_value = abs(b - new_value) * 2.5
    new_value = '#%02x%02x%02x' % (new_value, new_value, new_value)
    return new_value


def to_color_map_list(_list, a=0, b=50):
    ab_diff = b - a
    x_min = min(_list)
    x_max = max(_list)
    x_diff = x_max - x_min
    res = []
    for i in _list:
        val = a + ((ab_diff) / (x_diff)) * (i - x_min)
        res.append(val)
    return res


def to_color_map(_dict, a=0, b=100):
    values = _dict.values()
    if not values:
        return {}

    ab_diff = b - a
    x_min = min(values)
    x_max = max(values)
    x_diff = x_max - x_min

    for k, v in _dict.items():
        _dict[k] = _transorm(a, b, ab_diff, x_diff, x_min, v)

    return _dict


def read_file(fname):
    items = []
    with open(fname, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        header = get_columns(reader)

        for count, row in enumerate(reader):
            item = dict(zip(header, row))

            try:
                country_code = item['country_code']
                item['country_code'] = \
                    convert_country_code(country_code).upper()
            except KeyError:
                pass  # Country not found

            items.append(item)

    return items


def get_data(fname, year):
    # settings.CO2_FILE
    fpath = settings.DATA_FILES[fname]
    result = read_file(fname=fpath)

    data = {i['country_code']: float(i[year])
            for i in result if i.get(year)}

    data = to_color_map(data)
    return data
    # worldmap_chart = pygal.Worldmap()
    # worldmap_chart.title = 'C02'
    # worldmap_chart.add('Year {}'.format(year), data)
    # worldmap_chart.render_to_file("{}.svg".format(year))


def _filter_years(_dict):
    _dict.pop("indicator_code")
    _dict.pop("country_name")
    return {k: v for k, v in _dict.items() if k.isdigit() and v}


def get_data_by_country(fname, country):
    fpath = settings.DATA_FILES[fname]
    data = read_file(fname=fpath)
    data = {i['country_code']: _filter_years(i)
            for i in data if i['country_code'] == country}

    data = data[country]
    data = OrderedDict(data).values()
    data = [float(i) for i in data]
    data = to_color_map_list(data)
    return data
