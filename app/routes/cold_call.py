from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Depends

# import schema
from schema.cold_call import ColdCallRequest

# For  db Session
from sqlalchemy.orm import Session
from model.cold_call import ColdCall
from db.postgres import get_db



router = APIRouter()


@router.put("/edit-cold-call-script")
def edit_cold_call_script(request: ColdCallRequest, db: Session = Depends(get_db)):
    """To Edit cold call script"""
    try:
        updated_rows = (
            db.query(ColdCall)
            .filter(ColdCall.id == 1)
            .update({"cold_call_message": request.script}, synchronize_session=False)
        )
        db.commit()

        if updated_rows == 0:
            return JSONResponse(status_code=404, content={"detail": "Error while updating the cold call"})
        else:
            return JSONResponse(status_code=200, content={"message": "Cold call message updated"})
    except Exception as e:
        raise HTTPException(status_code=500, detail="An Error has occurred")

    
@router.get("/get-cold-call-script")
def get_cold_call_script(db: Session = Depends(get_db)):
    """To get cold call script from the db"""
    try:
        script = db.query(ColdCall).filter(ColdCall.id == 1).first()
        print("data is: ",script.cold_call_message)
        if script:
            return JSONResponse(status_code=200, content={"cold_call_script": script.cold_call_message})
        else:
            return HTTPException(status_code=404, detail="Not Found")
    except Exception as e:
        return HTTPException(status_code=500, detail="An Error has occured")


    

