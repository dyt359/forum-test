import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
from datetime import datetime

from selenium.webdriver.common.by import By# 导入By类，用于定位元素
from selenium.webdriver.support.wait import WebDriverWait# 显式等待
from selenium.webdriver.support import expected_conditions as EC# 导入预期条件类，用于等待元素出现
from common.Utils import ForumDriver, cleanToastText# 导入ForumDriver类(浏览器)与toast文案清洗函数

# 帖子详情页
class PostDetailsPage:
    url = ""
    driver = ""
    def __init__(self):
        self.url = "http://127.0.0.1:58080/sign-in.html"
        self.driver = ForumDriver.driver
        self.driver.get(self.url)
        self.driver.maximize_window ()# 最大化窗口
        self.wait = WebDriverWait(self.driver, 5)

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
    
    #板块切换函数
    def PlateSwitching(self , i , name):
        self.driver.find_element ( By.CSS_SELECTOR , f"#topBoardList > li:nth-child({i})" ).click ()
        # 等待标题文本真正变成预期的 name
        self.wait.until (
            EC.text_to_be_present_in_element (
                (By.CSS_SELECTOR , "#article_list_board_title") , name
            ))
        text = self.driver.find_element ( By.CSS_SELECTOR , "#article_list_board_title" ).text.strip ()
        #print ( i + " " + name )
        #print ( f"预期值: [{name}], 实际值: [{text}]" )
        assert text == name
        ForumDriver.getScreenshot ()

    def postTest(self):# 进入帖子详情页
        homePostTitle ="#artical-items-body > div:nth-child(1) > div"#首页帖子标题
        postLink ="#artical-items-body > div:nth-child(1) > div > div.col > div.text-truncate > a"#帖子链接
        postTitle ="#details_article_title"#帖子标题
        homeVisit = self.driver.find_element(By.CSS_SELECTOR, "#artical-items-body > div:nth-child(1) > div > div.col > div.text-muted.mt-2 > div > div.col-auto > ul > li.list-inline-item:nth-child(1)").text.strip()#首页首帖浏览数(统计三项之首)
        text = self.driver.find_element(By.CSS_SELECTOR, postLink).text# 获取帖子链接文本
        ForumDriver.getScreenshot("home")# 首页首帖截图(进入详情页前)
        self.driver.find_element(By.CSS_SELECTOR, postLink).click()
        toast = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, postTitle)))
        assert toast.text == text# 断言帖子标题与首页帖子标题一致
        visitCount = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#details_article_visitCount"))).text.strip()#详情页浏览数
        assert int(visitCount) == int(homeVisit) + 1, \
            f"浏览数未+1: 首页[{homeVisit}] 详情页[{visitCount}]"
        print(f"浏览数: 首页[{homeVisit}] -> 详情页[{visitCount}]")
        ForumDriver.getScreenshot("detail")

    # 帖子详情页元素检查
    def postDetailsPageElementCheck(self):# 检查帖子详情页元素
        postTitle ="#details_article_title"#帖子标题
        postContent ="#details_article_content"#帖子内容
        postTime ="#details_article_createTime"#帖子创建时间
        postViews ="#details_article_visitCount"#帖子访问数
        postLikes ="#details_article_likeCount"#帖子点赞数
        postComments ="#details_article_replyCount"#帖子评论数
        postAuthor ="#article_details_author_name"#帖子作者用户名

        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, postTitle)))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, postContent)))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, postTime)))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, postViews)))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, postLikes)))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, postAuthor)))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, postComments)))

        ForumDriver.getScreenshot()

    #辅助回复帖子
    def replyPostAuxiliary(self,ReplyContent,ReplySuccessMsg,checkCountInc=False,label=None):#辅助回复帖子（
        # CodeMirror 是富文本编辑器，对内部 pre 元素 send_keys 会抛 ElementNotInteractable
        # 这里只定位到 CodeMirror 根容器，用它的 JS API 设值
        replyEditor = "#article_details_reply > div.CodeMirror"#回复内容编辑器
        replySubmit = "#details_btn_article_reply"#回复提交按钮
        toast = "body > div.jq-toast-wrap.bottom-right"#右下角所有提示框
        replyCount = "#details_article_replyCount"#回复数

        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, replyEditor)))# 等待回复内容编辑器可见
        beforeCount = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, replyCount))).text.strip()#回复前计数

        # 用 CodeMirror 的 API 设值——CodeMirror 不是普通 textarea，不能 send_keys
        self.driver.execute_script(
            "const cm = document.querySelector(arguments[0]);"
            "if (cm && cm.CodeMirror) { cm.CodeMirror.setValue(arguments[1]); }"
            "else { throw new Error('CodeMirror instance not found'); }",
            replyEditor, ReplyContent
        )
        time.sleep(0.5)
        # 按钮在页面底部（y≈6642），scrollIntoView 后几何点击仍被拦截，改用 JS click 绕过
        btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, replySubmit)))
        self.driver.execute_script("arguments[0].click();", btn)
        toast_locator = (By.CSS_SELECTOR, toast)
        # 等待包含期望文案的toast出现: 容器一旦显示过就持续可见, 用visibility会立刻返回上一条残留toast,
        # 改用 text_to_be_present_in_element, 残留toast不匹配时会一直等到新toast出现
        self.wait.until(EC.text_to_be_present_in_element(toast_locator, ReplySuccessMsg))
        toast_el = self.driver.find_element(*toast_locator)
        print("弹窗提示:", cleanToastText(toast_el.text))
        assert ReplySuccessMsg in toast_el.text# 断言回复提交成功（toast 含 ×/提示，用子串匹配）
        if checkCountInc:
            # SPA 导航可能变排序/板块, 直接在当前视图等回复数 DOM 从 beforeCount 变成 beforeCount+1 即可
            expectedCount = str(int(beforeCount) + 1)
            self.wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, replyCount), expectedCount))
            afterCount = self.driver.find_element(By.CSS_SELECTOR, replyCount).text.strip()
            assert int(afterCount) == int(beforeCount) + 1, \
                f"回复数未+1: 回复前[{beforeCount}] 回复后[{afterCount}]"
            print(f"回复数: {beforeCount} -> {afterCount}")
        ForumDriver.getScreenshot(label)


    #回复帖子
    def replyPost(self):#回复帖子
        time.sleep(2)
        self.replyPostAuxiliary("这是一条回复","回复成功",True,"success")
        time.sleep(2.5)
        self.replyPostAuxiliary("","请输入回复内容",label="empty")
        time.sleep(3)# 等待上一条提示淡出, 避免断言读到旧toast
        # 超长内容: 后端未做长度校验, 超长内容直接撞MySQL, 把MyBatis异常泄漏到toast
        self.replyPostAuxiliary("a" * 10000, "Data too long for column", label="toolong")

    #检查回复内容是否按时间排序
    def checkReplyTime(self):#检查回复内容是否按时间排序
        # 通用选择器：匹配所有回复的时间元素（格式 2026-08-26 03:43:03）
        replyTimeAll = "#details_reply_area > div > div.col-9.card.card-lg > div.card-footer.bg-transparent.mt-auto > div > div > ul > li"
        # 先等至少一条评论的时间出现
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, replyTimeAll)))
        # 抓取所有回复时间文本
        elements = self.driver.find_elements(By.CSS_SELECTOR, replyTimeAll)
        time_texts = [el.text for el in elements]
        #print("页面回复时间（自上而下）：", time_texts)
        # 解析为 datetime 对象
        times = [datetime.strptime(t, "%Y-%m-%d %H:%M:%S") for t in time_texts]
        # 断言：越早发布越在下边 → 自上而下应为降序（最新的在前）
        assert times == sorted(times, reverse=True), f"回复未按时间降序排列：{time_texts}"

    #点赞帖子
    def likePost(self):#点赞帖子
        likeBtn = "#details_btn_like_count"#点赞按钮
        toast = ".jq-toast-single"#点赞成功提示
        likes="#details_article_likeCount"#点赞数
        likeCount = self.driver.find_element(By.CSS_SELECTOR, likes).text

        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, likeBtn)))# 等待点赞按钮可见
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            self.driver.find_element(By.CSS_SELECTOR, likeBtn)
        )# 滚动点赞按钮进视口
        time.sleep(1)# 等待滚动动画结束
        self.driver.execute_script(
            "const likeBtn = document.querySelector(arguments[0]);"
            "if (likeBtn) { likeBtn.click(); }"
            "else { throw new Error('点赞按钮 not found'); }",
            likeBtn
        )# 点赞点赞按钮

        toast = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, toast)))# 断言点赞成功
        assert "点赞成功" in toast.text# 断言点赞成功（toast 含 ×/提示，用子串匹配）
        likeCount1 = self.driver.find_element(By.CSS_SELECTOR, likes).text
        assert int(likeCount1) == int(likeCount) + 1, "点赞数未增加1" # 断言点赞数增加1
        # 连点2次触发重复点赞bug, 让右下角堆叠多个"点赞成功"toast
        for _ in range(2):
            self.driver.execute_script(
                "const likeBtn = document.querySelector(arguments[0]);"
                "if (likeBtn) { likeBtn.click(); }",
                likeBtn
            )
            time.sleep(0.5)
        likeCount2 = self.driver.find_element(By.CSS_SELECTOR, likes).text
        print(f"点赞数: 首次[{likeCount1}] 重复点击后[{likeCount2}]")
        ForumDriver.getScreenshot()
        time.sleep(2)
        
    #检查权限控制（他人帖子不可见编辑按钮，他人帖子不可见删除按钮）
    def checkPermission(self):#检查权限控制
        url = "http://127.0.0.1:58080/index.html"
        name = "#index_nav_nickname"
        n = 1
        self.driver.get(url)
        # 找到非本人发布的帖子（用于权限校验：本人帖子可见编辑按钮，他人帖子不应可见）
        while True:
            AuthorUserName = "#artical-items-body > div:nth-child("+str(n)+") > div > div.col > div.text-muted.mt-2 > div > div.col > ul > li:nth-child(1)"
            EnterPost = "#artical-items-body > div:nth-child("+str(n)+") > div > div.col > div.text-truncate > a"
            nameText = self.driver.find_element(By.CSS_SELECTOR, name).text
            AuthorUserNameText = self.driver.find_element(By.CSS_SELECTOR, AuthorUserName).text
            if nameText == AuthorUserNameText:
                n += 1
            else:
                break
        replyTimeAll = "#bit-forum-content > div.page-body > div > div > div:nth-child(1) > div.col-9.card.card-lg > div.card-footer.bg-transparent.mt-auto.justify-content-end > div > div:nth-child(2)"#编辑按钮
        DeleteBtn = "#bit-forum-content > div.page-body > div > div > div:nth-child(1) > div.col-9.card.card-lg > div.card-footer.bg-transparent.mt-auto.justify-content-end > div > div:nth-child(3)"#删除按钮
        # 元素可能被固定定位元素遮挡或不在视口, 用 JS click 绕过 ElementClickInterceptedException
        enter_el = self.driver.find_element(By.CSS_SELECTOR, EnterPost)
        self.driver.execute_script("arguments[0].click();", enter_el)
        time.sleep(1)
        #检查编辑按钮是否可见（权限校验：他人帖子不应显示编辑按钮）
        assert self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, replyTimeAll))), "编辑按钮可见，权限控制失效"
        #检查删除按钮是否可见（权限校验：他人帖子不应显示删除按钮）
        assert self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, DeleteBtn))), "删除按钮可见，权限控制失效"
        ForumDriver.getScreenshot()

    #检查权限控制（本人帖子：编辑/删除按钮应可见）
    def checkOwnPostPermission(self):#检查权限控制（本人帖子）
        url = "http://127.0.0.1:58080/index.html"
        name = "#index_nav_nickname"
        n = 1
        self.driver.get(url)
        # 找到本人发布的帖子（用于权限校验：本人帖子应可见编辑/删除按钮）
        while True:
            AuthorUserName = "#artical-items-body > div:nth-child("+str(n)+") > div > div.col > div.text-muted.mt-2 > div > div.col > ul > li:nth-child(1)"
            EnterPost = "#artical-items-body > div:nth-child("+str(n)+") > div > div.col > div.text-truncate > a"
            nameText = self.driver.find_element(By.CSS_SELECTOR, name).text
            AuthorUserNameText = self.driver.find_element(By.CSS_SELECTOR, AuthorUserName).text
            if nameText == AuthorUserNameText:
                break
            else:
                n += 1
        replyTimeAll = "#bit-forum-content > div.page-body > div > div > div:nth-child(1) > div.col-9.card.card-lg > div.card-footer.bg-transparent.mt-auto.justify-content-end > div > div:nth-child(2)"#编辑按钮
        DeleteBtn = "#bit-forum-content > div.page-body > div > div > div:nth-child(1) > div.col-9.card.card-lg > div.card-footer.bg-transparent.mt-auto.justify-content-end > div > div:nth-child(3)"#删除按钮

        self.driver.find_element(By.CSS_SELECTOR, EnterPost).click()
        time.sleep(1)
        #检查编辑按钮是否可见（权限校验：本人帖子应显示编辑按钮）
        assert self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, replyTimeAll))), "编辑按钮不可见，权限控制失效"
        #检查删除按钮是否可见（权限校验：本人帖子应显示删除按钮）
        assert self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, DeleteBtn))), "删除按钮不可见，权限控制失效"
        ForumDriver.getScreenshot()
    
    #检查编辑按钮跳转后是否加载原文
    def checkEditPost(self):#检查编辑按钮跳转后是否加载原文
        # 详情页选择器(读原文)
        detail_title = "#details_article_title"
        detail_content = "#details_article_content"
        # 编辑按钮真实id(应用把 article 拼成了 artile)
        edit_btn = "#details_artile_edit"
        # 编辑页选择器(标题输入框 + Markdown 预览区)
        edit_title = "#edit_article_title"

        # 1. 详情页抓原文
        detail = {
            "title": self.driver.find_element(By.CSS_SELECTOR, detail_title).text,
            "content": self.driver.find_element(By.CSS_SELECTOR, detail_content).text
        }
        print("详情页原文:", detail)

        # 2. 点编辑按钮, 编辑表单以模态形式出现在当前页(URL不变)
        self.driver.find_element(By.CSS_SELECTOR, edit_btn).click()
        # 等待编辑页标题输入框可见
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, edit_title)))

        # 3. 编辑页抓加载的原文: 标题用 input.value, 内容用 Markdown 预览区文本(与详情页同一层级渲染)
        edit_page = {
            "title": self.driver.find_element(By.CSS_SELECTOR, edit_title).get_attribute("value"),
            "content": self.driver.find_element(By.CSS_SELECTOR, "#edit_article_content_area > div.editormd-preview > div").text
        }
        print("编辑页加载:", edit_page)

        # 4. 断言编辑页加载的标题/内容与详情页一致(strip 去除首尾空白)
        assert edit_page["title"].strip() == detail["title"].strip(), \
            f"标题不一致: 详情={detail['title']!r}, 编辑={edit_page['title']!r}"
        assert edit_page["content"].strip() == detail["content"].strip(), \
            f"内容不一致: 详情={detail['content']!r}, 编辑={edit_page['content']!r}"
        ForumDriver.getScreenshot()

    



if __name__ == "__main__":
    postDetailsPage = PostDetailsPage()
    postDetailsPage.loginTest()# 登录测试
    postDetailsPage.postTest()# 帖子测试
    postDetailsPage.postDetailsPageElementCheck()# 帖子详情页元素检查
    postDetailsPage.likePost()# 点赞帖子
    postDetailsPage.replyPost()# 回复帖子
    postDetailsPage.checkReplyTime()# 检查回复内容是否按时间排序
    postDetailsPage.checkPermission()# 检查权限控制
    postDetailsPage.checkOwnPostPermission()# 检查权限控制（本人帖子：编辑/删除按钮应可见）
    postDetailsPage.checkEditPost()# 检查编辑按钮跳转后是否加载原文
    

    time.sleep(2)
    postDetailsPage.driver.quit()
