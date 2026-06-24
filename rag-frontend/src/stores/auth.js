import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as apiLogin, register as apiRegister, logout as apiLogout, isAuthenticated as checkAuth } from '../api/auth.js'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)
  const loading = ref(false)

  const login = async (email, password) => {
    loading.value = true
    try {
      // 使用实际的API登录
      const result = await apiLogin(email, password)
      
      // 检查响应格式，支持两种格式：直接返回token或包装在data中
      const tokenData = result.data || result
      const accessToken = tokenData.access_token
      const userData = tokenData.user
      
      if (accessToken) {
        // 登录成功，设置用户信息
        user.value = {
          email: userData?.email || email,
          id: userData?.id || '1',
          username: userData?.username || email.split('@')[0]
        }
        isAuthenticated.value = true
        
        // 保存用户信息到localStorage
        localStorage.setItem('user_info', JSON.stringify(user.value))
        
        // Token已经在API层面通过setAuthToken保存到localStorage
        return { success: true, data: tokenData }
      } else {
        return { success: false, error: '登录失败，请检查用户名和密码' }
      }
    } catch (error) {
      console.error('登录失败:', error)
      return { success: false, error: error.message || '登录失败，请重试' }
    } finally {
      loading.value = false
    }
  }

  const register = async (email, password, username = null) => {
    loading.value = true
    try {
      // 使用实际的API注册
      const result = await apiRegister(email, password, username || email.split('@')[0])
      
      // 检查响应格式，支持两种格式：直接返回token或包装在data中
      const tokenData = result.data || result
      const accessToken = tokenData.access_token
      const userData = tokenData.user
      
      if (accessToken) {
        // 注册成功，设置用户信息
        user.value = {
          email: userData?.email || email,
          id: userData?.id || '1',
          username: userData?.username || username || email.split('@')[0]
        }
        isAuthenticated.value = true
        
        // 保存用户信息到localStorage
        localStorage.setItem('user_info', JSON.stringify(user.value))
        
        // Token已经在API层面通过setAuthToken保存到localStorage
        return { success: true, data: tokenData }
      } else {
        return { success: false, error: '注册失败，请重试' }
      }
    } catch (error) {
      console.error('注册失败:', error)
      return { success: false, error: error.message || '注册失败，请重试' }
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      await apiLogout()
      user.value = null
      isAuthenticated.value = false
      
      // 清除localStorage中的用户信息
      localStorage.removeItem('user_info')
      
      return { success: true }
    } catch (error) {
      console.error('登出失败:', error)
      // 即使API调用失败，也清除本地状态
      user.value = null
      isAuthenticated.value = false
      
      // 清除localStorage中的用户信息
      localStorage.removeItem('user_info')
      
      return { success: true }
    }
  }

  // 初始化时检查认证状态
  const initAuth = () => {
    const token = checkAuth()
    isAuthenticated.value = !!token
    if (token) {
      // 如果有token，尝试从localStorage获取用户信息
      const savedUser = localStorage.getItem('user_info')
      if (savedUser) {
        try {
          user.value = JSON.parse(savedUser)
        } catch (error) {
          console.error('解析用户信息失败:', error)
          // 如果解析失败，设置默认用户信息
          user.value = { email: 'user', id: '1', username: 'user' }
        }
      } else {
        // 如果没有保存的用户信息，设置默认值
        user.value = { email: 'user', id: '1', username: 'user' }
      }
    } else {
      user.value = null
    }
  }

  return {
    user,
    isAuthenticated,
    loading,
    login,
    register,
    logout,
    initAuth
  }
})