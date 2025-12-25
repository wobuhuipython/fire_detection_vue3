<template>
  <div class="home-container">
    <header class="page-header">
      <h1 class="page-title">系统概览</h1>
      <p class="page-desc">实时监控火灾检测状态与统计数据</p>
    </header>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor">
            <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
          </svg>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.total }}</span>
          <span class="stat-label">总评定数</span>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon correct">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
          </svg>
        </div>
        <div class="stat-info">
          <span class="stat-value correct">{{ stats.correct }}</span>
          <span class="stat-label">正确识别</span>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon incorrect">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </div>
        <div class="stat-info">
          <span class="stat-value incorrect">{{ stats.incorrect }}</span>
          <span class="stat-label">错误识别</span>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon accuracy">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor">
            <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM10 17l-3.5-3.5 1.41-1.41L10 14.17l4.59-4.59L16 11l-6 6z"/>
          </svg>
        </div>
        <div class="stat-info">
          <span class="stat-value accuracy">{{ (stats.accuracy * 100).toFixed(1) }}%</span>
          <span class="stat-label">准确率</span>
        </div>
      </div>
    </div>

    <div class="feature-section">
      <h2 class="section-title">快速开始</h2>
      <div class="feature-grid">
        <div class="feature-card" @click="$router.push('/camera')">
          <div class="feature-icon camera">
            <svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor">
              <path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/>
            </svg>
          </div>
          <div class="feature-content">
            <h3>摄像头检测</h3>
            <p>实时调用摄像头进行火灾烟雾检测</p>
          </div>
          <div class="feature-arrow">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
            </svg>
          </div>
        </div>
        
        <div class="feature-card" @click="$router.push('/video')">
          <div class="feature-icon video">
            <svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor">
              <path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z"/>
            </svg>
          </div>
          <div class="feature-content">
            <h3>视频检测</h3>
            <p>上传视频文件进行火灾检测分析</p>
          </div>
          <div class="feature-arrow">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
            </svg>
          </div>
        </div>
        
        <div class="feature-card" @click="$router.push('/image')">
          <div class="feature-icon image">
            <svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor">
              <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
            </svg>
          </div>
          <div class="feature-content">
            <h3>图片检测</h3>
            <p>上传图片快速获取检测结果</p>
          </div>
          <div class="feature-arrow">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
            </svg>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const stats = ref({ total: 0, correct: 0, incorrect: 0, accuracy: 0 })

const loadStats = async () => {
  try {
    const res = await axios.get('/api/evaluations')
    stats.value = res.data.statistics
  } catch (e) { console.error('加载统计数据失败:', e) }
}

onMounted(() => loadStats())
</script>

<style scoped>
.home-container { max-width: 1200px; margin: 0 auto; }

.page-header { margin-bottom: 28px; }
.page-title { font-size: 36px; font-weight: 700; color: #1f2937; margin-bottom: 10px; }
.page-desc { font-size: 18px; color: #6b7280; }

.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 36px; }

.stat-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.stat-icon {
  width: 48px; height: 48px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
}
.stat-icon.total { background: #eef2ff; color: #6366f1; }
.stat-icon.correct { background: #ecfdf5; color: #10b981; }
.stat-icon.incorrect { background: #fef2f2; color: #ef4444; }
.stat-icon.accuracy { background: #eff6ff; color: #3b82f6; }

.stat-info { display: flex; flex-direction: column; }
.stat-value { font-size: 36px; font-weight: 700; color: #1f2937; }
.stat-value.correct { color: #10b981; }
.stat-value.incorrect { color: #ef4444; }
.stat-value.accuracy { color: #3b82f6; }
.stat-label { font-size: 17px; color: #6b7280; margin-top: 4px; }

.section-title { font-size: 24px; font-weight: 600; color: #1f2937; margin-bottom: 20px; }

.feature-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }

.feature-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}
.feature-card:hover {
  border-color: #f97316;
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.12);
  transform: translateY(-2px);
}

.feature-icon {
  width: 52px; height: 52px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.feature-icon.camera { background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%); color: #fff; }
.feature-icon.video { background: linear-gradient(135deg, #ec4899 0%, #f43f5e 100%); color: #fff; }
.feature-icon.image { background: linear-gradient(135deg, #06b6d4 0%, #0ea5e9 100%); color: #fff; }

.feature-content { flex: 1; }
.feature-content h3 { font-size: 20px; font-weight: 600; color: #1f2937; margin-bottom: 6px; }
.feature-content p { font-size: 17px; color: #6b7280; line-height: 1.5; }

.feature-arrow { color: #d1d5db; transition: all 0.2s ease; }
.feature-card:hover .feature-arrow { color: #f97316; transform: translateX(4px); }
</style>
