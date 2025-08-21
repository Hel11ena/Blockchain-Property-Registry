from typing import Optional
from blockchain import Blockchain

"""
Simple CLI-like usage demo for a Blockchain-based Land/Property Registration System.
No external dependencies; runs on Python 3.10+.

Key operations:
- register_property(property_id, owner, location, area_sqft, survey_no)
- transfer_property(property_id, current_owner, new_owner, note)
- lookup_owner(property_id)
- show_history(property_id)
"""

# Initialize the blockchain (tweak difficulty for faster/slower PoW)
bc = Blockchain(difficulty=2)


def register_property(
    property_id: str,
    owner: str,
    location: str,
    area_sqft: float,
    survey_no: str,
) -> None:
    """
    Register a NEW property. Prevent duplicate registration of the same property_id.
    """
    if bc.is_property_registered(property_id):
        print(f"[X] Registration failed: Property '{property_id}' is already registered to '{bc.current_owner(property_id)}'.")
        return

    meta = {
        "location": location,
        "area_sqft": area_sqft,
        "survey_no": survey_no,
    }
    block = bc.add_block("REGISTER", property_id, owner, meta)
    print(f"[✓] Registered property '{property_id}' to '{owner}'. Block #{block.index} | Hash: {block.hash[:12]}...")


def transfer_property(
    property_id: str,
    current_owner: str,
    new_owner: str,
    note: str = "Ownership transfer",
) -> None:
    """
    Transfer ownership if the current_owner matches the blockchain's last recorded owner.
    """
    latest_owner: Optional[str] = bc.current_owner(property_id)

    if latest_owner is None:
        print(f"[X] Transfer failed: Property '{property_id}' is not registered.")
        return

    if latest_owner != current_owner:
        print(f"[X] Transfer denied: '{current_owner}' is not the current owner (current owner: '{latest_owner}').")
        return

    meta = {"note": note}
    block = bc.add_block("TRANSFER", property_id, new_owner, meta)
    print(f"[✓] Transferred '{property_id}' from '{current_owner}' to '{new_owner}'. Block #{block.index} | Hash: {block.hash[:12]}...")


def lookup_owner(property_id: str) -> None:
    owner = bc.current_owner(property_id)
    if owner is None:
        print(f"[i] Property '{property_id}' is not registered.")
    else:
        print(f"[i] Current owner of '{property_id}': {owner}")


def show_history(property_id: str) -> None:
    history = bc.property_history(property_id)
    if not history:
        print(f"[i] No records found for property '{property_id}'.")
        return

    print(f"\n--- History for Property '{property_id}' ---")
    for b in history:
        if b.action == "REGISTER":
            print(
                f"Block #{b.index} | {b.action} | Owner: {b.owner} | "
                f"Location: {b.meta.get('location')} | Area(sqft): {b.meta.get('area_sqft')} | "
                f"SurveyNo: {b.meta.get('survey_no')} | Hash: {b.hash[:12]}..."
            )
        else:
            print(
                f"Block #{b.index} | {b.action} | New Owner: {b.owner} | "
                f"Note: {b.meta.get('note')} | Hash: {b.hash[:12]}..."
            )
    print("--- End of History ---\n")


def validate_chain() -> None:
    ok = bc.is_chain_valid()
    print(f"[✓] Blockchain valid: {ok}" if ok else "[X] Blockchain INVALID!")


if __name__ == "__main__":
    # --- Demo flow you can show in README screenshots/logs ---

    # Register two properties
    register_property("PROP-CHN-001", owner="Alice", location="Chennai, Plot-45", area_sqft=1200, survey_no="S-9087")
    register_property("PROP-DEL-002", owner="Charlie", location="Delhi, Sector-9", area_sqft=980, survey_no="S-2211")

    # Attempt duplicate registration (should fail)
    register_property("PROP-CHN-001", owner="Eve", location="Chennai, Plot-45", area_sqft=1200, survey_no="S-9087")

    # Lookup owners
    lookup_owner("PROP-CHN-001")
    lookup_owner("PROP-DEL-002")
    lookup_owner("PROP-NOPE-404")  # not registered

    # Transfer ownership (success)
    transfer_property("PROP-CHN-001", current_owner="Alice", new_owner="Bob", note="Sale deed #A123")

    # Transfer ownership (failure: wrong current owner)
    transfer_property("PROP-DEL-002", current_owner="Bob", new_owner="Daisy", note="Attempted unauthorized transfer")

    # Show histories
    show_history("PROP-CHN-001")
    show_history("PROP-DEL-002")

    # Validate chain integrity
    validate_chain()
