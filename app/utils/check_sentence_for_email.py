def check_and_send_email(sentence):
    """
    Checks if the sentence contains any trigger phrases indicating self-harm.
    If found, an alert email is sent.
    """

    triggers = ["kill myself", "end my life", "want to die", "killing myself", "wanna die now"]

    sentence_lower = sentence.lower()
    
 
    if any(trigger in sentence_lower for trigger in triggers):
        return True
    else:
        return False