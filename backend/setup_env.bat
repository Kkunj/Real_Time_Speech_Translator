@echo off
echo Setting up Azure Speech Services Environment Variables...

set AZURE_SPEECH_KEY=FDvH7d9gB0gvymtPv1usYEMP88pVXihmwxQf7UznLm4EAqyJKuMJJQQJ99BHACGhslBXJ3w3AAAYACOGazc3
set AZURE_SPEECH_REGION=centralindia
set AZURE_TRANSLATOR_KEY=3MmDmC1XEDdt9X2uXAS4dfO7ovNLnJOQXrykwwbBJKNO1IsDHW0UJQQJ99BHACGhslBXJ3w3AAAbACOGQBKE
set AZURE_TRANSLATOR_LOCATION=centralindia

echo Environment variables set for current session
echo.
echo You can now run: python main.py
echo To run this script again: setup_env.bat
pause
