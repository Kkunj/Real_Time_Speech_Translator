#!/usr/bin/env python3
"""
Render Deployment Startup Script
===============================

This script is specifically designed for Render deployment.
It handles the PORT environment variable that Render provides
and ensures proper binding to the allocated port.
"""

import os
import uvicorn
from main import app

if __name__ == "__main__":
    # Get port from Render environment variable
    port = int(os.getenv("PORT", 8000))
    
    print(f"🚀 Starting Real-Time Speech Translator Backend for Render...")
    print(f"🌍 Host: 0.0.0.0")
    print(f"🔌 Port: {port}")
    print(f"🔗 WebSocket endpoint: ws://0.0.0.0:{port}/ws")
    print(f"🌐 HTTP endpoint: http://0.0.0.0:{port}")
    print(f"🇮🇳 Azure Region: centralindia")
    print(f"🎤 Speech Recognition: Enabled")
    print(f"🌐 Translation: Enabled")
    print("=" * 50)
    
    # Start the server with Render's port
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )
