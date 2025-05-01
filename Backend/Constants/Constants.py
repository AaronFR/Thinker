import re

MAX_SCHEMA_RETRIES = 2
MAX_PROMPT_RETRIES = 3

BACKOFF_INITIAL = 5
BACKOFF_FACTOR: float = 1.0

MEGABYTE = 1024 * 1024
MAX_FILE_SIZE = 10 * MEGABYTE
USER_DATA_LIMIT = 1000 * MEGABYTE  # Can be expanded later, but I don't want to be spammed.

DEFAULT_ENCODING = 'utf-8'
DEFAULT_EXTENSION = 'txt'

THE_THINKER_AI_DOMAIN_URL = "https://thethinkerai.com"  # woah this site looks pretty cool *WINKS AGGRESSIVELY*

# Envs

THINKER_ENV = "THINKER_ENV"
DEV_ENV = "development"
PROD_ENV = "production"

THE_THINKER_FRONTEND_URL = "THE_THINKER_FRONTEND_URL"
JWT_SECRET_KEY = "JWT_SECRET_KEY"

STORAGE_TYPE = "STORAGE_TYPE"
LOCAL_STORAGE = "local"
AWS_S3_STORAGE = "s3"

REDISCLOUD_URL = "REDISCLOUD_URL"

THE_THINKER_S3_STANDARD_ACCESS_KEY = "THE-THINKER-S3-STANDARD-ACCESS-KEY"
THE_THINKER_S3_STANDARD_SECRET_ACCESS_KEY = "THE-THINKER-S3-STANDARD-SECRET-ACCESS-KEY"
THE_THINKER_S3_STANDARD_BUCKET_ID = "THE-THINKER-S3-STANDARD-BUCKET-ID"

NEO4J_URI = "NEO4J_URI"
NEO4J_PASSWORD = "NEO4J_PASSWORD"

GEMINI_API_KEY = "GEMINI_API_KEY"

SENDGRID_API_KEY = "SENDGRID_API_KEY"

# Rate Limits

BASE_LIMIT = 10000
USER_BASE_LIMIT = 1000

HIGHLY_RESTRICTED = "100 per day"
RESTRICTED = "1000 per day"
RESTRICTED_HIGH_FREQUENCY = "50 per minute"
MODERATELY_RESTRICTED = "10000 per day"
LIGHTLY_RESTRICTED = "100000 per day"
LIGHTLY_RESTRICTED_HIGH_FREQUENCY = "10000 per hour"

USER_HIGHLY_RESTRICTED = "5 per day"
USER_RESTRICTED = "100 per day"
USER_RESTRICTED_HIGH_FREQUENCY = "1 per minute"
USER_MODERATELY_RESTRICTED = "1000 per day"
USER_LIGHTLY_RESTRICTED = "10000 per day"
USER_LIGHTLY_RESTRICTED_HIGH_FREQUENCY = "1000 per hour"

# REGEX

IDENTIFY_CONTEXT_NODE_PATTERN = re.compile(
    r'<(?P<node_name>[a-zA-Z_]+)\s+parameter="(?P<parameter>[^"]+)"\s+content="(?P<content>[^"]+)"\s*/>'
)

RESULT_AS_TAG_REGEX = r'<result="([^"]+)">'

TAG_WITH_PURPOSE_REGEX = r"<([^>\s]+)(?:\s+purpose='([^']+)')?>"

EXTRACT_LIST_REGEX = r'\[.*?\]'

# Ordered or Unordered
EXTRACT_ELEMENTS_FROM_LIST = r'^\s*[-*]\s+(.*)$|^\s*\d+\.\s+(.*)$'

# Standard Errors

CANNOT_AFFORD_REQUEST = "INSUFFICIENT WEALTH DETECTED"  # I mean it's not wrong

# Categorisation

DEFAULT_CATEGORY = "default"

# Info

DEFAULT_USER_PARAMETERS = ['email', 'augmentation_cost', 'select_category_cost', 'select_worker_cost', 'select_workflow_cost', 'questioning_cost', 'best_of_cost', 'loops_cost', 'internet_search_cost', 'summarise_workflows_cost', 'summarise_files_cost', 'user_context_cost']



