import os
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.base import BaseCheckpointSaver, empty_checkpoint
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


def clear_thread(thread_id: str):
    """
    Connects to the db and removes all references of thread_id
    """

    try:
        with conn.cursor() as cursor:
            # Start a transaction block
            cursor.execute("BEGIN;")

            # Execute multiple delete queries
            delete_query_1 = "DELETE FROM checkpoint_blobs WHERE thread_id = %s"
            delete_query_2 = "DELETE FROM checkpoint_writes WHERE thread_id = %s"
            delete_query_3 = "DELETE FROM checkpoints WHERE thread_id = %s"
            cursor.execute(delete_query_1, (thread_id,))
            cursor.execute(delete_query_2, (thread_id,))
            cursor.execute(delete_query_3, (thread_id,))

            # Commit the transaction
            cursor.execute("COMMIT;")
            print(f"Deleted all references of thread_id: {thread_id}")
    except Exception as e:
        # Rollback the transaction in case of error
        cursor.execute("ROLLBACK;")
        print(f"Error deleting thread_id {thread_id}: {e}")
