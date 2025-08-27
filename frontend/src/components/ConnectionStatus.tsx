import React from 'react'
import { Wifi, WifiOff, AlertCircle, Loader2 } from 'lucide-react'
import { ConnectionState } from '../types'

interface ConnectionStatusProps {
  state: ConnectionState
  sessionId?: string
}

const ConnectionStatus: React.FC<ConnectionStatusProps> = ({
  state,
  sessionId
}) => {
  const getStatusIcon = () => {
    switch (state) {
      case 'connected':
        return <Wifi className="w-6 h-6 text-green-600" />
      case 'connecting':
        return <Loader2 className="w-6 h-6 text-yellow-600 animate-spin" />
      case 'error':
        return <AlertCircle className="w-6 h-6 text-red-600" />
      default:
        return <WifiOff className="w-6 h-6 text-gray-500" />
    }
  }

  const getStatusText = () => {
    switch (state) {
      case 'connected':
        return 'Connected to Backend'
      case 'connecting':
        return 'Connecting...'
      case 'error':
        return 'Connection Error'
      default:
        return 'Disconnected'
    }
  }

  const getStatusColor = () => {
    switch (state) {
      case 'connected':
        return 'text-green-600'
      case 'connecting':
        return 'text-yellow-600'
      case 'error':
        return 'text-red-600'
      default:
        return 'text-gray-500'
    }
  }

  const getStatusBgColor = () => {
    switch (state) {
      case 'connected':
        return 'bg-green-50 border-green-200'
      case 'connecting':
        return 'bg-yellow-50 border-yellow-200'
      case 'error':
        return 'bg-red-50 border-red-200'
      default:
        return 'bg-gray-50 border-gray-200'
    }
  }

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      <div className={`p-5 border-2 rounded-lg ${getStatusBgColor()}`}>
        <div className="flex items-center space-x-4">
          {getStatusIcon()}
          <div>
            <h3 className={`text-lg font-semibold ${getStatusColor()}`}>
              {getStatusText()}
            </h3>
            <p className="text-base text-gray-600 mt-1">
              {state === 'connected' ? 'Ready to capture audio' : 
               state === 'connecting' ? 'Establishing connection...' :
               state === 'error' ? 'Please check your connection' :
               'Start a session to connect'}
            </p>
          </div>
        </div>
      </div>

      {/* Session Information */}
      {sessionId && (
        <div className="p-5 bg-gray-50 border-2 border-gray-200 rounded-lg">
          <h4 className="text-base font-semibold text-gray-700 mb-3">Session Information</h4>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 font-medium">Session ID:</span>
              <span className="text-sm font-mono text-gray-700 bg-gray-100 px-3 py-2 rounded">
                {sessionId.slice(-8)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 font-medium">Status:</span>
              <span className={`text-sm font-semibold ${getStatusColor()}`}>
                {state === 'connected' ? 'Active' : 
                 state === 'connecting' ? 'Connecting' :
                 state === 'error' ? 'Failed' : 'Inactive'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Connection Status Indicator */}
      {state === 'connected' && (
        <div className="p-4 bg-green-50 border-2 border-green-200 rounded-lg">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-base text-green-700 font-semibold">✓ All systems operational</span>
          </div>
        </div>
      )}
    </div>
  )
}

export default ConnectionStatus
