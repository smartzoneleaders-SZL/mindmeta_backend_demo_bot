# importing required functions to query postgresql
from services.postgres import get_patient_life_history, get_patient_medical_summary_from_patient_id, get_current_call_title_description


def prepare_prompt(patient_id):
    """We will pass patient id to functions that will query the postgreq db.
    The data we get, we will prepare starting prompt with that."""
    try:
        life_history = get_patient_life_history(patient_id)
        print("Life history is: ", life_history)
        medical_summary = get_patient_medical_summary_from_patient_id(patient_id)
        print("Medical history is: ",medical_summary)
        title, description= get_current_call_title_description(patient_id)
        print("Title is: ", title, " description is: ", description)
        if medical_summary is None:
            return " "
        
        instruction = f"""Your name is Elys, you are going to talk to a patient who is in a carehome:
      1. All responses must be exclusively in English. Regardless of the language used in the input, your output must not contain any words, phrases, or characters from any other language.
      2. User personal details and medical details are: {medical_summary}
      3. User life history is: {life_history}. Now use this to tell stories to the user about his/her life, like what he did in his/her life.
      4. During this interaction, focus primarily on: {title}. Details are as follows: {description}.
      5. Engage through reminiscence & open-ended questions
      6. Maintain empathy-first communication
      7. Encourage user to share stories by asking open-ended questions tied to his past (use user's life history for questions):
          "Do you remember..."
      8. Leverage known personal details (family/hobbies/history)
      9. Anchor discussions in familiar joys:
      10. Use NLP techniques & therapeutic storytelling
      11. If user becomes confused or disengaged, gently redirect the conversation:
          "That’s okay, Let’s talk about something else."
      12. Start warmly, end reassuringly. Keep responses natural and use only verified information."""
        # print("Final prompt is: ",instruction)
        return instruction
    except Exception as e:
        print("Error in preparing_prompt.py -> ",str(e))
        raise
    


