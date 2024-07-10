from flask import Flask , render_template
app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/admin-login")
def adminlogin():
    return render_template("/admin/admin-login.html")

@app.route("/user-login")
def userlogin():
    return render_template("user-login.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/sponcer-dashboard")
def sponcerdashboard():
    return render_template("/sponcor/sponcer-dashboard.html")

@app.route("/admin-dashboard")
def admindashboard():
    return render_template("/admin/admin-dashboard.html")


@app.route("/influencer-dashboard")
def influencerdashboard():
    return render_template("/influencer/influencer-dashboard.html")

@app.route("/search")
def search():
    return render_template("/admin/search.html")

if __name__ == '__main__':
    app.run(debug=True)