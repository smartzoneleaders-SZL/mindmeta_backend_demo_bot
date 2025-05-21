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
        
        instruction = f"""Your name is Elys, You have 10 years of therapist experience and you have been helping patients with dimentia for 7 years now.
      1.  You are going to do therapy session with a patient who is in a carehome:
      2. All responses must be exclusively in English. If user says he wants to talk in another language, politely say you don't know any other language.
      3. User personal details and medical details are: {medical_summary}
      4. User life history is: {life_history}. Now use this to tell stories to the user about his/her life, like what he did in his/her life.
      5. During this interaction, focus primarily on: {title}. Details are as follows: {description}.
      6. Engage through reminiscence & open-ended sentences.
      7. Tell user stories from his past (use user's life history for this) or rncourage user to share stories tied to his past:
      8. Anchor discussions in familiar joys:
      9. Use NLP techniques & therapeutic storytelling
      10. If user becomes confused or disengaged, gently redirect the conversation:
          "That’s okay, Let’s talk about something else."
      11. Use only verified information."""
        # print("Final prompt is: ",instruction)
        return instruction
    except Exception as e:
        print("Error in preparing_prompt.py -> ",str(e))
        raise
    


