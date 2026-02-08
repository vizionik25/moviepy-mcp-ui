## 2025-02-18 - FastMCP API Vulnerabilities
**Vulnerability:** FastMCP server APIs (using FastAPI) often default to permissive CORS ('*') and leak exception details (detail=str(e)).
**Learning:** These defaults are insecure for production or even local dev if exposed to the network.
**Prevention:** Use environment variables for ALLOWED_ORIGINS and implement a global exception handler or specific try/except blocks that log the error and return a generic 500 message.
