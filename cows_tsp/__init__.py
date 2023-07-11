from dataclasses import dataclass
from dotenv import dotenv_values
from more_itertools import chunked
from typing import TypedDict

import googlemaps
import numpy as np

from cows_tsp.cow_reader import get_cows

config = dotenv_values('.env')
gmaps = googlemaps.Client(key=config['GOOGLE_KEY'])

class ResponseDistance(TypedDict):
  text: str
  value: int

class ResponseDuration(TypedDict):
  text: str
  value: int

class ResponseElement(TypedDict):
  status: str
  distance: ResponseDistance
  duration: ResponseDuration

class ResponseRow(TypedDict):
  elements: list[ResponseElement]

class Response(TypedDict):
  status: str
  origin_addresses: list[str]
  destination_addresses: list[str]
  rows: list[ResponseRow]

def extract_data_from_response(response: Response) -> np.ndarray:
  def extract_data_from_row(row: ResponseRow) -> np.ndarray:
    def extract_data_from_element(element: ResponseElement) -> int:
      return element['distance']['value']
    return np.array(list(map(extract_data_from_element, row['elements'])))
  return np.array(list(map(extract_data_from_row, response['rows'])))

def get_cow_matrix(cows):
  cows_batched = list(chunked(cows, 10))
  parts_outer = []
  for origin_batch in cows_batched:
    parts_inner = []
    for destination_batch in cows_batched:
      origin_locations = [cow.location for cow in origin_batch]
      destination_locations = [cow.location for cow in destination_batch]

      response = gmaps.distance_matrix(
        origin_locations,
        destination_locations,
        mode='walking'
      )
      assert(response['status'] == 'OK')

      parts_inner.append(extract_data_from_response(response))
    parts_outer.append(np.concatenate(parts_inner, axis=1))
  return np.concatenate(parts_outer)

def main():
  exclude = [
    "A Midsummer's Eve",
    "Jordan's Pop Art",
    'The Eliot',
    'Gridiron Grazer',
    'Luna the Mooon Cow!',
    'GAIA',
  ]

  start = 38
  cows = [cow for cow in get_cows('cows.txt') if cow.name not in exclude]
  cows = cows[start:] + cows[:start]
  assert(len(cows) == 68)

  """
  matrix = get_cow_matrix(cows)
  with open('distances.npy', 'wb') as data_file:
    np.save(data_file, matrix)
  """

  with open('distances.npy', 'rb') as data_file:
    matrix = np.load(data_file)
  matrix[:, 0] = 0 # don't need to return to the start

  from python_tsp.heuristics import solve_tsp_simulated_annealing
  permutation, distance = solve_tsp_simulated_annealing(matrix, alpha=0.99)

  for i in permutation:
    print(cows[i].name)
  print(f'{distance} meters')
  
if __name__ == '__main__':
  main()
