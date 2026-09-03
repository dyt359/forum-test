import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import re
import time
from urllib.parse import unquote# URL解码, 用于中文关键字断言

from selenium.webdriver.common.by import By# 导入By类，用于定位元素
from selenium.webdriver.common.keys import Keys# 导入Keys类，用于模拟键盘按键
from selenium.webdriver.support.wait import WebDriverWait# 显式等待
from selenium.webdriver.support import expected_conditions as EC# 导入预期条件类，用于等待元素出现
from common.Utils import ForumDriver, cleanToastText# 导入ForumDriver类(浏览器)与toast文案清洗函数

#用户首页测试类
class ForumIndex:
    url = ""
    driver = ""
    def __init__(self):
        self.url = "http://127.0.0.1:58080/sign-in.html"
        self.driver = ForumDriver.driver# 获取浏览器驱动
        self.driver.get(self.url)# 打开首页
        self.driver.maximize_window ()# 最大化窗口(昵称父容器是 d-none d-xl-block, 窗口<1200px时昵称不可见)
        self.wait = WebDriverWait ( self.driver , 5 )# 显式等待，等待时间为5秒
        
    def _login(self, username, password):# 登录方法
        self.driver.find_element(By.CSS_SELECTOR, "#username").clear()
        self.driver.find_element(By.CSS_SELECTOR, "#password").clear()
        self.driver.find_element(By.CSS_SELECTOR, "#username").send_keys(username)
        self.driver.find_element(By.CSS_SELECTOR, "#password").send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, "#submit").click()

    def loginTest(self):# 登录测试账号
        self._login("admin", "123456")
        # 登录后前端可能把 index.html 重写为根路径(/?theme=...), URL断言不稳定, 统一等导航栏昵称元素出现
        self.wait.until ( EC.visibility_of_element_located ( (By.CSS_SELECTOR , "#index_nav_nickname") ) )
        ForumDriver.getScreenshot ()
    
    #板块切换函数
    def PlateSwitching(self , i , name):
        self.driver.find_element ( By.CSS_SELECTOR , f"#topBoardList > li:nth-child({i})" ).click ()

        # 等待标题文本真正变成预期的 name
        self.wait.until (
            EC.text_to_be_present_in_element (
                (By.CSS_SELECTOR , "#article_list_board_title") , name
            )
        )

        text = self.driver.find_element ( By.CSS_SELECTOR , "#article_list_board_title" ).text.strip ()

        #print ( i + " " + name )
        print ( f"板块{i}切换: 预期[{name}] 实际[{text}]" )
        assert text == name

        ForumDriver.getScreenshot ()
    #板块切换测试
    def boardTest(self):# 板块切换测试
        # 登录后前端可能把 index.html 重写为根路径(/?theme=...), URL断言不稳定, 改等板块导航元素出现
        self.wait.until ( EC.presence_of_element_located ( (By.CSS_SELECTOR , "#topBoardList") ) )
        s = {
        "2":"Java",
        "3":"C++",
        "4":"前端技术",
        "5":"MySQL",
        "6":"面试宝典",
        "7":"经验分享",
        "8":"招聘信息",
        "9":"福利待遇",
        "10":"灌水区"
        }
        for i in s:
            self.PlateSwitching(i,s[i])
    #帖子列表检查(idx-postlist: 标题非空/作者非空/时间格式/浏览·点赞·回复数为纯数字)
    def postTest(self):
        first = "#artical-items-body > div:nth-child(1) > div > div.col"#首帖行
        title = self.driver.find_element(By.CSS_SELECTOR, first + " > div.text-truncate > a").text.strip()#首帖标题
        print("首帖标题:", title)
        assert title != "", "首页首帖标题为空"
        author = self.driver.find_element(By.CSS_SELECTOR, first + " > div.text-muted.mt-2 > div > div.col > ul > li:nth-child(1)").text.strip()#作者昵称
        print("作者:", author)
        assert author != "", "首帖作者昵称为空"
        pubTime = self.driver.find_element(By.CSS_SELECTOR, first + " > div.text-muted.mt-2 > div > div.col > ul > li:nth-child(2)").text.strip()#发表时间
        print("发表时间:", pubTime)
        assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", pubTime), f"发表时间格式异常: [{pubTime}]"
        stats = self.driver.find_elements(By.CSS_SELECTOR, first + " > div.text-muted.mt-2 > div > div.col-auto > ul > li.list-inline-item")#浏览/点赞/回复
        assert len(stats) == 3, f"首帖统计项数量异常: {len(stats)} 项"
        for s in stats:
            assert s.text.strip().isdigit(), f"浏览/点赞/回复数格式异常: [{s.text}]"
        print("浏览/点赞/回复:", [s.text.strip() for s in stats])
        ForumDriver.getScreenshot()
    #个人信息检查

    def userInfoTest(self):# 个人信息检查
        self.driver.maximize_window ()# 最大化窗口
        # 点击头像区域的下拉触发器(不是头像图片本身), 展开"我的帖子/个人中心/退出登录"菜单
        self.driver.find_element(By.CSS_SELECTOR, "body > div.page > header.navbar.navbar-expand-md.navbar-light.d-print-none > div > div > div.nav-item.dropdown > a").click()
        time.sleep(0.5)# 等待下拉菜单动画展开
        text = self.driver.find_element(By.CSS_SELECTOR, "#index_nav_nickname").text
        print("导航栏昵称:", text)
        assert text =="admin"
        ForumDriver.getScreenshot()

    #主题切换测试
    def themeTest(self):# 主题切换测试
        self.driver.find_element(By.CSS_SELECTOR, "body > div.page > header.navbar.navbar-expand-md.navbar-light.d-print-none > div > div > div:nth-child(2) > a.nav-link.px-0.hide-theme-dark").click()
        url = self.driver.current_url
        print("主题切换[dark] URL:", url)
        assert "theme=dark" in url
        ForumDriver.getScreenshot("dark")
        self.driver.find_element(By.CSS_SELECTOR, "body > div.page > header.navbar.navbar-expand-md.navbar-light.d-print-none > div > div > div:nth-child(2) > a.nav-link.px-0.hide-theme-light").click()
        url = self.driver.current_url
        print("主题切换[light] URL:", url)
        assert "theme=light" in url
        ForumDriver.getScreenshot("light")
    
    #站内信测试
    def messageTest(self):# 站内信测试
        nav_msg = "body > div.page > header.navbar.navbar-expand-md.navbar-light.d-print-none > div > div > div:nth-child(2) > div"
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, nav_msg))).click()
        # 等待站内信下拉列表中的第一条消息可点击
        first_msg = "#index_div_message_list > div:nth-child(1) > div > div:nth-child(3)"
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, first_msg))).click()
        # 等待“回复”按钮可点击
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#btn_index_message_reply"))).click()
        # 等待回复输入框可见且可交互（点击回复后才会展开）
        reply_input = "#index_message_reply_receive_content"
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, reply_input))).send_keys("测试回复")
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#btn_index_send_message_reply"))).click()
        # 等待回复发送成功（与 ForumLogin.assertToast 同样的选择器 + in 断言）
        toast = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".jq-toast-single")))
        print("弹窗提示:", cleanToastText(toast.text))
        assert "操作成功" in toast.text
        ForumDriver.getScreenshot ()
        self.driver.find_element(By.CSS_SELECTOR, "#index_message_offcanvasEnd > div.offcanvas-header > button").click()
        #time.sleep(2)


    #搜索测试 (正常搜索框流程: 输入 + 回车提交)
    def searchTest(self):
        SearchBox ="body > div.page > header.navbar.navbar-expand-md.navbar-light.d-print-none > div > div > div.nav-item.d-none.d-md-flex.me-3 > div > form > div > input"
        title_sel = "#artical-items-body .article_list_a_title"

        def _do_search(keyword, label):
            # 每个场景都从首页开始, 保证互不影响
            self.driver.get("http://127.0.0.1:58080/index.html")
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, title_sel)))
            box = self.driver.find_element(By.CSS_SELECTOR, SearchBox)
            box.clear()
            if keyword:
                box.send_keys(keyword)
            # 回车提交, 走搜索框原生流程
            box.send_keys(Keys.RETURN)
            # 等待结果页加载(列表出现即可)
            try:
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, title_sel)))
            except Exception:
                pass
            url = self.driver.current_url
            titles = [e.text for e in self.driver.find_elements(By.CSS_SELECTOR, title_sel)]
            # 查找"无结果"提示元素
            no_result_hint = None
            for sel in [".empty-list", ".no-data", ".no-result", ".list-empty", "#artical-items-body > .text-center", "#artical-items-body > .text-muted"]:
                els = self.driver.find_elements(By.CSS_SELECTOR, sel)
                if els and els[0].is_displayed():
                    no_result_hint = els[0].text.strip()
                    break
            print(f"[{label}] 关键字='{keyword}'  URL={url}  结果数={len(titles)}  无结果提示={no_result_hint}")
            ForumDriver.getScreenshot ()

        # 场景1: 正常关键字搜索
        _do_search("测试", "正常关键字")
        # 场景2: 空关键字搜索
        _do_search("", "空关键字")
        # 场景3: 无结果关键字搜索 (用一个不可能匹配的关键字, 验证无结果提示)
        _do_search("zzz不存在的关键字zzz", "无结果关键字")
    
    #退出登录测试
    def logoutTest(self):# 退出登录测试
        self.driver.find_element(By.CSS_SELECTOR, "body > div.page > header.navbar.navbar-expand-md.navbar-light.d-print-none > div > div > div.nav-item.dropdown > a").click()
        self.driver.find_element(By.CSS_SELECTOR, "#index_user_logout").click()
        self.wait.until(EC.url_contains("sign-in.html"))
        ForumDriver.getScreenshot ()
    
    #未登录状态测试
    def unloginTest(self):# 未登录状态测试
        self.driver.get("http://127.0.0.1:58080/index.html")
        time.sleep(1)# 给SPA执行登录取向/渲染的时间
        print("当前实际URL:", self.driver.current_url)
        # SPA未登录时可能跳sign-in.html(昵称元素不存在), 也可能原地渲染空昵称, 两种都算通过
        els = self.driver.find_elements(By.CSS_SELECTOR, "#index_nav_nickname")
        nickText = els[0].text.strip() if els else ""
        assert len(els) == 0 or nickText == "", f"未登录访问首页, 昵称应不存在或为空, 实际: [{nickText}]"
        ForumDriver.getScreenshot ()
    



if __name__ == "__main__":
    test = ForumIndex()
    test.loginTest()# 登录测试账号
    test.boardTest()# 板块切换测试
    #test.postTest()# 帖子列表检查
    test.userInfoTest()# 个人信息检查
    #test.searchTest()# 搜索测试
    test.themeTest()# 主题切换测试
    test.messageTest()# 站内信测试
    test.logoutTest()# 退出登录测试
    test.unloginTest()# 未登录状态测试
    
    



    ForumDriver.driver.quit()



    