'''
Install in local: sudo apt install postgresql postgresql-contrib-y
Inside Env: pip install psycopg2-binary
Entering into Postgresql: sudo -i -u postgres
Setting username and password: (postgres@Sriram:~$ )
    password for "sriram" (not for postgresql) : 19705600

    (myenv) sriram@Sriram:~/Documents/FastAPI$ sudo -i -u postgres psql
    postgres=# CREATE USER fastapi_user WITH PASSWORD '1234';
    postgres-# CREATE DATABASE fastapi_db OWNER fastapi_user;
    postgres-# GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi_user;
    postgres-# \q
    postgres@Sriram:~$ exit
    logout
    (myenv) sriram@Sriram:~/Documents/FastAPI$ 
'''
'''
This Implementation is done in the Personal Project..!
'''