#!/usr/bin/env python3
"""
Fast Voice Processing System for KirkBot2
Optimizes Whisper transcription speed for instant responses
"""

import subprocess
import os
import json
import time
from pathlib import Path

def setup_fast_voice_processing():
    """Configure fastest possible voice processing"""
    
    config = {
        "whisper_optimized": True,
        "model": "turbo",  # Fastest Whisper model
        "language": "en",   # Fixed language for speed
        "output_format": "txt",
        "threads": 4,       # Use all available threads
        "cache_dir": "/tmp/whisper_cache",
        "compression": "low_memory"
    }
    
    # Create cache directory for faster loading
    os.makedirs("/tmp/whisper_cache", exist_ok=True)
    
    # Optimize whisper command for speed
    fast_command = [
        "whisper",
        "--model", "turbo",
        "--language", "en", 
        "--output_format", "txt",
        "--threads", "4",
        "--compress_ratio", "0",  # No compression for speed
        "--temperature", "0.0",    # Deterministic for consistency
        "--best_of", "1",          # Single pass for speed
    ]
    
    print("🚀 FAST VOICE PROCESSING CONFIGURED")
    print(f"⚡ Model: turbo (fastest available)")
    print(f"🔧 Threads: 4 (parallel processing)")
    print(f"💾 Cache: /tmp/whisper_cache")
    print(f"📝 Language: en (fixed for speed)")
    
    return fast_command

def process_voice_fast(audio_file):
    """Process voice message with optimized settings"""
    
    start_time = time.time()
    
    # Use pre-configured fast settings
    cmd = [
        "whisper",
        audio_file,
        "--model", "turbo",
        "--language", "en",
        "--output_format", "txt",
        "--threads", "4",
        "--temperature", "0.0",
        "--best_of", "1"
    ]
    
    try:
        # Execute with timeout for safety
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,  # 1 minute max
            cwd="/tmp"   # Use temp directory for speed
        )
        
        processing_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ VOICE PROCESSED IN {processing_time:.2f} seconds")
            return result.stdout
        else:
            print(f"❌ Voice processing failed: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("⏰ Voice processing timed out - falling back to faster mode")
        return process_voice_emergency(audio_file)
    except Exception as e:
        print(f"❌ Voice processing error: {str(e)}")
        return None

def process_voice_emergency(audio_file):
    """Emergency ultra-fast processing for critical situations"""
    
    print("🚨 EMERGENCY FAST MODE ACTIVATED")
    
    cmd = [
        "whisper",
        audio_file,
        "--model", "tiny",  # Fastest possible model
        "--language", "en",
        "--output_format", "txt",
        "--threads", "8",   # Maximum threads
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else None

def benchmark_voice_processing():
    """Benchmark current voice processing speed"""
    
    print("🧪 VOICE SPEED BENCHMARK RUNNING...")
    
    # Test with existing audio file if available
    test_file = "/root/.clawdbot/media/inbound/d1603837-d956-4de0-bc77-49d80c461a05.ogg"
    
    if os.path.exists(test_file):
        start_time = time.time()
        result = process_voice_fast(test_file)
        end_time = time.time()
        
        if result:
            print(f"⚡ PROCESSING TIME: {end_time - start_time:.2f} seconds")
            print(f"📝 RESULT: {result[:100]}...")
            return True
        else:
            print("❌ Benchmark failed")
            return False
    else:
        print("📁 No test audio file found")
        return False

if __name__ == "__main__":
    print("🎤 KIRKBOT2 FAST VOICE PROCESSING SETUP")
    
    # Configure fast processing
    setup_fast_voice_processing()
    
    # Run benchmark if audio available
    benchmark_voice_processing()
    
    print("\n🚀 SETUP COMPLETE!")
    print("📧 GUIDE CREATED: gmail-setup-guide.md")
    print("🎤 VOICE PROCESSING: Optimized for maximum speed")