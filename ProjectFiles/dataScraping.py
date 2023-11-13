"""
Data collection script:
This data collection script uses OpenStreetMap (OMS) which is an open source API that is free
for public use.

The script is implemented based on this tutorial https://github.com/vaclavdekanovsky/data-analysis-in-examples/blob/master/Maps/Driving%20Distance/Driving%20Distance%20between%20two%20places.ipynb
section "Distances between multiple cities and optimal route".

The initial dataset was obtained from https://simplemaps.com/data/us-cities. The spreadsheet contains a list of cities based on US Census, and
contains coordinates data (longitude and latitude). To make the database relevant to the project, we narrow down the list of cities to
the New England region, and selected cities which has more than 50,000 people. The final result contains 47 cities.
"""
import pandas as pd  # for data manipulation
import requests  # for calling OMS api
import json  # for processing JSON objects


def get_distance(point1: dict, point2: dict) -> tuple:
    """Gets distance between two points en route using http://project-osrm.org/docs/v5.10.0/api/#nearest-service"""

    url = f"""http://router.project-osrm.org/route/v1/driving/{point1["lon"]},{point1["lat"]};{point2["lon"]},{point2["lat"]}?overview=false&alternatives=false"""
    r = requests.get(url)

    # get the distance from the returned values
    route = json.loads(r.content)["routes"][0]
    return route["distance"]

def get_all_distance(excel_file_with_extension):
    """Function to get distance for all possible combinations of cities. Data for both directions are collected. Note
    that the output of this function saves to an Excel sheet titled "distance_data.xlsx"."""
    # import Excel sheet containing coordinates data for the selected cities
    df = pd.read_excel(excel_file_with_extension)
    # iterate for each city, get the distance data for that city to other cities
    dist_array = []
    for i, r in df.iterrows():
        point1 = {"lat": r["lat"], "lon": r["lon"]}
        for j, o in df[df.index != i].iterrows():
            point2 = {"lat": o["lat"], "lon": o["lon"]}
            dist = get_distance(point1, point2)
            dist_array.append((i, j, dist))
    # turn dist_array to a dataframe, so we can save it in another Excel sheet
    distances_df = pd.DataFrame(dist_array, columns=["origin", "destination", "distance(m)"])
    # append city name and denotes origin and destination
    distances_df = distances_df.merge(df[["city"]], left_on="origin", right_index=True).rename(
        columns={"city": "start"})
    distances_df = distances_df.merge(df[["city"]], left_on="destination", right_index=True).rename(
        columns={"city": "end"})
    # save the dataframe in an Excel sheet
    distances_df.to_excel("distance_data.xlsx")


def main():
    # note: since we are collecting 2162 connections, running this script will take roughly 35 minutes.
    get_all_distance("city_list.xlsx")


if __name__ == "__main__":
    main()
