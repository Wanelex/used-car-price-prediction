"""
Session Manager
Handles cookie persistence, fingerprint consistency, and session state
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from loguru import logger
import hashlib


class SessionManager:
    """
    Manages browser sessions with persistent cookies and fingerprints
    """

    def __init__(self, session_dir: str = ".sessions"):
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(exist_ok=True)
        self.current_session: Optional[Dict[str, Any]] = None

    def create_session(self, domain: str, fingerprint: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new session for a domain

        Args:
            domain: The target domain
            fingerprint: Optional custom fingerprint

        Returns:
            Session ID
        """
        session_id = self._generate_session_id(domain)

        session_data = {
            "session_id": session_id,
            "domain": domain,
            "created_at": datetime.utcnow().isoformat(),
            "last_used": datetime.utcnow().isoformat(),
            "cookies": [],
            "local_storage": {},
            "fingerprint": fingerprint or self._generate_fingerprint(),
            "user_agent": None,
            "proxy": None,
            "success_count": 0,
            "failure_count": 0
        }

        self.current_session = session_data
        self._save_session(session_id, session_data)

        logger.info(f"Created new session: {session_id}")
        return session_id

    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load an existing session

        Args:
            session_id: The session ID

        Returns:
            Session data or None if not found
        """
        session_file = self.session_dir / f"{session_id}.json"

        if not session_file.exists():
            logger.warning(f"Session not found: {session_id}")
            return None

        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            # Check if session is expired (30 days)
            created_at = datetime.fromisoformat(session_data["created_at"])
            if datetime.utcnow() - created_at > timedelta(days=30):
                logger.warning(f"Session expired: {session_id}")
                self.delete_session(session_id)
                return None

            # Update last used
            session_data["last_used"] = datetime.utcnow().isoformat()
            self._save_session(session_id, session_data)

            self.current_session = session_data
            logger.info(f"Loaded session: {session_id}")
            return session_data

        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {str(e)}")
            return None

    def get_or_create_session(self, domain: str) -> Dict[str, Any]:
        """
        Get existing session for domain or create new one

        Args:
            domain: The target domain

        Returns:
            Session data
        """
        # Try to find existing session for this domain
        session_id = self._generate_session_id(domain)
        session_data = self.load_session(session_id)

        if session_data:
            return session_data

        # Create new session
        return self.load_session(self.create_session(domain))

    def save_cookies(self, session_id: str, cookies: List[Dict[str, Any]]):
        """
        Save cookies to session

        Args:
            session_id: The session ID
            cookies: List of cookie dicts
        """
        session_data = self.load_session(session_id)
        if not session_data:
            logger.error(f"Cannot save cookies - session not found: {session_id}")
            return

        session_data["cookies"] = cookies
        session_data["last_used"] = datetime.utcnow().isoformat()
        self._save_session(session_id, session_data)

        logger.debug(f"Saved {len(cookies)} cookies to session {session_id}")

    def get_cookies(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get cookies from session

        Args:
            session_id: The session ID

        Returns:
            List of cookies
        """
        session_data = self.load_session(session_id)
        if not session_data:
            return []

        return session_data.get("cookies", [])

    def save_local_storage(self, session_id: str, local_storage: Dict[str, Any]):
        """
        Save localStorage data to session

        Args:
            session_id: The session ID
            local_storage: localStorage dict
        """
        session_data = self.load_session(session_id)
        if not session_data:
            logger.error(f"Cannot save localStorage - session not found: {session_id}")
            return

        session_data["local_storage"] = local_storage
        session_data["last_used"] = datetime.utcnow().isoformat()
        self._save_session(session_id, session_data)

        logger.debug(f"Saved localStorage to session {session_id}")

    def get_local_storage(self, session_id: str) -> Dict[str, Any]:
        """
        Get localStorage data from session

        Args:
            session_id: The session ID

        Returns:
            localStorage dict
        """
        session_data = self.load_session(session_id)
        if not session_data:
            return {}

        return session_data.get("local_storage", {})

    def update_session_stats(self, session_id: str, success: bool):
        """
        Update session success/failure statistics

        Args:
            session_id: The session ID
            success: Whether the request was successful
        """
        session_data = self.load_session(session_id)
        if not session_data:
            return

        if success:
            session_data["success_count"] += 1
        else:
            session_data["failure_count"] += 1

        session_data["last_used"] = datetime.utcnow().isoformat()
        self._save_session(session_id, session_data)

    def get_session_fingerprint(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the fingerprint for a session

        Args:
            session_id: The session ID

        Returns:
            Fingerprint dict
        """
        session_data = self.load_session(session_id)
        if not session_data:
            return None

        return session_data.get("fingerprint")

    def delete_session(self, session_id: str):
        """
        Delete a session

        Args:
            session_id: The session ID
        """
        session_file = self.session_dir / f"{session_id}.json"

        try:
            if session_file.exists():
                session_file.unlink()
                logger.info(f"Deleted session: {session_id}")
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {str(e)}")

    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all sessions

        Returns:
            List of session summaries
        """
        sessions = []

        for session_file in self.session_dir.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)

                sessions.append({
                    "session_id": session_data["session_id"],
                    "domain": session_data["domain"],
                    "created_at": session_data["created_at"],
                    "last_used": session_data["last_used"],
                    "success_count": session_data["success_count"],
                    "failure_count": session_data["failure_count"]
                })

            except Exception as e:
                logger.error(f"Failed to read session file {session_file}: {str(e)}")
                continue

        return sessions

    def clean_old_sessions(self, days: int = 30):
        """
        Delete sessions older than specified days

        Args:
            days: Age threshold in days
        """
        count = 0
        threshold = datetime.utcnow() - timedelta(days=days)

        for session_file in self.session_dir.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)

                last_used = datetime.fromisoformat(session_data["last_used"])

                if last_used < threshold:
                    session_file.unlink()
                    count += 1
                    logger.debug(f"Cleaned old session: {session_data['session_id']}")

            except Exception as e:
                logger.error(f"Failed to clean session {session_file}: {str(e)}")
                continue

        logger.info(f"Cleaned {count} old sessions")

    def _generate_session_id(self, domain: str) -> str:
        """
        Generate a consistent session ID for a domain

        Args:
            domain: The domain

        Returns:
            Session ID
        """
        # Create hash from domain to get consistent ID
        domain_clean = domain.replace("http://", "").replace("https://", "").replace("/", "")
        return hashlib.md5(domain_clean.encode()).hexdigest()[:16]

    def _generate_fingerprint(self) -> Dict[str, Any]:
        """
        Generate a consistent browser fingerprint

        Returns:
            Fingerprint dict
        """
        import random

        return {
            "canvas": random.randint(1000000, 9999999),
            "webgl": random.randint(1000000, 9999999),
            "audio": random.randint(1000000, 9999999),
            "screen_width": random.choice([1920, 1366, 1536, 1440, 1280]),
            "screen_height": random.choice([1080, 768, 864, 900, 720]),
            "timezone_offset": random.choice([-8, -7, -6, -5, -4, 0, 1, 2, 3]),
            "hardware_concurrency": random.choice([2, 4, 6, 8, 12]),
            "device_memory": random.choice([2, 4, 8, 16]),
            "platform": random.choice(["Win32", "MacIntel", "Linux x86_64"]),
            "language": random.choice(["en-US", "en-GB", "en"]),
            "color_depth": random.choice([24, 32])
        }

    def _save_session(self, session_id: str, session_data: Dict[str, Any]):
        """
        Save session data to file

        Args:
            session_id: The session ID
            session_data: The session data
        """
        session_file = self.session_dir / f"{session_id}.json"

        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to save session {session_id}: {str(e)}")


# Global session manager instance
session_manager = SessionManager()

logger.info("Session manager initialized")
