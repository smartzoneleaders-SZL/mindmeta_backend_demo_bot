from services.postgres import get_time_from_schedule_call_using_patient_id



def get_time_of_call(patient_id):
    """Will take patient_id as parameter and will call functions to get data of scheduled call
    of that patient.
        INPUT:
            - patient_id
        OUTPUT:
            - time in seconds like 300 seconds"""
    time_seconds = get_time_from_schedule_call_using_patient_id(patient_id)
    return time_seconds