"""HTTP client for authenticated PDF retrieval via OAuth 2.0 client credentials.

This module handles token management and file download from the configured API.
"""
from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import requests
from dotenv import load_dotenv

# Ensure environment variables are available when the module is imported.
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OAuthConfig:
    """Configuration fields required for OAuth 2.0 client credentials flow."""

    token_url: str
    client_id: str
    client_secret: str
    scope: Optional[str] = None

    @classmethod
    def from_env(cls) -> "OAuthConfig":
        """Build configuration from environment variables."""
        token_url = os.getenv("TOKEN_URL")
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")
        if not all([token_url, client_id, client_secret]):
            missing = [
                name
                for name, value in [
                    ("TOKEN_URL", token_url),
                    ("CLIENT_ID", client_id),
                    ("CLIENT_SECRET", client_secret),
                ]
                if not value
            ]
            raise ValueError(
                "Missing required OAuth environment variables: " + ", ".join(missing)
            )
        return cls(
            token_url=token_url,
            client_id=client_id,
            client_secret=client_secret,
            scope=os.getenv("OAUTH_SCOPE"),
        )


class APIClient:
    """Authenticated client for fetching protected resources from the PDF API."""

    def __init__(
        self,
        base_url: str,
        auth_config: OAuthConfig,
        *,
        session: Optional[requests.Session] = None,
    ) -> None:
        if not base_url:
            raise ValueError("base_url must be provided")
        self.base_url = base_url.rstrip("/") + "/"
        self.auth_config = auth_config
        self.session = session or requests.Session()
        self._token: Optional[dict] = None

    def _token_is_valid(self) -> bool:
        return bool(
            self._token
            and "access_token" in self._token
            and "expires_at" in self._token
            and time.time() < self._token["expires_at"]
        )

    def _refresh_token(self) -> None:
        logger.debug("Refreshing OAuth token")
        data = {"grant_type": "client_credentials"}
        if self.auth_config.scope:
            data["scope"] = self.auth_config.scope

        response = self.session.post(
            self.auth_config.token_url,
            data=data,
            auth=(self.auth_config.client_id, self.auth_config.client_secret),
            timeout=30,
        )
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            logger.error("Token request failed: %s", exc)
            raise

        payload = response.json()
        access_token = payload.get("access_token")
        expires_in = payload.get("expires_in", 3600)
        if not access_token:
            raise RuntimeError("Token endpoint response missing access_token")

        # Refresh slightly before the actual expiry to avoid race conditions.
        expires_at = time.time() + max(int(expires_in) - 30, 30)
        self._token = {
            "access_token": access_token,
            "token_type": payload.get("token_type", "Bearer"),
            "expires_at": expires_at,
        }
        logger.debug("Obtained new access token valid until %s", expires_at)

    def _auth_header(self) -> str:
        if not self._token_is_valid():
            self._refresh_token()
        assert self._token is not None
        token_type = self._token.get("token_type", "Bearer")
        return f"{token_type} {self._token['access_token']}"

    def fetch_pdf(self, pdf_id: str, output_path: Path) -> Path:
        """Download the PDF with the given identifier to the requested path."""
        if not pdf_id:
            raise ValueError("pdf_id must be provided")
        if not isinstance(output_path, Path):
            output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        url = urljoin(self.base_url, f"pdfs/{pdf_id}")
        logger.debug("Fetching PDF %s from %s", pdf_id, url)

        headers = {"Authorization": self._auth_header()}
        with self.session.get(url, headers=headers, stream=True, timeout=60) as response:
            try:
                response.raise_for_status()
            except requests.HTTPError as exc:
                logger.error("PDF download failed: %s", exc)
                raise
            with output_path.open("wb") as file_handle:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        file_handle.write(chunk)

        logger.info("Saved PDF %s to %s", pdf_id, output_path)
        return output_path
