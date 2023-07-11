from dataclasses import dataclass
import re

@dataclass
class Cow():
  name: str
  location: tuple[float, float]

def get_cows(filename='cows.txt'):
  cow_regex = re.compile(r'(.*) \((.*),(.*)\)')
  with open(filename) as cow_file:
    for cow in cow_file:
      match = cow_regex.match(cow)
      assert match is not None
      name, lat_s, lon_s = match.groups()
      lat = float(lat_s)
      lon = float(lon_s)
      yield Cow(name, (lat, lon))

