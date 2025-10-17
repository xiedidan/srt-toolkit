# README 更新说明

## 添加内容

请在现有 README.md 文件中添加以下内容：

### 安装说明部分

在配置API密钥部分后添加：

```markdown
5. 创建配置文件
复制配置模板并填入您的API密钥：
```bash
cp consts.py.template consts.py
```
然后编辑 `consts.py` 文件，填入您的实际API密钥和配置。

**注意**：
- `consts.py` 文件已在 `.gitignore` 中排除，不会被提交到版本控制系统
- 请勿分享或提交包含API密钥的 `consts.py` 文件
- 如需添加新的API配置，请参考 `consts.py.template` 中的格式
```

### 项目结构部分

在项目结构中添加：
```
├── consts.py.template      # 配置模板文件
├── requirements.md         # 功能需求文档
├── technical_design.md     # 技术设计文档
```

### 新增部分

在文件末尾添加：

```markdown
## 开发计划

详细的功能需求和技术实现方案请参考：
- [需求文档](requirements.md) - 包含所有待实现功能的详细描述
- [技术设计文档](technical_design.md) - 包含技术实现方案和架构设计

### 即将实现的功能

1. **Ollama Cloud 模型支持** - 扩展模型调用能力，支持更多AI模型
2. **改进的TTS语速处理** - 解决字幕语速过快时的语音合成问题
3. **Whisper语音转字幕** - 添加基于Whisper的语音/视频转字幕功能
4. **统一Web界面** - 整合所有工具的Web UI，支持项目管理和批量处理

### 贡献指南

如果您想参与开发，请：
1. 查看 [需求文档](requirements.md) 了解当前计划
2. 参考 [技术设计文档](technical_design.md) 了解实现方案
3. 创建 Issue 讨论您想开发的功能
4. 提交 Pull Request 之前请确保代码已通过测试

## 版本历史

- v2.0.0 (计划中) - 添加Ollama Cloud支持、改进TTS处理、语音转字幕、WebUI
- v1.x.x - 当前版本，包含基础的字幕翻译、语音合成和视频处理功能
```

## Git 提交说明

在提交代码时，请执行以下命令：

```bash
# 添加所有更改（除了consts.py，它已在.gitignore中被排除）
git add .

# 提交更改
git commit -m "Add project requirements and technical design documents

- Add requirements.md with detailed feature descriptions
- Add technical_design.md with implementation plans
- Update README with setup instructions for consts.py
- Plan for Ollama Cloud integration, TTS improvements, Whisper support, and WebUI"

# 推送到远程仓库
git push origin main
```

## 创建 consts.py.template 文件

请手动创建 `consts.py.template` 文件，内容如下：

```python
# SRT Translator 配置模板
# 复制此文件为 consts.py 并填入您的实际API密钥

API_CONFIG = {
    "ollama": [
        {
            "TYPE": "deepseek-v3.1:671b",
            "DEFAULT_API_KEY": 'your_ollama_api_key_here',
            "API_ENDPOINT": "https://ollama.com/api/chat",
            "MODEL": "deepseek-v3.1:671b-cloud",
            "PRICE_PER_100M": 0
        }
    ],
    "ollama_cloud": [
        {
            "TYPE": "llama3.1:8b",
            "DEFAULT_API_KEY": 'your_ollama_cloud_api_key_here',
            "API_ENDPOINT": "https://api.ollama.cloud/v1/chat/completions",
            "MODEL": "llama3.1:8b",
            "PRICE_PER_100M": 0
        },
        {
            "TYPE": "llama3.1:70b",
            "DEFAULT_API_KEY": 'your_ollama_cloud_api_key_here',
            "API_ENDPOINT": "https://api.ollama.cloud/v1/chat/completions",
            "MODEL": "llama3.1:70b",
            "PRICE_PER_100M": 0
        }
    ],
    "siliconflow": [
        {
            "TYPE": "deepseek-r1:671b",
            "DEFAULT_API_KEY": 'your_siliconflow_api_key_here',
            "API_ENDPOINT": "https://api.siliconflow.cn/v1/chat/completions",
            "MODEL": "deepseek-ai/DeepSeek-R1",
            "PRICE_PER_100M": 16
        },
        {
            "TYPE": "deepseek-r1:7b",
            "DEFAULT_API_KEY": 'your_siliconflow_api_key_here',
            "API_ENDPOINT": "https://api.siliconflow.cn/v1/chat/completions",
            "MODEL": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
            "PRICE_PER_100M": 0
        }
    ],
    "bailian": [
        {
            "TYPE": "deepseek-r1:671b",
            "DEFAULT_API_KEY": 'your_bailian_api_key_here',
            "API_ENDPOINT": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            "MODEL": "deepseek-r1",
            "PRICE_PER_100M": 16
        },
        {
            "TYPE": "deepseek-r1:70b",
            "DEFAULT_API_KEY": 'your_bailian_api_key_here',
            "API_ENDPOINT": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            "MODEL": "deepseek-r1-distill-llama-70b",
            "PRICE_PER_100M": 0
        },
        {
            "TYPE": "deepseek-v3:671b",
            "DEFAULT_API_KEY": 'your_bailian_api_key_here',
            "API_ENDPOINT": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            "MODEL": "deepseek-v3",
            "PRICE_PER_100M": 8
        },
        {
            "TYPE": "qwen3:235b",
            "DEFAULT_API_KEY": 'your_bailian_api_key_here',
            "API_ENDPOINT": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            "MODEL": "qwen3-235b-a22b",
            "PRICE_PER_100M": 4
        }
    ],
    "deepseek": [
        {
            "TYPE": "deepseek-r1:671b",
            "DEFAULT_API_KEY": 'your_deepseek_api_key_here',
            "API_ENDPOINT": "https://api.deepseek.com/v1/chat/completions",
            "MODEL": "deepseek-reasoner",
            "PRICE_PER_100M": 16
        },
        {
            "TYPE": "deepseek-v3:671b",
            "DEFAULT_API_KEY": 'your_deepseek_api_key_here',
            "API_ENDPOINT": "https://api.deepseek.com/v1/chat/completions",
            "MODEL": "deepseek-chat",
            "PRICE_PER_100M": 8
        }
    ]
}

# TTS服务配置
TTS_BASE_URL = "http://your-tts-server-url"  # 请替换为实际的TTS API基础URL
```

## 下一步行动

1. 更新 README.md 文件，添加上述内容
2. 创建 consts.py.template 文件
3. 提交所有更改到 git
4. 开始实现第一个需求：更新模型调用逻辑，增加Ollama Cloud支持