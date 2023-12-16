from googleapiclient.discovery import build
import pymongo
import psycopg2
import pandas as pd
import streamlit as st

#API key connection


def api_connect():
    api_Id ="AIzaSyADuAP4J9F1TOinbMTGxf7SvnW8dfD1070"
    api_service_name="youtube"
    api_version="v3"

    youtube=build(api_service_name,api_version,developerKey=api_Id)
    return youtube

youtube=api_connect()

#Get channel information

def get_channel_info(channel_id):
    request=youtube.channels().list(
        part="snippet,ContentDetails,statistics",
        id=channel_id
        )
    response=request.execute()
    for i in response['items']:
        data=dict(Channel_Name=i["snippet"]["title"],
                  Channel_Id=i["id"],
                  Subscribers=i["statistics"]["subscriberCount"],
                  Views=i["statistics"]["viewCount"],
                  Total_Videos=i["statistics"]["videoCount"],
                  Channel_Description=i["snippet"]["description"],
                  Playlist_Id=i["contentDetails"]["relatedPlaylists"]["uploads"])
    return data

#Get Video Ids

def get_videos_ids(channel_id):
    video_ids=[]
    response=youtube.channels().list( id=channel_id,
                                    part='contentDetails').execute()
    Playlist_Id=response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    next_page_token=None

    while True:
        response1=youtube.playlistItems().list(
            part='snippet',
            playlistId=Playlist_Id,
            maxResults=50,
            pageToken=next_page_token).execute()
        for i in range(len(response1['items'])):
            video_ids.append(response1['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token=response1.get('nextPageToken')

        if next_page_token is None:
            break
    return video_ids

#Get Video Information

def get_video_info(video_ids):
    video_data=[]
    for video_id in video_ids:
        request=youtube.videos().list(
            part="snippet,ContentDetails,statistics",
            id=video_id
        )
        response=request.execute()
        
        for item in response["items"]:
            data=dict(Channel_Name=item['snippet']['channelTitle'],
                    Channel_Id=item['snippet']['channelId'],
                    Video_Id=item['id'],
                    Title=item['snippet']['title'],
                    Tags=item['snippet'].get('tags'),
                    Thumbnail=item['snippet']['thumbnails']['default']['url'],
                    Description=item['snippet'].get('description'),
                    Published_Date=item['snippet']['publishedAt'],
                    Duration=item['contentDetails']['duration'],
                    Views=item['statistics'].get('viewCount'),
                    Likes=item['statistics'].get('likeCount'),
                    Comments=item['statistics'].get('commentCount'),
                    Favorite_Count=item['statistics']['favoriteCount'],
                    Definition=item['contentDetails']['definition'],
                    Caption_Status=item['contentDetails']['caption']
                    )
            video_data.append(data)
    return video_data

#Get Comment Information

def get_comment_info(video_ids):
    Comment_data=[]
    try:
        for video_id in video_ids:
            request=youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=50
                )
            response=request.execute()

            for item in response['items']:
                data=dict(Comment_Id=item['snippet']['topLevelComment']['id'],
                        Video_Id=item['snippet']['topLevelComment']['snippet']['videoId'],
                        Comment_Text=item['snippet']['topLevelComment']['snippet']['textDisplay'],
                        Comment_Author=item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                        Comment_Published=item['snippet']['topLevelComment']['snippet']['publishedAt'])
                Comment_data.append(data)
            
    except:
        pass
    return Comment_data

#Get Playlist Details

def get_playlist_details(channel_id):
    next_page_token=None
    All_data=[]
    while True:
        request=youtube.playlists().list(
            part='snippet,contentDetails',
            channelId=channel_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response=request.execute()

        for item in response['items']:
            data=dict(Playlist_Id=item['id'],
                    Title=item['snippet']['title'],
                    Channel_Id=item['snippet']['channelId'],
                    Channel_Name=item['snippet']['channelTitle'],
                    PublishedAt=item['snippet']['publishedAt'],
                    Video_Count=item['contentDetails']['itemCount'])
            All_data.append(data)

        next_page_token=response.get('nextPageToken')
        if next_page_token is None:
            break
    return All_data

#Upload to MongoDB

client=pymongo.MongoClient("mongodb+srv://keerthymohan45:4595@cluster0.zxf79bz.mongodb.net/?retryWrites=true&w=majority")
db=client["Utube_data_harvest"]

def channel_details(channel_id):
    ch_details=get_channel_info(channel_id)
    pl_details=get_playlist_details(channel_id)
    vid_ids=get_videos_ids(channel_id)
    vid_details=get_video_info(vid_ids)
    cmt_details=get_comment_info(vid_ids)
    
    coll1=db["channel_details"]
    coll1.insert_one({"channel_information":ch_details,"playlist_information":pl_details,
                            "video_information":vid_details,"comment_information":cmt_details})
    
    return "upload completed successfully"

    #Table Creation For Channels,Playlists,Videos,Comments

def channels_table():
    mydb=psycopg2.connect(host="localhost",
                            user="postgres",
                            password="4595",
                            database="youtube_Data_harvest",
                            port="5432")
    cursor=mydb.cursor()
    drop_query='''drop table if exists channels'''
    cursor.execute(drop_query)
    mydb.commit()

    try:
        create_query='''create table if not exists channels(Channel_Name varchar(100),
                                                                Channel_Id varchar(80) primary key,
                                                                Subscribers bigint,
                                                                Views bigint,
                                                                Total_Videos int,
                                                                Channel_Description text,
                                                                Playlist_Id varchar(80))'''
        cursor.execute(create_query)
        mydb.commit()

    except:
        print("Channels table already created")


    ch_list=[]
    db=client["Utube_data_harvest"]
    coll1=db["channel_details"]
    for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
        ch_list.append(ch_data["channel_information"])
    df=pd.DataFrame(ch_list)


    for index,row in df.iterrows():
        insert_query='''insert into channels(Channel_Name,
                                            Channel_Id,
                                            Subscribers,
                                            Views,
                                            Total_Videos,
                                            Channel_Description,
                                            Playlist_Id)
                                            
                                            values(%s,%s,%s,%s,%s,%s,%s)'''
        values=(row['Channel_Name'],
                row['Channel_Id'],
                row['Subscribers'],
                row['Views'],
                row['Total_Videos'],
                row['Channel_Description'],
                row['Playlist_Id'])
        try:
            cursor.execute(insert_query,values)
            mydb.commit()

        except:
            print("Channel values are already inserted")


            
def playlist_table():
        mydb=psycopg2.connect(host="localhost",
                user="postgres",
                password="4595",
                database="youtube_Data_harvest",
                port="5432")
        cursor=mydb.cursor()

        drop_query='''drop table if exists playlists'''
        cursor.execute(drop_query)
        mydb.commit()


        create_query='''create table if not exists playlists(Playlist_Id varchar(100) primary key,
                                                Title varchar(100),
                                                Channel_Id varchar(100),
                                                Channel_Name varchar(100),
                                                PublishedAt timestamp,
                                                Video_Count int)'''



        cursor.execute(create_query)
        mydb.commit()

        pl_list=[]
        db=client["Utube_data_harvest"]
        coll1=db["channel_details"]
        for pl_data in coll1.find({},{"_id":0,"playlist_information":1}):
                for i in range(len(pl_data["playlist_information"])):
                        pl_list.append(pl_data["playlist_information"][i])
        df1=pd.DataFrame(pl_list)
        
        
        for index,row in df1.iterrows():
                insert_query='''insert into playlists(Playlist_Id,
                                        Title,
                                        Channel_Id,
                                        Channel_Name,
                                        PublishedAt,
                                        Video_Count
                                        )
                                        
                                        values(%s,%s,%s,%s,%s,%s)'''
                values=(row['Playlist_Id'],
                        row['Title'],
                        row['Channel_Id'],
                        row['Channel_Name'],
                        row['PublishedAt'],
                        row['Video_Count'])
                
                
                cursor.execute(insert_query,values)
                mydb.commit()





def videos_table():
        mydb=psycopg2.connect(host="localhost",
                              user="postgres",
                              password="4595",
                              database="youtube_Data_harvest",
                              port="5432")
        cursor=mydb.cursor()

        drop_query='''drop table if exists videos'''
        cursor.execute(drop_query)
        mydb.commit()


        create_query='''create table if not exists videos(Channel_Name varchar(100),
                                                 Channel_Id varchar(100),
                                                 Video_Id varchar(40) primary key,
                                                 Title varchar(160),
                                                 Tags text,
                                                 Thumbnail varchar(200),
                                                 Description text,
                                                 Published_Date timestamp,
                                                 Duration interval,
                                                 Views bigint,
                                                 Likes bigint,
                                                 Comments int,
                                                 Favorite_Count int,
                                                 Definition varchar(20),
                                                 Caption_Status varchar(50)
                                                 )'''



        cursor.execute(create_query)
        mydb.commit()

        vd_list=[]
        db=client["Utube_data_harvest"]
        coll1=db["channel_details"]
        for vd_data in coll1.find({},{"_id":0,"video_information":1}):
                for i in range(len(vd_data["video_information"])):
                        vd_list.append(vd_data["video_information"][i])
        df2=pd.DataFrame(vd_list)


        for index,row in df2.iterrows():
                insert_query='''insert into videos(Channel_Name,
                                                 Channel_Id,
                                                 Video_Id,
                                                 Title,
                                                 Tags,
                                                 Thumbnail,
                                                 Description,
                                                 Published_Date,
                                                 Duration,
                                                 Views,
                                                 Likes,
                                                 Comments,
                                                 Favorite_Count,
                                                 Definition,
                                                 Caption_Status
                                        )
                                        
                                        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                
                values=(row['Channel_Name'],
                        row['Channel_Id'],
                        row['Video_Id'],
                        row['Title'],
                        row['Tags'],
                        row['Thumbnail'],
                        row['Description'],
                        row['Published_Date'],
                        row['Duration'],
                        row['Views'],
                        row['Likes'],
                        row['Comments'],
                        row['Favorite_Count'],
                        row['Definition'],
                        row['Caption_Status'])
                
                
                cursor.execute(insert_query,values)
                mydb.commit()



def comment_table():
        mydb=psycopg2.connect(host="localhost",
                            user="postgres",
                            password="4595",
                            database="youtube_Data_harvest",
                            port="5432")
        cursor=mydb.cursor()
       
        drop_query='''drop table if exists comments'''
        cursor.execute(drop_query)
        mydb.commit()
       
       
        create_query='''create table if not exists comments(Comment_Id varchar(100) primary key,
                                                    Video_Id varchar(50),
                                                    Comment_Text text,
                                                    Comment_Author varchar(150),
                                                    Comment_Published timestamp)'''
       
        cursor.execute(create_query)
        mydb.commit()
       
       
        cmt_list=[]
        db=client["Utube_data_harvest"]
        coll1=db["channel_details"]
        for cmt_data in coll1.find({},{"_id":0,"comment_information":1}):
                for i in range(len(cmt_data["comment_information"])):
                        cmt_list.append(cmt_data["comment_information"][i])
        df3=pd.DataFrame(cmt_list)


        for index,row in df3.iterrows():
            insert_query='''insert into comments(Comment_Id,
                                                    Video_Id,
                                                    Comment_Text,
                                                    Comment_Author,
                                                    Comment_Published)
                                        
                                        values(%s,%s,%s,%s,%s)'''
                
            values=(row['Comment_Id'],
                        row['Video_Id'],
                        row['Comment_Text'],
                        row['Comment_Author'],
                        row['Comment_Published'])
                
                
        cursor.execute(insert_query,values)
        mydb.commit()


def tables():
    channels_table()
    playlist_table()
    videos_table()
    comment_table()

    return "Tables are successfully created"



def show_channels_table():
    ch_list=[]
    db=client["Utube_data_harvest"]
    coll1=db["channel_details"]
    for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
        ch_list.append(ch_data["channel_information"])
    df=st.dataframe(ch_list)

    return df


def show_playlists_table():
        pl_list=[]
        db=client["Utube_data_harvest"]
        coll1=db["channel_details"]
        for pl_data in coll1.find({},{"_id":0,"playlist_information":1}):
                for i in range(len(pl_data["playlist_information"])):
                        pl_list.append(pl_data["playlist_information"][i])
        df1=st.dataframe(pl_list)

        return df1


def show_videos_table():
    vd_list=[]
    db=client["Utube_data_harvest"]
    coll1=db["channel_details"]
    for vd_data in coll1.find({},{"_id":0,"video_information":1}):
        for i in range(len(vd_data["video_information"])):
            vd_list.append(vd_data["video_information"][i])
    df2=st.dataframe(vd_list)

    return df2


def show_comments_table():
        cmt_list=[]
        db=client["Utube_data_harvest"]
        coll1=db["channel_details"]
        for cmt_data in coll1.find({},{"_id":0,"comment_information":1}):
                for i in range(len(cmt_data["comment_information"])):
                        cmt_list.append(cmt_data["comment_information"][i])
        df3=st.dataframe(cmt_list)

        return df3


# streamlit code

with st.sidebar:
    st.title(":blue[YOUTUBE DATA HARVESTING AND WAREHOUSING]")
    st.header("Skills Take Away")
    st.caption("Python scripting")
    st.caption("Data Collection")
    st.caption("MongoDB")
    st.caption("Streamlit")
    st.caption("API Integration")
    st.caption("Data Management using MongoDB and SQL")

channel_id=st.text_input("Enter the Channel ID")

if st.button("collect the data"):
    ch_ids=[]
    db=client["Utube_data_harvest"]
    coll1=db["channel_details"]
    for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
        ch_ids.append(ch_data["channel_information"]["Channel_Id"])

        if channel_id in ch_ids:
            st.success("The given Channel ID informations are already exists")

        else:
            insert=channel_details(channel_id)
            st.success(insert)

if st.button("Data migrate to SQL"):
    Table=tables()
    st.success(Table)

show_table=st.radio("SELECT THE TABLE FOR VIEW",("CHANNELS","PLAYLISTS","VIDEOS","COMMENTS"))

if show_table=="CHANNELS":
    show_channels_table()

elif show_table=="PLAYLISTS":
    show_playlists_table()

elif show_table=="VIDEOS":
    show_videos_table()

elif show_table=="COMMENTS":
    show_comments_table()

    

#SQL CONNECTION

mydb=psycopg2.connect(host="localhost",
                            user="postgres",
                            password="4595",
                            database="youtube_Data_harvest",
                            port="5432")
cursor=mydb.cursor()


question=st.selectbox("Select your questions",("1.What are the names of all the videos and their corresponding channels?",
                                                "2.Which channels have the most number of videos and how many videos do they have?",
                                                "3.What are the top 10 most viewed videos and their respective channels?",
                                                "4.How many comments were made on each video and what are their corresponding video names?",
                                                "5.Which videos have the highest number of likes and what are their corresponding channel names?",
                                                "6.What is the total number of likes and dislikes for each video and what are their corresponding video names?",
                                                "7.What is the total number of views for each channel and what are their corresponding channel names?",
                                                "8.What are the names of all the channels that have published videos in the year 2022?",
                                                "9.What is the average duration of all videos in each channel and what are their corresponding channel names?",
                                                "10.Which videos have the highest number of comments and what are their corresponding channel names?"
                                                ))

if question=="1.What are the names of all the videos and their corresponding channels?":
    query1='''select title as videos,channel_name as channelname from videos'''
    cursor.execute(query1)
    mydb.commit()
    x1=cursor.fetchall()
    df=pd.DataFrame(x1,columns=["video name","channel name"])
    st.write(df)

elif question=="2.Which channels have the most number of videos and how many videos do they have?":
    query2='''select channel_name as channelname,total_videos as no_of_videos from channels order by total_videos desc '''
    cursor.execute(query2)
    mydb.commit()
    x2=cursor.fetchall()
    df1=pd.DataFrame(x2,columns=["channel name","No of videos"])
    st.write(df1)

elif question=="3.What are the top 10 most viewed videos and their respective channels?":
    query3='''select views as views,channel_name as channelname,title as videotitle from videos where views is not null order by views desc limit 10'''
    cursor.execute(query3)
    mydb.commit()
    x3=cursor.fetchall()
    df2=pd.DataFrame(x3,columns=["views","channel name","video title"])
    st.write(df2)

elif question=="4.How many comments were made on each video and what are their corresponding video names?":
    query4='''select comments as no_of_comments,title as videotitle from videos where comments is not null'''
    cursor.execute(query4)
    mydb.commit()
    x4=cursor.fetchall()
    df3=pd.DataFrame(x4,columns=["No of comments","video title"])
    st.write(df3)

elif question=="5.Which videos have the highest number of likes and what are their corresponding channel names?":
    query5='''select title as videotitle,channel_name as channelname,likes as likecount from videos where likes is not null order by likes desc '''
    cursor.execute(query5)
    mydb.commit()
    x5=cursor.fetchall()
    df4=pd.DataFrame(x5,columns=["channel name","video title","Like count"])
    st.write(df4)

elif question=="6.What is the total number of likes and dislikes for each video and what are their corresponding video names?":
    query6='''select likes as likecount,title as videotitle from videos'''
    cursor.execute(query6)
    mydb.commit()
    x6=cursor.fetchall()
    df5=pd.DataFrame(x6,columns=["Like count","video title"])
    st.write(df5)

elif question=="7.What is the total number of views for each channel and what are their corresponding channel names?":
    query7='''select channel_name as channelname,views as totalviews from channels'''
    cursor.execute(query7)
    mydb.commit()
    x7=cursor.fetchall()
    df6=pd.DataFrame(x7,columns=["channel name","Total views"])
    st.write(df6)

elif question=="8.What are the names of all the channels that have published videos in the year 2022?":
    query8='''select title as videotitle,published_date as videoreleased,channel_name as channelname from videos where extract(year from published_date)=2022'''
    cursor.execute(query8)
    mydb.commit()
    x8=cursor.fetchall()
    df7=pd.DataFrame(x8,columns=["video title","published date","channel name"])
    st.write(df7)


elif question=="9.What is the average duration of all videos in each channel and what are their corresponding channel names?":
    query9='''select channel_name as channelname,AVG(duration) as averageduration from videos group by channel_name'''
    cursor.execute(query9)
    mydb.commit()
    x9=cursor.fetchall()
    df8=pd.DataFrame(x9,columns=["channel name","Average duration"])

    x9=[]
    for index,row in df8.iterrows():
        channel_title=row["channel name"]
        average_duration=row["Average duration"]
        average_duration_str=str(average_duration)
        x9.append(dict(channeltitle=channel_title,Avgduration=average_duration_str))
    df9=pd.DataFrame(x9)
    st.write(df9)

elif question=="10.Which videos have the highest number of comments and what are their corresponding channel names?":
    query10='''select title as videotitle,channel_name as channelname,comments as comments from videos where comments is not null order by comments desc'''
    cursor.execute(query10)
    mydb.commit()
    x10=cursor.fetchall()
    df10=pd.DataFrame(x10,columns=["video title","channel name","comments"])
    st.write(df10)
    
st.balloons()

    