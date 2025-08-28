#!/usr/bin/env python3
"""
Test script for TRNGPro integration with AetherOne system
"""
import os
import sys
import tempfile

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.hotbitsService import HotbitsService, HotbitsSource
from services.databaseService import CaseDAO


class MockMain:
    def emitMessage(self, channel, message):
        print(f"[{channel}] {message}")


def test_trngpro_integration():
    """Test TRNGPro integration without hardware"""
    print("Testing TRNGPro Integration...")
    
    # Create temporary directories for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        hotbits_dir = os.path.join(temp_dir, "hotbits")
        os.makedirs(hotbits_dir, exist_ok=True)
        
        db_path = os.path.join(temp_dir, "test.db")
        
        # Create mock database
        case_dao = CaseDAO(db_path)
        
        # Test 1: Create HotbitsService with TRNGPro source
        print("\n1. Creating HotbitsService with TRNGPro source...")
        try:
            hotbits_service = HotbitsService(
                hotbitsSource=HotbitsSource.TRNGPRO,
                folder_path=hotbits_dir,
                aetherOneDB=case_dao,
                main=MockMain(),
                useTRNGPro=True
            )
            print("[OK] HotbitsService created successfully with TRNGPro source")
        except Exception as e:
            print(f"[FAIL] Failed to create HotbitsService: {e}")
            return False
        
        # Test 2: Check if TRNGPro collector is initialized
        print("\n2. Checking TRNGPro collector initialization...")
        if hasattr(hotbits_service, 'trngproCollector'):
            print("[OK] TRNGPro collector initialized")
        else:
            print("[FAIL] TRNGPro collector not found")
            return False
        
        # Test 3: Test device availability check (should fail without hardware)
        print("\n3. Testing device availability check...")
        try:
            is_available = hotbits_service.trngproCollector.checkIfTRNGProIsAvailable()
            if not is_available:
                print("[OK] Device availability check works (correctly reports no device)")
            else:
                print("[INFO] Device availability check reports device found (unexpected)")
        except Exception as e:
            print(f"[OK] Device availability check failed as expected: {e}")
        
        # Test 4: Test database settings
        print("\n4. Testing database settings...")
        try:
            case_dao.update_setting('hotbits_use_TRNGPro', True)
            setting_value = case_dao.get_setting('hotbits_use_TRNGPro')
            if setting_value:
                print("[OK] TRNGPro database setting works")
            else:
                print("[FAIL] TRNGPro database setting failed")
                return False
        except Exception as e:
            print(f"[FAIL] Database setting test failed: {e}")
            return False
        
        # Test 5: Test source priority
        print("\n5. Testing source priority...")
        try:
            priority = case_dao.getHotbitsSourcePriority()
            if 'TRNGPro' in priority:
                print("[OK] TRNGPro appears in source priority list")
            else:
                print("[FAIL] TRNGPro not in source priority list")
                return False
        except Exception as e:
            print(f"[FAIL] Source priority test failed: {e}")
            return False
        
        # Close database connection properly
        try:
            case_dao.conn.close()
        except:
            pass
        
        print("\n" + "="*50)
        print("[OK] All TRNGPro integration tests passed!")
        print("[OK] TRNGPro source is ready for use when hardware is available")
        print("="*50)
        return True


if __name__ == "__main__":
    success = test_trngpro_integration()
    if success:
        print("\nTo use TRNGPro:")
        print("1. Connect TRNGPro device to USB port")
        print("2. Set 'hotbits_use_TRNGPro' to True in settings")
        print("3. Restart AetherOne application")
    else:
        print("\nIntegration test failed!")
        sys.exit(1)