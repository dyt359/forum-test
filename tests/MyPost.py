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

#我的帖子页（个人中心，index.html 的动态区域）
class MyPost:
    url = ""
    driver = ""
    def __init__(self):
        self.url = "http://127.0.0.1:58080/sign-in.html"
        self.driver = ForumDriver.driver# 获取浏览器驱动
        self.driver.get(self.url)# 打开登录页
        self.driver.maximize_window()# 最大化窗口
        self.wait = WebDriverWait(self.driver, 5)# 显式等待，等待时间为5秒

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

    #进入我的帖子页（点用户下拉 -> 我的帖子 -> 等列表加载）
    def _enterMyPost(self):
        UserInformation = "body > div.page > header.navbar.navbar-expand-md.navbar-light.d-print-none > div > div > div.nav-item.dropdown > a"#用户信息下拉
        self.driver.find_element(By.CSS_SELECTOR, UserInformation).click()#点击用户信息
        self.driver.find_element(By.CSS_SELECTOR, "#index_user_profile").click()#点击我的帖子
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#profile_article_body")))# 等待帖子列表加载

    #我的帖子页元素检查
    def myPostPageElementCheck(self):
        self._enterMyPost()
        #个人资料卡 + 帖子列表所有关键元素应可见
        elements = {
            "#profile_avatar": "用户头像",
            "#profile_nickname": "用户昵称",
            "#profile_articleCount": "帖子数量",
            "#profile_email": "用户邮箱",
            "#profile_createTime": "注册时间",
            "#profile_remark": "个人简介",
            "#profile_article_body": "帖子列表",
        }
        for selector, desc in elements.items():
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
        #昵称应为当前登录用户
        nickname = self.driver.find_element(By.CSS_SELECTOR, "#profile_nickname").text.strip()
        assert nickname == "admin", f"我的帖子页昵称 [{nickname}] 与当前登录用户 [admin] 不一致"
        print("我的帖子页昵称:", nickname)
        ForumDriver.getScreenshot()

    #帖子数量一致性测试：资料卡显示的帖子数 == 列表实际条数
    def postCountTest(self):
        self._enterMyPost()
        countText = self.driver.find_element(By.CSS_SELECTOR, "#profile_articleCount").text.strip()#资料卡帖子数
        items = self.driver.find_elements(By.CSS_SELECTOR, "#profile_article_body > li")#列表实际条数
        print(f"资料卡帖子数: {countText}, 列表实际条数: {len(items)}")
        assert str(len(items)) in countText, \
            f"帖子数不一致：资料卡显示 [{countText}]，列表实际 [{len(items)}] 条"
        ForumDriver.getScreenshot()

    #帖子列表内容检查：标题非空、时间格式正确、按时间降序排列
    def postListCheck(self):
        self._enterMyPost()
        titles = self.driver.find_elements(By.CSS_SELECTOR, "#profile_article_body .profile_article_list_a_title")#标题
        times = self.driver.find_elements(By.CSS_SELECTOR, "#profile_article_body .text-muted.mt-2 div.col > ul li.list-inline-item")#发布时间
        assert len(titles) > 0, "我的帖子列表为空"
        assert len(titles) == len(times), f"标题数 [{len(titles)}] 与时间数 [{len(times)}] 不一致"
        #每条标题非空
        for t in titles:
            assert t.text.strip() != "", "存在空标题的帖子"
        #时间格式正确
        time_texts = [t.text.strip() for t in times]
        times_parsed = [datetime.strptime(t, "%Y-%m-%d %H:%M:%S") for t in time_texts]
        #按时间降序排列（最新的在前）
        assert times_parsed == sorted(times_parsed, reverse=True), \
            f"我的帖子未按时间降序排列：{time_texts}"
        print("时间列表:", time_texts)
        #回复数检查(mine-list-reply)：每条帖子行的第3个 li（浏览/点赞/回复三项之末）应为纯数字
        rows = self.driver.find_elements(By.CSS_SELECTOR, "#profile_article_body > li")#帖子行
        for row in rows:
            reply = row.find_element(By.CSS_SELECTOR, "li:nth-child(3)").text.strip()#回复数
            assert reply.isdigit(), f"回复数格式异常: [{reply}]"
        print(f"{len(rows)} 条帖子的回复数均通过格式校验")
        ForumDriver.getScreenshot()

    #点击帖子标题进入帖子详情页
    def enterPostTest(self):
        self._enterMyPost()
        firstTitle = self.driver.find_element(By.CSS_SELECTOR, "#profile_article_body > li:nth-child(1) .profile_article_list_a_title")#第一条帖子标题
        titleText = firstTitle.text.strip()#列表页标题文本
        firstTitle.click()#点击标题进入详情页
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#details_article_title")))# 等待详情页标题可见
        detailTitle = self.driver.find_element(By.CSS_SELECTOR, "#details_article_title").text.strip()#详情页标题文本
        assert detailTitle == titleText, \
            f"详情页标题 [{detailTitle}] 与列表页标题 [{titleText}] 不一致"
        print("详情页标题:", detailTitle)
        ForumDriver.getScreenshot()

    #空列表状态提示(mine-empty)：用没发过帖子的 test01 账号验证"还没有帖子"提示(依赖注册测试已创建 test01)
    def emptyListTest(self):
        self.driver.get("http://127.0.0.1:58080/sign-in.html")#回登录页切换账号
        self._login("test01", "test@123")
        self.wait.until(EC.url_contains("index.html"))#等待登录成功
        self._enterMyPost()
        bodyText = self.driver.find_element(By.CSS_SELECTOR, "#profile_article_body").text.strip()#空列表提示文本
        assert bodyText == "还没有帖子", f"期望空列表提示 [还没有帖子]，实际 [{bodyText}]"
        count = self.driver.find_element(By.CSS_SELECTOR, "#profile_articleCount").text.strip()#资料卡帖子数
        assert count == "0", f"空账号帖子数应为 0，实际 [{count}]"
        print("空列表提示:", bodyText, "，帖子数:", count)
        ForumDriver.getScreenshot()

if __name__ == "__main__":
    myPost = MyPost()
    myPost.loginTest()# 登录测试账号
    myPost.myPostPageElementCheck()# 我的帖子页元素检查
    myPost.postCountTest()# 帖子数量一致性测试
    myPost.postListCheck()# 帖子列表内容检查(含回复数)
    myPost.enterPostTest()# 点击帖子标题进入详情页
    myPost.emptyListTest()# 空列表状态提示(切换 test01)

    time.sleep(2)
    ForumDriver.driver.quit()
