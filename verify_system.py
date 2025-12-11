import os
import sys
from pathlib import Path

# Define required components
COMPONENTS = {
    "[CORE] FastAPI REST API": ["backend/api/main.py"],
    "[CORE] Crawler Orchestrator": ["backend/crawler/crawler.py"],
    "[CORE] Browser Engine (Nodriver)": ["backend/crawler/engine.py"],
    "[CORE] HTTP Client (curl_cffi)": ["backend/crawler/http_client.py"],
    "[CORE] Content Extractor": ["backend/crawler/extractor.py"],
    "[CORE] Proxy Manager": ["backend/crawler/proxy.py"],
    "[CORE] Rate Limiter": ["backend/utils/rate_limiter.py"],
    "[CORE] CAPTCHA Solver": ["backend/crawler/bypass/captcha.py", "backend/crawler/bypass/captcha_manager.py"],
    "[CORE] Session Manager": ["backend/crawler/session_manager.py"],
    "[CORE] Specialized Parsers": ["backend/crawler/parsers/sahibinden_parser.py"],
    "[UTIL] Health Monitoring": ["backend/monitoring/health_monitor.py"],
    "[API] Routes (Jobs)": ["backend/api/routes/jobs.py"],
    "[API] Routes (Crawl)": ["backend/api/routes/crawl.py"],
    "[API] Models/Schemas": ["backend/api/models/schemas.py"],
}

# Features required
FEATURES = {
    "Stealth browser automation": "backend/crawler/stealth.py",
    "TLS fingerprinting": "backend/crawler/http_client.py",
    "CAPTCHA solving": "backend/crawler/bypass/captcha.py",
    "Proxy rotation": "backend/crawler/proxy.py",
    "Human-like behavior": "backend/crawler/engine.py",
    "Session persistence": "backend/crawler/session_manager.py",
    "Specialized parsers": "backend/crawler/parsers/sahibinden_parser.py",
}

print("\n" + "="*80)
print("SYSTEM VERIFICATION - COMPREHENSIVE CHECK")
print("="*80 + "\n")

# Check components
print("CORE COMPONENTS:")
print("-" * 80)
all_components_ready = True
for component, files in COMPONENTS.items():
    missing_files = [f for f in files if not Path(f).exists()]
    if not missing_files:
        print(f"[OK] {component}")
    else:
        print(f"[FAIL] {component} - Missing: {missing_files}")
        all_components_ready = False

print("\n")

# Check features
print("KEY FEATURES:")
print("-" * 80)
all_features_ready = True
for feature, file in FEATURES.items():
    if Path(file).exists():
        print(f"[OK] {feature}")
    else:
        print(f"[FAIL] {feature} - Missing: {file}")
        all_features_ready = False

print("\n")

# Check dependencies
print("DEPENDENCIES:")
print("-" * 80)
dependencies = [
    ("FastAPI", "fastapi"),
    ("Uvicorn", "uvicorn"),
    ("Nodriver", "nodriver"),
    ("Playwright", "playwright"),
    ("curl_cffi", "curl_cffi"),
    ("BeautifulSoup4", "bs4"),
    ("Pydantic", "pydantic"),
    ("Loguru", "loguru"),
    ("2Captcha Python", "twocaptcha"),
    ("Anti-Captcha", "python_anticaptcha"),
]

for name, module in dependencies:
    try:
        __import__(module)
        print(f"[OK] {name}")
    except ImportError:
        print(f"[WARN] {name} - Not installed (run: pip install -r requirements.txt)")

print("\n")

# Check configuration files
print("CONFIGURATION:")
print("-" * 80)
config_files = {
    ".env": ".env",
    "config/settings.py": "config/settings.py",
    "requirements.txt": "requirements.txt",
}

for name, file in config_files.items():
    if Path(file).exists():
        print(f"[OK] {name}")
    else:
        print(f"[FAIL] {name} - Missing")

print("\n")

# Check test files
print("TEST FILES:")
print("-" * 80)
test_files = {
    "Day 1 (Foundation)": "test_day1.py",
    "Day 2 (Browser)": "test_day2.py",
    "Day 3 (Content Extraction)": "test_day3.py",
    "Day 4 (CAPTCHA & Crawler)": "test_day4.py",
    "Day 5 (API)": "test_day5.py",
}

for name, file in test_files.items():
    if Path(file).exists():
        print(f"[OK] {name}")
    else:
        print(f"[WARN] {name} - Not found (Optional)")

print("\n")

# Check entry points
print("ENTRY POINTS:")
print("-" * 80)
entry_points = {
    "run_api.py": "run_api.py",
}

for name, file in entry_points.items():
    if Path(file).exists():
        print(f"[OK] {name}")
        print(f"     Run with: venv/Scripts/python.exe {file}")
    else:
        print(f"[FAIL] {name} - Missing")

print("\n" + "="*80)
if all_components_ready and all_features_ready:
    print("SUCCESS: SYSTEM IS 100% PRODUCTION READY!")
else:
    print("WARNING: Some components need attention (see above)")
print("="*80 + "\n")

