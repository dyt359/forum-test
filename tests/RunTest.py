import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))# 把项目根目录加入sys.path, 保证任意目录运行都能导入tests/common包

from tests import ForumLogin, ForumSignup, ForumIndex, PostDetailsPage, Posting, PersonalCenter, MyPost, Security
from common.Utils import ForumDriver


def _banner(title):# 模块横幅
    print(f"\n{'=' * 24} {title} {'=' * 24}")

def _step(title):# 用例步骤行
    print(f"\n---- {title} ----")

if __name__ == '__main__':
    # 注意: 每个测试类只实例化一次, 后续用例共用同一实例(与各测试文件自己__main__的写法一致)。
    # 构造函数会重新打开页面, 若每行都 X.Class().method() 会把登录态/页面状态重置掉。

    # ==================== 注册测试 ====================
    _banner("注册测试 ForumSignup")
    su = ForumSignup.ForumSignup()
    _step("正常注册")
    su.NormalSignupTest()
    _step("异常注册")
    su.AbnormalSignupTest()
    _step("未勾选协议无法注册(前端拦截标红)")
    su.PolicyUncheckTest()
    _step("注册页元素检查")
    su.SignupPageElementCheck()

    # ==================== 登录测试 ====================
    _banner("登录测试 ForumLogin")
    lg = ForumLogin.ForumLogin()
    _step("登录成功")
    lg.loginSucTest()
    _step("登录失败(错误用户名/密码)")
    lg.loginErrTest()
    _step("登录页元素检查")
    lg.LoginPageCheck()

    # ==================== 主页测试 ====================
    _banner("主页测试 ForumIndex")
    fi = ForumIndex.ForumIndex()
    _step("登录")
    fi.loginTest()
    _step("板块切换")
    fi.boardTest()
    _step("导航栏个人信息")
    fi.userInfoTest()
    _step("帖子列表断言(idx-postlist): 首帖标题/作者/时间格式/浏览·点赞·回复数为纯数字")
    fi.postTest()
    # _step("搜索")  # [BUG] 搜索用例暂缓: 1)后端不按关键字过滤(表单input缺name+后端未实现); 2)回车后页面重载与读列表存在竞态(StaleElementReferenceException)
    # fi.searchTest()

    _step("主题切换")
    fi.themeTest()
    _step("站内信")
    fi.messageTest()
    _step("退出登录")
    fi.logoutTest()
    _step("未登录状态访问(此后浏览器处于未登录态)")
    fi.unloginTest()

    # ==================== 个人中心测试 ====================
    # 其构造函数直接打开首页, 依赖上面未登录状态; 结束时昵称恢复admin、密码恢复123456
    _banner("个人中心测试 PersonalCenter")
    pc = PersonalCenter.PersonalCenter()
    _step("登录")
    pc.loginTest()
    _step("进入个人中心")
    pc._enterMyPost()
    _step("修改昵称(结束恢复为 admin)")
    pc._changeUser()
    _step("修改邮箱")
    pc.UserInfoTest()
    # [BUG] uc-avatar/uc-bad-email/uc-bad-phone/uc-pwd-bad-weak: 头像上传失效+邮箱/手机号/密码强度均无校验, 用例无法编写
    _step("修改密码(异常场景+正常修改+双向登录验证+恢复原密码)")
    pc._changePassword()

    # ==================== 发帖测试 ====================
    _banner("发帖测试 Posting")
    P = Posting.Posting()
    _step("发帖(成功+标题为空+内容为空)")
    P.postTest()
    _step("站内信全流程(test01发信给admin → admin收信+未读badge+回复 → test01确认收到回复)")
    P.messageTest()
    _step("编辑帖子(改刚发的那条, 再保存验证生效)")
    P.editPostTest()
    _step("删除帖子(删刚编辑过的那条, 避免标题跨运行累积后缀)")
    P.deletePostTest()
    _step("发帖页元素检查")
    P.PageElementInspection()

    # ==================== 帖子详情页测试 ====================
    _banner("帖子详情页测试 PostDetailsPage")
    pdp = PostDetailsPage.PostDetailsPage()
    _step("登录")
    pdp.loginTest()
    _step("进入帖子详情页")
    pdp.postTest()
    _step("详情页元素检查")
    pdp.postDetailsPageElementCheck()
    _step("点赞(点赞+取消+重复点赞)")
    pdp.likePost()
    _step("回复(成功/空内容/超长内容)")
    pdp.replyPost()
    _step("回复按时间降序排列")
    pdp.checkReplyTime()
    _step("他人帖子不可见编辑/删除按钮")
    pdp.checkPermission()
    _step("本人帖子可见编辑/删除按钮")
    pdp.checkOwnPostPermission()
    _step("编辑页加载原文校验")
    pdp.checkEditPost()

    # ==================== 我的帖子测试 ====================
    _banner("我的帖子测试 MyPost")
    mp = MyPost.MyPost()
    _step("登录")
    mp.loginTest()
    _step("我的帖子页元素检查")
    mp.myPostPageElementCheck()
    _step("帖子数量一致性")
    mp.postCountTest()
    _step("帖子列表内容(含回复数断言 mine-list-reply)")
    mp.postListCheck()
    _step("点击帖子标题进入详情页")
    mp.enterPostTest()
    _step("空列表状态提示(切换无帖子的 test01, 依赖注册测试)")
    mp.emptyListTest()

    # ==================== 安全测试 ====================
    # SQL 注入场景一/二已固化进 ForumLogin.loginErrTest(case 6/10) 每次回归; 本模块聚焦 XSS 注入
    _banner("安全测试 Security")
    sec = Security.Security()
    _step("XSS 注入(私信 payload <img onerror=alert> → admin 查看时检测 alert)")
    sec.xssTest()

    ForumDriver.driver.quit()
