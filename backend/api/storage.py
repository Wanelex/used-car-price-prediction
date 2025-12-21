from typing import Dict, Any

# Global in-memory job storage
# (Later this can be replaced with Redis / DB)
jobs_storage: Dict[str, Dict[str, Any]] = {}
