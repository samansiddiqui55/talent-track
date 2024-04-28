import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import mysql.connector
import matplotlib.pyplot as plt

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

# Main function
if __name__ == "__main__":
    # Example usage
    resume_text = "Experienced software engineer with a passion for coding and problem-solving."
    keywords = extract_keywords(resume_text)
    print("Extracted keywords:", keywords)
    skills = extract_skills(resume_text)
    print("Extracted skills:", skills)

    # Connect to MySQL database
    mydb = connect_to_database()
    mycursor = mydb.cursor()

    # Create employee table if not exists
    create_employee_table(mycursor)

    # Example employee data
    store_employee_data(mycursor, "John Doe", 5, 9.0, ["Python", "Java", "Problem Solving"])
    mydb.commit()

    # Example candidate comparison
    candidate_data = {"name": "Candidate", "rewards": 3, "academic_score": 8.5, "skills": ["Python", "Problem Solving", "Communication"]}
    comparison_result = compare_candidates(mycursor, candidate_data)
    print("Comparison result:", comparison_result)

    # Example graph generation
    candidate_performance = {"Candidate A": 7, "Candidate B": 8, "Candidate C": 6}
    generate_graph(candidate_performance)

    # Example candidate evaluation and selection
    feedback = evaluate_candidates(candidate_data)
    print("Feedback:", feedback)
    selected_candidates = select_candidates(candidate_data, mycursor)
    if selected_candidates:
        print("Candidate selected!")
    else:
        print("Candidate not selected.")

    # Dynamic table operations
    dynamic_table_operations(mycursor, 'create', 'additional_data')
    dynamic_table_operations(mycursor, 'delete', 'additional_data')

    # Rank candidates
    ranked_candidates = rank_candidates(mycursor)
    print("Ranked Candidates:", ranked_candidates)

    # Close the database connection
    mycursor.close()
    mydb.close()
