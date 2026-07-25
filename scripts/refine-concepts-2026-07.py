#!/usr/bin/env python3
"""精炼概念库：降噪别名 + 补齐 AI/多媒体等高频术语。

用法:
  python3 scripts/refine-concepts-2026-07.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONCEPTS = ROOT / "content" / "concepts"

# id -> patch（合并进现有文件；aliases 为完整替换列表）
PATCHES: dict[str, dict] = {
    "image": {
        "name": "容器镜像",
        "summaryMd": "容器或虚机的不可变构建产物（Container Image），不是普通图片。",
        "aliases": ["Container Image", "container image", "OCI Image"],
    },
    "ecosystem": {
        "name": "技术生态",
        "summaryMd": "围绕核心产品形成的插件、集成、社区与上下游工具链。",
        "aliases": ["ecosystem", "开发者生态", "产品生态"],
    },
    "workflow": {
        "name": "workflow",
        "summaryMd": "把多步任务编排成可复用、可观测的流程。",
        "aliases": ["Workflow", "工作流引擎", "workflow engine"],
    },
    "managed": {
        "name": "managed service",
        "summaryMd": "由云厂商运维的托管服务，减少自建负担。",
        "aliases": ["Managed Service", "托管服务", "全托管"],
    },
    "orchestration-cn": {
        "name": "国内编排",
        "summaryMd": "面向国内合规与网络环境的工作流/任务编排方案。",
        "aliases": ["国产编排", "国内工作流编排"],
    },
    "orchestrator": {
        "name": "orchestrator",
        "summaryMd": "负责任务调度与多步骤协调的编排器组件。",
        "aliases": ["Orchestrator", "编排器", "编排引擎"],
    },
    "ui": {
        "name": "UI",
        "summaryMd": "用户界面（User Interface）。",
        "aliases": ["User Interface", "用户界面"],
    },
    "ux": {
        "name": "UX",
        "summaryMd": "用户体验（User Experience）。",
        "aliases": ["User Experience", "用户体验"],
    },
    "dx": {
        "name": "DX",
        "summaryMd": "开发者体验（Developer Experience）。",
        "aliases": ["Developer Experience", "开发者体验"],
    },
    "token": {
        "name": "Token",
        "summaryMd": "模型计费与上下文的基本单位，通常小于一个词。",
        "aliases": ["token", "上下文 token", "token 计费"],
    },
    "cache": {
        "name": "cache",
        "summaryMd": "用更快介质暂存热点数据以降低延迟与成本。",
        "aliases": ["Cache", "缓存层", "cache layer"],
    },
    "prompt-cn": {
        "name": "提示词",
        "summaryMd": "给模型的自然语言指令与上下文。",
        "aliases": ["Prompt", "prompt", "用户提示", "提示工程"],
    },
    "vector-db": {
        "name": "vector database",
        "summaryMd": "专为向量相似度检索优化的数据库或索引服务。",
        "aliases": ["向量数据库", "vector db", "Vector DB", "向量检索"],
    },
    "agent": {
        "name": "Agent",
        "summaryMd": "能调用工具、规划步骤并自主完成任务的 AI 代理形态。",
        "aliases": ["AI Agent", "智能体", "Agents"],
    },
    "function-calling": {
        "name": "function calling",
        "summaryMd": "模型按约定发起工具/函数调用，由运行时执行后再回填。",
        "aliases": [
            "Function Calling",
            "函数调用",
            "tool calling",
            "工具调用",
            "Tool Calling",
        ],
    },
    "open-source": {
        "name": "open source",
        "summaryMd": "源码公开、允许研究与再分发的许可模式。",
        "aliases": ["开源", "Open Source", "开源可自托管", "开源权重"],
    },
    "inference": {
        "name": "inference",
        "summaryMd": "用已训练模型做预测/生成的服务阶段（相对训练）。",
        "aliases": ["Inference", "模型推理", "推理服务", "推理侧"],
    },
    "eval": {
        "name": "eval",
        "summaryMd": "用基准或人工评估衡量模型/系统质量。",
        "aliases": ["Eval", "模型评测", "评测集", "evaluation"],
    },
    "embedding": {
        "name": "embedding",
        "summaryMd": "把文本/图像等映射为稠密向量以便检索与聚类。",
        "aliases": ["Embedding", "向量嵌入", "文本嵌入"],
    },
    "fine-tuning": {
        "name": "fine-tuning",
        "summaryMd": "在预训练模型上用领域数据继续训练以适配任务。",
        "aliases": ["Fine-tuning", "微调", "模型微调"],
    },
    "hallucination": {
        "name": "hallucination",
        "summaryMd": "模型生成看似合理但事实错误或无依据的内容。",
        "aliases": ["Hallucination", "幻觉", "模型幻觉"],
    },
    "billing": {
        "name": "billing",
        "summaryMd": "用量计量、套餐与出账相关的商业计费能力。",
        "aliases": ["Billing", "按量计费", "计费系统", "用量计费"],
    },
    "backup": {
        "name": "backup",
        "summaryMd": "为恢复而保留的数据副本与快照策略。",
        "aliases": ["Backup", "数据备份", "备份策略", "快照备份"],
    },
    "container": {
        "name": "container",
        "summaryMd": "轻量隔离的运行时封装，常与镜像、编排一起出现。",
        "aliases": ["Container", "容器运行时", "Linux 容器"],
    },
    "latency": {
        "name": "latency",
        "summaryMd": "请求从发起到响应的时间延迟。",
        "aliases": ["Latency", "端到端延迟", "低延迟"],
    },
    "concurrency": {
        "name": "concurrency",
        "summaryMd": "同一时段内并行处理多个任务的能力。",
        "aliases": ["Concurrency", "高并发", "并发模型"],
    },
    "parallelism": {
        "name": "parallelism",
        "summaryMd": "把工作拆成可同时执行的部分以提升吞吐。",
        "aliases": ["Parallelism", "并行计算", "数据并行"],
    },
}

NEW: list[dict] = [
    {
        "id": "text-to-image",
        "name": "文生图",
        "summaryMd": "由文本提示生成图像（Text-to-Image / T2I）。",
        "aliases": ["text-to-image", "Text-to-Image", "T2I", "文本生成图像"],
    },
    {
        "id": "image-to-image",
        "name": "图生图",
        "summaryMd": "以图像（+可选文本）为条件生成或改图（Image-to-Image / I2I）。",
        "aliases": ["image-to-image", "Image-to-Image", "I2I", "图像编辑生成"],
    },
    {
        "id": "text-to-video",
        "name": "文生视频",
        "summaryMd": "由文本提示生成视频（Text-to-Video / T2V）。",
        "aliases": ["text-to-video", "Text-to-Video", "T2V", "文本生成视频"],
    },
    {
        "id": "image-to-video",
        "name": "图生视频",
        "summaryMd": "以图像为条件生成视频（Image-to-Video / I2V）。",
        "aliases": ["image-to-video", "Image-to-Video", "I2V", "图像生成视频"],
    },
    {
        "id": "agentic",
        "name": "agentic",
        "summaryMd": "强调工具调用、规划与自迭代的代理式（agentic）能力，而不只是单次生成。",
        "aliases": ["Agentic", "代理式", "agentic 工作流"],
    },
    {
        "id": "multimodal",
        "name": "多模态",
        "summaryMd": "同一模型或系统处理文本、图像、音视频等多种模态输入/输出。",
        "aliases": ["multimodal", "Multimodal", "多模态模型"],
    },
    {
        "id": "diffusion",
        "name": "Diffusion",
        "summaryMd": "以逐步去噪为核心的生成范式，广泛用于图像与视频模型。",
        "aliases": ["diffusion", "扩散模型", "Diffusion Model"],
    },
    {
        "id": "arena-eval",
        "name": "Arena 评测",
        "summaryMd": "以盲选对战（如 LM Arena）汇聚偏好投票的模型评测方式。",
        "aliases": ["Arena", "LM Arena", "LMArena", "竞技场评测"],
    },
    {
        "id": "api",
        "name": "API",
        "summaryMd": "应用程序接口：以 HTTP/SDK 等方式程序化调用服务能力。",
        "aliases": ["api", "HTTP API", "REST API"],
    },
]


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    CONCEPTS.mkdir(parents=True, exist_ok=True)
    patched = 0
    for cid, patch in PATCHES.items():
        path = CONCEPTS / f"{cid}.json"
        if not path.exists():
            print(f"skip missing {cid}")
            continue
        cur = json.loads(path.read_text(encoding="utf-8"))
        cur.update(patch)
        cur["id"] = cid
        save(path, cur)
        patched += 1

    created = 0
    for item in NEW:
        path = CONCEPTS / f"{item['id']}.json"
        if path.exists():
            # 仍刷新内容，保证 aliases 完整
            cur = json.loads(path.read_text(encoding="utf-8"))
            cur.update(item)
            save(path, cur)
            patched += 1
        else:
            save(path, item)
            created += 1

    print(f"patched={patched} created={created} total_concepts={len(list(CONCEPTS.glob('*.json')))}")


if __name__ == "__main__":
    main()
