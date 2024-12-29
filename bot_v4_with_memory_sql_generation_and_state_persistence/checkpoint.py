import os
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg import Connection
from dotenv import load_dotenv


load_dotenv()

conn = Connection.connect(
    "postgresql://{username}:{password}@{server}:{port}/{database}".format(
        **{
            "username": os.environ["DB_USER"],
            "password": os.environ["DB_PASSWORD"],
            "server": os.environ["DB_HOST"],
            "port": os.environ["DB_PORT"],
            "database": os.environ["DB_NAME"],
        }
    ),
    **(
        {
            "autocommit": True,
            "prepare_threshold": 0,
        }
    ),
)
checkpointer = PostgresSaver(conn)
