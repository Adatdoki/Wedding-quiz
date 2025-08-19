import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { 
  Shield, 
  Play, 
  Pause, 
  RotateCcw, 
  Coffee, 
  BarChart3, 
  Users, 
  Trophy,
  Clock,
  CheckCircle,
  XCircle,
  Key
} from 'lucide-react'
import ApiService from '../services/api.js'

const ModeratorPanel = ({ gameState, onUpdate }) => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [stats, setStats] = useState(null)
  const [secretCode, setSecretCode] = useState('')
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [drinkMessage, setDrinkMessage] = useState('Ital szünet! 🍻')
  const [selectedPlayer, setSelectedPlayer] = useState('')
  const [selectedTeam, setSelectedTeam] = useState('')

  // Statisztikák frissítése
  const refreshStats = async () => {
    try {
      const response = await ApiService.getModeratorStats()
      if (response.success) {
        setStats(response.stats)
      }
    } catch (error) {
      console.error('Statisztikák frissítése sikertelen:', error)
    }
  }

  // Automatikus frissítés
  useEffect(() => {
    if (isAuthenticated) {
      refreshStats()
      const interval = setInterval(refreshStats, 3000)
      return () => clearInterval(interval)
    }
  }, [isAuthenticated])

  // Moderátor autentikáció
  const handleAuthentication = async () => {
    if (!secretCode.trim()) return
    
    setLoading(true)
    setError('')
    
    try {
      const response = await ApiService.authenticateModerator(secretCode)
      if (response.success) {
        setIsAuthenticated(true)
        setSuccess('Moderátor hozzáférés engedélyezve! 🔓')
        setSecretCode('')
      }
    } catch (error) {
      setError('Hibás titkos kód: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  // Kör indítása
  const handleStartRound = async () => {
    setLoading(true)
    setError('')
    
    try {
      const response = await ApiService.startRound()
      if (response.success) {
        setSuccess(response.message)
        await onUpdate()
        await refreshStats()
      }
    } catch (error) {
      setError('Kör indítása sikertelen: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  // Játék szüneteltetése
  const handlePauseGame = async () => {
    setLoading(true)
    setError('')
    
    try {
      const response = await ApiService.pauseGame()
      if (response.success) {
        setSuccess(response.message)
        await onUpdate()
        await refreshStats()
      }
    } catch (error) {
      setError('Játék szüneteltetése sikertelen: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  // Ital szünet
  const handleDrinkBreak = async () => {
    setLoading(true)
    setError('')
    
    try {
      const response = await ApiService.announceDrinkBreak(drinkMessage)
      if (response.success) {
        setSuccess(response.message)
      }
    } catch (error) {
      setError('Ital szünet bejelentése sikertelen: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  // Manuális csapatváltás
  const handleManualTeamChange = async () => {
    if (!selectedPlayer || !selectedTeam) {
      setError('Játékos és csapat kiválasztása kötelező!')
      return
    }
    
    setLoading(true)
    setError('')
    
    try {
      const response = await ApiService.manualTeamChange(selectedPlayer, selectedTeam)
      if (response.success) {
        setSuccess(response.message)
        await onUpdate()
        await refreshStats()
        setSelectedPlayer('')
        setSelectedTeam('')
      }
    } catch (error) {
      setError('Csapatváltás sikertelen: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  // Játék újraindítása
  const handleResetGame = async () => {
    if (!confirm('Biztosan újraindítod a játékot? Ez törli az összes adatot!')) {
      return
    }
    
    setLoading(true)
    setError('')
    
    try {
      const response = await ApiService.resetGame()
      if (response.success) {
        setSuccess(response.message)
        await onUpdate()
        await refreshStats()
      }
    } catch (error) {
      setError('Játék újraindítása sikertelen: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  // Ha nincs autentikáció, mutassuk a bejelentkezési képernyőt
  if (!isAuthenticated) {
    return (
      <div className="max-w-md mx-auto mt-20">
        <Card className="bg-white/90 backdrop-blur-sm border-0 shadow-xl">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <div className="bg-gradient-to-r from-blue-500 to-indigo-600 p-3 rounded-full">
                <Shield className="w-8 h-8 text-white" />
              </div>
            </div>
            <CardTitle className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              Moderátor Panel
            </CardTitle>
            <p className="text-gray-600 mt-2">Titkos kód szükséges</p>
          </CardHeader>
          <CardContent className="space-y-6">
            {error && (
              <Alert className="border-red-200 bg-red-50">
                <XCircle className="h-4 w-4 text-red-600" />
                <AlertDescription className="text-red-800">{error}</AlertDescription>
              </Alert>
            )}
            
            {success && (
              <Alert className="border-green-200 bg-green-50">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-800">{success}</AlertDescription>
              </Alert>
            )}
            
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Titkos kód:</label>
              <Input
                type="password"
                placeholder="Moderátor kód"
                value={secretCode}
                onChange={(e) => setSecretCode(e.target.value)}
                className="text-center"
                onKeyPress={(e) => e.key === 'Enter' && handleAuthentication()}
                disabled={loading}
              />
            </div>
            
            <Button 
              onClick={handleAuthentication}
              className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-semibold py-3"
              disabled={!secretCode.trim() || loading}
            >
              {loading ? (
                <Clock className="w-5 h-5 mr-2 animate-spin" />
              ) : (
                <Key className="w-5 h-5 mr-2" />
              )}
              {loading ? 'Ellenőrzés...' : 'Belépés'}
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Fejléc */}
      <Card className="bg-white/90 backdrop-blur-sm border-0 shadow-xl">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-indigo-800 flex items-center">
            <Shield className="w-6 h-6 mr-2" />
            Moderátor Panel
            <Badge className="ml-4 bg-green-100 text-green-800">
              Aktív
            </Badge>
          </CardTitle>
        </CardHeader>
      </Card>

      {/* Hibaüzenetek és sikerüzenetek */}
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <XCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">{success}</AlertDescription>
        </Alert>
      )}

      {/* Statisztikák */}
      {stats && (
        <Card className="bg-white/90 backdrop-blur-sm border-0 shadow-xl">
          <CardHeader>
            <CardTitle className="text-xl font-bold text-indigo-800 flex items-center">
              <BarChart3 className="w-5 h-5 mr-2" />
              Játék Statisztikák
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <Users className="w-8 h-8 mx-auto mb-2 text-blue-600" />
                <div className="text-2xl font-bold text-blue-800">{stats.total_players}</div>
                <div className="text-sm text-blue-600">Játékos</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <Trophy className="w-8 h-8 mx-auto mb-2 text-green-600" />
                <div className="text-2xl font-bold text-green-800">{stats.active_teams}</div>
                <div className="text-sm text-green-600">Aktív Csapat</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <Clock className="w-8 h-8 mx-auto mb-2 text-purple-600" />
                <div className="text-2xl font-bold text-purple-800">{stats.current_round}</div>
                <div className="text-sm text-purple-600">Jelenlegi Kör</div>
              </div>
              <div className="text-center p-4 bg-orange-50 rounded-lg">
                <Badge className="w-8 h-8 mx-auto mb-2 text-orange-600" />
                <div className="text-2xl font-bold text-orange-800">{stats.active_tokens}</div>
                <div className="text-sm text-orange-600">Aktív Token</div>
              </div>
            </div>
            
            <div className="mt-4 flex items-center justify-center space-x-4">
              <Badge variant={stats.is_paused ? 'destructive' : 'default'}>
                {stats.is_paused ? 'Szüneteltetve' : 'Aktív'}
              </Badge>
              <Badge variant="outline">
                Állapot: {stats.game_state}
              </Badge>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Játék vezérlés */}
      <Card className="bg-white/90 backdrop-blur-sm border-0 shadow-xl">
        <CardHeader>
          <CardTitle className="text-xl font-bold text-indigo-800">
            Játék Vezérlés
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button 
              onClick={handleStartRound}
              className="bg-green-500 hover:bg-green-600 text-white"
              disabled={loading}
            >
              <Play className="w-4 h-4 mr-2" />
              Új Kör Indítása
            </Button>
            
            <Button 
              onClick={handlePauseGame}
              className="bg-yellow-500 hover:bg-yellow-600 text-white"
              disabled={loading}
            >
              <Pause className="w-4 h-4 mr-2" />
              {stats?.is_paused ? 'Folytatás' : 'Szünet'}
            </Button>
            
            <Button 
              onClick={handleResetGame}
              className="bg-red-500 hover:bg-red-600 text-white"
              disabled={loading}
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              Játék Újraindítása
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Ital szünet */}
      <Card className="bg-white/90 backdrop-blur-sm border-0 shadow-xl">
        <CardHeader>
          <CardTitle className="text-xl font-bold text-indigo-800">
            Ital Szünet Bejelentése
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-4">
            <Input
              placeholder="Ital szünet üzenet..."
              value={drinkMessage}
              onChange={(e) => setDrinkMessage(e.target.value)}
              className="flex-1"
            />
            <Button 
              onClick={handleDrinkBreak}
              className="bg-orange-500 hover:bg-orange-600 text-white"
              disabled={loading || !drinkMessage.trim()}
            >
              <Coffee className="w-4 h-4 mr-2" />
              Bejelentés
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Manuális csapatváltás */}
      {gameState?.teams && gameState.teams.length > 0 && (
        <Card className="bg-white/90 backdrop-blur-sm border-0 shadow-xl">
          <CardHeader>
            <CardTitle className="text-xl font-bold text-indigo-800">
              Manuális Csapatváltás
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <select 
                value={selectedPlayer}
                onChange={(e) => setSelectedPlayer(e.target.value)}
                className="p-2 border rounded-md"
              >
                <option value="">Válassz játékost...</option>
                {gameState.teams.flatMap(team => 
                  team.members.map(member => (
                    <option key={member.id} value={member.id}>
                      {member.name} ({team.name})
                    </option>
                  ))
                )}
              </select>
              
              <select 
                value={selectedTeam}
                onChange={(e) => setSelectedTeam(e.target.value)}
                className="p-2 border rounded-md"
              >
                <option value="">Válassz célcsapatot...</option>
                {gameState.teams.filter(team => team.is_active).map(team => (
                  <option key={team.id} value={team.id}>
                    {team.name} ({team.member_count} fő)
                  </option>
                ))}
              </select>
              
              <Button 
                onClick={handleManualTeamChange}
                className="bg-purple-500 hover:bg-purple-600 text-white"
                disabled={loading || !selectedPlayer || !selectedTeam}
              >
                <Users className="w-4 h-4 mr-2" />
                Áthelyezés
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default ModeratorPanel

