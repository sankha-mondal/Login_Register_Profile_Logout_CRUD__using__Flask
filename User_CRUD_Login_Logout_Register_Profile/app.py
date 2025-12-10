from flask import Flask, redirect, render_template, request, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
import pymysql
import bcrypt

# ---------------------- Flask Config --------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key_here"


# ---------------------- MySQL Connection -----------------------------
def get_db():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="#Sankha12@98",
        database="flask_user_db",
        cursorclass=pymysql.cursors.DictCursor
    )


# ---------------------- WTForms: Register Form ----------------------
class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (field.data,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            raise ValidationError("Email is already taken")


# ---------------------- WTForms: Login Form -------------------------
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")




















# ============================= Routes ====================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, hashed_password)
        )
        conn.commit()
        cursor.close()
        conn.close()

        flash("Registration successful. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
            session["user_id"] = user["id"]
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for("login"))

    return render_template("login.html", form=form)


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        return render_template("dashboard.html", user=user)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("login"))

@app.route("/add_edit_view_user", methods=["GET", "POST"])
def add_edit_view_user():
    conn = get_db()
    cursor = conn.cursor()
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, hashed_password)
        )
        conn.commit()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    # return redirect(url_for("login"))
    return render_template("add_edit_view_user.html", users=users)
    
@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    conn = get_db()
    print("user id:===========" + str(user_id))
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("User deleted successfully.", "success")
    return redirect(url_for("add_edit_view_user"))


# ---------------------- Run App --------------------------
if __name__ == "__main__":
    app.run(debug=True)
