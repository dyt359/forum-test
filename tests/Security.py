import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))# 把项目根目录加入sys.path, 保证任意目录运行都能导入tests/common包
import time
from datetime import datetime

from selenium.webdriver.common.by import By# 导入By类，用于定位元素
from selenium.webdriver.support.wait import WebDriverWait# 显式等待
from selenium.webdriver.support import expected_conditions as EC# 导入预期条件类，用于等待元素出现
from selenium.common.exceptions import TimeoutException# 超时异常, 用于检测 alert 未触发

from common.Utils import ForumDriver# 导入ForumDriver类，用于操作浏览器
from tests import ForumLogin# 导入ForumLogin类，用于登录


class Security:
    """安全测试: SQL 注入场景一/二已固化进 ForumLogin.loginErrTest(case 6/10); 本类聚焦 XSS 注入测试"""

    def __init__(self):
        self.driver = ForumDriver.driver# 获取浏览器驱动
        self.driver.get("http://127.0.0.1:58080/sign-in.html")# 打开登录页
        self.wait = WebDriverWait(self.driver, 5)# 显式等待，等待时间为5秒
        self.login = ForumLogin.ForumLogin()# 实例化ForumLogin类

    # XSS 注入测试(报告 3.2): test01 给 admin 发含 onerror 弹窗 payload 的私信, admin 查看时验证 alert 是否触发
    def xssTest(self):
        stamp = "XSS" + datetime.now().strftime("%H%M%S")# 唯一标识, 用于在收件箱中定位该私信
        payload = f'<img src=x onerror="alert(document.cookie)">{stamp}'# onerror 触发 alert 即证明内容被作为 HTML 渲染(未转义)
        nav_msg = "body > div.page > header.navbar.navbar-expand-md.navbar-light.d-print-none > div > div > div:nth-child(2) > div"#站内信入口

        # === 阶段一: test01 登录, 进首页第一个帖子详情页, 给 admin 发含 XSS payload 的私信 ===
        self.driver.get("http://127.0.0.1:58080/sign-in.html")
        self.login._login("test01", "test@123")
        # 登录是异步请求, 先等URL跳转到首页, 再等首页列表渲染(直接等列表元素容易超时)
        self.wait.until(EC.url_contains("index.html"))
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#artical-items-body")))
        self.driver.find_element(By.CSS_SELECTOR, "#artical-items-body > div:nth-child(1) .article_list_a_title").click()
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#btn_details_send_message"))).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#index_message_receive_content")))
        receiveName = self.driver.find_element(By.CSS_SELECTOR, "#index_message_receive_user_name").text
        assert "admin" in receiveName, f"发信收件人不是 admin: {receiveName}"
        self.driver.find_element(By.CSS_SELECTOR, "#index_message_receive_content").send_keys(payload)
        self.driver.find_element(By.CSS_SELECTOR, "#btn_index_send_message").click()
        toast = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".jq-toast-single")))
        assert "成功" in toast.text, f"发送 XSS 私信未提示成功: {toast.text}"
        print(f"test01 已向 admin 发送 XSS 私信: {stamp}")
        ForumDriver.getScreenshot("sendPayload")

        # === 阶段二: 切 admin 登录, 首页未读预览会立即渲染 XSS payload 触发 alert ===
        # 实测发现: alert 不在"打开私信抽屉"时触发, 而是登录进首页时未读预览就触发了
        # (alert 阻塞页面, 期间 driver.current_url 等调用会抛 UnexpectedAlertPresentException)
        # 所以登录后立即等 alert 出现, accept 后截图(截图时 alert 已关, 能截到首页未读 badge 状态作为旁证)
        self.driver.get("http://127.0.0.1:58080/sign-in.html")
        self.login._login("admin", "123456")
        try:
            alert = WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            alert_text = alert.text
            print(f"XSS 漏洞触发(首页未读预览即弹窗), alert 文本: {alert_text}")
            alert.accept()
            ForumDriver.getScreenshot("alertTriggered")
            xss_triggered = True
        except TimeoutException:
            # 5秒内无 alert, 认为私信内容已被转义, XSS 未触发
            ForumDriver.getScreenshot("noAlert")
            print("未触发 alert, 私信内容可能已被 HTML 转义")
            xss_triggered = False
        # 与测试报告 Bug#4 一致: 实际结果为弹窗出现, 即漏洞存在; 若已修复则断言失败提示
        assert xss_triggered, "XSS 未触发, 私信内容已被转义(缺陷已修复?)"
        print("XSS 注入测试完成: 漏洞存在, 首页未读预览即触发(影响面大于原报告描述)")


if __name__ == "__main__":
    sec = Security()
    sec.xssTest()
    ForumDriver.driver.quit()
