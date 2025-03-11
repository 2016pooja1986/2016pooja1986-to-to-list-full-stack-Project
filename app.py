from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'eqyzvxbxudbbtmdx'

# Initialize the database
def init_db():
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL,
                 email TEXT UNIQUE NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER NOT NULL,
                 task TEXT NOT NULL,
                 status TEXT DEFAULT 'Pending',
                 FOREIGN KEY (user_id) REFERENCES users(id))''')
    conn.commit()
    conn.close()

def email_connection(email,mail_body):
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Change if using Webmail
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = 'pooja.tgcpv@gmail.com'  # Replace with your email
    app.config['MAIL_PASSWORD'] = 'eqyzvxbxudbbtmdx'  # Use an App Password for Gmail

    mail = Mail(app)
        
        

            # Sending Email
    msg = Message(
                subject = "Your To-Do List",
                sender='pooja.tgcpv@gmail.com',
                recipients=[email],  # Replace with recipient email
                body = mail_body
                
            )


    try:
        mail.send(msg)
        flash("Your message has been sent successfully!", "success")
        #return redirect(url_for('success'))
    except Exception as e:
        flash(f"Failed to send email: {str(e)}", "danger")
        #return redirect(url_for('contact'))

init_db()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", (username, password, email))
            conn.commit()
            flash("Registration successful! Please login.", "success")

            body = f"User Name:{username}\nPassword:{password}\nregistered email:{email}"
        

            email_connection(email,body)

            # return redirect(url_for('index'))
            username = request.form['username']
            password = request.form['password']
        
            conn = sqlite3.connect('todo.db')
            c = conn.cursor()
            c.execute("SELECT id, email FROM users WHERE username=? AND password=?", (username, password))
            user = c.fetchone()
            conn.close()
            
            if user:
                session['user_id'] = user[0]
                session['email'] = user[1]
            return render_template('index.html')
        except sqlite3.IntegrityError:
            flash("Username or Email already exists!", "danger")
        conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("SELECT id, email FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['email'] = user[1]
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials! Please register.", "danger")
            return redirect(url_for('register'))
    return render_template('templates/login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/index')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("SELECT id, task, status FROM tasks WHERE user_id=?", (session['user_id'],))
    to_do_lst = c.fetchall()
    conn.close()
    
    return render_template('index.html', to_do_lst=to_do_lst)

@app.route('/add', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    task_name = request.form.get('task_name')
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("INSERT INTO tasks (user_id, task) VALUES (?, ?)", (session['user_id'], task_name))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE user_id=? AND id=?", (session['user_id'], task_id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/update_status/<int:task_id>')
def update_status(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("UPDATE tasks SET status='Completed' WHERE user_id=? AND id=?", (session['user_id'], task_id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/send_email', methods=['POST'])
def send_email():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("SELECT task, status FROM tasks WHERE user_id=?", (session['user_id'],))
    tasks = c.fetchall()
    conn.close()

    task_list = "\n".join([f"{task[0]} - {task[1]}" for task in tasks])
    user_email = session.get('email')

    if not user_email:
        flash("No email found for this account!", "danger")
        return redirect(url_for('index'))
    

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Change if using Webmail
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = 'pooja.tgcpv@gmail.com'  # Replace with your email
    app.config['MAIL_PASSWORD'] = 'eqyzvxbxudbbtmdx'  # Use an App Password for Gmail

    mail = Mail(app)
    
    

  # Sending Email
    msg = Message(
            subject = "Your To-Do List",
            sender='pooja.tgcpv@gmail.com',
            recipients=[user_email],  # Replace with recipient email
            body = f"Here is your to-do list:\n\n{task_list}"
        )


    try:
        mail.send(msg)
        flash("Your message has been sent successfully!", "success")
        #return redirect(url_for('success'))
    except Exception as e:
        flash(f"Failed to send email: {str(e)}", "danger")
        #return redirect(url_for('contact'))

    
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)
