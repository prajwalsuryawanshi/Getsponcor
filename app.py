from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    uname = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100))

    def __init__(self, password, uname):
        self.uname = uname
        self.password = password

    def check_password(self, password):
        return password == self.password

class Sponcer(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    uname = db.Column(db.String(100), unique=True, nullable=False)
    industry = db.Column(db.String(50), unique=False, nullable=False)
    password = db.Column(db.String(100))

    def __init__(self, password, uname, industry):
        self.uname = uname
        self.industry = industry
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(100), unique=True, nullable=False)
    platform = db.Column(db.String(25), unique=False , nullable=False )
    reach = db.Column(db.Integer, unique=False , nullable=False)
    niche = db.Column(db.String(25), unique=False, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, password, uname, platform, reach, niche):
        self.uname = uname
        self.platform = platform
        self.reach = reach
        self.niche = niche
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

class Campaigns(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date , nullable=False)
    end_date = db.Column(db.Date , nullable=False)
    uname = db.Column(db.String , nullable=False )
    niche = db.Column(db.String(30) , nullable=False)
    description = db.Column(db.String(3000) )
    created_on = db.Column(db.Date , nullable=False)
    budget = db.Column(db.Integer )
    title = db.Column(db.String(100), nullable=False)

    def __init__(self, start_date, end_date, uname, niche, description, created_on, budget, title):
        self.start_date = start_date
        self.end_date = end_date
        self.uname = uname
        self.niche = niche
        self.description = description
        self.created_on = created_on
        self.budget = budget
        self.title = title

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_on = db.Column(db.Date, default=datetime.now().date)

    campaign = db.relationship('Campaigns', backref=db.backref('requests', lazy=True))
    influencer = db.relationship('Influencer', backref=db.backref('requests', lazy=True))

    def __init__(self, campaign_id, influencer_id,  status='pending'):
        self.campaign_id = campaign_id
        self.influencer_id = influencer_id
        self.status = status
        self.created_on = datetime.now().date()

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

########## admin
@app.route("/admin-login", methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        uname = request.form['uname']
        passwd = request.form['passwd']

        user = Admin.query.filter_by(uname=uname).first()
        if user and user.check_password(passwd):
            session['uname'] = user.uname
            session['user_type'] = 'Admin'
            return redirect('/admin-dashboard')
        else:
            return render_template('/admin/admin-login.html', error='Invalid username or password')

    return render_template('/admin/admin-login.html')
        
@app.route("/admin-dashboard")
def admindashboard():
    if 'uname' in session and session.get('user_type') == 'Admin':
        user = Admin.query.filter_by(uname=session['uname']).first()
        return render_template("/admin/admin-dashboard.html", user=user)
    return redirect('/admin-login')
    
@app.route('/admin-logout')
def adminlogout():
    session.pop('uname', None)
    return redirect('/admin-login')

########## sponcer

@app.route("/sponcer-signup", methods=['GET', 'POST'])
def sponcorsignup():
    if request.method == 'POST':
        uname = request.form['uname']
        industry = request.form['industry']
        passwd = request.form['passwd']

        existing_user = Sponcer.query.filter_by(uname=uname).first()
        if existing_user:
            return render_template("/sponcor/sponcer-signup.html", error='Username already exists. Please choose a different one.')

        new_usr = Sponcer(uname=uname, password=passwd, industry=industry)
        db.session.add(new_usr)
        db.session.commit()


        return redirect('user-login')

    return render_template("/sponcor/sponcer-signup.html")

@app.route("/sponcer-dashboard", methods=['GET', 'POST'])
def sponcerdashboard():
    if 'uname' in session and session.get('user_type') == 'sponcer':
        user = Sponcer.query.filter_by(uname=session['uname']).first()
        if request.method == 'POST':
            start_date_str = request.form['start_date']
            end_date_str = request.form['end_date']
            uname = session['uname']
            niche = request.form['niche']
            description = request.form['description']
            created_on = datetime.now().date()
            budget = request.form['budget']
            title = request.form['title']

            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            except ValueError as e:
                flash(f"Invalid date format: {e}")
                return redirect(url_for('sponcerdashboard'))

            new_campaign = Campaigns(start_date=start_date, end_date=end_date, uname=uname, niche=niche, description=description, created_on=created_on, budget=budget, title=title)
            db.session.add(new_campaign)
            db.session.commit()
            flash("Campaign created successfully!")
        campaigns = Campaigns.query.filter_by(uname=session['uname']).all()
        influcencers = Influencer.query.all()
        today = datetime.now().date()
        return render_template("/sponcor/sponcer-dashboard.html", user=user, campaigns=campaigns , influcencers=influcencers , today=today)
    return redirect('/user-login')

@app.route("/delete_campaign/<int:campaign_id>", methods=['POST'])
def delete_campaign(campaign_id):
    if 'uname' in session and session.get('user_type') == 'sponcer':
        campaign = Campaigns.query.filter_by(id=campaign_id, uname=session['uname']).first()
        if campaign:
            db.session.delete(campaign)
            db.session.commit()
            flash("Campaign deleted successfully!")
    return redirect(url_for('sponcerdashboard'))

@app.route("/send_request/<int:campaign_id>", methods=['POST'])
def send_request(campaign_id):
    if 'uname' in session and session.get('user_type') == 'influencer':
        influencer = Influencer.query.filter_by(uname=session['uname']).first()
        new_request = Request(campaign_id=campaign_id, influencer_id=influencer.id,)
        db.session.add(new_request)
        db.session.commit()
        flash("Request sent successfully!")
        return redirect(url_for('influencerdashboard'))
    return redirect('/user-login')

########## influencer

@app.route("/influencer-signup", methods=['GET', 'POST'])
def influencersignup():
    if request.method == 'POST':
        uname = request.form['uname']
        platform = request.form['platform']
        reach = request.form['reach']
        niche = request.form['niche']
        passwd = request.form['passwd']

        existing_user = Influencer.query.filter_by(uname=uname).first()
        if existing_user:
            return render_template("/influencer/influencer-signup.html", error='Username already exists. Please choose a different one.')

        new_usr = Influencer(uname=uname, password=passwd, platform=platform, reach=reach, niche=niche)
        db.session.add(new_usr)
        db.session.commit()
        return redirect('user-login')

    return render_template("/influencer/influencer-signup.html")

@app.route("/influencer-dashboard")
def influencerdashboard():
    if 'uname' in session and session.get('user_type') == 'influencer':
        user = Influencer.query.filter_by(uname=session['uname']).first()
        campaigns = Campaigns.query.all()
        return render_template("/influencer/influencer-dashboard.html", user=user , campaigns=campaigns)
  
    return redirect('/user-login')

######## user both sponcer/influencer

@app.route("/user-login", methods=['GET', 'POST'])
def userlogin():
    if request.method == 'POST':
        uname = request.form['uname']
        passwd = request.form['passwd']

        user = Sponcer.query.filter_by(uname=uname).first()
        if user and user.check_password(passwd):
            session['uname'] = user.uname
            session['user_type'] = 'sponcer'
            return redirect('/sponcer-dashboard')
        else:
            user = Influencer.query.filter_by(uname=uname).first()
            if user and user.check_password(passwd):
                session['uname'] = user.uname
                session['user_type'] = 'influencer'
                return redirect('/influencer-dashboard')
            else:
                return render_template('user-login.html', error='Invalid username or password')

    return render_template("user-login.html")

@app.route('/user-logout')
def userlogout():
    session.pop('uname', None)
    return redirect('/user-login')

if __name__ == '__main__':
    app.run(debug=True)
