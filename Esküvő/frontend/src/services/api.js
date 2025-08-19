// API szolgáltatás a backend kommunikációhoz

const API_BASE_URL = 'https://9yhyi3c870vy.manus.space/api'

class ApiService {
  // Játékos regisztráció
  async register(name) {
    try {
      const response = await fetch(`${API_BASE_URL}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Regisztráció hiba:', error)
      throw error
    }
  }

  // Játék állapot lekérése
  async getGameState() {
    try {
      const response = await fetch(`${API_BASE_URL}/game/state`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Játék állapot hiba:', error)
      throw error
    }
  }

  // Partner választás
  async selectPartner(playerId, partnerId) {
    try {
      const response = await fetch(`${API_BASE_URL}/select-partner`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          player_id: playerId,
          partner_id: partnerId
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Partner választás hiba:', error)
      throw error
    }
  }

  // Szavazás
  async vote(teamId, number) {
    try {
      const response = await fetch(`${API_BASE_URL}/vote`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          team_id: teamId,
          number: number
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Szavazás hiba:', error)
      throw error
    }
  }

  // Kvíz válasz
  async submitQuizAnswer(teamId, answer) {
    try {
      const response = await fetch(`${API_BASE_URL}/quiz-answer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          team_id: teamId,
          answer: answer
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Kvíz válasz hiba:', error)
      throw error
    }
  }

  // Játékos rablás
  async stealPlayer(winnerTeamId, targetPlayerId) {
    try {
      const response = await fetch(`${API_BASE_URL}/steal-player`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          winner_team_id: winnerTeamId,
          target_player_id: targetPlayerId
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Játékos rablás hiba:', error)
      throw error
    }
  }

  // Új kör indítása
  async startNewRound() {
    try {
      const response = await fetch(`${API_BASE_URL}/start-round`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Új kör indítás hiba:', error)
      throw error
    }
  }

  // Új szavazási API
  async submitVote(playerId, number) {
    try {
      const response = await fetch(`${API_BASE_URL}/vote/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          player_id: playerId,
          number: number
        })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Szavazat leadás hiba:', error)
      throw error
    }
  }

  // Csapat szavazási állapot
  async getTeamVotingStatus(teamId) {
    try {
      const response = await fetch(`${API_BASE_URL}/vote/team-status/${teamId}`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Csapat szavazási állapot hiba:', error)
      throw error
    }
  }

  // Kör szavazási állapot
  async getRoundVotingStatus() {
    try {
      const response = await fetch(`${API_BASE_URL}/vote/round-status`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Kör szavazási állapot hiba:', error)
      throw error
    }
  }

  // Szavazás lezárása
  async finalizeVoting() {
    try {
      const response = await fetch(`${API_BASE_URL}/vote/finalize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Szavazás lezárás hiba:', error)
      throw error
    }
  }
}

export default ApiService

