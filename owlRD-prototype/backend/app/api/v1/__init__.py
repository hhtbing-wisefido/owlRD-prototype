"""
API v1路由
"""

from . import (
    tenants, users, roles, auth,
    locations, rooms, beds,
    residents, resident_contacts, resident_caregivers, resident_phi,
    devices,
    iot_data, alerts, alert_policies,
    cards, card_functions,
    care_quality,
    config_versions, mappings,
    export_api, websocket
)

__all__ = [
    "tenants", "users", "roles", "auth",
    "locations", "rooms", "beds",
    "residents", "resident_contacts", "resident_caregivers", "resident_phi",
    "devices",
    "iot_data", "alerts", "alert_policies",
    "cards", "card_functions",
    "care_quality",
    "config_versions", "mappings",
    "export_api", "websocket"
]
