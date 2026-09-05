<a name="top"></a>

<div align="center">

<h1>FPGA-Agent</h1>

<p><strong>从 HLS、RTL 到时序收敛，让智能体参与 FPGA 开发全流程。</strong></p>
<p>AMD Vivado / Vitis 工程技能 &nbsp;·&nbsp; 多智能体设计空间探索</p>

<p>
  <a href="#skills"><img src="https://img.shields.io/badge/FPGA_skills-9-0F766E?style=flat-square" alt="9 个 FPGA 技能"></a>
  <a href="#dse"><img src="https://img.shields.io/badge/Agentic--DSE-3_worker_roles-4F46E5?style=flat-square" alt="Agentic-DSE：3 类 Worker 角色"></a>
  <a href="#workflow"><img src="https://img.shields.io/badge/AMD-Vivado_%2F_Vitis-334155?style=flat-square" alt="AMD Vivado 和 Vitis"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-GPL--2.0-A16207?style=flat-square" alt="GPL-2.0 许可证"></a>
</p>

<p><a href="README.md">English</a> &nbsp;|&nbsp; <strong>简体中文</strong></p>

<p>
  <a href="#start">快速开始</a> &nbsp;·&nbsp;
  <a href="#skills">技能库</a> &nbsp;·&nbsp;
  <a href="#workflow">工程流程</a> &nbsp;·&nbsp;
  <a href="#dse">Agentic-DSE</a> &nbsp;·&nbsp;
  <a href="#resources">资源与配置</a>
</p>

</div>

---

## 两种使用方式

| 专项 FPGA 工程任务 | 多智能体设计空间探索 |
| --- | --- |
| 九个可复用技能，覆盖 HLS、综合、约束、实现、分析、时序收敛、仿真、TCL 和硬件调试。 | 由 Main Agent 协调 Explorer、Exploiter、Innovator，探索架构、pragma、参数和时钟选择。 |
| **从这里开始：** 一个设计、报告、脚本或工程问题。 | **从这里开始：** 一个 benchmark、数值契约、优化目标和有明确上限的搜索预算。 |
| [查看技能库 →](#skills) | [了解 Agentic-DSE →](#dse) |

<a name="start"></a>

## 快速开始

1. **选择入口。** 从下方技能库中选择需要的技能，或使用 [DSE-agent](DSE-agent/SKILL.md) 进行设计空间探索。
2. **让智能体可以读取技能目录。** 通过所用平台的技能机制加载，或直接提供 `SKILL.md` 及其配套资源。保持目录完整；除非任务明确要求替换，否则保留现有安装。
3. **说明目标与边界。** 明确需要分析、生成脚本、执行流程还是优化设计。相关技能可以在同一项已授权任务中配合使用。

| 你的目标 | 示例请求 |
| --- | --- |
| 理解报告 | “审阅这份时序报告，解释可能的瓶颈，不要修改设计。” |
| 准备自动化 | “为当前项目生成批处理 TCL 脚本，但不要执行。” |
| 执行实现流程 | “运行现有实现流程并检查所需输出，保留约束，不要烧录硬件。” |
| 改善时序 | “在当前 RTL 和时钟目标范围内改善时序，保留最佳候选，并说明尚未满足的验收条件。” |

技能以 AMD Vivado/Vitis **2025.2 文档**为主要参考基线。实际使用以已安装工具链支持的命令和器件为准。

<a name="skills"></a>

## 技能库

| 技能 | 覆盖内容 | AMD 文档 |
| --- | --- | --- |
| [vitis-hls-synthesis](vitis-hls-synthesis/SKILL.md) | C/C++ 转 RTL、pragma、接口、DATAFLOW、流水线、突发传输优化及分阶段检查 | UG1399 |
| [vivado-synth](vivado-synth/SKILL.md) | 综合策略、资源推断、属性、FSM 编码、层次结构及 OOC／增量综合 | UG901 |
| [vivado-constraints](vivado-constraints/SKILL.md) | 时钟、I/O 延迟、时序例外、CDC、物理约束及 XDC 调试 | UG903 |
| [vivado-impl](vivado-impl/SKILL.md) | 布局、布线、物理优化、拥塞、增量实现及 ECO 策略 | UG904 |
| [vivado-analysis](vivado-analysis/SKILL.md) | 时序路径、QoR、方法学、资源利用率、问题诊断及验收证据 | UG906 |
| [vivado-timing-closure](vivado-timing-closure/SKILL.md) | 约束基线、迭代优化、最佳候选保留及最终时序验收 | UG949 · UG1292 · XTP301 |
| [vivado-sim](vivado-sim/SKILL.md) | 行为级／网表级／时序仿真、xsim、第三方仿真器及 SAIF/VCD | UG900 |
| [vivado-tcl](vivado-tcl/SKILL.md) | 脚本生成与审阅、已授权的批量执行、结果检查及所需输出生成 | UG835 · UG892 |
| [vivado-debug](vivado-debug/SKILL.md) | ILA、VIO、JTAG-to-AXI、调试核插入、时钟要求及硬件故障排查 | UG908 |

<a name="workflow"></a>

## 工程流程

```text
HLS C/C++  →  RTL  →  综合  →  实现  →  时序检查
```

| 流程中的任务 | 使用的技能 |
| --- | --- |
| 约束与报告分析 | `vivado-constraints` + `vivado-analysis` |
| 迭代改善时序 | `vivado-timing-closure` + `vivado-impl` |
| 开发过程中的仿真 | `vivado-sim` |
| 跨阶段 TCL 自动化 | `vivado-tcl` |
| 用户请求且已授权的硬件调试 | `vivado-debug` |

<details>
<summary><strong>技能之间如何配合</strong></summary>

根据下一项实际需要完成的工作选择配套技能；这些关联并不要求每项任务都执行完整流程。

| 当前入口 | 配套技能 |
| --- | --- |
| `vitis-hls-synthesis` | 实现：`vivado-impl`；时序：`vivado-analysis`；约束：`vivado-constraints`；RTL 仿真：`vivado-sim`；调试：`vivado-debug`；自动化：`vivado-tcl` |
| `vivado-synth` | 执行：`vivado-tcl` |
| `vivado-constraints` | 执行：`vivado-tcl`；报告解读：`vivado-analysis` |
| `vivado-impl` | 脚本：`vivado-tcl`；综合：`vivado-synth`；约束：`vivado-constraints`；分析：`vivado-analysis`；HLS 修改：`vitis-hls-synthesis` |
| `vivado-analysis` | 命令：`vivado-tcl`；约束修改：`vivado-constraints`；实现策略：`vivado-impl` |
| `vivado-timing-closure` | 证据：`vivado-analysis`；约束：`vivado-constraints`；策略：`vivado-impl`；自动化：`vivado-tcl` |
| `vivado-debug` | 脚本：`vivado-tcl`；实现：`vivado-impl`；时序：`vivado-analysis`；HLS 调试选项：`vitis-hls-synthesis` |
| `vivado-sim` | 自动化：`vivado-tcl`；HLS 联合仿真：`vitis-hls-synthesis` |
| `vivado-tcl` | 调试决策：`vivado-debug`；分析：`vivado-analysis`；HLS IP 集成：`vitis-hls-synthesis` |

</details>

<a name="dse"></a>

## Agentic-DSE

**探索设计空间，保留完整证据，积累最佳候选。**

[Agentic-DSE](DSE-agent/SKILL.md) 将任务编排与候选实现分离。Main 负责需求、架构提案、任务分配、证据检查、归档、Pareto 筛选和经验知识维护。

| Worker | 搜索方式 | 冷启动方式 |
| --- | --- | --- |
| **Explorer** | 较大范围的架构与参数探索 | 基于 benchmark 实现新的种子方案 |
| **Exploiter** | 对基线或已通过验收的父本进行局部优化 | 建立或改进基线 |
| **Innovator** | 对兼容父本进行特征级交叉组合 | 显式使用种子方案或单父本变体 |

每轮使用全新的 Worker 身份和独立工作区。并发容量不足时，分批完成全部三类角色的任务。

### 核心能力

- **灵活的任务路由：** 需求审阅、架构建议、Pareto 查看和收敛诊断均可只读完成。
- **有上限的搜索：** 支持固定轮数或运行至收敛，同时设置有限轮次上限，并为每项 Worker 任务使用统一的总尝试预算。
- **两种验收模式：** 支持正式的 Csim／Csynth／Cosim／implementation 流程，也支持用户明确要求的仅联合仿真探索，后者单独保留为暂定结果。
- **可追溯的候选：** 通过输入指纹和阶段执行凭据，关联源码、头文件、测试数据、配置、工具身份和报告。
- **保留实验结果：** 使用不可覆盖的候选归档和父本引用，避免工作区复用破坏已有证据。
- **可比较的指标：** 使用固定参考点的精确 N 维超体积（HV），记录目标单位、配置标识，并区分延迟与吞吐指标。
- **项目知识保持私有：** 学习到的知识与实验依据保留在所选项目中，不随公开技能包发布。

### 开始一次搜索

保持 `DSE-agent` 目录完整。技能调用名称为 **`$run-agentic-dse`**。直接加载提示词的平台可从 [SKILL.md](DSE-agent/SKILL.md) 或兼容入口 [agent.md](DSE-agent/agent.md) 开始。

1. **选择 benchmark。** 提供源码、testbench／测试向量、目标配置，以及优化目标或规格说明。支持 `benchmarks/<name>/` 和旧版 `designs/<name>/` 两种目录布局。
2. **初始化项目。** 请求智能体准备所选 benchmark 和需求。Main 会补充缺失的状态文件和独立 Worker 输入，同时保留已有工作。
3. **确定搜索范围。** 例如：

   - “为这个 benchmark 运行三轮 DSE，保持数值契约不变。”
   - “运行两轮仅联合仿真的 DSE，不要运行 implementation。”
   - “继续运行至收敛，最多六轮。”
   - “展示 Pareto 前沿并解释当前瓶颈，不要修改文件。”

这些是自然语言请求，不是 shell 命令。运行时文件属于所选项目，项目目录可以与技能资源目录分开。

<details>
<summary><strong>DSE 配套文件说明</strong></summary>

| 路径 | 用途 |
| --- | --- |
| [DSE-agent/SKILL.md](DSE-agent/SKILL.md) | 主流程、任务路由与停止规则 |
| [DSE-agent/AGENTS.md](DSE-agent/AGENTS.md) | 文件所有权、委派与执行边界 |
| [DSE-agent/agent.md](DSE-agent/agent.md) | 兼容入口 |
| [DSE-agent/prompts/](DSE-agent/prompts/) | Parser、Architect、Worker、编码规范与检查清单 |
| [DSE-agent/references/](DSE-agent/references/) | 共用流程、状态、结果与证据契约 |
| [DSE-agent/src/hls_run.sh](DSE-agent/src/hls_run.sh) | 遵循执行策略的 HLS 阶段入口 |
| [DSE-agent/src/artifacts.py](DSE-agent/src/artifacts.py) | 输入／执行凭据检查与候选归档 |
| [DSE-agent/src/hypervolume.py](DSE-agent/src/hypervolume.py) | 正式候选种群的只读指标与超体积计算 |

</details>

<details>
<summary><strong>项目运行时目录</strong></summary>

```text
project/
├── benchmarks/<name>/       参考源码、测试与需求
├── workspace/<role>/        独立候选输入与 HLS 输出
├── results/<role>.json      Worker 结果与证据引用
├── state/                  Main 维护的指令、候选种群与谱系
├── knowledge/learned/       Main 维护的、关联实验依据的经验
├── tmp/<run_id>/            Parser 与 Architect 的临时提案
└── archive/<run_id>/        不可覆盖的轮次与候选快照
```

</details>

<a name="resources"></a>

## 资源与配置

**FPGA 工具。** 使用已安装的 Vivado/Vitis 工具链、器件许可证及所需硬件访问能力。仓库不附带 RapidWright 等可选辅助工具；不依赖这些工具的任务仍可使用现有原生工具完成。

**DSE 辅助脚本。** 执行需要 Python 3.10+ 和已配置的 Vitis CLI。精确超体积计算使用 NumPy 与 pymoo；缺少这一可选后端时仍可查看状态。多智能体轮次需要宿主平台提供文件访问、shell 执行和 Worker 委派能力。

**智能体平台。** Markdown 指令可供能够读取文件的不同平台使用。`agents/openai.yaml` 提供可选的界面元数据，不负责配置或选择模型。

### 配套示例

| 位置 | 内容 |
| --- | --- |
| [vivado-synth/examples/](vivado-synth/examples/) | UG901 的 RAM、DSP、ROM、SRL 和 FSM 设计 RTL 模板，以及配套数据文件 |
| [vivado-impl/examples/ug906/](vivado-impl/examples/ug906/) | 三组用于 QoR 建议的优化前／后 RTL 对照示例 |
| [vitis-hls-synthesis/examples/](vitis-hls-synthesis/examples/) | AMD HLS 设计、功能与入门教程 |

<details>
<summary><strong>单个技能目录的结构</strong></summary>

```text
skill-name/
├── SKILL.md            范围、决策指导与工作流程
├── agents/openai.yaml  兼容平台的界面元数据
├── REFERENCE.md        命令与属性参考（按需提供）
├── references/         专题指导（按需提供）
├── examples/           HDL/HLS 示例（按需提供）
└── evals/              评估用例或运行器封装（按需提供）
```

先阅读所选技能的 `SKILL.md`，再加载与任务相关的参考资料和示例。配套资源并非每项任务的统一前置条件。

</details>

## 支持项目

> **我的 Claude 账号被封了。** 😅 如果这个项目对你有帮助，欢迎赞助我开通 GPT Pro 20× 订阅，让我能继续开发。

## 许可证

采用 [GPL-2.0](LICENSE) 许可证。请保留配套第三方示例中的版权和许可证声明。

---

<p align="center"><a href="#top">返回顶部 ↑</a> &nbsp;·&nbsp; <a href="README.md">English</a> &nbsp;|&nbsp; <strong>简体中文</strong></p>
