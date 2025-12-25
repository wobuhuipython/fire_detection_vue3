"""
火灾检测API服务
支持摄像头、视频、图片三种识别模式
包含用户评定功能、检测历史和帧缓存稳定显示
数据存储使用MySQL数据库
"""

import os
import sys

# PyTorch 2.6+ 安全加载问题的解决方案
import torch
_original_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _original_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from contextlib import asynccontextmanager
import asyncio
import json
import time
import cv2
import base64
import numpy as np
from pathlib import Path
from typing import Dict, Optional, List
from collections import deque
from ultralytics import YOLO
import uuid
from datetime import datetime
import pymysql
from dbutils.pooled_db import PooledDB

# 全局变量
model = None
MODEL_PATH = Path(r"E:\pytest\fire\weights\best.pt")

# 文件存储目录
data_dir = Path(__file__).parent / "data"
history_dir = data_dir / "history"
data_dir.mkdir(parents=True, exist_ok=True)
history_dir.mkdir(parents=True, exist_ok=True)

# MySQL数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',  # 请修改为你的MySQL密码
    'database': 'fire_detection',
    'charset': 'utf8mb4'
}

# 数据库连接池
db_pool = None

def log_message(message: str):
    """统一日志输出"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [API] {message}")

def init_database():
    """初始化数据库和表"""
    global db_pool
    try:
        # 先创建数据库（如果不存在）
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            charset=DB_CONFIG['charset']
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.close()
        
        # 创建连接池
        db_pool = PooledDB(
            creator=pymysql,
            maxconnections=10,
            mincached=2,
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset=DB_CONFIG['charset'],
            cursorclass=pymysql.cursors.DictCursor
        )
        
        # 创建表
        conn = db_pool.connection()
        cursor = conn.cursor()
        
        # 评定记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                id VARCHAR(36) PRIMARY KEY,
                detection_id VARCHAR(50),
                is_correct BOOLEAN,
                detection_type VARCHAR(100),
                source_type VARCHAR(20),
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 检测历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detection_history (
                id VARCHAR(36) PRIMARY KEY,
                source_type VARCHAR(20),
                image_path VARCHAR(255),
                fire_count INT DEFAULT 0,
                smoke_count INT DEFAULT 0,
                detection_count INT DEFAULT 0,
                detections JSON,
                processing_time FLOAT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        log_message("数据库初始化成功")
        return True
    except Exception as e:
        log_message(f"数据库初始化失败: {e}")
        return False

def get_db_connection():
    """获取数据库连接"""
    if db_pool:
        return db_pool.connection()
    return None

def init_model():
    """初始化火灾检测模型"""
    global model
    try:
        log_message(f"尝试加载模型: {MODEL_PATH}")
        if MODEL_PATH.exists():
            model = YOLO(str(MODEL_PATH))
            log_message(f"火灾检测模型加载成功")
            return True
        else:
            log_message(f"模型文件不存在: {MODEL_PATH}")
            return False
    except Exception as e:
        log_message(f"模型加载失败: {e}")
        return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    log_message("=" * 60)
    log_message("火灾检测API服务启动")
    log_message("=" * 60)
    init_database()
    init_model()
    yield
    log_message("火灾检测API服务关闭")

app = FastAPI(title="火灾检测API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务 - 用于访问检测历史图片
app.mount("/static/history", StaticFiles(directory=str(history_dir)), name="history")

# 前端静态文件目录
static_dir = Path(__file__).parent / "static"

def predict_frame(frame: np.ndarray, conf_threshold: float = 0.5) -> dict:
    """对单帧进行推理"""
    if model is None:
        return {"error": "模型未加载"}
    
    start_time = time.time()
    results = model(frame, conf=conf_threshold, verbose=False)
    processing_time = time.time() - start_time
    
    detections = []
    fire_count = 0
    smoke_count = 0
    
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                cls = int(box.cls[0].cpu().numpy())
                class_name = model.names[cls] if cls < len(model.names) else f"class_{cls}"
                
                if 'fire' in class_name.lower():
                    fire_count += 1
                elif 'smoke' in class_name.lower():
                    smoke_count += 1
                
                detections.append({
                    "bbox": [float(x1), float(y1), float(x2), float(y2)],
                    "confidence": conf,
                    "class_id": cls,
                    "class_name": class_name
                })
    
    return {
        "detections": detections,
        "fire_count": fire_count,
        "smoke_count": smoke_count,
        "detection_count": len(detections),
        "processing_time": processing_time,
        "image_size": {"width": frame.shape[1], "height": frame.shape[0]}
    }

def save_detection_history(frame: np.ndarray, result: dict, source_type: str) -> str:
    """保存检测历史到数据库和文件系统"""
    try:
        record_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{record_id[:8]}.jpg"
        filepath = history_dir / filename
        
        # 绘制检测框并保存图片
        vis_frame = frame.copy()
        for det in result["detections"]:
            x1, y1, x2, y2 = [int(v) for v in det["bbox"]]
            color = (0, 0, 255) if 'fire' in det["class_name"].lower() else (128, 128, 128)
            cv2.rectangle(vis_frame, (x1, y1), (x2, y2), color, 2)
            label = f"{det['class_name']} {det['confidence']:.2f}"
            cv2.putText(vis_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        cv2.imwrite(str(filepath), vis_frame)
        
        # 保存到数据库
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO detection_history 
                (id, source_type, image_path, fire_count, smoke_count, detection_count, detections, processing_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                record_id,
                source_type,
                filename,
                result.get("fire_count", 0),
                result.get("smoke_count", 0),
                result.get("detection_count", 0),
                json.dumps(result.get("detections", [])),
                result.get("processing_time", 0)
            ))
            conn.commit()
            conn.close()
            log_message(f"检测历史已保存: {filename}")
        
        return record_id
    except Exception as e:
        log_message(f"保存检测历史失败: {e}")
        return None

@app.get("/api/model/status")
async def model_status():
    return {
        "loaded": model is not None,
        "model_path": str(MODEL_PATH),
        "classes": list(model.names.values()) if model else []
    }


@app.post("/api/inference/image")
async def inference_image(
    file: UploadFile = File(...),
    conf_threshold: float = Form(default=0.5)
):
    """图片推理接口"""
    if model is None:
        raise HTTPException(status_code=500, detail="模型未加载")
    
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="无法解析图片")
        
        result = predict_frame(frame, conf_threshold)
        
        # 如果有检测结果，保存到历史
        if result["detection_count"] > 0:
            save_detection_history(frame, result, "image")
        
        # 绘制检测结果
        vis_frame = frame.copy()
        for det in result["detections"]:
            x1, y1, x2, y2 = [int(v) for v in det["bbox"]]
            color = (0, 0, 255) if 'fire' in det["class_name"].lower() else (128, 128, 128)
            cv2.rectangle(vis_frame, (x1, y1), (x2, y2), color, 2)
            label = f"{det['class_name']} {det['confidence']:.2f}"
            cv2.putText(vis_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        _, buffer = cv2.imencode('.jpg', vis_frame)
        vis_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return {
            "success": True,
            "result": result,
            "visualization": f"data:image/jpeg;base64,{vis_base64}"
        }
    except Exception as e:
        log_message(f"图片推理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/evaluation")
async def submit_evaluation(
    detection_id: str = Form(...),
    is_correct: bool = Form(...),
    detection_type: str = Form(...),
    source_type: str = Form(...),
    notes: str = Form(default="")
):
    """提交用户评定 - 保存到MySQL"""
    try:
        evaluation_id = str(uuid.uuid4())
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO evaluations (id, detection_id, is_correct, detection_type, source_type, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (evaluation_id, detection_id, is_correct, detection_type, source_type, notes))
            conn.commit()
            conn.close()
            
            log_message(f"收到评定: {detection_type} - {'正确' if is_correct else '错误'}")
            return {"success": True, "id": evaluation_id}
        else:
            raise HTTPException(status_code=500, detail="数据库连接失败")
    except Exception as e:
        log_message(f"保存评定失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/evaluations")
async def get_evaluations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100)
):
    """获取评定记录 - 从MySQL读取"""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # 获取总数
            cursor.execute("SELECT COUNT(*) as total FROM evaluations")
            total = cursor.fetchone()['total']
            
            # 分页查询
            offset = (page - 1) * page_size
            cursor.execute("""
                SELECT * FROM evaluations 
                ORDER BY created_at DESC 
                LIMIT %s OFFSET %s
            """, (page_size, offset))
            evaluations = cursor.fetchall()
            
            # 统计数据
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct,
                    SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END) as incorrect
                FROM evaluations
            """)
            stats = cursor.fetchone()
            conn.close()
            
            # 格式化日期
            for e in evaluations:
                if e.get('created_at'):
                    e['created_at'] = e['created_at'].isoformat()
            
            return {
                "evaluations": evaluations,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": (total + page_size - 1) // page_size
                },
                "statistics": {
                    "total": stats['total'] or 0,
                    "correct": stats['correct'] or 0,
                    "incorrect": stats['incorrect'] or 0,
                    "accuracy": (stats['correct'] / stats['total']) if stats['total'] > 0 else 0
                }
            }
        else:
            raise HTTPException(status_code=500, detail="数据库连接失败")
    except Exception as e:
        log_message(f"获取评定记录失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/evaluations/{evaluation_id}")
async def delete_evaluation(evaluation_id: str):
    """删除单条评定记录"""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM evaluations WHERE id = %s", (evaluation_id,))
            conn.commit()
            conn.close()
            return {"success": True}
        else:
            raise HTTPException(status_code=500, detail="数据库连接失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/evaluations")
async def clear_evaluations():
    """清空所有评定记录"""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM evaluations")
            conn.commit()
            conn.close()
            return {"success": True, "message": "评定数据已清空"}
        else:
            raise HTTPException(status_code=500, detail="数据库连接失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 检测历史API ====================

@app.get("/api/history")
async def get_detection_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    source_type: str = Query(default=None)
):
    """获取检测历史"""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # 构建查询条件
            where_clause = ""
            params = []
            if source_type:
                where_clause = "WHERE source_type = %s"
                params.append(source_type)
            
            # 获取总数
            cursor.execute(f"SELECT COUNT(*) as total FROM detection_history {where_clause}", params)
            total = cursor.fetchone()['total']
            
            # 分页查询
            offset = (page - 1) * page_size
            cursor.execute(f"""
                SELECT * FROM detection_history 
                {where_clause}
                ORDER BY created_at DESC 
                LIMIT %s OFFSET %s
            """, params + [page_size, offset])
            records = cursor.fetchall()
            conn.close()
            
            # 格式化数据
            for r in records:
                if r.get('created_at'):
                    r['created_at'] = r['created_at'].isoformat()
                if r.get('detections') and isinstance(r['detections'], str):
                    r['detections'] = json.loads(r['detections'])
                # 添加图片URL
                r['image_url'] = f"/static/history/{r['image_path']}"
            
            return {
                "records": records,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": (total + page_size - 1) // page_size
                }
            }
        else:
            raise HTTPException(status_code=500, detail="数据库连接失败")
    except Exception as e:
        log_message(f"获取检测历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/history/{record_id}")
async def delete_history_record(record_id: str):
    """删除单条检测历史"""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            # 先获取图片路径
            cursor.execute("SELECT image_path FROM detection_history WHERE id = %s", (record_id,))
            record = cursor.fetchone()
            if record:
                # 删除图片文件
                filepath = history_dir / record['image_path']
                if filepath.exists():
                    filepath.unlink()
                # 删除数据库记录
                cursor.execute("DELETE FROM detection_history WHERE id = %s", (record_id,))
                conn.commit()
            conn.close()
            return {"success": True}
        else:
            raise HTTPException(status_code=500, detail="数据库连接失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/history")
async def clear_history():
    """清空所有检测历史"""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM detection_history")
            conn.commit()
            conn.close()
            # 清空历史图片目录
            for f in history_dir.glob("*.jpg"):
                f.unlink()
            return {"success": True, "message": "检测历史已清空"}
        else:
            raise HTTPException(status_code=500, detail="数据库连接失败")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== WebSocket推理 ====================

class FrameBuffer:
    """帧缓存类 - 用于稳定检测结果显示"""
    def __init__(self, buffer_size: int = 3):
        self.buffer_size = buffer_size
        self.detection_history = deque(maxlen=buffer_size)
        self.last_save_time = 0
        self.save_interval = 5  # 每5秒最多保存一次
    
    def add_detection(self, detections: list) -> list:
        self.detection_history.append(detections)
        
        if len(self.detection_history) < self.buffer_size:
            return []
        
        stable_detections = []
        class_counts = {}
        
        for frame_dets in self.detection_history:
            for det in frame_dets:
                class_name = det["class_name"]
                if class_name not in class_counts:
                    class_counts[class_name] = {"count": 0, "latest": det}
                class_counts[class_name]["count"] += 1
                class_counts[class_name]["latest"] = det
        
        for class_name, data in class_counts.items():
            if data["count"] >= self.buffer_size:
                stable_detections.append(data["latest"])
        
        return stable_detections
    
    def should_save(self) -> bool:
        """检查是否应该保存（限制保存频率）"""
        current_time = time.time()
        if current_time - self.last_save_time >= self.save_interval:
            self.last_save_time = current_time
            return True
        return False

active_connections: Dict[str, WebSocket] = {}
frame_buffers: Dict[str, FrameBuffer] = {}

@app.websocket("/ws/inference")
async def websocket_inference(websocket: WebSocket):
    """WebSocket推理接口"""
    await websocket.accept()
    connection_id = str(uuid.uuid4())
    active_connections[connection_id] = websocket
    frame_buffers[connection_id] = FrameBuffer(buffer_size=3)
    
    log_message(f"WebSocket连接建立: {connection_id}")
    
    frame_count = 0
    last_fps_time = time.time()
    fps = 0
    
    try:
        await websocket.send_json({
            "type": "connected",
            "connection_id": connection_id
        })
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "frame":
                frame_count += 1
                
                current_time = time.time()
                if current_time - last_fps_time >= 1.0:
                    fps = frame_count
                    frame_count = 0
                    last_fps_time = current_time
                
                try:
                    img_data = base64.b64decode(message["data"])
                    nparr = np.frombuffer(img_data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    if frame is not None:
                        conf_threshold = message.get("conf_threshold", 0.5)
                        source_type = message.get("source_type", "camera")
                        result = predict_frame(frame, conf_threshold)
                        
                        buffer = frame_buffers[connection_id]
                        stable_detections = buffer.add_detection(result["detections"])
                        
                        # 如果有稳定检测结果且满足保存条件，保存到历史
                        if stable_detections and buffer.should_save():
                            save_detection_history(frame, {
                                **result,
                                "detections": stable_detections
                            }, source_type)
                        
                        result["stable_detections"] = stable_detections
                        result["fps"] = fps
                        
                        await websocket.send_json({
                            "type": "result",
                            "data": result
                        })
                except Exception as e:
                    log_message(f"帧处理错误: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
            
            elif message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        log_message(f"WebSocket断开: {connection_id}")
    except Exception as e:
        log_message(f"WebSocket错误: {e}")
    finally:
        if connection_id in active_connections:
            del active_connections[connection_id]
        if connection_id in frame_buffers:
            del frame_buffers[connection_id]

# ==================== 前端静态文件服务（必须放在最后）====================
# 挂载 assets 目录
assets_dir = static_dir / "assets"
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

@app.get("/")
async def serve_index():
    """首页"""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "火灾检测API服务运行中", "model_loaded": model is not None}

@app.get("/{path:path}")
async def serve_spa(path: str):
    """SPA 路由支持 - 必须放在所有路由最后"""
    # 跳过 API 和 WebSocket 路径
    if path.startswith("api/") or path.startswith("ws/") or path.startswith("static/"):
        raise HTTPException(status_code=404, detail="Not found")
    
    file_path = static_dir / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    
    # 返回 index.html 支持 SPA 路由
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="Not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
