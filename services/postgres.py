from fastapi import HTTPException
# Postgres Models
from model.demo_history import DemoHistory
from model.patient import Patient
from model.summary import Summary
from model.life_history import LifeHistory
from model.schedule_call import ScheduledCall
from model.care_home import CareHome
from model.demo_access import DemoAccess

# For getting postgresql db 
from db.postgres import get_db

# To check the 48 hours access of demo user
from datetime import datetime, timezone







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



def did_change_status_to_completed(patient_id:str)->str:
    """This function gets called when a scheduled call ends and now we have to change its status
    INPUT:
        - patient_id
    OUTPUT:

        - True
        - If there is a problem an Error will be raised (raise)""" 
    try:
        db = next(get_db())
        status_change = db.query(ScheduledCall).filter(
                        ScheduledCall.patient_id == patient_id,
                        ScheduledCall.status == "scheduled").update({"status": "completed"}, synchronize_session=False)
        if status_change != 1:
            print('Critical error')
            print(status_change)
            
        db.commit()
        return True
    except Exception as e:
        print("Error in postgres while changing status -> ",str(e))
        raise


def get_time_from_schedule_call_using_patient_id(patient_id):
    """Get time of scheduled call in seconds"""
    try:
        db= next(get_db())
        time = (db.query(ScheduledCall.call_duration).filter(ScheduledCall.patient_id == patient_id, ScheduledCall.status == "scheduled").first())

        call_duration = time[0] if time else False

        print(call_duration)
        if call_duration:
            return call_duration
        else:
            print("Call duration is none that's what the db sent")
            raise
    
    except Exception as e:
        print("Error on get_time_from_schedule_call_using_patient_id in postgres.py -> ",str(e))
        raise



def get_carehome_email(patient_id):
    """To get carehome email from patient_id. This is so we can send carehome email,
        when user show suicidal thoughts"""
    try:
        db = next(get_db())
        carehome_email = db.query(CareHome.email) .join(Patient, CareHome.id == Patient.carehome_id).filter(Patient.id == patient_id).scalar()
        print("carehome email is: ",carehome_email)
        return carehome_email
    except Exception as e:
        print("Error while getiitng carehome email in -> get_carehome_email function in postgres",str(e))
    


def create_new_demo_access(email, name, phone_number):
    """To create demo access in postgress"""
    try:
        db = next(get_db())
        new_user = DemoAccess(
        name=name,
        email=email,
        phone_number=phone_number, remaining_time = 1800)
        db.add(new_user)
        db.commit()
        return True
    except Exception as e:
        print("Error on database is: ",str(e))
        raise HTTPException(status_code=500, detail="Error while creating user")

def validate_user(user_email: str):
    try:
        db = next(get_db())
        user = db.query(DemoAccess).filter(DemoAccess.email == user_email).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found, please register first")
        if user is not None:
            if user.access is False:
                raise HTTPException(status_code=403, detail="Your request hasn't been accepted yet by the admin.")

            current_time = datetime.now(timezone.utc)
            if current_time > user.access_upto:
                raise HTTPException(status_code=403, detail="Access expired.")

            return True
    except HTTPException as he:
        # Propagate HTTPException without modification.
        raise he
    except Exception as e:
        print("Error in postgres services: ", str(e))
        raise HTTPException(status_code=500, detail="Error in db")
    

def does_user_exist(email: str):
    """ To check if a user already exist using its email
    INPUT:
        - user email
    OUTPUT:
        - False: if user doesn't exist
        - True: if user does exist"""
    try:
        db = next(get_db())
        does_exist = db.query(DemoAccess).filter(DemoAccess.email == email).first()
        if does_exist is None:
            return False
        else:
            return True
        
    except Exception as e:
        print("Error in does user exist: ",str(e))
        raise HTTPException(status_code=500,detail={"details": "Error while checking if user already exist"})
    




def grant_access_by_email(email: str):
    """TO give access to user, this function will put True in False's place in access column of demo user"""
    db = next(get_db())
    user = db.query(DemoAccess).filter(DemoAccess.email == email, DemoAccess.access == False).first()
    
    if user:
        user.access = True  # Update the access field
        db.commit()  # Commit the changes
        db.refresh(user)  # Refresh the session
        return True  # Return the updated user object
    else:
        return False
    



def update_time_of_call(db,email: str, time: int):
    """Update this call time with the previous so user won't surpass the 30 min time"""
    try:
        user = db.query(DemoAccess).filter(DemoAccess.email == email).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found (which is impossible)")
        if user.access:
            user.remaining_time = time
            db.commit()  
            db.refresh(user)
            return True
        else:
            raise HTTPException(status_code=400, detail="User doesn't have access yet, access hasn't been granted by the admin")
    except HTTPException as ht:
        raise ht
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error occured while updating database time")



def is_user_eligible_for_call(db, email: str):
    try:
        user = db.query(DemoAccess).filter(DemoAccess.email == email).first()
        
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        if user.access:
            if user.remaining_time >= 1:
                return True, user.remaining_time  
            else:
                return False, 0
        else:
            raise HTTPException(status_code=400, detail="User doesn't have access")

    except HTTPException as hp:
        raise hp  #
    except Exception as e:
        print("Error in eligibility is: ",str(e))
        raise HTTPException(status_code=500, detail="An Error has occured while checking eligibility")

def delete_user_from_db(email: str):
    try:
        db = next(get_db())
        user = db.query(DemoAccess).filter(DemoAccess.email == email).first()
        db.delete(user)
        db.commit()
        return True
    except Exception as e:
        print("Error in deleting user from db: ",str(e))
        raise HTTPException(status_code=500, detail="An Error has occured while deleting user from db")

def add_demo_history(email: str, name: str, phone_number: str):
    """To add email to the demo history table"""
    try:
        db = next(get_db())
        new_history = DemoHistory(email=email, name =name , phone_number = phone_number)
        db.add(new_history)
        db.commit()
        return True
    except Exception as e:
        print("Error in adding demo history: ",str(e))
        raise HTTPException(status_code=500, detail="An Error has occured while adding demo history")

# Service to give access to user
def give_access_to_user_by_admin(email: str):
    try:
        db = next(get_db())
        user = db.query(DemoAccess).filter(DemoAccess.email == email).first()
        user.access = True
        db.commit()
        db.refresh(user)
        return True
    except Exception as e:
        print("Error in giving access to user by admin: ",str(e))
        raise HTTPException(status_code=500, detail="An Error has occured while giving access to user by admin")
    


def get_demo_user_by_email(email: str):
    """To get all the details of the demo user using its email"""
    try:
        db= next(get_db())
        user = db.query(DemoAccess).filter(DemoAccess.email == email).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail="An Error occured in while getting user data from the db")


    
def get_voice_from_db(patient_id):
    """To get voice from the db"""
    db = next(get_db())
    user = db.query(Patient).filter(Patient.id == patient_id).first()
    if user:
        return user.hume_voice
    else:
        False