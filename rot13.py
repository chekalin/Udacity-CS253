import cgi
import os
import string
from google.appengine.ext import webapp
import jinja2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

def encode_char(letter):
    uppercase = string.uppercase
    lowercase = string.lowercase
    if letter in uppercase:
        return uppercase[(uppercase.index(letter) + 13) % len(uppercase)]
    elif letter in lowercase:
        return lowercase[(lowercase.index(letter) + 13) % len(lowercase)]
    else:
        return letter

def encode_rot13(text):
    return "".join(map(encode_char, text))

class Rot13Handler(webapp.RequestHandler):
    def print_form(self, text=""):
        text = cgi.escape(text)
        text = encode_rot13(text)
        self.response.out.write(jinja_env.get_template("rot13.html").render(text=text))

    def post(self):
        text = self.request.get("text")
        self.print_form(text)

    def get(self):
        self.print_form()