import serial
import serial.tools.list_ports
import struct
import json
import time
import os
import sys
import platform

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))


class TRNGProCollector:
    def __init__(self, main, countHotbits, port=None, mode='normal', baudrate=115200, timeout=5):
        self.stopCollectingHotbits = False
        self.main = main
        self.countHotbits = countHotbits
        self.port = port
        self.mode = mode  # 'normal' for whitened, 'raw' for raw binary
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None
        self.system_platform = platform.system()
        print(f"TRNGPro collector initialized for {self.system_platform} platform")
    
    def get_platform_info(self):
        """Get detailed platform information"""
        return {
            'system': self.system_platform,
            'platform': platform.platform(),
            'architecture': platform.architecture(),
            'processor': platform.processor(),
            'python_version': platform.python_version()
        }

    def find_trngpro_device(self):
        """Find TRNGPro device by scanning serial ports with platform-specific logic"""
        system_platform = platform.system()
        
        ports = serial.tools.list_ports.comports()
        
        # Look for TRNGPro device identifiers first
        for port in ports:
            if ('TrueRNGpro' in port.description or 
                'CDC' in port.description or 
                'TrueRNG' in str(port.description)):
                try:
                    # Test connection
                    test_conn = serial.Serial(port.device, self.baudrate, timeout=1)
                    test_conn.close()
                    print(f"Found TRNGPro device by description at: {port.device} ({port.description})")
                    return port.device
                except Exception as e:
                    continue
        
        # Platform-specific fallback ports
        common_ports = []
        
        if system_platform == "Windows":
            # Windows COM ports
            common_ports = ['COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8']
            print("Scanning Windows COM ports for TRNGPro device...")
        elif system_platform == "Linux":
            # Linux USB serial ports (including Raspberry Pi)
            common_ports = ['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2', 
                          '/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2']
            print("Scanning Linux USB ports for TRNGPro device...")
        elif system_platform == "Darwin":  # macOS
            # macOS USB serial ports
            common_ports = ['/dev/tty.usbmodem*', '/dev/tty.usbserial*', 
                          '/dev/cu.usbmodem*', '/dev/cu.usbserial*']
            print("Scanning macOS USB ports for TRNGPro device...")
            
            # For macOS, we need to expand wildcards
            import glob
            expanded_ports = []
            for pattern in common_ports:
                expanded_ports.extend(glob.glob(pattern))
            common_ports = expanded_ports
        else:
            print(f"Unknown platform {system_platform}, using generic port names...")
            common_ports = ['/dev/ttyACM0', '/dev/ttyUSB0', 'COM3']
        
        # Try platform-specific common ports
        for port in common_ports:
            try:
                test_conn = serial.Serial(port, self.baudrate, timeout=1)
                test_conn.close()
                print(f"Found serial device at: {port} (Platform: {system_platform})")
                return port
            except:
                continue
                
        print(f"No TRNGPro device found on {system_platform} platform")
        return None

    def connect_to_device(self):
        """Establish connection to TRNGPro device"""
        if not self.port:
            self.port = self.find_trngpro_device()
            
        if not self.port:
            self.main.emitMessage('hotbits', 'TRNGPro device not found!')
            return False
            
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            # Configure device mode
            if self.mode == 'raw':
                self.serial_connection.write(b'r')  # Raw mode command
            else:
                self.serial_connection.write(b'n')  # Normal/whitened mode
                
            time.sleep(0.1)  # Allow device to switch modes
            
            self.main.emitMessage('hotbits', f'Connected to TRNGPro at {self.port} ({self.system_platform} platform, {self.mode} mode)')
            return True
            
        except Exception as e:
            self.main.emitMessage('hotbits', f'Failed to connect to TRNGPro: {str(e)}')
            return False

    def disconnect_from_device(self):
        """Close serial connection"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.serial_connection = None

    def bytes_to_integers(self, data_bytes, bytes_per_int=4):
        """Convert raw bytes to 32-bit integers"""
        integers = []
        for i in range(0, len(data_bytes) - bytes_per_int + 1, bytes_per_int):
            chunk = data_bytes[i:i + bytes_per_int]
            if len(chunk) == bytes_per_int:
                integer = struct.unpack('<I', chunk)[0]  # Little-endian unsigned int
                integers.append(integer)
        return integers

    def read_random_data(self, byte_count=40000):
        """Read random bytes from TRNGPro device"""
        if not self.serial_connection or not self.serial_connection.is_open:
            raise Exception("Not connected to TRNGPro device")
            
        data = b''
        start_time = time.time()
        
        while len(data) < byte_count:
            if self.stopCollectingHotbits:
                break
                
            # Check for timeout
            if time.time() - start_time > self.timeout * 2:
                raise Exception("Timeout reading from TRNGPro device")
                
            available = self.serial_connection.in_waiting
            if available > 0:
                chunk = self.serial_connection.read(min(available, byte_count - len(data)))
                data += chunk
            else:
                time.sleep(0.01)  # Small delay to prevent busy waiting
                
        return data

    def checkIfTRNGProIsAvailable(self):
        """Check if TRNGPro device is available and responding"""
        try:
            if self.connect_to_device():
                # Test reading a small amount of data
                test_data = self.read_random_data(100)
                self.disconnect_from_device()
                return len(test_data) > 0
        except Exception as e:
            print(f"TRNGPro availability check failed: {e}")
            
        return False

    def stop_generate_hotbits(self):
        """Stop the hotbits generation process"""
        self.stopCollectingHotbits = True

    def generate_hotbits(self, hotbitsPath: str, amount: int):
        """Generate hotbits using TRNGPro device"""
        print(f"generate_hotbits with TRNGPro on {self.system_platform} platform")
        
        if not self.connect_to_device():
            raise Exception(f"Failed to connect to TRNGPro device on {self.system_platform}")
            
        try:
            self.main.emitMessage('hotbits', 'Starting TRNGPro collection...')
            
            for batch in range(amount):
                if self.stopCollectingHotbits:
                    break
                    
                # Read 40KB of random data (should yield 10,000 32-bit integers)
                random_bytes = self.read_random_data(40000)
                
                # Convert bytes to integers
                integer_list = self.bytes_to_integers(random_bytes)
                
                # Ensure we have exactly 10,000 unique integers
                unique_integers = list(set(integer_list))[:10000]
                
                # If we don't have enough unique integers, read more data
                while len(unique_integers) < 10000 and not self.stopCollectingHotbits:
                    additional_bytes = self.read_random_data(4000)
                    additional_integers = self.bytes_to_integers(additional_bytes)
                    
                    for integer in additional_integers:
                        if integer not in unique_integers:
                            unique_integers.append(integer)
                            if len(unique_integers) >= 10000:
                                break
                
                # Trim to exactly 10,000 integers
                integer_list = unique_integers[:10000]
                
                # Save the integers to JSON file
                timestamp = int(time.time() * 1000)
                filename = f"{hotbitsPath}/hotbits_{timestamp}.json"
                with open(filename, 'w') as f:
                    json.dump({
                        "integerList": integer_list, 
                        "source": f"TRNGPro_{self.mode}",
                        "device_port": self.port,
                        "platform": self.system_platform,
                        "mode": self.mode,
                        "baudrate": self.baudrate
                    }, f)
                
                self.main.emitMessage('server_update', str(self.countHotbits()))
                print(f"TRNGPro hotbits saved to {filename}")
                
        except Exception as e:
            self.main.emitMessage('hotbits', f'TRNGPro error: {str(e)}')
            raise e
        finally:
            self.disconnect_from_device()
            self.stopCollectingHotbits = False


if __name__ == "__main__":
    # Test the TRNGPro collector
    class MockMain:
        def emitMessage(self, channel, message):
            print(f"[{channel}] {message}")
    
    def mock_count_hotbits():
        return 0
    
    collector = TRNGProCollector(MockMain(), mock_count_hotbits)
    
    if collector.checkIfTRNGProIsAvailable():
        print("TRNGPro device found and working")
        test_path = os.path.join(PROJECT_ROOT, "hotbits")
        os.makedirs(test_path, exist_ok=True)
        collector.generate_hotbits(test_path, 1)
    else:
        print("TRNGPro device not available")