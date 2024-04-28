import tkinter as tk
from tkinter import messagebox
import mysql.connector
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import matplotlib.pyplot as plt

# Initialize NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

# Phase 1: Resume Analysis and Comparison

def preprocess_text(text):
    # Tokenization
    tokens = word_tokenize(text)
    # Remove punctuation and convert to lowercase
    tokens = [word.lower() for word in tokens if word.isalpha()]
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return tokens

def extract_keywords(resume_text):
    # Extracting keywords (for demonstration, extracting nouns)
    tokens = preprocess_text(resume_text)
    tagged_words = nltk.pos_tag(tokens)
    keywords = [word for word, pos in tagged_words if pos.startswith('NN')]
    return keywords

def extract_skills(resume_text):
    # Extracting skills (for demonstration, extracting verbs)
    tokens = preprocess_text(resume_text)
    tagged_words = nltk.pos_tag(tokens)
    skills = [word for word, pos in tagged_words if pos.startswith('VB')]
    return skills

# Phase 2: Top Employee Data Storage and Graph Generation

def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="employee"
    )

def create_employee_table(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS employees
                 (id INT AUTO_INCREMENT PRIMARY KEY,
                 name VARCHAR(255),
                 rewards INT,
                 academic_score FLOAT,
                 skills TEXT)''')

def store_employee_data(cursor, name, rewards, academic_score, skills):
    sql = "INSERT INTO employees (name, rewards, academic_score, skills) VALUES (%s, %s, %s, %s)"
    val = (name, rewards, academic_score, ", ".join(skills))
    cursor.execute(sql, val)

def compare_candidates(cursor, candidate_data):
    cursor.execute("SELECT * FROM employees")
    top_employees = cursor.fetchall()

    match_criteria = 0
    for employee in top_employees:
        if candidate_data['rewards'] >= employee[2]:
            match_criteria += 1
        if candidate_data['academic_score'] >= employee[3]:
            match_criteria += 1
        candidate_skills = candidate_data['skills'] or []  # Ensure skills is a list
        employee_skills = employee[4] or ""  # Ensure employee skills is not None
        if any(skill in employee_skills.split(', ') for skill in candidate_skills):
            match_criteria += 1
    
    return match_criteria


def generate_graph(candidate_performance):
    names = list(candidate_performance.keys())
    scores = list(candidate_performance.values())
    
    plt.bar(names, scores)
    plt.xlabel('Candidate')
    plt.ylabel('Performance Score')
    plt.title('Candidate Performance Comparison')
    plt.show()

# Phase 3: Feedback and Selection

def evaluate_candidates(candidate_data):
    # Example evaluation logic (for demonstration)
    feedback = ""
    if candidate_data['rewards'] < 3:
        feedback += "Candidate has fewer rewards. "
    if candidate_data['academic_score'] < 8:
        feedback += "Candidate has a lower academic score. "
    if len(candidate_data['skills']) < 3:
        feedback += "Candidate lacks sufficient skills. "
    return feedback if feedback else "Candidate meets criteria."

def select_candidates(candidate_data, cursor):
    criteria_met = compare_candidates(cursor, candidate_data)
    if criteria_met >= 3:  # Adjusted criteria
        return True
    else:
        return False

# Phase 4: Additional Functionalities

def dynamic_table_operations(cursor, operation, table_name):
    if operation == 'create':
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {table_name}
                     (id INT AUTO_INCREMENT PRIMARY KEY,
                     name VARCHAR(255),
                     rewards INT,
                     academic_score FLOAT,
                     skills TEXT)''')
        print(f"Table {table_name} created successfully.")
    elif operation == 'delete':
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        print(f"Table {table_name} deleted successfully.")

def rank_candidates(cursor):
    cursor.execute("SELECT name, rewards, academic_score FROM employees ORDER BY rewards DESC, academic_score DESC")
    ranked_candidates = cursor.fetchall()
    return ranked_candidates

# Function to handle storing candidate data
def store_candidate_data():
    name = name_entry.get()
    rewards = rewards_entry.get()
    academic_score = academic_score_entry.get()
    skills = skills_entry.get()
    
    try:
        rewards = int(rewards)
        academic_score = float(academic_score)
        
        mydb = connect_to_database()
        mycursor = mydb.cursor()

        # Store candidate data
        store_employee_data(mycursor, name, rewards, academic_score, skills)
        mydb.commit()
        mycursor.close()
        mydb.close()
        
        messagebox.showinfo("Success", "Candidate data stored successfully!")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid rewards and academic score.")

# Function to handle comparing candidates
def compare_candidate_data():
    try:
        mydb = connect_to_database()
        mycursor = mydb.cursor()

        # Fetch candidate data from the database and perform comparison
        comparison_result = {}
        mycursor.execute("SELECT * FROM employees")
        for row in mycursor.fetchall():
            candidate_data = {"name": row[1], "rewards": row[2], "academic_score": row[3]}
            if row[4] is not None:
                candidate_data["skills"] = row[4].split(', ')
            else:
                candidate_data["skills"] = []
            match_criteria = compare_candidates(mycursor, candidate_data)
            comparison_result[candidate_data['name']] = match_criteria

        # Display the comparison results
        messagebox.showinfo("Comparison Result", f"Comparison Result:\n{comparison_result}")

        # Close the database connection
        mycursor.close()
        mydb.close()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Function to handle ranking candidates
def rank_candidate_data():
    try:
        mydb = connect_to_database()
        mycursor = mydb.cursor()

        # Fetch candidate data from the database and perform ranking
        ranked_candidates = rank_candidates(mycursor)

        # Display the ranked candidates
        ranked_candidates_info = "\n".join([f"{rank}. Name: {candidate[0]}, Rewards: {candidate[1]}, Academic Score: {candidate[2]}" for rank, candidate in enumerate(ranked_candidates, start=1)])
        messagebox.showinfo("Ranked Candidates", f"Ranked Candidates:\n{ranked_candidates_info}")

        # Close the database connection
        mycursor.close()
        mydb.close()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# Create the main window
root = tk.Tk()
root.title("Candidate Management System")

# Create and place entry fields for candidate data
tk.Label(root, text="Name:").grid(row=0, column=0)
name_entry = tk.Entry(root)
name_entry.grid(row=0, column=1)

tk.Label(root, text="Rewards:").grid(row=1, column=0)
rewards_entry = tk.Entry(root)
rewards_entry.grid(row=1, column=1)

tk.Label(root, text="Academic Score:").grid(row=2, column=0)
academic_score_entry = tk.Entry(root)
academic_score_entry.grid(row=2, column=1)

tk.Label(root, text="Skills:").grid(row=3, column=0)
skills_entry = tk.Entry(root)
skills_entry.grid(row=3, column=1)

# Create and place buttons for actions
store_button = tk.Button(root, text="Store Candidate Data", command=store_candidate_data)
store_button.grid(row=4, column=0, columnspan=2, pady=10)

compare_button = tk.Button(root, text="Compare Candidates", command=compare_candidate_data)
compare_button.grid(row=5, column=0, columnspan=2, pady=10)

rank_button = tk.Button(root, text="Rank Candidates", command=rank_candidate_data)
rank_button.grid(row=6, column=0, columnspan=2, pady=10)

# Run the main event loop
root.mainloop()
