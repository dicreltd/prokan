import os
from flask import Flask,render_template,request,redirect,session,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = b'>\x81:2yzVm6{j\x88\xc4\x99\xd5\x0f'

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
    plan_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self,pid,ptitle,pbody):
        self.pid = pid
        self.ptitle = ptitle
        self.pbody = pbody

    def __str__(self):
        return f"{self.pid} {self.ptitle} {self.pbody} {self.prate} {self.plan_at}"    

class Preport(db.Model):
    prid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey("user.uid"))
    rtitle = db.Column(db.String(2048))
    content = db.Column(db.String(2048))
    pr_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self,uid,rtitle,content):
        self.uid = uid
        self.rtitle = rtitle
        self.content = content

    def __str__(self):
        return f"{self.prid} {self.uid} {self.content} {self.pr_at}"    



@app.get('/')
def index():
    if "uid" not in session:
        return redirect("/login")
    
    rows = Project.query.all()
    return render_template("index.html", rows=rows)

@app.get('/project/<pid>')
def project(pid):
    row = Project.query.get_or_404(pid)
    return render_template("project.html", project=row)

@app.get('/user/<uid>')
def user(uid):
    row = User.query.get_or_404(uid)
    return render_template("user.html", user=row)

@app.get('/login')
def login():
    return render_template("login.html")

@app.post('/login')
def login_post():
    uname = request.form['uname']
    upass = request.form['upass']

    row = User.query.filter(User.uname==uname, User.upass == upass).first()

    if row is None:
        flash("ユーザ名またはパスワードが違います")
        return redirect("/login")
    else:
        session['uid'] = row.uid
        return redirect("/")

@app.get('/logout')
def logout():
    session.pop('uid', None)
    return redirect("/")


@app.get('/update_project/<pid>')
def update_project_get(pid):
    row = Project.query.get_or_404(pid)
    return render_template("update_project.html",toukou=row)

@app.post('/update_project/<pid>')
def update_project_post(tid):
    row = Project.query.get_or_404(tid)
    row.mes = request.form['mes']
    db.session.commit()
    return redirect(f"/project/{row.pid}")

@app.get('/plan/<pid>')
def plan_get(pid):
    row = Plan.query.get_or_404(pid)
    return render_template("plan.html",toukou=row)

@app.post('/plan_add/<pid>')
def plan_add_post(pid):
    row = Plan(
        pid = pid,
        ptitle = request.form['ptitle'],
        pbody = request.form['body'],
    )
    db.session.add(row)
    db.session.commit()
    return redirect(f"/project/{pid}")

@app.get('/regist')
def regist():
    return render_template("regist.html")

@app.post('/regist')
def regist_post():
    uname = request.form['uname']
    upass = request.form['upass']

    u = User(uname,upass)
    db.session.add(u)
    db.session.commit()

    return redirect("/login")


app.run(debug=True)