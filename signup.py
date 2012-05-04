import re
from google.appengine.ext import webapp

form = """
<html>
  <head>
    <title>Sign Up</title>
    <style type="text/css">
      .label {text-align: right}
      .error {color: red}
    </style>

  </head>

  <body>
    <h2>Signup</h2>
    <form method="post">
      <table>
        <tr>
          <td class="label">
            Username
          </td>
          <td>
            <input type="text" name="username" value="%(username)s">
          </td>
          <td class="error">%(er_username)s</td>
        </tr>

        <tr>
          <td class="label">
            Password
          </td>
          <td>
            <input type="password" name="password" value="%(password)s">
          </td>
          <td class="error">
              %(er_password)s
          </td>
        </tr>

        <tr>
          <td class="label">
            Verify Password
          </td>
          <td>
            <input type="password" name="verify" value="%(verify)s">
          </td>
          <td class="error">
            %(er_verify)s
          </td>
        </tr>

        <tr>
          <td class="label">
            Email (optional)
          </td>
          <td>
            <input type="text" name="email" value="%(email)s">
          </td>
          <td class="error">
            %(er_email)s
          </td>
        </tr>
      </table>

      <input type="submit">
    </form>
  </body>

</html>
"""

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
    return EMAIL_RE.match(email)


def get_errors(params):
    errors = {"er_username" : "", "er_password" : "", "er_verify" : "", "er_email" : ""}
    failed = False
    if not username_valid(params["username"]):
        errors["er_username"] = "That's not a valid username."
        failed = True
    if not password_valid(params["password"]):
        errors["er_password"] = "That wasn't a valid password."
        failed = True
    if not verify_valid(params["password"], params["verify"]):
        errors["er_verify"] = "Your passwords didn't match."
        failed = True
    if not email_valid(params["email"]):
        errors["er_email"] = "That's not a valid email."
        failed = True
    return failed, errors

class SignupHandler(webapp.RequestHandler):
    def get(self):
        self.print_form()

    def print_form(self, errors=None, params=None):
        if not errors: errors = {"er_username" : "", "er_password" : "", "er_verify" : "", "er_email" : ""}
        if not params: params = {"username" : "", "password" : "", "verify" : "", "email" : ""}
        self.response.out.write(form % dict(errors.items() + params.items()))

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")
        params = {"username" : username, "password" : password, "verify" : verify, "email" : email}
        failed, errors = get_errors(params)
        if not failed:
            self.redirect("/unit2/welcome?username=" + username)
        else:
            self.print_form(errors, params)

class WelcomeHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write("Welcome, " + self.request.get("username")+ "!")
