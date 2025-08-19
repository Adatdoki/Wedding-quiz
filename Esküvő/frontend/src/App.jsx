import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { Heart, Users, Trophy, Sparkles, Clock, CheckCircle, XCircle, Shield, Target } from 'lucide-react'
import ApiService from './services/api.js'
import './App.css'

// Játék állapotok
const GAME_STATES = {
  REGISTRATION: 'registration',
  PAIRING: 'pairing', 
  PLAYING: 'playing',
  QUIZ: 'quiz',
  FINISHED: 'finished'
}

function App() {
  const [gameState, setGameState] = useState(GAME_STATES.REGISTRATION)
  const [playerName, setPlayerName] = useState('')
  const [currentPlayer, setCurrentPlayer] = useState(null)
  const [players, setPlayers] = useState([])
  const [gameData, setGameData] = useState(null)
  const [voteNumber, setVoteNumber] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [quizQuestion, setQuizQuestion] = useState('')
  const [roundResult, setRoundResult] = useState(null)

  const apiService = new ApiService()

  // Játékosok és játék állapot frissítése
  const refreshGameState = async () => {
    try {
      const gameResponse = await apiService.getGameState()
      
      if (gameResponse && gameResponse.success) {
        setPlayers(gameResponse.players || [])
        setGameData(gameResponse.game)
      }
    } catch (error) {
      console.error('Játék állapot frissítés hiba:', error)
    }
  }

  // Regisztráció
  const handleRegister = async () => {
    if (!playerName.trim()) {
      setError('Add meg a neved!')
      return
    }
    
    setLoading(true)
    setError('')
    
    try {
      const response = await apiService.register(playerName.trim())
      
      if (response.success) {
        setCurrentPlayer(response.player)
        setSuccess(`Sikeres regisztráció! Beceneved: ${response.player.nickname}`)
        setGameState(GAME_STATES.PAIRING)
        await refreshGameState()
      } else {
        setError(response.message || 'Regisztráció sikertelen')
      }
    } catch (error) {
      setError('Regisztráció sikertelen: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  // Partner választás
  const handleSelectPartner = async (partnerId) => {
    if (!currentPlayer) return
    
    setLoading(true)
    try {
      const response = await apiService.selectPartner(currentPlayer.id, partnerId)
      
      if (response.success) {
        setSuccess('Partner kiválasztva!')
        await refreshGameState()
      } else {
        setError(response.message || 'Partner választás sikertelen')
      }
    } catch (error) {
      setError('Partner választás hiba: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  // Szavazás
  const handleVote = async () => {
    if (!currentPlayer || !voteNumber) return
    
    const number = parseInt(voteNumber)
    if (isNaN(number) || number < 1 || number > 25) {
      setError('Adj meg egy számot 1 és 25 között!')
      return
    }
    
    setLoading(true)
    try {
      const response = await apiService.submitVote(currentPlayer.id, number)
      
      if (response.success) {
        setSuccess(`Szavazat leadva: ${number}`)
        setVoteNumber('')
        await refreshGameState()
      } else {
        setError(response.message || 'Szavazás sikertelen')
      }
    } catch (error) {
      setError('Szavazás hiba: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  // Automatikus frissítés
  useEffect(() => {
    const interval = setInterval(refreshGameState, 3000)
    return () => clearInterval(interval)
  }, [currentPlayer])

  // Hibaüzenet automatikus eltűntetése
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(''), 5000)
      return () => clearTimeout(timer)
    }
  }, [error])

  // Siker üzenet automatikus eltűntetése
  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(''), 3000)
      return () => clearTimeout(timer)
    }
  }, [success])

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-100 via-purple-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto">
        <Card className="w-full max-w-md mx-auto">
          <CardHeader className="text-center">
            <div className="mx-auto w-16 h-16 bg-gradient-to-r from-pink-500 to-purple-600 rounded-full flex items-center justify-center mb-4">
              <Heart className="w-8 h-8 text-white" />
            </div>
            <CardTitle className="text-2xl font-bold bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
              Esküvői Kvíz
            </CardTitle>
            <p className="text-gray-600">Vidám csapatverseny</p>
          </CardHeader>
          
          <CardContent className="space-y-4">
            {/* Hibaüzenetek */}
            {error && (
              <Alert className="border-red-200 bg-red-50">
                <XCircle className="h-4 w-4 text-red-600" />
                <AlertDescription className="text-red-800">
                  {error}
                </AlertDescription>
              </Alert>
            )}
            
            {/* Siker üzenetek */}
            {success && (
              <Alert className="border-green-200 bg-green-50">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-800">
                  {success}
                </AlertDescription>
              </Alert>
            )}

            {/* Regisztráció */}
            {gameState === GAME_STATES.REGISTRATION && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Add meg a neved:
                  </label>
                  <Input
                    type="text"
                    placeholder="pl. Péter"
                    value={playerName}
                    onChange={(e) => setPlayerName(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleRegister()}
                    className="w-full"
                  />
                </div>
                
                <Button 
                  onClick={handleRegister}
                  disabled={loading || !playerName.trim()}
                  className="w-full bg-gradient-to-r from-pink-500 to-purple-600 hover:from-pink-600 hover:to-purple-700"
                >
                  {loading ? (
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      Csatlakozás...
                    </div>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 mr-2" />
                      Csatlakozom a játékhoz!
                    </>
                  )}
                </Button>
                
                <div className="text-center text-sm text-gray-500">
                  <Users className="w-4 h-4 inline mr-1" />
                  {players.length} játékos csatlakozott
                </div>
              </div>
            )}

            {/* Partner választás */}
            {gameState === GAME_STATES.PAIRING && (
              <div className="space-y-4">
                <div className="text-center">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">
                    Válassz partnert!
                  </h3>
                  <p className="text-sm text-gray-600">
                    Kattints egy másik játékosra, hogy csapatot alkossatok
                  </p>
                </div>
                
                <div className="grid gap-2 max-h-60 overflow-y-auto">
                  {players
                    .filter(player => player.id !== currentPlayer?.id && !player.team_id)
                    .map(player => (
                      <Button
                        key={player.id}
                        variant="outline"
                        onClick={() => handleSelectPartner(player.id)}
                        disabled={loading}
                        className="justify-start hover:bg-pink-50 hover:border-pink-300"
                      >
                        <Users className="w-4 h-4 mr-2" />
                        {player.name} ({player.nickname})
                      </Button>
                    ))}
                </div>
                
                {players.filter(p => p.id !== currentPlayer?.id && !p.team_id).length === 0 && (
                  <div className="text-center text-gray-500 py-4">
                    <Users className="w-8 h-8 mx-auto mb-2 opacity-50" />
                    <p>Nincs elérhető partner</p>
                    <p className="text-sm">Várj, amíg más játékosok is csatlakoznak</p>
                  </div>
                )}
              </div>
            )}

            {/* Játék */}
            {gameState === GAME_STATES.PLAYING && (
              <div className="space-y-4">
                <div className="text-center">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">
                    Szavazás
                  </h3>
                  <p className="text-sm text-gray-600">
                    Válassz egy számot 1 és 25 között
                  </p>
                </div>
                
                <div className="space-y-3">
                  <Input
                    type="number"
                    min="1"
                    max="25"
                    placeholder="Szám (1-25)"
                    value={voteNumber}
                    onChange={(e) => setVoteNumber(e.target.value)}
                    className="text-center text-lg"
                  />
                  
                  <Button 
                    onClick={handleVote}
                    disabled={loading || !voteNumber}
                    className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
                  >
                    {loading ? (
                      <div className="flex items-center gap-2">
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        Szavazás...
                      </div>
                    ) : (
                      <>
                        <Target className="w-4 h-4 mr-2" />
                        Szavazok!
                      </>
                    )}
                  </Button>
                </div>
              </div>
            )}

            {/* Várakozás */}
            {(gameState === GAME_STATES.QUIZ || gameState === GAME_STATES.FINISHED) && (
              <div className="text-center py-8">
                <Trophy className="w-12 h-12 mx-auto mb-4 text-yellow-500" />
                <h3 className="text-lg font-semibold text-gray-800 mb-2">
                  Játék folyamatban...
                </h3>
                <p className="text-sm text-gray-600">
                  Várj a következő körre vagy az eredményekre
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default App

