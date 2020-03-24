import os
import datetime
from flask import Flask, render_template, request, redirect, jsonify
from flask_socketio import SocketIO, emit
from models import *


# Configure flask app, socketio
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# Configure and initailise db - DATABASE_URL=postgres://wgfjftevfzhdct:89abb1c9f9fe4dd0c6e447c1baa97cd91387d5f8185681a77a137aea5123002f@ec2-54-247-72-30.eu-west-1.compute.amazonaws.com:5432/dtec51jksolrh
try:
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
except:
    print('Export DATABASE_URL')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Initialise socketio
socketio = SocketIO(app)

@app.route("/")
def index():
    # Query db for all channels and return to page
    channels = Channel.query.order_by(Channel.lastactive.desc()).all()

    # Compare date of last active column to see if last message sent today
    datenow = str(datetime.datetime.now().date())
    for channel in channels:
        lastactive = channel.lastactive[0:10]

        # If last message sent today trim off the date to show time of last message sent only
        if lastactive == datenow:
            channel.lastactive = channel.lastactive[10:-3]
        else:
            # Trim off seconds, only show hours:minutes
            channel.lastactive = channel.lastactive[:-3]

    return render_template("index.html", channels=channels)

@app.route("/newchannel", methods=["GET", "POST"])
def newchannel():
    # If new channel form submitted using post method
    if request.method == "POST":
        name = request.form.get("name")
        displayname = request.form.get("displayname")
        timedate = str(datetime.datetime.now())[:-7]
        # Check field not blank
        if len(name) < 1:
            msg = "Please enter the conversation topic"
            return render_template("newchannel.html", msg=msg)

        # Query db to see if any conversations with the name already exist
        rows = Channel.query.filter_by(topic=name).all()

        if len(rows) != 0:
            msg= "There already exists a conversation with this name"
            return render_template("newchannel.html", msg=msg)

        # # Insert new conversation into db
        try:
            channel = Channel(topic=name, creator=displayname,timedate=timedate, lastactive=timedate)
            db.session.add(channel)
            db.session.commit()
        except:
            msg = "Could not create channel at this time"
            return render_template("newchannel.html", msg=msg)

        rows = Channel.query.filter_by(topic=name).first()
        id = str(rows.id)

        return redirect("/channel/" + id)
    # If user arrived here via. get request then display newchannel page form
    else:
        return render_template("newchannel.html")

@app.route("/channel/<string:id>")
def channel(id):
    if not id:
        return redirect("/index")
    channel = Channel.query.filter_by(id=id).first()
    msgs = Comment.query.filter_by(channel=id).order_by(Comment.timedate).all()

    deleteoldest(id)
    return render_template("channel.html", msgs=msgs, channel=channel)


@socketio.on('send')
def send(data):
    # Add message to comments database
    try:
        timedate = str(datetime.datetime.now())[:-7]
        msg = Comment(comment=data["msg"], poster=data['name'],timedate=timedate, channel=data['id'])

        db.session.add(msg)

        # Update last active column of channel in conversations table
        lastactive = timedate
        channel = Channel.query.get(msg.channel)
        channel.lastactive = lastactive

        # commit changes
        db.session.commit()


    # If error emit error message only to sender
    except:
        emit('error', broadcast=False)
    # add msgid to data dictionary
    data['msgid'] = msg.id

    # If message successfully saved to db broadcast the message
    emit('receive', data, broadcast=True)

@app.route('/recalldelete', methods=["POST"])
def recalldelete():
    id = request.form.get("id")
    action = request.form.get("action")

    try:
        comment = Comment.query.get(id)

        if action == 'recall':
            comment.comment = 'Message recalled'
            db.session.commit()
        else:
            comment.comment = 'Message deleted'
            db.session.commit()
    except:
        return jsonify({'success': False})

    return jsonify({'success': True})

# deletes oldest comment in comment table if there are more than 100 comments
def deleteoldest(id):
    rows = Comment.query.filter_by(channel=id).count()
    while rows > 100:
        comment = Comment.query.filter_by(channel=id).first()
        db.session.delete(comment)
        db.session.commit()
        rows -= 1
