import pymysql

# 数据库连接配置（与论坛主服务 forum_db 同一个库）
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "123456",
    "database": "forum_db",
    "charset": "utf8mb4",
    "autocommit": False,
}


def permanent_delete_user(username):
    """
    按用户名彻底删除测试用户（物理删除，释放用户名，可重新注册）。
    会级联清理该用户的帖子、回复、站内信，与管理后台逻辑一致。
    返回被删除的用户 id；用户不存在或数据库连不上时返回 None。
    """
    try:
        conn = pymysql.connect(**DB_CONFIG)
    except Exception as e:
        print(f"[DBUtil] 数据库连接失败，跳过清理: {e}")
        return None
    try:
        with conn.cursor() as cur:
            # 先查出用户 id
            cur.execute("SELECT id FROM t_user WHERE username = %s", (username,))
            row = cur.fetchone()
            if not row:
                return None
            uid = row[0]

            # 级联删除（顺序：被依赖的先删）
            # 1) 该用户发的帖子下的回复
            cur.execute(
                "DELETE FROM t_article_reply WHERE articleId IN "
                "(SELECT id FROM t_article WHERE userId = %s)",
                (uid,),
            )
            # 2) 该用户发的帖子
            cur.execute("DELETE FROM t_article WHERE userId = %s", (uid,))
            # 3) 该用户在别人帖子下发的回复
            cur.execute("DELETE FROM t_article_reply WHERE postUserId = %s", (uid,))
            # 4) 站内信（发送或接收）
            cur.execute(
                "DELETE FROM t_message WHERE postUserId = %s OR receiveUserId = %s",
                (uid, uid),
            )
            # 5) 用户本身
            cur.execute("DELETE FROM t_user WHERE id = %s", (uid,))
        conn.commit()
        print(f"[DBUtil] 已彻底删除用户 '{username}' (id={uid})，用户名可重新注册")
        return uid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
