import type { MediaItem, ModelItem, PaperItem, RepoItem, TrendItem } from "./types";

export const trends: TrendItem[] = [
  {
    id: "trajectory-quality",
    rank: 1,
    title: "Agent evaluation is shifting from answer quality to trajectory quality",
    summary: "The new production unit is the full path: retrieval, tool calls, intermediate state, recovery behavior, latency, and cost — not just the final answer.",
    signal: "AEM + trajectory cost",
    category: "Agents",
    source: "AWS Machine Learning",
    sourceKind: "Research",
    score: 98,
    published: "Today · 2h ago",
    tags: ["Evals", "Observability", "Production"],
    href: "https://aws.amazon.com/blogs/machine-learning/",
  },
  {
    id: "prefix-routing",
    rank: 2,
    title: "Prefix-aware routing turns KV-cache locality into a scheduler input",
    summary: "Routing repeated prompt prefixes back to warm instances pushed cache hit rate above 80% and cut P50 time-to-first-token by up to 77% in AWS tests.",
    signal: "77% lower P50 TTFT",
    category: "Infrastructure",
    source: "Amazon SageMaker",
    sourceKind: "Product",
    score: 94,
    published: "Today · 4h ago",
    tags: ["Inference", "KV cache", "vLLM"],
    href: "https://aws.amazon.com/blogs/machine-learning/reduce-llm-latency-with-prefix-aware-routing-on-amazon-sagemaker-inference/",
  },
  {
    id: "hydrafusion",
    rank: 3,
    title: "Multi-model orchestration can beat one frontier model",
    summary: "HydraFusion routes planning, specialist execution, verification, and escalation to different models inside a single coding trajectory.",
    signal: "Planner → specialist → verifier",
    category: "Agents",
    source: "GitHub Next",
    sourceKind: "GitHub",
    score: 91,
    published: "Today · 6h ago",
    tags: ["Routing", "Coding agents", "Cost"],
    href: "https://github.blog/ai-and-ml/github-copilot/project-hydrafusion-frontier-quality-via-multi-model-orchestration/",
  },
  {
    id: "two-layer-monitoring",
    rank: 4,
    title: "Production agent monitoring is becoming a two-layer system",
    summary: "Application quality signals now sit beside infrastructure signals, separating reasoning failures from retrieval, tool, model, and runtime failures.",
    signal: "Quality + runtime telemetry",
    category: "Agents",
    source: "AWS AgentCore",
    sourceKind: "Product",
    score: 88,
    published: "Today · 8h ago",
    tags: ["Tracing", "MCP", "Reliability"],
    href: "https://aws.amazon.com/blogs/machine-learning/",
  },
  {
    id: "edge0",
    rank: 5,
    title: "Sparse models keep growing while active compute stays small",
    summary: "Edge0-35B-A3B joins the latest wave of models that separate total capacity from per-token active compute — a strong signal for edge serving.",
    signal: "35B total · 3B active",
    category: "Models",
    source: "Hugging Face Trending",
    sourceKind: "Hugging Face",
    score: 84,
    published: "Today · 10h ago",
    tags: ["MoE", "Edge", "Open weights"],
    href: "https://huggingface.co/models?sort=trending",
  },
  {
    id: "latent-reasoning",
    rank: 6,
    title: "Latent-space reasoning asks if more thinking needs more tokens",
    summary: "Pathway’s BDH direction explores recurrent computation in latent space rather than exposing every intermediate step as autoregressive text.",
    signal: "Post-Transformer research",
    category: "Research",
    source: "Pathway / AWS",
    sourceKind: "Research",
    score: 79,
    published: "Today · 11h ago",
    tags: ["Reasoning", "Efficiency", "Architecture"],
    href: "https://aws.amazon.com/blogs/machine-learning/category/artificial-intelligence/sagemaker/amazon-sagemaker-hyperpod/",
  },
];

export const hotModels: ModelItem[] = [
  { name: "DeepSeek-V4.1-Flash", org: "DeepSeek", detail: "244K downloads", momentum: "+42%", accent: "violet" },
  { name: "MiniCPM5-2B", org: "OpenBMB", detail: "150K downloads", momentum: "+124%", accent: "orange" },
  { name: "Edge0-35B-A3B", org: "Edge", detail: "35B / 3B active", momentum: "new", accent: "cyan" },
  { name: "Qwen3.8-27B", org: "Alibaba", detail: "Long-context MoE", momentum: "+18%", accent: "lime" },
];

export const hotPapers: PaperItem[] = [
  { title: "Agent Evaluation Metric (AEM)", authors: "AWS AI/ML Engineering", metric: "trajectory-first", note: "Decomposes multi-turn failures into their earliest causal turn.", href: "https://aws.amazon.com/blogs/machine-learning/" },
  { title: "Harness-of-Harness", authors: "OpenAI · Codex · DeepSeek", metric: "+52.25%", note: "Iterative harness improvement over standalone agent runtimes.", href: "https://arxiv.org/abs/2609.01481" },
  { title: "BDH-CQ", authors: "Pathway Research", metric: "ARC-AGI-1", note: "A brain-inspired route to latent recurrent reasoning.", href: "https://aws.amazon.com/blogs/machine-learning/" },
];

export const risingRepos: RepoItem[] = [
  { name: "project-hydrafusion", description: "Multi-model orchestration for coding agents.", stars: "8.4k", language: "Python", href: "https://github.blog/ai-and-ml/github-copilot/project-hydrafusion-frontier-quality-via-multi-model-orchestration/" },
  { name: "i-have-adhd", description: "Action-first communication patterns for coding agents.", stars: "13.2k", language: "Prompting", href: "https://github.com/ayghri/i-have-adhd" },
  { name: "vllm", description: "Fast and easy-to-use LLM inference and serving.", stars: "45.1k", language: "Python", href: "https://github.com/vllm-project/vllm" },
];

export const media: MediaItem[] = [
  { title: "How to evaluate an agent trajectory", type: "Video", duration: "18 min", meta: "AWS ML Engineering", href: "https://aws.amazon.com/blogs/machine-learning/" },
  { title: "The stack around the model", type: "Podcast", duration: "32 min", meta: "Signal Intelligence", href: "https://www.youtube.com/" },
  { title: "GPT-6 Astra: what changed in agents", type: "Video", duration: "24 min", meta: "AI Explained", href: "https://www.youtube.com/" },
];

export const topics = ["Agents", "LLM infra", "Models", "MLOps", "Multimodal", "Creative AI", "Evaluation", "Open source"];
