import os
from functools import lru_cache

from vanna.openai import OpenAI_Chat
from vanna.pgvector import PG_VectorStore


class MyVanna(PG_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        PG_VectorStore.__init__(
            self,
            config={
                "connection_string": "postgresql+psycopg://{username}:{password}@{server}:{port}/{database}".format(
                    **{
                        "username": os.environ["PGVECTOR_USER"],
                        "password": os.environ["PGVECTOR_PASSWORD"],
                        "server": os.environ["PGVECTOR_HOST"],
                        "port": os.environ["PGVECTOR_PORT"],
                        "database": os.environ["PGVECTOR_DB"],
                    }
                )
            },
        )
        OpenAI_Chat.__init__(
            self,
            config={
                "api_key": os.environ["OPENAI_API_KEY"],
                "model": "gpt-4o-mini",
            },
        )


@lru_cache(maxsize=1)
def setup_vanna():
    vn = MyVanna()
    vn.connect_to_postgres(
        host=os.environ["WAREHOUSE_HOST"],
        dbname=os.environ["WAREHOUSE_DB"],
        user=os.environ["WAREHOUSE_USER"],
        password=os.environ["WAREHOUSE_PASSWORD"],
        port=os.environ["WAREHOUSE_PORT"],
    )
    return vn


def generate_questions_cached():
    vn = setup_vanna()
    return vn.generate_questions()


def generate_sql_cached(question: str):
    vn = setup_vanna()
    return vn.generate_sql(question=question, allow_llm_to_see_data=True)


def is_sql_valid_cached(sql: str):
    vn = setup_vanna()
    return vn.is_sql_valid(sql=sql)


def run_sql_cached(sql: str):
    vn = setup_vanna()
    return vn.run_sql(sql=sql)


def should_generate_chart_cached(question, sql, df):
    vn = setup_vanna()
    return vn.should_generate_chart(df=df)


def generate_plotly_code_cached(question, sql, df):
    vn = setup_vanna()
    code = vn.generate_plotly_code(question=question, sql=sql, df=df)
    return code


def generate_plot_cached(code, df):
    vn = setup_vanna()
    return vn.get_plotly_figure(plotly_code=code, df=df)


def generate_followup_cached(question, sql, df):
    vn = setup_vanna()
    return vn.generate_followup_questions(question=question, sql=sql, df=df)


def generate_summary_cached(question, df):
    vn = setup_vanna()
    return vn.generate_summary(question=question, df=df)


def setup_training_plan_and_execute():
    vn = setup_vanna()
    df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")
    plan = vn.get_training_plan_generic(df_information_schema)
    vn.train(plan=plan)


def remove_training_data():
    vn = setup_vanna()
    vn.remove_training_data()
