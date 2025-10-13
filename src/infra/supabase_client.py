# src/infra/supabase_client.py

from httpx import AsyncClient
from src.config import settings

# This function creates and returns an AsyncClient instance
def get_async_supabase_http_client() -> AsyncClient:
    """
    Returns an httpx.AsyncClient instance configured for Supabase Auth API access.
    """
    # Note: We use SUPABASE_URL and SUPABASE_ANON_KEY (not the service key) 
    # for client-side Auth calls (like login).
    headers = {
        "apikey": settings.SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_ANON_KEY}",
    }
    
    # httpx.AsyncClient is created without the base URL here,
    # as the URL is used in the router (e.g., f"{settings.SUPABASE_URL}/auth/v1/token").
    return AsyncClient(headers=headers, timeout=10)

# Optional: If you need the 'supabase-py' client for *DB-side* operations (not Auth)
# from supabase import create_client, Client
# def get_sync_supabase_client() -> Client:
#     url: str = settings.SUPABASE_URL
#     # Use the Service Role Key for elevated privileges in some cases
#     key: str = settings.SUPABASE_SERVICE_KEY 
#     return create_client(url, key)



# Alberto approach
# from supabase import create_client, Client

# from src.config import settings

# url: str = settings.SUPABASE_URL
# key: str = settings.SUPABASE_KEY

# supabase: Client = create_client(url, key)
