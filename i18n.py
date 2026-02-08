# -*- coding: utf-8 -*-
"""
Simple i18n helper for OpenFilters.

Usage:
    - Call i18n.set_language("zh_CN") or "en" early in the startup.
    - Wrap all user-facing strings in _("...").
    - Keep translation keys = original English strings.
"""

try:
	import builtins  # type: ignore
except ImportError:  # pragma: no cover - Python 2 fallback
	import __builtin__ as builtins  # type: ignore

try:
	import user_config  # type: ignore
except ImportError:
	user_config = None  # type: ignore
import json
import os
import atexit
import re
import sys


class Translator(object):
	def __init__(self):
		# default language
		self._lang = "en"
		# translations[lang][original_text] = translated_text
		self.translations = {
			"zh_CN": {
				# 这里先给一些示例，后续会逐步补充
				# 菜单栏示例：
				"&File": "文件(&F)",
				"&Edit": "编辑(&E)",
				"&View": "视图(&V)",
				"&Help": "帮助(&H)",

				# 带快捷键的示例（注意保留 \tCtrl+N 部分）：
				"&New Project": "新建工程(&N)",
				"&Open Project": "打开工程(&O)",
				"&Save Project": "保存工程(&S)",
				"E&xit": "退出(&X)",

				# 对话框示例：
				"Optimization": "优化",
				"Target": "目标",
				"Target:": "目标：",
				"Cancel": "取消",
				"OK": "确定",
				"Apply": "应用",
				"Close": "关闭",

				# 提示信息示例：
				"Material not found": "未找到材料",
				"Do you want to save the current project before exiting?":
					"在退出之前要保存当前工程吗？",
				"Confirm Exit": "确认退出",
				"Error": "错误",
				"Warning": "警告",

				# 工具栏提示
				"Open": "打开",
				"Open a file": "打开文件",
				"Save": "保存",
				"Save current project": "保存当前工程",

				# 材料相关
				"Regular": "常规",
				"Mixture": "混合",
				"Constant": "常量",
				"Cauchy": "柯西",
				"Table": "表格",
				"Sellmeier": "塞尔迈耶",
				"Material error (%s): %s.": "材料错误（%s）：%s。",
				"Material error (%s).": "材料错误（%s）。",
				"Material does not exist": "材料不存在",
				"Impossible to open the file": "无法打开文件",
				"Cannot parse material because %s": "无法解析材料，因为 %s",
				"Multiple description in material": "材料描述重复",
				"Description must be on a single line": "描述必须在单行内",
				"Multiple definition in material": "材料定义重复",
				"Kind must be on a single line": "材料类型必须在单行内",
				"Kind must be regular or mixture": "材料类型必须为常规或混合",
				"Model must be on a single line": "模型必须在单行内",
				"Unknown material model!": "未知材料模型！",
				"Rate must be on a single line": "沉积速率必须在单行内",
				"Rate must be a float": "沉积速率必须为浮点数",
				"Rates must be floats": "沉积速率必须为浮点数",
				"Rates must be on a single line": "沉积速率必须在单行内",
				"Constants must be on multiple line": "常量必须为多行",
				"Constants must contain one description and one value": "常量必须包含一个描述和一个数值",
				"Constants values must be floats": "常量数值必须为浮点数",
				"Variables must be on multiple line": "变量必须为多行",
				"Variables must contain one description and a list of values": "变量必须包含一个描述和数值列表",
				"Variable values must be floats": "变量数值必须为浮点数",
				"Unknown keyword %s": "未知关键字 %s",
				"Missing information": "缺少必要信息",
				"A single value is necessary for constants": "常量必须为单一数值",
				"A single rate is necessary for regular material": "常规材料必须只有一个沉积速率",
				"Regular material cannot have variables": "常规材料不能有变量",
				"A list of rates must be provided for mixtures": "混合材料必须提供速率列表",
				"The number of rates must be equal to the number of properties": "速率数量必须等于属性数量",
				"Variable values must be lists": "变量数值必须为列表",
				"The number of variable values must be equal to the number of properties": "变量数值数量必须等于属性数量",
				"Invalid property format (%s)": "属性格式无效（%s）",
				"Invalid property format (there must be at least 2 mixtures)": "属性格式无效（至少需要 2 组混合）",
				"Invalid property format (there must be at least 2 mixtures and 2 wavelengths)": "属性格式无效（至少需要 2 组混合且至少 2 个波长）",
				"Invalid property format (first mixture number must be 0)": "属性格式无效（第一组混合编号必须为 0）",
				"Line %i of the file is formatted incorectly": "文件第 %i 行格式不正确",
				"The refractive index must be defined at least at 3 wavelengths": "折射率必须至少在 3 个波长点定义",
				"The refractive index is defined multiple times at the same wavelength": "同一波长的折射率被重复定义",

				# 模块加载
				"It was impossible to load the module %s. An exception occured and returned the value: %s.\n":
					"无法加载模块 %s。发生异常并返回值：%s。\n",
				"Could not find module %s. An exception occured and returned the value: %s.\n":
					"无法找到模块 %s。发生异常并返回值：%s。\n",
				"Could not extract the description from the module %s.\n":
					"无法从模块 %s 中提取描述。\n",
				"An error occured while creating the submodule %s of the module %s. An exception occured and returned the value:%s. Check that the description given in the module correspond to the functions.\n":
					"创建子模块 %s（模块 %s）时发生错误。发生异常并返回值：%s。请检查模块描述是否与函数对应。\n",

				# 命令行提示
				"%s is not a directory": "%s 不是目录",
				"%s is not readable": "%s 不可读",
				"change the user material directory": "更改用户材料目录",
				"&File": "&文件",
				"&Edit": "&编辑",
				"&Project": "&项目",
				"&Modules": "&模块",
				"&Optimization": "&优化",
				"&Tools": "&工具",
				"&Help": "&帮助",
				"&New Project\tCtrl+N": "&新建项目\tCtrl+N",
				"&Open Project...\tCtrl+O": "&打开项目...\tCtrl+O",
				"&Save Project\tCtrl+S": "&保存项目\tCtrl+S",
				"Save Project &As...": "项目另存为(&A)...",
				"&Import...": "&导入...",
				"&Export...": "&导出...",
				"E&xit\tAlt+X": "退出(&X)\tAlt+X",
				"&Undo\tCtrl+Z": "&撤消\tCtrl+Z",
				"&Redo\tCtrl+Y": "&重做\tCtrl+Y",
				"&Cut\tCtrl+X": "&剪切\tCtrl+X",
				"&Copy\tCtrl+C": "&复制\tCtrl+C",
				"&Paste\tCtrl+V": "&粘贴\tCtrl+V",
				"&Delete\tDel": "&删除\tDel",
				"&Select All\tCtrl+A": "&全选\tCtrl+A",
				"&Project Properties...": "&项目属性...",
				"&Materials...": "&材料...",
				"&Targets...": "&目标...",
				"&About OpenFilters...": "&关于 OpenFilters...",
				"New project": "新建项目",
				"Open project": "打开项目",
				"Save project": "保存项目",
				"Import material": "导入材料",
				"Export data": "导出数据",
				"Optimization options": "优化选项",
				"Run optimization": "运行优化",
				"Stop optimization": "停止优化",
				"Refractive index profile": "折射率剖面",
				"Transmittance / Reflectance": "透过率 / 反射率",
				"Color coordinates": "颜色坐标",
				"About OpenFilters": "关于 OpenFilters",
				"Optimization": "优化",
				"Target properties": "目标属性",
				"Layer properties": "膜层属性",
				"Material properties": "材料属性",
				"Project properties": "项目属性",
				"Export to file": "导出到文件",
				"Import from file": "从文件导入",
				"Confirm": "确认",
				"Error": "错误",
				"Warning": "警告",
				"Select Directory": "选择目录",
				"Choose a filename": "选择文件名",
				"OK": "确定",
				"Cancel": "取消",
				"Apply": "应用",
				"Add": "添加",
				"Remove": "移除",
				"Edit": "编辑",
				"Move Up": "上移",
				"Move Down": "下移",
				"Calculate": "计算",
				"Optimize": "优化",
				"Stop": "停止",
				"Close": "关闭",
				"Browse...": "浏览...",
				"Reset": "重置",
				"Save As...": "另存为...",
				"Import...": "导入...",
				"Clear": "清除",
				"Name:": "名称:",
				"Description:": "描述:",
				"Thickness (nm):": "厚度 (nm):",
				"Material:": "材料:",
				"Refractive index (n):": "折射率 (n):",
				"Extinction coefficient (k):": "消光系数 (k):",
				"Angle of incidence (°):": "入射角 (°):",
				"Wavelength range (nm):": "波长范围 (nm):",
				"Polarization:": "偏振:",
				"s-polarization": "s-偏振",
				"p-polarization": "p-偏振",
				"Average": "平均",
				"Target value:": "目标值:",
				"Tolerance:": "公差:",
				"Weight:": "权重:",
				"Substrate:": "基底:",
				"Incidence medium:": "入射介质:",
				"Layers:": "膜层:",
				"Total thickness:": "总厚度:",
				"Color space:": "颜色空间:",
				"Illuminant:": "光源:",
				"Create a new project": "创建新项目",
				"Open an existing project": "打开现有项目",
				"Save the current project": "保存当前项目",
				"Undo the last action": "撤消上次操作",
				"Redo the last undone action": "重做上次撤消的操作",
				"Add a new layer to the stack": "向膜堆添加新膜层",
				"Remove the selected layer": "移除选定膜层",
				"Edit the properties of the selected layer": "编辑选定膜层的属性",
				"Move the selected layer up": "上移选定膜层",
				"Move the selected layer down": "下移选定膜层",
				"Start the optimization process": "开始优化过程",
				"Stop the current optimization": "停止当前优化",
				"Ready": "就绪",
				"Calculating...": "计算中...",
				"Optimization finished.": "优化完成。",
				"Optimization stopped by user.": "用户停止了优化。",
				"Project saved successfully.": "项目保存成功。",
				"Do you want to save the changes to the current project?": "是否保存对当前项目的更改？",
				"File not found.": "未找到文件。",
				"Invalid input value.": "无效输入值。",
				"Please enter a valid number.": "请输入有效的数值。",
				"Material not found in database.": "数据库中未找到该材料。",
				"The project has been modified. Do you want to save the changes?": "项目已修改。是否保存更改？",
				"An error occurred while opening the file.": "打开文件时出错。",
				"Version:": "版本:",
				"Author:": "作者:",
				"Website:": "网站:",
				"License:": "许可证:",
				"F&ilter": "滤波器(&I)",
				"&Analyse": "分析(&A)",
				"&Design/Optimize": "设计/优化(&D)",
				"Preprod&uction": "预生产(&U)",
				"Close Project": "关闭项目",
				"Save Project As": "项目另存为...",
				"Revert": "还原",
				"Quit": "退出",
				"&Materials": "材料(&M)",
				"Add Filter": "添加滤波器",
				"Remove Filter": "移除滤波器",
				"Modify Filter": "修改滤波器",
				"Copy Filter": "复制滤波器",
				"Add Target": "添加目标",
				"Remove Target": "移除目标",
				"Modify Target": "修改目标",
				"Copy Target": "复制目标",
				"Read Target from File": "从文件读取目标",
				"Add Reflection Target": "添加反射目标",
				"Add Transmission Target": "添加透射目标",
				"Add Absorption Target": "添加吸收目标",
				"Add Reflection Spectrum Target": "添加反射光谱目标",
				"Add Transmission Spectrum Target": "添加透射光谱目标",
				"Add Absorption Spectrum Target": "添加吸收光谱目标",
				"Add Reflection Phase Target": "添加反射相位目标",
				"Add Transmission Phase Target": "添加透射相位目标",
				"Add Reflection GD Target": "添加反射群时延目标",
				"Add Transmission GD Target": "添加透射群时延目标",
				"Add Reflection GDD Target": "添加反射群时延色散目标",
				"Add Transmission GDD Target": "添加透射群时延色散目标",
				"Add Reflection Phase Spectrum Target": "添加反射相位光谱目标",
				"Add Transmission Phase Spectrum Target": "添加透射相位光谱目标",
				"Add Reflection GD Spectrum Target": "添加反射群时延光谱目标",
				"Add Transmission GD Spectrum Target": "添加透射群时延光谱目标",
				"Add Reflection GDD Spectrum Target": "添加反射群时延色散光谱目标",
				"Add Transmission GDD Spectrum Target": "添加透射群时延色散光谱目标",
				"Add Reflection Color Target": "添加反射颜色目标",
				"Add Transmission Color Target": "添加透射颜色目标",
				"Properties": "属性",
				"Add layer": "添加膜层",
				"Remove layer": "移除膜层",
				"Stack Formula": "膜系公式",
				"Import layer": "导入膜层",
				"Merge layers": "合并膜层",
				"Convert mixture to steps": "将混合物转换为阶梯",
				"Swap sides": "交换两侧",
				"Modules": "模块",
				"Export front index profile": "导出正面折射率剖面",
				"Export back index profile": "导出背面折射率剖面",
				"Calculate Reflection": "计算反射",
				"Calculate Transmission": "计算透射",
				"Calculate Absorption": "计算吸收",
				"Calculate Reflection Phase": "计算反射相位",
				"Calculate Transmission Phase": "计算透射相位",
				"Calculate Reflection GD": "计算反射群时延",
				"Calculate Transmission GD": "计算透射群时延",
				"Calculate Reflection GDD": "计算反射群时延色散",
				"Calculate Transmission GDD": "计算透射群时延色散",
				"Calculate Ellipsometry": "计算椭偏",
				"Calculate Color": "计算颜色",
				"Calculate Color Trajectory": "计算颜色轨迹",
				"Calculate Admittance Diagram": "计算导纳图",
				"Calculate Circle Diagram": "计算圆图",
				"Calculate Electric Field": "计算电场",
				"Calculate Reflection Monitoring": "计算反射监控",
				"Calculate Transmission Monitoring": "计算透射监控",
				"Calculate Ellipsometric Monitoring": "计算椭偏监控",
				"Reverse direction": "反向",
				"Show targets": "显示目标",
				"Show all results": "显示全部结果",
				"Export results as text": "导出结果为文本",
				"Export results as figure": "导出结果为图形",
				"Refine": "精修",
				"Needles / Refine": "针法 / 精修",
				"Steps / Refine": "阶梯 / 精修",
				"Fourier transform method": "傅里叶变换法",
				"Simulate random errors": "模拟随机误差",
				"Open Example Project": "打开示例项目",
				"Manage": "管理",
				"Change user material directory": "更改用户材料目录",
				"Add Absorption Spectrum Target": "添加吸收光谱目标",
				"Add Absorption Target": "添加吸收率目标",
				"Add Filter": "添加滤波器",
				"Add Reflection Color Target": "添加反射颜色目标",
				"Add Reflection GD Spectrum Target": "添加反射群延迟(GD)光谱目标",
				"Add Reflection GD Target": "添加反射群延迟(GD)目标",
				"Add Reflection GDD Spectrum Target": "添加反射群延迟色散(GDD)光谱目标",
				"Add Reflection GDD Target": "添加反射群延迟色散(GDD)目标",
				"Add Reflection Phase Spectrum Target": "添加反射相位光谱目标",
				"Add Reflection Phase Target": "添加反射相位目标",
				"Add Reflection Spectrum Target": "添加反射光谱目标",
				"Add Reflection Target": "添加反射率目标",
				"Add Target": "添加目标",
				"Add Transmission Color Target": "添加透过颜色目标",
				"Add Transmission GD Spectrum Target": "添加透过群延迟(GD)光谱目标",
				"Add Transmission GD Target": "添加透过群延迟(GD)目标",
				"Add Transmission GDD Spectrum Target": "添加透过群延迟色散(GDD)光谱目标",
				"Add Transmission GDD Target": "添加透过群延迟色散(GDD)目标",
				"Add Transmission Phase Spectrum Target": "添加透过相位光谱目标",
				"Add Transmission Phase Target": "添加透过相位目标",
				"Add Transmission Spectrum Target": "添加透过光谱目标",
				"Add Transmission Target": "添加透过率目标",
				"Add layer": "添加膜层",
				"Calculate Absorption": "计算吸收率",
				"Calculate Admittance Diagram": "计算导纳图",
				"Calculate Circle Diagram": "计算圆图",
				"Calculate Color": "计算颜色",
				"Calculate Color Trajectory": "计算颜色轨迹",
				"Calculate Electric Field": "计算电场",
				"Calculate Ellipsometric Monitoring": "计算椭偏监控",
				"Calculate Ellipsometry": "计算椭偏分析",
				"Calculate Reflection": "计算反射率",
				"Calculate Reflection GD": "计算反射群延迟(GD)",
				"Calculate Reflection GDD": "计算反射群延迟色散(GDD)",
				"Calculate Reflection Monitoring": "计算反射监控",
				"Calculate Reflection Phase": "计算反射相位",
				"Calculate Transmission": "计算透过率",
				"Calculate Transmission GD": "计算透过群延迟(GD)",
				"Calculate Transmission GDD": "计算透过群延迟色散(GDD)",
				"Calculate Transmission Monitoring": "计算透过监控",
				"Calculate Transmission Phase": "计算透过相位",
				"Close Project": "关闭项目",
				"Convert mixture to steps": "将混合层转换为阶梯层",
				"Copy Filter": "复制滤波器",
				"Copy Target": "复制目标",
				"Export back index profile": "导出后表面折射率剖面",
				"Export front index profile": "导出前表面折射率剖面",
				"Fourier transform method": "傅里叶变换法",
				"Import layer": "导入膜层",
				"Merge layers": "合并膜层",
				"Modify Filter": "修改滤波器",
				"Modify Target": "修改目标",
				"Modules": "模块",
				"Needles / Refine": "针式法 / 精炼",
				"Open Example Project": "打开示例项目",
				"Properties": "属性",
				"Quit": "退出",
				"Read Target from File": "从文件读取目标",
				"Refine": "精炼",
				"Remove Filter": "移除滤波器",
				"Remove Target": "移除目标",
				"Remove layer": "移除膜层",
				"Reverse direction": "反转方向",
				"Save Project As": "项目另存为",
				"Simulate random errors": "模拟随机误差",
				"Stack Formula": "堆栈公式",
				"Steps / Refine": "阶梯法 / 精炼",
				"Swap sides": "交换侧面",
				"&Close Project\tCtrl+W": "关闭项目(&C)\tCtrl+W",
				"Close the project": "关闭项目",
				"Save the project": "保存项目",
				"Save Project &As\tShift+Ctrl+S": "项目另存为(&A)\tShift+Ctrl+S",
				"Save the project under a new name": "将项目另存为新名称",
				"Revert the project to the last saved version": "还原到上次保存的项目",
				"&Quit\tCtrl+Q": "退出(&Q)\tCtrl+Q",
				"Quit the application": "退出应用程序",
				"&Add Filter\tCtrl+F": "添加滤波器(&F)\tCtrl+F",
				"&Add Filter": "添加滤波器(&F)",
				"Add a filter to the project": "向项目添加滤波器",
				"&Remove Filter": "移除滤波器(&R)",
				"Remove the selected filter from the project": "从项目中移除所选滤波器",
				"&Modify Filter": "修改滤波器(&M)",
				"Modify the selected filter": "修改所选滤波器",
				"&Copy Filter": "复制滤波器(&C)",
				"Make a copy of the selected filter": "复制所选滤波器",
				"Add &Target": "添加&目标",
				"Add &Reflection Target\tCtrl+R": "添加&反射目标\tCtrl+R",
				"Add &Reflection Target": "添加&反射目标",
				"Add a reflection target to the project": "向项目添加反射目标",
				"Add &Transmission Target\tCtrl+T": "添加&透射目标\tCtrl+T",
				"Add &Transmission Target": "添加&透射目标",
				"Add a transmission target to the project": "向项目添加透射目标",
				"Add &Absorption Target": "添加&吸收目标",
				"Add a absorption target to the project": "向项目添加吸收目标",
				"Add Reflection &Spectrum Target\tShift+Ctrl+R": "添加反射&光谱目标\tShift+Ctrl+R",
				"Add Reflection &Spectrum Target": "添加反射&光谱目标",
				"Add a reflection spectrum target to the project": "向项目添加反射光谱目标",
				"Add Transmission &Spectrum Target\tShift+Ctrl+T": "添加透射&光谱目标\tShift+Ctrl+T",
				"Add Transmission &Spectrum Target": "添加透射&光谱目标",
				"Add a transmission spectrum target to the project": "向项目添加透射光谱目标",
				"Add Absorption &Spectrum Target": "添加吸收&光谱目标",
				"Add a absorption spectrum target to the project": "向项目添加吸收光谱目标",
				"Add Reflection &Phase Target": "添加反射&相位目标",
				"Add a reflection phase target to the project": "向项目添加反射相位目标",
				"Add Transmission &Phase Target": "添加透射&相位目标",
				"Add a transmission phase target to the project": "向项目添加透射相位目标",
				"Add Reflection &GD Target": "添加反射&群时延目标",
				"Add a reflection GD target to the project": "向项目添加反射群时延目标",
				"Add Transmission &GD Target": "添加透射&群时延目标",
				"Add a transmission GD target to the project": "向项目添加透射群时延目标",
				"Add Reflection &GDD Target": "添加反射&群时延色散目标",
				"Add a reflection GDD target to the project": "向项目添加反射群时延色散目标",
				"Add Transmission &GDD Target": "添加透射&群时延色散目标",
				"Add a transmission GDD target to the project": "向项目添加透射群时延色散目标",
				"Add Reflection &Phase Spectrum Target": "添加反射&相位光谱目标",
				"Add a reflection phase spectrum target to the project": "向项目添加反射相位光谱目标",
				"Add Transmission &Phase Spectrum Target": "添加透射&相位光谱目标",
				"Add a transmission phase spectrum target to the project": "向项目添加透射相位光谱目标",
				"Add Reflection &GD Spectrum Target": "添加反射&群时延光谱目标",
				"Add a reflection GD spectrum target to the project": "向项目添加反射群时延光谱目标",
				"Add Transmission &GD Spectrum Target": "添加透射&群时延光谱目标",
				"Add a transmission GD spectrum target to the project": "向项目添加透射群时延光谱目标",
				"Add Reflection &GDD Spectrum Target": "添加反射&群时延色散光谱目标",
				"Add a reflection GDD spectrum target to the project": "向项目添加反射群时延色散光谱目标",
				"Add Transmission &GDD Spectrum Target": "添加透射&群时延色散光谱目标",
				"Add a transmission GDD spectrum target to the project": "向项目添加透射群时延色散光谱目标",
				"Add Reflection &Color Target": "添加反射&颜色目标",
				"Add a reflection color target to the project": "向项目添加反射颜色目标",
				"Add Transmission &Color Target": "添加透射&颜色目标",
				"Add a transmission color target to the project": "向项目添加透射颜色目标",
				"Read Target from &File": "从文件读取目标(&F)",
				"Read a spectrum in a file and add it as a target to the project": "读取文件中的光谱并作为目标加入项目",
				"&Remove Target": "移除目标(&R)",
				"Remove the selected target from the project": "从项目中移除所选目标",
				"&Modify Target": "修改目标(&M)",
				"Modify the selected target": "修改所选目标",
				"&Copy Target": "复制目标(&C)",
				"Make a copy of the selected target": "复制所选目标",
				"&Properties\tAlt+Enter": "属性(&P)\tAlt+Enter",
				"&Properties": "属性(&P)",
				"Show and modify the filter properties": "显示并修改滤波器属性",
				"&Add layer\tAlt+Ins": "添加膜层(&A)\tAlt+Ins",
				"&Add layer": "添加膜层(&A)",
				"Add a layer to the selected filter": "向所选滤波器添加膜层",
				"&Remove layer\tAlt+Del": "移除膜层(&R)\tAlt+Del",
				"&Remove layer": "移除膜层(&R)",
				"Remove a layer from the selected filter": "从所选滤波器移除膜层",
				"&Stack Formula\tAlt+S": "膜系公式(&S)\tAlt+S",
				"&Stack Formula": "膜系公式(&S)",
				"Design the selected filter using a stack formula": "使用膜系公式设计所选滤波器",
				"&Import layer": "导入膜层(&I)",
				"Import the index profile of a layer from a text file": "从文本文件导入膜层折射率剖面",
				"&Merge layers": "合并膜层(&M)",
				"Merge identical layers of the selected filter": "合并所选滤波器中的相同膜层",
				"&Convert mixture to steps": "将混合物转换为阶梯(&C)",
				"Convert mixture layers into steps in the selected filter": "将所选滤波器中的混合层转换为阶梯层",
				"&Swap sides": "交换两侧(&S)",
				"Swap sides of the selected filter": "交换所选滤波器的两侧",
				"M&odules": "模&块",
				"E&xport front index profile": "导出正面折射率剖面(&X)",
				"Export the front index profile of the selected filter": "导出所选滤波器的正面折射率剖面",
				"E&xport back index profile": "导出背面折射率剖面(&X)",
				"Export the back index profile of the selected filter": "导出所选滤波器的背面折射率剖面",
				"Calculate &Reflection\tAlt+R": "计算&反射\tAlt+R",
				"Calculate the reflection spectrum of the selected filter": "计算所选滤波器的反射光谱",
				"Calculate &Transmission\tAlt+T": "计算&透射\tAlt+T",
				"Calculate the transmission spectrum of the selected filter": "计算所选滤波器的透射光谱",
				"Calculate &Absorption": "计算&吸收",
				"Calculate the absorption spectrum of the selected filter": "计算所选滤波器的吸收光谱",
				"Calculate Reflection &Phase": "计算反射&相位",
				"Calculate the reflection phase spectrum of the selected filter": "计算所选滤波器的反射相位光谱",
				"Calculate Transmission &Phase": "计算透射&相位",
				"Calculate the transmission phase spectrum of the selected filter": "计算所选滤波器的透射相位光谱",
				"Calculate Reflection &GD": "计算反射&群时延",
				"Calculate the reflection GD spectrum of the selected filter": "计算所选滤波器的反射群时延光谱",
				"Calculate Transmission &GD": "计算透射&群时延",
				"Calculate the transmission GD spectrum of the selected filter": "计算所选滤波器的透射群时延光谱",
				"Calculate Reflection GD&D": "计算反射群时延色散(GD&D)",
				"Calculate the reflection GDD spectrum of the selected filter": "计算所选滤波器的反射群时延色散光谱",
				"Calculate Transmission GD&D": "计算透射群时延色散(GD&D)",
				"Calculate the transmission GDD spectrum of the selected filter": "计算所选滤波器的透射群时延色散光谱",
				"Calculate &Ellipsometry\tAlt+E": "计算&椭偏\tAlt+E",
				"Calculate the ellipsometric spectrum of the selected filter": "计算所选滤波器的椭偏光谱",
				"Calculate &Color\tAlt+C": "计算&颜色\tAlt+C",
				"Calculate the color of the selected filter": "计算所选滤波器的颜色",
				"Calculate &Color Trajectory\tShift+Alt+C": "计算&颜色轨迹\tShift+Alt+C",
				"Calculate the color trajectory of the selected filter": "计算所选滤波器的颜色轨迹",
				"Calculate A&dmittance Diagram": "计算&导纳图",
				"Calculate the admittance diagram of the selected filter": "计算所选滤波器的导纳图",
				"Calculate C&ircle Diagram": "计算&圆图",
				"Calculate the circle diagram of the selected filter": "计算所选滤波器的圆图",
				"Calculate Electric &Field": "计算&电场",
				"Calculate the electric field distribution in the selected filter": "计算所选滤波器的电场分布",
				"Calculate Reflection &Monitoring\tShift+Alt+R": "计算反射&监控\tShift+Alt+R",
				"Calculate the reflection monitoring curve of the selected filter": "计算所选滤波器的反射监控曲线",
				"Calculate Transmission &Monitoring\tShift+Alt+T": "计算透射&监控\tShift+Alt+T",
				"Calculate the transmission monitoring curve of the selected filter": "计算所选滤波器的透射监控曲线",
				"Calculate Ellipsometric &Monitoring\tShift+Alt+E": "计算椭偏&监控\tShift+Alt+E",
				"Calculate the ellipsometric monitoring curve of the selected filter": "计算所选滤波器的椭偏监控曲线",
				"Re&verse direction": "反&向",
				"Calculate &Reflection\tCtrl+Alt+R": "计算&反射\tCtrl+Alt+R",
				"Calculate the reflection spectrum in reverse direction of the selected filter": "计算所选滤波器反向的反射光谱",
				"Calculate &Transmission\tCtrl+Alt+T": "计算&透射\tCtrl+Alt+T",
				"Calculate the transmission spectrum in reverse direction of the selected filter": "计算所选滤波器反向的透射光谱",
				"Calculate the absorption in reverse direction of the selected filter": "计算所选滤波器反向的吸收光谱",
				"Calculate &Ellipsometry\tCtrl+Alt+E": "计算&椭偏\tCtrl+Alt+E",
				"Calculate the ellipsometric spectrum in reverse direction of the selected filter": "计算所选滤波器反向的椭偏光谱",
				"Calculate &Color\tCtrl+Alt+C": "计算&颜色\tCtrl+Alt+C",
				"Calculate the color in reverse direction of the selected filter": "计算所选滤波器反向的颜色",
				"Calculate &Color Trajectory\tCtrl+Shift+Alt+C": "计算&颜色轨迹\tCtrl+Shift+Alt+C",
				"Calculate the color trajectory in reverse direction of the selected filter": "计算所选滤波器反向的颜色轨迹",
				"Calculate Reflection &Monitoring\tCtrl+Shift+Alt+R": "计算反射&监控\tCtrl+Shift+Alt+R",
				"Calculate the reflection monitoring curve in reverse direction of the selected filter": "计算所选滤波器反向的反射监控曲线",
				"Calculate Transmission &Monitoring\tCtrl+Shift+Alt+T": "计算透射&监控\tCtrl+Shift+Alt+T",
				"Calculate the transmission monitoring curve in reverse direction of the selected filter": "计算所选滤波器反向的透射监控曲线",
				"Calculate Ellipsometric &Monitoring\tCtrl+Shift+Alt+E": "计算椭偏&监控\tCtrl+Shift+Alt+E",
				"Calculate the ellipsometric monitoring curve in reverse direction of the selected filter": "计算所选滤波器反向的椭偏监控曲线",
				"Show the targets in the plots": "在图中显示目标",
				"Show the results for all filters": "显示所有滤波器的结果",
				"Export the results to a text file": "将结果导出为文本文件",
				"Export the results to a figure file": "将结果导出为图形文件",
				"&Refine\tF1": "精&修\tF1",
				"Refine the selected filter": "精修所选滤波器",
				"&Needles / Refine\tF2": "针法 / 精修(&N)\tF2",
				"Synthesize the selected filter with the needle method": "使用针法合成所选滤波器",
				"&Steps / Refine\tF3": "阶梯 / 精修(&S)\tF3",
				"Synthesize the selected filter with the step method": "使用阶梯法合成所选滤波器",
				"&Fourier transform method\tF4": "傅里叶变换法(&F)\tF4",
				"Design the selected filter by the Fourier transform method": "使用傅里叶变换法设计所选滤波器",
				"Simulate &random errors\tAlt+F1": "模拟&随机误差\tAlt+F1",
				"Simulate the effect of random deposition errors": "模拟随机沉积误差的影响",
				"&Manage": "&管理",
				"Manage the materials": "管理材料",
				"&Change user material directory": "更改用户材料目录(&C)",
				"Change the directory where user specific materials are saved.": "更改用户材料保存目录。",
				"&Open Example Project": "打开示例项目(&O)",
				"Display program version, copyright and license information": "显示程序版本、版权和许可证信息",
				"&Close Project": "关闭项目(&C)",
				"&Quit": "退出(&Q)",
				"Save Project &As": "项目另存为(&A)",
				"Layer": "膜层",
				"Input file:": "输入文件：",
				"Nb header lines:": "表头行数：",
				"Multiband Rugate by R": "R 多带 Rugate",
				"&Open Project\tCtrl+O": "打开项目(&O)\tCtrl+O",
				"Rugate": "Rugate",
				"Simple layer": "简单膜层",
				"nm": "纳米",
				"nm OT": "纳米光学厚度",
				"QWOT": "四分之一波长光学厚度",
				"Thickness:": "厚度：",
				"Index:": "折射率：",
				"Side/Position": "侧面/位置",
				"front": "正面",
				"back": "背面",
				"Side:": "侧面：",
				"top": "顶部",
				"bottom": "底部",
				"at position ": "在位置 ",
				"Position:": "位置：",
			}
		}

	def set_language(self, lang):
		if not lang:
			return
		self._lang = lang

	def detect_language_from_config(self):
		"""Try to read language from user_config.language or user_config.LANG."""
		lang = None
		if user_config is not None:
			# 优先使用小写 language，如果没有再退回到大写 LANG
			lang = getattr(user_config, "language", None) or getattr(
				user_config, "LANG", None
			)
		if not lang:
			lang = "en"
		self._lang = lang

	def translate(self, text):
		"""Translate a string according to current language.

		Rules:
		- If language is 'en', return original text.
		- If translation exists, return it.
		- If no translation, fall back to original text.
		- For labels with accelerators, we may have to preserve the part after '\t'.
		"""
		if not text:
			return text
		lang = self._lang or "en"
		if lang == "en":
			return text

		lang_map = self.translations.get(lang, {})
		if _MISSING_ENABLED:
			_missing_collector.record_lookup()
			if text not in lang_map:
				_missing_collector.record_missing(text)
		full_tr = lang_map.get(text)
		if full_tr is not None:
			return full_tr

		# 处理菜单快捷键形式："Label\tCtrl+N"
		if "\t" in text:
			base, accel = text.split("\t", 1)
			base_tr = lang_map.get(base)
			if base_tr is not None:
				return "%s\t%s" % (base_tr, accel)
		return text


# 全局单例
_translator = Translator()


def init_from_config():
	"""Initialize language from user_config if available."""
	_translator.detect_language_from_config()
	lang = getattr(_translator, "_lang", None)
	if not lang:
		lang = "zh_CN"
	if not lang:
		lang = "en"
	_translator._lang = lang
	_translator.lang = lang
	if os.environ.get("OPENFILTERS_I18N_DEBUG") == "1":
		print("[i18n] lang=", _translator.lang)


def set_language(lang):
	_translator.set_language(lang)


def _(text):
	"""Global translation function.

	This will be bound to builtins._ at startup, so other modules can just call _('Text').
	"""
	return _translator.translate(text)


def install_builtin():
	"""Install '_' into builtins so all modules can use it without explicit import."""
	builtins._ = _
	if _MISSING_ENABLED:
		print("[i18n] collect_missing=1 path=%s" % _MISSING_PATH)
		print("[i18n] tip: set WXSUPPRESS_SIZER_FLAGS_CHECK=1 to suppress sizer flag asserts during collection")
	if os.environ.get("OPENFILTERS_I18N_SELFTEST") == "1":
		print(builtins._("&File"))
		print(builtins._("Add Target"))
		print(builtins._("Calculate Reflection"))


_MISSING_ENABLED = os.environ.get("OPENFILTERS_I18N_COLLECT_MISSING") == "1"
_MISSING_PATH = os.environ.get("OPENFILTERS_I18N_MISSING_PATH")
if not _MISSING_PATH:
	_MISSING_PATH = os.path.join(os.path.dirname(__file__), "i18n_missing.json")
_REPORT_ENABLED = os.environ.get("OPENFILTERS_I18N_REPORT") == "1"


class _I18nMissingCollector(object):
	def __init__(self):
		self.counts = {}
		self.total_lookups = 0
		self._cjk_re = re.compile(r"[\u4e00-\u9fff]")
	
	def record_lookup(self):
		self.total_lookups += 1
	
	def record_missing(self, text):
		if not text:
			return
		if not text.strip():
			return
		if self._cjk_re.search(text):
			return
		self.counts[text] = self.counts.get(text, 0) + 1
	
	def dump(self):
		if not _MISSING_ENABLED:
			return
		data = {
			"counts": self.counts,
			"total_lookups": self.total_lookups
		}
		with open(_MISSING_PATH, "w") as output:
			json.dump(data, output, indent=2, ensure_ascii=False)
	
	def report(self):
		if not _REPORT_ENABLED:
			return
		total = self.total_lookups
		missing_total = sum(self.counts.values())
		coverage = 0.0
		if total > 0:
			coverage = (float(total - missing_total) / float(total)) * 100.0
		print("[i18n] coverage=%.2f%% total=%d missing=%d" % (coverage, total, missing_total))
		if self.counts:
			top_items = sorted(self.counts.items(), key=lambda item: item[1], reverse=True)[:10]
			for key, count in top_items:
				print("[i18n] missing %d: %s" % (count, key))


_missing_collector = _I18nMissingCollector()


def _missing_atexit():
	_missing_collector.dump()
	_missing_collector.report()


if _MISSING_ENABLED or _REPORT_ENABLED:
	atexit.register(_missing_atexit)
	if _MISSING_ENABLED:
		_prev_hook = sys.excepthook
		def _missing_excepthook(exc_type, exc_value, exc_tb):
			_missing_atexit()
			if _prev_hook:
				_prev_hook(exc_type, exc_value, exc_tb)
		sys.excepthook = _missing_excepthook


_DUMP_ENABLED = os.environ.get("OPENFILTERS_I18N_DUMP") == "1"
_DUMP_PATH = os.environ.get("OPENFILTERS_I18N_DUMP_PATH")
if not _DUMP_PATH:
	_DUMP_PATH = os.path.join(os.path.dirname(__file__), "i18n_dump.json")


class _I18nDumpCollector(object):
	def __init__(self):
		self.menus = []
		self.toolbar = []
		self.dialogs = []
		self.raw_strings = set()
		self._menu_keys = set()
		self._toolbar_keys = set()
		self._dialog_keys = set()
	
	def _add_raw(self, text):
		if text:
			self.raw_strings.add(text)
	
	def add_menu_entry(self, path, label):
		key = (path, label)
		if key in self._menu_keys:
			return
		self._menu_keys.add(key)
		self.menus.append({"path": path, "label": label})
		self._add_raw(label)
	
	def add_toolbar_entry(self, label, short_help, long_help):
		key = (label, short_help, long_help)
		if key in self._toolbar_keys:
			return
		self._toolbar_keys.add(key)
		self.toolbar.append({
			"label": label or "",
			"short_help": short_help or "",
			"long_help": long_help or ""
		})
		self._add_raw(label)
		self._add_raw(short_help)
		self._add_raw(long_help)
	
	def add_dialog_entry(self, title, buttons, message=None):
		buttons_tuple = tuple(buttons or [])
		key = (title, buttons_tuple, message)
		if key in self._dialog_keys:
			return
		self._dialog_keys.add(key)
		self.dialogs.append({
			"title": title or "",
			"buttons": list(buttons_tuple),
			"message": message or ""
		})
		self._add_raw(title)
		self._add_raw(message)
		for button in buttons_tuple:
			self._add_raw(button)
	
	def dump(self):
		if not _DUMP_ENABLED:
			return
		data = {
			"lang": getattr(_translator, "_lang", None) or getattr(_translator, "lang", ""),
			"menus": self.menus,
			"toolbar": self.toolbar,
			"dialogs": self.dialogs,
			"raw_strings": sorted(self.raw_strings)
		}
		with open(_DUMP_PATH, "w") as output:
			json.dump(data, output, indent=2, ensure_ascii=False)


_dump_collector = _I18nDumpCollector()


def debug_collect_menus(menu_bar):
	if not _DUMP_ENABLED or menu_bar is None:
		return
	
	def item_label(menu_item):
		if hasattr(menu_item, "GetItemLabelText"):
			return menu_item.GetItemLabelText()
		return menu_item.GetItemLabel()
	
	def walk_menu(menu, path_prefix):
		if not menu:
			return
		for item in menu.GetMenuItems():
			if item.IsSeparator():
				continue
			label = item_label(item)
			if not label:
				continue
			path = "%s > %s" % (path_prefix, label)
			_dump_collector.add_menu_entry(path, label)
			submenu = item.GetSubMenu()
			if submenu:
				walk_menu(submenu, path)
	
	for i in range(menu_bar.GetMenuCount()):
		menu_label = menu_bar.GetMenuLabel(i)
		if not menu_label:
			continue
		_dump_collector.add_menu_entry(menu_label, menu_label)
		menu = menu_bar.GetMenu(i)
		walk_menu(menu, menu_label)
	
	_dump_collector.dump()


def debug_collect_toolbar(toolbar):
	if not _DUMP_ENABLED or toolbar is None:
		return
	
	if hasattr(toolbar, "GetToolsCount") and hasattr(toolbar, "GetToolByPos"):
		for i in range(toolbar.GetToolsCount()):
			tool = toolbar.GetToolByPos(i)
			if not tool:
				continue
			label = tool.GetLabel() if hasattr(tool, "GetLabel") else ""
			short_help = tool.GetShortHelp() if hasattr(tool, "GetShortHelp") else ""
			long_help = tool.GetLongHelp() if hasattr(tool, "GetLongHelp") else ""
			_dump_collector.add_toolbar_entry(label, short_help, long_help)
	
	_dump_collector.dump()


def debug_collect_dialog(title, buttons, message=None):
	if not _DUMP_ENABLED:
		return
	_dump_collector.add_dialog_entry(title, buttons, message)
	_dump_collector.dump()

