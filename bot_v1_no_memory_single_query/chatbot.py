"""
Basic bot that can you ask one off queries to
"""

import os
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv()


class BotState(TypedDict):
    message: str


class ChatWithDatabaseBot:
    def __init__(self):
        self.system = "You are a chat bot that can generate database queries. Respond with a sql if you know about it"
        self.model = ChatOpenAI(model="gpt-4o-mini")
        graph = StateGraph(BotState)
        graph.add_node("ask_openai", self.call_openai)
        graph.add_edge(START, "ask_openai")
        graph.add_edge("ask_openai", END)
        self.graph = graph.compile()

    def call_openai(self, state: BotState):
        messages = [state["message"]]
        if self.system:
            messages = [SystemMessage(content=self.system)] + [state["message"]]

        result_message = self.model.invoke(messages)
        return {"message": result_message}

    def generate_graph_png(self):
        image_bytes = self.graph.get_graph().draw_mermaid_png()
        image = Image.open(BytesIO(image_bytes))
        image.save(os.path.dirname(os.path.abspath(__file__)) + "/graph_v1.png")


if __name__ == "__main__":
    bot = ChatWithDatabaseBot()
    user_message = input("Ask something: ")
    response = bot.graph.invoke({"message": user_message})
    print(response["message"].content)
    bot.generate_graph_png()
