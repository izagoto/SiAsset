#!/usr/bin/env python3
"""
Database seeder script
Run this script to populate the database with initial data
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.seeders.run_seeder import run_seeders

if __name__ == "__main__":
    run_seeders()

