from langchain_groq import ChatGroq

import os
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage

from dotenv import load_dotenv
# For memory
from langgraph.graph import START, MessagesState, StateGraph


load_dotenv()


user_info ="Pete Hillman , a 78-year-old retired postmaster from Bristol, UK, who is living with early-stage dementia in a care home. Pete has two sons name 'jake' and 'jack' and a daughter name 'margurete'. Pete like to listen to colbie caillat. "







if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")




chat_prompt = ChatPromptTemplate.from_messages([
    ("system", f"""You're Pete's compassionate dementia companion.Your name is 'Elys' you were created my 'mindmeta engineers' Use memory to:
1. Don't say 'Hello' or 'Hi' or other word simply talk with the user
2. If Pete says 'Hello [user name]' or 'Hi' or similar words  in the chat, do NOT greet him assume taht you have already greeted the user which you have. If user however still says "hello" or "hi" simply say:
Your response: Yes, I'm here shall we continue our talk.
3. Your Responses should be a bit short but if needed they can be of normal size.
4. Maintain empathy-first communication
5. Make stories by using information tied to his past:
    "Pete, remember the first day you started working at the post office. How much fun was it going to your office on your first day remember you forgot to take your office bag that was a bummer you had to go back to your house to pick it up?"
6. Leverage known personal details (family/hobbies/history)
     user infomation is: {user_info}
7. Anchor discussions in familiar joys:
"Your love for classical music is truly inspiring! Who’s your favorite composer? Was it Mozart or Beethoven?"
8. Handle interruptions gracefully
6. Use NLP techniques & therapeutic storytelling
8. If Pete becomes confused or disengaged, gently redirect the conversation:
    "That’s okay, Pete! Let’s talk about something else. Have you spoken to Phil recently?"

Start warmly, end reassuringly. Keep responses natural and focused on verified information."""),
    MessagesPlaceholder("messages")
])











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
    # Build prompt template dynamically
    dynamic_tpl = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(prompt_template),
        HumanMessagePromptTemplate.from_template("{user_input}")
    ])

    input_data = {"input": user_text}
    config = {
        "configurable": {
            "thread_id": chat_id,
            "prompt_template": dynamic_tpl
        }
    }

    result = chat_with_model.invoke(input_data, config=config)
    return result["messages"][-1].content





from datetime import datetime

async def greet_user(name):

    messages = [
    SystemMessage("Greet user like 'good morning how is your day going' or 'good afternoon  how is my favarite person doing today' based on the time. Don't use these same examples be creative make your own"),
    HumanMessage(f"user name is : {name} and time right now is: {datetime.now().strftime('%I:%M %p')}"),]

    return model.invoke(messages)






# Get langchain chat history
from langchain_core.messages import AIMessage

def get_chat_history(chat_with_model, call_id):
    try:
        config = {"configurable": {"thread_id": str(call_id)}}
        state_snapshot = chat_with_model.get_state(config)
        messages = state_snapshot.values.get("messages", [])

        pairs = []
        user_msg = None

        for msg in messages:
            if isinstance(msg, HumanMessage):
                user_msg = msg.content
            elif isinstance(msg, AIMessage) and user_msg:
                pairs.append({
                    "user_query": user_msg,
                    "ai_response": msg.content
                })
                user_msg = None  

        return pairs

    except Exception as e:
        print(f"Error: {e}")
        return []

















