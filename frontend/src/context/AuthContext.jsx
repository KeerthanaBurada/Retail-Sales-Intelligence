import { createContext, useContext, useState, useEffect } from 'react'
import { loginUser, registerUser, getProfile } from '../api/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(true)

  // On mount, check if a token exists in localStorage and validate it
  useEffect(() => {
    const savedToken = localStorage.getItem('token')
    if (!savedToken) {
      setLoading(false)
      return
    }

    setToken(savedToken)
    getProfile()
      .then((res) => setUser(res.data))
      .catch(() => {
        // Token is expired or invalid — clean up
        localStorage.removeItem('token')
        setToken(null)
      })
      .finally(() => setLoading(false))
  }, [])

  const login = async (email, password) => {
    const res = await loginUser(email, password)
    const newToken = res.data.access_token
    localStorage.setItem('token', newToken)
    setToken(newToken)

    // Fetch user profile after login
    const profileRes = await getProfile()
    setUser(profileRes.data)
  }

  const register = async (email, name, password) => {
    const res = await registerUser(email, name, password)
    const newToken = res.data.access_token
    localStorage.setItem('token', newToken)
    setToken(newToken)

    const profileRes = await getProfile()
    setUser(profileRes.data)
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used inside an AuthProvider')
  }
  return context
}
