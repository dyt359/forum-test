#我的帖子测试

import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
from datetime import datetime

from selenium.webdriver.common.by import By# 导入By类，用于定位元素
from selenium.webdriver.support.wait import WebDriverWait# 显式等待
from selenium.webdriver.support import expected_conditions as EC# 导入预期条件类，用于等待元素出现
from common.Utils import ForumDriver# 导入ForumDriver类，用于操作浏览器
from tests import ForumLogin# 导入ForumLogin类，用于登录

# 定义个人中心类
class PersonalCenter():
    url = ""
    driver = ""
    def __init__(self):
        self.url = "http://127.0.0.1:58080/sign-in.html"
        self.driver = ForumDriver.driver# 获取浏览器驱动
        self.driver.get(self.url)# 打开登录页
        self.wait = WebDriverWait ( self.driver , 5 )# 显式等待，等待时间为5秒
        self.driver.maximize_window ()# 最大化窗口
    
    def _login(self, username, password):# 登录方法
        self.driver.find_element(By.CSS_SELECTOR, "#username").clear()
        self.driver.find_element(By.CSS_SELECTOR, "#password").clear()
        self.driver.find_element(By.CSS_SELECTOR, "#username").send_keys(username)
        self.driver.find_element(By.CSS_SELECTOR, "#password").send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, "#submit").click()

    def loginTest(self):# 登录测试账号
        self._login("admin", "123456")
        self.wait.until(EC.url_contains("index.html"))
        ForumDriver.getScreenshot()
    
    #进入我的帖子页（点用户下拉 -> 个人中心 ）
    def _enterMyPost(self):
        UserInformation = "body > div.page > header.navbar.navbar-expand-md.navbar-light.d-print-none > div > div > div.nav-item.dropdown > a"#用户信息下拉
        PersonalCenterTitle = "#bit-forum-content > div.page-header.d-print-none > div > div > div > h2"#个人中心标题
        self.driver.find_element(By.CSS_SELECTOR, UserInformation).click()#点击用户信息
        self.driver.find_element(By.CSS_SELECTOR, "#index_user_settings").click()#点击个人中心
        self.wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, PersonalCenterTitle), "用户中心"))#等待标题变成"用户中心"
        toast = self.driver.find_element(By.CSS_SELECTOR, PersonalCenterTitle)#获取个人中心标题
        print("个人中心标题:", toast.text)

        assert toast.text == "用户中心"#断言个人中心标题为"用户中心"
        ForumDriver.getScreenshot()
    
    #修改昵称（改完断言生效后再改回 admin，保证测试可重复执行）
    def _changeUser(self):
        namebox = "#setting_input_nickname"#昵称输入框
        ModifyButton = "#setting_submit_nickname"#修改按钮
        toast = ".jq-toast-single"#提交结果提示
        NavNickName = "#index_nav_nickname"#顶部导航昵称
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, namebox)))# 等待昵称输入框可见

        self.driver.find_element(By.CSS_SELECTOR, namebox).clear()#清空昵称输入框
        self.driver.find_element(By.CSS_SELECTOR, namebox).send_keys("newNickname")
        self.driver.execute_script("arguments[0].click();",
            self.driver.find_element(By.CSS_SELECTOR, ModifyButton))# JS 点击修改按钮，避免视口外被拦截
        self.wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, toast), "成功"))# 等待提交成功提示
        #断言昵称已修改：顶部导航昵称应实时更新为 newNickname
        assert self.driver.find_element(By.CSS_SELECTOR, NavNickName).text.strip() == "newNickname", \
            f"昵称修改失败，当前导航昵称: [{self.driver.find_element(By.CSS_SELECTOR, NavNickName).text.strip()}]"
        print("修改后导航昵称:", self.driver.find_element(By.CSS_SELECTOR, NavNickName).text.strip())
        ForumDriver.getScreenshot()

        #把昵称改回 admin，保证其他测试（登录等）不受影响
        self.driver.find_element(By.CSS_SELECTOR, namebox).clear()
        self.driver.find_element(By.CSS_SELECTOR, namebox).send_keys("admin")
        self.driver.execute_script("arguments[0].click();",
            self.driver.find_element(By.CSS_SELECTOR, ModifyButton))
        self.wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, toast), "成功"))
        assert self.driver.find_element(By.CSS_SELECTOR, NavNickName).text.strip() == "admin", "昵称未改回 admin"
        print("恢复后导航昵称:", self.driver.find_element(By.CSS_SELECTOR, NavNickName).text.strip())
        ForumDriver.getScreenshot()
    
    #辅助方法：个人中心资料修改（邮箱/手机号/个人简介都复用）
    def _changeUserInfo(self, box, ModifyButton, toast, inputNewValue):
        originalValue = self.driver.find_element(By.CSS_SELECTOR, box).get_attribute("value")# 记录原值，测完恢复
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, box)))
        self.driver.find_element(By.CSS_SELECTOR, box).clear()#清空输入框
        self.driver.find_element(By.CSS_SELECTOR, box).send_keys(inputNewValue)
        #清掉旧 toast 防串扰
        self.driver.execute_script("const t = document.querySelector('.jq-toast-wrap'); if (t) t.remove();")
        self.driver.execute_script("arguments[0].click();",
            self.driver.find_element(By.CSS_SELECTOR, ModifyButton))
        self.wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, toast), "成功"))# 等待提交成功提示
        #断言资料已修改：input/textarea 用 get_attribute("value") 取值
        actualValue = self.driver.find_element(By.CSS_SELECTOR, box).get_attribute("value")
        assert actualValue == inputNewValue, f"资料修改失败，期望 [{inputNewValue}]，实际 [{actualValue}]"
        print("修改后资料:", actualValue)
        #把资料改回原值，保证其他测试不受影响
        self.driver.find_element(By.CSS_SELECTOR, box).clear()
        self.driver.find_element(By.CSS_SELECTOR, box).send_keys(originalValue)
        self.driver.execute_script("const t = document.querySelector('.jq-toast-wrap'); if (t) t.remove();")
        self.driver.execute_script("arguments[0].click();",
            self.driver.find_element(By.CSS_SELECTOR, ModifyButton))
        self.wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, toast), "成功"))
        restoreValue = self.driver.find_element(By.CSS_SELECTOR, box).get_attribute("value")
        assert restoreValue == originalValue, f"资料未改回原值，期望 [{originalValue}]，实际 [{restoreValue}]"
        print("恢复后资料:", restoreValue)
        ForumDriver.getScreenshot()

    def UserInfoTest(self):
        # [BUG·uc-bad-email/uc-bad-phone] 邮箱/手机号均无格式校验：填 "abc"、5 位数字也能保存成功，
        # 期望的"表单内联错误提示且未保存"前提不成立，用例无法编写，已在任务清单标注 bug。
        self._changeUserInfo("#setting_input_email", "#setting_submit_email", ".jq-toast-single", "newEmail")#修改邮箱测试
        self._changeUserInfo("#setting_input_phoneNum", "#setting_submit_phoneNum", ".jq-toast-single", "newPhone")#修改手机号测试
        self._changeUserInfo("#settings_textarea_remark", "#settings_submit_remark", ".jq-toast-single", "newRemark")#修改个人介绍测试

    #填写三个密码框并提交，返回提交后的提示文本（成功场景提示可能瞬时消失，返回空串）
    def _submitPassword(self, oldPwd, newPwd, repeatPwd):
        oldBox = "#settings_input_oldPassword"#原密码输入框
        newBox = "#settings_input_newPassword"#新密码输入框
        repeatBox = "#settings_input_passwordRepeat"#确认密码输入框
        submit = "#settings_submit_password"#提交修改按钮
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, oldBox)))
        self.driver.find_element(By.CSS_SELECTOR, oldBox).clear()
        self.driver.find_element(By.CSS_SELECTOR, oldBox).send_keys(oldPwd)
        self.driver.find_element(By.CSS_SELECTOR, newBox).clear()
        self.driver.find_element(By.CSS_SELECTOR, newBox).send_keys(newPwd)
        self.driver.find_element(By.CSS_SELECTOR, repeatBox).clear()
        self.driver.find_element(By.CSS_SELECTOR, repeatBox).send_keys(repeatPwd)
        #清掉旧 toast，避免读到上一次提交的提示
        self.driver.execute_script("const t = document.querySelector('.jq-toast-wrap'); if (t) t.remove();")
        #按钮可能在视口外，用 JS click 避免被拦截
        self.driver.execute_script("arguments[0].click();",
            self.driver.find_element(By.CSS_SELECTOR, submit))
        try:#等待提交结果提示出现
            toastEl = WebDriverWait(self.driver, 3).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".jq-toast-single")))# 等待提交结果提示可见
            return toastEl.text# 返回提交结果提示文本
        except Exception:
            return ""# 返回空串

    #预期登录失败（用户名或密码错误弹窗）
    def _loginFail(self, username, password):
        self._login(username, password)
        toastText = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".jq-toast-single"))).text
        assert "用户名或密码错误" in toastText, f"期望登录失败，实际提示: [{toastText}]"
        print(f"旧密码 {password} 登录被拒:", toastText)

    #预期登录成功（跳转首页且导航昵称为当前用户）
    def _loginSuc(self, username, password):
        self._login(username, password)
        self.wait.until(EC.url_contains("index.html"))
        nickname = self.driver.find_element(By.CSS_SELECTOR, "#index_nav_nickname").text.strip()
        assert nickname == username, f"期望昵称 [{username}]，实际 [{nickname}]"
        print(f"新密码 {password} 登录成功，昵称: {nickname}")

    #修改密码测试：异常场景 + 正常修改 + 登录双向验证 + 恢复原密码
    def _changePassword(self):
        # 1. 两次新密码不一致
        toastText = self._submitPassword("123456", "a123456", "b123456")
        assert "两次输入的密码不相同" in toastText, f"期望提示两次密码不一致，实际: [{toastText}]"
        print("两次密码不一致提示:", toastText)
        ForumDriver.getScreenshot("pwdMismatch")
        # 2. 原密码错误
        toastText = self._submitPassword("1", "a123456", "a123456")
        assert "参数校验失败" in toastText, f"期望提示参数校验失败，实际: [{toastText}]"
        print("原密码错误提示:", toastText)
        ForumDriver.getScreenshot("oldPwdWrong")
        # [BUG·uc-pwd-bad-weak] 新密码无强度校验：纯数字/过短等弱密码可直接修改成功，
        # 期望的"密码太弱"提示不存在，用例无法编写，已在任务清单标注 bug。
        # 3. 正常修改为 a123456：修改成功后服务器强制退出并跳回登录页，跳转本身就是修改生效的证据
        self._submitPassword("123456", "a123456", "a123456")
        self.wait.until(EC.url_contains("sign-in.html"))
        print("密码修改成功，已跳回登录页")
        ForumDriver.getScreenshot("changed")
        # 4. 旧密码已失效
        self._loginFail("admin", "123456")
        ForumDriver.getScreenshot("oldPwdFail")
        # 5. 新密码登录成功
        self._loginSuc("admin", "a123456")
        ForumDriver.getScreenshot("newPwdSuc")
        # 6. 进用户中心把密码改回 123456
        self._enterMyPost()
        self._submitPassword("a123456", "123456", "123456")
        self.wait.until(EC.url_contains("sign-in.html"))
        ForumDriver.getScreenshot("restore")
        # 7. 确认 123456 可登录（恢复初始状态，保证其他用例不受影响）
        self._loginSuc("admin", "123456")
        print("密码已恢复为 123456")
        ForumDriver.getScreenshot("restored")

    # [BUG·uc-avatar] 头像上传功能未实现/失效：手动测试无论传什么文件，
    # 既无 toast 提示，导航头像也无变化，期望的"全站生效"不存在，用例无法编写，已搁置标注 bug。
    # 站内信全流程(uc-msg)已提取到 MessageTest.py 独立文件，依赖两账号切换不适合放本类。

if __name__ == '__main__':
    pc = PersonalCenter()
    pc.loginTest()#登录测试
    pc._enterMyPost()#进入个人中心
    pc._changeUser()#修改用户昵称测试
    pc.UserInfoTest()#修改邮箱测试
    pc._changePassword()#修改密码测试
    time.sleep(2)
    ForumDriver.driver.quit()

