"""
Basic bot that can remember your previous messages & respond with that context
You can use conditional words to stop the chat like "quit", "q", "exit", "bye"
Additionally, this bot can generate SQL queries based on the user input via vanna.ai for the warehouse
Also, this bot can persist the state of the bot in the database
"""

import os
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from typing_extensions import TypedDict, Annotated, Union
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, AnyMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import operator

from checkpoint import checkpointer, clear_thread
from sql_generation.main import generate_sql_cached

load_dotenv()


class BotState(TypedDict):
    last_sql_generated: Union[str, None]
    messages: Annotated[list[AnyMessage], operator.add]


class ChatWithDatabaseBot:
    LOOK_BACK_MESSAGES = (
        5  # this is the number of messages to look back to generate the sql
    )

    def __init__(self):
        self.system = "You are a chat bot that can generate database queries. Respond with a sql if you know about it otherwise give the best answer from the context of previous messages"
        self.model = ChatOpenAI(model="gpt-4o-mini")
        graph = StateGraph(BotState)
        # graph.add_node("train", self.train_warehouse_for_sql_generation) # this is being done via the seed.py
        graph.add_node("ask_human", self.ask_human)
        graph.add_node("generate_sql", self.generate_sql)
        graph.add_node("ask_openai", self.call_openai)

        graph.add_edge(START, "ask_human")
        graph.add_conditional_edges(
            "ask_human",
            self.should_continue_chat,
            {
                True: "generate_sql",
                False: END,
            },
        )
        graph.add_conditional_edges(
            "generate_sql",
            self.is_sql_generated,
            {True: "ask_human", False: "ask_openai"},
        )
        graph.add_edge("ask_openai", "ask_human")
        self.graph = graph.compile(checkpointer=checkpointer)

    def call_openai(self, state: BotState):
        # print("State length : ", len(state["messages"])) # if you uncomment this line, you will see the length increasing
        messages = state["messages"]
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages

        result_message = self.model.invoke(messages)
        return {"messages": [result_message]}

    def ask_human(self, state: BotState):
        user_input = input("Ask something: ")
        return {"messages": [HumanMessage(content=user_input)]}

    def generate_sql(self, state: BotState):
        all_messages: list[AnyMessage] = state.get("messages", [])
        print(
            "State length : ", len(all_messages)
        )  # if you uncomment this line, you will see the length increasing

        # get last n messages from state exclude the last one
        previous_context = "Use this information as context when the question sounds like a follow up : "
        for i in range(
            len(all_messages) - 2, len(all_messages) - 2 - self.LOOK_BACK_MESSAGES, -1
        ):
            if i >= 0:
                previous_context += f"{'Question' if all_messages[i].type == 'human' else 'Answer'} : {all_messages[i].content}\n"

        user_query = all_messages[-1].content
        sql_str = generate_sql_cached(user_query, initial_prompt=previous_context)
        return {
            "messages": [AIMessage(content=sql_str)],
            "last_sql_generated": sql_str,
        }

    def should_continue_chat(self, state: BotState):
        can_continue = state["messages"][-1].content not in ["quit", "q", "exit", "bye"]
        return can_continue

    def is_sql_generated(self, state: BotState):
        return state["last_sql_generated"] is not None

    def generate_graph_png(self):
        image_bytes = self.graph.get_graph().draw_mermaid_png()
        image = Image.open(BytesIO(image_bytes))
        image.save(os.path.dirname(os.path.abspath(__file__)) + "/graph_v5.png")


if __name__ == "__main__":
    import argparse

    config = {"configurable": {"thread_id": "1"}}

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset the thread and delete all message history",
    )
    args = parser.parse_args()
    if args.reset:
        clear_thread(config["configurable"]["thread_id"])

    bot = ChatWithDatabaseBot()
    bot.generate_graph_png()

    # load the previous messages in the thread for the latest state
    for m in bot.graph.get_state(config=config).values.get("messages", []):
        print(f"|> [{m.type}] : ", m.content)

    # this will trigger the graph and stream events so you undrestand whats happening
    for event in bot.graph.stream({"messages": []}, config=config):
        for v in event.values():
            if len(v["messages"]) > 0:
                print("Bot responded with : ", v["messages"][-1].content)
