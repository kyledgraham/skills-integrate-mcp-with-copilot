# Firebase Setup Guide

This application now uses Google Cloud Firestore for persistent data storage. Follow these steps to set up Firebase for your project.

## Prerequisites

- A Google account
- Access to Google Cloud Console

## Step 1: Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project"
3. Enter your project name (e.g., "Mergington High School")
4. Follow the setup wizard and create the project

## Step 2: Enable Firestore Database

1. In Firebase Console, go to your project
2. In the left sidebar, click "Firestore Database"
3. Click "Create database"
4. Start in production mode (or test mode for development)
5. Choose your database location and click "Enable"

## Step 3: Create Service Account Credentials

1. Go to Firebase Console > Project Settings (gear icon)
2. Click the "Service Accounts" tab
3. Click "Generate New Private Key"
4. This downloads a JSON file - save it as `firebase-credentials.json` in your project root
5. **IMPORTANT: Never commit this file to Git!** Add it to `.gitignore`

## Step 4: Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your Firebase credentials path:
   ```
   FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
   ```

## Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 6: Run the Application

```bash
python -m uvicorn src.app:app --reload
```

The application will:
- Connect to Firebase
- Initialize the Firestore database with default activities (if the database is empty)
- Serve the API at `http://localhost:8000`

## Firestore Database Structure

The database has a single collection: **activities**

Each document in the `activities` collection has this structure:

```json
{
  "activity_name": {
    "description": "Activity description",
    "schedule": "When the activity meets",
    "max_participants": 20,
    "participants": ["email@example.com", "another@example.com"]
  }
}
```

## Benefits of Firebase

✅ **Persistent Storage** - Data survives app restarts  
✅ **Real-time Sync** - Multiple users see updates instantly  
✅ **Scalability** - Handles growth without code changes  
✅ **Built-in Security** - Firestore Security Rules  
✅ **Backup & Recovery** - Automatic backups  
✅ **Future Features** - Ready for authentication, file storage, etc.

## Security Considerations

- Keep `firebase-credentials.json` secret - add to `.gitignore`
- Never commit credentials to version control
- Use Firestore Security Rules to restrict access (see [Firestore Security Rules Documentation](https://firebase.google.com/docs/firestore/security/start))
- For production, use Application Default Credentials with a service account

## Troubleshooting

### Connection Errors
- Verify `firebase-credentials.json` is in the project root
- Check that Firestore Database is enabled in Firebase Console
- Ensure your service account has read/write permissions

### "Collection not found" Error
- This is expected on first run - the app will create and initialize the database
- Check Firebase Console > Firestore Database to see if documents were created

### Permission Denied
- In Firebase Console, go to Firestore > Rules
- Ensure rules allow read/write for your service account
