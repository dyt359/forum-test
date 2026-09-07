# 论坛系统自动化测试

针对在线论坛系统（SPA 单页应用）搭建的 Selenium UI 自动化测试框架，覆盖注册、登录、首页、个人中心、发帖、详情页、站内信、安全测试等模块，共 **42 条用例**，发现 **15 个缺陷**，支持一键重复回归。

## 测试环境

| 项目 | 版本 |
|------|------|
| 操作系统 | Windows 11 |
| Python | 3.10.20 |
| 浏览器 | Chrome 151 |
| 驱动 | chromedriver 151（webdriver-manager 自动匹配） |
| 依赖 | selenium 4.0.0 / webdriver-manager 4.1.2 / PyMySQL 1.2.0 |

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动被测论坛系统（http://127.0.0.1:58080）

# 3. 运行全部测试
python tests/RunTest.py
```

测试截图自动归档至 `images/<日期>/第N次测试/`，同时刷新 `images/latest/` 固定副本供报告引用。

## 项目结构

```
ForumTest/
├── common/
│   ├── Utils.py          # 浏览器单例、截图归档、环境信息打印
│   └── DBUtil.py         # 物理删除测试用户，保证用例可重复执行
├── tests/
│   ├── RunTest.py        # 串行入口，按顺序执行各模块
│   ├── ForumSignup.py    # 注册测试（4 条）
│   ├── ForumLogin.py     # 登录测试（10 条，含 SQL 注入）
│   ├── ForumIndex.py     # 首页测试（8 条）
│   ├── PersonalCenter.py # 个人中心测试（5 条）
│   ├── Posting.py        # 发帖/编辑/删除/站内信（5 条）
│   ├── PostDetailsPage.py# 详情页测试（9 条）
│   ├── MyPost.py         # 我的帖子测试（6 条）
│   └── Security.py       # 安全测试（2 条，XSS 注入）
├── 测试报告/
│   ├── 论坛系统自动化测试报告.md
│   ├── 论坛系统自动化测试用例.md
│   └── 论坛系统自动化测试用例.xmind
├── images/latest/        # 报告引用截图
├── requirements.txt
└── LICENSE
```

## 框架特性

- **全程显式等待**：WebDriverWait + expected_conditions，禁止与隐式等待混用
- **SPA 适配**：不使用 driver.refresh，登录后等 URL 跳转再操作；CodeMirror 富文本用 JS API 操作
- **数据自恢复**：test01 用户每次运行前重建，admin 资料/密码用例结束自动还原
- **安全测试**：SQL 注入两场景固化进登录用例，XSS payload 独立验证 alert 触发
- **截图归档**：按日期+次数归档，latest 目录供报告自动引用

## 测试结果

42 条用例全部通过，发现 15 个缺陷（4 严重 / 5 一般 / 6 轻微），详见 [测试报告](测试报告/论坛系统自动化测试报告.md)。

## License

MIT
