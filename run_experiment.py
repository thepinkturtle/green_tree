"""
cse6242 s21
run_experiment.py - utilities to supply data to the templates.

This file contains a pair of functions for retrieving and manipulating data
that will be supplied to the template for generating the table. """
import sqlite3
from sqlite3 import Error
from dijkstar import Graph, find_path
from itertools import combinations
import random
import haversine as hs
from haversine import Unit
import statistics # RL #
import csv # RL #
import numpy 
from numpy  import array, savetxt
import collections


# -----Parameters------
dbName = "data/ProjectDB" # DO NOT CHANGE
# ---------------------

# TO DO: This sqlDB class is identical to the one found in generate_db.py and find_shortest_path.py, 
# so we can put this in its own file and import the class in each file
class sqlDB():
    # Method taken from HW1 Q2_SQL.py template
    def create_connection(self, path):
        connection = None
        try:
            connection = sqlite3.connect(path)
            connection.text_factory = str
        except Error as e:
            print("Error occurred: " + str(e))
    
        return connection
    
    # Method taken from HW1 Q2_SQL.py template
    def execute_query(self, connection, query):
        cursor = connection.cursor()
        try:
            if query == "":
                return "Query Blank"
            else:
                cursor.execute(query)
                connection.commit()
                return "Query executed successfully"
        except Error as e:
            return "Error occurred: " + str(e)
    
    def create_nodes_table(self, connection):
        ############### EDIT SQL STATEMENT ###################################
        create_sql = "CREATE TABLE nodes(id integer, number_of_dc_chargers real, latitude real, longitude real);"
        ######################################################################
        
        return self.execute_query(connection, create_sql)
    
    def create_edges_table(self, connection):
        ############### EDIT SQL STATEMENT ###################################
        create_sql = "CREATE TABLE edges(id1 integer, id2 integer, distance real);"
        ######################################################################
        
        return self.execute_query(connection, create_sql)
    
    def save_nodes(self, connection, df):
        n = len(df)
        for i in range(n):
            node = df.iloc[i]
            
            id_val = int(node['ID'])
            number_of_dc_chargers = int(node['EV DC Fast Count'])
            latitude = float(node['Latitude'])
            longitude = float(node['Longitude'])
            
            connection.execute("INSERT INTO nodes VALUES (?,?,?,?)", (id_val, 
                                                                      number_of_dc_chargers,
                                                                      latitude,
                                                                      longitude))
            connection.commit()

        sql = "SELECT COUNT(id) FROM nodes;"
        cursor = connection.execute(sql)
        return cursor.fetchall()[0][0]
    
    def save_edges(self, connection, edges):
        for edge in edges:
            id1 = int(edge[0])
            id2 = int(edge[1])
            distance = float(edge[2])
            connection.execute("INSERT INTO edges VALUES (?,?,?)", (id1,id2,distance))
            connection.commit()
            
        sql = "SELECT COUNT(id1) FROM edges;"
        cursor = connection.execute(sql)
        return cursor.fetchall()[0][0]

def username():
    return 'mholt33'

def data_wrangling(car_range, n=''):
    db = sqlDB()
    conn = db.create_connection(dbName)

    query = "SELECT * FROM nodes"
    if n:
        query += ' LIMIT {};'.format(n)
        print(query)
    cursor = conn.execute(query)
    nodes = cursor.fetchall()
    numOfNodes = len(nodes)


    # Select any edges less than the provided car range
    cursor = conn.execute("SELECT * FROM edges WHERE distance < {};".format(car_range))
    edges = cursor.fetchall()
    n = len(edges)
    print("\tNumber of Edges Less Than {} miles: {}".format(car_range, n))

    # build a dict to get # of dc chargers at each station
    dict_dc = {}
    for ii in nodes:
        dict_dc[ii[0]] = ii[1]
        
    maxdc = max(dict_dc.values()) # max # of dc charger
    dict_freq = {}
    for key, val in dict_dc.items():
        if val not in dict_freq:
            dict_freq[val] = 0
        dict_freq[val] += 1
    dict_freq = collections.OrderedDict(sorted(dict_freq.items()))
    # print("Freq table: # of dc chargers\n", dict_freq, "\n")
    
    return nodes, numOfNodes, edges, dict_dc, maxdc

def cost_func_fewest_stops(u, v, edge, prev_edge):
    return 1 # cost of each edge is one when determining fewest stops

def cost_func_shortest_dist(u, v, edge, prev_edge):
    return edge[0] # cost of each edge is the miles between the stations when determining shortest distance

def cost_func_reliability(u, v, edge, prev_edge):
    dist, nc = edge
    return 1 / nc

def find_all_shortest_paths(nodes, sampled_index_pairs, edges, car_range, objective = 2, print_vals = False):
    # Build the graph by looping through all edges and adding them in both directions 
    graph = Graph()

    for i, edge in enumerate(edges):
        graph.add_edge(edge[0], edge[1], (edge[2], dict_dc[edge[1]]))
        graph.add_edge(edge[1], edge[0], (edge[2], dict_dc[edge[0]]))

    all_costs_added = []
    all_trip_values = []
    all_shortest_possible_values = []
    all_fewest_possible_stops = []
    all_stops_added = []
    all_stops_values = []

    
    path_object = None
    for pair in sampled_index_pairs:
        index_1 = pair[0]
        index_2 = pair[1]
        
        station_id_1 = nodes[index_1][0]
        station_id_1_latlong = (nodes[index_1][2], nodes[index_1][3])
        
        station_id_2 = nodes[index_2][0]
        station_id_2_latlong = (nodes[index_2][2], nodes[index_2][3])

        straightline_distance = hs.haversine(station_id_1_latlong,
                                            station_id_2_latlong,
                                            unit=Unit.MILES)
        # shortest possible number of stops = straightline distance / car range (rounded down to nearest integer)
        fewest_possible_stops = int(straightline_distance / car_range)
        # shortest possible distance
        shortest_possible_value = straightline_distance
                
        # Find shortest path
        # if using default of objective (1 = fewest stops), we want to use the cost function where all edge weights are 1 (otherwise use the edge's distance)
        try:
            if objective == 1:
                path_object = find_path(graph, station_id_1, station_id_2, cost_func=cost_func_fewest_stops)
                cost_of_path_stops = path_object.total_cost - 1 # Must subtract 1 to capture number of stops
                                                          # because cost sums up all weight edges (so for one stop, we traverse two edges A --1--> stop --1--> B)
                # Sum total planned trip distance
                cost_of_path = 0
                for p in path_object.edges:
                    cost_of_path += p[0]
                
            elif objective == 2:
                # Sum total planned trip distance
                path_object = find_path(graph, station_id_1, station_id_2, cost_func=cost_func_shortest_dist)
                cost_of_path = path_object.total_cost
                # Count stops
                cost_of_path_stops = len(path_object.edges) - 1
                
            else:
                # Sum total planned trip distance
                path_object = find_path(graph, station_id_1, station_id_2, cost_func=cost_func_reliability)
                cost_of_path = 0
                for p in path_object.edges:
                    cost_of_path += p[0]
                # Count stops
                cost_of_path_stops = len(path_object.edges) - 1
                
            
            dist_added = cost_of_path - shortest_possible_value
            stop_added = cost_of_path_stops - fewest_possible_stops

            if print_vals:
                print("\nShortest Path Cost: {}".format(cost_of_path))
                print("Shortest Possible Cost: {}".format(shortest_possible_value))
                print("Cost Added: {}".format(distance_added))

            all_costs_added.append(dist_added)
            all_stops_added.append(stop_added)
            all_trip_values.append(cost_of_path)
            all_stops_values.append(cost_of_path_stops)
            all_shortest_possible_values.append(shortest_possible_value)
            all_fewest_possible_stops.append(fewest_possible_stops)
        except:
            print("No path between {} and {}".format(station_id_1, station_id_2))

    
        
    return all_costs_added, all_trip_values, all_shortest_possible_values, all_stops_added, all_stops_values, all_fewest_possible_stops


def get_all_data(car_range):
    print("Getting all stations from the database...")
    nodes, num_of_nodes, edges, dict_dc, maxdc = data_wrangling(car_range)
    print("\tNumber of stations: {}".format(num_of_nodes))
    return nodes, num_of_nodes, edges, dict_dc, maxdc

def get_sample_data(nodes, num_of_nodes):
    print("\nGetting all possible station pair combinations...")
    all_node_index_pairs = list(combinations(range(num_of_nodes), 2))
    num_of_node_pairs = len(all_node_index_pairs)
    print("\tTotal Number of Station Pairs: {}".format(num_of_node_pairs))
          
    print("\tRandomly sampling {} of these {} pairs".format(num_to_sample, num_of_node_pairs))
    random.seed(7)
    indices_of_node_combos = random.sample(range(num_of_node_pairs), num_to_sample)
    sampled_index_pairs = [all_node_index_pairs[i] for i in indices_of_node_combos]

    return sampled_index_pairs

       

if __name__ == '__main__':
    ################# PARAMETERS TO SET ###################################
    num_to_sample = 1000 # Want to sample 1000 pairs of locations
    car_range = 150   # Tesla's car can go 250 miles on one charge, so we go with 150 miles as a buffer
    ################# END OF PARAMETERS TO SET ############################

    
    
    print("\n\nNumber of location pairs tested: {}".format(num_to_sample)) # RL #
    print("Car range: {}\n".format(car_range)) # RL #

    # Step 1: Get all station data (our graph's nodes)
    nodes, num_of_nodes, edges, dict_dc, maxdc = get_all_data(car_range)

    # Step 2: Sample stations from the set of all stations (number chosen based on num_to_sample
    sampled_index_pairs = get_sample_data(nodes, num_of_nodes)

    # Step 3: For each objective, compare the shortest paths calculated versus the minimum possible values
    objective_names = ["Fewest Stops", "Shortest Distance", "Reliability"]
    for i, objective_name in enumerate(objective_names):
        print("\n\n-------Objective = {}-------\n".format(objective_name))
        
        all_costs_added, all_trip_values, all_shortest_possible_values, all_stops_added, all_stops_values, all_fewest_possible_stops = find_all_shortest_paths(nodes, sampled_index_pairs, edges, car_range, objective=i+1)

        # summarize cost of distance
        mean_trip_cost = sum(all_trip_values) / len(all_trip_values)
        mean_shortest_trip_cost = sum(all_shortest_possible_values) / len(all_shortest_possible_values)
        mean_cost_added = sum(all_costs_added) / len(all_costs_added)
        max_cost_added = max(all_costs_added) 
        min_cost_added = min(all_costs_added) 
        median_cost_added = statistics.median(all_costs_added) 
        stdev_cost_added = statistics.stdev(all_costs_added)
        array_all_costs_added = array(all_costs_added)
        
        # summarize cost of stops
        mean_trip_cost_stops = sum(all_stops_values) / len(all_stops_values)
        mean_fewest_trip_stops = sum(all_fewest_possible_stops) / len(all_fewest_possible_stops)
        mean_stops_added = sum(all_stops_added) / len(all_stops_added)
        max_stops_added = max(all_stops_added) 
        min_stops_added = min(all_stops_added) 
        median_stops_added = statistics.median(all_stops_added) 
        stdev_stops_added = statistics.stdev(all_stops_added)
        array_all_stops_added = array(all_stops_added)

        print("Average Number of Stops Per Trip: {} stops".format(mean_trip_cost_stops))
        print("Average Number of Minimum Possible Stops Per Trip: {} stops".format(mean_fewest_trip_stops))
        print("Number of Stops Added:")
        print("   Mean: {}".format(mean_stops_added))
        print("   Standard Deviation: {}".format(stdev_stops_added))
        print("   Median: {}".format(median_stops_added))
        print("   Max: {}".format(max_stops_added))
        print("   Min: {}".format(min_stops_added))

        print("Average Distance Per Trip: {} miles".format(mean_trip_cost))
        print("Average Minimum Straightline Distance Per Trip: {} miles".format(mean_shortest_trip_cost))
        print("Miles Added:")
        print("   Mean: {}".format(mean_cost_added))
        print("   Standard Deviation: {}".format(stdev_cost_added))
        print("   Median: {}".format(median_cost_added))
        print("   Max: {}".format(max_cost_added))
        print("   Min: {}".format(min_cost_added))

        if i+1 == 1: # RL #
            arr_obj = numpy.array([(i+1)] * len(all_costs_added))
            arr_1 = numpy.dstack((array_all_costs_added, array_all_stops_added, arr_obj))[0]

        elif i+1 == 2: # RL #
            arr_obj = numpy.array([(i+1)] * len(all_costs_added))
            arr_2 = numpy.dstack((array_all_costs_added, array_all_stops_added, arr_obj))[0]
            arr_2 = numpy.concatenate((arr_1, arr_2), axis=0)
            
        elif i+1 == 3: # RL #
            arr_obj = numpy.array([(i+1)] * len(all_costs_added))
            arr_3 = numpy.dstack((array_all_costs_added, array_all_stops_added, arr_obj))[0]
            arr_3 = numpy.concatenate((arr_2, arr_3), axis=0)
            
            # Output all results to a single csv results
            newfile = numpy.savetxt("flaskapp/output/all_value_added.csv", arr_3,"%f,%f,%d",header="Values, Stops, Objectives")

        

    
