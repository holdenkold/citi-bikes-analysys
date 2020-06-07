import numpy as np
import pandas as pd

def distance(s_lat, s_lng, e_lat, e_lng):

   # approximate radius of earth in km
   R = 6369.075

   s_lat = np.deg2rad(s_lat)                    
   s_lng = np.deg2rad(s_lng)     
   e_lat = np.deg2rad(e_lat)                       
   e_lng = np.deg2rad(e_lng)  

   d = np.sin((e_lat - s_lat)/2)**2 + np.cos(s_lat)*np.cos(e_lat) * np.sin((e_lng - s_lng)/2)**2

   return 2 * R * np.arcsin(np.sqrt(d))

def bearing(s_lat, s_lng, e_lat, e_lng):
    s_lat = np.deg2rad(s_lat)                    
    s_lng = np.deg2rad(s_lng)     
    e_lat = np.deg2rad(e_lat)                       
    e_lng = np.deg2rad(e_lng)  
    delta = e_lng - s_lng
    a = np.arctan2(np.sin(delta) * np.cos(e_lat), 
                   np.cos(s_lat) * np.sin(e_lat) - np.sin(s_lat) * np.cos(e_lat) * np.cos(delta))
    return (np.rad2deg(a) + 360) % 360

def manhattandistance(df):
    b = bearing(df['start station latitude'], df['start station longitude'], 
                df['end station latitude'], df['end station longitude'])
    d = distance(df['start station latitude'], df['start station longitude'], 
                 df['end station latitude'], df['end station longitude'])
    angle = np.deg2rad((b - 29) % 90)
    return d * (np.sin(angle) + np.cos(angle))

def prepareData(df):
    df["starttime"]= pd.to_datetime(df["starttime"], format="%Y-%m-%d %H:%M:%S.%f")
    df["stoptime"] = pd.to_datetime(df["stoptime"], format="%Y-%m-%d %H:%M:%S.%f")
    df = df[(df['tripduration'] > 120) & (df['tripduration'] < 7200)]
    df = df[(df['birth year'] <= 2000) & (df['birth year'] >= 1960)]
    df = df[df['start station id'] != df['end station id']]
    return df

files = ["201906-citibike-tripdata.csv",
         "201907-citibike-tripdata.csv",
         "201908-citibike-tripdata.csv",
         "201909-citibike-tripdata.csv",
         "201910-citibike-tripdata.csv",
         "201911-citibike-tripdata.csv"]
df = pd.read_csv(files[0])
del files[0]
for f in files:
    tmpdf = pd.read_csv(f)
    df = df.append(tmpdf)
    del tmpdf
df = prepareData(df)

df['distance'] = manhattandistance(df)
df['speed'] = df['distance'] / df['tripduration'] * 3600

df['hour'] = df.starttime.dt.hour
groupedbystarthour = df.groupby("hour")
meanpacesbyhour = groupedbystarthour.mean()['speed']
meanpacesbyhour.to_csv("meanpacesbyhour.csv")
del groupedbystarthour

df['weekday'] = df.starttime.dt.weekday
groupedbyweekday = df.groupby('weekday')
meanpacebyweekday = groupedbyweekday.mean()['speed']
meanpacebyweekday.to_csv("meanpacebyweekday.csv")
del groupedbyweekday

mpg = df[df["gender"] != 0].groupby("gender").mean()["speed"]
mpg.to_csv("mpg.csv")

mpy = df.groupby("birth year").mean()["speed"]
mpy.to_csv("mpy.csv")