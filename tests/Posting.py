#发帖测试

import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
from datetime import datetime

from selenium.webdriver.common.by import By# 导入By类，用于定位元素
from selenium.webdriver.support.wait import WebDriverWait# 显式等待
from selenium.webdriver.support import expected_conditions as EC# 导入预期条件类，用于等待元素出现
from selenium.webdriver.support.ui import Select# 导入Select类，用于操作下拉框
from common.Utils import ForumDriver# 导入ForumDriver类，用于操作浏览器
from tests import ForumLogin# 导入ForumLogin类，用于登录

class Posting:
    url = ""
    driver = ""
    def __init__(self):
        self.url = "http://127.0.0.1:58080/sign-in.html"
        self.driver = ForumDriver.driver# 获取浏览器驱动
        self.driver.get(self.url)# 打开登录页
        self.wait = WebDriverWait ( self.driver , 5 )# 显式等待，等待时间为5秒
        self.login = ForumLogin.ForumLogin()# 实例化ForumLogin类
        self.login._login("admin", "123456")# 登录
        self.driver.maximize_window ()# 最大化窗口
    

    #辅助发帖方法
    def _post(self, plate, title, content,expected_result):
        self.url = "http://127.0.0.1:58080/index.html"
        self.driver.get(self.url)
        PostingButton = "#bit-forum-content > div.page-header.d-print-none > div > div > div.col-auto.ms-auto.d-print-none > div"# 发帖按钮
        self.driver.find_element(By.CSS_SELECTOR, PostingButton).click()#进入发帖页面
        toast = "body > div.jq-toast-wrap.bottom-right"# toast 提示框
        # 选择板块（plate 传 option 的 value，如 "1"=JAVA）
        board = Select(self.driver.find_element(By.CSS_SELECTOR, "#article_post_borad"))
        board.select_by_value(str(plate))
        # 输入标题
        self.driver.find_element(By.CSS_SELECTOR, "#article_post_title").send_keys(title)
        # 输入内容（CodeMirror 编辑器不能用 send_keys，使用其 JS API 写入）
        self.driver.execute_script(
            "document.querySelector('#edit-article .CodeMirror').CodeMirror.setValue(arguments[0]);",
            content
        )
        time.sleep(1)
        # 点击发帖（按钮可能不在视口内或被遮挡，用 JS click 绕过）
        submit = self.driver.find_element(By.CSS_SELECTOR, "#article_post_submit")
        self.driver.execute_script("arguments[0].click();", submit)
        # 检查预期结果是否包含在 toast 中
        self.wait.until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, toast), expected_result))
        toast_text = self.driver.find_element(By.CSS_SELECTOR, toast).text
        assert expected_result in toast_text, \
            f"预期结果 '{expected_result}' 不在 toast 中"

    def postTest(self):
        # 发帖测试(标题加时间戳避免历史残留同名导致删除断言误报)
        self._post("1", "测试标题-" + datetime.now().strftime("%H%M%S"), "测试内容","发帖成功")
        ForumDriver.getScreenshot("success")
        # 发帖失败测试
        self._post("1", "", "测试内容","请输入帖子标题")
        ForumDriver.getScreenshot("noTitle")
        self._post("1", "测试标题", "","请输入帖子内容")
        ForumDriver.getScreenshot("noContent")
        self._post("1", "", "","请输入帖子标题")
        ForumDriver.getScreenshot("bothEmpty")

    #删除帖子测试
    def deletePostTest(self):
        toast = "body > div.jq-toast-wrap.bottom-right"# toast 提示框
        UserInformation = "body > div.page > header.navbar.navbar-expand-md.navbar-light.d-print-none > div > div > div.nav-item.dropdown > a"#用户信息下拉
        # 回首页
        self.driver.get("http://127.0.0.1:58080/index.html")
        #点击我的帖子
        self.driver.find_element(By.CSS_SELECTOR, UserInformation).click()#点击用户信息
        self.driver.find_element(By.CSS_SELECTOR, "#index_user_profile").click()#点击我的帖子
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#profile_article_body")))# 等待帖子列表加载
        firstTitle = self.driver.find_element(By.CSS_SELECTOR, "#profile_article_body > li:nth-child(1) .profile_article_list_a_title")#第一条帖子标题
        titleText = firstTitle.text.strip()#列表页标题文本
        nBefore = len(self.driver.find_elements(By.CSS_SELECTOR, "#profile_article_body > li"))#删除前列表实际条数(计数文本不刷新, 用列表项为准)
        firstTitle.click()#点击标题进入详情页
        #点击删除按钮
        DeleteBtn = "#bit-forum-content > div.page-body > div > div > div:nth-child(1) > div.col-9.card.card-lg > div.card-footer.bg-transparent.mt-auto.justify-content-end > div > div:nth-child(3)"#删除按钮
        self.driver.find_element(By.CSS_SELECTOR, DeleteBtn).click()#点击删除按钮
        DeleteBtnConfirm = "#details_artile_delete"# 删除确认按钮
        self.driver.find_element(By.CSS_SELECTOR, DeleteBtnConfirm).click()#点击删除确认按钮
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, toast)))# 等待删除成功提示加载
        assert "删除成功" in self.driver.find_element(By.CSS_SELECTOR, toast).text, \
            f"预期结果 '删除成功' 不在 toast 中"
        ForumDriver.getScreenshot("confirm")
        # 回我的帖子列表验证删除生效: 帖子消失 + 列表条数-1
        self.driver.get("http://127.0.0.1:58080/index.html")
        self.driver.find_element(By.CSS_SELECTOR, UserInformation).click()#点击用户信息
        self.driver.find_element(By.CSS_SELECTOR, "#index_user_profile").click()#点击我的帖子
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#profile_article_body")))# 等待列表刷新
        nAfter = len(self.driver.find_elements(By.CSS_SELECTOR, "#profile_article_body > li"))#删除后列表实际条数
        assert nAfter == nBefore - 1, f"删除后列表条数未-1: 删除前[{nBefore}] 删除后[{nAfter}]"
        titles = [e.text.strip() for e in self.driver.find_elements(By.CSS_SELECTOR, "#profile_article_body .profile_article_list_a_title")]#剩余标题
        assert titleText not in titles, f"删除的帖子[{titleText}]仍在列表中"
        print(f"删除后列表刷新: 条数 {nBefore}->{nAfter}, [{titleText}] 已不在列表")
        ForumDriver.getScreenshot()
        

    # 编辑帖子测试
    def editPostTest(self):
        
        self.driver.get("http://127.0.0.1:58080/index.html")  # 回首页
        name = "#index_nav_nickname" 
        n = 1
        
        # 找到本人发布的帖子（用于权限校验：本人帖子应可见编辑/删除按钮）
        while True:
            AuthorUserName = "#artical-items-body > div:nth-child("+str(n)+") > div > div.col > div.text-muted.mt-2 > div > div.col > ul > li:nth-child(1)"
            EnterPost = "#artical-items-body > div:nth-child("+str(n)+") > div > div.col > div.text-truncate > a"
            nameText = self.driver.find_element(By.CSS_SELECTOR, name).text.strip()#获取当前昵称
            AuthorUserNameText = self.driver.find_element(By.CSS_SELECTOR, AuthorUserName).text.strip()#获取帖子作者昵称

            if nameText == AuthorUserNameText:#如果当前昵称与帖子作者昵称相同，说明是本人帖子
                break
            else:
                n += 1
        editBtn = "#details_artile_edit"#编辑按钮真实id(应用把 article 拼成了 artile)

        self.driver.find_element(By.CSS_SELECTOR, EnterPost).click()#点击帖子标题，进入帖子详情页
        time.sleep(1)
        # 1. 详情页获取原文
        detail = {
            "title": self.driver.find_element(By.CSS_SELECTOR, "#details_article_title").text.strip(),
            "content": self.driver.find_element(By.CSS_SELECTOR, "#details_article_content").text.strip()
        }
        print("详情页原文:", detail)
        # 2. 点编辑按钮, 编辑模态框出现在当前页(SPA, URL不变)
        assert self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, editBtn))), "编辑按钮不可见"
        self.driver.find_element(By.CSS_SELECTOR, editBtn).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#edit_article_title")))
        # 3. 验证编辑页加载的原文与详情页一致（内容从 Markdown 预览区读取, 而非 CodeMirror 原始值）
        edit_page = {
            "title": self.driver.find_element(By.CSS_SELECTOR, "#edit_article_title").get_attribute("value"),
            "content": self.driver.find_element(By.CSS_SELECTOR, "#edit_article_content_area > div.editormd-preview > div").text.strip()
        }
        print("编辑页加载:", edit_page)
        assert edit_page["title"].strip() == detail["title"], \
            f"编辑页标题 '{edit_page['title']}' 与详情页标题 '{detail['title']}' 不一致"
        assert edit_page["content"].strip() == detail["content"], \
            f"编辑页内容与详情页内容不一致"
        ForumDriver.getScreenshot()

        # ---- 新增: 修改→保存→验证生效 ----
        stamp = datetime.now().strftime("%H%M%S")
        newTitle = detail["title"] + "-已编辑-" + stamp
        newContent = detail["content"] + "\n--- 编辑追加 " + stamp + " ---"
        # 4. 修改标题
        titleBox = self.driver.find_element(By.CSS_SELECTOR, "#edit_article_title")
        titleBox.clear()
        titleBox.send_keys(newTitle)
        # 5. 修改内容(CodeMirror 用 JS API setValue)
        self.driver.execute_script(
            "const cm = document.querySelector('#edit_article_content_area > div.CodeMirror');"
            "if (cm && cm.CodeMirror) { cm.CodeMirror.setValue(arguments[0]); }",
            newContent
        )
        time.sleep(0.5)
        # 6. 点击保存按钮(命名规律: 发帖=#article_post_submit → 编辑猜测=#edit_article_submit)
        saveBtn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#edit_article_submit")))
        self.driver.execute_script("arguments[0].click();", saveBtn)
        # 7. 等待保存成功 toast
        self.wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, ".jq-toast-single"), "成功"))
        print("保存成功 toast 已出现")
        # 8. SPA 保存后跳回首页列表. 遍历列表找"当前用户"发布的帖子, 点回去验证生效
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#artical-items-body")))
        currentNick = self.driver.find_element(By.CSS_SELECTOR, "#index_nav_nickname").text.strip()
        # 遍历首页列表, 找作者==当前昵称的帖子链接
        posts = self.driver.find_elements(By.CSS_SELECTOR, "#artical-items-body > div")
        link_found = None
        for p in posts:
            try:
                author = p.find_element(By.CSS_SELECTOR, ".text-muted ul li:nth-child(1)").text.strip()
                if author == currentNick:
                    link_found = p.find_element(By.CSS_SELECTOR, ".text-truncate > a")
                    break
            except Exception:
                continue
        assert link_found is not None, f"首页列表中未找到作者=[{currentNick}]的帖子"
        self.driver.execute_script("arguments[0].click();", link_found)
        # 9. 等待详情页回来, 断言标题和内容已更新
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#details_article_title")))
        updated_title = self.driver.find_element(By.CSS_SELECTOR, "#details_article_title").text.strip()
        updated_content = self.driver.find_element(By.CSS_SELECTOR, "#details_article_content").text.strip()
        assert updated_title == newTitle, \
            f"保存后标题未更新: 期望[{newTitle}] 实际[{updated_title}]"
        assert stamp in updated_content, \
            f"保存后内容未更新: 期望包含[{stamp}] 实际[{updated_content}]"
        print(f"保存后验证通过: 标题=[{updated_title}], 内容含时间戳=[{stamp}]")
        ForumDriver.getScreenshot()
    
    
        
    
    # 发帖页面元素检查验
    def PageElementInspection(self):
        self.driver.get("http://127.0.0.1:58080/index.html")  # 回首页
        PostingButton = "#bit-forum-content > div.page-header.d-print-none > div > div > div.col-auto.ms-auto.d-print-none > div"
        self.driver.find_element(By.CSS_SELECTOR, PostingButton).click()#进入发帖页面
        self.driver.find_element(By.CSS_SELECTOR, "#article_post_borad")#板块选择器
        self.driver.find_element(By.CSS_SELECTOR, "#article_post_title")#标题输入框
        self.driver.find_element(By.CSS_SELECTOR, "#article_post_content")#内容输入框
        self.driver.find_element(By.CSS_SELECTOR, "#article_post_submit")#发帖按钮
        ForumDriver.getScreenshot()

    #站内信全流程(uc-msg)：test01 给 admin 发私信 → admin 收信(未读badge+列表) → 回复 → test01 确认收到回复
    #依赖：postTest 已发帖(admin 的帖子在首页第一位)；注册测试已创建 test01(test@123)
    def messageTest(self):
        stamp = "私信测试" + datetime.now().strftime("%H%M%S")#带时间戳避免与历史消息重复
        nav_msg = "body > div.page > header.navbar.navbar-expand-md.navbar-light.d-print-none > div > div > div:nth-child(2) > div"#站内信入口

        # === 阶段一：切 test01 登录，点首页第一个帖子(admin 刚发的)进详情页，给 admin 发私信 ===
        self.driver.get("http://127.0.0.1:58080/sign-in.html")
        self.login._login("test01", "test@123")
        # 登录是异步请求, 先等URL跳转到首页, 再等首页列表渲染(直接等列表元素容易超时)
        self.wait.until(EC.url_contains("index.html"))
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#artical-items-body")))
        # 直接点首页第一个帖子进详情页(刚发的 admin 帖子在第一位，无需遍历)
        self.driver.find_element(By.CSS_SELECTOR, "#artical-items-body > div:nth-child(1) .article_list_a_title").click()
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#btn_details_send_message"))).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#index_message_receive_content")))
        receiveName = self.driver.find_element(By.CSS_SELECTOR, "#index_message_receive_user_name").text
        assert "admin" in receiveName, f"发信收件人不是 admin: {receiveName}"
        self.driver.find_element(By.CSS_SELECTOR, "#index_message_receive_content").send_keys(stamp)
        self.driver.find_element(By.CSS_SELECTOR, "#btn_index_send_message").click()
        toast = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".jq-toast-single")))
        assert "成功" in toast.text, f"发送私信未提示成功: {toast.text}"
        print(f"test01 已向 admin 发送私信: {stamp}")
        ForumDriver.getScreenshot()

        # === 阶段二：切 admin 登录，验证未读 badge + 收件箱列表 + 状态为未读，然后回复 ===
        self.driver.get("http://127.0.0.1:58080/sign-in.html")
        self.login._login("admin", "123456")
        # 登录是异步请求, 先等URL跳转完成再等nickname元素(避免间歇性超时)
        self.wait.until(EC.url_contains("index.html"))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#index_nav_nickname")))
        badge = self.driver.find_element(By.CSS_SELECTOR, "#index_nva_message_badge")
        assert badge.is_displayed(), "admin 未读 badge 未显示，应有 test01 的未读私信"
        print("未读 badge 显示，文本:", badge.text)
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, nav_msg))).click()
        # 等消息列表容器可见, 再等至少一条消息项渲染出来(消息是异步加载的, 容器可见时项可能还没出来)
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#index_div_message_list")))
        target = None
        for attempt in range(3):
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#index_div_message_list > div.list-group-item")))
            items = self.driver.find_elements(By.CSS_SELECTOR, "#index_div_message_list > div.list-group-item")
            for item in items:
                preview = item.find_element(By.CSS_SELECTOR, ".text-muted.text-truncate.mt-n1").text
                if stamp in preview:
                    target = item
                    break
            if target is not None:
                break
            time.sleep(1)  # 未找到, 等1秒后重试
        assert target is not None, f"收件箱未找到内容含 [{stamp}] 的私信"
        status = target.find_element(By.CSS_SELECTOR, ".index_message_item_statue").text.strip()
        assert status not in ("[已读]", "[已回复]"), f"新私信应为未读，实际状态: {status}"
        print(f"找到未读私信，状态: {status}，内容预览: {stamp}")
        ForumDriver.getScreenshot()
        # 点该信标题打开回复弹窗，点"回复"按钮展开输入框，输入回复并发送
        target.find_element(By.CSS_SELECTOR, ".index_message_title").click()
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#btn_index_message_reply"))).click()
        reply_input = "#index_message_reply_receive_content"
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, reply_input))).send_keys("回复" + stamp)
        self.driver.find_element(By.CSS_SELECTOR, "#btn_index_send_message_reply").click()
        toast = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".jq-toast-single")))
        assert "成功" in toast.text, f"回复未提示成功: {toast.text}"
        print("admin 已回复该私信")
        ForumDriver.getScreenshot()
        self.driver.find_element(By.CSS_SELECTOR, "#index_message_offcanvasEnd > div.offcanvas-header > button").click()

        # === 阶段三：切回 test01 登录，确认收到 admin 的回信（铃铛只显示收到的消息）===
        # 站内信收件箱只有收到的消息，test01 发出的那条不在这里；admin 回复后 test01 收件箱会出现 admin 的回信
        reply_stamp = "回复" + stamp
        self.driver.get("http://127.0.0.1:58080/sign-in.html")
        self.login._login("test01", "test@123")
        # 登录是异步请求, 先等URL跳转完成再等nickname元素(避免间歇性超时)
        self.wait.until(EC.url_contains("index.html"))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#index_nav_nickname")))
        # 刷新首页让站内信列表重新请求最新数据
        self.driver.get("http://127.0.0.1:58080/index.html")
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#index_nav_nickname")))
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, nav_msg))).click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#index_div_message_list")))
        target = None
        for attempt in range(3):
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#index_div_message_list > div.list-group-item")))
            items = self.driver.find_elements(By.CSS_SELECTOR, "#index_div_message_list > div.list-group-item")
            for item in items:
                preview = item.find_element(By.CSS_SELECTOR, ".text-muted.text-truncate.mt-n1").text
                if reply_stamp in preview:
                    target = item
                    break
            if target is not None:
                break
            time.sleep(1)  # 未找到, 等1秒后重试
        assert target is not None, "test01 收件箱未找到 admin 的回信"
        status = target.find_element(By.CSS_SELECTOR, ".index_message_item_statue").text.strip()
        assert status == "[未读]", f"admin 回信应为未读(test01 尚未查看)，实际状态: {status}"
        print(f"test01 收到 admin 回信，内容: {reply_stamp}，状态: {status}")
        ForumDriver.getScreenshot()
        self.driver.find_element(By.CSS_SELECTOR, "#index_message_offcanvasEnd > div.offcanvas-header > button").click()

        # 恢复 admin 登录态，保证后续 deletePostTest 等用例不受影响
        self.driver.get("http://127.0.0.1:58080/sign-in.html")
        self.login._login("admin", "123456")
        # 登录是异步请求, 先等URL跳转完成再等nickname元素(避免间歇性超时)
        self.wait.until(EC.url_contains("index.html"))
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#index_nav_nickname")))
        print("已恢复 admin 登录态")




if __name__ == '__main__':
    P = Posting()
    P.postTest()#发帖测试
    P.messageTest()#站内信全流程(用刚发的帖进详情页发信)
    P.deletePostTest()#删除帖子测试
    time.sleep(10)
    P.editPostTest()
    P.PageElementInspection()
    P.driver.quit()
