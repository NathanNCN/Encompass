## imported libraries
import pathlib
import cachecontrol
import google.auth.transport.requests
from flask import Flask, render_template, request, redirect, session, request, abort
from google.oauth2 import id_token
from pymongo import MongoClient
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import os
import requests
from datetime import datetime
import random
from dotenv import load_dotenv
import json

## Load environment variables
load_dotenv()


## Load and connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["Encompass"]
user_db = db["Users"]
flash_library_db = db["Flashcards"]
goals_db = db["Goals"]
calender_db = db["Calender"]


## Flask setup and google authentication
app = Flask(__name__)
app.secret_key = os.getenv('app.secret_key')


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "/etc/secrets/client_secret.json")
flow = Flow.from_client_secrets_file(client_secrets_file=client_secrets_file,
                                     scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
                                     redirect_uri = 'http://127.0.0.1:5000/callback')


## app route to login page
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login')
def login():

    ## create url to application and save state
    authorization_url, state = flow.authorization_url()
    session['state'] = state
    return redirect(authorization_url)
@app.route('/callback')
def callback():
    ## collect current state
    flow.fetch_token(authorization_response = request.url)\

    ##determine if the user has logged in
    if not session['state'] == request.args['state']:
        abort(500)

    ## Collect user google information
    credential = flow.credentials
    request_session = requests.Session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)
    id_info = id_token.verify_oauth2_token(
        id_token = credential._id_token,
        request = token_request,
        audience = GOOGLE_CLIENT_ID
    )

    ## Collect important user Data
    user_name = id_info.get('name')
    user_email = id_info.get('email')

    ## Create a new log in user_db if user is not found in user_db
    if user_db.find_one({"Name": user_name, "Email": user_email}) is None:
        user_db.insert_one({"Name": user_name, "Email": user_email})

    ## Update session with current user information
    session["flashcard_set"] = ""
    session['google_id'] = id_info.get('sub')
    session['name'] = id_info.get('name')
    session["email"] = id_info.get('email')

    ## redirect to home
    return redirect("/home")


## Homepage for Encompass
@app.route('/home')
def home():
    return render_template("index.html")

## Page for timer
@app.route('/timer')
def timer():
    return render_template("timer.html")

## page flashLibrary
@app.route('/flash-library')
def flashLibrary():

    ## collect users information via session
    current_user = session["email"]
    flashcard_db = db["Flashcards"]

    ## create a list of all current flashcard user has in flashcard_db
    list_of_flashcards = [flashcard['Set_Name'] for flashcard in flashcard_db.find({"Email": current_user}) ]

    ## load html with list of flashcards
    return render_template('flash_library.html', data = list_of_flashcards )


@app.route('/create-new-set', methods=['Post', 'Get'])
def createNewSet():

    ## check if method was post
    if request.method == 'POST':

        ## Collect request from data and convert into variables
        values = list(request.form)
        title = request.form[values[0]]
        keys = values[1:]
        dict_of_values = {}

        ## loop through request form collecting input term and defintion
        for i in range(0, len(keys), 2):
            if i+1 < len(keys):
                term = request.form[keys[i]]
                definition = request.form[keys[i + 1]]

                ## add term and definition to dict_of_values
                dict_of_values[term] = definition

        ## Update flashcard database with users new flashcard set
        flash_library_db.insert_one({
            "Email": session['email'],
            "Set_Name": title,
            "Terms": dict_of_values
        })
        return redirect('/flash-library')
    else:
        ## load flashcard create
        return render_template('flash_card_add.html')


@app.route('/card', methods = ["Post", "Get"])
def card():

    ## check if request was a post
    if request.method == "POST":
        
        ## determine if secret key is in request form
        if "RemoveThisSet#$#_129Kqaoe_982AmcAA1((**//10" in list(request.form.keys())[0]:
            
            ## remove set from flashcard database
            flash_library_db.delete_one(
                {"Email": session['email'],
                 
                 ## removes secret key from request form
                 "Set_Name": list(request.form.keys())[0].replace("RemoveThisSet#$#_129Kqaoe_982AmcAA1((**//10", "")})
            return redirect("/flash-library")
        else:
            ## collect the current flashcart set
            session["flashcard_set"] = list(request.form.keys())[0]
            
            ## collect a random pair 
            term = getRandomTerm()
            
            ## open html file with the random pair
            return render_template("card.html", data=term)

    else:
        return render_template("card.html", data = getRandomTerm())

def getRandomTerm():
    
    ## collect current flashcard set's terms and definition pairs 
    terms = flash_library_db.find_one({"Email": session["email"],
                                       "Set_Name": session["flashcard_set"]})["Terms"]
    ## get list of keys and select a random one
    keys = list(terms.keys())
    random_key = random.choice(keys)
    
    ## return term and definition 
    term = [random_key, terms[random_key]]
    return term

@app.route('/goalsetter', methods = ["POST", "GET"])
def GoalSetter():
    
    ## check if request was a poset
    if request.method == "POST":
        
        ## collect goal that was inputted 
        goal = request.form["value"]
        
        ## update goals database with new goal  
        goals_db.update_one(
            {"Email": session["email"]},
            {"$push": {"Goals": goal}},
            upsert=True
        )
        
        ## load newly updated database
        goals = goals_db.find_one({"Email": session["email"]})["Goals"]
        
        ## load html with new data
        return render_template('goalSetter.html', GoalList=goals)

    else:
        
        ## get user in goals database
        goals = goals_db.find_one({"Email": session["email"]})
        
        ## check if user has created zero goals
        if goals is None:
            ## open html with no data
            return render_template('goalSetter.html', GoalList=[])
        else:
            ## open html with data
            return render_template('goalSetter.html', GoalList = goals["Goals"])

@app.route('/remove_goal', methods=["Post"])
def removeGoal():
    
    ## collect corresponding index of removed goal 
    index = int(list(request.form.keys())[0])

    ## get list of current goals
    goals = goals_db.find_one({"Email": session["email"]})["Goals"]

    ## remove goal at index
    goals.pop(index)

    ## update goals database
    goals_db.update_one(
        {"Email": session["email"]},
        {"$set": {"Goals": goals}}
    )
    
    return redirect("/goalsetter")

@app.route("/calender", methods=["Post","Get"])
def calender():

    ## check if request was a post
    if request.method=="POST":

        ## collect information
        values = request.form
        keys = list(request.form.keys())

        ## Update calender database
        calender_db.update_one(
            {"Email": session["email"]},
            {"$push": {"task": [values[keys[0]], values[keys[1]]]}},
            upsert=True
        )

        ## sort the task in database by date
        sorted_task = dateSorter(calender_db.find_one({"Email": session['email']})["task"])

        ## update data base with sorted task
        calender_db.update_one(
            {"Email": session["email"]},
            {"$set": {"task": sorted_task}},
        )

        ## collect task and render html
        tasks = calender_db.find_one({"Email": session["email"]})["task"]
        return render_template('calender.html', tasks=tasks)
    else:

        ## collect task
        tasks = calender_db.find_one({"Email": session["email"]})

        ##check if user has zero task
        if tasks is None:
            return render_template('calender.html', tasks=[])

        else:
            return render_template('calender.html', tasks=tasks["task"])

@app.route('/remove_task', methods=["Post"])
def removeTask():

    ## collect index of task
    index = int(list(request.form.keys())[0])
    new_tasks = calender_db.find_one({"Email": session["email"]})["task"]

    ## pop item at index off calender database
    new_tasks.pop(index)

    ## update calender database
    calender_db.update_one(
        {"Email": session["email"]},
        {"$set": {"task": new_tasks}}
    )

    return redirect("/calender")



def dateSorter(listOfDates):

    ## loop through the list of dates
    ## convert data into correct format
    ## then sort by date
    return sorted(listOfDates, key=lambda x: datetime.strptime(x[0], "%Y-%m-%d"))

if __name__ == "__main__":
    app.run(debug=True,hosts= "0.0.0.0", port=5000)
