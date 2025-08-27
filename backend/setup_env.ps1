# Azure Speech Services Environment Setup Script
Write-Host "Setting up Azure Speech Services Environment Variables..." -ForegroundColor Green

# Set environment variables for current session
$env:AZURE_SPEECH_KEY = "FDvH7d9gB0gvymtPv1usYEMP88pVXihmwxQf7UznLm4EAqyJKuMJJQQJ99BHACGhslBXJ3w3AAAYACOGazc3"
$env:AZURE_SPEECH_REGION = "centralindia"
$env:AZURE_TRANSLATOR_KEY = "3MmDmC1XEDdt9X2uXAS4dfO7ovNLnJOQXrykwwbBJKNO1IsDHW0UJQQJ99BHACGhslBXJ3w3AAAbACOGQBKE"
$env:AZURE_TRANSLATOR_LOCATION = "centralindia"

# Create .env file content
$envContent = "AZURE_SPEECH_KEY=FDvH7d9gB0gvymtPv1usYEMP88pVXihmwxQf7UznLm4EAqyJKuMJJQQJ99BHACGhslBXJ3w3AAAYACOGazc3`nAZURE_SPEECH_REGION=centralindia`nAZURE_TRANSLATOR_KEY=3MmDmC1XEDdt9X2uXAS4dfO7ovNLnJOQXrykwwbBJKNO1IsDHW0UJQQJ99BHACGhslBXJ3w3AAAbACOGQBKE`nAZURE_TRANSLATOR_LOCATION=centralindia`nHOST=0.0.0.0`nPORT=8000"

# Write to .env file
$envContent | Out-File -FilePath ".env" -Encoding UTF8 -Force

Write-Host "Environment variables set for current session" -ForegroundColor Green
Write-Host ".env file created/updated" -ForegroundColor Green
Write-Host ""
Write-Host "Verifying environment variables..." -ForegroundColor Yellow

# Verify the variables
Write-Host "AZURE_SPEECH_KEY: $($env:AZURE_SPEECH_KEY.Substring(0,10))..." -ForegroundColor Cyan
Write-Host "AZURE_SPEECH_REGION: $env:AZURE_SPEECH_REGION" -ForegroundColor Cyan
Write-Host "AZURE_TRANSLATOR_KEY: $($env:AZURE_TRANSLATOR_KEY.Substring(0,10))..." -ForegroundColor Cyan
Write-Host "AZURE_TRANSLATOR_LOCATION: $env:AZURE_TRANSLATOR_LOCATION" -ForegroundColor Cyan

Write-Host ""
Write-Host "You can now run: python main.py" -ForegroundColor Green
Write-Host "To run this script again: .\setup_env.ps1" -ForegroundColor Yellow
