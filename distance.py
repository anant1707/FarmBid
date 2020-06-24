import pandas as pd
import numpy as np
from geopy.distance import geodesic
import psycopg2 as psql

df=pd.read_excel('dataset/lat.xlsx')
conn=psql.connect("dbname='PROJECT' user='postgres' host='localhost' password='Anant@1707'")
cur=conn.cursor()

for i in range(df.shape[0]):
    for j in range(1,df.shape[0]):
        cur.execute(F"INSERT INTO DISTANCES VALUES{(df.iloc[i,0],df.iloc[j,0],(geodesic(df.iloc[i,[1,2]],df.iloc[j,[1,2]]).km))}")
        conn.commit()
        print(df.iloc[i,0],df.iloc[j,0],(geodesic(df.iloc[i,[1,2]],df.iloc[j,[1,2]]).km))

