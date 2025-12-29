<template>
  <div class="history-container">
    <header class="page-header">
      <h1 class="page-title">检测历史</h1>
      <p class="page-desc">查看所有检测到火灾/烟雾的历史记录，并进行评定</p>
    </header>

    <div class="toolbar">
      <div class="filter-group">
        <button class="filter-btn" :class="{ active: filterType === '' }" @click="filterType = ''; loadHistory()">全部</button>
        <button class="filter-btn" :class="{ active: filterType === 'camera' }" @click="filterType = 'camera'; loadHistory()">摄像头</button>
        <button class="filter-btn" :class="{ active: filterType === 'video' }" @click="filterType = 'video'; loadHistory()">视频</button>
        <button class="filter-btn" :class="{ active: filterType === 'image' }" @click="filterType = 'image'; loadHistory()">图片</button>
      </div>
      <button class="btn btn-danger" @click="clearHistory" :disabled="records.length === 0">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
          <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
        </svg>
        清空历史
      </button>
    </div>

    <div class="history-grid" v-if="records.length > 0">
      <div class="history-card" v-for="record in records" :key="record.id">
        <div class="card-image" @click="showPreview(record)">
          <img :src="getImageUrl(record.image_path)" :alt="record.id" />
          <div class="image-overlay">
            <svg viewBox="0 0 24 24" width="32" height="32" fill="currentColor">
              <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
            </svg>
          </div>
          <!-- 评定状态标签 -->
          <div class="eval-badge" v-if="record.is_evaluated" :class="record.is_correct ? 'correct' : 'incorrect'">
            {{ record.is_correct ? '✓ 正确' : '✗ 错误' }}
          </div>
        </div>
        <div class="card-content">
          <div class="card-stats">
            <span class="stat fire" v-if="record.fire_count > 0">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                <path d="M13.5.67s.74 2.65.74 4.8c0 2.06-1.35 3.73-3.41 3.73-2.07 0-3.63-1.67-3.63-3.73l.03-.36C5.21 7.51 4 10.62 4 14c0 4.42 3.58 8 8 8s8-3.58 8-8C20 8.61 17.41 3.8 13.5.67zM11.71 19c-1.78 0-3.22-1.4-3.22-3.14 0-1.62 1.05-2.76 2.81-3.12 1.77-.36 3.6-1.21 4.62-2.58.39 1.29.59 2.65.59 4.04 0 2.65-2.15 4.8-4.8 4.8z"/>
              </svg>
              火焰 {{ record.fire_count }}
            </span>
            <span class="stat smoke" v-if="record.smoke_count > 0">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                <path d="M19.48 12.35c-1.57-4.08-7.16-4.3-5.81-10.23.1-.44-.37-.78-.75-.55C9.29 3.71 6.68 8 8.87 13.62c.18.46-.36.89-.75.59-1.81-1.37-2-3.34-1.84-4.75.06-.52-.62-.77-.91-.34C4.69 10.16 4 11.84 4 14.37c.38 5.6 5.11 7.32 6.81 7.54 2.43.31 5.06-.14 6.95-1.87 2.08-1.93 2.84-5.01 1.72-7.69zm-9.28 5.03c1.44-.35 2.18-1.39 2.38-2.31.33-1.43-.96-2.83-.09-5.09.33 1.87 3.27 3.04 3.27 5.08.08 2.53-2.66 4.7-5.56 2.32z"/>
              </svg>
              烟雾 {{ record.smoke_count }}
            </span>
          </div>
          <div class="card-meta">
            <span class="source-tag" :class="record.source_type">{{ getSourceLabel(record.source_type) }}</span>
            <span class="time">{{ formatTime(record.created_at) }}</span>
          </div>
          <!-- 评定按钮 -->
          <div class="eval-actions" v-if="!record.is_evaluated">
            <button class="eval-btn correct" @click.stop="submitEvaluation(record, true)" title="标记为正确">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
            </button>
            <button class="eval-btn incorrect" @click.stop="submitEvaluation(record, false)" title="标记为错误">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
            </button>
          </div>
          <button class="delete-btn" @click.stop="deleteRecord(record.id)">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
              <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <div class="empty-state" v-else>
      <svg viewBox="0 0 24 24" width="64" height="64" fill="currentColor">
        <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zm-5-7l-3 3.72L9 13l-3 4h12l-4-5z"/>
      </svg>
      <p>暂无检测历史记录</p>
    </div>

    <div class="pagination" v-if="pagination.total_pages > 1">
      <button class="page-btn" :disabled="pagination.page <= 1" @click="goPage(pagination.page - 1)">上一页</button>
      <span class="page-info">{{ pagination.page }} / {{ pagination.total_pages }}</span>
      <button class="page-btn" :disabled="pagination.page >= pagination.total_pages" @click="goPage(pagination.page + 1)">下一页</button>
    </div>

    <!-- 图片预览弹窗 -->
    <div class="preview-modal" v-if="previewRecord" @click="previewRecord = null">
      <div class="preview-content" @click.stop>
        <img :src="getImageUrl(previewRecord.image_path)" />
        <div class="preview-info">
          <h3>检测详情</h3>
          <p><strong>来源:</strong> {{ getSourceLabel(previewRecord.source_type) }}</p>
          <p><strong>时间:</strong> {{ formatTime(previewRecord.created_at) }}</p>
          <p><strong>火焰数量:</strong> {{ previewRecord.fire_count }}</p>
          <p><strong>烟雾数量:</strong> {{ previewRecord.smoke_count }}</p>
          <p><strong>处理时间:</strong> {{ (previewRecord.processing_time * 1000).toFixed(0) }}ms</p>
          <div class="preview-eval" v-if="!previewRecord.is_evaluated">
            <p><strong>评定结果:</strong></p>
            <div class="preview-eval-btns">
              <button class="btn btn-success" @click="submitEvaluation(previewRecord, true)">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
                正确
              </button>
              <button class="btn btn-error" @click="submitEvaluation(previewRecord, false)">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
                错误
              </button>
            </div>
          </div>
          <div class="preview-eval-result" v-else>
            <p><strong>评定结果:</strong> 
              <span :class="previewRecord.is_correct ? 'correct' : 'incorrect'">
                {{ previewRecord.is_correct ? '正确' : '错误' }}
              </span>
            </p>
          </div>
        </div>
        <button class="close-btn" @click="previewRecord = null">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const records = ref([])
const pagination = ref({ page: 1, page_size: 20, total: 0, total_pages: 0 })
const filterType = ref('')
const previewRecord = ref(null)

const loadHistory = async (page = 1) => {
  try {
    const params = { page, page_size: 20 }
    if (filterType.value) params.source_type = filterType.value
    
    const res = await axios.get('/api/history', { params })
    records.value = res.data.records
    pagination.value = res.data.pagination
  } catch (e) {
    ElMessage.error('加载历史记录失败')
  }
}

const submitEvaluation = async (record, isCorrect) => {
  try {
    const fd = new FormData()
    fd.append('detection_id', record.id)
    fd.append('is_correct', isCorrect)
    fd.append('detection_type', record.detections?.map(d => d.class_name).join(',') || '')
    fd.append('source_type', record.source_type)
    fd.append('notes', '')
    
    await axios.post('/api/evaluation', fd)
    
    // 更新本地状态
    record.is_evaluated = true
    record.is_correct = isCorrect
    
    ElMessage.success('评定提交成功')
  } catch (e) {
    ElMessage.error('评定提交失败')
  }
}

const deleteRecord = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除这条记录吗？', '确认删除', { type: 'warning' })
    await axios.delete(`/api/history/${id}`)
    ElMessage.success('删除成功')
    loadHistory(pagination.value.page)
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

const clearHistory = async () => {
  try {
    await ElMessageBox.confirm('确定清空所有检测历史吗？此操作不可恢复！', '确认清空', { type: 'warning' })
    await axios.delete('/api/history')
    ElMessage.success('历史记录已清空')
    loadHistory()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('清空失败')
  }
}

const goPage = (page) => loadHistory(page)
const showPreview = (record) => { previewRecord.value = record }
const getImageUrl = (path) => `/static/history/${path}`
const getSourceLabel = (type) => ({ camera: '摄像头', video: '视频', image: '图片' }[type] || type)
const formatTime = (isoString) => isoString ? new Date(isoString).toLocaleString('zh-CN') : ''

onMounted(() => loadHistory())
</script>


<style scoped>
.history-container { max-width: 1400px; margin: 0 auto; }
.page-header { margin-bottom: 24px; }
.page-title { font-size: 36px; font-weight: 700; color: #1f2937; margin-bottom: 10px; }
.page-desc { font-size: 18px; color: #6b7280; }

.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; padding: 16px 20px; background: #fff; border-radius: 12px; border: 1px solid #e5e7eb; }
.filter-group { display: flex; gap: 8px; }
.filter-btn { padding: 10px 20px; border: 1px solid #e5e7eb; background: #fff; border-radius: 8px; font-size: 16px; color: #6b7280; cursor: pointer; transition: all 0.15s; }
.filter-btn:hover { background: #f9fafb; }
.filter-btn.active { background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); color: #fff; border-color: transparent; }

.btn { display: inline-flex; align-items: center; gap: 8px; padding: 12px 20px; border-radius: 10px; border: none; font-size: 16px; font-weight: 500; cursor: pointer; transition: all 0.15s; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-danger { background: #fef2f2; color: #ef4444; border: 1px solid #fecaca; }
.btn-danger:hover:not(:disabled) { background: #fee2e2; }
.btn-success { background: #ecfdf5; color: #10b981; border: 1px solid #a7f3d0; }
.btn-success:hover:not(:disabled) { background: #d1fae5; }
.btn-error { background: #fef2f2; color: #ef4444; border: 1px solid #fecaca; }
.btn-error:hover:not(:disabled) { background: #fee2e2; }

.history-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
.history-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; overflow: hidden; transition: all 0.2s; }
.history-card:hover { box-shadow: 0 8px 24px rgba(0,0,0,0.1); transform: translateY(-2px); }

.card-image { position: relative; aspect-ratio: 16/10; overflow: hidden; cursor: pointer; }
.card-image img { width: 100%; height: 100%; object-fit: cover; }
.image-overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.2s; color: #fff; }
.card-image:hover .image-overlay { opacity: 1; }

.eval-badge { position: absolute; top: 10px; right: 10px; padding: 4px 10px; border-radius: 6px; font-size: 13px; font-weight: 600; }
.eval-badge.correct { background: #ecfdf5; color: #10b981; }
.eval-badge.incorrect { background: #fef2f2; color: #ef4444; }

.card-content { padding: 14px 16px; position: relative; }
.card-stats { display: flex; gap: 12px; margin-bottom: 10px; }
.stat { display: inline-flex; align-items: center; gap: 4px; padding: 4px 10px; border-radius: 6px; font-size: 14px; font-weight: 500; }
.stat.fire { background: #fef2f2; color: #ef4444; }
.stat.smoke { background: #f3f4f6; color: #6b7280; }

.card-meta { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.source-tag { padding: 4px 10px; border-radius: 6px; font-size: 13px; font-weight: 500; }
.source-tag.camera { background: #ecfdf5; color: #10b981; }
.source-tag.video { background: #eff6ff; color: #3b82f6; }
.source-tag.image { background: #fef3c7; color: #d97706; }
.time { font-size: 13px; color: #9ca3af; }

.eval-actions { display: flex; gap: 8px; }
.eval-btn { width: 32px; height: 32px; border: none; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.15s; }
.eval-btn.correct { background: #ecfdf5; color: #10b981; }
.eval-btn.correct:hover { background: #d1fae5; }
.eval-btn.incorrect { background: #fef2f2; color: #ef4444; }
.eval-btn.incorrect:hover { background: #fee2e2; }

.delete-btn { position: absolute; top: 12px; right: 12px; width: 28px; height: 28px; border: none; background: #fef2f2; color: #ef4444; border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.2s; }
.history-card:hover .delete-btn { opacity: 1; }
.delete-btn:hover { background: #fee2e2; }

.empty-state { text-align: center; padding: 80px 20px; color: #9ca3af; }
.empty-state svg { margin-bottom: 16px; }
.empty-state p { font-size: 18px; }

.pagination { display: flex; justify-content: center; align-items: center; gap: 16px; margin-top: 32px; }
.page-btn { padding: 10px 20px; border: 1px solid #e5e7eb; background: #fff; border-radius: 8px; font-size: 15px; cursor: pointer; transition: all 0.15s; }
.page-btn:hover:not(:disabled) { background: #f9fafb; }
.page-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.page-info { font-size: 15px; color: #6b7280; }

.preview-modal { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: flex; align-items: center; justify-content: center; z-index: 2000; }
.preview-content { position: relative; max-width: 90%; max-height: 90%; background: #fff; border-radius: 16px; overflow: hidden; display: flex; }
.preview-content img { max-width: 70%; max-height: 80vh; object-fit: contain; }
.preview-info { padding: 24px; min-width: 280px; }
.preview-info h3 { font-size: 20px; font-weight: 600; color: #1f2937; margin-bottom: 16px; }
.preview-info p { font-size: 15px; color: #6b7280; margin-bottom: 10px; }
.preview-info strong { color: #374151; }

.preview-eval { margin-top: 20px; padding-top: 16px; border-top: 1px solid #e5e7eb; }
.preview-eval-btns { display: flex; gap: 10px; margin-top: 12px; }
.preview-eval-result { margin-top: 20px; padding-top: 16px; border-top: 1px solid #e5e7eb; }
.preview-eval-result .correct { color: #10b981; font-weight: 600; }
.preview-eval-result .incorrect { color: #ef4444; font-weight: 600; }

.close-btn { position: absolute; top: 12px; right: 12px; width: 36px; height: 36px; border: none; background: rgba(0,0,0,0.5); color: #fff; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; }
.close-btn:hover { background: rgba(0,0,0,0.7); }
</style>
