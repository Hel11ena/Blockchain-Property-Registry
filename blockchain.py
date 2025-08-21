import hashlib
import time
import json

# ------------------------
# Block class
# ------------------------
class Block:
    def __init__(self, index, data, prev_hash):
        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.prev_hash = prev_hash
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "prev_hash": self.prev_hash
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()


# ------------------------
# Blockchain class
# ------------------------
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, {"action": "GENESIS"}, "0")

    def add_block(self, data):
        prev_block = self.chain[-1]
        block = Block(len(self.chain), data, prev_block.hash)
        self.chain.append(block)
        return block

    def validate_chain(self):
        for i in range(1, len(self.chain)):
            prev = self.chain[i-1]
            curr = self.chain[i]
            if curr.prev_hash != prev.hash:
                return False
            if curr.hash != curr.compute_hash():
                return False
        return True


# ------------------------
# Property Registry
# ------------------------
class PropertyRegistry:
    def __init__(self):
        self.blockchain = Blockchain()
        self.ownership = {}

    # Register new property
    def register_property(self, prop_id, owner, location, area, survey):
        if prop_id in self.ownership:
            print(f"[X] Registration failed: Property '{prop_id}' already registered.")
            return None
        data = {
            "action": "REGISTER",
            "property_id": prop_id,
            "owner": owner,
            "location": location,
            "area": area,
            "survey_no": survey
        }
        block = self.blockchain.add_block(data)
        self.ownership[prop_id] = owner
        print(f"[✓] Registered property '{prop_id}' to '{owner}'. Block #{block.index} | Hash: {block.hash[:12]}...")
        return block

    # Transfer property ownership
    def transfer_property(self, prop_id, current_owner, new_owner, note=""):
        if prop_id not in self.ownership:
            print(f"[X] Transfer failed: Property '{prop_id}' not found.")
            return None
        if self.ownership[prop_id] != current_owner:
            print(f"[X] Transfer denied: '{current_owner}' is not the current owner (current owner: '{self.ownership[prop_id]}').")
            return None
        data = {
            "action": "TRANSFER",
            "property_id": prop_id,
            "from": current_owner,
            "to": new_owner,
            "note": note
        }
        block = self.blockchain.add_block(data)
        self.ownership[prop_id] = new_owner
        print(f"[✓] Transferred '{prop_id}' from '{current_owner}' to '{new_owner}'. Block #{block.index} | Hash: {block.hash[:12]}...")
        return block

    # Get current owner
    def get_current_owner(self, prop_id):
        return self.ownership.get(prop_id, None)

    # Show transaction history of a property
    def show_property_history(self, prop_id):
        print(f"\n--- History for Property '{prop_id}' ---")
        found = False
        for block in self.blockchain.chain:
            data = block.data
            if data.get("property_id") == prop_id:
                found = True
                if data["action"] == "REGISTER":
                    print(f"Block #{block.index} | REGISTER | Owner: {data['owner']} | Location: {data['location']} | "
                          f"Area: {data['area']} sqft | SurveyNo: {data['survey_no']} | Hash: {block.hash[:12]}...")
                elif data["action"] == "TRANSFER":
                    print(f"Block #{block.index} | TRANSFER | From: {data['from']} → To: {data['to']} | "
                          f"Note: {data['note']} | Hash: {block.hash[:12]}...")
        if not found:
            print("No history found for this property.")
        print("--- End of History ---")
