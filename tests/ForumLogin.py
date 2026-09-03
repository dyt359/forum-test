from selenium.webdriver.common.by import By# 导入By类，用于定位元素
from selenium.webdriver.support.wait import WebDriverWait# 显式等待
from selenium.webdriver.support import expected_conditions as EC# 导入预期条件类，用于等待元素出现

# 导入预期条件类，用于等待元素出现
from common.Utils import ForumDriver, cleanToastText# 导入ForumDriver类(浏览器)与toast文案清洗函数

#用户认证测试
class ForumLogin:
    url = ""
    driver = ""

    def __init__(self):
        self.url = "http://127.0.0.1:58080/sign-in.html"# 登录页URL
        self.driver = ForumDriver.driver# 获取浏览器驱动
        self.driver.get(self.url)# 打开登录页
        self.wait = WebDriverWait ( self.driver , 5 )# 显式等待，等待时间为5秒
    #登录方法
    def _login(self, username, password):
        self.driver.find_element(By.CSS_SELECTOR, "#username").clear()
        self.driver.find_element(By.CSS_SELECTOR, "#password").clear()
        self.driver.find_element(By.CSS_SELECTOR, "#username").send_keys(username)
        self.driver.find_element(By.CSS_SELECTOR, "#password").send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, "#submit").click()

    #登录成功测试
    def loginSucTest(self):
        self._login("admin", "123456")
        #断言登录成功
        self.assertLogin("index.html")
        self.driver.find_element(By.CSS_SELECTOR, "#index_nav_nickname")
        ForumDriver.getScreenshot()
        self.driver.back()

    #断言登录
    def assertLogin(self,url):
        self.wait.until ( EC.url_contains ( url ) )
        print("当前实际URL:", self.driver.current_url)
        assert self.driver.current_url == "http://127.0.0.1:58080/"+url

    #弹窗内容检查
    def assertToast(self, toast_text, css_selector):
        # toast会自动消失且新toast会替换旧容器, 直接visibility+读text会碰到残留旧toast或StaleElementReference;
        # 改用text_to_be_present_in_element: 内部捕获stale并重试, 旧toast文案不匹配时等到新toast出现
        self.wait.until (EC.text_to_be_present_in_element ((By.CSS_SELECTOR , css_selector) , toast_text))
        toast = self.driver.find_element(By.CSS_SELECTOR, css_selector)
        print("弹窗提示:", cleanToastText(toast.text))
        assert toast_text in toast.text

    #异常登录辅助函数（对应 ForumIndex.PlateSwitching）
    def loginErrCase(self, username, password, toast_text, css_selector):
        self.driver.get(self.url)# 每条用例重置页面, 避免前一条的表单校验状态残留
        self._login(username, password)
        #断言登录失败：验证警告弹窗
        self.assertToast(toast_text, css_selector)
        #断言登录失败（应停留在登录页）
        self.assertLogin("sign-in.html")
        ForumDriver.getScreenshot()

    #异常登录测试（对应 ForumIndex.boardTest：字典 + 循环）
    def loginErrTest(self):
        cases = {
            "1": ("admin1",        "1234",     "用户名或密码错误",   ".jq-toast-single.jq-icon-warning"),
            "2": ("admin1",        "123456",   "用户名或密码错误",   ".jq-toast-single.jq-icon-warning"),
            "3": ("admin",         "1234",     "用户名或密码错误",   ".jq-toast-single.jq-icon-warning"),
            "4": ("admin",         "",         "密码不能为空",       "#signInForm > div.mb-2 > div > div"),
            "5": ("",              "123456",   "用户名不能为空",     "#signInForm > div.mb-3 > div"),
            "6": ("' OR '1'='1",   "1",        "用户名或密码错误",   ".jq-toast-single.jq-icon-warning"),
            "7": ("admin",         "12345",    "用户名或密码错误",   ".jq-toast-single.jq-icon-warning"),
            "8": ("admin",         "a1",   "用户名或密码错误",   ".jq-toast-single.jq-icon-warning"),
            "9": ("",              "",         "用户名不能为空",     "#signInForm > div.mb-3 > div"),
            # SQL 注入场景一(报告 3.1 场景一): 用户名带单引号 123', 预期被参数化查询挡下, 提示用户名或密码错误
            "10": ("123'",          "1",        "用户名或密码错误",   ".jq-toast-single.jq-icon-warning"),
        }
        for c in cases:
            self.loginErrCase(*cases[c])
            ForumDriver.getScreenshot(c)

    def LoginPageCheck(self):
        self.driver.find_element ( By.CSS_SELECTOR , "#username" )
        self.driver.find_element ( By.CSS_SELECTOR , "#password" )
        self.driver.find_element ( By.CSS_SELECTOR , "#submit" )
        self.driver.find_element( By.CSS_SELECTOR , "body > div.page.page-center > div > div > div:nth-child(1) > div > div.text-center.text-muted.mt-3 > a" )
        ForumDriver.getScreenshot()

if __name__ == "__main__":
    test = ForumLogin()
    test.loginSucTest()
    test.loginErrTest()
    test.LoginPageCheck()