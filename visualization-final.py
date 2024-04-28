import tkinter as tk
from tkinter import messagebox
import mysql.connector
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
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
    tokens = [word for word in tokens if word.isalpha()]
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

# Phase 2: Data Storage and Comparison

def connect_to_database():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="employee"
    )

def create_tables(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS candidates
                 (id INT AUTO_INCREMENT PRIMARY KEY,
                 name VARCHAR(255),
                 rewards INT,
                 academic_score FLOAT,
                 skills TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS employees
                 (id INT AUTO_INCREMENT PRIMARY KEY,
                 name VARCHAR(255),
                 rewards INT,
                 academic_score FLOAT,
                 skills TEXT)''')

def store_data(cursor, table_name, name, rewards, academic_score, skills):
    sql = f"INSERT INTO {table_name} (name, rewards, academic_score, skills) VALUES (%s, %s, %s, %s)"
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
        if any(skill in employee_skills for skill in candidate_skills):
            match_criteria += 1
    
    return match_criteria

def evaluate_candidate(candidate_data):
    feedback = ""
    if candidate_data['rewards'] < 3:
        feedback += "Candidate has fewer rewards. "
    if candidate_data['academic_score'] < 8:
        feedback += "Candidate has a lower academic score. "
    if len(candidate_data['skills']) < 3:
        feedback += "Candidate lacks sufficient skills. "
    return feedback if feedback else "Candidate meets criteria."

def generate_candidate_comparison_graph():
    try:
        mydb = connect_to_database()
        mycursor = mydb.cursor()

        # Fetch candidate data from the database
        mycursor.execute("SELECT * FROM candidates")
        candidate_data = mycursor.fetchall()

        # Extract candidate names and match criteria
        candidate_names = [row[1] for row in candidate_data]
        match_criteria = [compare_candidates(mycursor, {"name": row[1], "rewards": row[2], "academic_score": row[3], "skills": row[4] if row[4] else []}) for row in candidate_data]

        # Generate bar chart
        plt.bar(candidate_names, match_criteria)
        plt.xlabel('Candidate')
        plt.ylabel('Match Criteria')
        plt.title('Candidate Comparison')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

        # Close the database connection
        mycursor.close()
        mydb.close()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def generate_employee_candidate_comparison_graph():
    try:
        mydb = connect_to_database()
        mycursor = mydb.cursor()

        # Fetch employee and candidate data from the database
        mycursor.execute("SELECT * FROM employees")
        employee_data = mycursor.fetchall()

        mycursor.execute("SELECT * FROM candidates")
        candidate_data = mycursor.fetchall()

        # Extract employee and candidate names and match criteria
        employee_names = [row[1] for row in employee_data]
        employee_match_criteria = [compare_candidates(mycursor, {"name": row[1], "rewards": row[2], "academic_score": row[3], "skills": row[4] if row[4] else []}) for row in employee_data]

        candidate_names = [row[1] for row in candidate_data]
        candidate_match_criteria = [compare_candidates(mycursor, {"name": row[1], "rewards": row[2], "academic_score": row[3], "skills": row[4] if row[4] else []}) for row in candidate_data]

        # Generate bar chart
        fig, ax = plt.subplots()
        ax.bar(employee_names, employee_match_criteria, label='Employees')
        ax.bar(candidate_names, candidate_match_criteria, label='Candidates')
        ax.set_xlabel('Name')
        ax.set_ylabel('Match Criteria')
        ax.set_title('Employee vs Candidate Comparison')
        ax.legend()
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

        # Close the database connection
        mycursor.close()
        mydb.close()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


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
        sql = "INSERT INTO candidates (name, rewards, academic_score, skills) VALUES (%s, %s, %s, %s)"
        val = (name, rewards, academic_score, skills)
        mycursor.execute(sql, val)
        
        mydb.commit()
        mycursor.close()
        mydb.close()
        
        messagebox.showinfo("Success", "Candidate data stored successfully!")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid rewards and academic score.")

def extract_and_compare_candidates(description_entry):
    description = description_entry.get(1.0, tk.END)
    description = description.strip()

    if not description:
        messagebox.showwarning("Warning", "Please enter a job description.")
        return

    try:
        mydb = connect_to_database()
        mycursor = mydb.cursor()

        # Extract keywords and skills from the description
        keywords = extract_keywords(description)
        skills = extract_skills(description)

        # Debugging: Print extracted keywords and skills
        print("Extracted Keywords:", keywords)
        print("Extracted Skills:", skills)

        # Fetch candidate data from the database
        mycursor.execute("SELECT * FROM candidates")
        candidate_data = mycursor.fetchall()

        # Debugging: Print candidate data
        print("Candidate Data:", candidate_data)

        # Compare extracted keywords and skills with candidate data
        selected_candidates = []
        for row in candidate_data:
            candidate_name = row[1]
            candidate_skills_str = row[4] if row[4] else ""  # Fetch skills as a string from database
            candidate_skills = [skill.strip() for skill in candidate_skills_str.split(',')]  # Split skills string into a list

            # Debugging: Print candidate skills
            print(f"Candidate Skills for {candidate_name}:", candidate_skills)

            if any(keyword in candidate_skills for keyword in keywords) or any(skill in candidate_skills for skill in skills):
                selected_candidates.append(candidate_name)
                print(f"Selected Candidate: {selected_candidates}")
        if selected_candidates:
            messagebox.showinfo("Selected Candidates", f"Selected candidates: {', '.join(selected_candidates)}")
            print(f"Selected Candidate: {selected_candidates}")
        else:
            messagebox.showinfo("Selected Candidates", "No candidates match the job description.")

        # Close the database connection
        mycursor.close()
        mydb.close()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


# Function to handle comparing candidates
def compare_candidate_data():
    generate_candidate_comparison_graph()

# Function to handle comparing employees and new candidates
def compare_employee_candidate_data():
    generate_employee_candidate_comparison_graph()

# Create the main window
root = tk.Tk()
root.title("Candidate Management System")

# Create and place entry fields for job description
description_label = tk.Label(root, text="Job Description:")
description_label.grid(row=0, column=0, padx=5, pady=5)
description_entry = tk.Text(root, height=10, width=50)
description_entry.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

# Create button to extract and compare candidates
extract_button = tk.Button(root, text="Extract and Compare Candidates", command=lambda: extract_and_compare_candidates(description_entry))
extract_button.grid(row=1, column=0, columnspan=3, pady=5)

# Create and place entry fields for candidate data
tk.Label(root, text="Name:").grid(row=2, column=0)
name_entry = tk.Entry(root)
name_entry.grid(row=2, column=1)

tk.Label(root, text="Rewards:").grid(row=3, column=0)
rewards_entry = tk.Entry(root)
rewards_entry.grid(row=3, column=1)

tk.Label(root, text="Academic Score:").grid(row=4, column=0)
academic_score_entry = tk.Entry(root)
academic_score_entry.grid(row=4, column=1)

tk.Label(root, text="Skills:").grid(row=5, column=0)
skills_entry = tk.Entry(root)
skills_entry.grid(row=5, column=1)

# Create and place buttons for actions
store_button = tk.Button(root, text="Store Candidate Data", command=store_candidate_data)
store_button.grid(row=6, column=0, columnspan=2, pady=10)

compare_button = tk.Button(root, text="Compare Candidates", command=compare_candidate_data)
compare_button.grid(row=7, column=0, columnspan=2, pady=10)

compare_employee_button = tk.Button(root, text="Compare Employees vs Candidates", command=compare_employee_candidate_data)
compare_employee_button.grid(row=8, column=0, columnspan=2, pady=10)

# Run the main event loop
root.mainloop()