import os
import logging
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Environment loading
# ---------------------------------------------------------------------------
# load_dotenv() reads a .env file when running locally.
# In a container the file is absent and os.environ values are used directly.
# ---------------------------------------------------------------------------
load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App config
# ---------------------------------------------------------------------------

# Port the uvicorn server listens on.
PORT: int = int(os.getenv("PORT", "8080"))
