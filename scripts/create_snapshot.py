#!/usr/bin/env python3
"""
Snapshot creation tool for SciDiscover
"""
import sys
import os
import argparse
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scidiscover.snapshot import SnapshotManager

def main():
    parser = argparse.ArgumentParser(description="Create and manage SciDiscover snapshots.")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Create snapshot command
    create_parser = subparsers.add_parser("create", help="Create a new snapshot")
    create_parser.add_argument("name", help="Snapshot name")
    create_parser.add_argument("-d", "--description", help="Snapshot description")
    
    # List snapshots command
    list_parser = subparsers.add_parser("list", help="List all snapshots")
    
    # Show snapshot command
    show_parser = subparsers.add_parser("show", help="Show details of a snapshot")
    show_parser.add_argument("name_or_id", help="Snapshot name or ID")
    
    args = parser.parse_args()
    
    # Initialize snapshot manager
    snapshot_manager = SnapshotManager()
    
    if args.command == "create":
        snapshot = snapshot_manager.create_snapshot(args.name, args.description)
        print(f"Created snapshot '{snapshot['name']}' (ID: {snapshot['id']})")
        print(f"Description: {snapshot['description']}")
        print(f"Created at: {snapshot['created_at']}")
        print(f"Files: {len(snapshot['files'])}")
        
    elif args.command == "list":
        snapshots = snapshot_manager.list_snapshots()
        print(f"Found {len(snapshots)} snapshots:")
        for snapshot in snapshots:
            print(f"- {snapshot['name']} (ID: {snapshot['id']}, Created: {snapshot['created_at']})")
            
    elif args.command == "show":
        snapshot = snapshot_manager.get_snapshot(args.name_or_id)
        if snapshot:
            print(f"Snapshot: {snapshot['name']} (ID: {snapshot['id']})")
            print(f"Description: {snapshot['description']}")
            print(f"Created at: {snapshot['created_at']}")
            print(f"Files: {len(snapshot['files'])}")
        else:
            print(f"Snapshot '{args.name_or_id}' not found.")
            
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
