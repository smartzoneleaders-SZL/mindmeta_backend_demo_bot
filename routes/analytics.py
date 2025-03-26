from fastapi import APIRouter
from fastapi.responses import JSONResponse

# for services
from services.postgre_for_analytics import all_users_not_accessed_by_admin, all_users_with_time_analytics, never_used_percentage, people_never_registered_back_after_first_usage, percentage_of_not_accessed_by_admin_users, percentage_of_users_came_back_after_30_minutes_usage

from fastapi import HTTPException

# for db
from fastapi import Depends
from sqlalchemy.orm import Session
from db.postgres import get_db

router = APIRouter()

@router.get("/users-with-time")
def get_all_users_with_time(db: Session = Depends(get_db)):
    """
    Endpoint to fetch analytics data for all demo users.

    Returns:
        JSON response with a list of all users and their usage data:
    """
    try:
        users_data = all_users_with_time_analytics(db)
        return JSONResponse(
            content={"status": True, "data": users_data},
            status_code=200
        )
    except HTTPException as http_exc:
        return JSONResponse(
            content={"status": False, "detail": http_exc.detail},
            status_code=http_exc.status_code
        )
    except Exception as e:
        print(f"Error in get_users_analytics: {str(e)}")
        return JSONResponse(
            content={"status": False, "detail": "An unexpected error occurred"},
            status_code=500
        )
    
@router.get("/never-used-users-percentage")
def get_never_used_users_percentage(db: Session = Depends(get_db)):
    """
    Endpoint to fetch analytics data for demo users percentage that never used the bot.

    Returns:
        JSON response with a percentage of users that never used the bot:
    """
    try:
        users_data = never_used_percentage(db)
        return JSONResponse(
            content={"status": True, "data": users_data},
            status_code=200
        )
    except HTTPException as http_exc:
        return JSONResponse(
            content={"status": False, "detail": http_exc.detail},
            status_code=http_exc.status_code
        )
    except Exception as e:
        print(f"Error in get_never_used_users: {str(e)}")
        return JSONResponse(
            content={"status": False, "detail": "An unexpected error occurred"},
            status_code=500
        )

@router.get("/not-accessed-by-admin-users-percentage")
def get_not_accessed_by_admin_users_percentage(db: Session = Depends(get_db)):
    """
    Endpoint to fetch analytics data for demo users percentage that have not accessed to use the bot by admin.

    Returns:
        JSON response with a percentage of users that have not accessed to use the bot by admin:
    """
    try:
        users_data = percentage_of_not_accessed_by_admin_users(db)
        return JSONResponse(content={"status": True, "data": users_data}, status_code=200)
    except HTTPException as http_exc:
        return JSONResponse(
            content={"status": False, "detail": http_exc.detail},
            status_code=http_exc.status_code
        )
    except Exception as e:
        print(f"Error in get_not_activated_users: {str(e)}")
        return JSONResponse(
            content={"status": False, "detail": "An unexpected error occurred"},
            status_code=500
        )

@router.get("/all-users-not-accessed-by-admin")
def get_all_users_not_accessed_by_admin(db: Session = Depends(get_db)):
    """
    Endpoint to fetch analytics data for all demo users that have not accessed to use the bot by admin.
    """
    try:
        users_data = all_users_not_accessed_by_admin(db)
        return JSONResponse(content={"status": True, "data": users_data}, status_code=200)
    except HTTPException as http_exc:
        return JSONResponse(
            content={"status": False, "detail": http_exc.detail},
            status_code=http_exc.status_code
        )
    except Exception as e:
        print(f"Error in get_all_users_not_accessed_by_admin: {str(e)}")
        return JSONResponse(
            content={"status": False, "detail": "An unexpected error occurred"},
            status_code=500
        )
    
@router.get("/registered-back-after-30-minutes-usage-percentage")
def percentage_of_users_registered_back_after_30_minutes_usage(db: Session = Depends(get_db)):
    """
    Endpoint to fetch analytics data for demo users percentage that registered back after their 30 minutes usage.
    """
    try:
        users_data = percentage_of_users_came_back_after_30_minutes_usage(db)
        return JSONResponse(content={"status": True, "data": users_data}, status_code=200)
    except HTTPException as http_exc:
        return JSONResponse(
            content={"status": False, "detail": http_exc.detail},
            status_code=http_exc.status_code
        )
    except Exception as e:
        print(f"Error in get_users_registered_back_after_30_minutes_usage: {str(e)}")
        return JSONResponse(content={"status": False, "detail": "An unexpected error occurred"}, status_code=500)
    
@router.get("/never-registered-back-after-first-usage")
def percentage_of_people_never_registered_back_after_first_usage(db: Session = Depends(get_db)):
    """
    Endpoint to fetch analytics data for demo users percentage that never registered back after their first usage.
    """
    try:
        users_data = people_never_registered_back_after_first_usage(db)
        return JSONResponse(content={"status": True, "data": users_data}, status_code=200)
    except HTTPException as http_exc:
        return JSONResponse(content={"status": False, "detail": http_exc.detail}, status_code=http_exc.status_code)
    except Exception as e:
        print(f"Error in count_of_people_never_registered_back_after_first_usage: {str(e)}")
        return JSONResponse(content={"status": False, "detail": "An unexpected error occurred"}, status_code=500)
    
