# 拾光校园 Campus Glimmer

基于 Django 开发的校园二手交易平台，面向校内闲置物品流转场景，提供商品发布、浏览检索、购物车、订单、评论和站内私信等功能，帮助用户完成较完整的校内交易闭环。

## 项目简介

这个项目以校园二手交易为业务背景，围绕用户注册登录、商品展示与管理、交易流程和用户沟通等核心场景进行实现。系统同时提供 SimpleUI 后台管理能力，便于管理员审核商品、查看订单和维护基础数据。

## 技术栈

- Python 3.8
- Django 4.2
- SQLite
- Bootstrap 5
- JavaScript
- django-simpleui
- Locust

## 核心功能

- 用户模块：注册、登录、退出、个人资料编辑、头像上传
- 商品模块：商品发布、编辑、删除、分类浏览、详情展示、状态管理
- 搜索模块：按商品标题和描述进行关键词检索
- 交易模块：购物车、立即购买、订单查看
- 互动模块：商品评论、站内私信、会话记录
- 后台管理：基于 SimpleUI 的后台管理界面，支持商品审核和图片预览
- 性能测试：提供 `locustfile.py` 用于基础并发压测

## 项目亮点

- 使用 Django 按业务拆分 `accounts`、`listings`、`chat_messages` 三个核心应用
- 通过商品状态 `pending / available / sold` 实现基础审核与交易流转
- 支持多图商品展示、搜索功能与首页分页加载
- 实现买卖双方围绕商品场景进行私信沟通
- 提供后台商品图片预览与审核操作，增强管理体验
- 编写初始化脚本快速生成测试数据，便于本地演示和答辩展示

## 目录结构

```text
campus_glimmer/
├─ accounts/           # 用户与个人资料模块
├─ campus_glimmer/     # Django 项目配置
├─ chat_messages/      # 评论与私信模块
├─ listings/           # 商品、购物车、订单模块
├─ media/              # 本地开发媒体资源
├─ static/             # 静态资源
├─ templates/          # 前端模板
├─ init_data.py        # 初始化测试数据脚本
├─ locustfile.py       # 压测脚本
└─ manage.py
```

## 本地运行

1. 克隆仓库并进入项目目录

```bash
git clone https://github.com/kuku-1019/campus_glimmer-main.git
cd campus_glimmer-main
```

2. 创建并激活虚拟环境

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

4. 执行数据库迁移

```bash
python manage.py migrate
```

5. 初始化测试数据

```bash
python init_data.py
```

6. 启动项目

```bash
python manage.py runserver
```

启动后访问：

- 前台首页：`http://127.0.0.1:8000/`
- 后台管理：`http://127.0.0.1:8000/admin/`

## 演示账号

初始化脚本会生成一组本地演示账号，便于快速体验系统流程：

- 普通用户：`student_li / 123456`
- 管理员：`admin / admin123`

这些账号仅用于本地开发与演示环境。

## 仓库说明

- 当前仓库保留了项目运行所需的默认头像资源
- 本地数据库、缓存文件和商品上传资源建议不纳入版本控制
- 如果用于简历展示，建议在 GitHub 仓库中补充项目描述、置顶仓库和页面截图
