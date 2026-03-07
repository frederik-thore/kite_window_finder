import os

# Keep tests deterministic and independent of external network availability.
os.environ.setdefault("LIVE_WEATHER_ENABLED", "false")
os.environ.setdefault("ALLOW_SYNTHETIC_FALLBACK", "true")
