import datetime
import os.path
import re
import sys

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


#创建一个浏览器对象
class Driver:
    driver = ""
    # 项目根目录（common/ 的上一级），让截图输出位置不依赖运行目录
    _ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _IMG_DIR = os.path.join(_ROOT, "images")

    def __init__(self):
        options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.implicitly_wait(2)
        self._RUN_DIR = self._makeRunDir()# 每次运行独立截图子目录
        self._LATEST_DIR = os.path.join(self._IMG_DIR, "latest")# 固定文件名副本, 供测试报告引用
        os.makedirs(self._LATEST_DIR, exist_ok=True)
        self._printEnv()

    def _printEnv(self):
        import platform
        caps = self.driver.capabilities
        print("=" * 60)
        print("测试环境信息")
        print("-" * 60)
        print(f"操作系统:   {platform.platform()}")
        print(f"Python:     {platform.python_version()}")
        print(f"浏览器:     {caps.get('browserName', '?')} {caps.get('browserVersion', '?')}")
        print(f"Driver:     chromedriver {caps.get('chrome', {}).get('chromedriverVersion', '?')}")
        print(f"项目路径:   {self._ROOT}")
        print(f"截图目录:   {self._RUN_DIR}")
        print("=" * 60)

    def _makeRunDir(self):
        #每次运行(实例化Driver)建独立子目录: images/2026-09-01/第N次测试, N=当天已有最大次数+1
        day_dir = os.path.join(self._IMG_DIR, datetime.datetime.now().strftime("%Y-%m-%d"))
        n = 1
        if os.path.exists(day_dir):
            for name in os.listdir(day_dir):
                m = re.fullmatch(r"第(\d+)次测试", name)
                if m and os.path.isdir(os.path.join(day_dir, name)):
                    n = max(n, int(m.group(1)) + 1)
        run_dir = os.path.join(day_dir, f"第{n}次测试")
        os.makedirs(run_dir)# 多级目录一起创建
        return run_dir

    def getScreenshot(self, label=None):
        #截图双份归档:
        #  1) 按次留存: images/2026-09-01/第N次测试/方法名[-label]-时间戳.png
        #  2) 固定副本: images/latest/类名_方法名[_label].png (每次运行覆盖, 测试报告用固定相对路径引用)
        #  label: 可选, 用于循环测试里区分各子场景(如 loginErrCase 传 "1" 生成 loginErrCase_1.png)
        frame = sys._getframe().f_back
        method = frame.f_code.co_name
        ts = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
        suffix = f"_{label}" if label else ""
        self.driver.save_screenshot(os.path.join(self._RUN_DIR, f"{method}{suffix}-{ts}.png"))
        self_obj = frame.f_locals.get("self")
        cls = type(self_obj).__name__ if self_obj is not None else None
        stable = f"{cls}_{method}{suffix}.png" if cls else f"{method}{suffix}.png"
        self.driver.save_screenshot(os.path.join(self._LATEST_DIR, stable))




def cleanToastText(text):
    #jq-toast 的 text 是 "×\n标题\n内容" 多行, 清洗成单行 "标题 | 内容"
    lines = [l.strip() for l in text.replace("×", "").splitlines() if l.strip()]
    return " | ".join(lines)


ForumDriver = Driver()
