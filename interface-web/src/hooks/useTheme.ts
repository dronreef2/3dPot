import { useState, useEffect, useCallback } from 'react'

type Theme = 'light' | 'dark' | 'auto'

export function useTheme(initialTheme: Theme = 'auto') {
  const [theme, setTheme] = useState<Theme>(initialTheme)
  const [isDark, setIsDark] = useState(false)

  // Check if system prefers dark mode
  const getSystemPreference = useCallback(() => {
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  }, [])

  // Update theme based on current setting
  const updateTheme = useCallback((newTheme: Theme) => {
    setTheme(newTheme)
    localStorage.setItem('3dpot-theme', newTheme)
    
    let shouldBeDark = false
    
    if (newTheme === 'dark') {
      shouldBeDark = true
    } else if (newTheme === 'light') {
      shouldBeDark = false
    } else if (newTheme === 'auto') {
      shouldBeDark = getSystemPreference()
    }
    
    setIsDark(shouldBeDark)
    
    // Apply theme to document
    if (shouldBeDark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    
    // Update meta theme-color for mobile browsers
    const metaThemeColor = document.querySelector('meta[name="theme-color"]')
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', shouldBeDark ? '#1f2937' : '#3b82f6')
    }
  }, [getSystemPreference])

  // Toggle between light and dark (useful for a simple toggle button)
  const toggleTheme = useCallback(() => {
    if (theme === 'light') {
      updateTheme('dark')
    } else if (theme === 'dark') {
      updateTheme('light')
    } else {
      // If auto, switch to opposite of current system preference
      updateTheme(getSystemPreference() ? 'light' : 'dark')
    }
  }, [theme, updateTheme, getSystemPreference])

  // Set specific theme
  const setThemeMode = useCallback((newTheme: Theme) => {
    updateTheme(newTheme)
  }, [updateTheme])

  // Initialize theme from localStorage or default
  useEffect(() => {
    const savedTheme = localStorage.getItem('3dpot-theme') as Theme
    if (savedTheme && ['light', 'dark', 'auto'].includes(savedTheme)) {
      updateTheme(savedTheme)
    } else {
      updateTheme(initialTheme)
    }
  }, []) // Only run on mount

  // Listen for system theme changes when in auto mode
  useEffect(() => {
    if (theme === 'auto') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      
      const handleChange = (e: MediaQueryListEvent) => {
        updateTheme('auto')
      }
      
      // Modern browsers
      if (mediaQuery.addEventListener) {
        mediaQuery.addEventListener('change', handleChange)
        return () => mediaQuery.removeEventListener('change', handleChange)
      } else {
        // Fallback for older browsers
        mediaQuery.addListener(handleChange)
        return () => mediaQuery.removeListener(handleChange)
      }
    }
  }, [theme, updateTheme])

  // Apply theme immediately on state change
  useEffect(() => {
    updateTheme(theme)
  }, [theme, updateTheme])

  return {
    theme,
    isDark,
    toggleTheme,
    setTheme: setThemeMode,
    updateTheme
  }
}