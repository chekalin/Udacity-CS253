import cgi
import string
from google.appengine.ext import webapp

form = """
    <html>
      <head>
        <title>Unit 2 Rot 13</title>
      </head>

      <body>
        <h2>Enter some text to ROT13:</h2>
        <form method="post">
            <textarea name="text" style="height: 100px; width: 400px;">%(text)s</textarea>
          <br>
          <input type="submit">
        </form>
      </body>

    </html>
"""

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
        self.response.out.write(form % {"text" : text})

    def post(self):
        text = self.request.get("text")
        self.print_form(text)

    def get(self):
        self.print_form()