import { useState } from 'react'
import AudioCapture from './components/AudioCapture'
import TranscriptDisplay from './components/TranscriptDisplay'
import ConnectionStatus from './components/ConnectionStatus'
import AzureLanguageSelector from './components/AzureLanguageSelector'
import { TranscriptEntry, ConnectionState, LanguagePair } from './types'
import { Mic, Wifi, Globe, Play } from 'lucide-react'

function App() {
  const [connectionState, setConnectionState] = useState<ConnectionState>('disconnected')
  const [transcripts, setTranscripts] = useState<TranscriptEntry[]>([])
  const [languagePair, setLanguagePair] = useState<LanguagePair>({ source: 'auto', target: 'en' })
  const [sessionId, setSessionId] = useState<string>('')

  const handleTranscriptUpdate = (entry: TranscriptEntry) => {
    setTranscripts(prev => [...prev, entry])
  }

  const handleConnectionChange = (state: ConnectionState) => {
    setConnectionState(state)
  }

  const handleLanguageChange = (pair: LanguagePair) => {
    setLanguagePair(pair)
  }

  const handleSessionStart = (id: string) => {
    setSessionId(id)
    setTranscripts([])
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-6 py-10">
        <header className="text-center mb-10">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Real-Time Speech Translator
          </h1>
          <p className="text-xl text-gray-600">
            Capture meeting audio and get real-time translations powered by Azure Speech Services
          </p>
        </header>

        {/* Quick Start Guide */}
        <div className="mb-10 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl shadow-lg">
          <h2 className="text-2xl font-bold text-blue-900 mb-4 text-center">
            🚀 Quick Start Guide - Live Transcript
          </h2>
          
          {/* WebRTC Requirement Notice */}
          <div className="mb-6 p-4 bg-amber-100 border-2 border-amber-300 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-amber-500 rounded-full flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white">
                  <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path>
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                  <line x1="12" x2="12" y1="19" y2="22"></line>
                </svg>
              </div>
              <div>
                <h3 className="font-semibold text-amber-900 text-lg">⚠️ Important: Enable WebRTC in Chrome</h3>
                <p className="text-amber-800 text-sm">
                  Before using this app, you <strong>must enable WebRTC</strong> in your Chrome browser and allow microphone access for speech recognition.
                </p>
                <div className="mt-2 text-xs text-amber-700">
                  <strong>How to enable:</strong> Go to <code className="bg-amber-200 px-1 rounded">chrome://settings/content/microphone</code> and ensure microphone access is allowed for this site and visit <code className="bg-amber-200 px-1 rounded">chrome://flags/</code> for WebRTC.
                </div>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center p-4 bg-white rounded-lg border border-blue-200">
              <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-3">
                <Wifi className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold text-blue-900 mb-2">Step 1: Connect</h3>
              <p className="text-sm text-blue-700">
                Click "Connect WebSocket" to establish connection with the backend
              </p>
            </div>

            <div className="text-center p-4 bg-white rounded-lg border border-blue-200">
              <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-3">
                <Globe className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold text-green-900 mb-2">Step 2: Set Languages</h3>
              <p className="text-sm text-green-700">
                Choose source language (what you'll speak) and target language (translation)
              </p>
            </div>

            <div className="text-center p-4 bg-white rounded-lg border border-blue-200">
              <div className="w-12 h-12 bg-purple-500 rounded-full flex items-center justify-center mx-auto mb-3">
                <Mic className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold text-purple-900 mb-2">Step 3: Start Capture</h3>
              <p className="text-sm text-purple-700">
                Click "Start Capturing Meeting Audio" to begin speech recognition
              </p>
            </div>

            <div className="text-center p-4 bg-white rounded-lg border border-blue-200">
              <div className="w-12 h-12 bg-orange-500 rounded-full flex items-center justify-center mx-auto mb-3">
                <Play className="w-6 h-6 text-white" />
              </div>
              <h3 className="font-semibold text-orange-900 mb-2">Step 4: Speak & Watch</h3>
              <p className="text-sm text-orange-700">
                Speak naturally and watch real-time transcripts appear in both languages
              </p>
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-blue-100 rounded-lg border border-blue-300">
            <h4 className="font-semibold text-blue-900 mb-2">💡 Pro Tips:</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• <strong>Auto-detect</strong> supports 4 languages: English, Hindi, Spanish, French</li>
              <li>• <strong>Target language</strong> can be any of 23+ Indian languages or international languages</li>
              <li>• <strong>Real-time updates</strong> show both original speech and translation simultaneously</li>
              <li>• <strong>Central India optimized</strong> for best performance with Indian languages</li>
            </ul>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
          {/* Left Column - Controls */}
          <div className="space-y-8">
            <div className="card">
              <h2 className="text-2xl font-semibold mb-6">Connection</h2>
              <ConnectionStatus 
                state={connectionState} 
                sessionId={sessionId}
              />
            </div>

            <div className="card">
              <h2 className="text-2xl font-semibold mb-6">Language Settings</h2>
              <AzureLanguageSelector 
                value={languagePair}
                onChange={handleLanguageChange}
                disabled={connectionState === 'connected'}
              />
            </div>

            <div className="card">
              <h2 className="text-2xl font-semibold mb-6">Audio Capture</h2>
              <AudioCapture 
                onConnectionChange={handleConnectionChange}
                onTranscriptUpdate={handleTranscriptUpdate}
                onSessionStart={handleSessionStart}
                languagePair={languagePair}
                connectionState={connectionState}
              />
            </div>
          </div>

          {/* Right Column - Transcripts */}
          <div className="lg:col-span-2">
            <div className="card h-full">
              <h2 className="text-2xl font-semibold mb-6">Live Transcripts</h2>
              <TranscriptDisplay 
                transcripts={transcripts}
                connectionState={connectionState}
                languagePair={languagePair}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
