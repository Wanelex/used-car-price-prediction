"""Firebase Authentication utilities"""

from typing import Optional, Dict, Any
import firebase_admin
from firebase_admin import auth as firebase_auth
from loguru import logger


class FirebaseAuthManager:
    """Manage Firebase authentication"""

    @staticmethod
    def create_user(email: str, password: str) -> Optional[str]:
        """
        Create a new user

        Returns: user_id or None
        """
        try:
            user = firebase_auth.create_user(email=email, password=password)
            logger.success(f"Created user: {email}")
            return user.uid
        except firebase_auth.EmailAlreadyExistsError:
            logger.warning(f"User already exists: {email}")
            return None
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return None

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            user = firebase_auth.get_user_by_email(email)
            return {
                'uid': user.uid,
                'email': user.email,
                'display_name': user.display_name,
                'created_at': user.user_metadata.creation_timestamp,
            }
        except firebase_auth.UserNotFoundError:
            return None
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return None

    @staticmethod
    def delete_user(uid: str) -> bool:
        """Delete user"""
        try:
            firebase_auth.delete_user(uid)
            logger.info(f"Deleted user: {uid}")
            return True
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return False

    @staticmethod
    def update_user_display_name(uid: str, display_name: str) -> bool:
        """Update user display name"""
        try:
            firebase_auth.update_user(uid, display_name=display_name)
            logger.info(f"Updated display name for {uid}: {display_name}")
            return True
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return False

    @staticmethod
    def verify_id_token(id_token: str) -> Optional[Dict[str, Any]]:
        """Verify Firebase ID token"""
        try:
            decoded = firebase_auth.verify_id_token(id_token)
            return decoded
        except firebase_auth.InvalidIdTokenError:
            logger.warning("Invalid ID token")
            return None
        except firebase_auth.ExpiredIdTokenError:
            logger.warning("Expired ID token")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return None
