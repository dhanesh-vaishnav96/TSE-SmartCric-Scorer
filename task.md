# 🏏 Cricket Scorecard Web App (Full Project Prompt)

## 📌 Project Title

**Cricket Scorecard System (Manual Input, Real Rules, Responsive UI)**

---

## 🎯 Objective

Build a **Cricket Scorecard Web Application** using:

* Python (FastAPI)
* HTML
* CSS
* Jinja2 Templates

The system should simulate a **real cricket match scoring system** with manual input and support both **single-player and two-player modes**.

---

## ⚙️ Tech Stack

* Backend: FastAPI (Python)
* Frontend: HTML, CSS
* Template Engine: Jinja2
* Optional: JavaScript (for UI interactivity)

---

## 🧩 Core Features

### 1. 🏁 Match Setup Page

* Team A Name input
* Team B Name input
* Total Overs selection (manual input)
* Toss System:

  * Toss winner selection
  * Choose: Bat / Bowl

---

### 2. 👤 Player Modes

#### Single Player Mode

* One user controls entire match

#### Two Player Mode

* Player 1 → Batting team
* Player 2 → Bowling team

---

### 3. 🏏 Match Screen UI

#### Input Fields:

* Striker Name
* Non-Striker Name
* Bowler Name

#### Buttons:

* Runs: 0, 1, 2, 3, 4, 6
* Extras:

  * Wide
  * No Ball
  * Bye
  * Leg Bye
* Wicket button

---

### 4. 📊 Scorecard Display

* Total Runs / Wickets
* Overs (e.g., 5.3)
* Run Rate
* Target (if second innings)

#### Batting Table:

* Player Name
* Runs
* Balls
* 4s / 6s
* Strike Rate

#### Bowling Table:

* Bowler Name
* Overs
* Runs
* Wickets
* Economy

---

### 5. 🔄 Strike Rotation Logic

* Strike changes on:

  * Odd runs (1, 3)
  * End of over

---

### 6. ⚠️ Wicket Handling

* On wicket:

  * New batsman input
* Track:

  * Total wickets
  * Individual stats

---

### 7. 🎯 Over System

* Each over = 6 valid balls
* Wide / No Ball = extra ball
* Automatically increment overs

---

### 8. 🧮 Real Cricket Rules

Include:

* Extras calculation
* Target calculation (2nd innings)
* Match end conditions:

  * All wickets fallen
  * Overs completed
  * Target achieved

---

### 9. 📱 Responsive UI

* Mobile-friendly layout
* Clean scoreboard design
* Button-based scoring interface

---

## 📁 Suggested Folder Structure

```
project/
│── main.py
│── templates/
│     ├── index.html
│     ├── match.html
│     ├── scorecard.html
│── static/
│     ├── style.css
│── models/
│     ├── match.py
│── routes/
│     ├── match_routes.py
```

---

## 🔌 FastAPI Backend Requirements

* Route: `/` → Match setup page
* Route: `/start-match` → Initialize match
* Route: `/update-score` → Handle scoring actions
* Route: `/scorecard` → Show final scorecard

---

## 🧠 Logic Requirements

* Maintain match state (in-memory or session)
* Track:

  * Runs
  * Balls
  * Overs
  * Wickets
  * Players stats
* Handle innings switching

---

## 🎨 UI Requirements

* Simple and clean design
* Scoreboard at top
* Buttons for scoring
* Tables for stats

---

## 🚀 Bonus Features (Optional)

* Match history storage
* Local database (SQLite)
* Dark mode UI
* Sound effects on scoring

---

## 📌 Expected Output

A working web app where:

* User sets match
* Plays ball-by-ball scoring manually
* Gets real-time score updates
* Views final scorecard

---

## 🔥 Important Notes

* Keep UI simple (no complex JS frameworks)
* Focus on logic + functionality
* Ensure proper cricket rules implementation
* Use Jinja2 for dynamic rendering

---

## 🧾 Deliverables

* Fully working FastAPI app
* Clean UI
* Proper cricket logic
* Responsive design

---
