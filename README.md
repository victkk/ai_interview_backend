# AI 面试系统后端

基于 FastAPI 开发的 AI 面试系统后端，支持实时视频流处理和 AI 分析功能。

## 功能特性

- 🎥 **实时视频流接收**: 通过 WebSocket 接收前端传输的实时视频流
- 🎤 **语音识别**: 使用 Whisper 模型将音频转换为文本
- 📊 **视频分析**: 表情识别、手势检测、眼神接触分析
- 🔄 **实时处理**: 异步处理视频流，实时返回分析结果
- 📝 **面试管理**: 完整的面试会话管理系统
- 🛠️ **模块化设计**: 清晰的代码架构，易于扩展

### 🚀 新增AI面试核心功能

- 🎭 **面试官角色生成**: 根据岗位和要求生成个性化面试官角色
- 📋 **智能题库生成**: 自动生成针对特定岗位的面试题库
- 💬 **动态追问系统**: 基于候选人回答智能生成追问问题
- 🎯 **多模态评估**: 综合文本、语音、视频进行全方位评估
- 📊 **智能报告生成**: 自动生成企业决策报告和候选人反馈报告
- 🛡️ **安全合规检查**: 全局安全监控，防偏见和隐私保护

## 技术栈

- **框架**: FastAPI 0.104.1
- **WebSocket**: 实时通信
- **视频处理**: FFmpeg
- **AI 模型**: Whisper (语音识别)
- **异步处理**: asyncio
- **日志系统**: Python logging

### 🔧 新增技术栈

- **AI 服务**: OpenAI GPT-4o-mini / Azure OpenAI
- **Prompt 管理**: 基于 JSON 的模板系统
- **HTTP 客户端**: aiohttp (异步HTTP请求)
- **重试机制**: tenacity (智能重试策略)
- **数据验证**: Pydantic (类型安全和数据验证)
- **多模态处理**: 文本、语音、视频综合分析

## 项目结构

```
ai_interview_backend/
├── main.py                 # 主应用入口
├── requirements.txt        # 项目依赖
├── README.md              # 项目文档
├── data/                  # 数据存储
│   └── prompts.json       # Prompt模板存储
├── config/                # 配置文件
│   └── ai_config.json     # AI服务配置
├── models/                # 数据模型
│   ├── __init__.py
│   └── schemas.py         # Pydantic数据模型(已扩展)
├── routers/               # 路由处理
│   ├── __init__.py
│   ├── interview.py       # 面试管理路由(已扩展)
│   └── ai_processing.py   # AI处理路由(已扩展)
├── services/              # 业务逻辑
│   ├── __init__.py
│   ├── websocket_manager.py    # WebSocket连接管理
│   ├── interview_session.py    # 面试会话管理(已扩展)
│   ├── audio_processor.py      # 音频处理服务
│   ├── ai_service.py          # AI模型调用服务(已扩展)
│   ├── prompt_manager.py      # Prompt模板管理(新增)
│   └── openai_client.py       # OpenAI客户端(新增)
└── utils/                 # 工具函数
    ├── __init__.py
    ├── logger.py          # 日志配置
    └── util.py            # 通用工具函数
```

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 AI 服务

在 `config/ai_config.json` 中配置 OpenAI API：

```json
{
  "openai": {
    "api_key": "your-openai-api-key-here",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-4o-mini"
  }
}
```

或者设置环境变量：

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### 3. 启动服务

```bash
python main.py
```

或使用 uvicorn 直接运行：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问 API 文档

启动后访问 `http://localhost:8000/docs` 查看自动生成的 API 文档。

## 主要接口

### 面试管理

- `POST /api/interview/start` - 开始新的面试会话
- `GET /api/interview/session/{session_id}` - 获取面试会话信息
- `PUT /api/interview/session/{session_id}/status` - 更新会话状态
- `GET /api/interview/sessions` - 获取面试会话列表
- `GET /api/interview/results/{session_id}` - 获取面试结果

#### 🆕 新增面试管理接口

- `POST /api/interview/session/{session_id}/question` - 设置当前面试问题
- `POST /api/interview/session/{session_id}/persona` - 设置面试官角色
- `GET /api/interview/session/{session_id}/summary` - 获取面试摘要信息
- `POST /api/interview/session/{session_id}/final-report` - 生成最终面试报告

### AI 处理

- `POST /api/ai/transcribe` - 文件语音识别
- `POST /api/ai/analyze-video` - 视频分析
- `POST /api/ai/detect-emotions` - 情感检测
- `POST /api/ai/analyze-speech-quality` - 语音质量分析
- `GET /api/ai/models/status` - 获取模型状态

#### 🆕 新增AI核心功能接口

- `POST /api/ai/interviewer-persona` - 生成面试官角色
- `POST /api/ai/question-bank` - 生成岗位面试题库
- `POST /api/ai/follow-up` - 生成动态追问问题
- `POST /api/ai/multimodal-evaluation` - 多模态表现评估
- `POST /api/ai/interview-report` - 生成最终面试报告
- `POST /api/ai/safety-check` - 安全合规检查
- `POST /api/ai/batch-process` - 批量处理请求
- `GET /api/ai/health` - AI服务健康检查

### WebSocket

- `ws://localhost:8000/ws/video/{session_id}` - 实时视频流传输
- `ws://localhost:8000/ws/audio/{session_id}` - 实时音频流传输

## 使用示例

### 1. 创建面试会话

```bash
curl -X POST "http://localhost:8000/api/interview/start" \
     -H "Content-Type: application/json" \
     -d '{"user_id": "user123", "metadata": {"position": "前端工程师"}}'
```

### 2. WebSocket 连接（JavaScript）

```javascript
const sessionId = "your-session-id";
const ws = new WebSocket(`ws://localhost:8000/ws/video-stream/${sessionId}`);

ws.onopen = function (event) {
  console.log("WebSocket连接已建立");
};

ws.onmessage = function (event) {
  const data = JSON.parse(event.data);
  console.log("收到消息:", data);
};

// 发送视频数据
function sendVideoData(videoBlob) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(videoBlob);
  }
}
```

### 3. 文件上传语音识别

```bash
curl -X POST "http://localhost:8000/api/ai/transcribe" \
     -F "session_id=your-session-id" \
     -F "language=zh" \
     -F "audio_file=@audio.wav"
```

### 4. 🆕 AI面试功能使用示例

#### 生成面试官角色

```bash
curl -X POST "http://localhost:8000/api/ai/interviewer-persona" \
     -H "Content-Type: application/json" \
     -d '{
       "job_position": "高级前端工程师",
       "key_focus_areas": ["技术深度", "项目经验", "团队协作"],
       "personality_style": "专业严谨",
       "interviewer_name": "张经理"
     }'
```

#### 生成面试题库

```bash
curl -X POST "http://localhost:8000/api/ai/question-bank" \
     -H "Content-Type: application/json" \
     -d '{
       "job_position": "高级前端工程师",
       "technical_field": "前端开发",
       "core_competency_indicators": ["专业知识水平", "逻辑思维能力", "项目经验"]
     }'
```

#### 生成追问问题

```bash
curl -X POST "http://localhost:8000/api/ai/follow-up" \
     -H "Content-Type: application/json" \
     -d '{
       "original_question": "请介绍一下你做过的最复杂的项目",
       "candidate_answer": "我做过一个电商网站，使用了React",
       "target_competency": "项目经验",
       "interviewer_persona": "专业严谨"
     }'
```

#### 多模态评估

```bash
curl -X POST "http://localhost:8000/api/ai/multimodal-evaluation" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "请介绍一下你的项目经验",
       "evaluation_indicators": ["专业知识水平", "语言表达能力", "逻辑思维能力"],
       "text_analysis": {
         "transcript": "我主要负责前端开发，使用React和Vue框架",
         "keywords_coverage": 0.8,
         "answer_structure": "结构清晰，逻辑完整"
       },
       "audio_analysis": {
         "avg_speech_rate": "150字/分钟",
         "sentiment_tone": "自信",
         "pauses_and_fillers": "适量停顿"
       },
       "video_analysis": {
         "eye_contact_level": "良好",
         "micro_expressions": ["自信", "思考"],
         "body_language": "坐姿端正"
       }
     }'
```

## AI 模型集成

### Whisper 语音识别

```python
# 当前为模拟实现，实际集成时替换为：
import whisper

class AIService:
    def __init__(self):
        self.whisper_model = whisper.load_model("base")

    async def transcribe_audio(self, audio_data, session_id, language="zh"):
        # 使用真实的Whisper模型
        result = self.whisper_model.transcribe(audio_data, language=language)
        return WhisperResponse(
            text=result["text"],
            language=result["language"],
            segments=result["segments"],
            confidence=1.0  # Whisper不直接提供置信度
        )
```

### 视频分析模型

```python
# 集成其他AI模型，如OpenCV、MediaPipe等
import cv2
import mediapipe as mp

class VideoProcessor:
    def __init__(self):
        self.face_detection = mp.solutions.face_detection.FaceDetection()
        self.pose = mp.solutions.pose.Pose()

    async def analyze_video_frame(self, frame):
        # 人脸检测
        face_results = self.face_detection.process(frame)

        # 姿态检测
        pose_results = self.pose.process(frame)

        return {
            "faces": face_results,
            "pose": pose_results
        }
```

## 日志系统

系统自动在 `logs/` 目录下生成日志文件：

- `ai_interview_YYYYMMDD.log` - 详细日志
- `error_YYYYMMDD.log` - 错误日志

日志级别：

- DEBUG: 详细调试信息
- INFO: 一般信息
- WARNING: 警告信息
- ERROR: 错误信息

## 配置说明

### 环境变量

可以通过环境变量配置以下参数：

```bash
# 服务器配置
export HOST=0.0.0.0
export PORT=8000

# 日志级别
export LOG_LEVEL=INFO

# AI模型配置
export WHISPER_MODEL=base
export MODEL_CACHE_DIR=./models
```

## 扩展开发

### 添加新的 AI 模型

1. 在 `services/ai_service.py` 中添加新的模型加载和调用方法
2. 在 `models/schemas.py` 中定义相应的请求和响应模型
3. 在 `routers/ai_processing.py` 中添加新的 API 端点

### 添加新的路由

1. 在 `routers/` 目录下创建新的路由文件
2. 在 `main.py` 中注册新的路由
3. 更新相应的数据模型

## 性能优化

- 使用异步处理避免阻塞
- WebSocket 连接池管理
- 视频流缓存策略
- AI 模型预加载
- 日志轮转机制

## 部署建议

### Docker 部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 生产环境配置

- 使用 Gunicorn + Uvicorn workers
- 配置反向代理（Nginx）
- 设置 SSL 证书
- 配置数据库（PostgreSQL/MongoDB）
- 添加 Redis 缓存

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请创建 Issue 或联系项目维护者。
