import os
from google.appengine.ext import webapp
import jinja2
from blog import NewPostHandler, PostPermalinkHandler, BlogHandler, JsonPermalinkHandler, JsonBlogHandler
from rot13 import Rot13Handler
from signup import SignupHandler, WelcomeHandler
from registration import RegistrationHandler, WelcomeHandler2, LoginHandler, LogoutHandler

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

class ContentsHandler(webapp.RequestHandler):
    def get(self):
        template = jinja_env.get_template("contents.html")
        return self.response.out.write(template.render())

app = webapp.WSGIApplication([
                              ('/', ContentsHandler),
                              ('/unit2/rot13', Rot13Handler),
                              ('/unit2/signup', SignupHandler),
                              ('/unit2/welcome', WelcomeHandler),
                              ('/unit3/blog/newpost', NewPostHandler),
                              ('/blog/welcome', WelcomeHandler2),
                              ('/blog/login', LoginHandler),
                              ('/blog/logout', LogoutHandler),
                              ('/blog', BlogHandler),
                              ('/blog/signup', RegistrationHandler),
                              ('/blog/newpost', NewPostHandler),
                              ('/blog/(\d+)', PostPermalinkHandler),
                              ('/blog/(\d+).json', JsonPermalinkHandler),
                              ('/blog.json', JsonBlogHandler),
                              ('/blog/.json', JsonBlogHandler)
                             ], debug=True)
