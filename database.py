
import mysql.connector

def get_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rishabh@252010",
        database="ecotrack",
        charset="utf8",
    )
    return connection


connection = get_connection()

if connection.is_connected():
    print("EcoTrack Database Connected Successfully!")

connection.close()
