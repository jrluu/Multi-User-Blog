#Usees JINJA to seperate HTML from python script
#autoescape to prevent JS/HTML/CSS injections
#


import os
import jinja2
import webapp2
import hashlib      # For hash function...not needed if using HMAC
import hmac

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)




class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template,**kw))

class Art(db.Model):
    title = db.StringProperty(required = True)
    art = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class MainPage(Handler):

    def render_front(self, title="", art="", error=""):
        arts = db.GqlQuery("SELECT * FROM Art "
                           "ORDER BY created DESC")

        self.render("front.html", title= title, art= art, error=error, arts = arts)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        art = self.request.get("art")

        if title and art:
            a = Art(title = title, art = art)
            a.put()

            self.redirect("/")
        else:
            error = "we need both a title and some artwork"
            self.render_front(title, art, error)

#Create Database
class blog(db.Model):
    title = db.StringProperty(required = True)
    blog = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("blogPost.html", p = self)

class blog(Handler):

    def render_front(self):
        blog = db.GqlQuery("SELECT * FROM blog "
                           "ORDER BY created DESC")

        self.render("blog.html", blog = blog)

    def get(self):
        self.render_front()

class blogPost(Handler):
    def render_front(self, subject="", content="", error=""):
        self.render("blogPost.html", subject=subject, content=content, error=error)

    def get(self):
        self.render_front()

    def post(self):
        #Get values from the URL
        #For example, localhost:8080/?subject="food"
        subject = self.request.get("subject")
        content = self.request.get("content")

        if title and content:
            b = blog(subject = subject, content = content)
            b.put()

            self.redirect("/blogPost")
        else:
            error = "we need both a title and some artwork"
            self.render_front(subject, content, error)


SECRET = "asdf"
def hash_str(s):
    return hmac.new(SECRET,s).hexdigest()

#Takes in some value, and returns "value,hash"
def make_secure_val(s):
    return "%s|%s" %(s, hash_str(s))

#Takes in a string of format "value,hash"
#Return value if true
def check_secure_val(h):
    val = h.split('|')[0]
    if hmac.compare_digest(h, make_secure_val(val)):
        return val

#Use HMAC (hash-based messaged authentication code) to add salt
class CookiePage(Handler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        visits = 0
        visit_cookie_str = self.request.cookies.get('visits')
        if visit_cookie_str:
            cookie_val = check_secure_val(visit_cookie_str)
            if cookie_val:
                visits = int(cookie_val)

        visits += 1

        new_cookie_val = make_secure_val(str(visits))

        self.response.headers.add_header('Set-Cookie', 'visits=%s' % new_cookie_val)

        if visits > 100:
            self.write("You are the best ever!")
        else:
            self.write("You've been here %s times!" % visits)

app = webapp2.WSGIApplication([('/', MainPage),
                                ('/blog', blog),
                                ('/blogPost', blogPost),
                                ('/cookiepage', CookiePage),
                                ],
                                debug=True)
