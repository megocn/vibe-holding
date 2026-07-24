#!/usr/bin/env python3
"""多模态第二波：源头丰富性补种（实时/语音/视频/图像/音乐）。

相对第一波「代表条目」，本波按选型池补齐：
- 国内端到端实时：Qwen-Audio Realtime、豆包 S2S、Omni Realtime…
- 百炼 TTS：Qwen-Audio-TTS、CosyVoice
- 海外编排/平台：Pipecat、Hume、Inworld、Bland、Ultravox、Agora…
- 视频旗舰：Veo、PixVerse、HunyuanVideo、LTX、Dreamina、HeyGen…
- 图像/音乐缺口：Grok Imagine、混元生图、Stable Audio…

幂等：已存在文件默认跳过。`--overwrite` 强制覆盖。

用法:
  python3 scripts/expand-multimodal-rich-2026-07.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
ENTRIES = CONTENT / "entries"
VENDORS = CONTENT / "vendors"
EDGES = CONTENT / "edges"
REVIEWED = "2026-07-24"


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def entry(**kw) -> dict:
    e = {
        "pricing": {"model": "freemium"},
        "availability": {
            "chinaAccessible": True,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["global"],
        },
        "tags": [],
        "maturity": "stable",
        "pitfalls": [],
        "updates": [],
        "rankings": [],
        "sources": [],
        "lastReviewed": REVIEWED,
        "region": "overseas",
    }
    e.update(kw)
    if "officialUrl" in e and not e["sources"]:
        e["sources"] = [e["officialUrl"]]
    if e.get("vendorId") is None:
        e.pop("vendorId", None)
    assert len(e["oneLiner"]) <= 60, (e["id"], len(e["oneLiner"]), e["oneLiner"])
    assert len(e.get("descriptionMd", "")) >= 120, (e["id"], len(e.get("descriptionMd", "")))
    assert e.get("pitfalls"), e["id"]
    assert e.get("subcategory"), e["id"]
    return e


def desc(what: str, when: str, caution: str) -> str:
    return f"{what}\n\n{when}\n\n{caution}\n"


def mk(eid, name, cat, sub, one, url, what, when, caution, **extra):
    pitfalls = extra.pop("pitfalls", None)
    kw = {
        "id": eid,
        "name": name,
        "category": cat,
        "subcategory": sub,
        "oneLiner": one,
        "officialUrl": url,
        "descriptionMd": desc(what, when, caution),
        "pitfalls": pitfalls or [caution[:80]],
    }
    kw.update(extra)
    return entry(**kw)


def edge(eid, frm, to, typ, weight=0.7, confidence="community", note=None):
    e = {
        "id": eid,
        "from": frm,
        "to": to,
        "type": typ,
        "weight": weight,
        "confidence": confidence,
        "sources": [],
        "createdAt": REVIEWED,
    }
    if note:
        e["note"] = note
    return e


def vendor(vid, name, region="overseas", url=None):
    v = {"id": vid, "name": name, "region": region}
    if url:
        v["url"] = url
    return v


CN = {
    "chinaAccessible": True,
    "needsCompany": False,
    "needsIcp": False,
    "regions": ["CN"],
}
US_BLOCKED = {
    "chinaAccessible": False,
    "needsCompany": False,
    "needsIcp": False,
    "regions": ["global"],
}

ENTRIES_DATA: list[dict] = [
    # ========== ai-realtime · 端到端 S2S ==========
    mk(
        "qwen-audio-realtime",
        "Qwen-Audio Realtime",
        "ai-realtime",
        "speech-to-speech",
        "通义端到端实时语音 · 3.0 Plus/Flash · 百炼",
        "https://help.aliyun.com/zh/model-studio/qwen-audio-realtime-user-guides",
        "Qwen-Audio Realtime（当前主推 **Qwen-Audio-3.0-Realtime** Plus/Flash）是阿里通义端到端实时语音交互模型，经百炼 WebSocket 双工协议提供语音进/语音出，支持 server_vad、smart_turn 与 push-to-talk，并可 Function Calling / MCP。",
        "国内智能客服、语音助手、情感陪伴需要低延迟全双工、且已用阿里云/百炼时优先；与 OpenAI Realtime / 豆包 S2S 同层对比。",
        "版本与地域 endpoint 需锁定；勿把版本名拆成独立条目——档位写在 currentVersion。海外节点与计费以控制台为准。",
        vendorId="alibaba-cloud",
        region="domestic",
        tags=["realtime", "s2s", "domestic", "qwen", "dashscope"],
        pricing={"model": "usage", "currency": "CNY"},
        currentVersion="3.0 Realtime (Plus/Flash)",
        docsUrl="https://help.aliyun.com/zh/model-studio/qwen-audio-realtime-user-guides",
        availability=CN,
        maturity="stable",
    ),
    mk(
        "qwen-omni-realtime",
        "Qwen-Omni Realtime",
        "ai-realtime",
        "speech-to-speech",
        "通义 Omni 实时 · 音视频多模态 · 百炼",
        "https://help.aliyun.com/zh/model-studio/s2s-model",
        "Qwen-Omni Realtime（如 qwen3.5-omni-flash-realtime）在实时会话中同时处理文本/音频/图像等输入，面向「边看边说」的多模态助手，与纯语音的 Qwen-Audio Realtime 分工不同。",
        "需要摄像头/屏幕画面 + 语音同会话、国内合规落地时评估；纯电话/耳机语音可优先 Audio Realtime 以降本。",
        "模态越多成本与延迟越高；与 Gemini Live 对标时注意区域可达与工具调用成熟度。",
        vendorId="alibaba-cloud",
        region="domestic",
        tags=["realtime", "multimodal", "omni", "domestic", "qwen"],
        pricing={"model": "usage", "currency": "CNY"},
        currentVersion="3.5 Omni Flash Realtime",
        availability=CN,
    ),
    mk(
        "doubao-realtime",
        "豆包端到端实时语音",
        "ai-realtime",
        "speech-to-speech",
        "字节豆包 S2S · Omni/强人格 · 火山",
        "https://www.volcengine.com/docs/6561/1594360",
        "豆包端到端实时语音大模型在火山引擎上提供 Speech-to-Speech 能力，含偏助手的 Omni 线与偏角色扮演的 Strong Character 线，强调超拟人表达与低时延，替代传统 ASR→LLM→TTS 级联。",
        "国内 ToB 语音助手、车载、客服或角色陪伴，且已用火山/豆包生态时优先 POC。",
        "模型版本号与音色 speaker 需按文档锁定；出海与英文场景需另测，勿默认等同海外 Realtime API。",
        vendorId="bytedance",
        region="domestic",
        tags=["realtime", "s2s", "domestic", "doubao", "volcengine"],
        pricing={"model": "usage", "currency": "CNY"},
        docsUrl="https://www.volcengine.com/docs/6561/1594360",
        availability=CN,
    ),
    mk(
        "ultravox",
        "Ultravox",
        "ai-realtime",
        "speech-to-speech",
        "开源友好 S2S · 语音 Agent 模型层",
        "https://github.com/fix-of-Thought/ultravox",
        "Ultravox 提供面向实时语音 Agent 的 speech-to-speech 模型与托管选项，定位模型层能力，常与自建电话/WebRTC 栈组合，而非一站式呼叫中心 SaaS。",
        "语音 AI 创业或需要可控 S2S 模型、可对照 OpenAI Realtime 做成本/延迟基准时评估。",
        "电话与合规能力需自建；生态与文档体量小于超大规模云厂商。",
        vendorId="fix-of-thought",
        tags=["realtime", "s2s", "open-source"],
        pricing={"model": "usage", "currency": "USD"},
        githubUrl="https://github.com/fix-of-Thought/ultravox",
    ),
    mk(
        "hume-ai",
        "Hume AI",
        "ai-realtime",
        "speech-to-speech",
        "表情语音 · EVI/Octave · 情感可控",
        "https://www.hume.ai",
        "Hume AI 以情感智能与表达力语音著称，提供 EVI（Empathic Voice Interface）与 Octave TTS 等能力，强调语气、情绪与副语言，可接入 Pipecat 等编排框架。",
        "需要高表现力陪伴/角色对话、或研究情感计算的语音产品时评估；与 ElevenLabs/Cartesia 在「听感」维度对照。",
        "企业电话与合规场景未必是强项；成本与延迟需按会话压测。",
        vendorId="hume-inc",
        tags=["realtime", "expressive", "tts", "evi"],
        pricing={"model": "usage", "currency": "USD"},
    ),
    mk(
        "inworld-realtime",
        "Inworld Realtime",
        "ai-realtime",
        "speech-to-speech",
        "Inworld 实时管线 · TTS/STT/路由 · 游戏角色向",
        "https://inworld.ai",
        "Inworld 提供 Realtime TTS/STT 与 LLM Router，以及可在单 WebSocket 上跑级联 STT→LLM→TTS 的 Realtime API，游戏 NPC 与消费级互动角色场景常见；与 Pipecat 有原生集成。",
        "需要角色一致性、可换底层 LLM、又要语音管线开箱时评估；对照原生 S2S（OpenAI/Gemini/Qwen-Audio）。",
        "级联架构延迟通常高于原生 S2S；游戏外企业客服需另看电话与合规。",
        vendorId="inworld-inc",
        tags=["realtime", "tts", "game", "npc"],
        pricing={"model": "usage", "currency": "USD"},
    ),
    mk(
        "pipecat",
        "Pipecat",
        "ai-realtime",
        "realtime-infra",
        "开源语音 Agent 编排 · Daily · 可插拔",
        "https://github.com/pipecat-ai/pipecat",
        "Pipecat 是面向实时语音与多模态 Agent 的开源 Python 编排框架，用帧管道组合 STT/LLM/TTS 或原生 Realtime 模型，可由 Daily 提供 Pipecat Cloud；与 LiveKit Agents 同属「自建编排」选型层。",
        "要自选模型组合、多 Agent 交接、或把 OpenAI/Gemini/Cartesia 等拼成生产管线时优先；电话可用 SIP/PSTN 扩展。",
        "自托管需运维与可观测；只要「一键电话 Agent」可先看 Vapi/Retell/Bland。",
        vendorId="daily-co",
        tags=["realtime", "orchestration", "open-source", "python"],
        pricing={"model": "open-source"},
        githubUrl="https://github.com/pipecat-ai/pipecat",
        maturity="stable",
    ),
    mk(
        "bland-ai",
        "Bland AI",
        "ai-realtime",
        "voice-agent-platform",
        "电话语音 Agent · 外呼/转入 · 打包计费",
        "https://www.bland.ai",
        "Bland AI 是偏电话场景的语音 Agent 平台，强调快速上线入站/出站通话，常以打包分钟费率包含模型与线路，适合销售外呼与高并发电话自动化。",
        "北美英语电话外呼、需要少集成尽快跑通时评估；与 Vapi/Retell/Synthflow 同层。",
        "中文与国内线路弱；深度定制媒体层仍可能下沉 Pipecat/LiveKit。",
        vendorId="bland-inc",
        tags=["voice-agent", "telephony", "outbound"],
        pricing={"model": "usage", "currency": "USD"},
    ),
    mk(
        "synthflow",
        "Synthflow",
        "ai-realtime",
        "voice-agent-platform",
        "低代码语音 Agent · 电话工作流",
        "https://synthflow.ai",
        "Synthflow 提供偏可视化/低代码的语音 Agent 构建与电话工作流，面向业务团队快速配置来电接待与外呼剧本，开发者可再接自定义工具。",
        "非工程主导、要尽快配置电话脚本与转接逻辑时评估；与 Vapi 的开发者中心取向对照。",
        "复杂多模型编排与自托管能力有限；单价随分钟与增值路由上升。",
        vendorId="synthflow-inc",
        tags=["voice-agent", "telephony", "low-code"],
        pricing={"model": "usage", "currency": "USD"},
    ),
    mk(
        "agora-conversational-ai",
        "Agora Conversational AI",
        "ai-realtime",
        "realtime-infra",
        "声网实时音视频 · 对话式 AI 扩展",
        "https://www.agora.io/en/products/conversational-ai/",
        "Agora（声网）在实时音视频网络之上提供 Conversational AI 相关能力，适合已有 Agora RTC 的 App 叠加语音助手，而不是从零自建 WebRTC。",
        "直播/教育/社交 App 已用 Agora，需要低延迟语音对话附加层时评估。",
        "模型层仍常外接 LLM/TTS；纯「只要模型 API」不必为此引入 RTC 账单。",
        vendorId="agora-inc",
        tags=["realtime", "webrtc", "rtc"],
        pricing={"model": "usage", "currency": "USD"},
        region="both",
    ),
    # ========== ai-speech · TTS/ASR ==========
    mk(
        "qwen-audio-tts",
        "Qwen-Audio TTS",
        "ai-speech",
        "tts",
        "通义 Audio TTS · 3.0 Plus/Flash · AA 榜强",
        "https://help.aliyun.com/zh/model-studio/realtime-tts-user-guide",
        "Qwen-Audio TTS（当前 **Qwen-Audio-3.0-TTS** Plus/Flash）是阿里百炼实时语音合成线，强调自然度、指令控制与多语覆盖，在 Artificial Analysis Speech Arena 等第三方对比中表现突出。",
        "国内产品需要高质量中文/多语旁白或流式 TTS、且与通义同账号时优先；与 CosyVoice 按克隆/系统音色场景分流。",
        "地域与 WebSocket endpoint 需按文档配置；版本名写入 currentVersion，勿拆条。",
        vendorId="alibaba-cloud",
        region="domestic",
        tags=["tts", "domestic", "qwen", "dashscope"],
        pricing={"model": "usage", "currency": "CNY"},
        currentVersion="3.0 TTS (Plus/Flash)",
        docsUrl="https://help.aliyun.com/zh/model-studio/realtime-tts-user-guide",
        availability=CN,
    ),
    mk(
        "cosyvoice",
        "CosyVoice",
        "ai-speech",
        "tts",
        "阿里 CosyVoice · 复刻/声音设计 · 百炼",
        "https://help.aliyun.com/zh/model-studio/realtime-tts-user-guide",
        "CosyVoice 是阿里通义实验室语音合成模型族（经百炼提供 v3/v3.5 等），擅长声音复刻与声音设计，适合自定义音色的助手、有声与客服场景；新项目文档建议优先于旧 Sambert。",
        "需要克隆品牌音色或「文本描述出声」设计、国内合规落地时评估；与 Qwen-Audio-TTS 可同平台对照。",
        "部分版本仅特定地域/仅支持复刻音色；生产前确认 voice id 与模型名匹配。",
        vendorId="alibaba-cloud",
        region="domestic",
        tags=["tts", "voice-clone", "domestic", "cosyvoice"],
        pricing={"model": "usage", "currency": "CNY"},
        currentVersion="v3.5 (Plus/Flash)",
        availability=CN,
    ),
    mk(
        "google-cloud-speech",
        "Google Cloud Speech",
        "ai-speech",
        "speech-suite",
        "GCP Speech-to-Text · Chirp · 企业套件",
        "https://cloud.google.com/speech-to-text",
        "Google Cloud Speech-to-Text（含 Chirp 等模型）与配套 TTS 构成 GCP 语音套件，强调多语、企业合同与 Vertex 同区部署，适合已在 Google Cloud 的转写与语音管线。",
        "需要批量/流式转写、多语支持、与 GCP 账单一体时选用；创意旁白可另配 Chirp/云 TTS 或第三方。",
        "国内直连受限；表现力旁白常不如 ElevenLabs，需按场景分拆选型。",
        vendorId="google",
        tags=["asr", "stt", "tts", "gcp"],
        pricing={"model": "usage", "currency": "USD"},
        availability=US_BLOCKED,
        maturity="mature",
    ),
    mk(
        "amazon-polly",
        "Amazon Polly",
        "ai-speech",
        "tts",
        "AWS 神经 TTS · 与 Transcribe 同栈",
        "https://aws.amazon.com/polly/",
        "Amazon Polly 提供神经与生成式音色的文本转语音，常与 Amazon Transcribe 组成 AWS 语音管线，适合已深度绑定 AWS 的播报、无障碍与联络中心场景。",
        "基础设施在 AWS、需要 IAM/区域合规一体的 TTS 时默认选项之一。",
        "创意克隆与极致延迟通常弱于 Cartesia/ElevenLabs；实时 Agent 常再外接专用模型。",
        vendorId="amazon",
        tags=["tts", "aws"],
        pricing={"model": "usage", "currency": "USD"},
        maturity="mature",
    ),
    mk(
        "amazon-transcribe",
        "Amazon Transcribe",
        "ai-speech",
        "asr",
        "AWS 托管转写 · 通话分析 · 流式",
        "https://aws.amazon.com/transcribe/",
        "Amazon Transcribe 提供批处理与流式语音识别，以及通话分析等联络中心能力，与 Polly/Connect 等同生态。",
        "AWS 上的会议转写、客服质检或合规存档场景常用。",
        "中文与小语种效果需自测；极致低延迟语音对话更常看 Deepgram 或原生 Realtime。",
        vendorId="amazon",
        tags=["asr", "stt", "aws"],
        pricing={"model": "usage", "currency": "USD"},
        maturity="mature",
    ),
    mk(
        "tencent-speech",
        "腾讯云语音",
        "ai-speech",
        "speech-suite",
        "腾讯云 ASR/TTS · 微信生态邻近",
        "https://cloud.tencent.com/product/tts",
        "腾讯云语音提供语音识别、合成与相关 AI 语音能力，面向国内 App 与政企客户，并常与微信/企微等腾讯生态场景邻近落地。",
        "产品已在腾讯云、需要国内语音能力或与微信场景打通时评估；可与讯飞/火山/百炼同层对照。",
        "海外语种与文档生态弱于国际语音厂商；接口风格偏国内云。",
        vendorId="tencent-cloud",
        region="domestic",
        tags=["tts", "asr", "domestic"],
        pricing={"model": "usage", "currency": "CNY"},
        availability=CN,
    ),
    mk(
        "baidu-speech",
        "百度智能云语音",
        "ai-speech",
        "speech-suite",
        "百度 ASR/TTS · 国内老牌语音",
        "https://cloud.baidu.com/product/speech",
        "百度智能云语音技术提供听写、合成与语音唤醒等能力，长期服务国内车载、物联网与 ToB 语音场景。",
        "存量百度云客户或车载/IoT 中文语音需求时评估。",
        "新一代表达力与实时 S2S 叙事弱于通义 Audio / 豆包端到端，新项目建议对照百炼与火山。",
        vendorId="baidu",
        region="domestic",
        tags=["tts", "asr", "domestic"],
        pricing={"model": "usage", "currency": "CNY"},
        availability=CN,
        maturity="mature",
    ),
    mk(
        "funasr",
        "FunASR",
        "ai-speech",
        "asr",
        "开源工业 ASR · 达摩院 · 可自托管",
        "https://github.com/modelscope/FunASR",
        "FunASR 是面向生产的开源语音识别工具包（ModelScope/达摩院生态），支持标点、时间戳、说话人等，适合私有化转写与中文场景自托管。",
        "数据不能出域、或要自建中文 ASR 服务时优先评估；可与开源 TTS 组成私有管线。",
        "需自备 GPU/运维；实时全双工对话体验仍可能不如云端 S2S。",
        vendorId="alibaba-cloud",
        region="domestic",
        tags=["asr", "stt", "open-source", "self-hosted"],
        pricing={"model": "open-source"},
        githubUrl="https://github.com/modelscope/FunASR",
    ),
    mk(
        "chattts",
        "ChatTTS",
        "ai-speech",
        "tts",
        "开源对话向 TTS · 中文社区常用",
        "https://github.com/2noise/ChatTTS",
        "ChatTTS 是面向对话场景的开源 TTS 模型，中文社区采用多，适合本地试验自然口语合成与研究原型。",
        "需要本地/开源中文 TTS 原型、或对照云厂商听感时试用。",
        "商用授权、稳定性与长文本一致性需逐案核对；生产 SLA 不如云 API。",
        tags=["tts", "open-source", "chinese"],
        pricing={"model": "open-source"},
        githubUrl="https://github.com/2noise/ChatTTS",
        region="both",
    ),
    mk(
        "playht",
        "PlayHT",
        "ai-speech",
        "tts",
        "多语 TTS · 克隆 · 创作者/产品 API",
        "https://play.ht",
        "PlayHT 提供多语种 TTS、声音克隆与流式 API，面向创作者工具与产品内嵌旁白，是 ElevenLabs 常见对照选项之一。",
        "需要多语旁白 API、克隆与创作者工作流，并做供应商备份时评估。",
        "极致 Agent 延迟与企业电话合规需另测；定价档位变化较快。",
        vendorId="playht-inc",
        tags=["tts", "voice-clone"],
        pricing={"model": "subscription", "currency": "USD"},
    ),
    mk(
        "speechmatics",
        "Speechmatics",
        "ai-speech",
        "asr",
        "高精度多语 ASR · 企业转写",
        "https://www.speechmatics.com",
        "Speechmatics 以高精度多语语音识别著称，提供实时与批处理 API，面向媒体、会议与受监管行业转写。",
        "多语媒体转写、字幕或企业合规 ASR 短名单中常见。",
        "纯中文性价比需与国内云/FunASR 对照；不是语音 Agent 全家桶。",
        vendorId="speechmatics-inc",
        tags=["asr", "stt", "enterprise"],
        pricing={"model": "usage", "currency": "USD"},
        maturity="mature",
    ),
    mk(
        "gladia",
        "Gladia",
        "ai-speech",
        "asr",
        "音视频转写 API · 说话人/翻译",
        "https://www.gladia.io",
        "Gladia 提供面向开发者的音视频转写 API，强调说话人分离、翻译与媒体工作流集成，适合播客/会议产品内嵌。",
        "需要快速给媒体产品加转写层、并要 diarization/翻译时评估。",
        "实时语音对话 Agent 不是主战场；延迟敏感场景对照 Deepgram。",
        vendorId="gladia-inc",
        tags=["asr", "stt", "media"],
        pricing={"model": "usage", "currency": "USD"},
    ),
    # ========== design-ai-video ==========
    mk(
        "google-veo",
        "Google Veo",
        "design-ai-video",
        "video-gen",
        "DeepMind 视频旗舰 · 原生音频 · Flow",
        "https://deepmind.google/models/veo/",
        "Veo（当前叙事以 Veo 3.1 等为代表）是 Google DeepMind 视频生成旗舰，强调物理真实感、prompt 遵循与**原生音画同生**，经 Gemini API / Flow 等入口提供。",
        "需要高保真营销/叙事短片、且音效对白希望同模型生成时评估；与 Runway/Sora/Kling 同层。",
        "区域与配额政策变化快；国内直连受限；成本按秒/积分高。",
        vendorId="google",
        tags=["ai", "video", "audio-native"],
        pricing={"model": "usage", "currency": "USD"},
        currentVersion="Veo 3.1",
        availability=US_BLOCKED,
    ),
    mk(
        "pixverse",
        "PixVerse",
        "design-ai-video",
        "video-gen",
        "多镜视频 · 转场/参考 · 社交向",
        "https://pixverse.ai",
        "PixVerse 面向创作者的 AI 视频平台，强调多镜生成、转场、参考图与音频相关控制，适合短视频与社交素材快速迭代。",
        "需要短多镜、社交节奏、快速试风格时评估；与 Pika/Luma 对照。",
        "影视级长镜头与商用授权需核对；质量随版本波动。",
        vendorId="pixverse-inc",
        tags=["ai", "video", "social"],
        pricing={"model": "subscription", "currency": "USD"},
    ),
    mk(
        "hunyuan-video",
        "混元生视频",
        "design-ai-video",
        "video-gen",
        "腾讯混元视频 · 开源/API · 国内",
        "https://hunyuan.tencent.com",
        "混元生视频是腾讯混元多模态能力的一部分，提供文/图生视频与开源权重叙事，适合国内团队在腾讯云/混元生态内做视频生成与自托管试验。",
        "需要国内可达、或开源自托管视频模型时纳入短名单；与可灵/海螺/Vidu 对照。",
        "产品入口与开源仓库版本迭代快；商用条款与云 API 分开确认。",
        vendorId="tencent-hunyuan",
        region="domestic",
        tags=["ai", "video", "domestic", "open-source"],
        pricing={"model": "freemium", "currency": "CNY"},
        availability=CN,
    ),
    mk(
        "ltx-video",
        "LTX Video",
        "design-ai-video",
        "video-gen",
        "Lightricks LTX · 开源/Studio · 可控",
        "https://www.lightricks.com/ltxv",
        "LTX Video（Lightricks）提供偏实时/高效的视频生成模型与 LTX Studio 创作界面，强调镜头级控制与开源权重可用性，创作者与自托管管线常见。",
        "需要开源视频模型、或故事板级控制（Studio）时评估；与 HunyuanVideo/Runway 对照。",
        "旗舰云厂商的原生音画一体能力仍需另测；硬件需求不低。",
        vendorId="lightricks",
        tags=["ai", "video", "open-source"],
        pricing={"model": "freemium"},
        githubUrl="https://github.com/Lightricks/LTX-Video",
    ),
    mk(
        "dreamina",
        "即梦 · 视频",
        "design-ai-video",
        "video-gen",
        "即梦平台文/图生视频 · Seedance · 国内",
        "https://jimeng.jianying.com",
        "即梦（海外品牌名 Dreamina）同一平台上的**视频生成**能力（如 Seedance 线），文/图生视频，面向国内创作者与剪映二次剪辑链路；id 仍为 dreamina 仅为历史兼容。",
        "已在即梦做图、需要同账号延伸到短视频/动态素材时选用；与可灵、海螺、Vidu 同叶对比。图像能力见「即梦 · 图像」。",
        "与「即梦 · 图像」是同一平台不同模态，勿当两家竞品；商用与水印随套餐变。",
        vendorId="bytedance",
        region="domestic",
        tags=["ai", "video", "domestic", "jimeng-platform"],
        pricing={"model": "freemium", "currency": "CNY"},
        availability=CN,
    ),
    mk(
        "heygen",
        "HeyGen",
        "design-ai-video",
        "avatar-video",
        "数字人视频 · 多语口型 · 营销向",
        "https://www.heygen.com",
        "HeyGen 专注数字人/口播视频：上传形象或模板，生成多语口型同步讲解，营销、培训与产品介绍高频使用，与文生镜头类工具分工不同。",
        "需要「真人出镜感」讲解视频、多语本地化口播时优先；不要与 Runway/Veo 的文生场景片混比。",
        "形象授权与 deepfake 合规严格；创意镜头控制弱于生成式视频模型。",
        vendorId="heygen-inc",
        tags=["ai", "video", "avatar", "dubbing"],
        pricing={"model": "subscription", "currency": "USD"},
    ),
    mk(
        "synthesia",
        "Synthesia",
        "design-ai-video",
        "avatar-video",
        "企业数字人口播 · 培训/合规向",
        "https://www.synthesia.io",
        "Synthesia 提供企业向 AI 数字人视频平台，强调模板、品牌安全与培训/内部沟通场景，是 HeyGen 在企业培训赛道的常见对照。",
        "大型组织需要标准化培训视频、审核流程与多语口播时评估。",
        "创意生成与镜头运动弱；按席位/分钟计费需测算规模。",
        vendorId="synthesia-inc",
        tags=["ai", "video", "avatar", "enterprise"],
        pricing={"model": "subscription", "currency": "USD"},
        maturity="mature",
    ),
    # ========== design-ai-image ==========
    mk(
        "grok-imagine",
        "Grok Imagine",
        "design-ai-image",
        "image-gen",
        "xAI 文生图/短视频 · Grok 生态",
        "https://x.ai",
        "Grok Imagine 是 xAI 在 Grok 产品中的图像（及短视频向）生成能力，强调创意与表达，与 Grok 对话生态绑定。",
        "已在 xAI/Grok 生态、需要快速出图或趣味视觉时试用；严肃品牌管线仍对照 Midjourney/Flux。",
        "区域与 API 成熟度变化快；企业合规与商用条款需核对。",
        vendorId="xai",
        tags=["ai", "image", "xai"],
        pricing={"model": "subscription", "currency": "USD"},
        availability=US_BLOCKED,
        maturity="beta",
    ),
    mk(
        "hunyuan-image",
        "混元生图",
        "design-ai-image",
        "image-gen",
        "腾讯混元文生图 · 国内云",
        "https://hunyuan.tencent.com",
        "混元生图是腾讯混元多模态中的文生图能力，面向国内开发者与营销/电商素材，可与混元视频及腾讯云业务同生态落地。",
        "腾讯云/微信生态应用需要国内文生图时评估；与即梦、通义万相、可图对照选型。",
        "艺术社区热度因场景而异；内容安全审核策略需适配产品。",
        vendorId="tencent-hunyuan",
        region="domestic",
        tags=["ai", "image", "domestic"],
        pricing={"model": "usage", "currency": "CNY"},
        availability=CN,
    ),
    mk(
        "liblib",
        "LiblibAI",
        "design-ai-image",
        "image-gen",
        "国内 AI 创作社区 · 模型/工作流",
        "https://www.liblib.art",
        "LiblibAI 是国内活跃的 AI 图像创作与模型分享社区/平台，提供在线生成与大量自定义模型，适合设计师试验风格与工作流。",
        "需要中文社区模型、LoRA/工作流试验、国内可达创作平台时评估。",
        "偏创作社区而非稳定企业 API SLA；商用与模型授权需逐案确认。",
        vendorId="liblib-inc",
        region="domestic",
        tags=["ai", "image", "domestic", "community"],
        pricing={"model": "freemium", "currency": "CNY"},
        availability=CN,
    ),
    mk(
        "seaart",
        "SeaArt",
        "design-ai-image",
        "image-gen",
        "AI 艺术社区 · 多模型 · 创作者向",
        "https://www.seaart.ai",
        "SeaArt 提供多模型 AI 图像生成与创作者社区，聚合多种风格、模型和工具，面向艺术创作与社交创意图场景。",
        "需要多模型切换试风格、社区模板丰富、快速出图时试用；可与 Midjourney/Liblib 对照。",
        "企业级 API/合规不如云厂商；版权与成人内容策略需关注。",
        vendorId="seaart-inc",
        tags=["ai", "image", "community"],
        pricing={"model": "freemium"},
    ),
    # ========== design-ai-music ==========
    mk(
        "stable-audio",
        "Stable Audio",
        "design-ai-music",
        "music-gen",
        "Stability 音频生成 · 开源/API",
        "https://stability.ai/stable-audio",
        "Stable Audio 是 Stability AI 的音频/音乐生成线，提供 API 与开源相关权重叙事，适合音效、BGM 草稿与可自托管试验。",
        "需要开源/API 音频生成、或与 Stable Diffusion 同厂商管线时评估；完整「带唱歌曲」对照 Suno/Udio。",
        "人声歌曲完整度通常弱于 Suno；商用与训练数据许可需法务过目。",
        vendorId="stability-ai",
        tags=["ai", "music", "audio", "open-source"],
        pricing={"model": "freemium"},
    ),
    mk(
        "aiva",
        "AIVA",
        "design-ai-music",
        "music-gen",
        "AI 作曲 · 配乐/情绪向",
        "https://www.aiva.ai",
        "AIVA 偏重作曲与配乐生成，面向游戏、影像与广告的情绪化乐器编曲，与「带歌词流行歌」生成器（Suno/Udio）定位不同。",
        "需要器乐 BGM、片头片尾或游戏配乐草稿、且要可商用授权套餐时评估。",
        "流行人声歌曲非强项；授权套餐决定商用范围。",
        vendorId="aiva-inc",
        tags=["ai", "music", "soundtrack"],
        pricing={"model": "subscription", "currency": "USD"},
        maturity="mature",
    ),
    mk(
        "mubert",
        "Mubert",
        "design-ai-music",
        "music-gen",
        "生成式流媒体 BGM · API",
        "https://mubert.com",
        "Mubert 提供生成式背景音乐与开发者 API，强调按情绪/场景流式出乐，适合 App 内动态 BGM 与内容平台配乐层。",
        "产品需要可编程、可流式的背景乐，而不是一次性出完整流行歌时评估。",
        "完整流行歌曲与人声不是主场景；授权按计划区分。",
        vendorId="mubert-inc",
        tags=["ai", "music", "bgm", "api"],
        pricing={"model": "subscription", "currency": "USD"},
    ),
]

VENDORS_DATA: list[dict] = [
    vendor("fix-of-thought", "Fixie.ai / Ultravox", url="https://github.com/fix-of-Thought/ultravox"),
    vendor("hume-inc", "Hume AI", url="https://www.hume.ai"),
    vendor("inworld-inc", "Inworld AI", url="https://inworld.ai"),
    vendor("daily-co", "Daily", url="https://www.daily.co"),
    vendor("bland-inc", "Bland AI", url="https://www.bland.ai"),
    vendor("synthflow-inc", "Synthflow", url="https://synthflow.ai"),
    vendor("agora-inc", "Agora", region="both", url="https://www.agora.io"),
    vendor("playht-inc", "PlayHT", url="https://play.ht"),
    vendor("speechmatics-inc", "Speechmatics", url="https://www.speechmatics.com"),
    vendor("gladia-inc", "Gladia", url="https://www.gladia.io"),
    vendor("pixverse-inc", "PixVerse", url="https://pixverse.ai"),
    vendor("lightricks", "Lightricks", url="https://www.lightricks.com"),
    vendor("heygen-inc", "HeyGen", url="https://www.heygen.com"),
    vendor("synthesia-inc", "Synthesia", url="https://www.synthesia.io"),
    vendor("xai", "xAI", url="https://x.ai"),
    vendor("liblib-inc", "LiblibAI", region="domestic", url="https://www.liblib.art"),
    vendor("seaart-inc", "SeaArt", url="https://www.seaart.ai"),
    vendor("aiva-inc", "AIVA", url="https://www.aiva.ai"),
    vendor("mubert-inc", "Mubert", url="https://mubert.com"),
]

EDGES_DATA: list[dict] = [
    # realtime S2S
    edge("edge-qwen-audio-rt-openai-dom", "qwen-audio-realtime", "openai-realtime", "domestic_equivalent_of", note="国内端到端实时 vs OpenAI Realtime"),
    edge("edge-qwen-audio-rt-gemini-alt", "qwen-audio-realtime", "gemini-live", "alternative_to"),
    edge("edge-doubao-rt-openai-dom", "doubao-realtime", "openai-realtime", "domestic_equivalent_of"),
    edge("edge-doubao-rt-qwen-alt", "doubao-realtime", "qwen-audio-realtime", "alternative_to", note="火山豆包 vs 通义 Audio"),
    edge("edge-qwen-omni-rt-audio-with", "qwen-omni-realtime", "qwen-audio-realtime", "commonly_used_with", note="同属通义实时；按是否需要视觉分流"),
    edge("edge-qwen-omni-rt-gemini-alt", "qwen-omni-realtime", "gemini-live", "alternative_to", note="多模态实时对照"),
    edge("edge-qwen-audio-rt-partof-qwen", "qwen-audio-realtime", "qwen", "part_of"),
    edge("edge-doubao-rt-partof-doubao", "doubao-realtime", "doubao", "part_of"),
    edge("edge-ultravox-openai-rt-alt", "ultravox", "openai-realtime", "alternative_to"),
    edge("edge-hume-openai-rt-alt", "hume-ai", "openai-realtime", "alternative_to", weight=0.55),
    edge("edge-inworld-openai-rt-alt", "inworld-realtime", "openai-realtime", "alternative_to", weight=0.6),
    edge("edge-pipecat-livekit-alt", "pipecat", "livekit", "alternative_to", note="开源语音 Agent 编排对照"),
    edge("edge-pipecat-openai-rt-with", "pipecat", "openai-realtime", "commonly_used_with"),
    edge("edge-pipecat-gemini-live-with", "pipecat", "gemini-live", "commonly_used_with"),
    edge("edge-pipecat-cartesia-with", "pipecat", "cartesia", "commonly_used_with"),
    edge("edge-pipecat-hume-with", "pipecat", "hume-ai", "commonly_used_with"),
    edge("edge-bland-vapi-alt", "bland-ai", "vapi", "alternative_to"),
    edge("edge-synthflow-vapi-alt", "synthflow", "vapi", "alternative_to"),
    edge("edge-agora-livekit-alt", "agora-conversational-ai", "livekit", "alternative_to", weight=0.55),
    # speech
    edge("edge-qwen-tts-eleven-dom", "qwen-audio-tts", "elevenlabs", "domestic_equivalent_of"),
    edge("edge-cosyvoice-eleven-dom", "cosyvoice", "elevenlabs", "domestic_equivalent_of", note="复刻/设计向"),
    edge("edge-qwen-tts-cosy-with", "qwen-audio-tts", "cosyvoice", "commonly_used_with", note="同属百炼 TTS"),
    edge("edge-qwen-tts-rt-with", "qwen-audio-tts", "qwen-audio-realtime", "commonly_used_with", note="同厂商 Audio 线；场景分流"),
    edge("edge-gcp-speech-azure-alt", "google-cloud-speech", "azure-speech", "alternative_to"),
    edge("edge-polly-openai-tts-alt", "amazon-polly", "openai-tts", "alternative_to"),
    edge("edge-transcribe-deepgram-alt", "amazon-transcribe", "deepgram", "alternative_to"),
    edge("edge-polly-transcribe-with", "amazon-polly", "amazon-transcribe", "commonly_used_with"),
    edge("edge-tencent-speech-azure-dom", "tencent-speech", "azure-speech", "domestic_equivalent_of"),
    edge("edge-baidu-speech-azure-dom", "baidu-speech", "azure-speech", "domestic_equivalent_of"),
    edge("edge-funasr-whisper-os", "funasr", "openai-whisper", "open_source_alternative_to"),
    edge("edge-chattts-eleven-os", "chattts", "elevenlabs", "open_source_alternative_to", weight=0.5),
    edge("edge-playht-eleven-alt", "playht", "elevenlabs", "alternative_to"),
    edge("edge-speechmatics-deepgram-alt", "speechmatics", "deepgram", "alternative_to"),
    edge("edge-gladia-assembly-alt", "gladia", "assemblyai", "alternative_to"),
    # video
    edge("edge-veo-runway-alt", "google-veo", "runway", "alternative_to", note="原生音画旗舰对照"),
    edge("edge-veo-sora-alt", "google-veo", "openai-sora", "alternative_to"),
    edge("edge-pixverse-pika-alt", "pixverse", "pika", "alternative_to"),
    edge("edge-hunyuan-video-kling-dom", "hunyuan-video", "runway", "domestic_equivalent_of"),
    edge("edge-hunyuan-video-kling-alt", "hunyuan-video", "kling", "alternative_to"),
    edge("edge-ltx-runway-alt", "ltx-video", "runway", "alternative_to"),
    edge("edge-dreamina-jimeng-with", "dreamina", "jimeng", "commonly_used_with", weight=0.95, note="同一即梦平台的视频/图像模态入口，非两家竞品"),
    edge("edge-dreamina-kling-alt", "dreamina", "kling", "alternative_to"),
    edge("edge-heygen-synthesia-alt", "heygen", "synthesia", "alternative_to"),
    edge("edge-heygen-runway-related", "heygen", "runway", "alternative_to", weight=0.4, note="数字人 vs 文生镜头，弱替代"),
    # image / music
    edge("edge-grok-imagine-mj-alt", "grok-imagine", "midjourney", "alternative_to", weight=0.55),
    edge("edge-hunyuan-image-mj-dom", "hunyuan-image", "midjourney", "domestic_equivalent_of"),
    edge("edge-hunyuan-image-wanxiang-alt", "hunyuan-image", "tongyi-wanxiang", "alternative_to"),
    edge("edge-liblib-mj-dom", "liblib", "midjourney", "domestic_equivalent_of", weight=0.55),
    edge("edge-seaart-mj-alt", "seaart", "midjourney", "alternative_to", weight=0.55),
    edge("edge-stable-audio-suno-alt", "stable-audio", "suno", "alternative_to", weight=0.5),
    edge("edge-aiva-suno-alt", "aiva", "suno", "alternative_to", weight=0.45, note="配乐 vs 完整歌曲"),
    edge("edge-mubert-suno-alt", "mubert", "suno", "alternative_to", weight=0.45),
]


def write_item(dir_path: Path, item: dict, overwrite: bool) -> bool:
    path = dir_path / f"{item['id']}.json"
    if path.exists() and not overwrite:
        return False
    save(path, item)
    return True


def ensure_refs() -> None:
    entry_ids = {p.stem for p in ENTRIES.glob("*.json")}
    vendor_ids = {p.stem for p in VENDORS.glob("*.json")}
    # upcoming
    entry_ids |= {e["id"] for e in ENTRIES_DATA}
    vendor_ids |= {v["id"] for v in VENDORS_DATA}
    missing_v = sorted(
        {
            e.get("vendorId")
            for e in ENTRIES_DATA
            if e.get("vendorId") and e["vendorId"] not in vendor_ids
        }
    )
    if missing_v:
        print(f"warn: missing vendors: {missing_v}")
    for ed in EDGES_DATA:
        for end in (ed["from"], ed["to"]):
            if end not in entry_ids and end not in vendor_ids:
                print(f"warn: edge {ed['id']} endpoint missing: {end}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    # preflight length
    for e in ENTRIES_DATA:
        pass

    ensure_refs()

    ea = va = eda = 0
    for e in ENTRIES_DATA:
        if write_item(ENTRIES, e, args.overwrite):
            ea += 1
    for v in VENDORS_DATA:
        if write_item(VENDORS, v, args.overwrite):
            va += 1
    for ed in EDGES_DATA:
        if write_item(EDGES, ed, args.overwrite):
            eda += 1

    print(
        f"done: +entries={ea} +vendors={va} +edges={eda} "
        f"total_entries={len(list(ENTRIES.glob('*.json')))} "
        f"total_edges={len(list(EDGES.glob('*.json')))} "
        f"total_vendors={len(list(VENDORS.glob('*.json')))}"
    )


if __name__ == "__main__":
    main()
