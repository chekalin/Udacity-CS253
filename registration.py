import hashlib
import hmac
import os
import random
import re
import string
from google.appengine.ext import webapp, db
import jinja2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)
SECRET = "mega-secret-keyword"

class BaseHandler(webapp.RequestHandler):
    def render(self, template, **kwargs):
        self.response.out.write(jinja_env.get_template(template).render(**kwargs))

    def set_cookie_and_redirect(self, user):
        hashed_id_token = create_hashed_token(str(user.key().id()))
        self.response.headers.add_header('Set-Cookie', 'user_id=%s; Path=/' % hashed_id_token)
        return self.redirect("/blog/welcome")

class RegistrationHandler(BaseHandler):
    def get(self):
        self.render("signup.html")

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")
        params = {"username" : username, "password" : password, "verify" : verify, "email" : email}
        errors = validate(params)
        if errors:
            params_errors = dict(params.items() + errors.items())
            self.render("signup.html", **params_errors)
        else:
            hashed = make_pw_hash(username, password)
            user = User(username=username, password=hashed, email=email)
            user.put()
            return self.set_cookie_and_redirect(user)

def validate(params):
    errors = {}
    if not username_valid(params["username"]):
        errors["er_username"] = "That's not a valid username."
    if not password_valid(params["password"]):
        errors["er_password"] = "That wasn't a valid password."
    if not verify_valid(params["password"], params["verify"]):
        errors["er_verify"] = "Your passwords didn't match."
    if params["email"] and not email_valid(params["email"]):
        errors["er_email"] = "That's not a valid email."
    return errors

def username_valid(username):
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    return USER_RE.match(username)

def password_valid(password):
    PASSWORD_RE = re.compile(r"^.{3,20}$")
    return PASSWORD_RE.match(password)

def verify_valid(password, verify):
    return password == verify

def email_valid(email):
    EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
    return not email or EMAIL_RE.match(email)

class User(db.Model):
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (h, salt)

def valid_pw(name, pw, h):
    salt = h.split(",")[1]
    return h == make_pw_hash(name, pw, salt)

def get_hash(user_id):
    return hmac.new(SECRET, user_id).hexdigest()

def create_hashed_token(user_id):
    user_id = str(user_id)
    return str(user_id + "|" + get_hash(user_id))

def valid_username(hashed_id_token):
    user_id = extract_id(hashed_id_token)
    hashed = hashed_id_token.split("|")[1]
    return hashed == get_hash(user_id)

def extract_id(user_id_token):
    return user_id_token.split("|")[0]

class WelcomeHandler2(BaseHandler):
    def get(self):
        user_id_token = str(self.request.cookies.get('user_id'))
        if user_id_token and valid_username(user_id_token):
            user_id = extract_id(user_id_token)
            user = User.get_by_id(int(user_id))
            return self.render("welcome.html", username=user.username)
        else:
            return self.redirect("/blog/signup")

class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html")

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        users = db.GqlQuery("SELECT * FROM User WHERE username='" + username + "'")
        if users.count() > 0:
            user = users[0]
            if valid_pw(username, password, user.password):
                return self.set_cookie_and_redirect(user)
        return self.render("login.html", er_login="Invalid login")

class LogoutHandler(BaseHandler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
        return self.redirect("/blog/signup")




