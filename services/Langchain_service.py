from langchain_groq import ChatGroq

import os
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage

from dotenv import load_dotenv
# For memory
from langgraph.graph import START, MessagesState, StateGraph


load_dotenv()




if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


from langgraph.checkpoint.memory import MemorySaver


# langchain_essentials.py

from langchain.chat_models import init_chat_model
from langchain.schema import BaseMessage
from typing import TypedDict, List


class ChatState(TypedDict):
    input: str
    messages: List[BaseMessage]


model = init_chat_model("gpt-3.5-turbo-0125", model_provider="openai")
# model = init_chat_model("llama3-8b-8192", model_provider="groq")
# model = init_chat_model("claude-3-5-sonnet-latest", model_provider="anthropic")



def generate_chat_prompt(state: ChatState, config):
    tpl: ChatPromptTemplate = config["configurable"]["prompt_template"]
    user_msg = tpl.format_messages(user_input=state["input"])
    
    # Append prompt messages to history
    messages = state.get("messages", []) + user_msg
    return {"input": state["input"], "messages": messages}

def call_model(state: ChatState, config):
    messages = state.get("messages", [])
    response = model.invoke(messages[-5:]) 
    messages.append(response)
    return {"input": state["input"], "messages": messages}


workflow = StateGraph(state_schema=ChatState)
workflow.add_node("chat_prompt", generate_chat_prompt)
workflow.add_node("model", call_model)
workflow.add_edge(START, "chat_prompt")
workflow.add_edge("chat_prompt", "model")

memory = MemorySaver()
chat_with_model = workflow.compile(checkpointer=memory)









from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
def invoke_model(user_text: str, chat_id: str, prompt_template: str):
    dynamic_tpl = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(prompt_template),
        HumanMessagePromptTemplate.from_template("{user_input}")
    ])

    config = {
        "configurable": {
            "thread_id": chat_id,
            "prompt_template": dynamic_tpl
        }
    }

    # Pull existing state to preserve context
    try:
        current_state = chat_with_model.get_state(config)
        messages = current_state.values.get("messages", [])
    except:
        messages = []

    input_data = {
        "input": user_text,
        "messages": messages
    }

    result = chat_with_model.invoke(input_data, config=config)
    return result["messages"][-1].content






from datetime import datetime

async def greet_user(name):

    messages = [
    SystemMessage("Greet user like 'good morning how is your day going' or 'good afternoon  how is my favarite person doing today' based on the time. Don't use these same examples be creative make your own"),
    HumanMessage(f"user name is : {name} and time right now is: {datetime.now().strftime('%I:%M %p')}"),]

    return model.invoke(messages)



















