from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
from textblob import TextBlob
import random

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ----------------

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS mood(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        mood TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- AI MOOD ANALYSIS ----------------

def analyze_mood(text):

    text = text.lower()

    if any(word in text for word in ["depress","hopeless","sad"]):
        return "Depression"

    elif any(word in text for word in ["stress","pressure","tension"]):
        return "Stress"

    elif any(word in text for word in ["anxiety","panic","fear"]):
        return "Anxiety"

    elif any(word in text for word in ["sleep","insomnia","tired"]):
        return "Sleep Disorder"

    else:
        analysis = TextBlob(text)

        if analysis.sentiment.polarity > 0:
            return "Happy"
        else:
            return "Neutral"


# ---------------- DOCTORS ----------------

doctors_data = {

"Depression":[
{"name":"Dr Anjali Sharma","phone":"9876543210"},
{"name":"Dr Raj Verma","phone":"9123456780"}
],

"Stress":[
{"name":"Dr Neha Singh","phone":"9988776655"},
{"name":"Dr Aman Kapoor","phone":"9871234560"}
],

"Anxiety":[
{"name":"Dr Priya Mehta","phone":"9765432109"},
{"name":"Dr Rohit Malhotra","phone":"9012345678"}
],

"Sleep Disorder":[
{"name":"Dr Kavita Jain","phone":"8899001122"},
{"name":"Dr Arjun Nair","phone":"8877665544"}
],

"Happy":[
{"name":"Wellness Coach Aman","phone":"9090909090"},
{"name":"Lifestyle Coach Riya","phone":"9088776655"}
]

}

# ---------------- ROUTES ----------------

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method=="POST":

        user=request.form.get("username")
        pwd=request.form.get("password")

        conn=sqlite3.connect("database.db")
        c=conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?",(user,pwd))
        data=c.fetchone()

        if not data:
            c.execute("INSERT INTO users(username,password) VALUES (?,?)",(user,pwd))
            conn.commit()

        conn.close()

        session["user"]=user
        return redirect("/dashboard")

    return render_template("login.html")


@app.route("/dashboard", methods=["GET","POST"])
def dashboard():

    if "user" not in session:
        return redirect("/login")

    mood_result=""
    suggestion=""
    doctor_list=[]

    if request.method=="POST":

        text=request.form.get("mood")
        mood_result=analyze_mood(text)

        if mood_result=="Depression":
            suggestion="Talk to someone you trust."

        elif mood_result=="Stress":
            suggestion="Try meditation and deep breathing."

        elif mood_result=="Anxiety":
            suggestion="Relax your mind."

        elif mood_result=="Sleep Disorder":
            suggestion="Maintain a sleep schedule."

        elif mood_result=="Happy":
            suggestion="Keep smiling."

        doctor_list=doctors_data.get(mood_result,[])

        conn=sqlite3.connect("database.db")
        c=conn.cursor()

        c.execute("INSERT INTO mood(user,mood) VALUES (?,?)",
                  (session["user"],mood_result))

        conn.commit()
        conn.close()

    conn=sqlite3.connect("database.db")
    c=conn.cursor()

    c.execute("SELECT mood,COUNT(*) FROM mood GROUP BY mood")

    data=c.fetchall()

    conn.close()

    labels=[row[0] for row in data]
    values=[row[1] for row in data]

    stress=random.randint(40,90)
    sleep=random.randint(4,9)

    return render_template(
        "dashboard.html",
        mood=mood_result,
        stress=stress,
        sleep=sleep,
        suggestion=suggestion,
        doctor_list=doctor_list,
        labels=labels,
        values=values
    )


@app.route("/chatbot")
def chatbot_page():
    return render_template("chatbot.html")


@app.route("/chatbot-api", methods=["POST"])
def chatbot():

    msg=request.json.get("message","").lower()

    if "sad" in msg:
        reply="I'm here for you 💙"

    elif "stress" in msg:
        reply="Take a small break and breathe."

    elif "happy" in msg:
        reply="That's amazing 😊"

    else:
        reply="Tell me more about how you feel."

    return jsonify({"reply":reply})


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__=="__main__":
    app.run(debug=True)
