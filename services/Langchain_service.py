from langchain_groq import ChatGroq
import getpass
import os
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage

from dotenv import load_dotenv
# For memory
from langgraph.graph import START, MessagesState, StateGraph


load_dotenv()


user_info ="Pete Hillman , a 78-year-old retired postmaster from Bristol, UK, who is living with early-stage dementia in a care home "

# # Set the API key
# os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# # Initialize the model



if not os.environ.get("GROQ_API_KEY"):
#   os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
  os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")



chat_prompt = ChatPromptTemplate.from_messages([
    ("system", f"""You're Pete's compassionate dementia companion. Your name is Elys Use memory to:
1. Engage through reminiscence & open-ended questions
2. Maintain empathy-first communication
3. Encourage user to share stories by asking open-ended questions tied to his past:
    "Pete, do you remember the first day you started working at the post office? What was it like stepping into that role?"
3. Leverage known personal details (family/hobbies/history)
     user infomation is: {user_info}
4. Anchor discussions in familiar joys:
"Your love for classical music is truly inspiring! Who’s your favorite composer? Was it Mozart or Beethoven?"
5. Handle interruptions gracefully
6. Use NLP techniques & therapeutic storytelling
7. If Pete becomes confused or disengaged, gently redirect the conversation:
    "That’s okay, Pete! Let’s talk about something else. Have you spoken to Phil recently?"

Start warmly, end reassuringly. Keep responses natural and focused on verified information."""),
    MessagesPlaceholder("messages")
])







from langgraph.checkpoint.memory import MemorySaver


# langchain_essentials.py

from langchain.chat_models import init_chat_model


# Initialize the chat model
# model = init_chat_model("gpt-3.5-turbo-0125", model_provider="openai")
model = init_chat_model("gemma2-9b-it", model_provider="groq")

# Define the function that calls the model
def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": [response]}


# Define a node function for generating the prompt
def generate_chat_prompt(state: MessagesState):
    state["messages"] = chat_prompt.format_messages(messages=[])
    return state

# Now define your workflow:
workflow = StateGraph(state_schema=MessagesState)
workflow.add_node("chat_prompt", generate_chat_prompt)
workflow.add_node("model", call_model)

# Define edges to establish the flow:
workflow.add_edge(START, "chat_prompt")
workflow.add_edge("chat_prompt", "model")

memory = MemorySaver()
# Compile the workflow with the memory checkpointer
chat_with_model = workflow.compile(checkpointer=memory)







