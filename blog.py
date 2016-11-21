"""
This file contains all of the code for blog.
It contains handlers for all the page and it has the Kind/Collection/Schema
for the database, ndb
"""
import os
import hmac
import urllib
import webapp2
import jinja2
from google.appengine.ext import ndb

from post import Post
from vote import Vote
from account import Account

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
                               autoescape=True)

SECRET = "SamSmith"
DEFAULT_POST_ID = 1111111111111111

def hash_str(string):
    """Returns a string encyrpted by using the HMAC protocol"""
    return hmac.new(SECRET, string).hexdigest()


class Handler(webapp2.RequestHandler):
    """
    Base Handler Class
    Takes care of page rendering, cookies maniupulation, and header
    """

    def write(self, *a, **kw):
        """ Writes output to client's browser """
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        """ Renders HTML using template """
        params['user'] = self.request.cookies.get("username")
        t = JINJA_ENV.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        """ Calls Above Functions """
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        """ Sets username and password(hashed version) into cookie """
        self.response.headers['Content-Type'] = 'text/html'
        cookie_val = str(hash_str(val))
        self.response.headers.add_header('Set-Cookie', 'username = %s' % str(name))
        self.response.headers.add_header('Set-Cookie', 'password = %s' % cookie_val)

    def check_cookie(self):
        """  Checks cookie username and password against database """
        username = self.request.cookies.get("username")
        password = self.request.cookies.get("password")

        if username:
            account_query = Account.get_by_id(username)
            if account_query and account_query.password:
                    return True if account_query.password == password else False


    def clear_cooke(self):
        """  Clears Cookie """
        self.response.headers['Content-Type'] = 'text/html'
        self.response.headers.add_header('Set-Cookie', "username = ")
        self.response.headers.add_header('Set-Cookie', "password = ")

    def is_owner(self, name):
        """ Checks input name with username stored inside the cookie
            NOTE: User should check_cookie first
        """
        username = self.request.cookies.get("username")
        return True if username == name else False

    def render_not_found(self):
        """ Renders a Not Found page """
        self.render("notFound.html")

    def find_blog_query(self):
        """Takes blog_query_id and parent from the header
            Then looks for it in post.
            If not found, return "None"
        """
        blog_post_id = int(self.request.get('blog_post_id', DEFAULT_POST_ID))

        # Creates a parent query and checks if it exists
        parent_id = int(self.request.get('parent', DEFAULT_POST_ID))
        parent_query = Post.get_by_id(parent_id)
        if parent_query:
            parent_key = parent_query.key
            blog_query = Post.get_by_id(blog_post_id, parent_key)
        else:
            blog_query = Post.get_by_id(blog_post_id)

        return blog_query


class InvalidCookiePage(Handler):
    """Invalid Cookie Page"""
    def get(self):
        """get request that renders the page """
        self.render("invalidCookie.html")


class FrontPage(Handler):
    """Front page that displays the 10 most recent post"""
    def render_front(self):
        """Renders the 10 most recent post"""
        post_query = Post.query(Post.isRoot == True).order(-Post.created).fetch(10)
        self.render("frontPage.html", post_query=post_query)

    def get(self):
        """get request that calls the render_front function"""
        self.render_front()


class CreatePostPage(Handler):
    """ Allows users to post a blog """
    def render_front(self):
        """Method to render sign up page with appropriate values"""
        if not self.check_cookie():
            self.redirect('/invalidCookie')
            return

        self.render("post.html")

    def get(self):
        """ Inital get request """
        self.render_front()

    def post(self):
        """
           post request that takes the submitted information and inserts it
           the Post Kind inside the database
        """
        if not self.check_cookie():
            self.redirect('/invalidCookie')
            return

        username = self.request.cookies.get("username")
        title = self.request.get("title")
        content = self.request.get("content")

        post_obj = Post(author=username, title=title, content=content,
                        isRoot=True)
        post_obj.put()

        blog_query_id = post_obj.key.id()
        query_params = {'blog_post_id': blog_query_id}
        self.redirect('/blogPost?' + urllib.urlencode(query_params))


class SignUpPage(Handler):
    """Page handler that handles user registration"""

    def render_front(self, username="", password="", verifypw="",
                     email="", error_user="", error_pass=""):
        """Method to render sign up page with appropriate values"""
        self.render("sign_up.html", username=username, password=password,
                    verifypw=verifypw, email=email, error_user=error_user,
                    error_pass=error_pass)

    def get(self):
        """Initial get request"""
        self.render_front()

    def post(self):
        """
            Takes in user information, and checks it against the database.
            If valid,
                create the user
            Else,
                return to sign up with the old information and appropriate error
        """
        username = self.request.get("username")
        password = self.request.get("password")
        verifypw = self.request.get("verifypw")
        email = self.request.get("email")
        error_user = ""
        error_pass = ""
        redirect = False

        if username and password and verifypw:
            account_query = Account.get_by_id(username)

            if account_query:
                error_user = "Username Taken"
                redirect = True
            if password != verifypw:
                error_pass = "Passwords do not match"
                redirect = True
        else:
            """
            Taken care of this case with required value in the .html file
            but leaving as redundancy
            """
            redirect = True
            error_user = "Please fill out username and password fields"
            error_pass = ""

        if redirect:
            self.render_front(username, password, verifypw, email, error_user, error_pass)
        else:
            user = Account(id=username, password=hash_str(password), email=email)
            user.put()
            self.set_secure_cookie(username, password)
            self.redirect('/')


class LoginPage(Handler):
    """
        Handler that handles User login and creates cookies for an
        authenticated user
    """
    def render_front(self, username="", password="", error=""):
        """Method to render sign up page with appropriate values"""
        self.render("login.html", username=username, password=password, error=error)

    def get(self):
        """ Inital get method """
        self.render_front()

    def post(self):
        """
            post method that checks if the user is valid against the database
            if the user and password match the database,
                Create a cookie and send user to front page
        """

        username = self.request.get("username")
        password = self.request.get("password")

        if username and password:
            account_query = Account.get_by_id(username)

            if account_query:
                if account_query.password:
                    if account_query.password == hash_str(password):
                        self.set_secure_cookie(username, password)
                        self.redirect('/')

        self.render_front(username, password, "Invalid Username or Password")


class LogoutPage(Handler):
    """
    Takes care of user logout by clearing cookie
    """
    def get(self):
        """Clears cookie and redirects page"""
        self.clear_cooke()
        self.redirect('signup')


class WelcomePage(Handler):
    """
    CURRENTLY UNUSED...PENDING REMOVAL....
    When users login or sign up, this page welcomes then and then redirects them
    Redirection is handled in the meta tag in welcome.html
    """
    def render_front(self):
        """Method to render sign up page with appropriate values"""
        if not self.check_cookie():
            self.redirect('/invalidCookie')
            return

        username = self.request.cookies.get("username")
        self.render("welcome.html", username=username)

    def get(self):
        """get request """
        self.render_front()


class BlogPostPage(Handler):
    """Handles the individaul page for the Blog Post"""

    def render_front(self, blog_query="", comments=""):
        """Displays the blog post and the comments associated with the post"""

        """Query that searches in Post for attributees isRoot and ancestor"""
        comments_query = Post.query(Post.isRoot == False,
                                    ancestor=blog_query.key).order(-Post.created)
        comments = comments_query.fetch(10)
        self.render("blogPost.html", blog_query=blog_query, comments=comments)

    def get(self):
        """ Initial get request """
        blog_post_id = int(self.request.get('blog_post_id', DEFAULT_POST_ID))
        blog_query = Post.get_by_id(blog_post_id)

        if blog_query:
            self.render_front(blog_query)
        else:
            self.render_not_found()

    def post(self):
        """Grabs comment information and associates it with the blog post"""
        if not self.check_cookie():
            self.redirect('/invalidCookie')
            return

        username = self.request.cookies.get("username")
        content = self.request.get("content")

        blog_post_id = int(self.request.get('blog_post_id', DEFAULT_POST_ID))
        blog_query = Post.get_by_id(blog_post_id)

        """Create Post child(this is a comment) on blog_query"""
        post_key = Post(parent=blog_query.key, author=username, content=content)
        post_key.put()

        self.render_front(blog_query)


class EditPostPage(Handler):
    """ Handler that modifies blog post or comments """

    def render_front(self, blog_query="", error=""):
        """Method to render EditPost page"""
        self.render("editPost.html", blog_query=blog_query, error=error)

    def redirect_to_post(self, blog_query):
        """Method to redirect website to a blog post"""
        parent_id = self.request.get("parent")

        if parent_id:
            query_params = {'blog_post_id': parent_id}
        else:
            blog_query_id = blog_query.key.id()
            query_params = {'blog_post_id': blog_query_id}
        self.redirect('/blogPost?' + urllib.urlencode(query_params))

    def get(self):
        """
            Get method that checks if user CAN edit the page
            and if so, renders form to do so
        """
        if not self.check_cookie():
            self.redirect('/invalidCookie')
            return

        blog_query = self.find_blog_query()

        if blog_query:
            if self.is_owner(blog_query.author):
                self.render_front(blog_query)
            else:
                self.render_front(blog_query, "You are not the owner")
        else:
            self.render_not_found()

    def post(self):
        """Checks if user owns post, and if so, updates the post"""
        if not self.check_cookie():
            self.redirect('/invalidCookie')
            return

        blog_query = self.find_blog_query()

        if blog_query:
            if self.is_owner(blog_query.author):
                blog_query.title = self.request.get("title")
                blog_query.content = self.request.get("content")
                blog_query.put()

                self.redirect_to_post(blog_query)

            else:
                self.render_front(blog_query, "You are not the owner")
        else:
            self.render_not_found()


class DeletePostPage(Handler):
    """ Handler that allows user to delete post """

    def render_front(self, blog_query="", error=""):
        """Method that renders DeletePostPage"""
        self.render("deletePost.html", blog_query=blog_query, error=error)

    def get(self):
        """Method that finds the appropriate blog and renders it"""
        if not self.check_cookie():
            self.redirect('/invalidCookie')
            return

        blog_query = self.find_blog_query()

        if blog_query:
            if self.is_owner(blog_query.author):
                self.render_front(blog_query)
            else:
                self.render_front(blog_query, "You are not the owner")
        else:
            self.render_not_found()

    def post(self):
        """
            Checks to see if user wants to delete post.
            If response is yes,
                delete the page
            Otherwise,
                Redirect to old page
        """
        if not self.check_cookie():
            self.redirect('/invalidCookie')
            return

        blog_query = self.find_blog_query()
        response = int(self.request.get('q1'))

        if blog_query:
            if self.is_owner(blog_query.author) and (response == 1):
                blog_query.key.delete()
                self.redirect("/")
            elif self.is_owner(blog_query.author) and (response == 0):
                self.render_front(blog_query, "Post remains intact!")
            else:
                self.render_front(blog_query, "You are not the owner")
        else:
            self.render_not_found()


class VotePage(Handler):
    """Handler that creates or updates Vote entities"""

    def decide_value(self, value):
        """Method that determines appropriate value"""
        value = int(value)

        return 1 if value>=1 else -1

    def get(self):
        """
            Get request(not really, it's a hack) to allow users to vote
            This method creates a Vote entity if the user has not previous voted
            on a post or comment
            If the user has already voted, this method updates the Vote entity
            already in the database
        """

        if not self.check_cookie():
            self.redirect('/invalidCookie')
            return

        blog_query = self.find_blog_query()
        parent_id = self.request.get("parent")
        voter = self.request.cookies.get("username")
        value = self.request.get("value")

        if value:
            value = self.decide_value(value)

        if blog_query:
            vote_query = Vote.query(Vote.post == blog_query.key, Vote.user_id == voter).get()
            if vote_query:
                self.write(vote_query.value)
                if vote_query.value != value:
                    vote_query.value = value
                    #Mulitply by 2 to undo previous action
                    blog_query.likes += (2 * value)
            else:
                vote_query = Vote(post=blog_query.key, user_id=voter, value=value)
                blog_query.likes += value
            vote_query.put()
            blog_query.put()

            if parent_id:
                query_params = {'blog_post_id': parent_id}
            else:
                blog_query_id = blog_query.key.id()
                query_params = {'blog_post_id': blog_query_id}
            self.redirect('/blogPost?' + urllib.urlencode(query_params))

        self.render_not_found()


app = webapp2.WSGIApplication([('/', FrontPage),
                               ('/signup', SignUpPage),
                               ('/invalidCookie', InvalidCookiePage),
                               ('/login', LoginPage),
                               ('/welcome', WelcomePage),
                               ('/logout', LogoutPage),
                               ('/createPost', CreatePostPage),
                               ('/blogPost', BlogPostPage),
                               ('/editPost', EditPostPage),
                               ('/deletePost', DeletePostPage),
                               ("/vote", VotePage),
                              ],
                              debug=True)
