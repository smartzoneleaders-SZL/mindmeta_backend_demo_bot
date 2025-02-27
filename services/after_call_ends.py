


def get_chat_hisory(chat_with_model,call_id):
    try:
        config = {"configurable": {"thread_id": call_id}}
        state_snapshot = chat_with_model.get_state(config)
        print("History is: ",state_snapshot.values["messages"])
        return True
    except Exception as e:
        return False
    