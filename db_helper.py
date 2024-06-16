import sqlite3
class dbManager():
    def __init__(self, member_openid):
        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()
        self.member_openid=member_openid
        self.c.execute(f"""
            create table if not exists  `{member_openid}` (
                id integer primary key,
                addtime integer,
                content text,
                role text
            )

        """)

        # 用户需要ai记住的长期记忆
        self.c.execute(f"""
            create table if not exists  `{member_openid}_long` (
                
                content text                
            )
        """)
        self.conn.commit()

    # 添加长期记忆
    def add_long(self,  content):
        # 首先清除原有的长期记忆
        self.c.execute(f"""delete from  `{self.member_openid}_long` """)
        # 添加新的长期记忆
        self.c.execute(f"""insert into  `{self.member_openid}_long` (content) values (?)""", (content,))
        self.conn.commit()

    # 查询长期记忆
    def query_long(self):
        self.c.execute(f"""select * from  `{self.member_openid}_long` """)
        return self.c.fetchall()

    # 添加数据
    def add(self, addtime, content, role):
        self.c.execute(f"""insert into  `{self.member_openid}` (addtime, content, role) values (?, ?, ?)""", (addtime, content, role))
        self.conn.commit()

    # 查询数据，返回最近6条数据
    def query(self):
        self.c.execute(f"""select * from  `{self.member_openid}` order by addtime desc limit 6""")
        return self.c.fetchall()
    #    关闭数据库
    def close(self):
        self.conn.close()
        


  



def main():
    member_openid="123234"
    db = dbManager(member_openid)
    db.add(123, "hello", "user")
    db.add(124, "world", "ai")
    print(db.query())

if __name__ == '__main__':
    main() 