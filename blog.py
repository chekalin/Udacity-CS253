import os
from google.appengine.ext import webapp, db
import jinja2

ERROR_MESSAGE = "subject and content, please!"

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

class NewPostHandler(webapp.RequestHandler):
    def new_post_form(self, error_message="", subject="", content=""):
        template = jinja_env.get_template("newpost.html")
        return self.response.out.write(template.render(error_message=error_message, subject=subject, blog=content))

    def get(self):
        return self.new_post_form()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")
        if not subject or not content:
            return self.new_post_form(subject=subject, content=content, error_message=ERROR_MESSAGE)
        else:
            post = BlogPost(subject=subject, content=content)
            post.put()
            self.redirect("/unit3/blog/" + str(post.key().id()))

class BlogPost(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

class GenericBlogHandler(webapp.RequestHandler):
    def blog_form(self, posts):
        template = jinja_env.get_template("blog.html")
        return self.response.out.write(template.render(posts=posts))

class BlogHandler(GenericBlogHandler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created desc")
        return self.blog_form(posts)

class PostPermalinkHandler(GenericBlogHandler):
    def get(self, post_id):
        post = BlogPost.get_by_id(int(post_id))
        return self.blog_form([post])