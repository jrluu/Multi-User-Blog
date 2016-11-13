#Multi User Blog

##Description

In this project, I created a website that allows you to register for an account,
 post a blog, comment on blog posts, and upvote/downvote them.

In order to create this website, I took advantage of Google Cloud app engine, which allows its users to rapidly deploy scalable web applications and mobile backends. To store the users and blog posts, I used Google's Cloud storage, a NoSQL database, because Google Cloud can easily add more nodes and automatically load balance stress between the nodes, allowing me to scale up as the userbase grows. To ensure that a user can stay signed into the blog, I implemented a session cookie that contains the username and the password, which is securely hashed to slow down a rainbow table attack.

##How to deploy

##Technologies Used  
* [Google Cloud](https://cloud.google.com/)   
* [Google Cloud Storage(NoSQL)](https://cloud.google.com/storage/)  
* [Python 2.7] (https://www.python.org/download/releases/2.7/)
* [Jinja2](http://jinja.pocoo.org/docs/dev/)
* Hash Encryption
* Cookies

##For more information
Please contact me at jrluu@ucdavis.edu
