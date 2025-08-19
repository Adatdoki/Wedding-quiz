import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Badge } from './ui/badge'
import { Heart, Trophy, Users, Target, ArrowRight, Sparkles } from 'lucide-react'
import ApiService from '../services/api'

const SupporterScreen = ({ currentPlayer, gameState, onUpdate }) => {
  const [supporterTokens, setSupporterTokens] = useState([])
  const [prediction, setPrediction] = useState({
    number: '',
    teamId: ''
  })
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  // Szurkolói tokenek betöltése
  useEffect(() => {
    loadSupporterTokens()
  }, [])

  const loadSupporterTokens = async () => {
    try {
      const response = await ApiService.getSupporterTokens()
      setSupporterTokens(response.tokens || [])
    } catch (error) {
      console.error('Szurkolói tokenek betöltése hiba:', error)
    }
  }

  // Aktuális játékos token-je
  const playerToken = supporterTokens.find(token => 
    token.player_id === currentPlayer?.id && token.is_active
  )

  // Tipp leadása
  const handleSubmitPrediction = async () => {
    if (!prediction.number || !prediction.teamId || !playerToken) {
      setMessage('Kérlek válassz számot és csapatot!')
      return
    }

    setLoading(true)
    try {
      const response = await ApiService.submitPrediction(
        currentPlayer.id,
        prediction.number,
        prediction.teamId
      )
      
      setMessage(response.message)
      loadSupporterTokens()
      onUpdate?.()
    } catch (error) {
      setMessage('Hiba történt a tipp leadásakor: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  // Visszatérés a játékba
  const handleRejoinGame = async () => {
    if (!playerToken || !playerToken.is_prediction_correct) {
      return
    }

    setLoading(true)
    try {
      const response = await ApiService.rejoinGame(playerToken.id)
      setMessage(response.message)
      onUpdate?.()
    } catch (error) {
      setMessage('Hiba történt a visszatéréskor: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  if (!currentPlayer) {
    return (
      <Card className="w-full max-w-md mx-auto">
        <CardContent className="p-6 text-center">
          <Heart className="w-12 h-12 mx-auto mb-4 text-pink-500" />
          <p className="text-gray-600">Jelentkezz be a szurkoláshoz!</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      {/* Szurkolói státusz */}
      <Card className="bg-gradient-to-r from-purple-500 to-pink-500 text-white">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="w-6 h-6" />
            Szurkolói Mód
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-lg font-semibold">{currentPlayer.name}</p>
              <p className="text-purple-100">({currentPlayer.nickname})</p>
            </div>
            <Badge variant="secondary" className="bg-white/20 text-white">
              <Sparkles className="w-4 h-4 mr-1" />
              Szurkoló
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Token státusz */}
      {playerToken ? (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="w-5 h-5 text-blue-500" />
              Szurkolói Token
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {playerToken.predicted_number && playerToken.predicted_team_id ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                  <span className="text-sm text-gray-600">Tippelt szám:</span>
                  <Badge variant="outline" className="text-blue-600">
                    {playerToken.predicted_number}
                  </Badge>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                  <span className="text-sm text-gray-600">Tippelt csapat:</span>
                  <Badge variant="outline" className="text-green-600">
                    {playerToken.predicted_team?.name || 'Ismeretlen'}
                  </Badge>
                </div>

                {playerToken.is_prediction_correct === true && (
                  <div className="p-4 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <Trophy className="w-5 h-5" />
                      <span className="font-semibold">Helyes tipp! 🎉</span>
                    </div>
                    <p className="text-sm text-green-100 mb-3">
                      Eltaláltad a nyerő csapatot! Visszatérhetsz a játékba.
                    </p>
                    <Button 
                      onClick={handleRejoinGame}
                      disabled={loading}
                      className="w-full bg-white text-green-600 hover:bg-green-50"
                    >
                      <ArrowRight className="w-4 h-4 mr-2" />
                      Visszatérés a játékba
                    </Button>
                  </div>
                )}

                {playerToken.is_prediction_correct === false && (
                  <div className="p-3 bg-red-50 text-red-700 rounded-lg text-center">
                    <span className="text-sm">Sajnos nem találtad el. Próbáld újra a következő körben!</span>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                <p className="text-gray-600 text-center">
                  Tippelj a következő kör nyertesére és visszatérhetsz a játékba!
                </p>

                {/* Szám választás */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">
                    Tippelt szám (1-100):
                  </label>
                  <Input
                    type="number"
                    min="1"
                    max="100"
                    value={prediction.number}
                    onChange={(e) => setPrediction(prev => ({
                      ...prev,
                      number: e.target.value
                    }))}
                    placeholder="pl. 42"
                  />
                </div>

                {/* Csapat választás */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-700">
                    Tippelt nyerő csapat:
                  </label>
                  <div className="grid grid-cols-1 gap-2">
                    {gameState?.teams?.map(team => (
                      <Button
                        key={team.id}
                        variant={prediction.teamId === team.id ? "default" : "outline"}
                        onClick={() => setPrediction(prev => ({
                          ...prev,
                          teamId: team.id
                        }))}
                        className="justify-start"
                      >
                        <Users className="w-4 h-4 mr-2" />
                        {team.name} ({team.member_count} fő)
                      </Button>
                    ))}
                  </div>
                </div>

                <Button 
                  onClick={handleSubmitPrediction}
                  disabled={loading || !prediction.number || !prediction.teamId}
                  className="w-full"
                >
                  <Target className="w-4 h-4 mr-2" />
                  Tipp leadása
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-6 text-center">
            <Heart className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p className="text-gray-600">
              Jelenleg nincs szurkolói token-ed. 
              Várj a következő körig, vagy amíg kiesik egy csapat!
            </p>
          </CardContent>
        </Card>
      )}

      {/* Üzenet megjelenítése */}
      {message && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="p-4">
            <p className="text-blue-800 text-center">{message}</p>
          </CardContent>
        </Card>
      )}

      {/* Játék állapot */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5 text-green-500" />
            Jelenlegi Állás
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {gameState?.teams?.map(team => (
              <div key={team.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <span className="font-medium">{team.name}</span>
                <Badge variant="outline">
                  {team.member_count} fő
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default SupporterScreen

