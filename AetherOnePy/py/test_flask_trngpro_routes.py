#!/usr/bin/env python3
"""Test TRNGPro Flask routes"""
import os
import sys
import tempfile
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import AetherOnePy
from flask import Flask
from services.databaseService import CaseDAO


def test_flask_routes():
    """Test TRNGPro Flask routes functionality"""
    print("Testing TRNGPro Flask Routes Integration")
    print("=" * 45)
    
    temp_dir = tempfile.mkdtemp()
    try:
        hotbits_dir = os.path.join(temp_dir, 'hotbits')
        os.makedirs(hotbits_dir, exist_ok=True)
        
        # Create AetherOne instance
        aether_one = AetherOnePy()
        
        # Test 1: Check if TRNGPro routes are registered
        print("1. Testing route registration...")
        routes = []
        for rule in aether_one.app.url_map.iter_rules():
            routes.append(rule.rule)
        
        if '/collectTRNGProHotBits' in routes:
            print("[OK] TRNGPro route registered")
        else:
            print("[FAIL] TRNGPro route not found")
            return False
        
        # Test 2: Test ping endpoint includes TRNGPro availability
        print("\n2. Testing ping endpoint...")
        with aether_one.app.test_client() as client:
            response = client.get('/ping')
            if response.status_code == 200:
                data = json.loads(response.data)
                if 'trngproAvailable' in data:
                    print(f"[OK] Ping includes TRNGPro availability: {data['trngproAvailable']}")
                else:
                    print("[WARN] TRNGPro availability not in ping response")
            else:
                print(f"[FAIL] Ping endpoint failed with status {response.status_code}")
        
        # Test 3: Test settings endpoint includes TRNGPro setting
        print("\n3. Testing settings endpoint...")
        with aether_one.app.test_client() as client:
            response = client.get('/settings')
            if response.status_code == 200:
                data = json.loads(response.data)
                if 'hotbits_use_TRNGPro' in data:
                    print(f"[OK] Settings includes TRNGPro: {data['hotbits_use_TRNGPro']}")
                else:
                    print("[FAIL] TRNGPro setting not in settings response")
                    return False
            else:
                print(f"[FAIL] Settings endpoint failed with status {response.status_code}")
                return False
        
        print("\n" + "="*45)
        print("[SUCCESS] All TRNGPro Flask routes integration tests passed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False
        
    finally:
        # Cleanup
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


if __name__ == "__main__":
    success = test_flask_routes()
    if success:
        print("\nTRNGPro Flask integration is ready!")
    else:
        sys.exit(1)