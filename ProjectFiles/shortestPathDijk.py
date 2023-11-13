# Import the pandas library for data manipulation and analysis
import pandas as pd

# Import the heapq module for priority queue implementation
import heapq

# Import the numpy library for numerical computing and array operations
import numpy as np

# Import the folium library for creating interactive maps
import folium

# Import the os module for interacting with the operating system
import os

# new ----------------------------------------------
# constant to convert meter to miles
METER_TO_MILES = 0.00062137

# make the defined coordinates dictionary global so we don't have to change method signature
global coordinates
# new ----------------------------------------------

def dijkstra(graph, start):
    num_cities = len(graph)
    distances = np.full(num_cities, float('inf'))  # Initialize distances with infinity
    distances[start] = 0  # Set distance of start city to 0
    queue = [(0, start)]  # Priority queue to track cities to visit
    visited = set()  # Set to track visited cities
    previous_cities = {}  # Dictionary to track previous cities for each neighbor

    while queue:
        current_distance, current_city = heapq.heappop(queue)  # Get the city with the shortest distance

        if current_city in visited:
            continue  # Skip if already visited

        visited.add(current_city)

        for neighbor, distance in graph[current_city].items():
            total_distance = current_distance + distance  # Compute the total distance to the neighbor

            if total_distance < distances[neighbor]:
                distances[neighbor] = total_distance  # Update the distance to the neighbor
                previous_cities[neighbor] = current_city  # Track previous city for neighbor
                heapq.heappush(queue, (total_distance, neighbor))  # Add the neighbor to the queue

    return distances, previous_cities


# new ----------------------------------------------
def setup_coordinates(city_data):
    """
    Function to gather all coordinates of all city, and turn it into a dictionary.
    :param city_data: Excel sheet containing coordinates.
    :return: A dictionary where city name is the key, and the values are tuples (latitude, longitude).
    """
    # drop all columns that doesn't get utilized
    city_data = city_data[["city", "lat", "lon"]]
    # remove white spaces from city names
    city_data["city"] = city_data["city"].str.strip()
    # convert dataframe into a dictionary
    coordinate_dict = city_data.set_index("city").T.to_dict('list')
    # convert list into tuples
    for city in coordinate_dict:
        coordinate_dict[city] = tuple(coordinate_dict[city])

    return coordinate_dict


def get_coordinates(city):
    # Define the coordinates for each city
    # coordinates = {
    #     'Newport': (41.49008, -71.312796),
    #     'Boston': (42.3601, -71.0589),
    #     'Manchester': (42.9956, -71.4548),
    #     'Portland': (43.6615, -70.2553),
    #     'Worcester': (42.2626, -71.8023),
    #     'Hartford': (41.7637, -72.6851),
    #     'Providence': (41.824, -71.4128),
    #     'Concord': (43.2081, -71.537),
    #     'Burlington': (44.4759, -73.2121),
    #     'Chicago': (41.8781, -87.6298),
    #     'Los Angeles': (34.0522, -118.2437),
    #     'Houston': (29.7604, -95.3698),
    #     'Miami': (25.7617, -80.1918),
    #     'Seattle': (47.6062, -122.3321),
    #     'Denver': (39.7392, -104.9903),
    #     'Atlanta': (33.7490, -84.3880),
    #     'New York City': (40.7128, -74.0060),
    #     'San Francisco': (37.7749, -122.4194),
    #     'Dallas': (32.7767, -96.7970),
    #     'Salt Lake City': (40.7608, -111.8910),
    #     'Las Vegas': (36.1699, -115.1398),
    #     'Phoenix': (33.4484, -112.0740),
    #     'Philadelphia': (39.9526, -75.1652),
    #     'Tulsa': (36.1540, -95.9928),
    #     'Des Moines': (41.5868, -93.6250),
    #     'Milwaukee': (43.0389, -87.9065),
    #     'Wichita': (37.6872, -97.3301),
    #     'Boise': (43.6150, -116.2023),
    #     'Memphis': (35.1495, -90.0490),
    #     'New Orleans': (29.9511, -90.0715)
    # }

    # Retrieve the coordinates for the given city
    return coordinates.get(city, (0, 0))  # Default to (0, 0) if coordinates are not found
# new ----------------------------------------------------


def shortest_path(graph, start, end):
    distances, previous_cities = dijkstra(graph, start)  # Compute the shortest distances and previous cities

    if distances[end] == float('inf'):
        return None  # No path exists

    path = []
    current_city = end
    while current_city != start:
        path.append(current_city)  # Add the current city to the path
        current_city = previous_cities[current_city]  # Move to the previous city

    path.append(start)  # Add the start city to the path
    path.reverse()  # Reverse the path to get the correct order

    return path


# new ------------------------------------------------
def clean_up_data(data_frame):
    """
    Function to clean up data that was generated from dataScraping.py. Since the output
    generates extra columns, we will need to drop those. On top of that, the distance data is
    originally in meters, which we will convert to miles.
    :param data_frame: dataframe that contains distance data between cities.
    :return: dataframe that is compatible with dijkstra implementation.
    """
    # drop all columns that doesn't get utilized
    data_frame = data_frame[["distance(m)", "start", "end"]]
    # convert meters to miles
    data_frame = data_frame.assign(distance=lambda x: (x["distance(m)"] * METER_TO_MILES))
    # drop the distance(m) column because we don't need it anymore
    data_frame = data_frame[["start", "end", "distance"]]
    # remove trailing white spaces in names
    data_frame["start"] = data_frame["start"].str.strip()
    data_frame["end"] = data_frame["end"].str.strip()
    return data_frame
# new -----------------------------------------------------------


def main():
    # new ----------------------------------------------
    # suppress warning from pd because chained assignment was used to remove white spaces
    # from the cities columns
    pd.set_option('mode.chained_assignment', None)
    # Read the Excel sheet and create the graph
    df = pd.read_excel('distance_data.xlsx')  # changed input file name
    df = clean_up_data(df)  # cleaned up data, so it's compatible with the rest of the code

    # Read the Excel sheet that contains coordinates for all cities
    coor_df = pd.read_excel('city_list.xlsx')
    # make the coordinates data global, so we don't need to modify function signatures
    global coordinates
    # get coordinates for all cities as dictionary
    coordinates = setup_coordinates(coor_df)
    # new ----------------------------------------------

    #print(df[['start','end']])
    cities = sorted(set(df['start']).union(set(df['end'])))
    num_cities = len(cities)
    print("Cities:", cities)  # Print the cities to check the names
    graph = {}

    for row in df.itertuples(index=False):
        start = cities.index(row.start.strip())
        end = cities.index(row.end.strip())
        distance = row.distance

        if start not in graph:
            graph[start] = {}  # Create an empty dictionary for the start city if it doesn't exist
        if end not in graph:
            graph[end] = {}  # Create an empty dictionary for the end city if it doesn't exist

        # Add the distance as a value in the start and end city's dictionaries
        graph[start][end] = distance


    while True:
        # Prompt the user for input
        while True:
            try:
                user_input = input("Enter the starting city (or 'quit' to exit): ").strip()

                if user_input.lower() == "quit":
                    print("Exiting the program...")
                    return
                elif user_input.strip() not in map(str.strip, cities):
                    print("Invalid city. Please try again.")
                else:
                    start_city = cities.index(user_input.strip())
                    break
            except KeyboardInterrupt:
                print("\nProgram interrupted.")
                return

        while True:
            try:
                user_input = input("Enter the destination city (or 'quit' to exit): ").strip()

                if user_input.lower() == "quit":
                    print("Exiting the program...")
                    return
                elif user_input.strip() not in map(str.strip, cities):
                    print("Invalid city. Please try again.")
                else:
                    end_city = cities.index(user_input.strip())
                    break
            except KeyboardInterrupt:
                print("\nProgram interrupted.")
                return

        # Find the shortest path
        path = shortest_path(graph, start_city, end_city)

        # Check if a valid path exists
        if path is None:
            print("No path exists.")
        else:
            # Create a map
            m = folium.Map(location=[42.3601, -71.0589], zoom_start=10)  # Adjust the center and zoom level accordingly

            # Plot cities as markers
            for city in cities:
                lat, lon = get_coordinates(city)  # Assuming you have a function to get the coordinates of each city
                folium.Marker([lat, lon], popup=city).add_to(m)

            # Draw the shortest path
            line_coords = [(get_coordinates(cities[city])[0], get_coordinates(cities[city])[1]) for city in path]
            folium.PolyLine(line_coords, color="red", weight=2.5, opacity=1).add_to(m)

            # Display the map
            output_path = os.path.expanduser("~/Desktop/shortest_path_map.html")
            m.save(output_path)
            print(f"Shortest path map saved as '{output_path}'.")
            # m.save("shortestPathMap.html")
            # print("Shortest path map saved as 'shortest_path_map.html'.")
            print("Shortest path:", " -> ".join(cities[city] for city in path))

        # Prompt the user to find another path
        user_input = input("Do you want to find another path? (y/n): ")
        if user_input.lower() != "y":
            print("Exiting the program...")
            return


main()