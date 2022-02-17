"""
cse6242 s21
wrangling.py - utilities to supply data to the templates.

This file contains a pair of functions for retrieving and manipulating data
that will be supplied to the template for generating the table. """
import sqlite3
from sqlite3 import Error
from dijkstar import Graph, find_path


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

def data_wrangling(n=''):
    db = sqlDB()
    conn = db.create_connection(dbName)

    query = "SELECT * FROM nodes"
    if n:
        query += ' LIMIT {};'.format(n)
        print(query)
    cursor = conn.execute(query)
    nodes = cursor.fetchall()
    numOfNodes = len(nodes)
        
    return nodes, numOfNodes
    #return header, table

def cost_func_fewest_stops(u, v, edge, prev_edge):
    return 1 # cost of each edge is one when determining fewest stops

def cost_func_shortest_dist(u, v, edge, prev_edge):
    return edge[0] # cost of each edge is the miles between the stations when determining shortest distance

def cost_func_reliability(u, v, edge, prev_edge):
    dist, nc = edge
    return 1 / nc

def find_shortest_path(station1, station2, carRange, objective = 1):
    db = sqlDB()
    conn = db.create_connection(dbName)

    query = "SELECT * FROM nodes"
    cursor = conn.execute(query)
    nodes = cursor.fetchall()
    numOfNodes = len(nodes)

    # build a dict to get # of dc chargers at each station
    dict_dc = {}
    for node in nodes:
        dict_dc[node[0]] = node[1]

    # Select any edges less than the provided car range
    cursor = conn.execute("SELECT * FROM edges WHERE distance < {};".format(carRange))
    edges = cursor.fetchall()
    n = len(edges)
    print("\n\nNumber of Edges Less Than {} miles: {}\n\n".format(carRange, n))
    
    graph = Graph()

    # Build the graph by looping through all edges
    for i, edge in enumerate(edges):
        graph.add_edge(edge[0], edge[1], (edge[2], dict_dc[edge[1]]))
        graph.add_edge(edge[1], edge[0], (edge[2], dict_dc[edge[0]]))
        # graph.add_edge(edge[0], edge[1], edge[2])
        # graph.add_edge(edge[1], edge[0], edge[2])


    path_object = None
    try: 
        # if using default of objective (1 = fewest stops), we want to use the cost function where all edge weights are 1 (otherwise use the edge's distance)
        if objective == 1:
            path_object = find_path(graph, station1, station2, cost_func=cost_func_fewest_stops)
        elif objective == 2:
            path_object = find_path(graph, station1, station2, cost_func=cost_func_shortest_dist)
        else:
            path_object = find_path(graph, station1, station2, cost_func=cost_func_reliability)

        print("\nPath Object:")
        print(path_object)

        nodes_on_path = path_object.nodes
        edges_on_path = [edge[0] for edge in path_object.edges]
        num_of_edges = len(edges_on_path)
        str_of_path = str(nodes_on_path[0])
        total_distance = 0 
        for i, node in enumerate(nodes_on_path[1:]):
            if i < num_of_edges:
                edge = edges_on_path[i]
                total_distance += edge
                edge = round(edge, 1)
                str_of_path += '  -({} miles)->  {}'.format(edge, node)
            else:
                str_of_path += str(node)

        cost_of_path = round(path_object.total_cost, 2)
        print("\nShortest Path Cost: {}".format(cost_of_path))
        print("\nDistance of Path: {} miles".format(total_distance))

        number_of_stops = len(nodes_on_path) - 2 # We must subtract the starting and ending point to determine number of stops


        print(str_of_path)
        return nodes_on_path, str_of_path, cost_of_path, edges_on_path, total_distance, number_of_stops
    except:
        print("Could not find a path from {} to {}!".format(station1, station2))
        return [], "", 0, [], 0, 0

# if __name__ == '__main__':
#     db = sqlDB()
#     conn = db.create_connection(dbName)
#     query = "SELECT * FROM nodes"
#     if n:
#         query += ' LIMIT {};'.format(n)
#         print(query)
#     cursor = conn.execute(query)
#     nodes = cursor.fetchall()
#     numOfNodes = len(nodes)

#     # build a dict to get # of dc chargers at each station
#     dict_dc = {}
#     for node in nodes:
#         dict_dc[node[0]] = node[1]
