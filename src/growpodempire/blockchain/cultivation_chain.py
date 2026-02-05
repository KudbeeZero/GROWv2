"""
Blockchain Integration for Data Integrity
Provides immutable record keeping for cultivation data
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from ..models import BlockchainRecord


class Block:
    """Individual block in the blockchain"""
    
    def __init__(self, block_number: int, data: Dict[str, Any], previous_hash: str):
        self.block_number = block_number
        self.timestamp = datetime.now()
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate block hash"""
        # Convert datetime objects to strings in data
        serializable_data = self._make_serializable(self.data)
        block_string = json.dumps({
            "block_number": self.block_number,
            "timestamp": self.timestamp.isoformat(),
            "data": serializable_data,
            "previous_hash": self.previous_hash
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def _make_serializable(self, obj):
        """Convert objects to JSON serializable format"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        return obj
    
    def to_record(self) -> BlockchainRecord:
        """Convert block to blockchain record"""
        return BlockchainRecord(
            record_id=str(self.data.get("id", "unknown")),
            record_type=self.data.get("type", "unknown"),
            data_hash=self.hash,
            previous_hash=self.previous_hash,
            timestamp=self.timestamp,
            block_number=self.block_number
        )


class CultivationBlockchain:
    """Blockchain system for cannabis cultivation data integrity"""
    
    def __init__(self):
        self.chain: List[Block] = []
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_block = Block(0, {"type": "genesis", "data": "GrowPodEmpire Genesis Block"}, "0")
        self.chain.append(genesis_block)
    
    def get_latest_block(self) -> Block:
        """Get the most recent block"""
        return self.chain[-1]
    
    def add_block(self, data: Dict[str, Any]) -> BlockchainRecord:
        """Add a new block to the chain"""
        previous_block = self.get_latest_block()
        new_block = Block(
            block_number=len(self.chain),
            data=data,
            previous_hash=previous_block.hash
        )
        self.chain.append(new_block)
        return new_block.to_record()
    
    def record_plant_data(self, plant_id: str, data: Dict[str, Any]) -> BlockchainRecord:
        """Record plant data on blockchain"""
        block_data = {
            "type": "plant_data",
            "id": plant_id,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        return self.add_block(block_data)
    
    def record_environmental_data(self, pod_id: str, data: Dict[str, Any]) -> BlockchainRecord:
        """Record environmental data on blockchain"""
        block_data = {
            "type": "environmental_data",
            "id": pod_id,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        return self.add_block(block_data)
    
    def record_harvest(self, plant_id: str, harvest_data: Dict[str, Any]) -> BlockchainRecord:
        """Record harvest event on blockchain"""
        block_data = {
            "type": "harvest",
            "id": plant_id,
            "timestamp": datetime.now().isoformat(),
            "data": harvest_data
        }
        return self.add_block(block_data)
    
    def verify_chain(self) -> bool:
        """Verify the integrity of the blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if current block's hash is correct
            if current_block.hash != current_block.calculate_hash():
                return False
            
            # Check if previous hash matches
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True
    
    def get_records_by_type(self, record_type: str) -> List[Dict[str, Any]]:
        """Get all records of a specific type"""
        records = []
        for block in self.chain[1:]:  # Skip genesis block
            if block.data.get("type") == record_type:
                records.append({
                    "block_number": block.block_number,
                    "timestamp": block.timestamp.isoformat(),
                    "hash": block.hash,
                    "data": block.data
                })
        return records
    
    def get_records_by_id(self, record_id: str) -> List[Dict[str, Any]]:
        """Get all records for a specific plant or pod"""
        records = []
        for block in self.chain[1:]:  # Skip genesis block
            if block.data.get("id") == record_id:
                records.append({
                    "block_number": block.block_number,
                    "timestamp": block.timestamp.isoformat(),
                    "hash": block.hash,
                    "data": block.data
                })
        return records
    
    def get_chain_info(self) -> Dict[str, Any]:
        """Get blockchain statistics"""
        return {
            "total_blocks": len(self.chain),
            "is_valid": self.verify_chain(),
            "latest_block": {
                "number": self.chain[-1].block_number,
                "hash": self.chain[-1].hash,
                "timestamp": self.chain[-1].timestamp.isoformat()
            }
        }
