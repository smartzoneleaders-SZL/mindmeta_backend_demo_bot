from model.patient import Patient

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
        db = get_db()
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        return patient.carehome_id if patient else None
    except Exception as e: 
        print("Error in postgres.py in services: ",str(e))
        raise
