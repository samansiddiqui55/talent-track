# Talent Track
### Description:
TalentTrack is a Candidate Management System designed to streamline the process of analyzing, storing, and comparing candidate data. It includes features for extracting keywords and skills from resumes, storing candidate information in a MySQL database, and visualizing candidate comparisons using bar charts.

### Features:
1. **Resume Analysis:** Automatically extract keywords and skills from candidate resumes using Natural Language Processing (NLP) techniques.
2. **Data Storage:** Store candidate information, including name, rewards, academic score, and skills, in a MySQL database.
3. **Candidate Comparison:** Compare candidates based on rewards, academic score, and skills, visualizing the results with bar charts.
4. **User Interface:** Provides a user-friendly interface using Tkinter for easy interaction with the system.

### Installation:
1. Install Python (if not already installed).
2. Install required dependencies using pip:
```pip install mysql-connector-python nltk matplotlib```
3. Download NLTK resources by running the following Python script:
```
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
```

### Usage:
1. Run the main Python script visualization-final.py.
2. Enter a job description in the provided text field and click "Extract and Compare Candidates" to compare candidates based on the job requirements.
3. Enter candidate details (name, rewards, academic score, and skills) and click "Store Candidate Data" to store candidate information in the database.
4. Use the "Compare Candidates" button to visualize the comparison of candidates based on match criteria.
5. Use the "Compare Employees vs Candidates" button to compare employees and candidates based on match criteria.

### Contributing:
Contributions are welcome! Feel free to submit bug reports, feature requests, or pull requests on GitHub.

