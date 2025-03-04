"""
Snapshot management for SciDiscover
Allows creating and loading development snapshots
"""
import os
import json
import shutil
import datetime
from pathlib import Path
from typing import Dict, List, Optional

class SnapshotManager:
    """Manages project snapshots for saving development states"""
    
    def __init__(self, base_dir: str = "snapshots"):
        """Initialize the snapshot manager with base directory"""
        self.base_dir = Path(base_dir)
        self.snapshots_file = self.base_dir / "snapshots.json"
        
        # Create snapshot directory if it doesn't exist
        os.makedirs(self.base_dir, exist_ok=True)
        
        # Initialize snapshots registry
        if not self.snapshots_file.exists():
            self._save_snapshots_registry({})
    
    def create_snapshot(self, name: str, description: Optional[str] = None) -> Dict:
        """
        Create a new snapshot of the current project state
        
        Args:
            name: Name of the snapshot
            description: Optional description of the snapshot
            
        Returns:
            Snapshot metadata
        """
        # Get existing snapshots
        snapshots = self._load_snapshots_registry()
        
        # Create snapshot directory
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        snapshot_id = f"{timestamp}_{name.lower().replace(' ', '_')}"
        snapshot_dir = self.base_dir / snapshot_id
        
        # Check if snapshot already exists
        if name in [s["name"] for s in snapshots.values()]:
            print(f"Warning: Snapshot with name '{name}' already exists. Creating a new version.")
        
        # Create snapshot data
        snapshot_data = {
            "id": snapshot_id,
            "name": name,
            "description": description or f"Snapshot created on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "created_at": datetime.datetime.now().isoformat(),
            "files": []
        }
        
        # Create directory for this snapshot
        os.makedirs(snapshot_dir, exist_ok=True)
        
        # Copy important project files
        self._backup_directory("scidiscover", snapshot_dir / "scidiscover")
        
        # Add main.py and other root files
        for root_file in ["main.py", ".streamlit/config.toml"]:
            if os.path.exists(root_file):
                target_dir = snapshot_dir / os.path.dirname(root_file)
                os.makedirs(target_dir, exist_ok=True)
                shutil.copy2(root_file, snapshot_dir / root_file)
                snapshot_data["files"].append(root_file)
        
        # Update snapshots registry
        snapshots[snapshot_id] = snapshot_data
        self._save_snapshots_registry(snapshots)
        
        print(f"✅ Created snapshot '{name}' with ID {snapshot_id}")
        return snapshot_data
    
    def list_snapshots(self) -> List[Dict]:
        """List all available snapshots"""
        snapshots = self._load_snapshots_registry()
        return list(snapshots.values())
    
    def get_snapshot(self, name_or_id: str) -> Optional[Dict]:
        """Get a specific snapshot by name or ID"""
        snapshots = self._load_snapshots_registry()
        
        # Try to find by ID first
        if name_or_id in snapshots:
            return snapshots[name_or_id]
        
        # Try to find by name
        for snapshot in snapshots.values():
            if snapshot["name"] == name_or_id:
                return snapshot
        
        return None
    
    def _backup_directory(self, src_dir: str, dest_dir: str) -> None:
        """Recursively backup a directory"""
        if not os.path.exists(src_dir):
            return
            
        # Create destination directory
        os.makedirs(dest_dir, exist_ok=True)
        
        # Copy all files and subdirectories
        for item in os.listdir(src_dir):
            src_item = os.path.join(src_dir, item)
            dest_item = os.path.join(dest_dir, item)
            
            # Skip __pycache__ directories and .pyc files
            if item == "__pycache__" or item.endswith(".pyc"):
                continue
                
            if os.path.isdir(src_item):
                self._backup_directory(src_item, dest_item)
            else:
                shutil.copy2(src_item, dest_item)
    
    def _load_snapshots_registry(self) -> Dict:
        """Load the snapshots registry file"""
        if not self.snapshots_file.exists():
            return {}
        
        with open(self.snapshots_file, 'r') as f:
            return json.load(f)
    
    def _save_snapshots_registry(self, snapshots: Dict) -> None:
        """Save the snapshots registry file"""
        with open(self.snapshots_file, 'w') as f:
            json.dump(snapshots, f, indent=2)
