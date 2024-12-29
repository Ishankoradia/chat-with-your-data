"""
Basic bot that can remember your previous messages & respond with that context
You can use conditional words to stop the chat like "quit", "q", "exit", "bye"
"""

import os
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from typing_extensions import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, AnyMessage, HumanMessage
from langchain_openai import ChatOpenAI
import operator


load_dotenv()


class BotState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]


class ChatWithDatabaseBot:
    def __init__(self):
        self.system = "You are a chat bot that can generate database queries. Respond with a sql if you know about it otherwise give the best answer from the context of previous messages"
        self.model = ChatOpenAI(model="gpt-4o-mini")
        graph = StateGraph(BotState)
        graph.add_node("ask_openai", self.call_openai)
        graph.add_node("ask_human", self.ask_human)

        graph.add_edge(START, "ask_openai")
        graph.add_edge("ask_openai", "ask_human")
        graph.add_conditional_edges(
            "ask_human",
            self.should_continue,
            {
                True: "ask_openai",
                False: END,
            },
        )
        self.graph = graph.compile()

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

    def should_continue(self, state: BotState):
        return state["messages"][-1].content not in ["quit", "q", "exit", "bye"]

    def generate_graph_png(self):
        image_bytes = self.graph.get_graph().draw_mermaid_png()
        image = Image.open(BytesIO(image_bytes))
        image.save(os.path.dirname(os.path.abspath(__file__)) + "/graph_v2.png")


if __name__ == "__main__":
    bot = ChatWithDatabaseBot()
    bot.generate_graph_png()
    config = {"configurable": {"thread_id": 1}}
    # this will trigger the graph and stream events so you undrestand whats happening
    for event in bot.graph.stream({"messages": []}, config=config):
        for v in event.values():
            print(v["messages"][-1].content)