import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from common.Utils import ForumDriver
from common.DBUtil import permanent_delete_user

#用户注册测试
class ForumSignup:
    url = ""
    driver = ""

    def __init__(self):
        self.url = "http://127.0.0.1:58080/sign-up.html"
        self.driver = ForumDriver.driver
        self.driver.get(self.url)
        self.wait = WebDriverWait ( self.driver , 10 )

    def _signUp(self,username,nickname,password,passwordRepeat,policy=1):
        self.driver.find_element ( By.CSS_SELECTOR , "#username" ).clear ()
        self.driver.find_element ( By.CSS_SELECTOR , "#nickname" ).clear ()
        self.driver.find_element ( By.CSS_SELECTOR , "#password" ).clear ()
        self.driver.find_element ( By.CSS_SELECTOR , "#passwordRepeat" ).clear ()

        self.driver.find_element ( By.CSS_SELECTOR , "#username" ).send_keys ( username )
        self.driver.find_element ( By.CSS_SELECTOR , "#nickname" ).send_keys ( nickname )
        self.driver.find_element ( By.CSS_SELECTOR , "#password" ).send_keys ( password )
        self.driver.find_element ( By.CSS_SELECTOR , "#passwordRepeat" ).send_keys ( passwordRepeat )
        if policy:# 1=勾选协议(默认), 0=不勾选
            self.driver.find_element( By.CSS_SELECTOR , "#policy" ).click ()
        self.driver.find_element ( By.CSS_SELECTOR , "#submit" ).click ()
    def _inspect(self,Check_position,Inspection_content,label=None):
        # 断言登录失败：验证警告弹窗
        toast = self.wait.until (
            EC.visibility_of_element_located ( (By.CSS_SELECTOR , Check_position) ) )
        # print ( "弹窗提示:" , toast.text )
        assert Inspection_content in toast.text
        ForumDriver.getScreenshot(label)# 截图在页面重置前, 保留错误状态
        self.driver.get ( self.url )


    #正常注册测试
    def NormalSignupTest(self):
        # 清理上次测试残留的 test01，保证可重复注册
        permanent_delete_user("test01")
        self._signUp("test01","测试同学","test@123","test@123")

        self.wait.until ( EC.url_contains ( "sign-in.html" ) )
        assert "sign-in.html" in self.driver.current_url , "注册后未跳转到首页"
        print ( "当前实际URL:" , self.driver.current_url )
        ForumDriver.getScreenshot ()
        self.driver.get ( self.url )

    #异常注册测试

    #异常注册辅助函数
    def signupErrCase(self, username, nickname, password, passwordRepeat, Check_position, Inspection_content, label=None):
        self._signUp(username, nickname, password, passwordRepeat)
        self._inspect(Check_position, Inspection_content, label)

    #异常注册测试（字典 + 循环）
    def AbnormalSignupTest(self):
        cases = {
            "01": ("admin",  "测试同学", "test@123",  "test@123",   ".jq-toast-single.jq-icon-warning",                "用户已存在"),
            "02": ("test01", "测试同学", "test@123",  "test@1234",  "#signUpForm > div > div:nth-child(5) > div > div", "请检查确认密码"),
            "03": ("",       "测试同学", "test@123",  "test@123",   "#signUpForm > div > div:nth-child(2) > div",       "用户名不能为空"),
            "04": ("test01", "",         "test@123",  "test@123",   "#signUpForm > div > div:nth-child(3) > div",       "昵称不能为空"),
            "05": ("test01", "测试同学", "",          "test@123",   "#signUpForm > div > div:nth-child(4) > div",       "密码不能为空"),
            "06": ("test01", "测试同学", "test@123",  "",           "#signUpForm > div > div:nth-child(5) > div",       "请检查确认密码"),
            #已知缺陷密码为纯数字可注册
            #"07": ("test01", "测试同学", "123456",  "123456",       "#signUpForm > div > div:nth-child(5) > div",       "密码不能为纯数字"),
            #已知缺陷密码长度小于6位可注册
            #"08": ("test01", "测试同学", "a1",       "a1",           "#signUpForm > div > div:nth-child(5) > div",      "密码长度必须大于等于6位"),
        }
        for c in cases:
            self.signupErrCase(*cases[c], label=c)

    #不勾选协议测试：前端直接拦截(表单标红 is-invalid), 不发请求、不跳转
    def PolicyUncheckTest(self):
        self.driver.get(self.url)# 重置页面状态, 保证协议框未被勾选
        self._signUp("test01","测试同学","test@123","test@123",policy=0)
        assert "sign-up.html" in self.driver.current_url, "未勾选协议却注册成功"
        policyClass = self.driver.find_element(By.CSS_SELECTOR, "#policy").get_attribute("class")
        assert "is-invalid" in policyClass, f"协议勾选框未标红: class=[{policyClass}]"
        print("未勾选协议被拦截, 协议框标红:", policyClass)
        ForumDriver.getScreenshot()

    # 检查注册页面元素是否存在
    def SignupPageElementCheck(self):
        self.driver.find_element ( By.CSS_SELECTOR , "#username" )
        self.driver.find_element ( By.CSS_SELECTOR , "#nickname" )
        self.driver.find_element ( By.CSS_SELECTOR , "#password" )
        self.driver.find_element ( By.CSS_SELECTOR , "#passwordRepeat" )
        self.driver.find_element ( By.CSS_SELECTOR , "#policy" )
        self.driver.find_element ( By.CSS_SELECTOR , "#submit" )
        self.driver.find_element ( By.CSS_SELECTOR , "body > div > div > div.text-center.text-muted.mt-3 > a" )
        ForumDriver.getScreenshot()


if __name__ == "__main__":
    test = ForumSignup()
    test.NormalSignupTest()
    test.AbnormalSignupTest()
    test.PolicyUncheckTest()
    test.SignupPageElementCheck()


    ForumDriver.driver.quit ()
