<template>
  <div class="detection-container">
    <header class="page-header">
      <h1 class="page-title">图片检测</h1>
      <p class="page-desc">上传图片快速获取火灾烟雾检测结果</p>
    </header>

    <div class="content-grid">
      <div class="image-section">
        <div class="image-card">
          <div class="image-header">
            <span class="image-title">图片预览</span>
            <span v-if="processingTime > 0" class="stat-badge time">处理: {{ processingTime }}ms</span>
          </div>
          <div class="image-wrapper">
            <div v-if="!imageUrl" class="image-placeholder upload-zone" @click="selectFile" @dragover.prevent @drop.prevent="handleDrop">
              <div class="placeholder-icon">
                <svg viewBox="0 0 24 24" width="48" height="48" fill="currentColor">
                  <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z"/>
                </svg>
              </div>
              <p class="placeholder-text">拖拽图片到此处，或点击上传</p>
              <p class="placeholder-hint">支持 JPG, PNG, BMP 等格式</p>
            </div>
            <div v-else class="image-display">
              <img :src="resultImageUrl || imageUrl" class="preview-image" />
            </div>
          </div>
          <div class="image-controls">
            <button class="btn btn-secondary" @click="selectFile">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
              选择图片
            </button>
            <button class="btn btn-primary" @click="startDetection" :disabled="!imageFile" :class="{ loading: isLoading }">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46C19.54 15.03 20 13.57 20 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74C4.46 8.97 4 10.43 4 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/></svg>
              {{ isLoading ? '检测中...' : '开始检测' }}
            </button>
            <button class="btn btn-ghost" @click="resetImage">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>
              重置
            </button>
            <!-- 置信度按钮 -->
            <div class="dropdown-wrapper" @click.stop>
              <button class="btn btn-option" @click="showConfMenu = !showConfMenu">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M19.14 12.94c.04-.31.06-.63.06-.94 0-.31-.02-.63-.06-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.04.31-.06.63-.06.94s.02.63.06.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg>
                {{ (Number(confidenceThreshold) * 100).toFixed(0) }}%
              </button>
              <div class="dropdown-menu conf-menu" v-show="showConfMenu">
                <div class="conf-slider-wrap">
                  <span class="conf-label">置信度阈值</span>
                  <input type="range" :value="confidenceThreshold" @input="onConfidenceChange" min="0.1" max="0.9" step="0.05" class="conf-slider" />
                  <span class="conf-value">{{ (Number(confidenceThreshold) * 100).toFixed(0) }}%</span>
                </div>
              </div>
            </div>
          </div>
          <div v-if="imageFile" class="file-info">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>
            <span>{{ imageFile.name }}</span>
          </div>
        </div>
      </div>

      <div class="info-section">
        <div class="result-card">
          <div class="card-header"><span class="card-title">检测结果</span></div>
          <div class="detection-stats">
            <div class="detection-stat">
              <div class="stat-circle fire"><span class="stat-num">{{ fireCount }}</span></div>
              <span class="stat-name">火焰</span>
            </div>
            <div class="detection-stat">
              <div class="stat-circle smoke"><span class="stat-num">{{ smokeCount }}</span></div>
              <span class="stat-name">烟雾</span>
            </div>
          </div>
          <div class="detection-list">
            <div v-for="(det, index) in detections" :key="index" class="detection-item">
              <span class="det-tag" :class="det.class_name.includes('fire') ? 'fire' : 'smoke'">{{ det.class_name }}</span>
              <span class="det-conf">{{ (det.confidence * 100).toFixed(1) }}%</span>
            </div>
            <div v-if="detections.length === 0 && !isLoading" class="empty-state"><span>暂无检测结果</span></div>
          </div>
        </div>

        <div class="eval-card">
          <div class="card-header"><span class="card-title">结果评定</span></div>
          <p class="eval-hint">当前检测结果是否正确?</p>
          <div class="eval-buttons">
            <button class="btn btn-success" @click="submitEvaluation(true)" :disabled="detections.length === 0">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
              正确
            </button>
            <button class="btn btn-error" @click="submitEvaluation(false)" :disabled="detections.length === 0">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
              错误
            </button>
          </div>
          <textarea v-model="evalNotes" class="eval-textarea" placeholder="备注信息(可选)"></textarea>
        </div>
      </div>
    </div>
    <input type="file" ref="fileInputRef" accept="image/*" style="display: none" @change="onFileSelected" />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const fileInputRef = ref(null)
const imageFile = ref(null), imageUrl = ref(''), resultImageUrl = ref('')
const isLoading = ref(false), fireCount = ref(0), smokeCount = ref(0)
const rawDetections = ref([]), processingTime = ref(0), evalNotes = ref('')
const confidenceThreshold = ref(0.5)
const showConfMenu = ref(false)

const detections = computed(() => {
  return rawDetections.value.filter(d => d.confidence >= confidenceThreshold.value)
})

watch(detections, (dets) => {
  fireCount.value = dets.filter(d => d.class_name.toLowerCase().includes('fire')).length
  smokeCount.value = dets.filter(d => d.class_name.toLowerCase().includes('smoke')).length
})

// 点击外部关闭下拉菜单
const closeMenus = (e) => {
  if (!e.target.closest('.dropdown-wrapper')) {
    showConfMenu.value = false
  }
}
onMounted(() => document.addEventListener('click', closeMenus))
onBeforeUnmount(() => document.removeEventListener('click', closeMenus))

const onConfidenceChange = (e) => {
  confidenceThreshold.value = parseFloat(e.target.value)
}

const selectFile = () => fileInputRef.value.click()
const onFileSelected = (e) => { if (e.target.files[0]) loadImageFile(e.target.files[0]) }
const handleDrop = (e) => { if (e.dataTransfer.files[0]) loadImageFile(e.dataTransfer.files[0]) }

const loadImageFile = (file) => {
  imageFile.value = file; imageUrl.value = URL.createObjectURL(file); resultImageUrl.value = ''
  rawDetections.value = []; fireCount.value = 0; smokeCount.value = 0; processingTime.value = 0
  ElMessage.success('图片加载成功')
}

const startDetection = async () => {
  if (!imageFile.value) return
  isLoading.value = true
  try {
    const fd = new FormData(); fd.append('file', imageFile.value); fd.append('conf_threshold', confidenceThreshold.value)
    const res = await axios.post('/api/inference/image', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    if (res.data.success) {
      const r = res.data.result
      rawDetections.value = r.detections || []
      processingTime.value = Math.round((r.processing_time || 0) * 1000)
      if (res.data.visualization) resultImageUrl.value = res.data.visualization
      ElMessage.success('检测完成')
    } else { ElMessage.error('检测失败') }
  } catch (e) { ElMessage.error('检测失败: ' + (e.response?.data?.detail || e.message)) }
  finally { isLoading.value = false }
}

const resetImage = () => {
  imageFile.value = null; imageUrl.value = ''; resultImageUrl.value = ''
  rawDetections.value = []; fireCount.value = 0; smokeCount.value = 0; processingTime.value = 0
  fileInputRef.value.value = ''
}

const submitEvaluation = async (isCorrect) => {
  try {
    const fd = new FormData()
    fd.append('detection_id', Date.now().toString()); fd.append('is_correct', isCorrect)
    fd.append('detection_type', detections.value.map(d => d.class_name).join(','))
    fd.append('source_type', 'image'); fd.append('notes', evalNotes.value)
    await axios.post('/api/evaluation', fd); ElMessage.success('评定提交成功'); evalNotes.value = ''
  } catch { ElMessage.error('评定提交失败') }
}
</script>

<style scoped>
.detection-container { max-width: 1400px; margin: 0 auto; }
.page-header { margin-bottom: 24px; }
.page-title { font-size: 36px; font-weight: 700; color: #1f2937; margin-bottom: 10px; }
.page-desc { font-size: 18px; color: #6b7280; }
.content-grid { display: grid; grid-template-columns: 1fr 340px; gap: 24px; }

.image-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04); overflow: visible; }
.result-card, .eval-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04); overflow: hidden; }
.image-header, .card-header { padding: 14px 18px; border-bottom: 1px solid #f0f0f0; display: flex; justify-content: space-between; align-items: center; }
.image-title, .card-title { font-size: 20px; font-weight: 600; color: #1f2937; }
.stat-badge { padding: 6px 14px; border-radius: 6px; font-size: 16px; font-weight: 500; }
.stat-badge.time { background: #eff6ff; color: #3b82f6; }

.image-wrapper { min-height: 380px; background: #f9fafb; display: flex; align-items: center; justify-content: center; }
.image-placeholder { width: calc(100% - 32px); height: 350px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #9ca3af; }
.upload-zone { cursor: pointer; border: 2px dashed #e5e7eb; margin: 16px; border-radius: 10px; transition: all 0.2s; background: #fafafa; }
.upload-zone:hover { border-color: #f97316; background: #fff7ed; }
.placeholder-icon { margin-bottom: 12px; }
.placeholder-text { font-size: 18px; margin-bottom: 4px; color: #6b7280; }
.placeholder-hint { font-size: 16px; color: #9ca3af; }

.image-display { padding: 16px; width: 100%; display: flex; justify-content: center; }
.preview-image { max-width: 100%; max-height: 450px; object-fit: contain; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }

.image-controls { padding: 14px 18px; display: flex; gap: 10px; justify-content: center; background: #fafafa; position: relative; overflow: visible; border-radius: 0 0 12px 12px; }

/* 下拉菜单样式 */
.dropdown-wrapper { position: relative; z-index: 1000; }
.dropdown-menu {
  position: absolute; bottom: 100%; left: 50%; transform: translateX(-50%);
  margin-bottom: 8px; background: #fff; border: 1px solid #e5e7eb;
  border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.15);
  z-index: 1001; min-width: 100px; overflow: visible;
}
.conf-menu { min-width: 240px; padding: 16px; }
.conf-slider-wrap { display: flex; flex-direction: column; gap: 10px; }
.conf-label { font-size: 15px; font-weight: 600; color: #374151; }
.conf-slider { 
  width: 100%; height: 8px; -webkit-appearance: none; appearance: none; 
  background: #e5e7eb; border-radius: 4px; outline: none; cursor: pointer;
}
.conf-slider::-webkit-slider-thumb {
  -webkit-appearance: none; width: 20px; height: 20px; border-radius: 50%;
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
  cursor: pointer; box-shadow: 0 2px 6px rgba(249, 115, 22, 0.4);
}
.conf-value { font-size: 18px; font-weight: 700; color: #f97316; text-align: center; }

.btn-option { background: #f3f4f6; color: #374151; border: 1px solid #e5e7eb; min-width: 90px; }
.btn-option:hover { background: #e5e7eb; }
.file-info { padding: 0 20px 16px; display: flex; align-items: center; gap: 10px; font-size: 17px; color: #6b7280; }

.btn { display: inline-flex; align-items: center; gap: 10px; padding: 13px 18px; border-radius: 10px; border: none; font-size: 17px; font-weight: 500; cursor: pointer; transition: all 0.15s ease; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); color: #fff; }
.btn-primary:hover:not(:disabled) { box-shadow: 0 4px 12px rgba(249, 115, 22, 0.35); transform: translateY(-1px); }
.btn-secondary { background: #f3f4f6; color: #374151; border: 1px solid #e5e7eb; }
.btn-secondary:hover:not(:disabled) { background: #e5e7eb; }
.btn-ghost { background: transparent; color: #6b7280; }
.btn-ghost:hover:not(:disabled) { color: #374151; background: #f3f4f6; }
.btn-success { background: #ecfdf5; color: #10b981; border: 1px solid #a7f3d0; flex: 1; justify-content: center; }
.btn-success:hover:not(:disabled) { background: #d1fae5; }
.btn-error { background: #fef2f2; color: #ef4444; border: 1px solid #fecaca; flex: 1; justify-content: center; }
.btn-error:hover:not(:disabled) { background: #fee2e2; }

.info-section { display: flex; flex-direction: column; gap: 16px; }
.result-card, .eval-card { padding-bottom: 16px; }
.detection-stats { display: flex; justify-content: center; gap: 36px; padding: 20px; }
.detection-stat { text-align: center; }
.stat-circle { width: 68px; height: 68px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 8px; }
.stat-circle.fire { background: #fef2f2; border: 2px solid #fecaca; }
.stat-circle.smoke { background: #f3f4f6; border: 2px solid #e5e7eb; }
.stat-num { font-size: 36px; font-weight: 700; }
.stat-circle.fire .stat-num { color: #ef4444; }
.stat-circle.smoke .stat-num { color: #6b7280; }
.stat-name { font-size: 17px; color: #6b7280; }

.detection-list { padding: 0 18px; max-height: 140px; overflow-y: auto; }
.detection-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #f0f0f0; }
.detection-item:last-child { border-bottom: none; }
.det-tag { padding: 6px 14px; border-radius: 6px; font-size: 16px; font-weight: 500; }
.det-tag.fire { background: #fef2f2; color: #ef4444; }
.det-tag.smoke { background: #f3f4f6; color: #6b7280; }
.det-conf { font-size: 17px; color: #6b7280; }
.empty-state { text-align: center; padding: 20px; color: #9ca3af; font-size: 17px; }

.eval-hint { padding: 16px 20px 12px; font-size: 18px; color: #6b7280; text-align: center; }
.eval-buttons { display: flex; gap: 12px; padding: 0 18px; }
.eval-textarea { width: calc(100% - 40px); margin: 16px 20px 0; padding: 14px 16px; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 10px; color: #1f2937; font-size: 17px; resize: none; font-family: inherit; }
.eval-textarea::placeholder { color: #9ca3af; }
.eval-textarea:focus { outline: none; border-color: #f97316; background: #fff; }
</style>
