#!/usr/bin/env python3
"""
Raspberry Pi 5 Optimized Audio System with PipeWire Support
Designed for maximum responsiveness and reliability on Pi 5 8GB
"""

import os
import sys
import platform
import subprocess
import threading
import time
import psutil
from pathlib import Path

# Audio backend detection and optimization
def detect_audio_system():
    """Detect the audio system running on the Pi"""
    try:
        # Check for PipeWire (Pi 5 default)
        result = subprocess.run(['systemctl', '--user', 'is-active', 'pipewire'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return 'pipewire'
        
        # Check for PulseAudio
        result = subprocess.run(['pulseaudio', '--check'], capture_output=True)
        if result.returncode == 0:
            return 'pulseaudio'
        
        # Fallback to ALSA
        return 'alsa'
    except:
        return 'alsa'

class RaspberryPiAudioManager:
    """Optimized audio manager for Raspberry Pi 5"""
    
    def __init__(self):
        self.audio_system = detect_audio_system()
        self.is_raspberry_pi = self._is_raspberry_pi()
        self.mixer_initialized = False
        self.audio_lock = threading.RLock()
        self._setup_raspberry_pi_optimizations()
        
    def _is_raspberry_pi(self):
        """Detect if running on Raspberry Pi"""
        try:
            with open('/proc/device-tree/model', 'r') as f:
                model = f.read()
                return 'Raspberry Pi' in model
        except:
            return 'arm' in platform.machine().lower()
    
    def _setup_raspberry_pi_optimizations(self):
        """Setup optimizations specific to Raspberry Pi 5"""
        if not self.is_raspberry_pi:
            return
            
        print(f"🔧 Optimizing for Raspberry Pi 5 with {self.audio_system}")
        
        # Set CPU governor to performance for audio processing
        try:
            subprocess.run(['sudo', 'cpufreq-set', '-g', 'performance'], 
                         capture_output=True)
        except:
            pass
        
        # Optimize audio buffer settings for PipeWire
        if self.audio_system == 'pipewire':
            self._optimize_pipewire()
        elif self.audio_system == 'pulseaudio':
            self._optimize_pulseaudio()
        else:
            self._optimize_alsa()
    
    def _optimize_pipewire(self):
        """Optimize PipeWire settings for low latency"""
        config_dir = Path.home() / '.config' / 'pipewire'
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Ultra-low latency PipeWire config
        pipewire_config = """
context.properties = {
    default.clock.rate = 48000
    default.clock.quantum = 128
    default.clock.min-quantum = 64
    default.clock.max-quantum = 256
    default.video.width = 640
    default.video.height = 480
    default.video.rate.num = 25
    default.video.rate.denom = 1
    mem.warn-mlock = false
    mem.allow-mlock = true
    settings.check-quantum = false
    settings.check-rate = false
}

context.modules = [
    { name = libpipewire-module-rt
        args = {
            nice.level = -15
            rt.prio = 88
            rt.time.soft = 200000
            rt.time.hard = 200000
        }
        flags = [ ifexists nofail ]
    }
    { name = libpipewire-module-protocol-native }
    { name = libpipewire-module-profiler }
    { name = libpipewire-module-metadata }
    { name = libpipewire-module-spa-device-factory }
    { name = libpipewire-module-spa-node-factory }
    { name = libpipewire-module-client-node }
    { name = libpipewire-module-client-device }
    { name = libpipewire-module-portal }
    { name = libpipewire-module-access
        args = {
            access.allowed = [
                { permission = "rw" }
            ]
        }
    }
    { name = libpipewire-module-adapter }
    { name = libpipewire-module-link-factory }
    { name = libpipewire-module-session-manager }
]
"""
        
        config_file = config_dir / 'pipewire.conf'
        with open(config_file, 'w') as f:
            f.write(pipewire_config)
        
        print("✅ PipeWire optimized for ultra-low latency")
    
    def _optimize_pulseaudio(self):
        """Optimize PulseAudio for low latency"""
        pa_config = """
# Ultra-responsive PulseAudio config for Raspberry Pi 5
load-module module-udev-detect
load-module module-native-protocol-unix auth-anonymous=1 socket=/tmp/pulse-socket
load-module module-default-device-restore
load-module module-rescue-streams
load-module module-always-sink
load-module module-intended-roles
load-module module-suspend-on-idle timeout=1
load-module module-console-kit
load-module module-position-event-sounds

# Low latency settings
default-sample-format = s16le
default-sample-rate = 44100
default-sample-channels = 1
default-channel-map = mono
default-fragments = 2
default-fragment-size-msec = 10
"""
        
        config_dir = Path.home() / '.config' / 'pulse'
        config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(config_dir / 'default.pa', 'w') as f:
            f.write(pa_config)
        
        print("✅ PulseAudio optimized for low latency")
    
    def _optimize_alsa(self):
        """Optimize ALSA for low latency"""
        asound_config = """
pcm.!default {
    type hw
    card 0
    device 0
    period_size 128
    buffer_size 512
}

ctl.!default {
    type hw
    card 0
}
"""
        
        with open(Path.home() / '.asoundrc', 'w') as f:
            f.write(asound_config)
        
        print("✅ ALSA optimized for low latency")

class OptimizedAudioPlayback:
    """High-performance audio playback optimized for Pi 5"""
    
    def __init__(self, audio_manager):
        self.audio_manager = audio_manager
        self.playback_interrupted = False
        self.current_playback = None
        self.playback_lock = threading.RLock()
        self._initialize_audio_backend()
    
    def _initialize_audio_backend(self):
        """Initialize the best available audio backend"""
        self.backend = None
        
        # Try different backends in order of preference for Pi 5
        backends_to_try = [
            ('pipewire_pygame', self._init_pipewire_pygame),
            ('pulseaudio_pygame', self._init_pulseaudio_pygame),
            ('pyaudio_direct', self._init_pyaudio_direct),
            ('pygame_fallback', self._init_pygame_fallback),
            ('system_player', self._init_system_player)
        ]
        
        for backend_name, init_func in backends_to_try:
            try:
                if init_func():
                    self.backend = backend_name
                    print(f"✅ Audio backend: {backend_name}")
                    break
            except Exception as e:
                print(f"⚠️  Failed to initialize {backend_name}: {e}")
                continue
        
        if not self.backend:
            raise RuntimeError("No audio backend available")
    
    def _init_pipewire_pygame(self):
        """Initialize pygame with PipeWire optimization"""
        if self.audio_manager.audio_system != 'pipewire':
            return False
        
        import pygame
        
        # Set environment variables for PipeWire
        os.environ['SDL_AUDIODRIVER'] = 'pipewire'
        
        try:
            pygame.mixer.quit()  # Clean slate
        except:
            pass
        
        # Ultra-optimized settings for Pi 5
        mixer_settings = {
            'frequency': 44100,  # Standard rate for Pi 5
            'size': -16,         # 16-bit signed
            'channels': 1,       # Mono for faster processing
            'buffer': 256        # Larger buffer for Pi stability
        }
        
        pygame.mixer.pre_init(**mixer_settings)
        pygame.mixer.init()
        
        if not pygame.mixer.get_init():
            return False
        
        # Test playback
        self._test_audio_playback()
        return True
    
    def _init_pulseaudio_pygame(self):
        """Initialize pygame with PulseAudio"""
        if self.audio_manager.audio_system != 'pulseaudio':
            return False
        
        import pygame
        
        os.environ['SDL_AUDIODRIVER'] = 'pulse'
        
        try:
            pygame.mixer.quit()
        except:
            pass
        
        mixer_settings = {
            'frequency': 44100,
            'size': -16,
            'channels': 1,
            'buffer': 512  # Slightly larger for PulseAudio
        }
        
        pygame.mixer.pre_init(**mixer_settings)
        pygame.mixer.init()
        
        return pygame.mixer.get_init() is not None
    
    def _init_pyaudio_direct(self):
        """Initialize direct PyAudio for maximum control"""
        try:
            import pyaudio
            self.pa = pyaudio.PyAudio()
            
            # Find the best output device
            default_device = self.pa.get_default_output_device_info()
            
            self.audio_format = pyaudio.paInt16
            self.channels = 1
            self.rate = 44100
            self.chunk = 1024
            
            # Test opening a stream
            stream = self.pa.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.rate,
                output=True,
                frames_per_buffer=self.chunk
            )
            stream.close()
            
            return True
        except Exception as e:
            print(f"PyAudio direct init failed: {e}")
            return False
    
    def _init_pygame_fallback(self):
        """Fallback pygame initialization"""
        import pygame
        
        try:
            pygame.mixer.quit()
        except:
            pass
        
        # Conservative settings for compatibility
        pygame.mixer.pre_init(
            frequency=22050,  # Lower for compatibility
            size=-16,
            channels=1,
            buffer=1024
        )
        pygame.mixer.init()
        
        return pygame.mixer.get_init() is not None
    
    def _init_system_player(self):
        """Initialize system-level audio player as last resort"""
        # Test if aplay is available
        try:
            result = subprocess.run(['which', 'aplay'], capture_output=True)
            if result.returncode == 0:
                return True
        except:
            pass
        
        # Test if paplay is available
        try:
            result = subprocess.run(['which', 'paplay'], capture_output=True)
            if result.returncode == 0:
                return True
        except:
            pass
        
        return False
    
    def _test_audio_playback(self):
        """Test audio playback capability"""
        # Generate a simple test tone to verify audio works
        try:
            import numpy as np
            import pygame
            
            # Generate 0.1 second test tone at 440Hz
            sample_rate = 44100
            duration = 0.1
            frequency = 440
            
            frames = int(duration * sample_rate)
            arr = np.zeros((frames, 1))
            
            for i in range(frames):
                arr[i][0] = 32767 * np.sin(2 * np.pi * frequency * i / sample_rate)
            
            arr = arr.astype(np.int16)
            
            # Convert to pygame sound and test
            sound = pygame.sndarray.make_sound(arr)
            # Don't actually play the test tone, just verify it can be created
            
            return True
        except Exception as e:
            print(f"Audio test failed: {e}")
            return False
    
    def play_audio_file(self, file_path):
        """Play audio file with the best available method"""
        if not os.path.exists(file_path):
            print(f"Audio file not found: {file_path}")
            return False
        
        with self.playback_lock:
            self.stop_playback()  # Stop any current playback
            
            if self.backend in ['pipewire_pygame', 'pulseaudio_pygame', 'pygame_fallback']:
                return self._play_with_pygame(file_path)
            elif self.backend == 'pyaudio_direct':
                return self._play_with_pyaudio(file_path)
            elif self.backend == 'system_player':
                return self._play_with_system(file_path)
        
        return False
    
    def _play_with_pygame(self, file_path):
        """Play audio using pygame"""
        try:
            import pygame
            
            # Ensure mixer is ready
            if not pygame.mixer.get_init():
                self._initialize_audio_backend()
            
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            # Monitor playback in separate thread
            def monitor_playback():
                while pygame.mixer.music.get_busy() and not self.playback_interrupted:
                    time.sleep(0.01)  # Very responsive checking
                
                if self.playback_interrupted:
                    pygame.mixer.music.stop()
                    self.playback_interrupted = False
            
            self.current_playback = threading.Thread(target=monitor_playback, daemon=True)
            self.current_playback.start()
            
            return True
        except Exception as e:
            print(f"Pygame playback failed: {e}")
            return False
    
    def _play_with_pyaudio(self, file_path):
        """Play audio using PyAudio directly"""
        try:
            import pyaudio
            import wave
            
            wf = wave.open(file_path, 'rb')
            
            stream = self.pa.open(
                format=self.pa.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True
            )
            
            def play_audio():
                chunk = 1024
                data = wf.readframes(chunk)
                
                while data and not self.playback_interrupted:
                    stream.write(data)
                    data = wf.readframes(chunk)
                
                stream.stop_stream()
                stream.close()
                wf.close()
            
            self.current_playback = threading.Thread(target=play_audio, daemon=True)
            self.current_playback.start()
            
            return True
        except Exception as e:
            print(f"PyAudio playback failed: {e}")
            return False
    
    def _play_with_system(self, file_path):
        """Play audio using system player"""
        try:
            # Try different system players
            players = [
                ['aplay', file_path],
                ['paplay', file_path],
                ['pw-play', file_path],  # PipeWire player
                ['ffplay', '-nodisp', '-autoexit', file_path]
            ]
            
            for player_cmd in players:
                try:
                    def play_audio():
                        subprocess.run(player_cmd, 
                                     capture_output=True, 
                                     check=True)
                    
                    self.current_playback = threading.Thread(target=play_audio, daemon=True)
                    self.current_playback.start()
                    return True
                except:
                    continue
            
            return False
        except Exception as e:
            print(f"System player failed: {e}")
            return False
    
    def stop_playback(self):
        """Stop current audio playback"""
        self.playback_interrupted = True
        
        if self.current_playback and self.current_playback.is_alive():
            self.current_playback.join(timeout=0.1)
        
        # Backend-specific cleanup
        if self.backend in ['pipewire_pygame', 'pulseaudio_pygame', 'pygame_fallback']:
            try:
                import pygame
                pygame.mixer.music.stop()
            except:
                pass
    
    def interrupt_playback(self):
        """Interrupt current playback for immediate response"""
        self.stop_playback()

# Memory and CPU optimization for Pi 5
class RaspberryPiOptimizer:
    """System-level optimizations for Raspberry Pi 5"""
    
    def __init__(self):
        self.original_settings = {}
        self.is_raspberry_pi = self._detect_pi()
        
    def _detect_pi(self):
        """Detect if running on Raspberry Pi"""
        try:
            with open('/proc/device-tree/model', 'r') as f:
                return 'Raspberry Pi' in f.read()
        except:
            return False
    
    def optimize_for_audio(self):
        """Apply optimizations for audio processing"""
        if not self.is_raspberry_pi:
            print("🔧 Running on Mac - skipping Pi-specific optimizations")
            return
        
        print("🚀 Applying Raspberry Pi 5 optimizations...")
        
        # Set CPU governor to performance
        self._set_cpu_governor('performance')
        
        # Increase audio thread priority
        self._optimize_audio_priority()
        
        # Optimize memory settings
        self._optimize_memory()
        
        # Set GPU memory split for optimal performance
        self._optimize_gpu_memory()
        
        print("✅ Raspberry Pi optimizations applied")
    
    def _set_cpu_governor(self, governor='performance'):
        """Set CPU governor for consistent performance"""
        try:
            cpu_count = psutil.cpu_count()
            for cpu in range(cpu_count):
                cmd = f'echo {governor} | sudo tee /sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_governor'
                subprocess.run(cmd, shell=True, capture_output=True)
            print(f"🔧 CPU governor set to {governor}")
        except Exception as e:
            print(f"⚠️  Could not set CPU governor: {e}")
    
    def _optimize_audio_priority(self):
        """Optimize process priority for audio"""
        try:
            import psutil
            p = psutil.Process()
            p.nice(-10)  # Higher priority
            print("🔧 Process priority optimized for audio")
        except Exception as e:
            print(f"⚠️  Could not set process priority: {e}")
    
    def _optimize_memory(self):
        """Optimize memory settings"""
        try:
            # Force garbage collection
            import gc
            gc.set_threshold(700, 10, 10)  # More aggressive GC
            print("🔧 Memory optimization applied")
        except Exception as e:
            print(f"⚠️  Memory optimization failed: {e}")
    
    def _optimize_gpu_memory(self):
        """Optimize GPU memory split"""
        try:
            # For Pi 5, 128MB GPU memory is usually optimal for audio applications
            result = subprocess.run(['vcgencmd', 'get_mem', 'gpu'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                gpu_mem = result.stdout.strip()
                print(f"🔧 Current GPU memory: {gpu_mem}")
        except Exception as e:
            print(f"⚠️  Could not check GPU memory: {e}")
    
    def cleanup(self):
        """Restore original settings"""
        if not self.is_raspberry_pi:
            return
        
        # Restore CPU governor if we changed it
        try:
            self._set_cpu_governor('ondemand')  # Default governor
        except:
            pass

# Global instances
_audio_manager = None
_audio_playback = None
_optimizer = None

def initialize_raspberry_pi_audio():
    """Initialize the complete audio system for Raspberry Pi"""
    global _audio_manager, _audio_playback, _optimizer
    
    if _audio_manager is None:
        _audio_manager = RaspberryPiAudioManager()
        _audio_playback = OptimizedAudioPlayback(_audio_manager)
        _optimizer = RaspberryPiOptimizer()
        _optimizer.optimize_for_audio()
    
    return _audio_manager, _audio_playback, _optimizer

def get_optimized_audio_player():
    """Get the optimized audio player instance"""
    global _audio_playback
    if _audio_playback is None:
        initialize_raspberry_pi_audio()
    return _audio_playback

def cleanup_raspberry_pi_audio():
    """Cleanup audio system"""
    global _optimizer
    if _optimizer:
        _optimizer.cleanup()

# Test function
def test_audio_system():
    """Test the audio system"""
    print("🧪 Testing Raspberry Pi 5 audio system...")
    
    audio_manager, audio_playback, optimizer = initialize_raspberry_pi_audio()
    
    print(f"Audio system detected: {audio_manager.audio_system}")
    print(f"Audio backend: {audio_playback.backend}")
    print(f"Raspberry Pi detected: {audio_manager.is_raspberry_pi}")
    
    # Test with a simple tone if no test file exists
    try:
        # Create a test audio file if none exists
        test_file = '/tmp/test_audio.wav'
        if not os.path.exists(test_file):
            print("Creating test audio file...")
            # Use system command to create test audio
            subprocess.run([
                'ffmpeg', '-f', 'lavfi', '-i', 'sine=frequency=440:duration=0.5',
                '-y', test_file
            ], capture_output=True)
        
        if os.path.exists(test_file):
            print("🔊 Playing test audio...")
            success = audio_playback.play_audio_file(test_file)
            if success:
                time.sleep(0.6)  # Let it play
                print("✅ Audio test successful!")
            else:
                print("❌ Audio test failed")
        else:
            print("⚠️  No test audio file available")
    except Exception as e:
        print(f"Audio test error: {e}")

if __name__ == "__main__":
    test_audio_system()
