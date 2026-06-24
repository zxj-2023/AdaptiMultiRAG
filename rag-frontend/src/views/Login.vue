<template>
  <div class="min-h-screen w-full bg-amber-50/30 flex items-center justify-center p-4 relative overflow-hidden">
    <!-- 纸质纹理背景 -->
    <div class="absolute inset-0 opacity-30" style="background-image: url('data:image/svg+xml,%3Csvg width=&quot;100&quot; height=&quot;100&quot; xmlns=&quot;http://www.w3.org/2000/svg&quot;%3E%3Cfilter id=&quot;noise&quot;%3E%3CfeTurbulence type=&quot;fractalNoise&quot; baseFrequency=&quot;0.9&quot; numOctaves=&quot;4&quot; stitchTiles=&quot;stitch&quot;/%3E%3C/filter%3E%3Crect width=&quot;100&quot; height=&quot;100&quot; filter=&quot;url(%23noise)&quot; opacity=&quot;0.05&quot;/%3E%3C/svg%3E');"></div>

    <!-- 主容器 - 类纸化卡片 -->
    <div class="relative w-full max-w-5xl">
      <div class="bg-white rounded-2xl shadow-[0_2px_8px_rgba(0,0,0,0.08)] border border-gray-100 overflow-hidden">
        <div class="flex flex-col md:flex-row">
          <!-- 左侧表单区域 -->
          <div class="w-full md:w-3/5 p-12 lg:p-16">
            <div class="max-w-md mx-auto">
              <!-- Logo区域 -->
              <div class="mb-12">
                <div class="inline-flex items-center space-x-2 mb-8">
                  <div class="w-8 h-8 rounded-lg bg-gray-900 flex items-center justify-center">
                    <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-3.582 8-8 8a8.959 8.959 0 01-4.906-1.471c-.905-.556-1.94-.808-3.094-.808-1.154 0-2.189.252-3.094.808A8.959 8.959 0 013 20c0-4.418 3.582-8 8-8s8 3.582 8 8z"/>
                    </svg>
                  </div>
                  <span class="text-xl font-medium text-gray-900">AdaptiMultiRAG</span>
                </div>

                <h1 class="text-3xl font-normal text-gray-900 mb-2 tracking-tight">
                  {{ isLogin ? '欢迎回来' : '创建账户' }}
                </h1>
                <p class="text-base text-gray-600 font-light">
                  {{ isLogin ? '登录以继续使用AI助手' : '注册以开始使用AI助手' }}
                </p>
              </div>

              <!-- 表单 -->
              <form @submit.prevent="handleSubmit" class="space-y-6">
                <!-- 用户名 (注册时) -->
                <!-- 注册功能-->
                <div v-if="!isLogin" class="space-y-2">
                  <label for="username" class="block text-sm font-medium text-gray-700">
                    用户名
                  </label>
                  <input
                    id="username"
                    v-model="form.username"
                    type="text"
                    required
                    class="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all"
                    placeholder="请输入用户名"
                  />
                </div>

                <!-- 邮箱 -->
                <div class="space-y-2">
                  <label for="email" class="block text-sm font-medium text-gray-700">
                    邮箱地址
                  </label>
                  <input
                    id="email"
                    v-model="form.email"
                    type="email"
                    required
                    class="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all"
                    placeholder="your@email.com"
                  />
                </div>

                <!-- 密码 -->
                <div class="space-y-2">
                  <label for="password" class="block text-sm font-medium text-gray-700">
                    密码
                  </label>
                  <input
                    id="password"
                    v-model="form.password"
                    type="password"
                    required
                    class="w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent transition-all"
                    placeholder="••••••••"
                  />
                </div>

                <!-- 记住我/忘记密码 -->
                <div v-if="isLogin" class="flex items-center justify-between text-sm">
                  <label class="flex items-center cursor-pointer group">
                    <input type="checkbox" class="w-4 h-4 rounded border-gray-300 text-gray-900 focus:ring-gray-900 cursor-pointer">
                    <span class="ml-2 text-gray-600">记住我</span>
                  </label>
                  <a href="#" class="text-gray-900 hover:text-gray-700 font-medium">忘记密码?</a>
                </div>

                <!-- 提交按钮 -->
                <button
                  type="submit"
                  :disabled="loading"
                  class="w-full bg-gray-900 text-white py-3 px-4 rounded-lg hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-gray-900 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                >
                  <span v-if="loading" class="flex items-center justify-center">
                    <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ isLogin ? '登录中...' : '注册中...' }}
                  </span>
                  <span v-else>{{ isLogin ? '登录' : '注册' }}</span>
                </button>
              </form>

              <!-- 切换模式 -->
              <!-- 注册功能，隐藏切换按钮 -->
              <div class="mt-8 text-center">
                <p class="text-sm text-gray-600">
                  {{ isLogin ? '还没有账户?' : '已有账户?' }}
                  <button @click="toggleMode" class="text-gray-900 hover:text-gray-700 font-medium ml-1">
                    {{ isLogin ? '注册' : '登录' }}
                  </button>
                </p>
              </div>
              <!-- <div class="mt-8 text-center">
                <p class="text-sm text-gray-500">
                  注册功能已禁用，如需账户请联系管理员
                </p>
              </div> -->

              <!-- 分隔线 -->
              <div class="mt-10 pt-8 border-t border-gray-100">
                <p class="text-xs text-gray-500 text-center">
                  继续使用即表示您同意我们的服务条款和隐私政策
                </p>
              </div>
            </div>
          </div>

          <!-- 右侧信息区域 -->
          <div class="hidden md:flex md:w-2/5 bg-gradient-to-br from-amber-50 to-orange-50 p-12 items-center justify-center border-l border-gray-100 relative">
            <!-- 装饰性引号 -->
            <div class="absolute top-12 left-12 text-6xl text-gray-200 font-serif leading-none">"</div>

            <div class="relative z-10 space-y-8">
              <!-- 标题 -->
              <div>
                <h2 class="text-2xl font-normal text-gray-900 mb-3 leading-relaxed">
                  自适应多RAG智能体<br/>让科研更高效
                </h2>
                <p class="text-base text-gray-600 leading-relaxed">
                  双模式检索 + 智能爬虫 + 知识图谱构建
                </p>
              </div>

              <!-- 特性列表 -->
              <div class="space-y-4">
                <div class="flex items-start space-x-3">
                  <div class="flex-shrink-0 w-5 h-5 mt-0.5">
                    <svg class="w-5 h-5 text-gray-900" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                    </svg>
                  </div>
                  <div>
                    <h3 class="text-sm font-medium text-gray-900 mb-1">智能理解</h3>
                    <p class="text-sm text-gray-600">基于先进语言模型的深度理解</p>
                  </div>
                </div>

                <div class="flex items-start space-x-3">
                  <div class="flex-shrink-0 w-5 h-5 mt-0.5">
                    <svg class="w-5 h-5 text-gray-900" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                    </svg>
                  </div>
                  <div>
                    <h3 class="text-sm font-medium text-gray-900 mb-1">流式响应</h3>
                    <p class="text-sm text-gray-600">实时查看AI的思考过程</p>
                  </div>
                </div>

                <div class="flex items-start space-x-3">
                  <div class="flex-shrink-0 w-5 h-5 mt-0.5">
                    <svg class="w-5 h-5 text-gray-900" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                    </svg>
                  </div>
                  <div>
                    <h3 class="text-sm font-medium text-gray-900 mb-1">持久记忆</h3>
                    <p class="text-sm text-gray-600">保存并回顾所有对话历史</p>
                  </div>
                </div>
              </div>

              <!-- 底部装饰 -->
              <div class="pt-8 border-t border-gray-200">
                <p class="text-xs text-gray-500 italic">
                  "简洁、优雅、高效的AI对话体验"
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部文字 -->
      <div class="mt-8 text-center">
        <p class="text-sm text-gray-500">
          © 2024 AdaptiMultiRAG. 保留所有权利.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import message from '../utils/message'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  email: '',
  password: '',
  username: ''
})

const loading = ref(false)
const isLogin = ref(true)

const toggleMode = () => {
  isLogin.value = !isLogin.value
  form.value = { email: '', password: '', username: '' }
}

const handleSubmit = async () => {
  loading.value = true

  try {
    // 基本验证
    if (!form.value.email || !form.value.password) {
      message.error('请填写完整的登录信息')
      return
    }

    if (!isLogin.value && !form.value.username) {
      message.error('注册时请填写用户名')
      return
    }

    let result
    if (isLogin.value) {
      // 登录时使用email作为用户名
      result = await authStore.login(form.value.email, form.value.password)
    } else {
      // 注册时传入用户名、密码和邮箱
      // 注册功能
      result = await authStore.register(form.value.email, form.value.password, form.value.username)
      // message.error('注册功能已禁用，请联系管理员')
      return result
    }

    if (result.success) {
      message.success(isLogin.value ? '登录成功！' : '注册成功！')
      router.push('/chat')
    } else {
      message.error(result.error || '操作失败，请重试')
    }
  } catch (error) {
    console.error('提交失败:', error)
    message.error('操作失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>
