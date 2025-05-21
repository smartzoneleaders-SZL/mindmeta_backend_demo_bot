import re

def remove_thinking(text):
    # Remove everything from <think> to </think>
    cleaned_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    return cleaned_text