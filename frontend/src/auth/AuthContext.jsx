import { createContext, useContext, useEffect, useState } from 'react'
import client, { clearSystemInfoCache } from '../api/client.js'

const AuthCtx = createContext(null)
export const useAuth = () => useContext(AuthCtx)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('jc_token')
    if (!token) {
      setLoading(false)
      return
    }
    client
      .get('/auth/me')
      .then((res) => setUser(res.data))
      .catch(() => {
        localStorage.removeItem('jc_token')
        clearSystemInfoCache()
      })
      .finally(() => setLoading(false))
  }, [])

  async function authenticate(path, payload) {
    const res = await client.post(`/auth/${path}`, payload)
    localStorage.setItem('jc_token', res.data.access_token)
    setUser(res.data.user)
    return res.data.user
  }

  const login = (email, password) => authenticate('login', { email, password })
  const register = (name, email, password) => authenticate('register', { name, email, password })

  function logout() {
    localStorage.removeItem('jc_token')
    clearSystemInfoCache()
    setUser(null)
  }

  return (
    <AuthCtx.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthCtx.Provider>
  )
}
