import sqlite3
from sqlite3 import Error
import pandas as pd
import numpy as np
import haversine as hs
from haversine import Unit

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
        create_sql = "CREATE TABLE nodes(id integer, number_of_dc_chargers real, latitude real, longitude real, station_name string, street_address string, city string, state string, zip_code string);"
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
            station_name = str(node['Station Name'])
            street_address = str(node['Street Address'])
            city = str(node['City'])
            state = str(node['State'])
            zip_code = str(node['ZIP'])

            connection.execute("INSERT INTO nodes VALUES (?,?,?,?,?,?,?,?,?)", (id_val, 
                                                                              number_of_dc_chargers,
                                                                              latitude,
                                                                              longitude,
                                                                              station_name,
                                                                              street_address,
                                                                              city,
                                                                              state,
                                                                              zip_code))
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

def build_df(path_to_data):
    df = pd.read_csv(path_to_data)
    
    # Find all stations in California
    cal_df = df[df['State'] == 'CA'].copy()
    
    # Now we need to format our Latitude and Longitude coordinates into a single tuple
    cal_df['Lat Long Tuple'] = cal_df.apply(lambda row: (row.loc['Latitude'], row.loc['Longitude']), axis=1)

    # Filter to only those stations with a DC charger
    cal_df_dc_chargers = cal_df[cal_df['EV DC Fast Count'] > 0]
    return cal_df_dc_chargers
    

# Now let's build all edges within a given mile range
def build_all_edges(df, mile_range=250):
    n = len(df)

    all_edges = []
    num_of_edges = 0
    for i in range(n):
        node1 = df.iloc[i]
        loc1 = node1['Lat Long Tuple']
        id1 = node1['ID']
        for j in range(i+1, n):
            node2 = df.iloc[j]
            loc2 = node2['Lat Long Tuple']
            id2 = node2['ID']

            # Compute distance in miles between two stations
            miles_between = hs.haversine(loc1,loc2,unit=Unit.MILES)
            all_edges.append((id1, id2, miles_between))

            if miles_between < mile_range:
                num_of_edges += 1
    print("Number of Edges Within {} Miles: {}".format(mile_range, num_of_edges))
    return all_edges



if __name__ == "__main__":
    # -----Parameters------
    dbName = "../data/ProjectDB" # DO NOT CHANGE
    dbAlreadyExists = True # change to False to overwrite existing tables and regenerate all data
    path_to_data = '../data/alt_fuel_stations (Sep 11 2021).csv' # relative path to the csv file
    # ---------------------
    db = sqlDB()
    try:
        #sqlite3.register_adapter(np.int64, lambda val: int(val)) # Need this adapter to save off integers
        conn = db.create_connection(dbName)
    except:
        print("Database Creation Error")

    if not dbAlreadyExists: # We will create it now
        try:
            conn.execute("DROP TABLE IF EXISTS edges;")
            conn.execute("DROP TABLE IF EXISTS nodes;")
        except:
            print("Error in Table Drops")


        # Build the dataframe and all the edges first
        try:
            print("Building dataframe of charging stations...")
            cal_df_dc_chargers = build_df(path_to_data)
            print("Dataframe built! Number of charging stations: {}".format(len(cal_df_dc_chargers)))

            print("Building all edges...")
            all_edges = build_all_edges(cal_df_dc_chargers)
            print("Edges built! Number of total edges: {}".format(len(all_edges)))
        except:
            print("Error building dataframe or edges")


        # Now save off the nodes and edges
        try:
            db.create_nodes_table(conn)
            num_of_nodes = db.save_nodes(conn, cal_df_dc_chargers)
            print("Number of Nodes Saved: {}".format(num_of_nodes))
        except:
            print("Error in saving nodes")
            
        try:
            db.create_edges_table(conn)
            num_of_edges = db.save_edges(conn, all_edges)
            print("Number of Edges Saved: {}".format(num_of_edges))
        except:
            print("Error in saving edges")

        print("\nPrinting 5 sample nodes:")
        cursor = conn.execute("SELECT * FROM nodes LIMIT 5;")
        for node in cursor.fetchall():
            print(node)
            
        print("\nPrinting 5 sample edges:")
        cursor = conn.execute("SELECT * FROM edges LIMIT 5;")
        for edge in cursor.fetchall():
            print(edge)
    else:
        print("Tables already exist!")
        cursor = conn.execute("SELECT COUNT(id) FROM nodes;")
        print("Number of Nodes: {}".format(cursor.fetchall()[0][0]))
        cursor = conn.execute("SELECT COUNT(id1) FROM edges;")
        print("Number of Edges: {}".format(cursor.fetchall()[0][0]))

        print("\nPrinting 5 sample nodes:")
        cursor = conn.execute("SELECT * FROM nodes LIMIT 5;")
        for node in cursor.fetchall():
            print(node)
            
        print("\nPrinting 5 sample edges:")
        cursor = conn.execute("SELECT * FROM edges LIMIT 5;")
        for edge in cursor.fetchall():
            print(edge)
