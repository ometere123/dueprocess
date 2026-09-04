"""Opt-in StudioNet lifecycle checkpoint.

CI must never pretend mocked Direct Mode is a finalized multi-validator network proof.
The exact live path is documented in docs/REVIEWER_DEMO.md and its results belong in DEPLOYMENT.md.
"""

import os
import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("DUEPROCESS_RUN_STUDIONET") != "1",
    reason="set DUEPROCESS_RUN_STUDIONET=1 only with a configured live StudioNet environment",
)


def test_live_lifecycle_checkpoint():
    pytest.skip("execute docs/REVIEWER_DEMO.md against StudioNet and record finalized evidence in DEPLOYMENT.md")
