"""LLM caller bootstrap — wire HTTP caller into runtime at startup."""

from __future__ import annotations

import logging
import os

_LOGGER = logging.getLogger("llm_policy")


def bootstrap_llm_caller() -> None:
    """Create and register the HTTP LLM caller if env vars are configured.

    Guard order:
    1. LLM_POLICY_ENABLED must be true
    2. LLM_POLICY_ALLOW_PLACEHOLDERS must be false
    3. LLM_API_KEY must be set
    """
    from llm_policy.config import (
        get_llm_policy_allow_placeholders,
        is_llm_policy_enabled,
    )

    if not is_llm_policy_enabled():
        _LOGGER.info("LLM policy disabled, skipping bootstrap")
        return

    if get_llm_policy_allow_placeholders():
        _LOGGER.error(
            "Cannot register real LLM caller with placeholders enabled. "
            "Set LLM_POLICY_ALLOW_PLACEHOLDERS=false to use a real caller."
        )
        return

    api_key = os.getenv("LLM_API_KEY", "")
    if not api_key:
        _LOGGER.warning("LLM_API_KEY not set, LLM caller not registered")
        return

    from llm_policy.http_caller import create_http_caller
    from llm_policy.runtime import set_llm_caller

    caller = create_http_caller(api_key=api_key)
    set_llm_caller(caller)
    _LOGGER.info("LLM caller registered successfully")
