"""
Central India Azure Speech Services Setup
========================================

This script helps you set up Azure Speech Services for Central India region.
Run this script to configure your environment variables.
"""

import os
import sys

def setup_central_india():
    """Setup Central India Azure Speech Services configuration"""
    
    print("🌍 Central India Azure Speech Services Setup")
    print("=" * 50)
    print()
    
    # Check current configuration
    current_key = os.getenv("AZURE_SPEECH_KEY", "NOT_SET")
    current_region = os.getenv("AZURE_SPEECH_REGION", "NOT_SET")
    
    print("Current Configuration:")
    print(f"  AZURE_SPEECH_KEY: {'*' * 10 + current_key[-4:] if current_key != 'NOT_SET' else 'NOT_SET'}")
    print(f"  AZURE_SPEECH_REGION: {current_region}")
    print()
    
    # Instructions
    print("📋 Setup Instructions:")
    print("1. Go to Azure Portal: https://portal.azure.com/")
    print("2. Create a new Speech Services resource")
    print("3. Choose 'Central India' as the region")
    print("4. Go to 'Keys and Endpoint' section")
    print("5. Copy 'Key 1'")
    print()
    
    # Get user input
    print("🔑 Enter your Azure Speech Services key (or press Enter to skip):")
    user_key = input("Key: ").strip()
    
    if user_key:
        # Set environment variable for current session
        os.environ["AZURE_SPEECH_KEY"] = user_key
        os.environ["AZURE_SPEECH_REGION"] = "centralindia"
        
        print()
        print("✅ Environment variables set for current session!")
        print(f"  AZURE_SPEECH_KEY: {'*' * 10 + user_key[-4:]}")
        print(f"  AZURE_SPEECH_REGION: centralindia")
        print()
        
        # Create .env file
        env_content = f"""# Central India Azure Speech Services Configuration
AZURE_SPEECH_KEY={user_key}
AZURE_SPEECH_REGION=centralindia

# Central India endpoint: https://centralindia.api.cognitive.microsoft.com/
# This provides optimal performance for users in India
"""
        
        try:
            with open(".env", "w") as f:
                f.write(env_content)
            print("📁 Created .env file with your configuration")
        except Exception as e:
            print(f"⚠️  Could not create .env file: {e}")
            print("   Please create it manually with the content above")
        
        print()
        print("🚀 You're ready to use Central India Azure Speech Services!")
        print("   Run 'python main.py' to start the backend")
        
    else:
        print()
        print("⚠️  No key provided. Please set the environment variables manually:")
        print("   Windows: set AZURE_SPEECH_KEY=your_key_here")
        print("   Linux/Mac: export AZURE_SPEECH_KEY=your_key_here")
        print("   Or create a .env file with:")
        print("   AZURE_SPEECH_KEY=your_key_here")
        print("   AZURE_SPEECH_REGION=centralindia")

def test_connection():
    """Test Azure Speech Services connection"""
    print()
    print("🧪 Testing Azure Speech Services Connection...")
    
    try:
        import azure.cognitiveservices.speech as speechsdk
        
        key = os.getenv("AZURE_SPEECH_KEY")
        region = os.getenv("AZURE_SPEECH_REGION")
        
        if not key or key == "NOT_SET":
            print("❌ AZURE_SPEECH_KEY not configured")
            return False
        
        if region != "centralindia":
            print("❌ AZURE_SPEECH_REGION not set to 'centralindia'")
            return False
        
        # Test configuration
        speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
        print("✅ Azure Speech SDK imported successfully")
        print("✅ Speech configuration created successfully")
        print(f"✅ Region: {region}")
        print(f"✅ Key: {'*' * 10 + key[-4:]}")
        
        return True
        
    except ImportError:
        print("❌ Azure Speech SDK not installed. Run: pip install azure-cognitiveservices-speech")
        return False
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

if __name__ == "__main__":
    setup_central_india()
    
    if input("\n🧪 Test connection? (y/n): ").lower() == 'y':
        test_connection()
    
    print("\n📚 For more information, see:")
    print("   - MIGRATION_GUIDE.md")
    print("   - README.md")
    print("   - centralindia_config.py")
