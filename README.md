---

[**English**](#english-version) | [**中文版**](#chinese-version)

<a name="english-version"></a>

# Tool Project - A Personal Toolbox of Utility Scripts

This is a collection of various Python scripts that I wrote on the fly to solve different problems encountered in my daily work. The main purpose of this project is to conveniently store, manage, and reuse these small tools, as well as to serve as one of my personal GitHub projects.

## Introduction

This project contains multiple independent script modules, each targeting a specific task such as file processing and image manipulation. By consolidating these scripts, I hope to improve my own efficiency and provide a reference for others who might need similar functionalities.

## Features & Modules

Based on the directory structure, this project currently includes the following core modules:

*   **`Design_partition`**:
    *   Connects to an LLM (tested with GPT-5) to obtain JSON coordinates for a design plan using a fixed prompt template, then draws a corresponding draft of the functional partitions.

*   **`Download_from_url`**:
    *   Batch downloads images from URLs listed in an Excel sheet.

*   **`Format_conversion`**:
    *   Batch unifies the format and renames images, designed as a preprocessing step for AI model training.

*   **`Img_insert_2_excel`**:
    *   Batch inserts images into an Excel sheet according to a specified format.

*   **`Plant_annotation`**:
    *   Connects to an LLM (tested with GPT-5) to obtain JSON coordinates of plants in an image using a fixed prompt template, intended for plant annotation. (Future updates may include direct API key integration for automatic returns).

*   **`Video_deal_tool`**:
    *   Batch processes videos by packaging them, extracting, and compressing their first frame.

## How to Use

Each tool module is standalone. You can run them by directly executing the corresponding Python script or by double-clicking the included `.bat` file where available.

---

<a name="chinese-version"></a>

[**English**](#english-version) | [**中文版**](#chinese-version)

# Tool Project - 个人实用脚本工具箱

这是一个汇集了我在日常工作中为了解决当下不同的问题，即时编写的各种Python脚本的工具集合。创建这个项目主要是为了方便地存储、管理和复用这些小工具，同时也作为个人GitHub项目之一。

## 简介

本项目包含多个独立的脚本模块，每个模块都针对一个特定的任务，例如文件处理、图像操作等。通过将这些脚本整合在一起，我希望能够提高个人效率，并为可能需要类似功能的朋友提供一些参考。

## 功能模块

根据目录结构，本项目目前包含以下几个核心功能模块：

*   **`Design_partition`**:
    *   可以接入LLM，通过固定的提示词范式获取设计规划的JSON坐标，并绘制对应的功能分区草图。（测试时接入的模型为GPT-5）

*   **`Download_from_url`**:
    *   可以通过读取Excel表，批量下载URL对应的图片。

*   **`Format_conversion`**:
    *   批量对图片进行格式统一与重命名（为AI模型训练进行数据预处理）。

*   **`Img_insert_2_excel`**:
    *   批量将图片按指定格式插入到Excel表格中。

*   **`Plant_annotation`**:
    *   可以接入LLM，通过固定的提示词范式获取图片中植物的JSON坐标，用于植物图像标注。（测试时接入的模型为GPT-5，后续可能更新为可直接接入API Key自动返回的形式）。

*   **`Video_deal_tool`**:
    *   用于批处理视频，将其打包、抽取并压缩视频的第一帧图像。

## 使用说明

每个工具模块都是独立的，你可以直接运行对应的Python脚本，或者直接双击其中的`.bat`批处理文件来使用。