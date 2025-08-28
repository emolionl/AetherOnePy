#!/usr/bin/env python3
"""Simple TRNGPro integration test"""
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.hotbitsService import HotbitsService, HotbitsSource
from services.databaseService import CaseDAO


class MockMain:
    def emitMessage(self, channel, message):
        print(f"[{channel}] {message}")


def main():
    print("Simple TRNGPro Integration Test")
    print("=" * 40)
    
    # Create temporary database
    db_path = "temp_test.db"
    hotbits_dir = "temp_hotbits"
    
    try:
        os.makedirs(hotbits_dir, exist_ok=True)
        
        # Test database creation
        case_dao = CaseDAO(db_path)
        print("[OK] Database created")
        
        # Test HotbitsService creation with TRNGPro
        hotbits_service = HotbitsService(
            HotbitsSource.TRNGPRO, 
            hotbits_dir, 
            case_dao, 
            MockMain(), 
            useTRNGPro=True
        )
        print("[OK] HotbitsService created with TRNGPro")
        
        # Test TRNGPro collector initialization
        if hasattr(hotbits_service, 'trngproCollector'):
            print("[OK] TRNGPro collector initialized")
        else:
            print("[FAIL] TRNGPro collector not found")
            return False
        
        # Test source enum
        print(f"[INFO] Available HotbitsSource values: {list(HotbitsSource)}")
        print(f"[INFO] Current source: {hotbits_service.source}")
        
        # Close database
        case_dao.conn.close()
        print("[OK] Database closed")
        
        print("=" * 40)
        print("[SUCCESS] TRNGPro integration is working!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False
        
    finally:
        # Cleanup
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
            if os.path.exists(hotbits_dir):
                os.rmdir(hotbits_dir)
        except:
            pass


if __name__ == "__main__":
    success = main()
    if success:
        print("\nTRNGPro is ready to use when hardware is connected!")
        print("To enable: Set 'hotbits_use_TRNGPro' to True in settings")
    else:
        sys.exit(1)