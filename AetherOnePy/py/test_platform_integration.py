#!/usr/bin/env python3
"""Test platform-aware TRNGPro integration"""
import os
import sys
import tempfile

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.hotbitsService import HotbitsService, HotbitsSource
from services.databaseService import CaseDAO


class MockMain:
    def emitMessage(self, channel, message):
        print(f"[{channel}] {message}")


def test_platform_integration():
    print("Testing Platform-Aware TRNGPro Integration")
    print("=" * 45)
    
    temp_dir = tempfile.mkdtemp()
    try:
        hotbits_dir = os.path.join(temp_dir, 'hotbits')
        os.makedirs(hotbits_dir)
        
        case_dao = CaseDAO(os.path.join(temp_dir, 'test.db'))
        
        hotbits_service = HotbitsService(
            HotbitsSource.TRNGPRO, 
            hotbits_dir, 
            case_dao, 
            MockMain(), 
            useTRNGPro=True
        )
        
        # Test platform info
        platform_info = hotbits_service.trngproCollector.get_platform_info()
        print(f"Platform: {platform_info['system']}")
        print(f"Architecture: {platform_info['architecture'][0]}")
        
        case_dao.conn.close()
        print("[OK] Platform-aware TRNGPro integration successful!")
        
    except Exception as e:
        print(f"[FAIL] Test failed: {e}")
    finally:
        import shutil
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


if __name__ == "__main__":
    test_platform_integration()