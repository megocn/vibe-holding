#!/usr/bin/env python3
"""多模态基建扩种：TTS/ASR、实时语音、视频/音乐生成、图像补强。

幂等：已存在的 entry/vendor/edge 文件默认跳过；`--overwrite` 可强制覆盖。
Runway 迁至 design-ai-video 始终执行。

用法:
  python3 scripts/expand-multimodal-2026-07.py
  python3 scripts/expand-multimodal-2026-07.py --overwrite
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


def edge(eid, frm, to, typ, weight=0.7, confidence="community", note=None, sources=None):
    e = {
        "id": eid,
        "from": frm,
        "to": to,
        "type": typ,
        "weight": weight,
        "confidence": confidence,
        "sources": sources or [],
        "createdAt": REVIEWED,
    }
    if note:
        e["note"] = note
    return e


def vendor(vid, name, region="overseas", url=None, note=None):
    v = {"id": vid, "name": name, "region": region}
    if url:
        v["url"] = url
    if note:
        v["note"] = note
    return v


# ---------- entries ----------
ENTRIES_DATA: list[dict] = [
    # —— ai-speech ——
    mk(
        "elevenlabs",
        "ElevenLabs",
        "ai-speech",
        "tts",
        "表达力 TTS · 克隆/配音 · Conversational AI",
        "https://elevenlabs.io",
        "ElevenLabs 以高表达力 TTS、声音克隆与配音闻名，并扩展 Scribe STT、Conversational AI 与音乐能力，是内容与语音产品常用的声音层。",
        "需要品牌旁白、多语言配音、或角色一致的语音克隆时优先评估；Flash/Turbo 档适合低延迟对话，v3 档偏媒体质量。",
        "按字符/分钟计费上升快；克隆与商用授权、deepfake 合规需法务过目；国内直连与支付可能受限。",
        vendorId="elevenlabs-inc",
        tags=["tts", "voice-clone", "asr"],
        pricing={"model": "subscription", "currency": "USD"},
    ),
    mk(
        "cartesia",
        "Cartesia",
        "ai-speech",
        "tts",
        "超低延迟流式 TTS · Sonic · 语音 Agent 常用",
        "https://cartesia.ai",
        "Cartesia 以 Sonic 系列流式 TTS 著称，强调极低 time-to-first-audio，面向实时语音 Agent 与互动应用的最后一公里合成。",
        "自建 STT→LLM→TTS 管线、且瓶颈在 TTS 首包延迟时，常与 Deepgram/LiveKit 搭配选型。",
        "生态与音色库仍在扩张；表达力与克隆深度通常不如 ElevenLabs 旗舰档，需按场景盲听对比。",
        vendorId="cartesia-inc",
        tags=["tts", "low-latency", "streaming"],
        pricing={"model": "usage", "currency": "USD"},
    ),
    mk(
        "deepgram",
        "Deepgram",
        "ai-speech",
        "asr",
        "生产级流式 STT · Nova · Aura TTS 一体",
        "https://deepgram.com",
        "Deepgram 以高精度流式语音识别（Nova 系）立足，并提供 Aura TTS 与 Voice Agent API，适合企业级转写与可编排语音管线。",
        "客服质检、会议转写、电话 Agent 需要低延迟 STT 与结构化结果时常用；HIPAA 等合规场景亦多见。",
        "中文与小语种效果需自测；纯「最美旁白」场景表达力可能不如 ElevenLabs。",
        vendorId="deepgram-inc",
        tags=["asr", "stt", "tts", "streaming"],
        pricing={"model": "usage", "currency": "USD"},
        maturity="mature",
    ),
    mk(
        "assemblyai",
        "AssemblyAI",
        "ai-speech",
        "asr",
        "结构化 STT · 说话人分离 · 实时转写",
        "https://www.assemblyai.com",
        "AssemblyAI 提供批处理与实时转写，强调说话人分离、关键术语提示与摘要等结构化能力，面向产品内嵌音视频理解。",
        "需要会议纪要、播客索引或带 diarization 的音视频流水线时评估；API 偏开发者友好。",
        "定价按小时；极致低延迟语音对话更常看 Deepgram / 原生 Realtime API。",
        vendorId="assemblyai-inc",
        tags=["asr", "stt", "diarization"],
        pricing={"model": "usage", "currency": "USD"},
    ),
    mk(
        "openai-tts",
        "OpenAI TTS",
        "ai-speech",
        "tts",
        "OpenAI Audio TTS · 简单旁白 · 生态一体",
        "https://platform.openai.com/docs/guides/text-to-speech",
        "OpenAI TTS（tts-1 / hd / gpt-4o-mini-tts 等）提供开箱即用的文本转语音，适合已在 OpenAI 栈内的旁白、助手播报与原型。",
        "已有 OpenAI 账单与 SDK、只需简单多音色朗读、不要求克隆与极致延迟时的默认选项。",
        "音色与克隆能力有限；真正实时对话应看 Realtime API，而非把标准 TTS 硬拼成 Agent。",
        vendorId="openai",
        tags=["tts", "openai"],
        pricing={"model": "usage", "currency": "USD"},
        docsUrl="https://platform.openai.com/docs/guides/text-to-speech",
        availability={
            "chinaAccessible": False,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["global"],
        },
    ),
    mk(
        "openai-whisper",
        "OpenAI Whisper / Transcribe",
        "ai-speech",
        "asr",
        "Whisper 生态 · gpt-4o-transcribe · 多语转写",
        "https://platform.openai.com/docs/guides/speech-to-text",
        "OpenAI 语音转写线从开源 Whisper 演进到托管 Transcription API（含 gpt-4o-transcribe 等），覆盖批处理与近实时多语识别。",
        "需要快速接入转写、与 GPT 同账号结算、或本地可跑开源 Whisper 权重做私有化时选用。",
        "流式电话级延迟与端点检测不如专用 STT；国内直连受限，常经 Azure 或中转。",
        vendorId="openai",
        tags=["asr", "stt", "whisper", "openai"],
        pricing={"model": "usage", "currency": "USD"},
        docsUrl="https://platform.openai.com/docs/guides/speech-to-text",
        availability={
            "chinaAccessible": False,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["global"],
        },
    ),
    mk(
        "azure-speech",
        "Azure Speech",
        "ai-speech",
        "speech-suite",
        "微软语音套件 · TTS/STT/翻译 · 企业合规",
        "https://azure.microsoft.com/products/ai-services/ai-speech",
        "Azure AI Speech 覆盖语音识别、神经 TTS、翻译与说话人识别，深度嵌入 Azure 身份、区域与合规体系。",
        "已在 Azure/微软生态、需要企业合同、数据驻留或与 Azure OpenAI 同区部署时优先。",
        "配置面宽、学习成本高于单一 TTS API；创意旁白音色库不如消费级品牌产品丰富。",
        vendorId="microsoft",
        tags=["tts", "asr", "enterprise"],
        pricing={"model": "usage", "currency": "USD"},
        maturity="mature",
    ),
    mk(
        "iflytek-speech",
        "讯飞开放平台语音",
        "ai-speech",
        "speech-suite",
        "国内语音老牌 · ASR/TTS · 方言与教育场景",
        "https://www.xfyun.cn",
        "科大讯飞开放平台提供语音听写、合成、评测与方言能力，长期服务国内教育、客服与车载等语音场景。",
        "产品面向中国大陆用户、需要中文/方言识别或国内备案合规语音能力时评估。",
        "海外语种与出海产品体验需另测；API 与套餐体系偏国内云风格，与国际语音栈接口不完全同构。",
        vendorId="iflytek",
        region="domestic",
        tags=["tts", "asr", "domestic"],
        pricing={"model": "usage", "currency": "CNY"},
        availability={
            "chinaAccessible": True,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["CN"],
        },
    ),
    mk(
        "volcengine-speech",
        "火山引擎语音",
        "ai-speech",
        "speech-suite",
        "字节系语音 · TTS/ASR · 豆包/抖音生态",
        "https://www.volcengine.com/product/voice-tech",
        "火山引擎语音技术提供合成、识别与音视频理解能力，常与豆包大模型、抖音/剪映系内容工具同生态落地。",
        "国内 App 需要中文 TTS/ASR、且已用火山或字节云时优先 POC；适合内容与互动场景。",
        "海外节点与文档相对少；企业采购需确认数据出境与模型版本锁定。",
        vendorId="bytedance",
        region="domestic",
        tags=["tts", "asr", "domestic", "volcengine"],
        pricing={"model": "usage", "currency": "CNY"},
        availability={
            "chinaAccessible": True,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["CN"],
        },
    ),
    mk(
        "minimax-speech",
        "MiniMax 语音",
        "ai-speech",
        "tts",
        "MiniMax Speech · 中文角色音色 · 国内 API",
        "https://www.minimaxi.com",
        "MiniMax 在文本大模型之外提供语音合成与音色能力，强调中文表现力与角色一致性，面向国内 ToB 与互动娱乐。",
        "国内需要高质量中文旁白/角色语音、并可能同栈使用 MiniMax 文本或视频能力时评估。",
        "国际语种与文档生态弱于 ElevenLabs；生产前需锁定音色与 endpoint 版本。",
        vendorId="minimax-inc",
        region="domestic",
        tags=["tts", "domestic", "voice"],
        pricing={"model": "usage", "currency": "CNY"},
        availability={
            "chinaAccessible": True,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["CN"],
        },
    ),
    mk(
        "fish-audio",
        "Fish Audio",
        "ai-speech",
        "tts",
        "开源友好 TTS · 克隆 · 社区常用",
        "https://fish.audio",
        "Fish Audio 提供语音合成与克隆相关能力，在开源/社区与中文开发者中常见，适合快速试验角色音色与本地化旁白。",
        "需要低成本试用克隆音色、或社区模型与 API 结合的原型阶段可评估。",
        "企业 SLA、合规与商用授权成熟度需逐案核对；勿默认等同于 ElevenLabs 级生产保障。",
        vendorId="fish-audio-inc",
        tags=["tts", "voice-clone", "community"],
        pricing={"model": "freemium"},
    ),
    # —— ai-realtime ——
    mk(
        "openai-realtime",
        "OpenAI Realtime API",
        "ai-realtime",
        "speech-to-speech",
        "原生语音到语音 · 打断/工具调用 · 低延迟会话",
        "https://platform.openai.com/docs/guides/realtime",
        "OpenAI Realtime API 以原生 speech-to-speech 会话为核心，支持打断、工具调用与 WebSocket/WebRTC，避免自拼 STT→LLM→TTS 的状态撕裂。",
        "语音即界面、需要自然轮次与工具编排、且团队已在 OpenAI 生态时优先；电话/客服 Agent 常见底座。",
        "按音频 token 计费；国内直连受限；若只要模块化 ASR/TTS 可控性，模块管线可能更透明。",
        vendorId="openai",
        tags=["realtime", "voice-agent", "openai", "webrtc"],
        pricing={"model": "usage", "currency": "USD"},
        docsUrl="https://platform.openai.com/docs/guides/realtime",
        availability={
            "chinaAccessible": False,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["global"],
        },
    ),
    mk(
        "gemini-live",
        "Gemini Live",
        "ai-realtime",
        "speech-to-speech",
        "Gemini 实时多模态 · 语音+视觉 · 多语",
        "https://ai.google.dev/gemini-api/docs/live",
        "Gemini Live（Flash Live 等）提供实时多模态会话，覆盖语音与视觉输入，强调低延迟与广泛语种，适合 Google 生态内的语音助手。",
        "需要「边看边说」多模态、或语种覆盖面优先、且已用 Gemini/GCP 时评估。",
        "国内访问 Google API 需网络与合规方案；复杂工具编排与电话栈成熟度需对照 OpenAI Realtime / LiveKit。",
        vendorId="google",
        tags=["realtime", "multimodal", "gemini"],
        pricing={"model": "usage", "currency": "USD"},
        docsUrl="https://ai.google.dev/gemini-api/docs/live",
        availability={
            "chinaAccessible": False,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["global"],
        },
    ),
    mk(
        "livekit",
        "LiveKit",
        "ai-realtime",
        "realtime-infra",
        "开源实时音视频 · Agents 框架 · WebRTC",
        "https://livekit.io",
        "LiveKit 提供开源 WebRTC 实时音视频基础设施与 Agents 框架，可编排 STT/LLM/TTS 或对接原生 Realtime 模型，自托管与云服务并存。",
        "需要可控媒体层、多参与者房间、或把多家语音模型拼成生产 Agent 时优先；与 Cartesia/Deepgram 常见搭配。",
        "自托管需运维 SFU 与带宽；纯「一键电话 Agent」比 Vapi/Retell 更偏基础设施。",
        vendorId="livekit-inc",
        tags=["webrtc", "realtime", "agents", "open-source"],
        pricing={"model": "freemium"},
        githubUrl="https://github.com/livekit/livekit",
    ),
    mk(
        "vapi",
        "Vapi",
        "ai-realtime",
        "voice-agent-platform",
        "语音 Agent 编排平台 · 可插拔模型 · 电话",
        "https://vapi.ai",
        "Vapi 是面向开发者的语音 Agent 平台，支持自选 STT/LLM/TTS、电话接入与工作流编排，强调快速上线可通话的助手。",
        "要尽快上线来电/外呼 Agent、又不想自建 WebRTC 与电话栈时评估；组件可替换适合迭代。",
        "平台抽成与供应商锁定需算清；极端延迟与合规场景可能要下沉到 LiveKit + 自管模型。",
        vendorId="vapi-inc",
        tags=["voice-agent", "telephony", "orchestration"],
        pricing={"model": "usage", "currency": "USD"},
    ),
    mk(
        "retell-ai",
        "Retell AI",
        "ai-realtime",
        "voice-agent-platform",
        "电话语音 Agent · 低延迟 · 业务编排",
        "https://www.retellai.com",
        "Retell AI 专注电话场景的语音 Agent，提供低延迟会话、业务工作流与监控，面向销售/客服自动化来电与外呼。",
        "北美/英语电话 Agent、需要开箱电话能力与仪表盘时常见选项；与 Vapi 同类可比。",
        "中文与国内线路支持有限；深度定制媒体层仍可能回到 LiveKit/自建。",
        vendorId="retell-inc",
        tags=["voice-agent", "telephony"],
        pricing={"model": "usage", "currency": "USD"},
    ),
    # —— design-ai-video ——
    mk(
        "kling",
        "可灵 Kling",
        "design-ai-video",
        "video-gen",
        "快手可灵 · 文/图生视频 · 国内高频",
        "https://klingai.com",
        "可灵（Kling）是快手系 AI 视频生成产品，支持文生视频与图生视频，国内创作者与营销团队使用频率高，质量与时长持续迭代。",
        "面向中国大陆用户的短视频/广告素材、或需要国内可达的 AI video 时优先 POC。",
        "商用授权与水印策略随套餐变化；出海品牌需核对素材合规与平台条款。",
        vendorId="kuaishou",
        region="domestic",
        tags=["ai", "video", "domestic"],
        pricing={"model": "subscription", "currency": "CNY"},
        availability={
            "chinaAccessible": True,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["CN"],
        },
    ),
    mk(
        "luma-ai",
        "Luma Dream Machine",
        "design-ai-video",
        "video-gen",
        "Luma 视频生成 · 速度快 · 3D/创意向",
        "https://lumalabs.ai/dream-machine",
        "Luma Dream Machine 提供文/图生视频，强调生成速度与创意控制，并与 Luma 的 3D/NeRF 能力叙事相邻，适合概念片与产品预演。",
        "需要较快出片、创意 previs 或与 3D 工作流衔接时评估；海外 indie 常用。",
        "按积分/订阅计费；长镜头一致性与商用授权需逐案确认。",
        vendorId="luma-labs",
        tags=["ai", "video"],
        pricing={"model": "freemium", "currency": "USD"},
    ),
    mk(
        "pika",
        "Pika",
        "design-ai-video",
        "video-gen",
        "Pika 文/图生视频 · 社交短视频向",
        "https://pika.art",
        "Pika 面向创作者的 AI 视频工具，支持文生/图生与多种特效修改，偏社交短视频、梗图动态化与轻量营销素材场景。",
        "营销/社媒需要快速把静态创意做成短视频、且接受订阅积分制时试用；与 Runway/Luma 可同层对比。",
        "影视级控制力弱于专业管线；版权与人物相似性合规要审核。",
        vendorId="pika-labs",
        tags=["ai", "video", "social"],
        pricing={"model": "subscription", "currency": "USD"},
    ),
    mk(
        "hailuo",
        "海螺视频",
        "design-ai-video",
        "video-gen",
        "MiniMax 海螺 · 国内视频生成",
        "https://hailuoai.com",
        "海螺视频是 MiniMax 旗下 AI 视频生成产品，面向国内用户提供文/图生视频，常与 MiniMax 模型与语音能力形成内容生产闭环。",
        "国内团队需要中文 prompt 友好、与 MiniMax 同账号生态的视频生成时评估。",
        "海外发行与长视频稳定性需自测；积分消耗与并发限制影响批量生产。",
        vendorId="minimax-inc",
        region="domestic",
        tags=["ai", "video", "domestic"],
        pricing={"model": "freemium", "currency": "CNY"},
        availability={
            "chinaAccessible": True,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["CN"],
        },
    ),
    mk(
        "vidu",
        "Vidu",
        "design-ai-video",
        "video-gen",
        "生数 Vidu · 国内文生视频",
        "https://www.vidu.com",
        "Vidu 由生数科技推出，提供 AI 视频生成能力，面向国内创作者与企业营销素材场景，强调中文语境与本地化体验。",
        "需要国内可达的竞品对比（相对可灵/海螺）或特定风格样本时纳入选型短名单。",
        "生态与插件仍在扩张；商用条款与 API 成熟度需对照官网最新说明。",
        vendorId="shengshu",
        region="domestic",
        tags=["ai", "video", "domestic"],
        pricing={"model": "freemium", "currency": "CNY"},
        availability={
            "chinaAccessible": True,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["CN"],
        },
    ),
    mk(
        "openai-sora",
        "Sora",
        "design-ai-video",
        "video-gen",
        "OpenAI 视频生成 · 高保真叙事 · 生态绑定",
        "https://openai.com/sora",
        "Sora 是 OpenAI 的文生视频产品线，强调高保真运动与叙事连贯，常作为海外旗舰视频生成参照，接入与配额随 ChatGPT/API 产品策略变化。",
        "已在 OpenAI 生态、需要旗舰级演示片或研究级样本时关注；具体 API/产品形态以官方当前开放为准。",
        "可用性与区域政策变化快；成本高，生产批量素材更常看 Kling/Runway/Luma 等。",
        vendorId="openai",
        tags=["ai", "video", "openai"],
        pricing={"model": "subscription", "currency": "USD"},
        availability={
            "chinaAccessible": False,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["global"],
        },
        maturity="beta",
    ),
    # —— design-ai-music ——
    mk(
        "suno",
        "Suno",
        "design-ai-music",
        "music-gen",
        "文生歌曲 · 人声+伴奏 · 创作者向",
        "https://suno.com",
        "Suno 以文本生成完整歌曲（人声与伴奏）著称，创作者与营销快速出 demo 曲、BGM 草稿时使用广泛。",
        "需要带歌词的完整曲目草稿、播客/短视频临时配乐时评估；订阅制常见。",
        "商用授权与唱片工业版权争议需法务关注；风格同质化后品牌项目应定制。",
        vendorId="suno-inc",
        tags=["ai", "music"],
        pricing={"model": "subscription", "currency": "USD"},
    ),
    mk(
        "udio",
        "Udio",
        "design-ai-music",
        "music-gen",
        "AI 音乐生成 · 人声表现力 · Suno 对标",
        "https://www.udio.com",
        "Udio 提供 AI 音乐与歌声生成，强调音色表现与风格控制，常与 Suno 并列为文生歌曲选型对照。",
        "需要对比不同 AI 音乐厂商的人声/编曲风格、或特定曲风样本时纳入短名单。",
        "授权条款与平台政策变动快；勿将生成曲直接当无风险商用发行。",
        vendorId="udio-inc",
        tags=["ai", "music"],
        pricing={"model": "freemium", "currency": "USD"},
    ),
    # —— design-ai-image 补强 ——
    mk(
        "openai-gpt-image",
        "GPT Image / DALL·E",
        "design-ai-image",
        "image-gen",
        "OpenAI 文生图 · ChatGPT/API · 生态一体",
        "https://platform.openai.com/docs/guides/images",
        "OpenAI 图像生成线（历史上 DALL·E，现多以 GPT Image / Images API 形态演进）与 ChatGPT、API 深度集成，适合产品内嵌出图与助手配图。",
        "已用 OpenAI 栈、需要对话式改图或简单营销图时的默认选项；与 Midjourney 比更偏 API/产品集成。",
        "艺术风格上限常低于 Midjourney；国内直连受限；内容策略与拒图规则需适配产品 UX。",
        vendorId="openai",
        tags=["ai", "image", "openai"],
        pricing={"model": "usage", "currency": "USD"},
        docsUrl="https://platform.openai.com/docs/guides/images",
        availability={
            "chinaAccessible": False,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["global"],
        },
    ),
    mk(
        "google-imagen",
        "Imagen",
        "design-ai-image",
        "image-gen",
        "Google 文生图 · Vertex/Gemini · 企业向",
        "https://deepmind.google/technologies/imagen/",
        "Imagen 是 Google 的文生图模型族，经 Vertex AI / Gemini 生态提供，强调与 Google Cloud 企业合同、安全过滤与多模态管线集成。",
        "已在 GCP、需要企业级图像生成与统一计费时评估；可与 Gemini 多模态应用同栈。",
        "国内访问受限；消费级审美社区热度通常低于 Midjourney/Flux。",
        vendorId="google",
        tags=["ai", "image", "gcp"],
        pricing={"model": "usage", "currency": "USD"},
        availability={
            "chinaAccessible": False,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["global"],
        },
    ),
    mk(
        "tongyi-wanxiang",
        "通义万相",
        "design-ai-image",
        "image-gen",
        "阿里通义文生图 · 国内云 · 电商素材",
        "https://tongyi.aliyun.com/wanxiang/",
        "通义万相是阿里云通义系文生图产品，面向国内开发者与电商/营销素材场景，可与阿里云账号与备案业务同区落地。",
        "国内电商主图、活动视觉、且已用阿里云时优先；与即梦等形成国内可选池。",
        "艺术风格社区口碑因场景而异；API 字段与计费以阿里云文档为准，注意内容安全审核。",
        vendorId="alibaba-cloud",
        region="domestic",
        tags=["ai", "image", "domestic"],
        pricing={"model": "usage", "currency": "CNY"},
        availability={
            "chinaAccessible": True,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["CN"],
        },
    ),
    mk(
        "kolors",
        "可图 Kolors",
        "design-ai-image",
        "image-gen",
        "快手可图 · 开源权重 · 国内文生图",
        "https://github.com/Kwai-Kolors/Kolors",
        "可图（Kolors）是快手系文生图模型，提供开源权重与平台侧生成体验，常与可灵视频同生态出现在国内创意生产链路。",
        "国内需要文生图且可能与可灵视频串联、或希望自托管开源权重时评估。",
        "产品入口与品牌叙事可能随可灵平台整合变化；商用与开源许可分开核对。",
        vendorId="kuaishou",
        region="domestic",
        tags=["ai", "image", "domestic", "open-source"],
        pricing={"model": "freemium", "currency": "CNY"},
        githubUrl="https://github.com/Kwai-Kolors/Kolors",
        availability={
            "chinaAccessible": True,
            "needsCompany": False,
            "needsIcp": False,
            "regions": ["CN"],
        },
    ),
]

VENDORS_DATA: list[dict] = [
    vendor("elevenlabs-inc", "ElevenLabs", url="https://elevenlabs.io"),
    vendor("cartesia-inc", "Cartesia", url="https://cartesia.ai"),
    vendor("deepgram-inc", "Deepgram", url="https://deepgram.com"),
    vendor("assemblyai-inc", "AssemblyAI", url="https://www.assemblyai.com"),
    vendor("iflytek", "科大讯飞", region="domestic", url="https://www.xfyun.cn"),
    vendor("fish-audio-inc", "Fish Audio", url="https://fish.audio"),
    vendor("livekit-inc", "LiveKit", url="https://livekit.io"),
    vendor("vapi-inc", "Vapi", url="https://vapi.ai"),
    vendor("retell-inc", "Retell AI", url="https://www.retellai.com"),
    vendor("kuaishou", "快手", region="domestic", url="https://www.kuaishou.com"),
    vendor("luma-labs", "Luma AI", url="https://lumalabs.ai"),
    vendor("pika-labs", "Pika Labs", url="https://pika.art"),
    vendor("shengshu", "生数科技", region="domestic", url="https://www.vidu.com"),
    vendor("suno-inc", "Suno", url="https://suno.com"),
    vendor("udio-inc", "Udio", url="https://www.udio.com"),
]

EDGES_DATA: list[dict] = [
    # speech alternatives
    edge("edge-elevenlabs-cartesia-alt", "elevenlabs", "cartesia", "alternative_to", note="表达力 vs 极致延迟"),
    edge("edge-elevenlabs-openai-tts-alt", "elevenlabs", "openai-tts", "alternative_to"),
    edge("edge-cartesia-openai-tts-alt", "cartesia", "openai-tts", "alternative_to", note="低延迟流式 vs 简单旁白"),
    edge("edge-deepgram-assemblyai-alt", "deepgram", "assemblyai", "alternative_to", note="流式生产 STT 对照"),
    edge("edge-deepgram-whisper-alt", "deepgram", "openai-whisper", "alternative_to"),
    edge("edge-assemblyai-whisper-alt", "assemblyai", "openai-whisper", "alternative_to"),
    edge("edge-minimax-speech-eleven-dom", "minimax-speech", "elevenlabs", "domestic_equivalent_of"),
    edge("edge-volc-speech-eleven-dom", "volcengine-speech", "elevenlabs", "domestic_equivalent_of"),
    edge("edge-iflytek-azure-dom", "iflytek-speech", "azure-speech", "domestic_equivalent_of", note="国内语音套件 vs 微软企业语音"),
    edge("edge-fish-eleven-alt", "fish-audio", "elevenlabs", "alternative_to", weight=0.55),
    edge("edge-deepgram-cartesia-with", "deepgram", "cartesia", "commonly_used_with", note="STT+低延迟 TTS 管线"),
    edge("edge-openai-tts-whisper-with", "openai-tts", "openai-whisper", "commonly_used_with", note="同属 OpenAI Audio"),
    # realtime
    edge("edge-openai-rt-gemini-live-alt", "openai-realtime", "gemini-live", "alternative_to", note="原生 S2S 对照"),
    edge("edge-vapi-retell-alt", "vapi", "retell-ai", "alternative_to", note="电话 Agent 平台对照"),
    edge("edge-livekit-vapi-alt", "livekit", "vapi", "alternative_to", note="自建媒体层 vs 托管编排"),
    edge("edge-vapi-openai-rt-with", "vapi", "openai-realtime", "commonly_used_with"),
    edge("edge-livekit-cartesia-with", "livekit", "cartesia", "commonly_used_with"),
    edge("edge-livekit-deepgram-with", "livekit", "deepgram", "commonly_used_with"),
    edge("edge-openai-rt-partof-openai", "openai-realtime", "openai-tts", "commonly_used_with", note="同厂商语音能力；选型勿混用场景"),
    # video
    edge("edge-kling-runway-dom", "kling", "runway", "domestic_equivalent_of"),
    edge("edge-hailuo-runway-dom", "hailuo", "runway", "domestic_equivalent_of"),
    edge("edge-vidu-runway-dom", "vidu", "runway", "domestic_equivalent_of"),
    edge("edge-luma-runway-alt", "luma-ai", "runway", "alternative_to"),
    edge("edge-pika-runway-alt", "pika", "runway", "alternative_to"),
    edge("edge-sora-runway-alt", "openai-sora", "runway", "alternative_to", weight=0.65),
    edge("edge-kling-hailuo-alt", "kling", "hailuo", "alternative_to"),
    edge("edge-kling-vidu-alt", "kling", "vidu", "alternative_to"),
    edge("edge-hailuo-minimax-owned", "hailuo", "minimax-inc", "owned_by", note="海螺属 MiniMax 产品线"),
    # music
    edge("edge-suno-udio-alt", "suno", "udio", "alternative_to"),
    # image
    edge("edge-gpt-image-mj-alt", "openai-gpt-image", "midjourney", "alternative_to"),
    edge("edge-imagen-mj-alt", "google-imagen", "midjourney", "alternative_to"),
    edge("edge-wanxiang-mj-dom", "tongyi-wanxiang", "midjourney", "domestic_equivalent_of"),
    edge("edge-kolors-mj-dom", "kolors", "midjourney", "domestic_equivalent_of"),
    edge("edge-wanxiang-jimeng-alt", "tongyi-wanxiang", "jimeng", "alternative_to"),
    edge("edge-kolors-jimeng-alt", "kolors", "jimeng", "alternative_to"),
    edge("edge-kling-kolors-with", "kling", "kolors", "commonly_used_with", note="快手创意同生态"),
]


def write_item(dir_path: Path, item: dict, overwrite: bool) -> bool:
    path = dir_path / f"{item['id']}.json"
    if path.exists() and not overwrite:
        return False
    save(path, item)
    return True


def migrate_runway() -> None:
    path = ENTRIES / "runway.json"
    if not path.exists():
        print("migrate skip: runway missing")
        return
    e = json.loads(path.read_text(encoding="utf-8"))
    changed = False
    if e.get("category") != "design-ai-video":
        e["category"] = "design-ai-video"
        changed = True
    if e.get("subcategory") != "video-gen":
        e["subcategory"] = "video-gen"
        changed = True
    e["lastReviewed"] = REVIEWED
    if changed:
        save(path, e)
        print("migrate: runway → design-ai-video")
    else:
        print("migrate: runway already on design-ai-video")


def ensure_vendor_exists(vendors_needed: set[str]) -> None:
    """部分 vendor（openai/google/bytedance 等）应已存在；缺失则告警。"""
    existing = {p.stem for p in VENDORS.glob("*.json")}
    missing = sorted(vendors_needed - existing)
    if missing:
        print(f"warn: missing vendors (will fail validate if referenced): {missing}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    migrate_runway()

    entry_added = vendor_added = edge_added = 0
    for e in ENTRIES_DATA:
        if write_item(ENTRIES, e, args.overwrite):
            entry_added += 1
    for v in VENDORS_DATA:
        if write_item(VENDORS, v, args.overwrite):
            vendor_added += 1
    for ed in EDGES_DATA:
        if write_item(EDGES, ed, args.overwrite):
            edge_added += 1

    needed = {e.get("vendorId") for e in ENTRIES_DATA if e.get("vendorId")}
    needed |= {v["id"] for v in VENDORS_DATA}
    # owned_by 等边可能指向 vendor
    for ed in EDGES_DATA:
        if ed["type"] == "owned_by":
            needed.add(ed["to"])
    ensure_vendor_exists({x for x in needed if x})

    print(
        f"done: +entries={entry_added} +vendors={vendor_added} +edges={edge_added} "
        f"total_entries={len(list(ENTRIES.glob('*.json')))} "
        f"total_edges={len(list(EDGES.glob('*.json')))} "
        f"total_vendors={len(list(VENDORS.glob('*.json')))}"
    )


if __name__ == "__main__":
    main()
