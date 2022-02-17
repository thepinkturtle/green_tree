# Description
This package serves to help electric vehicle drivers better plan their trips by minimizing charging stops. The provided code offers an end-to-end solution from processing raw station data to deploying an interactive dashboard. The root directory of the "CODE" folder contains the run.py file, which can be executed to start up the Flask-based web application, and the run_experiment.py, which is used to evaluate our trip planning algorithm versus the ideal/direct trip route for any given number of test start/end pairs and any input car range. The remaining code is structured into three subfolders: data, flaskapp, and wrangling_scripts.

The "data" subfolder serves to host all data needed for the project, specifically the raw CSV file of stations and the SQLite database version of that raw data after ingestion (called "ProjectDB"). To avoid overly large amounts of data in this submitted zip folder, we provide a small, toy subset of these data files here as a quick start guide.

The "wrangling_scripts" subfolder hosts all files specific to data processing, specifically generate_db.py and wrangling.py. As its name indicates, generate_db.py is the Python script used to generate the "ProjectDB" SQLite database mentioned above in the "data" subfolder. When executed, this file will parse the raw CSV file in the "data" subfolder and save off all nodes (stations) and edges into their respective SQLite tables within the "ProjectDB" object in that same "data" subfolder. The other file, wrangling.py, contains all the code for the data-specific tasks of the Flask web app. For example, this is where we compute the shortest path between any two nodes in the graph of charging stations. 

The final subfolder is "flaskapp", which contains all app-specific files. It contains the index.html page that is rendered at app start-up and the routes.py file responsible for managing all routes between the front-end code and our back-end Python functions mentioned in the "wrangling_scripts" subfolder section above. There is also a style.css file to help format the HTML page using CSS.

# Installation 
Follow the below steps to install all dependencies within a project-specific Python virtual environment:

1. If you do not have “virtualenv” installed, install it with the following command: ```pip install virtualenv```
2. Navigate to the project folder ("CODE") within your terminal and run the following command to create a new “evProject” virtual environment: ```virtualenv evProject```
3. Activate this virtual environment with the following command: ```source ./evProject/bin/activate```
4. Run the following command to install all dependencies in your virtual environment: ```pip install -r requirements.txt```



# Execution 
Now that all dependencies have been installed and set up in the above INSTALLATION section, we need to follow the below steps to run a demo on this code:

1. Ensure the SQLite DB "ProjectDB" exists within the "data" subfolder.
2. Open a terminal inside the root of this project activate the virtual environment: ```source ./evProject/bin/activate```
3. Run the following command to start the Flask app: ```python3 run.py```
4. After running the command, go to http://127.0.0.1:3001/ in your browser.
5. Assuming proper set-up, you should now see a map of California with user options at the top.
6. Use the dropdown at the top of the page to select an objective.
7. Input a value for the car's range (in miles).
8. Click any two stations in the graph to plan a trip between them according to your input parameters.
9. You should now be provided with the optimal path of charging stations to stop at during your trip based on your input objective.
10. To plan another trip, click the "Plan Another Trip" button in the top right and then repeat steps 6-9 above.
11. To shut down the Flask app when finished, return to your running terminal and hit Ctrl + C. 

# Demo Video
URL of 1-minute install video: ___________________
