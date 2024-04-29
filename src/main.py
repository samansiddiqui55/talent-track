import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import mysql.connector
import matplotlib.pyplot as plt

# Phase 1: Resume Analysis and Comparison

def preprocess_text(text):
    # Tokenization using regular expression to split on word boundaries
    tokens = re.findall(r'\b\w+\b', text)
    # Convert tokens to lowercase
    tokens = [word.lower() for word in tokens]
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
    mydb = connect_to_database()
    mycursor = mydb.cursor()
    
    # Example usage
    resume_text = "Experienced software engineer with a passion for coding and problem-solving."
    keywords = extract_keywords(resume_text)
    print("Extracted keywords:", keywords)
    skills = extract_skills(resume_text)
    print("Extracted skills:", skills)
    
    # Create employee table if not exists
    create_employee_table(mycursor)

    candidate_data_list = []

    while True:
        # Example candidate data input
        candidate_name = input("Enter candidate name (or type 'stop' to exit): ")
        if candidate_name.lower() == 'stop':
            break
        candidate_rewards = int(input("Enter candidate rewards: "))
        candidate_academic_score = float(input("Enter candidate academic score: "))
        candidate_skills = input("Enter candidate skills (comma-separated): ").split(', ')

        # Store candidate data
        store_employee_data(mycursor, candidate_name, candidate_rewards, candidate_academic_score, candidate_skills)
        mydb.commit()

    compare_option = input("Enter 'just now' to compare candidates just written, or 'all' to compare all candidates in the database: ")
    if compare_option.lower() == 'just now':
        # Compare just inputted candidates
        candidate_data_list = []
        mycursor.execute("SELECT * FROM employees ORDER BY id DESC LIMIT 0, %s", (len(candidate_data_list),))
        for row in mycursor.fetchall():
            candidate_data = {"name": row[1], "rewards": row[2], "academic_score": row[3]}
            if row[4] is not None:
                candidate_data["skills"] = row[4].split(', ')
            else:
                candidate_data["skills"] = []
            candidate_data_list.append(candidate_data)
    elif compare_option.lower() == 'all':
        # Compare all candidates in the database
        candidate_data_list = []
        mycursor.execute("SELECT * FROM employees")
        for row in mycursor.fetchall():
            candidate_data = {"name": row[1], "rewards": row[2], "academic_score": row[3]}
            if row[4] is not None:
                candidate_data["skills"] = row[4].split(', ')
            else:
                candidate_data["skills"] = []
            candidate_data_list.append(candidate_data)
    else:
        print("Invalid option!")

    # Compare all candidates with existing employees
    comparison_scores = {}
    for candidate_data in candidate_data_list:
        comparison_result = compare_candidates(mycursor, candidate_data)
        comparison_scores[candidate_data['name']] = comparison_result

    # Generate graph based on comparison scores
    generate_graph(comparison_scores)

    rank_option = input("Enter 'just now' to rank candidates just written, or 'all' to rank all candidates in the database: ")
    if rank_option.lower() == 'just now':
        # Rank just inputted candidates
        ranked_candidates = rank_candidates(mycursor)
    elif rank_option.lower() == 'all':
        # Rank all candidates in the database
        ranked_candidates = rank_candidates(mycursor)
    else:
        print("Invalid option!")

    # Print ranked candidates
    print("Ranked Candidates:")
    for rank, candidate in enumerate(ranked_candidates, start=1):
        print(f"{rank}. Name: {candidate[0]}, Rewards: {candidate[1]}, Academic Score: {candidate[2]}")

    # Close the database connection
    mycursor.close()
    mydb.close()