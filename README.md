# AgentRadar

Minimal scanner for public Python projects that use LangGraph.

It treats two fields as authoritative:

- `langgraph_status=confirmed` means Python source imports `langgraph`.
- `github_stars` comes directly from the GitHub repository API.

Everything else is a conservative static-analysis attempt. Unknown or dynamic values stay unknown.

## Current agent catalog

Snapshot from 500 GitHub candidates, updated 2026-08-25. The table contains the 176
repositories whose Python code imports LangGraph and whose README review identifies a
runnable agent or complete agent application. Counts are confirmed static lower bounds;
`?` means dynamic code may add more at runtime. The JSON and CSV files remain authoritative.

<!-- agent-catalog:start -->
| Project | Stars | Direction | Deps | Commercial APIs | Nodes | State fields | Subagents | Review |
|---|---:|---|---:|---|---:|---:|---:|---|
| [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) | 99,728 | multi-agent | 26 | anthropic<br>google_genai<br>groq<br>mistral<br>openai | 10+? | 1+? | 0+? | high |
| [bytedance/deer-flow](https://github.com/bytedance/deer-flow) | 80,803 | research | 73 | anthropic<br>exa<br>google_genai<br>openai<br>tavily | 29+? | 5+? | 0+? | high |
| [assafelovic/gpt-researcher](https://github.com/assafelovic/gpt-researcher) | 29,136 | research | 173 | anthropic<br>exa<br>fireworks<br>google_genai<br>groq<br>mistral<br>openai<br>tavily | 11 | 0+? | 0+? | high |
| [langchain-ai/deepagents](https://github.com/langchain-ai/deepagents) | 28,380 | research | 96 | anthropic<br>fireworks<br>google_genai<br>groq<br>mistral<br>openai<br>tavily | 8 | 2+? | 0+? | high |
| [langchain-ai/open-swe](https://github.com/langchain-ai/open-swe) | 10,611 | browser/automation | 29 | anthropic<br>exa<br>fireworks<br>google_genai<br>groq<br>openai | 2 | 12+? | 0+? | high |
| [xerrors/Yuxi](https://github.com/xerrors/Yuxi) | 6,546 | data/SQL | 79 | anthropic<br>google_genai<br>openai<br>tavily | 0 | 0+? | 0+? | high |
| [PurpleAILAB/Decepticon](https://github.com/PurpleAILAB/Decepticon) | 5,318 | browser/automation | 34 | anthropic<br>fireworks<br>google_genai<br>groq<br>mistral<br>openai | 9 | 0+? | 0+? | high |
| [EvoScientist/EvoScientist](https://github.com/EvoScientist/EvoScientist) | 4,498 | coding | 47 | anthropic<br>google_genai<br>openai<br>tavily | 4 | 2+? | 0+? | high |
| [JoshuaC215/agent-service-toolkit](https://github.com/JoshuaC215/agent-service-toolkit) | 4,435 | RAG/knowledge | 42 | anthropic<br>google_genai<br>groq<br>openai | 31 | 0+? | 2+? | high |
| [Awarexone/Agentic-Bug-Hunter](https://github.com/Awarexone/Agentic-Bug-Hunter) | 4,412 | browser/automation | 2 | anthropic<br>google_genai<br>groq<br>mistral<br>openai | 2 | 1+? | 0+? | high |
| [simonlin1212/TradingAgents-astock](https://github.com/simonlin1212/TradingAgents-astock) | 3,070 | multi-agent | 25 | anthropic<br>google_genai<br>openai | 11+? | 1+? | 0+? | high |
| [wassim249/fastapi-langgraph-agent-production-ready-template](https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template) | 2,611 | data/SQL | 43 | openai | 2 | 0+? | 0+? | high |
| [beenuar/AiSOC](https://github.com/beenuar/AiSOC) | 2,494 | data/SQL | 70 | anthropic<br>openai | 13+? | 0+? | 0+? | high |
| [1517005260/graph-rag-agent](https://github.com/1517005260/graph-rag-agent) | 2,323 | RAG/knowledge | 40 | openai | 4+? | 1+? | 0+? | high |
| [guy-hartstein/company-research-agent](https://github.com/guy-hartstein/company-research-agent) | 2,251 | multi-agent | 11 | google_genai<br>openai<br>tavily | 10 | 0+? | 0+? | high |
| [ai-christianson/RA.Aid](https://github.com/ai-christianson/RA.Aid) | 2,222 | coding | 43 | anthropic<br>fireworks<br>google_genai<br>groq<br>openai<br>tavily | 0 | 0+? | 0+? | high |
| [olaxbt/ai-market-maker](https://github.com/olaxbt/ai-market-maker) | 2,057 | data/SQL | 30 | openai | 9+? | 0+? | 0+? | high |
| [zi-yue-1129/DATAGEN](https://github.com/zi-yue-1129/DATAGEN) | 1,792 | browser/automation | 19 | anthropic<br>google_genai<br>groq<br>openai | 12 | 0+? | 0+? | high |
| [ginlix-ai/LangAlpha](https://github.com/ginlix-ai/LangAlpha) | 1,689 | data/SQL | 82 | anthropic<br>exa<br>google_genai<br>openai<br>tavily | 19 | 0+? | 0+? | high |
| [ShenSeanChen/waku-agent](https://github.com/ShenSeanChen/waku-agent) | 1,551 | multi-agent | 30 | anthropic<br>google_genai<br>openai<br>tavily | 1+? | 0+? | 0+? | high |
| [rotemweiss57/gpt-newspaper](https://github.com/rotemweiss57/gpt-newspaper) | 1,469 | research | 10 | openai<br>tavily | 5 | 0+? | 0+? | high |
| [darwin-lau/langmanus](https://github.com/darwin-lau/langmanus) | 1,316 | browser/automation | 20 | openai<br>tavily | 7 | 0+? | 0+? | high |
| [rcortx/kiwiq](https://github.com/rcortx/kiwiq) | 1,227 | data/SQL | 81 | anthropic<br>fireworks<br>google_genai<br>openai | 0+? | 0+? | 0+? | medium |
| [SalesforceAIResearch/enterprise-deep-research](https://github.com/SalesforceAIResearch/enterprise-deep-research) | 1,201 | research | 48 | anthropic<br>google_genai<br>groq<br>openai<br>tavily | 9 | 0+? | 0+? | high |
| [Azure-Samples/chat-with-your-data-solution-accelerator](https://github.com/Azure-Samples/chat-with-your-data-solution-accelerator) | 1,178 | RAG/knowledge | 36 | openai | 1 | 1+? | 0+? | high |
| [test-zeus-ai/testzeus-hercules](https://github.com/test-zeus-ai/testzeus-hercules) | 1,127 | browser/automation | 42 | anthropic<br>openai | 3 | 21+? | 0+? | high |
| [EuniAI/Prometheus](https://github.com/EuniAI/Prometheus) | 1,126 | coding | 36 | anthropic<br>google_genai<br>openai<br>tavily | 135 | 0+? | 0+? | high |
| [Fullive-AI/Anima](https://github.com/Fullive-AI/Anima) | 1,056 | unknown | 20 | openai | 4 | 13+? | 0+? | high |
| [hrithikkoduri/WebRover](https://github.com/hrithikkoduri/WebRover) | 1,022 | RAG/knowledge | 22 | anthropic<br>openai | 55 | 22+? | 0+? | high |
| [mikekelly/AgentK](https://github.com/mikekelly/AgentK) | 971 | browser/automation | 10 | anthropic<br>openai | 11 | 0+? | 0+? | high |
| [FareedKhan-dev/production-grade-agentic-system](https://github.com/FareedKhan-dev/production-grade-agentic-system) | 933 | data/SQL | 37 | openai | 2 | 0+? | 0+? | medium |
| [XD-MHLOO/Osintgraph](https://github.com/XD-MHLOO/Osintgraph) | 931 | unknown | 15 | google_genai | 5 | 4+? | 0+? | high |
| [zamalali/DeepGit](https://github.com/zamalali/DeepGit) | 903 | research | 15 | groq<br>openai | 29 | 6+? | 0+? | high |
| [Pan-Chera/Multi-Agent-CAD](https://github.com/Pan-Chera/Multi-Agent-CAD) | 890 | multi-agent | 19 | anthropic<br>openai | 7 | 0+? | 0+? | high |
| [lc2panda/alphastream](https://github.com/lc2panda/alphastream) | 882 | browser/automation | 69 | anthropic<br>google_genai<br>openai<br>tavily | 15 | 0+? | 0+? | high |
| [cuga-project/cuga-agent](https://github.com/cuga-project/cuga-agent) | 870 | coding | 59 | google_genai<br>groq<br>mistral<br>openai<br>tavily | 38+? | 0+? | 0+? | high |
| [NVIDIA-AI-Blueprints/aiq](https://github.com/NVIDIA-AI-Blueprints/aiq) | 845 | research | 83 | exa<br>openai<br>tavily | 14 | 2+? | 0+? | high |
| [icey1287/SuperMew](https://github.com/icey1287/SuperMew) | 832 | RAG/knowledge | 31 | openai | 8 | 27+? | 0+? | medium |
| [langchain-ai/react-agent](https://github.com/langchain-ai/react-agent) | 827 | research | 9 | anthropic<br>fireworks<br>openai<br>tavily | 2 | 0+? | 0+? | high |
| [nirbar1985/ai-travel-agent](https://github.com/nirbar1985/ai-travel-agent) | 797 | unknown | 8 | openai | 3 | 1+? | 0+? | high |
| [vinay-gatech/stocks-insights-ai-agent](https://github.com/vinay-gatech/stocks-insights-ai-agent) | 749 | RAG/knowledge | 0 | openai | 9 | 0+? | 0+? | high |
| [Chen-zexi/open-ptc-agent](https://github.com/Chen-zexi/open-ptc-agent) | 728 | multi-agent | 41 | anthropic<br>google_genai<br>openai<br>tavily | 1 | 0+? | 0+? | high |
| [isoftstone-data-intelligence-ai/efflux-backend](https://github.com/isoftstone-data-intelligence-ai/efflux-backend) | 722 | data/SQL | 18 | openai | 0 | 0+? | 0+? | high |
| [braincrew-lab/langgraph-mcp-agents](https://github.com/braincrew-lab/langgraph-mcp-agents) | 717 | RAG/knowledge | 13 | anthropic<br>openai | 0 | 0+? | 0+? | medium |
| [stophobia/deerflow2.0-enhanced](https://github.com/stophobia/deerflow2.0-enhanced) | 692 | research | 36 | anthropic<br>google_genai<br>openai<br>tavily | 0 | 0+? | 0+? | high |
| [Westlake-AGI-Lab/AppAgentX](https://github.com/Westlake-AGI-Lab/AppAgentX) | 669 | RAG/knowledge | 36 | openai<br>pinecone | 11 | 0+? | 0+? | high |
| [nuglifeleoji/Options-Analytics-Agent](https://github.com/nuglifeleoji/Options-Analytics-Agent) | 639 | RAG/knowledge | 17 | anthropic<br>openai<br>tavily | 18 | 17+? | 0+? | high |
| [langtalks/swe-agent](https://github.com/langtalks/swe-agent) | 638 | browser/automation | 10 | anthropic | 13 | 2+? | 0+? | high |
| [tablegpt/tablegpt-agent](https://github.com/tablegpt/tablegpt-agent) | 637 | data/SQL | 48 | openai | 9 | 0+? | 0+? | high |
| [zhongyu09/openchatbi](https://github.com/zhongyu09/openchatbi) | 633 | data/SQL | 64 | anthropic<br>openai | 23 | 0+? | 0+? | high |
| [51bitquant/ai-hedge-fund-crypto](https://github.com/51bitquant/ai-hedge-fund-crypto) | 616 | unknown | 23 | anthropic<br>google_genai<br>groq<br>openai | 4+? | 0+? | 0+? | high |
| [wassim249/YT-Navigator](https://github.com/wassim249/YT-Navigator) | 602 | data/SQL | 27 | groq | 6 | 0+? | 0+? | high |
| [esxr/langgraph-mcp](https://github.com/esxr/langgraph-mcp) | 584 | multi-agent | 12 | openai | 14 | 0+? | 0+? | high |
| [NicholasGoh/fastapi-mcp-langgraph-template](https://github.com/NicholasGoh/fastapi-mcp-langgraph-template) | 555 | data/SQL | 18 | openai | 2 | 0+? | 0+? | medium |
| [psyray/oasis](https://github.com/psyray/oasis) | 550 | RAG/knowledge | 16 | — | 15 | 0+? | 0+? | medium |
| [bcefghj/multi-agent-ecommerce-system](https://github.com/bcefghj/multi-agent-ecommerce-system) | 525 | multi-agent | 17 | openai | 6 | 15+? | 0+? | high |
| [vibesurf-ai/VibeSurf](https://github.com/vibesurf-ai/VibeSurf) | 482 | browser/automation | 159 | anthropic<br>google_genai<br>groq<br>mistral<br>openai<br>pinecone | 3+? | 0+? | 0+? | high |
| [NanGePlus/LangGraphChatBot](https://github.com/NanGePlus/LangGraphChatBot) | 470 | data/SQL | 0 | openai | 10 | 3+? | 0+? | medium |
| [SponsioLabs/Sponsio](https://github.com/SponsioLabs/Sponsio) | 436 | browser/automation | 23 | anthropic<br>google_genai<br>openai | 0 | 0+? | 0+? | medium |
| [Tswoen/Paper-Agent](https://github.com/Tswoen/Paper-Agent) | 412 | RAG/knowledge | 8 | anthropic<br>openai | 9 | 23+? | 0+? | high |
| [brainqub3/jar3d_meta_expert](https://github.com/brainqub3/jar3d_meta_expert) | 408 | RAG/knowledge | 21 | anthropic<br>google_genai<br>groq<br>mistral<br>openai | 15+? | 7+? | 0+? | high |
| [john-adeojo/graph_websearch_agent](https://github.com/john-adeojo/graph_websearch_agent) | 403 | unknown | 7 | google_genai<br>groq<br>openai | 9 | 0+? | 0+? | high |
| [Arvo-AI/aurora](https://github.com/Arvo-AI/aurora) | 399 | RAG/knowledge | 93 | anthropic<br>google_genai<br>openai | 6 | 0+? | 0+? | medium |
| [skygazer42/GustoBot](https://github.com/skygazer42/GustoBot) | 390 | browser/automation | 54 | anthropic<br>openai | 38 | 13+? | 0+? | high |
| [Xeron2000/openOii](https://github.com/Xeron2000/openOii) | 377 | data/SQL | 24 | anthropic | 17 | 0+? | 0+? | high |
| [togethercomputer/open_deep_research](https://github.com/togethercomputer/open_deep_research) | 377 | research | 22 | tavily | 0 | 0+? | 0+? | high |
| [amanv1906/GENAI-CareerAssistant-Multiagent](https://github.com/amanv1906/GENAI-CareerAssistant-Multiagent) | 375 | multi-agent | 17 | groq<br>openai | 6 | 5+? | 0+? | high |
| [kaymen99/sales-outreach-automation-langgraph](https://github.com/kaymen99/sales-outreach-automation-langgraph) | 372 | RAG/knowledge | 16 | anthropic<br>google_genai<br>openai | 18 | 0+? | 0+? | high |
| [bcefghj/smart-cs-multi-agent](https://github.com/bcefghj/smart-cs-multi-agent) | 369 | multi-agent | 19 | openai | 5 | 9+? | 0+? | high |
| [NVlabs/SpatialClaw](https://github.com/NVlabs/SpatialClaw) | 368 | unknown | 39 | openai | 7 | 0+? | 0+? | high |
| [cnunescoelho/kiroku](https://github.com/cnunescoelho/kiroku) | 353 | multi-agent | 16 | openai<br>tavily | 0+? | 0+? | 0+? | high |
| [NVIDIA-AI-IOT/remembr](https://github.com/NVIDIA-AI-IOT/remembr) | 352 | unknown | 11 | openai | 3 | 1+? | 0+? | medium |
| [CronusL-1141/AI-company](https://github.com/CronusL-1141/AI-company) | 346 | browser/automation | 21 | anthropic | 5+? | 7+? | 0+? | high |
| [EthanXiang777/circuit-framework](https://github.com/EthanXiang777/circuit-framework) | 344 | multi-agent | 27 | anthropic<br>google_genai<br>groq<br>mistral<br>openai | 12+? | 1+? | 0+? | medium |
| [GoogleCloudPlatform/cymbal-air-toolbox-demo](https://github.com/GoogleCloudPlatform/cymbal-air-toolbox-demo) | 341 | RAG/knowledge | 25 | — | 5 | 1+? | 0+? | medium |
| [ivebotunac/PrimoAgent](https://github.com/ivebotunac/PrimoAgent) | 339 | multi-agent | 18 | anthropic<br>openai | 4 | 0+? | 0+? | high |
| [Negai-ai/AgentClaw](https://github.com/Negai-ai/AgentClaw) | 339 | browser/automation | 32 | anthropic<br>openai | 8+? | 0+? | 0+? | high |
| [lhh737/LangChain-ReAct-Agent](https://github.com/lhh737/LangChain-ReAct-Agent) | 331 | RAG/knowledge | 11 | — | 0 | 0+? | 0+? | high |
| [didilili/shopkeeper-agent](https://github.com/didilili/shopkeeper-agent) | 317 | data/SQL | 17 | — | 12 | 0+? | 0+? | high |
| [kmeanskaran/stock-agent-ops](https://github.com/kmeanskaran/stock-agent-ops) | 304 | multi-agent | 27 | google_genai | 4 | 0+? | 0+? | high |
| [jd-opensource/JoySafeter](https://github.com/jd-opensource/JoySafeter) | 303 | data/SQL | 59 | anthropic<br>google_genai<br>openai<br>tavily | 0+? | 0+? | 0+? | medium |
| [liangdabiao/langgraph_multi-agent-rag-customer-support](https://github.com/liangdabiao/langgraph_multi-agent-rag-customer-support) | 300 | multi-agent | 23 | openai | 29 | 0+? | 0+? | high |
| [hwchase17/langchain-streamlit-template](https://github.com/hwchase17/langchain-streamlit-template) | 298 | unknown | 5 | openai | 0 | 0+? | 0+? | medium |
| [yolo-hyl/medical-rag](https://github.com/yolo-hyl/medical-rag) | 297 | RAG/knowledge | 0 | openai | 12 | 22+? | 0+? | high |
| [dhruvsinghal09/Adaptive-Rag](https://github.com/dhruvsinghal09/Adaptive-Rag) | 296 | RAG/knowledge | 22 | groq<br>openai<br>tavily | 7 | 0+? | 0+? | high |
| [HKUSTDial/DeepFund](https://github.com/HKUSTDial/DeepFund) | 293 | multi-agent | 15 | anthropic<br>fireworks<br>openai | 1+? | 0+? | 0+? | high |
| [langchain-ai/new-langgraph-project](https://github.com/langchain-ai/new-langgraph-project) | 288 | unknown | 4 | — | 1 | 0+? | 0+? | high |
| [goruck/home-generative-agent](https://github.com/goruck/home-generative-agent) | 287 | data/SQL | 15 | anthropic<br>google_genai<br>openai | 5 | 0+? | 0+? | high |
| [jarrycyx/openlens-ai](https://github.com/jarrycyx/openlens-ai) | 278 | research | 30 | openai<br>tavily | 38 | 0+? | 0+? | high |
| [NVIDIA-AI-Blueprints/ai-virtual-assistant](https://github.com/NVIDIA-AI-Blueprints/ai-virtual-assistant) | 274 | data/SQL | 29 | — | 14 | 7+? | 0+? | high |
| [quarqlabs/argus](https://github.com/quarqlabs/argus) | 273 | RAG/knowledge | 120 | google_genai<br>openai | 15 | 16+? | 0+? | high |
| [kaymen99/langgraph-email-automation](https://github.com/kaymen99/langgraph-email-automation) | 272 | RAG/knowledge | 18 | google_genai<br>groq | 9 | 0+? | 0+? | high |
| [SecurityClaw/SecurityClaw](https://github.com/SecurityClaw/SecurityClaw) | 266 | multi-agent | 16 | anthropic<br>openai | 10 | 30+? | 0+? | high |
| [Lyra-stellAI/BYO-LLM-WIKI](https://github.com/Lyra-stellAI/BYO-LLM-WIKI) | 261 | data/SQL | 15 | anthropic<br>google_genai<br>mistral<br>openai | 9 | 29+? | 0+? | high |
| [artnoage/Podcast](https://github.com/artnoage/Podcast) | 260 | data/SQL | 77 | openai | 3 | 4+? | 0+? | high |
| [lingxi-agent/Lingxi](https://github.com/lingxi-agent/Lingxi) | 258 | multi-agent | 34 | anthropic<br>openai | 9 | 0+? | 0+? | high |
| [mfmezger/conversational-agent-langchain](https://github.com/mfmezger/conversational-agent-langchain) | 255 | RAG/knowledge | 29 | google_genai<br>openai | 6 | 0+? | 0+? | high |
| [tyxben/AI_novel](https://github.com/tyxben/AI_novel) | 255 | browser/automation | 32 | google_genai<br>openai | 14+? | 0+? | 0+? | high |
| [bernatsampera/event-deep-research](https://github.com/bernatsampera/event-deep-research) | 254 | research | 13 | anthropic<br>google_genai<br>openai<br>tavily | 15 | 3+? | 0+? | high |
| [Y-Research-SBU/PosterGen](https://github.com/Y-Research-SBU/PosterGen) | 253 | multi-agent | 53 | anthropic<br>google_genai<br>openai | 7 | 0+? | 0+? | medium |
| [datawhalechina/vibe-blog](https://github.com/datawhalechina/vibe-blog) | 252 | research | 28 | anthropic<br>google_genai<br>openai<br>tavily | 2 | 0+? | 0+? | high |
| [huygiatrng/AlpacaTradingAgent](https://github.com/huygiatrng/AlpacaTradingAgent) | 252 | multi-agent | 38 | anthropic<br>google_genai<br>openai | 12+? | 1+? | 0+? | high |
| [KodyKendall/LlamaBot](https://github.com/KodyKendall/LlamaBot) | 241 | data/SQL | 143 | anthropic<br>google_genai<br>openai<br>tavily | 17 | 0+? | 0+? | medium |
| [lgesuellip/langgraph-whatsapp-agent](https://github.com/lgesuellip/langgraph-whatsapp-agent) | 240 | multi-agent | 11 | google_genai<br>openai | 0 | 0+? | 1+? | high |
| [billy-enrizky/openbrowser-ai](https://github.com/billy-enrizky/openbrowser-ai) | 240 | browser/automation | 44 | anthropic<br>google_genai<br>groq<br>openai | 1 | 4+? | 0+? | high |
| [NVIDIA-AI-Blueprints/vulnerability-analysis](https://github.com/NVIDIA-AI-Blueprints/vulnerability-analysis) | 240 | data/SQL | 40 | openai<br>tavily | 5 | 0+? | 0+? | high |
| [wshobson/financial-chat](https://github.com/wshobson/financial-chat) | 237 | finance | 31 | anthropic<br>tavily | 17 | 2+? | 0+? | high |
| [nicoladisabato/MultiAgenticRAG](https://github.com/nicoladisabato/MultiAgenticRAG) | 235 | RAG/knowledge | 8 | openai | 9 | 0+? | 0+? | high |
| [eosho/langchain_data_agent](https://github.com/eosho/langchain_data_agent) | 234 | data/SQL | 48 | openai | 9+? | 0+? | 0+? | high |
| [growgraph/ontocast](https://github.com/growgraph/ontocast) | 230 | RAG/knowledge | 54 | anthropic<br>google_genai<br>openai | 3+? | 4+? | 0+? | medium |
| [louisgthier/decompai](https://github.com/louisgthier/decompai) | 219 | unknown | 9 | google_genai<br>openai | 3 | 0+? | 0+? | high |
| [Nachoeigu/agentic-customer-service-medical-clinic](https://github.com/Nachoeigu/agentic-customer-service-medical-clinic) | 218 | RAG/knowledge | 13 | anthropic<br>google_genai<br>groq<br>openai<br>pinecone | 3 | 1+? | 0+? | high |
| [jamwithai/observable-job-agent](https://github.com/jamwithai/observable-job-agent) | 218 | unknown | 17 | groq<br>openai<br>tavily | 5 | 0+? | 0+? | high |
| [Gen-Future/ExcelMind](https://github.com/Gen-Future/ExcelMind) | 218 | RAG/knowledge | 12 | openai | 2 | 1+? | 0+? | high |
| [kulkarnirohit123/cra-agent](https://github.com/kulkarnirohit123/cra-agent) | 217 | unknown | 26 | anthropic<br>openai | 5 | 0+? | 0+? | high |
| [Yanyutin753/LambChat](https://github.com/Yanyutin753/LambChat) | 217 | data/SQL | 49 | anthropic<br>google_genai<br>openai | 5+? | 3+? | 0+? | high |
| [Yonom/assistant-ui-langgraph-fastapi](https://github.com/Yonom/assistant-ui-langgraph-fastapi) | 210 | unknown | 7 | openai | 2 | 0+? | 0+? | medium |
| [HezaoHezao/poirot](https://github.com/HezaoHezao/poirot) | 209 | research | 17 | anthropic<br>google_genai<br>openai | 0 | 0+? | 0+? | high |
| [fzn0x/watchtower](https://github.com/fzn0x/watchtower) | 207 | data/SQL | 17 | anthropic<br>google_genai<br>openai | 4 | 0+? | 0+? | high |
| [yycyyv/M-Cube](https://github.com/yycyyv/M-Cube) | 206 | RAG/knowledge | 18 | anthropic<br>google_genai<br>openai | 27 | 0+? | 0+? | medium |
| [jank/curiosity](https://github.com/jank/curiosity) | 206 | data/SQL | 83 | groq<br>openai | 0 | 0+? | 0+? | medium |
| [muratcankoylan/readwren](https://github.com/muratcankoylan/readwren) | 204 | multi-agent | 8 | openai | 3 | 5+? | 0+? | high |
| [tavily-ai/meeting-prep-agent](https://github.com/tavily-ai/meeting-prep-agent) | 201 | research | 42 | groq<br>openai<br>tavily | 5 | 6+? | 0+? | high |
| [ZhangJinHaHaHa/FinchainAgent](https://github.com/ZhangJinHaHaHa/FinchainAgent) | 201 | multi-agent | 5 | openai<br>tavily | 6 | 12+? | 0+? | high |
| [guangshu100/BidMaster-Pro](https://github.com/guangshu100/BidMaster-Pro) | 201 | RAG/knowledge | 39 | google_genai<br>openai | 0+? | 0+? | 0+? | high |
| [tevslin/meeting-reporter](https://github.com/tevslin/meeting-reporter) | 199 | browser/automation | 12 | openai | 6 | 0+? | 0+? | high |
| [ai-forever/giga_agent](https://github.com/ai-forever/giga_agent) | 197 | data/SQL | 99 | google_genai<br>openai<br>tavily | 50 | 24+? | 0+? | medium |
| [duartecaldascardoso/article-explainer](https://github.com/duartecaldascardoso/article-explainer) | 191 | multi-agent | 11 | openai | 0 | 0+? | 5+? | high |
| [chatchat-space/LangGraph-Chatchat](https://github.com/chatchat-space/LangGraph-Chatchat) | 190 | RAG/knowledge | 62 | openai | 35 | 11+? | 0+? | medium |
| [didilili/deepsearch-agents](https://github.com/didilili/deepsearch-agents) | 187 | research | 25 | openai<br>tavily | 4 | 4+? | 0+? | high |
| [OS3Lab/agent4kdump](https://github.com/OS3Lab/agent4kdump) | 186 | RAG/knowledge | 28 | openai<br>tavily | 0 | 0+? | 0+? | high |
| [akamai/patchdiff-ai](https://github.com/akamai/patchdiff-ai) | 184 | multi-agent | 30 | anthropic<br>google_genai<br>openai | 20+? | 0+? | 0+? | high |
| [tarun7r/deep-research-agent](https://github.com/tarun7r/deep-research-agent) | 183 | research | 23 | google_genai<br>openai<br>tavily | 4 | 0+? | 0+? | high |
| [skygazer42/Weaver](https://github.com/skygazer42/Weaver) | 178 | browser/automation | 55 | anthropic<br>exa<br>openai<br>tavily | 27 | 10+? | 0+? | medium |
| [kaymen99/personal-ai-assistant](https://github.com/kaymen99/personal-ai-assistant) | 178 | browser/automation | 24 | anthropic<br>google_genai<br>groq<br>openai<br>tavily | 0 | 0+? | 0+? | high |
| [Yourdaylight/stock_datasource](https://github.com/Yourdaylight/stock_datasource) | 176 | multi-agent | 42 | openai | 0 | 0+? | 0+? | high |
| [YUHAO-corn/manufacturing-agents](https://github.com/YUHAO-corn/manufacturing-agents) | 170 | RAG/knowledge | 38 | anthropic<br>google_genai<br>openai | 14+? | 0+? | 0+? | high |
| [GU-Cryptography/anykb](https://github.com/GU-Cryptography/anykb) | 170 | RAG/knowledge | 32 | anthropic<br>openai | 2 | 0+? | 0+? | high |
| [EYamanS/texel-studio](https://github.com/EYamanS/texel-studio) | 168 | unknown | 16 | google_genai<br>openai | 0 | 0+? | 0+? | medium |
| [Y-Research-SBU/TimeSeriesScientist](https://github.com/Y-Research-SBU/TimeSeriesScientist) | 167 | multi-agent | 30 | anthropic<br>google_genai<br>openai | 5 | 0+? | 0+? | high |
| [FeiCoder/BreadFree-Simu](https://github.com/FeiCoder/BreadFree-Simu) | 162 | data/SQL | 17 | openai | 12 | 18+? | 0+? | medium |
| [CopilotKit/scene-creator-copilot](https://github.com/CopilotKit/scene-creator-copilot) | 159 | unknown | 10 | google_genai | 3 | 0+? | 0+? | high |
| [FareedKhan-dev/scalable-rag-pipeline](https://github.com/FareedKhan-dev/scalable-rag-pipeline) | 159 | RAG/knowledge | 29 | anthropic<br>openai<br>tavily | 3 | 0+? | 0+? | high |
| [kaymen99/Upwork-AI-jobs-applier](https://github.com/kaymen99/Upwork-AI-jobs-applier) | 158 | browser/automation | 10 | anthropic<br>google_genai<br>groq<br>openai | 10 | 0+? | 0+? | high |
| [kargarisaac/telegram_link_summarizer_agent](https://github.com/kargarisaac/telegram_link_summarizer_agent) | 155 | browser/automation | 36 | openai<br>tavily | 8 | 8+? | 0+? | high |
| [xiongQvQ/AI_Find_Customer](https://github.com/xiongQvQ/AI_Find_Customer) | 155 | browser/automation | 23 | anthropic<br>groq<br>openai<br>tavily | 7 | 0+? | 0+? | high |
| [itshyao/proxyless-llm-websearch](https://github.com/itshyao/proxyless-llm-websearch) | 154 | browser/automation | 18 | openai | 2 | 0+? | 0+? | high |
| [langchain-ai/langgraph-fullstack-python](https://github.com/langchain-ai/langgraph-fullstack-python) | 153 | research | 12 | anthropic<br>fireworks<br>openai<br>tavily | 0 | 0+? | 0+? | high |
| [123-qw-as/Beacon](https://github.com/123-qw-as/Beacon) | 150 | multi-agent | 24 | openai | 45 | 0+? | 0+? | medium |
| [iblameandrew/open-deepthink](https://github.com/iblameandrew/open-deepthink) | 150 | RAG/knowledge | 26 | openai | 7+? | 0+? | 0+? | high |
| [BjornMelin/docmind-ai-llm](https://github.com/BjornMelin/docmind-ai-llm) | 150 | multi-agent | 44 | anthropic<br>openai | 12+? | 9+? | 0+? | high |
| [argonne-lcf/ChemGraph](https://github.com/argonne-lcf/ChemGraph) | 148 | multi-agent | 52 | anthropic<br>google_genai<br>groq<br>openai | 46 | 1+? | 0+? | high |
| [Ganador1/FenixAI_tradingBot](https://github.com/Ganador1/FenixAI_tradingBot) | 147 | browser/automation | 102 | anthropic<br>groq<br>openai | 6 | 30+? | 0+? | high |
| [hwchase17/autoresearch-agents](https://github.com/hwchase17/autoresearch-agents) | 146 | coding | 0 | openai | 0 | 0+? | 0+? | high |
| [leonzzz435/garmin-ai-coach](https://github.com/leonzzz435/garmin-ai-coach) | 146 | multi-agent | 14 | anthropic<br>openai | 39 | 0+? | 0+? | high |
| [EricHong123/B-agent](https://github.com/EricHong123/B-agent) | 146 | RAG/knowledge | 42 | openai | 0 | 0+? | 0+? | high |
| [neopen/story-shot-agent](https://github.com/neopen/story-shot-agent) | 145 | RAG/knowledge | 42 | openai | 40+? | 10+? | 0+? | high |
| [kevin333353/jobsmith](https://github.com/kevin333353/jobsmith) | 145 | multi-agent | 19 | anthropic<br>openai<br>tavily | 10 | 0+? | 0+? | medium |
| [bamboo-moon/zhisaotong-Agent](https://github.com/bamboo-moon/zhisaotong-Agent) | 144 | RAG/knowledge | 12 | — | 0 | 0+? | 0+? | medium |
| [waseens/deep-search-pro](https://github.com/waseens/deep-search-pro) | 144 | data/SQL | 135 | anthropic<br>google_genai<br>openai<br>tavily | 0 | 0+? | 0+? | high |
| [Neon549/Alpha_stock](https://github.com/Neon549/Alpha_stock) | 144 | RAG/knowledge | 34 | openai | 15 | 4+? | 0+? | medium |
| [colossus-lab/openarg_backend](https://github.com/colossus-lab/openarg_backend) | 143 | data/SQL | 50 | anthropic<br>google_genai | 24 | 18+? | 0+? | medium |
| [NVIDIA-AI-Blueprints/biomedical-aiq-research-agent](https://github.com/NVIDIA-AI-Blueprints/biomedical-aiq-research-agent) | 143 | research | 62 | openai | 8 | 0+? | 0+? | high |
| [kaymen99/local-rag-researcher-deepseek](https://github.com/kaymen99/local-rag-researcher-deepseek) | 142 | RAG/knowledge | 16 | openai<br>tavily | 8 | 0+? | 0+? | high |
| [ro-anderson/multi-agent-rag-customer-support](https://github.com/ro-anderson/multi-agent-rag-customer-support) | 140 | multi-agent | 12 | openai | 19 | 0+? | 0+? | high |
| [twanew/OmniWriter](https://github.com/twanew/OmniWriter) | 138 | RAG/knowledge | 19 | openai<br>tavily | 20 | 9+? | 0+? | high |
| [IatomicreactorI/CSGOTrading](https://github.com/IatomicreactorI/CSGOTrading) | 137 | multi-agent | 14 | openai | 1+? | 0+? | 0+? | high |
| [jaguarliuu/xunlong](https://github.com/jaguarliuu/xunlong) | 137 | browser/automation | 38 | anthropic<br>openai | 10 | 30+? | 0+? | medium |
| [Eldergenix/Plato-Scientific-Research-Autonomous-Agent](https://github.com/Eldergenix/Plato-Scientific-Research-Autonomous-Agent) | 134 | data/SQL | 60 | anthropic<br>google_genai<br>mistral<br>openai | 41 | 4+? | 0+? | high |
| [bcefghj/medical-multi-agent-system](https://github.com/bcefghj/medical-multi-agent-system) | 133 | coding | 21 | openai | 5 | 0+? | 0+? | high |
| [seanlxh/Air-Lingjing](https://github.com/seanlxh/Air-Lingjing) | 131 | data/SQL | 14 | — | 30 | 0+? | 0+? | high |
| [agruai/company-research-agent](https://github.com/agruai/company-research-agent) | 131 | multi-agent | 13 | google_genai<br>openai<br>tavily | 10 | 0+? | 0+? | high |
| [shodan1q/zeroapp](https://github.com/shodan1q/zeroapp) | 130 | data/SQL | 26 | anthropic<br>google_genai<br>openai | 9 | 0+? | 0+? | medium |
| [bcefghj/agent-knowledge-hub](https://github.com/bcefghj/agent-knowledge-hub) | 129 | RAG/knowledge | 28 | openai | 7 | 0+? | 0+? | high |
| [KRATSZ/LabScript-AI](https://github.com/KRATSZ/LabScript-AI) | 129 | RAG/knowledge | 13 | openai | 4 | 18+? | 0+? | high |
| [ljxpython/ai-agent-platform](https://github.com/ljxpython/ai-agent-platform) | 126 | RAG/knowledge | 87 | anthropic<br>google_genai<br>openai | 1 | 0+? | 0+? | medium |
<!-- agent-catalog:end -->

## Run

GitHub CLI authentication or `GITHUB_TOKEN` is recommended.

```bash
python3 agentradar.py scan --limit 20
```

Outputs:

```text
data/catalog.json
data/catalog.csv
data/provider_candidates.json
data/scan_cache.json
data/repositories_seen.json
```

Static counts are confirmed lower bounds, not claims about runtime totals. The scan cache
reuses analysis when a repository's `pushed_at` value is unchanged; stars still refresh.
`repositories_seen.json` keeps every discovered candidate, including filtered and failed scans.
Cache and seen-repository state are checkpointed after every candidate, so an interrupted
large scan can resume without losing completed repository analysis.

Prepare ten new or changed projects for a lightweight Codex host review:

```bash
python3 agentradar.py prepare-review --limit 10
```

This writes `data/review_queue.json`. Host-agent judgments live separately in
`data/agent_reviews.json` and never replace LangGraph or GitHub Star facts.

Use a custom repository search when needed:

```bash
python3 agentradar.py scan \
  --query 'langgraph agent in:readme language:Python archived:false fork:false' \
  --limit 50
```

## Test

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q agentradar.py tests
```

The scanner downloads repository tarballs but never extracts them to disk, imports target code, installs target dependencies, or runs target commands.
