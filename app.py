import os
from flask import Flask,render_template,request,redirect,session,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import markdown2
from markupsafe import Markup

app = Flask(__name__)
app.secret_key = b'>\x81:2yzVm6{j\x88\xc4\x99\xd5\x0f'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prokan.db'
db = SQLAlchemy(app)

def md_to_html(text):
    """
    MarkdownテキストをHTMLに変換する関数
    """
    return Markup(markdown2.markdown(text))

# Jinja2テンプレートで使用できるようにフィルターとして登録
app.jinja_env.filters['markdown'] = md_to_html


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
        self.comment = ""

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
        self.comment = ""

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
        self.comment = ""

    def __str__(self):
        return f"{self.prid} {self.uid} {self.content} {self.pr_at}"    



@app.get('/')
def index():
    if "uid" not in session:
        return redirect("/login")
    
    
    rows = Project.query.all()
    user =  User.query.get_or_404(session['uid'])
    return render_template("index.html", rows=rows, user=user)

@app.get('/project/<pid>')
def project(pid):
    row = Project.query.get_or_404(pid)
    
    if is_myproject(row.pid):
        return render_template("project_edit.html",project=row,user=User.query.get(session['uid']))
    else:
        return render_template("project.html",project=row,user=User.query.get(session['uid']))

@app.post('/project/<pid>')
def project_post(pid):
    row = Project.query.get_or_404(pid)
    row.title = request.form['title']
    row.desc = request.form['desc']
    row.category = request.form['category']
    db.session.commit()
    return redirect(f"/")

@app.get('/project_add')
def project_add():
    return render_template(f"project_add.html")


@app.post('/project_add')
def project_add_post():
    row = Project(
        title = request.form['title'],
        category = request.form['category'],
        desc = request.form['desc'],
    )
    db.session.add(row)
    db.session.commit()

    member = Member(
        pid = row.pid,
        uid = session['uid']
    )
    db.session.add(member)
    db.session.commit()

    return redirect(f"/")


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


def is_myproject(pid):
    row = Member.query.filter(Member.pid==pid, Member.uid == session['uid']).first()
    return row is not None or session['uid'] == 1


@app.get('/plan/<planid>')
def plan_get(planid):
    row = Plan.query.get_or_404(planid)
    if is_myproject(row.pid):
        return render_template("plan_edit.html",plan=row,user=User.query.get(session['uid']))
    else:
        return render_template("plan.html",plan=row, user=User.query.get(session['uid']))
        

@app.post('/plan/<planid>')
def plan_post(planid):
    row = Plan.query.get_or_404(planid)
    if is_myproject(row.pid)==False:
        return redirect(r'/login')
    
    row.ptitle = request.form['ptitle'];
    row.prate = request.form['prate'];
    row.pbody = request.form['pbody'];
    row.plan_at = datetime.now()
    db.session.commit()
    return redirect(f"/project/{row.pid}")

@app.get('/plan_add/<pid>')
def plan_add_get(pid):
    if is_myproject(pid)==False:
        return redirect(r'/login')

    row = Project.query.get_or_404(pid)
    return render_template("plan_add.html",project=row)

@app.post('/plan_add/<pid>')
def plan_add_post(pid):
    if is_myproject(pid)==False:
        return redirect(r'/login')

    row = Plan(
        pid = pid,
        ptitle = request.form['ptitle'],
        pbody = request.form['pbody'],
    )
    db.session.add(row)
    db.session.commit()
    return redirect(f"/project/{pid}")

@app.get('/preport')
def preport():
    if "uid" not in session:
        return redirect("/login")
    
    rows = Preport.query.filter(Preport.uid == session['uid']).all()
    user = User.query.get(session['uid'])
    return render_template("preport.html", rows=rows, user=user)

@app.get('/preport/<prid>')
def preport_get(prid):
    row = Preport.query.get_or_404(prid)
    if row.uid != session['uid'] and session['uid'] != 1:
        return redirect("/login")
    return render_template("preport_edit.html",preport=row, user=User.query.get(session['uid']))

@app.post('/preport/<prid>')
def preport_post(prid):
    row = Preport.query.get_or_404(prid)
    if row.uid != session['uid'] and session['uid'] != 1:
        return redirect("/login")

    row.rtitle = request.form['rtitle'];
    row.content = request.form['content'];
    row.pr_at = datetime.now()
    db.session.commit()
    return redirect(f"/preport")

@app.get('/preport_add')
def preport_add_get():
    return render_template("preport_add.html")

@app.post('/preport_add')
def preport_add_post():
    row = Preport(
        uid = session['uid'],
        rtitle = request.form['rtitle'],
        content = request.form['content'],
    )
    db.session.add(row)
    db.session.commit()
    return redirect(f"/preport")

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

@app.get('/member/<mid>')
def member(mid):
    row = Member.query.get_or_404(mid)
    return render_template(f"member.html", member=row)

@app.post('/member_del/<mid>')
def member_del(mid):
    row = Member.query.get_or_404(mid)
    if row.uid != session['uid'] and session['uid'] != 1:
        return redirect("/login")
    
    db.session.delete(row)
    db.session.commit()

    return redirect(f"/project/{row.pid}")

@app.post('/member_add/<pid>')
def member_add(pid):
    print("1")
    user = User.query.filter(User.uname == request.form['uname']).first()
    if user == None:
        flash('ユーザが見つかりません')
        return redirect(f"/project/{pid}")    
    print("2")
    uid = user.uid
    
    exists_member = Member.query.filter(Member.pid == pid).all()
    if len(exists_member) >= 4:
        flash('既にメンバーが４人以上居ます')
        return redirect(f"/project/{pid}")    
    print("3")
    mem = Member.query.filter(Member.pid == pid, Member.uid == uid).first()
    if mem != None:
        flash('既に追加されています：' + user.uname)
        return redirect(f"/project/{pid}")    

    print("4")
    mem = Member.query.filter(Member.uid == uid).first()
    if mem != None:
        flash('既に他のプロジェクトに参加しています。このプロジェクトに参加する場合、解除してください。')
        return redirect(f"/project/{pid}")    

    print("5")
    m = Member(
        uid = uid,
        pid = pid
    )
    db.session.add(m)
    db.session.commit()

    return redirect(f"/project/{pid}")

# 管理者用
@app.get('/user_admin')
def user_admin():
    if session["uid"] != 1:
        return redirect("/login")
    
    rows = User.query.all()
    return render_template("user_admin.html", rows=rows)

@app.get('/preport_admin/<uid>')
def preport_admin(uid):
    if session["uid"] != 1:
        return redirect("/login")
    
    rows = Preport.query.filter(Preport.uid == uid).all()
    user = User.query.get(uid)
    return render_template("preport.html", rows=rows, user=user)

@app.post('/pcomment/<pid>')
def pcomment_post(pid):
    if session['uid'] != 1:
        return redirect("/login")

    row = Project.query.get_or_404(pid)
    row.comment = request.form['comment']
    db.session.commit()
    flash('講師コメント更新')
    return redirect(f"/project/{pid}")

@app.post('/plancomment/<planid>')
def plancomment_post(planid):
    if session['uid'] != 1:
        return redirect("/login")

    row = Plan.query.get_or_404(planid)
    row.comment = request.form['comment']
    db.session.commit()
    flash('講師コメント更新')
    return redirect(f"/plan/{planid}")


@app.post('/prcomment/<prid>')
def prcomment_post(prid):
    if session['uid'] != 1:
        return redirect("/login")

    row = Preport.query.get_or_404(prid)
    row.comment = request.form['comment']
    db.session.commit()
    flash('講師コメント更新')
    return redirect(f"/preport/{prid}")


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8885)
