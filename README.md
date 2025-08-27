# Real-Time Speech Translator with Azure Speech Services

A browser-based real-time speech translator for online meetings (Zoom/GMeet) that captures meeting tab audio, streams it to a Python backend via WebSocket, uses **Azure Speech Services** for advanced speech recognition with native multilingual support, and displays real-time transcripts with automatic language detection and translation.

## 🚀 New Features (Azure Migration)

- **🌍 Native Multilingual Support**: Automatic language detection for 90+ languages
- **🔄 Real-time Translation**: Built-in translation without additional API calls
- **🎯 Auto Language Detection**: Azure automatically identifies spoken language
- **⚡ Lower Latency**: Improved performance with Azure's optimized models
- **💰 Cost Efficient**: Better pricing for high-volume usage
- **🔒 Enterprise Grade**: Microsoft's security and compliance standards

## Features

- **Real-time Audio Capture**: Capture audio from meeting tabs using `getDisplayMedia()`
- **Azure Speech Services**: State-of-the-art speech recognition with multilingual support
- **Live Translation**: Real-time translation with support for 90+ languages
- **Auto Language Detection**: Automatically identifies spoken language
- **Low Latency**: Partial transcripts within 100-300ms of speech
- **Modern UI**: Beautiful React interface with Tailwind CSS
- **WebSocket Streaming**: Efficient binary audio streaming for optimal performance

## Architecture

```
Browser (Frontend) ←→ FastAPI Backend ←→ Azure Speech Services
     ↓                    ↓                    ↓
Tab Audio Capture   WebSocket Server   Speech Recognition + Translation
React UI            Audio Processing   Auto Language Detection
Translation         Session Management  Real-time Streaming
```

## Tech Stack

- **Frontend**: React + TypeScript + Vite, Tailwind CSS
- **Backend**: FastAPI with uvicorn server
- **ASR**: Azure Speech Services with multilingual support
- **Audio**: Web Audio API, PCM16LE, 16kHz, Mono
- **Transport**: WebSocket with binary audio frames

## Prerequisites

- Python 3.8+
- Node.js 16+
- **Azure Speech Services** subscription (get one at [Azure Portal](https://portal.azure.com/))
- Modern browser with Web Audio API support

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd live_speech_v2
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Set your Azure Speech Services credentials:
```bash
# Windows
set AZURE_SPEECH_KEY=your_azure_key_here
set AZURE_SPEECH_REGION=centralindia

# Linux/Mac
export AZURE_SPEECH_KEY=your_azure_key_here
export AZURE_SPEECH_REGION=centralindia
```

Or create a `.env` file in the backend directory:
```bash
# Required: Azure Speech Services
AZURE_SPEECH_KEY=your_azure_speech_key_here
AZURE_SPEECH_REGION=centralindia

# Optional: Azure Translator API (for better translation quality)
AZURE_TRANSLATOR_KEY=your_azure_translator_key_here
AZURE_TRANSLATOR_LOCATION=centralindia
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Usage

1. **Open the Application**: Navigate to http://localhost:3000
2. **Select Languages**: Choose source language (Auto-detect or specific) and target language
3. **Start Capture**: Click "Start Capturing Meeting Audio"
4. **Select Tab**: Choose the meeting tab to capture audio from
5. **View Transcripts**: See real-time partial and final transcripts with translations
6. **Language Detection**: Azure automatically detects the spoken language

## Audio Specifications

- **Sample Rate**: 16kHz (Azure Speech Services optimized)
- **Frame Size**: 128ms (2048 samples = 4096 bytes)
- **Format**: PCM16LE, mono channel
- **Transport**: Binary WebSocket frames every 128ms

## Language Support

### Source Languages (Speech Recognition)
- **Auto-Detect**: Automatically identifies 90+ languages
- **Specific Languages**: English (US), Spanish, French, German, Italian, Portuguese, Hindi, Japanese, Korean, Chinese, Arabic, Russian, and more

### Target Languages (Translation)
- **English, Spanish, French, German, Italian, Portuguese**
- **Hindi, Japanese, Korean, Chinese, Arabic, Russian**
- **And many more supported by Azure Speech Services**

## Configuration

### Backend Configuration

Edit `backend/main.py`:
```python
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY", "your_key")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "centralindia")
```

Or use the configuration file:
```bash
python azure_config.py
```

### Frontend Configuration

Edit `frontend/vite.config.ts` for proxy settings:
```typescript
proxy: {
  '/ws': {
    target: 'ws://localhost:8000',
    ws: true,
  },
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
}
```

## API Endpoints

- `GET /` - Health check
- `GET /health` - API status
- `GET /azure/supported-languages` - List supported languages
- `GET /azure/sessions` - List active sessions
- `WebSocket /ws` - Real-time audio streaming and transcript delivery

## WebSocket Message Types

### Client → Server
- `session_init` - Initialize session with language pair and service type
- `ping` - Keep-alive ping

### Server → Client
- `session_confirmed` - Session ready confirmation with Azure features
- `connection_status` - Connection state update with Azure status
- `partial_transcript` - Real-time partial transcript
- `final_transcript` - Final transcript with translation and detected language
- `error` - Error message
- `ack` - Audio frame acknowledgment

## Development

### Project Structure
```
live_speech_v2/
├── backend/
│   ├── main.py              # FastAPI application with Azure Speech
│   ├── azure_config.py      # Azure Speech configuration
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── AzureLanguageSelector.tsx  # Azure-specific language selector
│   │   │   ├── AudioCapture.tsx           # Updated for Azure Speech
│   │   │   └── TranscriptDisplay.tsx      # Enhanced with Azure features
│   │   ├── types.ts         # TypeScript types with Azure support
│   │   ├── App.tsx          # Main app component
│   │   ├── main.tsx         # Entry point
│   │   └── index.css        # Tailwind CSS
│   ├── package.json         # Node.js dependencies
│   ├── vite.config.ts       # Vite configuration
│   └── tailwind.config.js   # Tailwind configuration
├── MIGRATION_GUIDE.md       # Complete migration guide
└── README.md
```

### Key Components

- **AzureLanguageSelector**: Azure-specific language selection with auto-detection
- **AudioCapture**: Handles tab audio capture and Azure Speech streaming
- **TranscriptDisplay**: Shows real-time transcripts with detected languages
- **ConnectionStatus**: Displays connection state and Azure session info

### Audio Processing Flow

1. **Capture**: `getDisplayMedia()` captures tab audio
2. **Process**: AudioContext processes audio at 16kHz
3. **Convert**: Float32 → Int16 PCM conversion
4. **Stream**: Binary frames sent via WebSocket every 128ms
5. **Azure Processing**: Backend streams to Azure Speech Services
6. **Language Detection**: Azure automatically detects spoken language
7. **Translation**: Real-time translation to target language
8. **Display**: UI shows results with language information

## Troubleshooting

### Common Issues

1. **Azure Speech Key Not Configured**
   - Set `AZURE_SPEECH_KEY` environment variable
   - Verify key is valid in Azure Portal

2. **Invalid Azure Region**
   - Use valid regions: `eastus`, `westeurope`, `southeastasia`
   - Check `azure_config.py` for supported regions

3. **Audio Format Issues**
   - Verify sample rate is 16kHz
   - Ensure mono channel output
   - Check frame size is 2048 samples (128ms)

4. **Language Detection Not Working**
   - Set source language to "auto" for auto-detection
   - Check supported languages in configuration

### Debug Mode

Enable detailed logging in backend:
```python
logging.basicConfig(level=logging.DEBUG)
```

Check browser console for frontend errors and Azure Speech messages.

## Performance Optimization

- **Audio Buffering**: 128ms frame size for optimal Azure processing
- **WebSocket Compression**: Binary audio frames for efficiency
- **React Optimization**: Efficient state management for rapid updates
- **Memory Management**: Proper cleanup of Azure Speech resources

## Security Considerations

- **API Key Protection**: Azure keys stored server-side
- **Input Validation**: All client inputs validated
- **CORS Configuration**: Configured for development (restrict in production)
- **WebSocket Security**: Session-based authentication
- **Azure Security**: Enterprise-grade security and compliance

## Production Deployment

1. **Environment Variables**: Use proper environment variable management
2. **HTTPS**: Enable HTTPS for production
3. **CORS**: Restrict origins to your domain
4. **Rate Limiting**: Implement API rate limiting
5. **Monitoring**: Add Azure Speech metrics and logging
6. **Scaling**: Consider Azure Speech scaling options

## Migration from AssemblyAI

If you're migrating from AssemblyAI, see the comprehensive [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for step-by-step instructions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check the troubleshooting section
- Review [Azure Speech Services documentation](https://docs.microsoft.com/azure/cognitive-services/speech-service/)
- Open an issue on GitHub

## Acknowledgments

- **Microsoft Azure Speech Services** for advanced speech recognition and multilingual support
- React and FastAPI communities
- Web Audio API specification

---

**🎉 Successfully migrated to Azure Speech Services with native multilingual support and real-time translation!**
