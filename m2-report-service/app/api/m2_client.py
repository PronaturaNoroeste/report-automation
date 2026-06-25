"""ProtectedSeas M2 API client.

The data source is the Monthly Radar Track ZIP:

    GET /api/map/{radar_id}/{year}/{month:02d}/download-s3-zip

Retry policy: transport errors, 5xx and 429 are retried with exponential
backoff; other 4xx (401/403/404) are permanent and raised immediately.
"""

import asyncio
import logging

import httpx

from app.config import settings

log = logging.getLogger(__name__)

MAX_ATTEMPTS = 3
BACKOFF_BASE_SECONDS = 2  # 2s, 4s between retries
# ZIPs for a busy month can be tens of MB — generous read timeout.
REQUEST_TIMEOUT = httpx.Timeout(300.0, connect=15.0)


class M2ApiError(Exception):
    """Raised when an M2 API call fails permanently."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def _auth_headers() -> dict:
    # Bare token, no "Bearer " prefix — the M2 API rejects the Bearer form
    # with 403 (confirmed against download-s3-zip with the real token).
    return {"Authorization": settings.m2_api_token}


def _is_retryable(status_code: int) -> bool:
    return status_code >= 500 or status_code == 429


async def _get_with_retry(client: httpx.AsyncClient, url: str, params: dict | None = None) -> httpx.Response:
    last_error: Exception | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = await client.get(url, params=params, headers=_auth_headers())
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            if not _is_retryable(status):
                raise M2ApiError(
                    f"M2 API returned {status} for {url} — permanent error, not retrying.",
                    status_code=status,
                ) from e
            last_error = e
        except httpx.TransportError as e:
            last_error = e
        if attempt < MAX_ATTEMPTS:
            delay = BACKOFF_BASE_SECONDS ** attempt
            log.warning("M2 API attempt %d/%d failed for %s: %s — retrying in %ds",
                        attempt, MAX_ATTEMPTS, url, last_error, delay)
            await asyncio.sleep(delay)
    raise M2ApiError(f"M2 API request failed after {MAX_ATTEMPTS} attempts: {url}") from last_error


async def download_monthly_zip(radar_id: int, year: int, month: int) -> bytes:
    """Download the Monthly Radar Track ZIP for one site and month.

    The API docs spell the endpoint "download-s3-zip" but their own example
    uses "download_s3_zip" — try the documented form first, fall back on 404.
    """
    candidates = [
        f"{settings.m2_api_base_url}/{radar_id}/{year}/{month:02d}/download-s3-zip",
        f"{settings.m2_api_base_url}/{radar_id}/{year}/{month:02d}/download_s3_zip",
    ]
    last_error: M2ApiError | None = None
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
        for url in candidates:
            try:
                response = await _get_with_retry(client, url)
                log.info("Downloaded monthly ZIP for radar %s %d-%02d (%d bytes)",
                         radar_id, year, month, len(response.content))
                return response.content
            except M2ApiError as e:
                if e.status_code == 404:
                    last_error = e
                    continue  # try the alternate spelling
                raise
    raise M2ApiError(
        f"Monthly ZIP not found for radar {radar_id} {year}-{month:02d} "
        "(404 on both endpoint spellings — data may not be published yet)."
    ) from last_error
