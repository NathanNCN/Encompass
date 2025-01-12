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
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["Encompass"]
user_db = db["Users"]
flash_library_db = db["Flashcards"]
goals_db = db["Goals"]
calendar_db = db["calendar"]


## Flask setup and Google authentication
app = Flask(__name__)
app.secret_key = os.getenv('app.secret_key')


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "/etc/secrets/client_secret.json")
flow = Flow.from_client_secrets_file(client_secrets_file=client_secrets_file,
                                     scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
                                     redirect_uri = os.getenv('callBack'))


## App route to login page
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login')
def login():

    ## Create url to application and save state
    authorization_url, state = flow.authorization_url()
    session['state'] = state
    return redirect(authorization_url)
@app.route('/callback')
def callback():
    ## Collect current state
    flow.fetch_token(authorization_response = request.url)\

    ## Determine if the user has logged in
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

    ## Create a new login user_db if user is not found in user_db
    if user_db.find_one({"Name": user_name, "Email": user_email}) is None:
        user_db.insert_one({"Name": user_name, "Email": user_email})

    ## Update session with current user information
    session["flashcard_set"] = ""
    session['google_id'] = id_info.get('sub')
    session['name'] = id_info.get('name')
    session["email"] = id_info.get('email')

    ## Redirect to home
    return redirect("/home")


## Homepage for Encompass
@app.route('/home')
def home():
    return render_template("index.html")

## Page for timer
@app.route('/timer')
def timer():
    return render_template("timer.html")

## page flash library
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

    ## Check if method was post
    if request.method == 'POST':

        ## Collect requests from data and convert them into variables
        values = list(request.form)
        title = request.form[values[0]]
        keys = values[1:]
        dict_of_values = {}

        ## loop through request form collecting input term and definition
        for i in range(0, len(keys), 2):
            if i+1 < len(keys):
                term = request.form[keys[i]]
                definition = request.form[keys[i + 1]]

                ## add term and definition to dict_of_values
                dict_of_values[term] = definition

        ## Update flashcard database with users' new flashcard set
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

    ## Check if the request was a post
    if request.method == "POST":
        
        ## Determine if the secret key is in the request form
        if "RemoveThisSet#$#_129Kqaoe_982AmcAA1((**//10" in list(request.form.keys())[0]:
            
            ## Remove set from flashcard database
            flash_library_db.delete_one(
                {"Email": session['email'],
                 
                 ## Removes the secret key from the request form
                 "Set_Name": list(request.form.keys())[0].replace("RemoveThisSet#$#_129Kqaoe_982AmcAA1((**//10", "")})
            return redirect("/flash-library")
        else:
            ## Collect the current flashcard set
            session["flashcard_set"] = list(request.form.keys())[0]
            
            ## Collect a random pair 
            term = getRandomTerm()
            
            ## Open html file with the random pair
            return render_template("card.html", data=term)

    else:
        return render_template("card.html", data = getRandomTerm())

def getRandomTerm():
    
    ## Collect current flashcard set's terms and definition pairs 
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
    
    ## Check if request was a post
    if request.method == "POST":
        
        ## Collect goal that was inputted 
        goal = request.form["value"]
        
        ## Update the goals database with a new goal  
        goals_db.update_one(
            {"Email": session["email"]},
            {"$push": {"Goals": goal}},
            upsert=True
        )
        
        ## Load newly updated database
        goals = goals_db.find_one({"Email": session["email"]})["Goals"]
        
        ## Load HTML with new data
        return render_template('goalSetter.html', GoalList=goals)

    else:
        
        ## Get user in goals database
        goals = goals_db.find_one({"Email": session["email"]})
        
        ## Check if the user has created zero goals
        if goals is None:
            ## open html with no data
            return render_template('goalSetter.html', GoalList=[])
        else:
            ## Open HTML with data
            return render_template('goalSetter.html', GoalList = goals["Goals"])

@app.route('/remove_goal', methods=["Post"])
def removeGoal():
    
    ## Collect corresponding index of removed goal 
    index = int(list(request.form.keys())[0])

    ## Get list of current goals
    goals = goals_db.find_one({"Email": session["email"]})["Goals"]

    ## Remove goal at index
    goals.pop(index)

    ## Update goals database
    goals_db.update_one(
        {"Email": session["email"]},
        {"$set": {"Goals": goals}}
    )
    
    return redirect("/goalsetter")

@app.route("/calendar", methods=["Post","Get"])
def calendar():

    ## Check if the request was a post
    if request.method=="POST":

        ## Collect information
        values = request.form
        keys = list(request.form.keys())

        ## Update calendar database
        calendar.update_one(
            {"Email": session["email"]},
            {"$push": {"task": [values[keys[0]], values[keys[1]]]}},
            upsert=True
        )

        ## Sort the task in the database by date
        sorted_task = dateSorter(calendar_db.find_one({"Email": session['email']})["task"])

        ## Update database with sorted task
        calendar_db.update_one(
            {"Email": session["email"]},
            {"$set": {"task": sorted_task}},
        )

        ## Collect task and render html
        tasks = calendar_db.find_one({"Email": session["email"]})["task"]
        return render_template('calendar.html', tasks=tasks)
    else:

        ## Collect task
        tasks = calendar_db.find_one({"Email": session["email"]})

        ## Check if the user has zero tasks
        if tasks is None:
            return render_template('calendar.html', tasks=[])

        else:
            return render_template('calendar.html', tasks=tasks["task"])

@app.route('/remove_task', methods=["Post"])
def removeTask():

    ## Collect index of task
    index = int(list(request.form.keys())[0])
    new_tasks = calendar_db.find_one({"Email": session["email"]})["task"]

    ## Pop item at index off calendar database
    new_tasks.pop(index)

    ## Update calendar database
    calendar_db.update_one(
        {"Email": session["email"]},
        {"$set": {"task": new_tasks}}
    )

    return redirect("/calendar")



def dateSorter(listOfDates):

    ## Loop through the list of dates
    ## Convert data into the correct format
    ## Then sort by date
    return sorted(listOfDates, key=lambda x: datetime.strptime(x[0], "%Y-%m-%d"))

if __name__ == "__main__":
    app.run(debug=True,hosts= "0.0.0.0", port=5000)
