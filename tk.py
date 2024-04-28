import tkinter as tk
from tkinter import messagebox
import mysql.connector
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import matplotlib.pyplot as plt
import seaborn as sns
from tkinter import filedialog

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

# Function to handle extracting keywords and skills from provided resume text
def extract_resume_data():
    resume_text = resume_text_entry.get("1.0", "end-1c")  # Get the resume text from the text widget
    keywords = extract_keywords(resume_text)
    skills = extract_skills(resume_text)
    messagebox.showinfo("Resume Analysis", f"Extracted Keywords: {keywords}\nExtracted Skills: {skills}")

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
        if any(skill in employee_skills.split(',') for skill in candidate_skills):
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

selected_candidates = []
def display_selected_candidates():
    if selected_candidates:
        selected_candidates_str = "\n".join(selected_candidates)
        messagebox.showinfo("Selected Candidates", f"The following candidates have been selected:\n\n{selected_candidates_str}")
    else:
        messagebox.showinfo("Selected Candidates", "No candidates have been selected yet.")

# Function to handle storing candidate data
def store_candidate_data():
    name = name_entry.get()
    rewards = rewards_entry.get()
    academic_score = academic_score_entry.get()
    skills = skills_entry.get().split(", ")  # Split skills entered by the user
    
    try:
        rewards = int(rewards)
        academic_score = float(academic_score)
        
        mydb = connect_to_database()
        mycursor = mydb.cursor()
        
        # Join skills without spaces
        skills_val = ",".join(skills)
        
        # Store candidate data
        store_employee_data(mycursor, name, rewards, academic_score, skills_val)  # Pass skills_val instead of skills
        mydb.commit()
        
        # Evaluate and potentially select the candidate
        candidate_data = {"name": name, "rewards": rewards, "academic_score": academic_score, "skills": skills}
        if select_candidates(candidate_data, mycursor):
            messagebox.showinfo("Success", f"Candidate '{name}' stored successfully and selected!")
        else:
            messagebox.showinfo("Success", f"Candidate '{name}' stored successfully, but not selected.")
        
        mycursor.close()
        mydb.close()
    except ValueError:
        messagebox.showerror("Error", "Please enter valid rewards and academic score.")

# Function to handle comparing candidates
def compare_candidate_data():
    try:
        mydb = connect_to_database()
        mycursor = mydb.cursor()

        # Fetch candidate data from the database
        mycursor.execute("SELECT * FROM employees")
        candidates_data = mycursor.fetchall()

        # Extract skills from the resume text
        resume_text = resume_text_entry.get("1.0", "end-1c")
        resume_skills = set(extract_skills(resume_text))

        # Compare candidates' skills with the resume skills
        selected_candidates = []
        for candidate in candidates_data:
            candidate_skills = set(candidate[4].split(', ')) if candidate[4] else set()
            if resume_skills.issubset(candidate_skills):
                selected_candidates.append(candidate)

        # Display selected candidates
        if selected_candidates:
            selected_candidates_info = "\n".join([f"Name: {candidate[1]}, Rewards: {candidate[2]}, Academic Score: {candidate[3]}" for candidate in selected_candidates])
            messagebox.showinfo("Selected Candidates", f"Selected Candidates:\n{selected_candidates_info}")
        else:
            messagebox.showinfo("No Candidates", "No candidates match the skills extracted from the resume.")

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

# Create a button to display selected candidates
display_button = tk.Button(root, text="Display Selected Candidates", command=display_selected_candidates)
display_button.grid(row=7, column=0, columnspan=2, pady=10)

# Create a text widget for entering resume text
resume_text_label = tk.Label(root, text="Enter Resume Text:")
resume_text_label.grid(row=8, column=0, padx=10, pady=5)
resume_text_entry = tk.Text(root, height=10, width=50)
resume_text_entry.grid(row=8, column=1, columnspan=2, padx=10, pady=5)

# Create a button to trigger resume analysis
analyze_button = tk.Button(root, text="Extract Keywords and Skills", command=extract_resume_data)
analyze_button.grid(row=9, column=0, columnspan=3, pady=10)

# Run the main event loop
root.mainloop()
