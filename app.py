from flask import Flask, render_template, request, redirect, url_for, flash, abort, session, jsonify
import json 
import os.path
from werkzeug.utils import secure_filename
import random
from random import randint
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.secret_key = 'jkdfhjieraidfau'

class LoginForm(FlaskForm):
    roomName = StringField("Room Name", validators=[DataRequired()])
    roomPassword = PasswordField("Room Password", validators=[DataRequired()])
    playerName = StringField("Player Name", validators=[DataRequired()])
    submit = SubmitField("Login")



class RegisterForm(FlaskForm):
    roomName = StringField("Room Name", validators=[DataRequired()])
    roomPassword = PasswordField("Room Password", validators=[DataRequired()])
    submit = SubmitField("Create Room")

data = []
my_room = {}
cards_name = {}
cards_name[1] = "skip"
cards_name[2] = "attack"
cards_name[3] = "see the future"
cards_name[4] = "pikachu"
cards_name[5] = "doremon"
cards_name[6] = "favor"
cards_name[7] = "shuffle"
cards_name[8] = "rainbow"
cards_name[9] = "defuse"
cards_name[0] = "bomb"
cards_name[10] = "nope"

cards = []
for i in range(5):
    cards.append(1)
    cards.append(2)
    cards.append(3)
    cards.append(4)
    cards.append(5)
    cards.append(6)
    cards.append(7)
    cards.append(8)
    cards.append(10)

plist = []
random.shuffle(cards)

cp_cards = cards

for i in range(6):
    cp_cards.append(0)

random.shuffle(cp_cards)


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/api")
def api():
    if os.path.exists('data.json'):
        with open('data.json') as data_file:
            data = json.load(data_file)
    return jsonify(data)

@app.route("/delete/")
@app.route("/delete/<string:idx>")
def delete(idx=None):
    data = []
    if idx==None:
        if os.path.exists('data.json'):
            with open('data.json', 'w') as data_file:
                json.dump(data, data_file)
        return jsonify(data)
    else:
        if os.path.exists('data.json'):
            with open('data.json') as data_file:
                data = json.load(data_file)
            copy_data = data
            for room in data:
                if room["roomId"] == idx: 
                    copy_data.remove(room)
            with open('data.json', 'w') as data_file:
                json.dump(copy_data, data_file)
            return jsonify(copy_data)


@app.route("/login", methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if os.path.exists('data.json'):
            with open('data.json') as data_file:
                data = json.load(data_file)
        copy_data = data 
        for i in range(len(data)):
            if data[i]["roomName"]==form.roomName.data and data[i]["roomPassword"]==form.roomPassword.data:
                p_cards = []
                c = 1
                for j in range(7):
                    p_cards.append(cards_name[c])
                    c = c + 1

                p_cards.append(cards_name[9])
                random.shuffle(p_cards)

                p = {}
                l = len(data[i]["playerList"])
                if l > 5 :
                    flash("only 5 members allowed at a time in a room ", "success")
                    return render_template('home.html')

                if data[i]["active"]:
                    flash("Game has already started!! Wait for end. ", "danger")
                    return render_template("home.html")

                p["pid"] = len(data[i]["playerList"])
                p["playerName"] = form.playerName.data
                p["cards"] = p_cards

                session["player"] = p
                session["roomName"] = form.roomName.data

                copy_data[i]["playerList"].append(p)

                if not bool(copy_data[i]["curr_player"]):
                    copy_data[i]["curr_player"] = p

                with open('data.json', 'w') as data_file:
                    json.dump(copy_data, data_file)
                my_room = copy_data[i]

                return render_template('show_players.html', data=copy_data[i]["playerList"])

        flash("Room doesn't exists", "success")
        return render_template('home.html')

    return render_template('login.html', form=form, login=True)


@app.route("/register", methods=['POST', 'GET'])
def register():
    d = {}
    form = RegisterForm()
    if form.validate_on_submit():
        d["roomId"] = random.randint(100, 999)
        d["roomPassword"] = form.roomPassword.data
        d["roomName"] = form.roomName.data
        d["playerList"] = []
        d["roomCards"] = cp_cards
        d["curr_player"] = {}
        d["pending"] = 0
        d["active"] = False
        d["message"] = ""
        if os.path.exists('data.json'):
            with open('data.json') as data_file:
                data = json.load(data_file)
        for room in data:
            if room["roomName"] == d["roomName"]:
                flash("Room already exists !! ", "danger")
                return redirect('register')
        data.append(d)        
        with open('data.json', 'w') as data_file:
            json.dump(data, data_file)
        flash("Room Created successfully !! ", "success")
        return render_template('home.html')

    return render_template('register.html', form=form, register=True)

@app.route("/show_players")
def show_players():
    plist = []
    curr_player = {}
    index = 0
    if os.path.exists('data.json'):
        with open('data.json') as data_file:
            data = json.load(data_file)
            for i in range(len(data)):
                if data[i]["roomName"] == session["roomName"]:
                    plist = data[i]["playerList"]
                    curr_player = data[i]["curr_player"]
                    index = i

    if request.args.get("refresh")=="refresh":
        return render_template('show_players.html', data=plist)

    elif request.args.get("start0")=="start0":
        if session["player"]["pid"] == curr_player["pid"]:
            return render_template("dashboard.html", players=session["player"], waiting=False)
        else:
            return render_template("dashboard.html", players=session["player"], waiting=True)

    return render_template('show_players.html', data=plist)


@app.route("/dashboard")
def dashboard():

    index = 0
    plist = []
    curr_player = {}
    if os.path.exists('data.json'):
        with open('data.json') as data_file:
            data = json.load(data_file)
            for i in range(len(data)):
                if data[i]["roomName"] == session["roomName"]:
                    plist = data[i]["playerList"]
                    curr_player = data[i]["curr_player"]
                    index = i

    copy_data = data
    copy_data[index]["active"] = True

    if data[index]["message"]!="":
        flash(data[index]["message"], "danger")
        copy_data[index]["message"] = ""

    for i in range(len(plist)):
        if plist[i]["pid"]==session["player"]["pid"]:
            session["player"] = plist[i]

    if request.args.get("refresh")=="refresh":
        if session["player"]["pid"] == curr_player["pid"]:
            return render_template("dashboard.html", players=session["player"], waiting=False)
        else:
            return render_template("dashboard.html", players=session["player"], waiting=True)

    l = len(plist)  
    if l==1:
        for room in data:
            if room["roomName"] == session["roomName"]: 
                copy_data.remove(room)
        with open('data.json', 'w') as data_file:
            json.dump(copy_data, data_file)

        if session["player"]["playerName"]==curr_player["playerName"]:
            session["roomName"] = False
            session["player"] = False
        return render_template('message.html',won=True, name=curr_player["playerName"])

    if request.args.get("submit_btn")=="submit_0":
        r =  copy_data[index]["roomCards"].pop()
        if len(data[index]["roomCards"])==0:
            copy_data[index]["roomCards"] = cp_cards
        if r == 0:
            name = curr_player["playerName"]
            if cards_name[9] in curr_player["cards"]:
                curr_player["cards"].remove(cards_name[9])
                if session["player"]["pid"]==curr_player["pid"]:
                    session["player"]["cards"] = curr_player["cards"]
                for i in range(len(data[index]["playerList"])):
                    if curr_player["pid"] == data[index]["playerList"][i]["pid"]:
                        copy_data[index]["playerList"][i]["cards"] = curr_player["cards"]
                flash("You just saved your life! " + name, "danger")
            else:
                plist.remove(curr_player)
                l = len(plist)
                curr_player = plist[0]
                if session["player"]["playerName"]==name:
                    session["roomName"] = False
                    session["player"] = False

                copy_data[index]["playerList"] = plist
                copy_data[index]["curr_player"] = curr_player
                with open('data.json', 'w') as data_file:
                    json.dump(copy_data, data_file)

                return render_template("message.html" ,won=False, name=name) 
        else:
            curr_player["cards"].append(cards_name[r])
            for i in range(len(data[index]["playerList"])):
                if curr_player["pid"] == data[index]["playerList"][i]["pid"]:
                    copy_data[index]["playerList"][i]["cards"].append(cards_name[r])

        session["player"] = curr_player

        if data[index]["pending"] > 0:
            copy_data[index]["pending"] = data[index]["pending"] - 1
            with open('data.json', 'w') as data_file:
                json.dump(copy_data, data_file)
            return render_template('dashboard.html', players=session["player"], waiting=False)

        copy_data[index]["curr_player"] = copy_data[index]["playerList"][(curr_player["pid"] + 1)%l]
        with open('data.json', 'w') as data_file:
            json.dump(copy_data, data_file)

    elif request.args.get("submit_btn")=="submit_1":
        card = request.args.get("myDroppedCard")
        if request.args.get("myDroppedCard")== cards_name[1] or request.args.get("myDroppedCard")== cards_name[10]:
            for i in range(len(data[index]["playerList"])):
                if curr_player["pid"] == data[index]["playerList"][i]["pid"]:
                    copy_data[index]["playerList"][i]["cards"].remove(card)

            curr_player["cards"].remove(card)
            session["player"] = curr_player
            copy_data[index]["curr_player"] = copy_data[index]["playerList"][(curr_player["pid"] + 1)%l]

        elif request.args.get("myDroppedCard")==cards_name[2]: 
            for i in range(len(data[index]["playerList"])):
                if curr_player["pid"] == data[index]["playerList"][i]["pid"]:
                    copy_data[index]["playerList"][i]["cards"].remove(cards_name[2])

            copy_data[index]["pending"] = data[index]["pending"] + 1
            curr_player["cards"].remove(cards_name[2])
            session["player"] = curr_player
            copy_data[index]["curr_player"] = copy_data[index]["playerList"][(curr_player["pid"] + 1)%l]

        elif request.args.get("myDroppedCard")==cards_name[3]:
            for i in range(len(data[index]["playerList"])):
                if curr_player["pid"] == data[index]["playerList"][i]["pid"]:
                    copy_data[index]["playerList"][i]["cards"].remove(cards_name[3])

            curr_player["cards"].remove(cards_name[3])
            session["player"] = curr_player
            last = []
            totalCards = data[index]["roomCards"]
            if len(totalCards) < 3:
                for i in range(len(totalCards)-1, -1, -1):
                    last.append(totalCards[i])
            else:
                last.append(totalCards[len(totalCards)-1])
                last.append(totalCards[len(totalCards)-2])
                last.append(totalCards[len(totalCards)-3])
            message = ""
            l = 1
            for i in last:
                message = message + "card " + str(l) + cards_name[i] + ", "
                l += 1
            flash("Your last 3 cards are : "+message, "success")
            with open('data.json', 'w') as data_file:
                json.dump(copy_data, data_file)

            return render_template('dashboard.html', players=session["player"], waiting=False)
            
        elif request.args.get("myDroppedCard")==cards_name[7]:
            for i in range(len(data[index]["playerList"])):
                if curr_player["pid"] == data[index]["playerList"][i]["pid"]:
                    copy_data[index]["playerList"][i]["cards"].remove(cards_name[7])    

            curr_player["cards"].remove(cards_name[7])
            session["player"] = curr_player

            random.shuffle(copy_data[index]["roomCards"])
            flash("Card shuffled well now !!", "success")
            with open('data.json', 'w') as data_file:
                json.dump(copy_data, data_file)

            return render_template('dashboard.html', players=session["player"], waiting=False)

        elif request.args.get("myDroppedCard")==cards_name[6]:
            for i in range(len(data[index]["playerList"])):
                if curr_player["pid"] == data[index]["playerList"][i]["pid"]:
                    copy_data[index]["playerList"][i]["cards"].remove(cards_name[6])    

            curr_player["cards"].remove(cards_name[6])
            session["player"] = curr_player

            with open('data.json', 'w') as data_file:
                json.dump(copy_data, data_file)

            return render_template('favor.html', players=session["player"], playersList=plist)

        elif request.args.get("myDroppedCard")==cards_name[5] or request.args.get("myDroppedCard")==cards_name[4] or request.args.get("myDroppedCard")==cards_name[8]:
            card = request.args.get("myDroppedCard")
            for i in range(len(data[index]["playerList"])):
                if curr_player["pid"] == data[index]["playerList"][i]["pid"]:
                    c=copy_data[index]["playerList"][i]["cards"].count(card)
                    if c==2:
                        copy_data[index]["playerList"][i]["cards"].remove(card)
                        copy_data[index]["playerList"][i]["cards"].remove(card)    
                        curr_player["cards"].remove(card)
                        curr_player["cards"].remove(card)
                        with open('data.json', 'w') as data_file:
                            json.dump(copy_data, data_file)
                        session["players"] = curr_player
                        return render_template('favor.html', players=session["players"], playersList=plist, value3=False)
                    elif c>=3:
                        copy_data[index]["playerList"][i]["cards"].remove(card)
                        copy_data[index]["playerList"][i]["cards"].remove(card) 
                        copy_data[index]["playerList"][i]["cards"].remove(card)       
                        curr_player["cards"].remove(card)
                        curr_player["cards"].remove(card)
                        curr_player["cards"].remove(card)
                        with open('data.json', 'w') as data_file:
                            json.dump(copy_data, data_file)
                        session["players"] = curr_player
                        return render_template('favor.html', players=session["players"], playersList=plist, value3=True)
                    else:
                        flash("Not able to perform action, change card !!", "danger")   

            return render_template('dashboard.html', players=session["player"], waiting=False)

    with open('data.json', 'w') as data_file:
        json.dump(copy_data, data_file)

    return render_template('dashboard.html', players=session["player"], waiting=True)


@app.route("/favor")
def favor():
    index = 0
    plist = []
    curr_player = {}
    if os.path.exists('data.json'):
        with open('data.json') as data_file:
            data = json.load(data_file)
            for i in range(len(data)):
                if data[i]["roomName"] == session["roomName"]:
                    plist = data[i]["playerList"]
                    curr_player = data[i]["curr_player"]
                    index = i

    copy_data = data
    if request.args.get("favor")=="favor":
        selected_player_name = None
        card = request.args.get("mySelectedCard")
        for i in range(len(plist)):
            if plist[i]["playerName"] == request.args.get("mySelectedPlayer"):
                
                if card:
                    if card in plist[i]["cards"]:
                        copy_data[index]["playerList"][i]["cards"].remove(card)
                    else:
                        flash("Your card not found !! ", "danger")
                        card = None

                elif cards_name[7] in plist[i]["cards"]:
                    card = cards_name[7]
                    copy_data[index]["playerList"][i]["cards"].remove(cards_name[7])
                elif cards_name[6] in plist[i]["cards"]:
                    card = cards_name[6]
                    copy_data[index]["playerList"][i]["cards"].remove(cards_name[6])
                elif cards_name[8] in plist[i]["cards"]:
                    card = cards_name[8]
                    copy_data[index]["playerList"][i]["cards"].remove(cards_name[8])
                elif cards_name[5] in plist[i]["cards"]:
                    card = cards_name[5]
                    copy_data[index]["playerList"][i]["cards"].remove(cards_name[5])
                elif cards_name[4] in plist[i]["cards"]:
                    card = cards_name[4]
                    copy_data[index]["playerList"][i]["cards"].remove(cards_name[4])
                elif cards_name[3] in plist[i]["cards"]:
                    card = cards_name[3]
                    copy_data[index]["playerList"][i]["cards"].remove(cards_name[3])
                elif cards_name[2] in plist[i]["cards"]:
                    card = cards_name[2]
                    copy_data[index]["playerList"][i]["cards"].remove(cards_name[2])
                else:
                    card = cards_name[1]
                    copy_data[index]["playerList"][i]["cards"].remove(cards_name[1])
                selected_player_name = plist[i]["playerName"]


        if card:
            for i in range(len(plist)):
                if plist[i]["playerName"] == curr_player["playerName"]:
                    copy_data[index]["playerList"][i]["cards"].append(card)
                    curr_player["cards"].append(card) 
            if selected_player_name:
                copy_data[index]["message"] = "Player " + curr_player["playerName"] + " take " + selected_player_name + " 's card "+card

        session["player"] = curr_player
        with open('data.json', 'w') as data_file:
            json.dump(copy_data, data_file)

        return render_template("dashboard.html", players=session["player"], waiting=False)
    return render_template("favor.html")


if __name__ == '__main__':
    app.run(debug=True)


