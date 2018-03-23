from flask import Flask, jsonify, request
from httplib2 import Http
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from db_setup import Users, Posts, Base

engine = create_engine('sqlite:///Ofaly.db')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)


# get list of saved users from database
@app.route('/users/')
@app.route('/users/param')
def usersPage():
    users = [i.serialize for i in session.query(Users).all()]
    page = int(request.args.get('page', 0))
    user_id = ""
    link = 'localhost:5000/users%s/param?page=%s'
    return paginate(users, page, user_id, link)


# get info about each user
@app.route("/users/<string:user_id>/")
@app.route('/users/<string:user_id>/param/')
def userPage(user_id):
    if request.args.get('local') == 'true':
        return jsonify(session.query(Users).filter_by(id=user_id).one().serialize)
    user = getUser(user_id)
    tmp = session.query(Users).filter_by(id=user_id).first()
    if tmp:
        tmp.name = user['name']
        tmp.id = user['id']
    else:
        tmp = Users(name=user['name'], id=user['id'])
    session.add(tmp)
    session.commit()
    return jsonify(tmp.serialize)


def getUser(user_id):
    h = Http()
    access_token = '446784265754696|lnphcrCeWOk0mDbMS0b_54gRErg'
    url = "https://graph.facebook.com/v2.12/%s?access_token=%s" % (
        user_id, access_token)
    response, content = h.request(url, 'GET')
    return json.loads(content.decode())


@app.route('/users/<string:user_id>/posts/')
@app.route('/users/<string:user_id>/posts/param')
def postsPage(user_id):
    if request.args.get('local') == 'true':
        return jsonify(posts=[i.serialize for i in session.query(Posts).filter_by(user_id=user_id).all()])
    try :
    	posts = getPosts()
    except KeyError:
   		return jsonify(error="access_token expired, contact : Karim.Tawfik17@gmail.com")
    try:
        latest_post_id = session.query(
            Posts).filter_by(user_id=user_id).first().id
    except:
        latest_post_id = -1

    new_posts = []
    count = 0
    for post in posts:
        if post['id'] == latest_post_id:
            break
            count += 1

        try:
            tmp = Posts(date=post['created_time'].split('T')[0], id=post['id'],
                        text=post['message'], user_id=user_id)
        except KeyError:
            pass
        new_posts.append(tmp)
        if latest_post_id == -1:
            session.add(tmp)
    session.commit()
    j = 0
    for i in session.query(Posts).filter_by(user_id=user_id).limit(count):
        i.id = new_posts[j].id
        i.date = new_posts[j].date

        i.text = new_posts[j].text
        session.add(i)
    session.commit()
    result = [i.serialize for i in session.query(
        Posts).filter_by(user_id=user_id).all()]
    page = int(request.args.get('page', 0))
    link = 'localhost:5000/users/%s/posts/param?page=%s'
    return paginate(result, page, user_id, link)


def getPosts(limit=25):
    h = Http()
    #this access_token might be expired ,, contact me for another one
    access_token = 'EAACEdEose0cBAKgVNw6Ibi6oxR6E4DshpDLYfTttUPY0iZC8wGrWPTi9k3V82ZBmWCet1ZAoO6OZChZBubIgqZA9ThsSeCXimSNGgZAWQM5X5jyp6VRStAP8eFWKZCEOxB3hXE8oJpHiVOTWHibLKYN9LLddvLIwOGFAlmwj0OcO0OA9kpZAZAIBZCzkqtZAI0cZAlKvCXGcv0GKQ8i0PhBXg7ZA8gUZAOSFxINyZBYZD'
    url = "https://graph.facebook.com/v2.12/me?fields=posts.limit(%s)&access_token=%s" % (limit,
                                                                                          access_token)
    response, content = h.request(url, 'GET')
    data = json.loads(content.decode())
    return data["posts"]["data"]


def paginate(result, page, user_id, link):
    return jsonify(results=result[page * 5:(page * 5 + 5)], pagination={'next_page': link % (user_id, str(page + 1)), 'prev_page': link % (user_id, str(page - 1))})


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
