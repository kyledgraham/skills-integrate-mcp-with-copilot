"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.

Now powered by Firebase Firestore for persistent data storage!
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Initialize Firebase
try:
    # Check if Firebase is already initialized
    firebase_admin.get_app()
except ValueError:
    # Initialize Firebase with credentials
    firebase_creds_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
    if os.path.exists(firebase_creds_path):
        creds = credentials.Certificate(firebase_creds_path)
        firebase_admin.initialize_app(creds)
    else:
        # If running locally without credentials, initialize without credentials
        # In production, use Application Default Credentials or environment variables
        firebase_admin.initialize_app()

# Get Firestore client
db = firestore.client()

# Reference to activities collection
activities_collection = db.collection("activities")

# Default activities to seed the database if empty
default_activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}

# Initialize database with default activities if empty
def init_database():
    """Initialize Firestore database with default activities if collection is empty."""
    docs = activities_collection.stream()
    if not list(docs):
        print("Initializing database with default activities...")
        for activity_name, activity_data in default_activities.items():
            activities_collection.document(activity_name).set(activity_data)
        print("Database initialization complete!")

# Initialize database on startup
init_database()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    """Get all activities from Firestore database."""
    activities_dict = {}
    try:
        docs = activities_collection.stream()
        for doc in docs:
            activities_dict[doc.id] = doc.to_dict()
        return activities_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching activities: {str(e)}")


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    try:
        # Get activity from Firestore
        activity_doc = activities_collection.document(activity_name).get()
        
        # Validate activity exists
        if not activity_doc.exists:
            raise HTTPException(status_code=404, detail="Activity not found")

        # Get the specific activity
        activity = activity_doc.to_dict()

        # Validate student is not already signed up
        if email in activity["participants"]:
            raise HTTPException(
                status_code=400,
                detail="Student is already signed up"
            )

        # Check if activity is at capacity
        if len(activity["participants"]) >= activity["max_participants"]:
            raise HTTPException(
                status_code=400,
                detail="Activity is at maximum capacity"
            )

        # Add student to activity
        activity["participants"].append(email)
        
        # Update in Firestore
        activities_collection.document(activity_name).update({
            "participants": activity["participants"]
        })
        
        return {"message": f"Signed up {email} for {activity_name}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during signup: {str(e)}")


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    try:
        # Get activity from Firestore
        activity_doc = activities_collection.document(activity_name).get()
        
        # Validate activity exists
        if not activity_doc.exists:
            raise HTTPException(status_code=404, detail="Activity not found")

        # Get the specific activity
        activity = activity_doc.to_dict()

        # Validate student is signed up
        if email not in activity["participants"]:
            raise HTTPException(
                status_code=400,
                detail="Student is not signed up for this activity"
            )

        # Remove student from activity
        activity["participants"].remove(email)
        
        # Update in Firestore
        activities_collection.document(activity_name).update({
            "participants": activity["participants"]
        })
        
        return {"message": f"Unregistered {email} from {activity_name}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during unregister: {str(e)}")
