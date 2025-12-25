<template>
  <div class="evaluation-container">
    <header class="page-header">
      <div>
        <h1 class="page-title">评定记录</h1>
        <p class="page-desc">查看历史检测结果的评定数据</p>
      </div>
      <button class="btn btn-danger" @click="clearEvaluations" :disabled="evaluations.length === 0">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
          <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
        </svg>
        清空记录
      </button>
    </header>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor">
            <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
          </svg>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ statistics.total }}</span>
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
          <span class="stat-value correct">{{ statistics.correct }}</span>
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
          <span class="stat-value incorrect">{{ statistics.incorrect }}</span>
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
          <span class="stat-value accuracy">{{ (statistics.accuracy * 100).toFixed(1) }}%</span>
          <span class="stat-label">准确率</span>
        </div>
      </div>
    </div>

    <div class="table-card">
      <div class="table-header">
        <span class="table-title">评定列表</span>
        <span class="table-count">共 {{ evaluations.length }} 条记录</span>
      </div>
      <div class="table-wrapper">
        <table class="data-table" v-if="evaluations.length > 0">
          <thead>
            <tr>
              <th>时间</th>
              <th>来源</th>
              <th>检测类型</th>
              <th>评定结果</th>
              <th>备注</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in evaluations" :key="item.id">
              <td class="time-cell">{{ formatTime(item.timestamp) }}</td>
              <td><span class="source-tag" :class="item.source_type">{{ getSourceLabel(item.source_type) }}</span></td>
              <td class="type-cell">{{ item.detection_type || '-' }}</td>
              <td><span class="result-tag" :class="item.is_correct ? 'correct' : 'incorrect'">{{ item.is_correct ? '正确' : '错误' }}</span></td>
              <td class="notes-cell">{{ item.notes || '-' }}</td>
            </tr>
          </tbody>
        </table>
        <div v-else class="empty-state">
          <svg viewBox="0 0 24 24" width="48" height="48" fill="currentColor">
            <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
          </svg>
          <p>暂无评定记录</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const evaluations = ref([])
const statistics = ref({ total: 0, correct: 0, incorrect: 0, accuracy: 0 })

const loadEvaluations = async () => {
  try {
    const res = await axios.get('/api/evaluations')
    evaluations.value = res.data.evaluations.reverse()
    statistics.value = res.data.statistics
  } catch { ElMessage.error('加载评定记录失败') }
}

const clearEvaluations = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有评定记录吗?', '确认', { type: 'warning' })
    await axios.delete('/api/evaluations')
    evaluations.value = []
    statistics.value = { total: 0, correct: 0, incorrect: 0, accuracy: 0 }
    ElMessage.success('评定记录已清空')
  } catch (e) { if (e !== 'cancel') ElMessage.error('清空失败') }
}

const formatTime = (ts) => ts ? new Date(ts).toLocaleString('zh-CN') : '-'
const getSourceLabel = (s) => ({ camera: '摄像头', video: '视频', image: '图片' }[s] || s)

onMounted(() => loadEvaluations())
</script>

<style scoped>
.evaluation-container { max-width: 1200px; margin: 0 auto; }

.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.page-title { font-size: 36px; font-weight: 700; color: #1f2937; margin-bottom: 10px; }
.page-desc { font-size: 18px; color: #6b7280; }

.btn { display: inline-flex; align-items: center; gap: 10px; padding: 13px 18px; border-radius: 10px; border: none; font-size: 17px; font-weight: 500; cursor: pointer; transition: all 0.15s ease; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-danger { background: #fef2f2; color: #ef4444; border: 1px solid #fecaca; }
.btn-danger:hover:not(:disabled) { background: #fee2e2; }

.stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 24px; }

.stat-card {
  background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 18px;
  display: flex; align-items: center; gap: 14px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.stat-icon { width: 46px; height: 46px; border-radius: 10px; display: flex; align-items: center; justify-content: center; }
.stat-icon.total { background: #eef2ff; color: #6366f1; }
.stat-icon.correct { background: #ecfdf5; color: #10b981; }
.stat-icon.incorrect { background: #fef2f2; color: #ef4444; }
.stat-icon.accuracy { background: #eff6ff; color: #3b82f6; }

.stat-info { display: flex; flex-direction: column; }
.stat-value { font-size: 34px; font-weight: 700; color: #1f2937; }
.stat-value.correct { color: #10b981; }
.stat-value.incorrect { color: #ef4444; }
.stat-value.accuracy { color: #3b82f6; }
.stat-label { font-size: 17px; color: #6b7280; margin-top: 4px; }

.table-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04); overflow: hidden; }

.table-header { padding: 14px 18px; border-bottom: 1px solid #f0f0f0; display: flex; justify-content: space-between; align-items: center; }
.table-title { font-size: 20px; font-weight: 600; color: #1f2937; }
.table-count { font-size: 17px; color: #9ca3af; }

.table-wrapper { overflow-x: auto; }

.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: 12px 18px; text-align: left; border-bottom: 1px solid #f0f0f0; }
.data-table th { font-size: 15px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; background: #f9fafb; }
.data-table td { font-size: 17px; color: #374151; }
.data-table tr:hover td { background: #fafafa; }
.data-table tr:last-child td { border-bottom: none; }

.time-cell { color: #6b7280; font-size: 16px; }
.type-cell { max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.notes-cell { max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: #6b7280; }

.source-tag { padding: 6px 14px; border-radius: 6px; font-size: 16px; font-weight: 500; }
.source-tag.camera { background: #f3e8ff; color: #9333ea; }
.source-tag.video { background: #fce7f3; color: #db2777; }
.source-tag.image { background: #cffafe; color: #0891b2; }

.result-tag { padding: 6px 14px; border-radius: 6px; font-size: 16px; font-weight: 500; }
.result-tag.correct { background: #ecfdf5; color: #10b981; }
.result-tag.incorrect { background: #fef2f2; color: #ef4444; }

.empty-state { padding: 60px 20px; text-align: center; color: #9ca3af; }
.empty-state svg { margin-bottom: 12px; }
.empty-state p { font-size: 18px; }
</style>
