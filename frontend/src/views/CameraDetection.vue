<template>
  <div class="detection-container">
    <header class="page-header">
      <h1 class="page-title">摄像头检测</h1>
      <p class="page-desc">实时调用摄像头进行火灾烟雾检测</p>
    </header>

    <div class="content-grid">
      <div class="video-section">
        <div class="video-card">
          <div class="video-header">
            <span class="video-title">实时画面</span>
            <div class="video-stats" v-if="isRunning">
              <span class="stat-badge fps">FPS: {{ fps }}</span>
              <span class="stat-badge time">{{ processingTime }}ms</span>
            </div>
          </div>
          <div class="video-wrapper">
            <video ref="videoRef" class="video-element" autoplay muted playsinline></video>
            <canvas ref="canvasRef" class="overlay-canvas"></canvas>
            <div v-if="!isRunning" class="video-placeholder">
              <div class="placeholder-icon">
                <svg viewBox="0 0 24 24" width="56" height="56" fill="currentColor">
                  <path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/>
                </svg>
              </div>
              <p class="placeholder-text">点击下方按钮启动摄像头</p>
            </div>
          </div>
          <div class="video-controls">
            <button class="btn btn-primary" @click="startDetection" :disabled="isRunning" :class="{ loading: isLoading }">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
              {{ isLoading ? '启动中...' : '开始检测' }}
            </button>
            <button class="btn btn-danger" @click="stopDetection" :disabled="!isRunning">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M6 6h12v12H6z"/></svg>
              停止检测
            </button>
            <!-- 置信度按钮 -->
            <div class="dropdown-wrapper" @click.stop>
              <button class="btn btn-option" @click="showConfMenu = !showConfMenu">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M19.14 12.94c.04-.31.06-.63.06-.94 0-.31-.02-.63-.06-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.04.31-.06.63-.06.94s.02.63.06.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/></svg>
                {{ (confidenceThreshold * 100).toFixed(0) }}%
              </button>
              <div class="dropdown-menu conf-menu" v-show="showConfMenu">
                <div class="conf-slider-wrap">
                  <span class="conf-label">置信度阈值</span>
                  <input type="range" v-model="confidenceThreshold" min="0.1" max="0.9" step="0.05" class="conf-slider" />
                  <span class="conf-value">{{ (confidenceThreshold * 100).toFixed(0) }}%</span>
                </div>
              </div>
            </div>
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
            <div v-for="(det, index) in stableDetections" :key="index" class="detection-item">
              <span class="det-tag" :class="det.class_name.includes('fire') ? 'fire' : 'smoke'">{{ det.class_name }}</span>
              <span class="det-conf">{{ (det.confidence * 100).toFixed(1) }}%</span>
            </div>
            <div v-if="stableDetections.length === 0" class="empty-state"><span>暂无检测结果</span></div>
          </div>
        </div>

        <div class="tip-card">
          <div class="card-header"><span class="card-title">提示</span></div>
          <p class="tip-text">检测到的结果会自动保存到检测历史中，您可以在检测历史页面进行评定。</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const videoRef = ref(null)
const canvasRef = ref(null)
const isRunning = ref(false)
const isLoading = ref(false)
const fps = ref(0)
const processingTime = ref(0)
const fireCount = ref(0)
const smokeCount = ref(0)
const rawDetections = ref([])
const confidenceThreshold = ref(0.5)
const showConfMenu = ref(false)

let mediaStream = null
let websocket = null
let animationId = null
let lastSendTime = 0
const TARGET_FPS = 10
const FRAME_INTERVAL = 1000 / TARGET_FPS
let pendingResponse = false

const stableDetections = computed(() => {
  return rawDetections.value.filter(d => d.confidence >= confidenceThreshold.value)
})

watch(stableDetections, (dets) => {
  fireCount.value = dets.filter(d => d.class_name.toLowerCase().includes('fire')).length
  smokeCount.value = dets.filter(d => d.class_name.toLowerCase().includes('smoke')).length
})

const closeMenus = (e) => {
  if (!e.target.closest('.dropdown-wrapper')) {
    showConfMenu.value = false
  }
}
onMounted(() => document.addEventListener('click', closeMenus))
onBeforeUnmount(() => { stopDetection(); document.removeEventListener('click', closeMenus) })

const startDetection = async () => {
  isLoading.value = true
  try {
    mediaStream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } })
    videoRef.value.srcObject = mediaStream
    await videoRef.value.play()
    connectWebSocket()
  } catch (e) { ElMessage.error('无法访问摄像头: ' + e.message); isLoading.value = false }
}

const stopDetection = () => {
  isRunning.value = false
  if (animationId) { cancelAnimationFrame(animationId); animationId = null }
  if (websocket) { websocket.close(); websocket = null }
  if (mediaStream) { mediaStream.getTracks().forEach(track => track.stop()); mediaStream = null }
  if (videoRef.value) { videoRef.value.srcObject = null }
  clearCanvas(); rawDetections.value = []; fireCount.value = 0; smokeCount.value = 0
}

const connectWebSocket = () => {
  // 自动适配协议和端口
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host  // 包含端口号
  const wsUrl = `${protocol}//${host}/ws/inference`
  websocket = new WebSocket(wsUrl)
  websocket.onopen = () => { isRunning.value = true; isLoading.value = false; ElMessage.success('连接成功'); startSendingFrames() }
  websocket.onmessage = (e) => { pendingResponse = false; const d = JSON.parse(e.data); if (d.type === 'result') handleResult(d.data) }
  websocket.onerror = () => { ElMessage.error('连接失败'); isLoading.value = false }
  websocket.onclose = () => { isRunning.value = false }
}

const startSendingFrames = () => {
  const tc = document.createElement('canvas'), tx = tc.getContext('2d')
  const sendFrame = () => {
    if (!isRunning.value || !websocket || websocket.readyState !== WebSocket.OPEN) return
    const now = Date.now()
    if (now - lastSendTime < FRAME_INTERVAL || pendingResponse) { animationId = requestAnimationFrame(sendFrame); return }
    const v = videoRef.value
    if (v && v.videoWidth > 0) {
      tc.width = 640; tc.height = 480; tx.drawImage(v, 0, 0, 640, 480)
      websocket.send(JSON.stringify({ 
        type: 'frame', 
        data: tc.toDataURL('image/jpeg', 0.7).split(',')[1], 
        conf_threshold: confidenceThreshold.value,
        source_type: 'camera'
      }))
      pendingResponse = true; lastSendTime = now
    }
    animationId = requestAnimationFrame(sendFrame)
  }
  animationId = requestAnimationFrame(sendFrame)
}

const handleResult = (r) => {
  fps.value = r.fps || 0; processingTime.value = Math.round((r.processing_time || 0) * 1000)
  // 合并稳定检测和实时检测结果
  const stableDets = r.stable_detections || []
  const realtimeDets = r.detections || []
  rawDetections.value = stableDets.length > 0 ? stableDets : realtimeDets
  drawDetections(r)
}

const drawDetections = (r) => {
  const c = canvasRef.value, v = videoRef.value; if (!c || !v) return
  const ctx = c.getContext('2d'); c.width = v.offsetWidth; c.height = v.offsetHeight
  ctx.clearRect(0, 0, c.width, c.height)
  const sx = c.width / (r.image_size?.width || 640), sy = c.height / (r.image_size?.height || 480)
  const dets = rawDetections.value.filter(d => d.confidence >= confidenceThreshold.value)
  dets.forEach(d => {
    const [x1,y1,x2,y2] = d.bbox, sx1=x1*sx, sy1=y1*sy, sx2=x2*sx, sy2=y2*sy
    const isFire = d.class_name.toLowerCase().includes('fire'), color = isFire ? '#ef4444' : '#6b7280'
    ctx.strokeStyle = color; ctx.lineWidth = 3; ctx.strokeRect(sx1, sy1, sx2-sx1, sy2-sy1)
    const label = `${d.class_name} ${(d.confidence*100).toFixed(0)}%`
    ctx.font = 'bold 14px Inter, sans-serif'
    ctx.fillStyle = color; ctx.fillRect(sx1, sy1-24, ctx.measureText(label).width+12, 22)
    ctx.fillStyle = '#fff'; ctx.fillText(label, sx1+6, sy1-7)
  })
}

const clearCanvas = () => { const c = canvasRef.value; if (c) c.getContext('2d').clearRect(0, 0, c.width, c.height) }
</script>

<style scoped>
.detection-container { max-width: 1400px; margin: 0 auto; }
.page-header { margin-bottom: 24px; }
.page-title { font-size: 36px; font-weight: 700; color: #1f2937; margin-bottom: 10px; }
.page-desc { font-size: 18px; color: #6b7280; }

.content-grid { display: grid; grid-template-columns: 1fr 340px; gap: 24px; }

.video-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04); overflow: visible; }
.result-card, .tip-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04); overflow: hidden; }

.video-header, .card-header {
  padding: 14px 18px; border-bottom: 1px solid #f0f0f0;
  display: flex; justify-content: space-between; align-items: center;
}
.video-title, .card-title { font-size: 20px; font-weight: 600; color: #1f2937; }
.video-stats { display: flex; gap: 8px; }
.stat-badge { padding: 6px 14px; border-radius: 6px; font-size: 16px; font-weight: 500; }
.stat-badge.fps { background: #ecfdf5; color: #10b981; }
.stat-badge.time { background: #eff6ff; color: #3b82f6; }

.video-wrapper { position: relative; aspect-ratio: 4/3; background: #f9fafb; }
.video-element { width: 100%; height: 100%; object-fit: contain; background: #1f2937; }
.overlay-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }

.video-placeholder {
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  color: #9ca3af; background: #f9fafb;
}
.placeholder-icon { margin-bottom: 12px; }
.placeholder-text { font-size: 18px; }

.video-controls { padding: 14px 18px; display: flex; gap: 12px; justify-content: center; background: #fafafa; position: relative; overflow: visible; border-radius: 0 0 12px 12px; }

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

.btn {
  display: inline-flex; align-items: center; gap: 10px;
  padding: 14px 22px; border-radius: 10px; border: none;
  font-size: 18px; font-weight: 500; cursor: pointer; transition: all 0.15s ease;
}
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary { background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); color: #fff; }
.btn-primary:hover:not(:disabled) { box-shadow: 0 4px 12px rgba(249, 115, 22, 0.35); transform: translateY(-1px); }
.btn-danger { background: #fef2f2; color: #ef4444; border: 1px solid #fecaca; }
.btn-danger:hover:not(:disabled) { background: #fee2e2; }

.info-section { display: flex; flex-direction: column; gap: 16px; }
.result-card { padding-bottom: 16px; }

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

.tip-card { padding: 16px 18px; }
.tip-text { font-size: 16px; color: #6b7280; line-height: 1.6; }
</style>
