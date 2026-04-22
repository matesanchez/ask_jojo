"""Interface-conformance tests for cloud + web connector stubs.

These make sure the stubs fail *loudly* (NotImplementedError with an actionable
message) rather than silently doing nothing. Replace the NotImplementedError
check with a real behavior check when each connector is wired up.
"""

from __future__ import annotations

import pytest

from jojo_connectors_common import Connector
from jojo_ingest.nurixnet import NurixNetConnector
from jojo_ingest.onedrive import OneDriveConnector
from jojo_ingest.sharepoint import SharePointConnector


@pytest.mark.parametrize(
    "factory, source_type",
    [
        (lambda: SharePointConnector(), "sharepoint"),
        (lambda: OneDriveConnector(), "onedrive"),
        (lambda: NurixNetConnector(), "nurixnet"),
    ],
)
def test_stub_connector_conforms_to_interface(factory, source_type):
    conn = factory()
    assert isinstance(conn, Connector)
    assert conn.source_type == source_type
    with pytest.raises(NotImplementedError) as excinfo:
        list(conn.fetch())
    msg = str(excinfo.value).lower()
    # Clear failure mode that points at why it isn't working.
    assert any(
        phrase in msg
        for phrase in ("not wired", "ms graph", "vpn", "playwright", "it ticket")
    ), f"Stub for {source_type} lacks an actionable message: {msg}"
