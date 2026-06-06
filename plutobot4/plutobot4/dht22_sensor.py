import platform

# Check if we're on a supported platform for hardware sensors
IS_RASPBERRY_PI = platform.machine().startswith('arm') and platform.system() == 'Linux'
IS_SUPPORTED_HARDWARE = IS_RASPBERRY_PI

try:
    # Only try to import hardware libraries on supported platforms
    if IS_SUPPORTED_HARDWARE:
        try:
            # Try modern CircuitPython library first
            import adafruit_dht
            import board
            CIRCUITPYTHON_AVAILABLE = True
            ADAFRUIT_DHT_AVAILABLE = False
            print("✅ Using modern Adafruit CircuitPython DHT library")
        except ImportError:
            try:
                # Fallback to legacy Adafruit_DHT library
                import Adafruit_DHT  # type: ignore
                ADAFRUIT_DHT_AVAILABLE = True
                CIRCUITPYTHON_AVAILABLE = False
                print("✅ Using legacy Adafruit_DHT library")
            except ImportError:
                ADAFRUIT_DHT_AVAILABLE = False
                CIRCUITPYTHON_AVAILABLE = False
                print("⚠️  DHT22 libraries not found on Raspberry Pi")
    else:
        # Not on Raspberry Pi - skip hardware libraries
        ADAFRUIT_DHT_AVAILABLE = False
        CIRCUITPYTHON_AVAILABLE = False
        print(f"🔧 Running on {platform.system()} {platform.machine()} - using mock DHT22 sensor")

except Exception as e:
    ADAFRUIT_DHT_AVAILABLE = False
    CIRCUITPYTHON_AVAILABLE = False
    print(f"⚠️  DHT22 library import failed: {e}")

import time
import json
from datetime import datetime

class DHT22Sensor:
    def __init__(self, pin=4):
        """
        Initialize DHT22 sensor
        pin: GPIO pin number (default is 4)
        """
        self.pin = pin
        self.last_reading = None
        self.last_reading_time = None
        
        # Initialize sensor based on available library
        if CIRCUITPYTHON_AVAILABLE:
            try:
                # Modern CircuitPython approach
                pin_obj = getattr(board, f'D{pin}', None)  # type: ignore
                if pin_obj:
                    self.sensor = adafruit_dht.DHT22(pin_obj)  # type: ignore
                    self.sensor_type = 'circuitpython'
                else:
                    self.sensor = None
                    self.sensor_type = 'mock'
            except Exception:
                self.sensor = None
                self.sensor_type = 'mock'
        elif ADAFRUIT_DHT_AVAILABLE:
            # Legacy library
            self.sensor = Adafruit_DHT.DHT22  # type: ignore
            self.sensor_type = 'legacy'
        else:
            # Mock sensor
            self.sensor = None
            self.sensor_type = 'mock'
        
    def read_sensor(self):
        """
        Read temperature and humidity from DHT22 sensor
        Returns: dict with temperature, humidity, timestamp, or None if failed
        """
        try:
            if self.sensor_type == 'mock':
                # Return mock data for testing
                import random
                temp = round(22 + random.uniform(-3, 6), 1)  # 19-28°C range
                humidity = round(45 + random.uniform(-10, 20), 1)  # 35-65% range
                reading = {
                    'temperature_c': temp,
                    'temperature_f': round(temp * 9/5 + 32, 1),
                    'humidity': humidity,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success',
                    'mock': True,
                    'sensor_type': 'mock'
                }
                self.last_reading = reading
                self.last_reading_time = time.time()
                return reading
            
            elif self.sensor_type == 'circuitpython':
                # Modern CircuitPython library
                temperature = self.sensor.temperature  # type: ignore
                humidity = self.sensor.humidity  # type: ignore
                
                if temperature is not None and humidity is not None:
                    reading = {
                        'temperature_c': round(temperature, 1),
                        'temperature_f': round(temperature * 9/5 + 32, 1),
                        'humidity': round(humidity, 1),
                        'timestamp': datetime.now().isoformat(),
                        'status': 'success',
                        'mock': False,
                        'sensor_type': 'circuitpython'
                    }
                    self.last_reading = reading
                    self.last_reading_time = time.time()
                    return reading
                    
            elif self.sensor_type == 'legacy':
                # Legacy Adafruit_DHT library
                humidity, temperature = Adafruit_DHT.read_retry(self.sensor, self.pin)  # type: ignore
                
                if humidity is not None and temperature is not None:
                    reading = {
                        'temperature_c': round(temperature, 1),
                        'temperature_f': round(temperature * 9/5 + 32, 1),
                        'humidity': round(humidity, 1),
                        'timestamp': datetime.now().isoformat(),
                        'status': 'success',
                        'mock': False,
                        'sensor_type': 'legacy'
                    }
                    self.last_reading = reading
                    self.last_reading_time = time.time()
                    return reading
            
            # If we get here, sensor reading failed
            return {
                'temperature_c': None,
                'temperature_f': None,
                'humidity': None,
                'timestamp': datetime.now().isoformat(),
                'status': 'failed',
                'error': 'Failed to get sensor reading',
                'sensor_type': self.sensor_type
            }
            
        except Exception as e:
            return {
                'temperature_c': None,
                'temperature_f': None,
                'humidity': None,
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e),
                'sensor_type': self.sensor_type
            }
    
    def get_cached_reading(self, max_age_seconds=30):
        """
        Get last reading if it's fresh enough, otherwise take new reading
        max_age_seconds: maximum age of cached reading before taking new one
        """
        if (self.last_reading and self.last_reading_time and 
            time.time() - self.last_reading_time < max_age_seconds):
            return self.last_reading
        else:
            return self.read_sensor()
    
    def get_temperature_celsius(self):
        """Get just temperature in Celsius"""
        reading = self.get_cached_reading()
        return reading.get('temperature_c') if reading['status'] == 'success' else None
    
    def get_temperature_fahrenheit(self):
        """Get just temperature in Fahrenheit"""
        reading = self.get_cached_reading()
        return reading.get('temperature_f') if reading['status'] == 'success' else None
    
    def get_humidity(self):
        """Get just humidity percentage"""
        reading = self.get_cached_reading()
        return reading.get('humidity') if reading['status'] == 'success' else None
    
    def format_reading(self, reading=None, use_fahrenheit=False):
        """
        Format sensor reading for speech output
        """
        if reading is None:
            reading = self.get_cached_reading()
        
        if reading['status'] != 'success':
            return f"Sorry, couldn't read the sensor right now. {reading.get('error', '')}"
        
        temp = reading['temperature_f'] if use_fahrenheit else reading['temperature_c']
        temp_unit = "°F" if use_fahrenheit else "°C"
        
        return f"It's {temp}{temp_unit} and {reading['humidity']}% humidity in here."

# Convenience function for easy import
def get_room_conditions(use_fahrenheit=False):
    """
    Quick function to get formatted room conditions
    Returns string suitable for voice output
    """
    sensor = DHT22Sensor()
    reading = sensor.read_sensor()
    return sensor.format_reading(reading, use_fahrenheit)

# Test function
if __name__ == "__main__":
    print("Testing DHT22 sensor...")
    sensor = DHT22Sensor()
    
    for i in range(3):
        reading = sensor.read_sensor()
        print(f"Reading {i+1}: {reading}")
        if reading['status'] == 'success':
            print(f"Formatted: {sensor.format_reading(reading)}")
        time.sleep(2)
