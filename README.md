"YouTube Data Harvesting and Warehousing using SQL, MongoDB and Streamlit"

Main Objective:
     This project aims to develop a user-friendly Streamlit application that utilizes the Google API to extract information on a YouTube channel, stores it in a MongoDB database, migrates it to a SQL data warehouse, and enables users to search for channel details and join tables to view data in the Streamlit app.
Skills Take Away:
     1.Python scripting
     2.Data Collection
     3.MongoDB
     4.Streamlit 
     5.API integration
     6.Data Management using MongoDB (Atlas) and SQL

Problem Statement:
    The problem statement is to create a Streamlit application that allows users to access and analyze data from multiple YouTube channels.
Features that are added in this applications:
    1.User can able to give input as a YouTube channel ID, it retrieve all the relevant data like Channel name, subscribers, total video count, playlist ID, video ID, likes, dislikes, comments of each videos using Google API.
    2.Provide Option to store the data in a MongoDB database as a data lake.
    3.Ability to collect data for up to 10 different YouTube channels and store them in the data lake by clicking a button.
    4.Provide Option to select a channel name and migrate its data from the data lake to a SQL database as tables.
    5.Ability to search and retrieve data from the SQL database using different search options, including joining tables to get channel details.
To accomplish this, several packages are utilized:
    Google apiclient.discovery: This package allows interaction with the YouTube Data API, enabling the retrieval of video-related data.

    Streamlit: Streamlit is employed as the web application framework for this project. It provides an intuitive and user-friendly interface for easy interaction with the application.

    psycopg2: This package is utilized to establish a connection and perform operations on a PostgreSQL database. It facilitates the migration of data from MongoDB to PostgreSQL for subsequent analysis.

    pandas: The pandas package is used for data manipulation and analysis. It aids in organizing and structuring the collected data in a convenient format.

    pymongo: This package is employed to interact with MongoDB, a NoSQL database. It enables the storage of unstructured data extracted from YouTube.

Approach of this project:
    I used VS code platform for python code in virtual environments in that I want to installed some packages like google-api-python-client,pymongo,psycopg2(postgresql),pandas and streamlit for building this application.
    The basic idea of work flow is:
               1.Set up a Streamlit app
               2.Connect to the YouTube API
               3.Store data in a MongoDB data lake
               4.Migrate data to a SQL data warehouse
               5.Query the SQL data warehouse
               6.Display data in the Streamlit app

  SQL Query Output need to displayed as table in Streamlit Application:
              1.What are the names of all the videos and their corresponding channels?
              2.Which channels have the most number of videos and how many videos do they have?
              3.What are the top 10 most viewed videos and their respective channels?
              4.How many comments were made on each video and what are their corresponding video names?
              5.Which videos have the highest number of likes and what are their corresponding channel names?
              6.What is the total number of likes and dislikes for each video and what are their corresponding video names?
              7.What is the total number of views for each channel and what are their corresponding channel names?
              8.What are the names of all the channels that have published videos in the year 2022?
              9.What is the average duration of all videos in each channel and what are their corresponding channel names?
              10.Which videos have the highest number of comments and what are their corresponding channel names?

Flow of writing a code is:
            Initially create a new virtual environment file as .py file and then we need to connect the API using youtube API reference[https://developers.google.com/youtube/v3/getting-started]
            and then we create some individual functional blocks for extract the information of channel,video ids,playlists,videos,comments.
            after the extraction is done we need to upload the collection of data in mongodb and then create the table creation of channels,playlists,videos,comments in sql database.
            after the table formation completes,we move on to streamlit code.For streamlit build we refer[https://docs.streamlit.io/library/api-reference]
            after code computation we save the file and click the terminal and run streamlit as (streamlit run filename.py) once it executes it automatically redirect to our streamlit application page that we created.
            in that web page application,we give any channel id in that search box then collect the data and migrate the data in sql by click their respective buttons. then we view channel details as the output of the corresponding queries that we selected.

 

               
