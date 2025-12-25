# 火灾检测系统

基于 Vue3 + FastAPI + YOLO 的火灾烟雾检测平台

## 功能特性

- 摄像头实时检测
- 视频文件检测
- 图片检测
- 用户评定功能
- 帧缓存稳定显示（连续3帧才显示）
- FPS 实时显示

## 项目结构

```
fire-detection-platform/
├── backend/           # 后端 FastAPI 服务
│   ├── api_server.py  # API 服务主文件
│   ├── requirements.txt
│   └── data/          # 数据存储目录
├── frontend/          # 前端 Vue3 项目
│   ├── src/
│   │   ├── views/     # 页面组件
│   │   ├── router/    # 路由配置
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 启动方式

### 1. 启动后端服务

```bash
cd fire-detection-platform/backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
python api_server.py
```

后端服务将在 http://localhost:8000 运行

### 2. 启动前端服务

```bash
cd fire-detection-platform/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:5173 运行

## 模型路径

系统默认使用 `E:\pytest\fire\weights\best.pt` 作为检测模型

## 技术栈

- 前端: Vue 3 + Element Plus + Vite
- 后端: FastAPI + Ultralytics YOLO
- 通信: WebSocket (实时检测) + REST API (图片检测)
