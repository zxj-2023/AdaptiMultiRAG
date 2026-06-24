/**
 * 认证相关API接口
 * 对接后端 /workspace/rag-zxj/rag-demo/backend/api/auth.py
 *
/

/**
 * 用户登录
 * @param {string} email - 邮箱地址
 * @param {string} password - 密码
 * @returns {Promise<Object>} 登录响应
 */
import { httpClient, setAuthToken, getAuthToken } from './config.js'
export async function login(email, password) {
  try {
    const response = await httpClient.post('/api/auth/login', {
      email,
      password
    })
    
    // 检查响应格式，支持两种格式：直接返回token或包装在data中
    const tokenData = response.data || response
    const accessToken = tokenData.access_token
    
    // 如果登录成功，保存token
    if (accessToken) {
      setAuthToken(accessToken)
    }
    
    return response
  } catch (error) {
    console.error('登录失败:', error)
    throw new Error(error.message || '登录失败')
  }
}

/**
 * 用户注册
 * @param {string} email - 邮箱地址
 * @param {string} password - 密码
 * @param {string} username - 用户名
 * @returns {Promise<Object>} 注册响应
 */
export async function register(email, password, username) {
  try {
    const response = await httpClient.post('/api/auth/register', {
      username,
      password,
      email
    })
    
    // 检查响应格式，支持两种格式：直接返回token或包装在data中
    const tokenData = response.data || response
    const accessToken = tokenData.access_token
    
    // 如果注册成功，保存token
    if (accessToken) {
      setAuthToken(accessToken)
    }
    
    return response
  } catch (error) {
    console.error('注册失败:', error)
    throw new Error(error.message || '注册失败')
  }
}

/**
 * 获取当前用户信息
 * @returns {Promise<Object>} 用户信息响应
 */
export async function getCurrentUser() {
  try {
    const response = await httpClient.get('/api/auth/me')
    return response
  } catch (error) {
    console.error('获取用户信息失败:', error)
    throw new Error(error.message || '获取用户信息失败')
  }
}

/**
 * 访问受保护的资源
 * @returns {Promise<Object>} 受保护资源响应
 */
export async function accessProtected() {
  try {
    const response = await httpClient.get('/api/auth/protected')
    return response
  } catch (error) {
    console.error('访问受保护资源失败:', error)
    throw new Error(error.message || '访问受保护资源失败')
  }
}

/**
 * 用户登出
 * @returns {Promise<void>}
 */
export async function logout() {
  try {
    // 清除本地token
    setAuthToken(null)
    
    // 可以调用后端登出接口（如果有的话）
    // await httpClient.post('/auth/logout')
    
    return { success: true, message: '登出成功' }
  } catch (error) {
    console.error('登出失败:', error)
    throw new Error(error.message || '登出失败')
  }
}

/**
 * 检查是否已认证
 * @returns {boolean} 是否已认证
 */
export function isAuthenticated() {
  const token = getAuthToken()
  return !!token
}

/**
 * 获取认证token
 * @returns {string|null} 认证token
 */
export function getToken() {
  return getAuthToken()
}