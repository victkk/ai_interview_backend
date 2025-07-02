# WebSocket 接口说明文档

## 概述

本文档描述了 AI 面试系统后端提供的 WebSocket 接口，用于实时视频流传输和 AI 处理。

## 基本信息

- **协议**: WebSocket
- **端点**: `/ws/video-stream/{session_id}`
- **服务地址**: `ws://localhost:8000` (开发环境)
- **连接方式**: 长连接，支持双向通信

## 连接建立

### 端点格式

```
ws://服务器地址/ws/video-stream/{session_id}
```

### 路径参数

- `session_id` (必需): 面试会话 ID，用于标识唯一的面试会话

### 连接流程

1. 客户端发起 WebSocket 连接请求
2. 服务器接受连接并发送连接确认消息
3. 开始数据传输和处理

## 消息格式

### 发送消息（客户端 -> 服务器）

#### 视频数据传输

- **数据类型**: 二进制数据 (bytes)
- **内容**: 视频流的字节数据
- **格式**: 支持 webm 等格式
- **发送方式**: 使用 `websocket.send(bytes)` 或类似方法

### 接收消息（服务器 -> 客户端）

所有接收的消息都是 JSON 格式，包含以下基本字段：

```json
{
  "type": "消息类型",
  "session_id": "会话ID",
  "timestamp": "时间戳",
  "message": "消息内容",
  "data": {}
}
```

## 消息类型

### 1. 连接确认消息

**类型**: `connection_established`

```json
{
  "type": "connection_established",
  "session_id": "会话ID",
  "message": "连接已建立，可以开始传输视频流"
}
```

### 2. 视频数据接收确认

**类型**: `video_data_received`

```json
{
  "type": "video_data_received",
  "session_id": "会话ID",
  "data_size": 1024,
  "timestamp": "2024-01-01T12:00:00"
}
```

### 3. 处理状态更新

**类型**: `status`

```json
{
  "status": "processing",
  "message": "视频数据处理中",
  "data_size": 1024
}
```

### 4. 语音转录结果

**类型**: `transcription_result`

```json
{
  "type": "transcription_result",
  "session_id": "会话ID",
  "result": {
    "text": "转录的文本内容",
    "language": "zh",
    "confidence": 0.95,
    "segments": []
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

### 5. 视频分析结果

**类型**: `video_analysis_result`

```json
{
  "type": "video_analysis_result",
  "session_id": "会话ID",
  "result": {
    "emotions": [],
    "gestures": [],
    "eye_contact": 0.8,
    "posture_score": 0.7
  },
  "timestamp": "2024-01-01T12:00:00"
}
```

### 6. 错误消息

**类型**: `error`

```json
{
  "type": "error",
  "session_id": "会话ID",
  "message": "错误描述",
  "error_code": "ERROR_CODE"
}
```

## 连接管理

### 连接状态

- `connected`: 连接已建立
- `processing`: 数据处理中
- `disconnected`: 连接已断开

### 自动断开条件

- 网络异常
- 数据传输错误
- 服务器主动断开
- 会话超时

### 重连机制

客户端应实现重连逻辑：

- 监听连接断开事件
- 实现指数退避重连策略
- 保存会话状态以便重连后恢复

## 数据传输规范

### 视频数据要求

- **格式**: 推荐使用 WebM 格式
- **编码**: VP8/VP9 视频编码，Opus 音频编码
- **分块**: 建议每个数据块大小不超过 64KB
- **频率**: 根据网络条件调整发送频率

### 传输注意事项

- 按顺序发送视频数据块
- 确保数据完整性
- 监控网络状况，适时调整传输策略
- 处理背压（backpressure）情况

## 错误处理

### 常见错误类型

1. **连接错误**: 无法建立 WebSocket 连接
2. **认证错误**: session_id 无效或过期
3. **数据格式错误**: 发送的数据格式不正确
4. **处理错误**: 服务器处理视频数据时发生错误
5. **网络错误**: 网络中断或超时

### 错误处理建议

- 实现完整的错误处理逻辑
- 向用户显示友好的错误信息
- 记录详细的错误日志
- 在适当的情况下自动重试

## 性能优化建议

### 客户端优化

- 实现数据缓冲机制
- 根据网络状况动态调整视频质量
- 使用 Web Workers 处理大量数据
- 实现流量控制避免内存溢出

### 网络优化

- 启用数据压缩
- 使用 CDN 加速连接
- 监控连接延迟和带宽
- 实现自适应码率

## 安全考虑

### 数据安全

- 所有视频数据在传输过程中应加密
- 验证 session_id 的有效性
- 防止会话劫持

### 访问控制

- 确保只有授权用户可以建立连接
- 实现适当的权限检查
- 防止未授权访问

## 调试和监控

### 调试方法

- 使用浏览器开发者工具监控 WebSocket 连接
- 检查网络选项卡中的 WebSocket 帧
- 监控连接状态和消息流

### 监控指标

- 连接成功率
- 消息传输延迟
- 数据处理时间
- 错误发生频率

## 注意事项

1. **会话管理**: 确保在使用 WebSocket 前已创建有效的面试会话
2. **数据同步**: WebSocket 连接与 HTTP API 的数据保持同步
3. **资源清理**: 连接断开时清理相关资源
4. **并发控制**: 一个会话同时只允许一个 WebSocket 连接
5. **超时处理**: 实现适当的超时和心跳机制

## 集成示例

### JavaScript 客户端基础结构

```javascript
// 建立连接
const ws = new WebSocket(`ws://localhost:8000/ws/video-stream/${sessionId}`);

// 监听消息
ws.onmessage = function (event) {
  const message = JSON.parse(event.data);
  handleMessage(message);
};

// 发送视频数据
function sendVideoData(videoData) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(videoData);
  }
}

// 处理不同类型的消息
function handleMessage(message) {
  switch (message.type) {
    case "connection_established":
      // 处理连接确认
      break;
    case "transcription_result":
      // 处理转录结果
      break;
    // ... 其他消息类型
  }
}
```

---
