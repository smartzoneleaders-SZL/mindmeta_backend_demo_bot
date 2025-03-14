
# Postgres Models
from model.patient import Patient
from model.summary import Summary
from model.life_history import LifeHistory
from model.schedule_call import ScheduledCall

# For getting postgresql db 
from db.postgres import get_db


def get_carehome_id_from_patient_id(patient_id: str) -> str:
    """
    Given a patient_id, returns the associated carehome_id.
    
    :param patient_id: The UUID of the patient.
    :param session: SQLAlchemy session instance.
    :return: The carehome_id for the patient, or None if the patient does not exist.
    """
    try:
        db = next(get_db()) 
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        return patient.carehome_id if patient else None
    except Exception as e: 
        print("Error in postgres.py in services: ",str(e))
        raise


def get_patient_medical_summary_from_patient_id(patient_id :str) ->str:
    """ Given patient_id in the parameters.
    Function will use get_db to access postgresql and will query 'summaries' Table to
    get the summary of patient details that where created using gpt from the data
    that the care home added as patient medical history
    
    INPUT:
        - patient_id
    OUTPUT:
        - patient_medical_history_summary(str)
    """
    try:
        db =next(get_db()) 
        patient_medical_history_summary = db.query(Summary).filter(Summary.patient_id == patient_id).first()
        # print("Patient medical history summary is: ",patient_medical_history_summary.content)
        if(patient_medical_history_summary is None):
            return False
        return patient_medical_history_summary.content if patient_medical_history_summary else None
    except Exception as e:
        print("Error in get_patient_summary_from_patient_id function inside postgres in services -> ",str(e))
        raise


def get_patient_life_history(patient_id:str) -> str:
    """To get patient life history that the family members added.
    INPUT:
        - patient_id
        
    OUTPUT:
        - patient life history(str)"""
    try:
        db = next(get_db()) 
        patient_life_history = db.query(LifeHistory).filter(LifeHistory.patient_id == patient_id).first()
        # print("Patient life history added by the family is: ",patient_life_history.history)
        if(patient_life_history is None):
            return False
        return patient_life_history.history if patient_life_history else None
    
    except Exception as e:
        print("Error in get_patient_life_history function inside postgres in services -> ",str(e))
        raise


def get_current_call_title_description(patient_id: str) ->str:
    """To get the title and desription (what to talk about in today's call)
    INPUT: 
        - patient_id
    OUTPUT:
        - title (str)
        - what_to_talk (what to talk about in the call)"""
    try:
        db = next(get_db())
        what_to_talk = db.query(ScheduledCall).filter(ScheduledCall.patient_id == patient_id,ScheduledCall.status == 'scheduled').first()

        if what_to_talk is None:
            return False
        # print("What to talk about in the call: ",what_to_talk.title, " and its description is: ",what_to_talk.description)
        return what_to_talk.title, what_to_talk.description
    except Exception as e:
        print("Error in get_current_call_title_description inside postgres in services -> ",str(e))
        raise        

