"""Reference scaffold for the SwarmGate key-management flow.

This module is intentionally not a cryptographic implementation. It models the
deployment lifecycle used in the R4 manuscript: fleet context, attribute
reports, device-local state, public encodings, policy-version and epoch binding,
revocation checks, predicate checking, and context-bound key derivation.

The scaffold is useful for tests, documentation, and protocol walkthroughs, but
it must not be used as a security library.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import FrozenSet, Tuple


Coordinate = Tuple[int, int]


@dataclass(frozen=True)
class FleetContext:
    """Public deployment context distributed during enrollment."""

    crs_id: str
    policy_id: str
    policy_version: str
    epoch: str
    session_id: str
    revoked_devices: FrozenSet[str] = frozenset()


@dataclass(frozen=True)
class AttributeReport:
    """Deployment-authenticated metadata for a private attribute.

    The report tag is a deterministic stand-in for a signature, attestation
    quote, secure-localization certificate, or operator-issued token.
    """

    device_id: str
    attribute_type: str
    policy_id: str
    policy_version: str
    epoch: str
    session_id: str
    tag: str


@dataclass(frozen=True)
class DeviceState:
    """Device-local state. In a real implementation, secret_key is secret."""

    device_id: str
    public_key: str
    secret_key: str
    attribute: Coordinate
    role: str
    software_epoch: str


@dataclass(frozen=True)
class PublicEncoding:
    """Public encoding posted to a directory, broadcast, or peer cache."""

    device_id: str
    public_key: str
    encoding: str
    policy_id: str
    policy_version: str
    epoch: str
    session_id: str
    report: AttributeReport


def _digest(*parts: object) -> str:
    h = sha256()
    for part in parts:
        h.update(str(part).encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


def issue_attribute_report(
    device_id: str,
    attribute: Coordinate,
    context: FleetContext,
    attribute_type: str = "quantized-location",
) -> AttributeReport:
    """Create a deterministic demo report bound to the private attribute."""

    tag = _digest(
        "report",
        device_id,
        attribute_type,
        context.policy_id,
        context.policy_version,
        context.epoch,
        context.session_id,
        attribute,
    )
    return AttributeReport(
        device_id=device_id,
        attribute_type=attribute_type,
        policy_id=context.policy_id,
        policy_version=context.policy_version,
        epoch=context.epoch,
        session_id=context.session_id,
        tag=tag,
    )


def verify_attribute_report(
    report: AttributeReport,
    device_id: str,
    attribute: Coordinate,
    context: FleetContext,
) -> bool:
    """Verify the demo report and fail closed on context mismatch."""

    if report.device_id != device_id:
        return False
    if report.policy_id != context.policy_id:
        return False
    if report.policy_version != context.policy_version:
        return False
    if report.epoch != context.epoch:
        return False
    if report.session_id != context.session_id:
        return False
    if report.device_id in context.revoked_devices:
        return False
    expected = issue_attribute_report(
        device_id=device_id,
        attribute=attribute,
        context=context,
        attribute_type=report.attribute_type,
    )
    return report.tag == expected.tag


def enroll_device(
    device_id: str,
    attribute: Coordinate,
    context: FleetContext,
    role: str = "robot",
    software_epoch: str = "software-001",
) -> DeviceState:
    """Create deterministic demo keys for a device in a fleet context."""

    if device_id in context.revoked_devices:
        raise ValueError("device is revoked")
    public_key = _digest("pk", context.crs_id, device_id)[:32]
    secret_key = _digest("sk", context.crs_id, device_id, attribute)[:32]
    return DeviceState(device_id, public_key, secret_key, attribute, role, software_epoch)


def attr_keygen(
    state: DeviceState,
    context: FleetContext,
    report: AttributeReport,
) -> PublicEncoding:
    """Create a toy public encoding bound to policy, session, epoch, and report."""

    if not verify_attribute_report(report, state.device_id, state.attribute, context):
        raise ValueError("attribute report verification failed")
    encoding = _digest(
        "pe",
        context.crs_id,
        context.policy_id,
        context.policy_version,
        context.epoch,
        context.session_id,
        state.public_key,
        state.attribute,
        report.tag,
    )
    return PublicEncoding(
        device_id=state.device_id,
        public_key=state.public_key,
        encoding=encoding,
        policy_id=context.policy_id,
        policy_version=context.policy_version,
        epoch=context.epoch,
        session_id=context.session_id,
        report=report,
    )


def validate_peer_encoding(peer_encoding: PublicEncoding, context: FleetContext) -> None:
    """Fail closed before predicate evaluation when public context is invalid."""

    if peer_encoding.device_id in context.revoked_devices:
        raise ValueError("peer is revoked")
    if peer_encoding.policy_id != context.policy_id:
        raise ValueError("policy mismatch")
    if peer_encoding.policy_version != context.policy_version:
        raise ValueError("policy-version mismatch")
    if peer_encoding.epoch != context.epoch:
        raise ValueError("epoch mismatch")
    if peer_encoding.session_id != context.session_id:
        raise ValueError("session mismatch")


def geolocation_accepts(a: Coordinate, b: Coordinate, threshold: int) -> bool:
    """Accept when two 2D quantized coordinates are close in L-infinity distance."""

    return max(abs(a[0] - b[0]), abs(a[1] - b[1])) < threshold


def fleet_admission_accepts(
    requester: DeviceState,
    responder: DeviceState,
    threshold: int,
    authorized_roles: FrozenSet[str],
    required_software_epoch: str,
    same_mission_epoch: bool = True,
) -> bool:
    """Demo composite predicate for R4 fleet admission."""

    role_ok = requester.role in authorized_roles
    software_ok = requester.software_epoch == required_software_epoch
    proximity_ok = geolocation_accepts(requester.attribute, responder.attribute, threshold)
    mission_ok = same_mission_epoch
    return proximity_ok and role_ok and software_ok and mission_ok


def derive_demo_key(
    own_state: DeviceState,
    peer_encoding: PublicEncoding,
    context: FleetContext,
    predicate_accepts: bool,
) -> str:
    """Derive a context-bound demo key.

    Real SwarmGate derives compatible predicate tokens through MKHSS evaluation.
    This scaffold represents only the public lifecycle. The predicate token is a
    deterministic stand-in: accepting sessions use a shared token, while
    rejecting sessions remain device-specific.
    """

    validate_peer_encoding(peer_encoding, context)
    predicate_token = "accept" if predicate_accepts else f"reject:{own_state.device_id}"
    nike_inputs = sorted([own_state.public_key, peer_encoding.public_key])
    nike_key = _digest("toy-nike", *nike_inputs)
    return _digest(
        predicate_token,
        nike_key,
        context.policy_id,
        context.policy_version,
        context.session_id,
        context.epoch,
    )


def demo() -> None:
    """Run a small proximity-gated exchange example."""

    context = FleetContext(
        crs_id="crs-robotics-demo",
        policy_id="fleet-admission",
        policy_version="policy-v4",
        epoch="epoch-001",
        session_id="mission-window-42",
    )
    alice = enroll_device("robot-A", (10, 12), context, role="leader")
    bob = enroll_device("robot-B", (13, 14), context, role="relay")
    alice_report = issue_attribute_report(alice.device_id, alice.attribute, context)
    bob_report = issue_attribute_report(bob.device_id, bob.attribute, context)
    alice_encoding = attr_keygen(alice, context, alice_report)
    bob_encoding = attr_keygen(bob, context, bob_report)
    accepts = fleet_admission_accepts(
        requester=bob,
        responder=alice,
        threshold=5,
        authorized_roles=frozenset({"relay", "leader"}),
        required_software_epoch="software-001",
    )
    alice_key = derive_demo_key(alice, bob_encoding, context, accepts)
    bob_key = derive_demo_key(bob, alice_encoding, context, accepts)
    print("predicate_accepts:", accepts)
    print("keys_equal:", alice_key == bob_key)


if __name__ == "__main__":
    demo()
