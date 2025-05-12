from fastapi import HTTPException
from sqlalchemy import func

# Postgres Models
from model.demo_access import DemoAccess

# For getting postgresql db 
from db.postgres import get_db

from sqlalchemy.orm import Session

from model.demo_history import DemoHistory

def all_users_with_time_analytics(db: Session):
    """
    Fetches all demo users with their name, email, and total time spent.
    
    Args:
        db (Session): SQLAlchemy database session provided by the route.
    
    Returns:
        list: A list of dictionaries containing user information:
              [
                {
                  "name": "User Name",
                  "email": "user@example.com",
                  "total_time": 600  # time in seconds
                },
                ...
              ]
    
    Raises:
        HTTPException: If there's an error querying the database.
    """
    try:
        # Query all users from the demo_user table (which are actived by admin)
        users = db.query(DemoAccess).filter(DemoAccess.access == True).all()
        
        # Format the results
        result = [
            {
                "name": user.name,
                "email": user.email,
                "phone_number": user.phone_number,
                "remaining_time": user.remaining_time,
            }
            for user in users
        ]
        
        return result
    
    except Exception as e:
        print(f"Error in all_users_with_time_analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
def never_used_percentage(db: Session):
    """
    Fetches the percentage of users that have never used the bot (remaining_time is 1800).
    Also returns a list of those users with their name, email, and phone number.
    
    Args:
        db (Session): SQLAlchemy database session provided by the route.
    
    Returns:
        dict: Dictionary containing percentage and list of users who never used the bot:
              {
                "percentage": 75.5,
                "users": [
                  {
                    "name": "User Name",
                    "email": "user@example.com",
                    "phone_number": "0xxxxxx0"
                  },
                  ...
                ]
              }
    
    Raises:
        HTTPException: If there's an error querying the database.
    """
    try:
        # Query all users from the demo_user table (which are actived by admin)
        total_users = db.query(DemoAccess).filter(DemoAccess.access == True).count()
        
        # Get users who never used the bot
        users_never_used_query = db.query(DemoAccess).filter(DemoAccess.access == True).filter(DemoAccess.remaining_time == 1800).all()
        users_never_used_count = len(users_never_used_query)
        
        # Prevent division by zero
        if total_users == 0:
            return {"percentage": 0.0, "users": []}
        
        # Calculate the percentage
        percentage = (users_never_used_count / total_users) * 100
        
        # Format user data
        users_list = [
            {
                "name": user.name,
                "email": user.email,
                "phone_number": user.phone_number
            }
            for user in users_never_used_query
        ]
        
        return {"percentage": percentage, "users": users_list}
    
    except Exception as e:
        print(f"Error in never_used_percentage: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
def all_users_not_accessed_by_admin(db: Session):
    """
    Fetches all demo users not have yet access to bot with their name, email.
    
    Args:
        db (Session): SQLAlchemy database session provided by the route.
    
    Returns:
        list: A list of dictionaries containing user information:
              [
                {
                  "name": "User Name",
                  "email": "user@example.com",
                  "phone_number": "0xxxxxx0"
                },
                ...
              ]
    
    Raises:
        HTTPException: If there's an error querying the database.
    """
    try:
        # Query all users from the demo_user table (which are actived by admin)
        users = db.query(DemoAccess).filter(DemoAccess.access == False).all()
        
        # Format the results
        result = [
            {
                "name": user.name,
                "email": user.email,
                "phone_number": user.phone_number,
            }
            for user in users
        ]
        
        return result
    
    except Exception as e:
        print(f"Error in all_users_not_accessed_by_admin: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

def percentage_of_not_accessed_by_admin_users(db: Session):
    """
    Fetches the percentage of users that have not activated the bot (access is False).
    """
    try:
        total_users = db.query(DemoAccess).count()  # Count all users instead of just activated ones
        users_not_activated = db.query(DemoAccess).filter(DemoAccess.access == False).count()
        
        # Prevent division by zero
        if total_users == 0:
            return 0.0
            
        percentage = (users_not_activated / total_users) * 100
        
        return percentage
    
    except Exception as e:
        print(f"Error in percentage_of_not_activated_users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
# check percentage of users registered back after their 30 minutes usage (having email in both demo_history and demo_access)
def percentage_of_users_came_back_after_30_minutes_usage(db: Session):
    """
    Fetches the percentage of users that have registered back after their 30 minutes usage.
    Also returns a list of those users with their name, email, and phone number.
    
    Returns:
        Dictionary with percentage and users data.
    """
    try:
        # users who have email in both demo_history and demo_access / total users in demo_access table
        total_users = db.query(DemoAccess).count()
        
        # Create a proper subquery that selects just the email column
        access_emails = db.query(DemoAccess.email).subquery()
        
        # Get users in DemoHistory whose emails are in the access_emails subquery
        users_came_back_emails = db.query(DemoHistory.email).filter(DemoHistory.email.in_(access_emails)).distinct().all()
        users_came_back_count = len(users_came_back_emails)
        
        # Get the full user details from DemoAccess for these emails
        emails_list = [user.email for user in users_came_back_emails]
        user_details = db.query(DemoAccess).filter(DemoAccess.email.in_(emails_list)).all()
        
        # prevent division by zero
        if total_users == 0:
            return {"percentage": 0.0, "users": []}

        percentage = (users_came_back_count / total_users) * 100
        
        # Format user data
        users_list = [
            {
                "name": user.name,
                "email": user.email,
                "phone_number": user.phone_number
            } 
            for user in user_details
        ]
        
        return {"percentage": percentage, "users": users_list}
    except Exception as e:
        print(f"Error in percentage_of_users_came_back_after_30_minutes_usage: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

def people_never_registered_back_after_first_usage(db: Session):
    """
    Fetches the percentage of users who used the bot exactly once and never registered back.
    Also returns a list of those users with their email (since name and phone are not available in DemoHistory).
    
    Returns:
        Dictionary with percentage and users data.
    """
    try:
        # Count total unique users in DemoHistory
        total_unique_users = db.query(DemoHistory.email).distinct().count()
        
        # Get emails that appear exactly once in DemoHistory
        emails_used_once = (
            db.query(DemoHistory.email)
            .group_by(DemoHistory.email)
            .having(func.count(DemoHistory.email) == 1)
            .subquery()
        )
        
        # Fetch emails of users who used once and never registered
        users_never_registered = (
            db.query(DemoHistory)
            .filter(DemoHistory.email.in_(emails_used_once))
            .filter(~DemoHistory.email.in_(db.query(DemoAccess.email)))
            .all()
        )
        print("USers are: ", users_never_registered)
        emails_used_once_not_registered = len(users_never_registered)
        
        # Prevent division by zero
        if total_unique_users == 0:
            return {"percentage": 0.0, "users": []}
        
        # Calculate the percentage
        percentage = (emails_used_once_not_registered / total_unique_users) * 100
        
        # Format user data
        users_list = [{"email": user.email, "name": user.name, "phone_number": user.phone_number} for user in users_never_registered]
        
        return {"percentage": percentage, "users": users_list}
    
    except Exception as e:
        print(f"Error in people_never_registered_back_after_first_usage: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

