import os
from google.appengine.api import memcache
from google.appengine.ext import webapp, db
import jinja2
import json
import time

ERROR_MESSAGE = "subject and content, please!"
KEY = 'TOP10'

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

def update_cache():
    posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 10")
    cache = (posts, time.time())
    memcache.set(KEY, cache)
    return cache

class NewPostHandler(webapp.RequestHandler):
    def new_post_form(self, error_message="", subject="", content=""):
        template = jinja_env.get_template("blog-newpost.html")
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
            update_cache()
            self.redirect("/blog/" + str(post.key().id()))

class BlogPost(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

class GenericBlogHandler(webapp.RequestHandler):
    def blog_form(self, posts, updated=0):
        template = jinja_env.get_template("blog.html")
        return self.response.out.write(template.render(posts=posts, updated=updated))

    def get_posts(self):
        cache = memcache.get(KEY)
        if cache is None:
            cache = update_cache()
        return cache

class BlogHandler(GenericBlogHandler):
    def get(self):
        cache = self.get_posts()
        updated = int(time.time() - cache[1])
        return self.blog_form(cache[0], updated)

class PostPermalinkHandler(GenericBlogHandler):
    def get(self, post_id):
        cache = memcache.get(post_id)
        if cache is None:
            post = BlogPost.get_by_id(int(post_id))
            if post:
                cache = (post, time.time())
                memcache.set(post_id, cache)
            else:
                self.redirect("/blog")
        updated = int(time.time() - cache[1])
        return self.blog_form([cache[0]], updated)

class GenericJsonHandler(GenericBlogHandler):
    def generateJsonForPosts(self, posts):
        content = [{'subject': post.subject,
                    'content': post.content,
                    'created': str(post.created.strftime('%a %b %d %H:%M:%S %Y'))
        } for post in posts]
        return json.dumps(content)

class JsonPermalinkHandler(GenericJsonHandler):
    def get(self, post_id):
        post = BlogPost.get_by_id(int(post_id))
        if post:
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write(self.generateJsonForPosts([post]))
        else:
            self.redirect("/blog")

class JsonBlogHandler(GenericJsonHandler):
    def get(self):
        cache = self.get_posts()
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(self.generateJsonForPosts(cache[0]))

class FlushCachesHandler(webapp.RequestHandler):
    def get(self):
        memcache.flush_all()
        self.redirect("/blog")