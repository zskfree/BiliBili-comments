# BiliBili-comments 数据分析项目

本项目用于对B站视频评论、视频内容及创作者信息进行批量分析，输出情感分布、关键词、可视化图表和分析报告。

## 目录结构

- `analysis.py`         主分析脚本，包含数据加载、分析、可视化与报告生成
- `setup_environment.py` 一键环境配置与依赖安装脚本
- `requirements.txt`    Python依赖包列表
- `config.yaml`         分析参数与可视化配置
- `data/`               存放原始数据（评论、视频、创作者）
- `results/`            输出分析结果（图表、报告、关键词等）
- `test.py`             数据结构与格式检查脚本

## 快速开始

1. **环境准备**

   推荐使用 Python 3.8 及以上版本。

   一键配置环境并安装依赖：

   ```sh
   python setup_environment.py
   ```

2. **数据准备**

   将待分析的原始数据（如 `search_comments_*.json` 等）放入 `data/` 目录。

3. **运行分析**

   ```sh
   python analysis.py
   ```

4. **查看结果**

   - 分析报告：`results/analysis_report.md`
   - 关键词词云与图表：`results/`
   - 详细分析数据：`results/analysis_results.json`

## 主要功能

- 评论情感分析（积极/中性/消极）
- 评论、标题、描述、签名等多源关键词提取（TF-IDF、TextRank、组合算法）
- 视频播放量、创作者粉丝等基础统计
- 词云与多种可视化图表自动生成
- Markdown 格式分析报告自动输出

## 依赖环境

详见 [requirements.txt](requirements.txt)。主要依赖：

- pandas, numpy, matplotlib, seaborn
- jieba, snownlp, wordcloud
- scikit-learn, tqdm, jsonlines

## 其他说明

- 支持自动检测和配置国内 pip 镜像源，提升依赖安装速度
- 支持自动检测中文字体，保证词云和图表中文显示正常
- 可通过 `test.py` 检查数据文件格式和字段完整性

---

如需自定义分析参数，请修改 [config.yaml](config.yaml)。
