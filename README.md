# 🗂 文件夹别名工具（Folder Alias Tool）

一个用于给 **Windows 文件夹设置显示别名（中文 / 自定义名称）** 的桌面工具。  
原文件夹名称与路径保持不变，通过 `desktop.ini` 实现别名 —— **安全、直观、可撤销**。

> 适用于：工具集、软件目录、学习资料、课程文件等  
> 真实路径保持英文命名，资源管理器中显示中文标题，更易管理。

---

## ✨ 功能特性

- ✅ **单个设置文件夹别名**
- ✅ **批量扫描目录并一键设置**
- ✅ 支持 **前缀 / 后缀** 批量生成别名
- ✅ 支持 **清空别名**
- ✅ 支持 **撤销上次更改**
- ✅ 自动生成 `desktop.ini`
- ✅ 自动设置文件属性：
  - 文件夹：`System`
  - `desktop.ini`：`Hidden + System`

📌 **不会修改真实目录名称或路径** —— 只影响资源管理器的显示名称。

---

## 🖥 运行环境

- Windows 10 / 11
- Python 3.12+（仅运行源码时需要）
- Tkinter（Python 自带 GUI 库）

> 普通用户推荐直接下载 Release 中的 exe（无需 Python）。

---

## 🚀 下载与使用（推荐）

1. 打开仓库的 **Releases** 页面  
2. 下载最新的 `folder_alias_tool.exe`  
3. 双击运行（免安装）

---

## 🛠 从源码运行（开发者）

```bash
git clone https://github.com/<your-name>/folder-alias-tool.git
cd folder-alias-tool

py folder_alias_tool.py
```

---

## 🏗 构建独立 EXE（开发者）

```bash
py -m pip install --upgrade pip
py -m pip install pyinstaller

py -m PyInstaller -F -w folder_alias_tool.py
```

构建产物：

- `dist/folder_alias_tool.exe`

---

## 📌 使用说明

### 1）单个设置

1. 点击「浏览」选择一个文件夹  
2. 输入「显示别名」  
3. 点击「应用别名」

> 到该文件夹的**上一级目录**查看显示效果。  
> 若未立即刷新：重新打开资源管理器或重启即可。

### 2）批量设置

1. 选择根目录（例如 `E:\Tools\CTF`）  
2. 点击「扫描子文件夹」  
3. 在列表中可逐个修改别名  
4. 可使用：
   - 「将前缀/后缀应用到下方别名列表」
   - 「清空别名」
   - 「撤销上次更改」
5. 点击「应用批量别名到所有项」

---

## ⚠ 注意事项

- 某些情况下需重新打开资源管理器才能显示更新
- 仅对「文件夹」生效
- 不会更改文件夹真实名称、路径与结构
- 如需恢复，可删除目标文件夹内的 `desktop.ini`（以及取消文件夹 `System` 属性）

---

## 📄 License

本项目基于 **MIT License** 开源发布。

---

## 🤝 贡献

欢迎提交 Issue / PR 来改进功能、修复问题与优化体验。

---

## ⭐ 支持项目

如果这个工具对你有帮助，欢迎点个 **Star ⭐** 🙌
