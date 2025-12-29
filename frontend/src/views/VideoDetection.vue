  <template>
    <div class="detection-container">
      <header class="page-header">
        <h1 class="page-title">视频检测</h1>
        <p class="page-desc">上传视频文件进行火灾烟雾检测分析</p>
      </header>

      <div class="content-grid">
        <div class="video-section">
          <div class="video-card">
            <div class="video-header">
              <span class="video-title">视频画面</span>
              <div class="video-stats" v-if="isRunning">
                <span class="stat-badge fps">FPS: {{ fps }}</span>
                <span class="stat-badge time">{{ processingTime }}ms</span>
              </div>
            </div>
            <div class="video-wrapper">
              <video ref="videoRef" class="video-element" @loadedmetadata="onVideoLoaded" @ended="onVideoEnded" muted></video>
              <canvas ref="canvasRef" class="overlay-canvas"></canvas>
              <div v-if="!videoFile" class="video-placeholder upload-zone" @click="selectFile" @dragover.prevent @drop.prevent="handleDrop">
                <div class="placeholder-icon">
                  <svg viewBox="0 0 24 24" width="48" height="48" fill="currentColor">
                    <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z"/>
                  </svg>
                </div>
                <p class="placeholder-text">拖拽视频文件到此处，或点击上传</p>
                <p class="placeholder-hint">支持 MP4, AVI, MOV 等格式</p>
              </div>
            </div>
            <div class="video-controls">
              <button class="btn btn-secondary" @click="selectFile" :disabled="isRunning">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
                选择视频
              </button>
              <button class="btn btn-primary" @click="startDetection" :disabled="!videoFile || isRunning">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
                开始检测
              </button>
              <button class="btn btn-danger" @click="stopDetection" :disabled="!isRunning">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M6 6h12v12H6z"/></svg>
                停止
              </button>
              <button class="btn btn-ghost" @click="resetVideo" :disabled="isRunning">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>
                重置
              </button>
              <!-- 倍速按钮 -->
              <div class="dropdown-wrapper" @click.stop>
                <button class="btn btn-option" @click="showSpeedMenu = !showSpeedMenu; showConfMenu = false">
                  <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M13 2.05v2.02c3.95.49 7 3.85 7 7.93 0 3.21-1.92 6-4.72 7.28L13 17v5h5l-1.22-1.22C19.91 19.07 22 15.76 22 12c0-5.18-3.95-9.45-9-9.95zM11 2.05C5.94 2.55 2 6.81 2 12c0 3.76 2.09 7.07 5.22 8.78L6 22h5v-5l-2.28 2.28C6.92 18 5 15.21 5 12c0-4.08 3.05-7.44 7-7.93V2.05z"/></svg>
                  {{ playbackRate }}x
                </button>
                <div class="dropdown-menu" v-show="showSpeedMenu">
                  <button v-for="speed in [0.5, 1, 1.5, 2]" :key="speed" class="dropdown-item" :class="{ active: playbackRate == speed }" @click="setPlaybackRate(speed)">
                    {{ speed }}x
                  </button>
                </div>
              </div>
              <!-- 置信度按钮 -->
              <div class="dropdown-wrapper" @click.stop>
                <button class="btn btn-option" @click="showConfMenu = !showConfMenu; showSpeedMenu = false">
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
            <div v-if="videoFile" class="file-info">
              <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z"/></svg>
              <span>{{ videoFile.name }}</span>
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
              <div v-for="(det, index) in filteredDetections" :key="index" class="detection-item">
                <span class="det-tag" :class="det.class_name.includes('fire') ? 'fire' : 'smoke'">{{ det.class_name }}</span>
                <span class="det-conf">{{ (det.confidence * 100).toFixed(1) }}%</span>
              </div>
              <div v-if="filteredDetections.length === 0" class="empty-state"><span>暂无检测结果</span></div>
            </div>
          </div>

          <div class="tip-card">
            <div class="card-header"><span class="card-title">提示</span></div>
            <p class="tip-text">检测到的结果会自动保存到检测历史中，您可以在检测历史页面进行评定。</p>
          </div>
        </div>
      </div>
      <input type="file" ref="fileInputRef" accept="video/*" style="display: none" @change="onFileSelected" />
    </div>
  </template>

  <script setup>
  import { ref, computed, onBeforeUnmount, watch, onMounted } from 'vue'
  import { ElMessage } from 'element-plus'

  const videoRef = ref(null), canvasRef = ref(null), fileInputRef = ref(null)
  const videoFile = ref(null), isRunning = ref(false)
  const fps = ref(0), processingTime = ref(0), fireCount = ref(0), smokeCount = ref(0)
  const stableDetections = ref([])

  const playbackRate = ref(1)
  const confidenceThreshold = ref(0.5)
  const showSpeedMenu = ref(false)
  const showConfMenu = ref(false)

  let websocket = null, animationId = null, lastSendTime = 0, pendingResponse = false
  const TARGET_FPS = 10, FRAME_INTERVAL = 1000 / TARGET_FPS

  const filteredDetections = computed(() => {
    return stableDetections.value.filter(d => d.confidence >= confidenceThreshold.value)
  })

  watch(filteredDetections, (dets) => {
    fireCount.value = dets.filter(d => d.class_name.toLowerCase().includes('fire')).length
    smokeCount.value = dets.filter(d => d.class_name.toLowerCase().includes('smoke')).length
  })

  const closeMenus = (e) => {
    if (!e.target.closest('.dropdown-wrapper')) {
      showSpeedMenu.value = false
      showConfMenu.value = false
    }
  }
  onMounted(() => document.addEventListener('click', closeMenus))
  onBeforeUnmount(() => { stopDetection(); document.removeEventListener('click', closeMenus) })

  const selectFile = () => fileInputRef.value.click()
  const onFileSelected = (e) => { if (e.target.files[0]) loadVideoFile(e.target.files[0]) }
  const handleDrop = (e) => { if (e.dataTransfer.files[0]) loadVideoFile(e.dataTransfer.files[0]) }

  const loadVideoFile = (file) => { 
    videoFile.value = file
    videoRef.value.src = URL.createObjectURL(file)
    ElMessage.success('视频加载成功') 
  }

  const onVideoLoaded = () => { 
    canvasRef.value.width = videoRef.value.videoWidth
    canvasRef.value.height = videoRef.value.videoHeight
    videoRef.value.playbackRate = playbackRate.value
  }

  const onVideoEnded = () => { if (isRunning.value) { stopDetection(); ElMessage.info('视频播放结束') } }

  const setPlaybackRate = (rate) => {
    playbackRate.value = rate
    if (videoRef.value) videoRef.value.playbackRate = rate
    showSpeedMenu.value = false
  }

  const startDetection = () => { if (!videoFile.value) return; connectWebSocket() }

  const stopDetection = () => {
    isRunning.value = false
    if (animationId) { cancelAnimationFrame(animationId); animationId = null }
    if (websocket) { websocket.close(); websocket = null }
    if (videoRef.value) videoRef.value.pause()
    clearCanvas()
  }

  const resetVideo = () => {
    stopDetection(); videoFile.value = null
    if (videoRef.value) videoRef.value.src = ''
    stableDetections.value = []; fireCount.value = 0; smokeCount.value = 0
    fileInputRef.value.value = ''
  }

  const connectWebSocket = () => {
    // 自动适配协议和端口
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host  // 包含端口号
    websocket = new WebSocket(`${protocol}//${host}/ws/inference`)
    websocket.onopen = () => { 
      isRunning.value = true
      videoRef.value.playbackRate = playbackRate.value
      videoRef.value.play()
      ElMessage.success('开始检测')
      startSendingFrames() 
    }
    websocket.onmessage = (e) => { 
      pendingResponse = false
      const d = JSON.parse(e.data)
      if (d.type === 'result') handleResult(d.data) 
    }
    websocket.onerror = () => ElMessage.error('连接失败')
    websocket.onclose = () => { isRunning.value = false }
  }

  const startSendingFrames = () => {
    const tc = document.createElement('canvas'), tx = tc.getContext('2d')
    let pendingTimeout = null
    
    const sendFrame = () => {
      if (!isRunning.value || !websocket || websocket.readyState !== WebSocket.OPEN) return
      
      const now = Date.now()
      // 如果等待响应超过2秒，重置pendingResponse防止卡死
      if (pendingResponse && now - lastSendTime > 2000) {
        pendingResponse = false
      }
      
      if (now - lastSendTime < FRAME_INTERVAL || pendingResponse) { 
        animationId = requestAnimationFrame(sendFrame)
        return 
      }
      
      const v = videoRef.value
      if (v && v.videoWidth > 0 && !v.paused) {
        tc.width = 640; tc.height = Math.round(640 * v.videoHeight / v.videoWidth)
        tx.drawImage(v, 0, 0, tc.width, tc.height)
        websocket.send(JSON.stringify({ 
          type: 'frame', 
          data: tc.toDataURL('image/jpeg', 0.7).split(',')[1], 
          conf_threshold: confidenceThreshold.value,
          source_type: 'video'
        }))
        pendingResponse = true
        lastSendTime = now
      }
      animationId = requestAnimationFrame(sendFrame)
    }
    animationId = requestAnimationFrame(sendFrame)
  }

  const handleResult = (r) => {
    fps.value = r.fps || 0
    processingTime.value = Math.round((r.processing_time || 0) * 1000)
    // 合并稳定检测和实时检测结果，优先显示稳定结果，但也保留实时结果
    const stableDets = r.stable_detections || []
    const realtimeDets = r.detections || []
    // 如果有稳定结果就用稳定结果，否则用实时结果（这样改变置信度时也能立即看到效果）
    stableDetections.value = stableDets.length > 0 ? stableDets : realtimeDets
    drawDetections(r, stableDetections.value)
  }

  const drawDetections = (r, detections) => {
    const c = canvasRef.value, v = videoRef.value
    if (!c || !v) return
    const ctx = c.getContext('2d')
    c.width = v.offsetWidth; c.height = v.offsetHeight
    ctx.clearRect(0, 0, c.width, c.height)
    const sx = c.width / (r.image_size?.width || v.videoWidth)
    const sy = c.height / (r.image_size?.height || v.videoHeight)
    const dets = (detections || []).filter(d => d.confidence >= confidenceThreshold.value)
    dets.forEach(d => {
      const [x1,y1,x2,y2] = d.bbox
      const sx1=x1*sx, sy1=y1*sy, sx2=x2*sx, sy2=y2*sy
      const isFire = d.class_name.toLowerCase().includes('fire')
      const color = isFire ? '#ef4444' : '#6b7280'
      ctx.strokeStyle = color; ctx.lineWidth = 3
      ctx.strokeRect(sx1, sy1, sx2-sx1, sy2-sy1)
      const label = `${d.class_name} ${(d.confidence*100).toFixed(0)}%`
      ctx.font = 'bold 16px Inter, sans-serif'
      ctx.fillStyle = color; ctx.fillRect(sx1, sy1-26, ctx.measureText(label).width+14, 24)
      ctx.fillStyle = '#fff'; ctx.fillText(label, sx1+7, sy1-7)
    })
  }

  const clearCanvas = () => { const c = canvasRef.value; if (c) c.getContext('2d').clearRect(0, 0, c.width, c.height) }
  </script>


  <style scoped>
  .detection-container { max-width: 1400px; margin: 0 auto; padding: 0; }
  .page-header { margin-bottom: 24px; }
  .page-title { font-size: 36px; font-weight: 700; color: #1f2937; margin-bottom: 10px; }
  .page-desc { font-size: 18px; color: #6b7280; }
  .content-grid { display: grid; grid-template-columns: 1fr 360px; gap: 24px; }

  .video-section { min-width: 0; }

  .video-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04); overflow: visible; }
  .result-card, .tip-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04); overflow: hidden; }
  .video-header, .card-header { padding: 16px 20px; border-bottom: 1px solid #f0f0f0; display: flex; justify-content: space-between; align-items: center; }
  .video-title, .card-title { font-size: 20px; font-weight: 600; color: #1f2937; }
  .video-stats { display: flex; gap: 10px; }
  .stat-badge { padding: 6px 14px; border-radius: 6px; font-size: 16px; font-weight: 500; }
  .stat-badge.fps { background: #ecfdf5; color: #10b981; }
  .stat-badge.time { background: #eff6ff; color: #3b82f6; }

  .video-wrapper { position: relative; aspect-ratio: 16/9; background: #1f2937; min-height: 400px; }
  .video-element { width: 100%; height: 100%; object-fit: contain; background: #1f2937; display: block; }
  .overlay-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }

  .video-placeholder { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: auto; height: auto; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #9ca3af; z-index: 10; }
  .upload-zone { cursor: pointer; border: 2px dashed #d1d5db; padding: 60px 100px; border-radius: 16px; transition: all 0.2s; background: #f9fafb; }
  .upload-zone:hover { border-color: #f97316; background: #fff7ed; }
  .placeholder-icon { margin-bottom: 24px; color: #9ca3af; }
  .placeholder-icon svg { width: 64px; height: 64px; }
  .placeholder-text { font-size: 22px; margin-bottom: 12px; color: #6b7280; }
  .placeholder-hint { font-size: 18px; color: #9ca3af; }

  .video-controls { padding: 16px 20px; display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; background: #fafafa; position: relative; overflow: visible; border-radius: 0 0 12px 12px; }
  .file-info { padding: 0 20px 16px; display: flex; align-items: center; gap: 10px; font-size: 17px; color: #6b7280; }

  .dropdown-wrapper { position: relative; z-index: 1000; }
  .dropdown-menu { position: absolute; bottom: 100%; left: 50%; transform: translateX(-50%); margin-bottom: 8px; background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.15); z-index: 1001; min-width: 100px; overflow: visible; }
  .dropdown-item { display: block; width: 100%; padding: 12px 20px; border: none; background: transparent; font-size: 17px; color: #374151; cursor: pointer; text-align: center; transition: all 0.15s; }
  .dropdown-item:hover { background: #f9fafb; }
  .dropdown-item.active { background: #fff7ed; color: #ea580c; font-weight: 600; }

  .conf-menu { min-width: 240px; padding: 16px; }
  .conf-slider-wrap { display: flex; flex-direction: column; gap: 10px; }
  .conf-label { font-size: 15px; font-weight: 600; color: #374151; }
  .conf-slider { width: 100%; height: 8px; -webkit-appearance: none; appearance: none; background: #e5e7eb; border-radius: 4px; outline: none; cursor: pointer; }
  .conf-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 20px; height: 20px; border-radius: 50%; background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); cursor: pointer; box-shadow: 0 2px 6px rgba(249, 115, 22, 0.4); }
  .conf-value { font-size: 18px; font-weight: 700; color: #f97316; text-align: center; }

  .btn { display: inline-flex; align-items: center; gap: 10px; padding: 13px 18px; border-radius: 10px; border: none; font-size: 17px; font-weight: 500; cursor: pointer; transition: all 0.15s ease; }
  .btn:disabled { opacity: 0.5; cursor: not-allowed; }
  .btn-primary { background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); color: #fff; }
  .btn-primary:hover:not(:disabled) { box-shadow: 0 4px 12px rgba(249, 115, 22, 0.35); transform: translateY(-1px); }
  .btn-secondary { background: #f3f4f6; color: #374151; border: 1px solid #e5e7eb; }
  .btn-secondary:hover:not(:disabled) { background: #e5e7eb; }
  .btn-danger { background: #fef2f2; color: #ef4444; border: 1px solid #fecaca; }
  .btn-danger:hover:not(:disabled) { background: #fee2e2; }
  .btn-ghost { background: transparent; color: #6b7280; }
  .btn-ghost:hover:not(:disabled) { color: #374151; background: #f3f4f6; }
  .btn-option { background: #f3f4f6; color: #374151; border: 1px solid #e5e7eb; min-width: 90px; }
  .btn-option:hover { background: #e5e7eb; }

  .info-section { display: flex; flex-direction: column; gap: 16px; }
  .result-card { padding-bottom: 16px; }
  .detection-stats { display: flex; justify-content: center; gap: 40px; padding: 24px; }
  .detection-stat { text-align: center; }
  .stat-circle { width: 76px; height: 76px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 10px; }
  .stat-circle.fire { background: #fef2f2; border: 2px solid #fecaca; }
  .stat-circle.smoke { background: #f3f4f6; border: 2px solid #e5e7eb; }
  .stat-num { font-size: 36px; font-weight: 700; }
  .stat-circle.fire .stat-num { color: #ef4444; }
  .stat-circle.smoke .stat-num { color: #6b7280; }
  .stat-name { font-size: 17px; color: #6b7280; }

  .detection-list { padding: 0 20px; max-height: 160px; overflow-y: auto; }
  .detection-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #f0f0f0; }
  .detection-item:last-child { border-bottom: none; }
  .det-tag { padding: 6px 14px; border-radius: 6px; font-size: 16px; font-weight: 500; }
  .det-tag.fire { background: #fef2f2; color: #ef4444; }
  .det-tag.smoke { background: #f3f4f6; color: #6b7280; }
  .det-conf { font-size: 17px; color: #6b7280; }
  .empty-state { text-align: center; padding: 24px; color: #9ca3af; font-size: 17px; }

  .tip-card { padding: 16px 18px; }
  .tip-text { font-size: 16px; color: #6b7280; line-height: 1.6; }
  </style>
