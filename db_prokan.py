from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prokan.db'
db = SQLAlchemy(app)

class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(255))
    upass = db.Column(db.String(255))

    member = db.relationship('Member', backref='user', lazy=True)
    preport = db.relationship('Preport', backref='user', lazy=True)

    def __init__(self,uname, upass):
        self.uname = uname
        self.upass = upass
    def __str__(self):
        return f"{self.uid} {self.uname} {self.upass}"


class Project(db.Model):
    pid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    category = db.Column(db.String(255))
    desc = db.Column(db.String(65545))
    updated_at = db.Column(db.DateTime, default=datetime.now)
    comment = db.Column(db.String(65545))

    member = db.relationship('Member', backref='project', lazy=True)
    plan = db.relationship('Plan', backref='project', lazy=True)
    
    def __init__(self,title,category,desc):
        self.title = title
        self.category = category
        self.desc = desc
        

    def __str__(self):
        return f"{self.pid} {self.title} {self.category} {self.desc} {self.updated_at}"    

class Member(db.Model):
    mid = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer, db.ForeignKey("project.pid"))
    uid = db.Column(db.Integer, db.ForeignKey("user.uid"))
    
    def __init__(self,pid,uid):
        self.uid = uid
        self.pid = pid

    def __str__(self):
        return f"{self.mid} {self.uid} {self.pid}"    

class Plan(db.Model):
    planid = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer, db.ForeignKey("project.pid"))
    ptitle = db.Column(db.String(255))
    pbody = db.Column(db.String(65545))
    prate = db.Column(db.Integer, default=0)
    url = db.Column(db.String(255))
    plan_at = db.Column(db.DateTime, default=datetime.now)
    comment = db.Column(db.String(65545))

    def __init__(self,pid,ptitle,pbody):
        self.pid = pid
        self.ptitle = ptitle
        self.pbody = pbody
        self.url = ""

    def __str__(self):
        return f"{self.pid} {self.ptitle} {self.pbody} {self.prate} {self.plan_at}"    

class Preport(db.Model):
    prid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey("user.uid"))
    rtitle = db.Column(db.String(2048))
    content = db.Column(db.String(2048))
    pr_at = db.Column(db.DateTime, default=datetime.now)
    comment = db.Column(db.String(65545))

    def __init__(self,uid,rtitle,content):
        self.uid = uid
        self.rtitle = rtitle
        self.content = content

    def __str__(self):
        return f"{self.prid} {self.uid} {self.content} {self.pr_at}"    

with app.app_context():
    db.drop_all() # テーブル全削除
    db.create_all() # テーブル作成

    # 初期データ追加
    data = [
        User(uname="skohara", upass="kensyu2023"),
        User(uname="tanaka", upass="aaa"),
        User(uname="yamada", upass="bbb"),
        Project(title="テストプロジェクト1", category="Web開発",desc="テスト1"),
        Project(title="テストプロジェクト2", category="データ分析",desc="テスト2"),
        Plan(pid=1, ptitle="基本設計", pbody="基本的な設計"),
        Member(uid=2, pid=1),
        Member(uid=3, pid=2),
        
    ]
    db.session.add_all(data)
    db.session.commit()

    rows = Project.query.all()
    for r in rows:
        print(r)
        for m in r.member:
            print(m.user)

