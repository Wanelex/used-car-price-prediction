#!/usr/bin/env python3

"Firebase Firestore initialization script"

import sys
import os
from loguru import logger

# Configure logger
logger.remove()
logger.add(
    sys.stdout,
    format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)


def check_firebase_credentials():
    """Check if Firebase credentials file exists"""
    cred_path = "./serviceAccountKey.json"

    if not os.path.exists(cred_path):
        logger.error(f"Firebase credentials file not found: {cred_path}")
        logger.error("\nTo use Firebase:")
        logger.error("1. Go to https://console.firebase.google.com")
        logger.error("2. Create a new project (or select existing)")
        logger.error("3. Go to Project Settings → Service Accounts")
        logger.error("4. Click 'Generate New Private Key'")
        logger.error("5. Save the JSON file as 'serviceAccountKey.json' in project root")
        logger.error("\nExample path: C:\\Users\\pc\\Harf Yapbozu\\used-car-price-prediction\\serviceAccountKey.json")
        return False

    logger.success(f"Firebase credentials found: {cred_path}")
    return True


def init_firebase():
    """Initialize Firebase and set up Firestore collections"""
    try:
        logger.info("Initializing Firebase Firestore...")

        from backend.storage.firebase_repository import FirestoreRepository

        # Initialize repository (which initializes Firebase)
        repo = FirestoreRepository()
        logger.success("Firebase Firestore connected successfully!")

        # Create initial document structure (Firestore auto-creates collections)
        # We'll create a metadata collection to verify write access
        db = repo.db
        metadata_doc = {
            'initialized_at': __import__('datetime').datetime.utcnow(),
            'app_version': '1.0',
            'status': 'ready'
        }

        db.collection('_metadata').document('app_info').set(metadata_doc)
        logger.success("Firestore collections ready")
        logger.info("   Collections that will be created on first use:")
        logger.info("   - car_listings (stores cleaned car data)")
        logger.info("   - listing_images (stores image metadata)")
        logger.info("   - _metadata (app information)")

        return True

    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {str(e)}")
        logger.error(f"\nTroubleshooting:")
        logger.error("1. Verify serviceAccountKey.json is in the correct location")
        logger.error("2. Verify Firebase credentials are valid")
        logger.error("3. Ensure Firestore is enabled in Firebase Console")
        logger.error("4. Check internet connection")
        return False


def main():
    """Main initialization function"""
    logger.info("=" * 60)
    logger.info("Firebase Firestore Initialization")
    logger.info("=" * 60)

    # Step 1: Check credentials
    if not check_firebase_credentials():
        logger.error("\nFirebase initialization aborted")
        return False

    # Step 2: Initialize Firebase
    if not init_firebase():
        logger.error("\nFirebase initialization failed")
        return False

    logger.success("\n" + "=" * 60)
    logger.success("Firebase Firestore is ready to use!")
    logger.success("=" * 60)
    logger.info("\nYou can now:")
    logger.info("1. Run: python run_api.py")
    logger.info("2. Test crawling with sahibinden URLs")
    logger.info("3. Data will be automatically saved to Firestore")
    logger.info("\nFirebase Console: https://console.firebase.google.com")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
