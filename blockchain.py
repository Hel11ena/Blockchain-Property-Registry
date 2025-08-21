import hashlib
import json
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any


def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


@dataclass
class Block:
    index: int
    timestamp: float
    action: str            # "REGISTER" or "TRANSFER"
    property_id: str
    owner: str
    meta: Dict[str, Any]   # e.g., {"location": "..."} or {"note": "..."}
    previous_hash: str
    nonce: int = 0         # simple PoW to make hashes non-trivial
    hash: str = ""

    def compute_hash(self) -> str:
        payload = {
            "index": self.index,
            "timestamp": self.timestamp,
            "action": self.action,
            "property_id": self.property_id,
            "owner": self.owner,
            "meta": self.meta,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }
        return sha256_hex(json.dumps(payload, sort_keys=True))


class Blockchain:
    def __init__(self, difficulty: int = 2):
        """
        difficulty: number of leading zeros required in block hash (simple PoW)
        """
        self.difficulty = difficulty
        self.chain: List[Block] = [self._create_genesis_block()]

    def _create_genesis_block(self) -> Block:
        b = Block(
            index=0,
            timestamp=time.time(),
            action="GENESIS",
            property_id="0",
            owner="SYSTEM",
            meta={"note": "Genesis Block"},
            previous_hash="0" * 64,
        )
        self._mine(b)
        return b

    @property
    def latest_block(self) -> Block:
        return self.chain[-1]

    def _mine(self, block: Block) -> None:
        """
        Very small proof-of-work: find nonce so that hash starts with '0' * difficulty.
        """
        while True:
            block.hash = block.compute_hash()
            if block.hash.startswith("0" * self.difficulty):
                break
            block.nonce += 1

    def add_block(self, action: str, property_id: str, owner: str, meta: Dict[str, Any]) -> Block:
        block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            action=action,
            property_id=property_id,
            owner=owner,
            meta=meta,
            previous_hash=self.latest_block.hash,
        )
        self._mine(block)
        self.chain.append(block)
        return block

    def is_chain_valid(self) -> bool:
        """
        Verify:
        - each block's hash is correct
        - previous_hash linkage is intact
        - PoW requirement holds for all blocks
        """
        if not self.chain:
            return False

        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]

            # Recompute and compare current hash
            recomputed = curr.compute_hash()
            if curr.hash != recomputed:
                return False

            # Check linkage
            if curr.previous_hash != prev.hash:
                return False

            # Check difficulty (PoW)
            if not curr.hash.startswith("0" * self.difficulty):
                return False

        # Genesis should also satisfy difficulty & self-consistency
        genesis = self.chain[0]
        if genesis.hash != genesis.compute_hash():
            return False
        if not genesis.hash.startswith("0" * self.difficulty):
            return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "difficulty": self.difficulty,
            "length": len(self.chain),
            "chain": [asdict(b) for b in self.chain],
        }

    # --- Domain helpers for property registry ---

    def current_owner(self, property_id: str) -> str | None:
        """
        Returns the latest known owner of a property_id, or None if never registered.
        """
        owner = None
        for b in self.chain:
            if b.property_id == property_id and b.action in ("REGISTER", "TRANSFER"):
                owner = b.owner
        return owner

    def property_history(self, property_id: str) -> List[Block]:
        """
        Returns list of blocks for a given property_id in chronological order.
        """
        return [b for b in self.chain if b.property_id == property_id]

    def is_property_registered(self, property_id: str) -> bool:
        return self.current_owner(property_id) is not None
