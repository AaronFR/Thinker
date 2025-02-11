import re

MAX_SCHEMA_RETRIES = 2
MAX_PROMPT_RETRIES = 3

BACKOFF_INITIAL = 5
BACKOFF_FACTOR: float = 1.0

MAX_FILE_SIZE = 10 * 1024 * 1024

DEFAULT_ENCODING = 'utf-8'
DEFAULT_EXTENSION = 'txt'


# Envs
JWT_SECRET_KEY = "JWT_SECRET_KEY"
THINKER_ENV = "THINKER_ENV"
THE_THINKER_FRONTEND_URL = "THE_THINKER_FRONTEND_URL"

STORAGE_TYPE = "STORAGE_TYPE"
LOCAL_STORAGE = "local"
AWS_S3_STORAGE = "s3"

THE_THINKER_S3_STANDARD_ACCESS_KEY = "THE-THINKER-S3-STANDARD-ACCESS-KEY"
THE_THINKER_S3_STANDARD_SECRET_ACCESS_KEY = "THE-THINKER-S3-STANDARD-SECRET-ACCESS-KEY"
THE_THINKER_S3_STANDARD_BUCKET_ID = "THE-THINKER-S3-STANDARD-BUCKET-ID"

NEO4J_URI = "NEO4J_URI"
NEO4J_PASSWORD = "NEO4J_PASSWORD"

GEMINI_API_KEY = "GEMINI_API_KEY"

# REGEX

IDENTIFY_CONTEXT_NODE_PATTERN = re.compile(
    r'<(?P<node_name>[a-zA-Z_]+)\s+parameter="(?P<parameter>[^"]+)"\s+content="(?P<content>[^"]+)"\s*/>'
)

RESULT_AS_TAG_REGEX = r'<result="([^"]+)">'

TAG_WITH_PURPOSE_REGEX = r"<([^>\s]+)(?:\s+purpose='([^']+)')?>"

EXTRACT_LIST_REGEX = r'\[.*?\]'

# Ordered or Unordered
EXTRACT_ELEMENTS_FROM_LIST = r'^\s*[-*]\s+(.*)$|^\s*\d+\.\s+(.*)$'

SENTENCE_WITH_FULL_STOP_REGEX = r'^.*\.$'
