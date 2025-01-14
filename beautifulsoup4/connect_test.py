import pymysql
import pymysql.cursors
from dynaconf import Dynaconf

settings = Dynaconf(
    settings_file = ('../settings.toml')
)

conn = pymysql.connect(
    database= settings.db_name,
    user= settings.db_user,
    password= settings.db_pass,
    host= '192.168.1.173',
    port= 3417
)

def test():
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM `restaurant`;')
    results = cursor.fetchall()
    return results

print(test())