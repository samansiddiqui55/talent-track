import nltk
import ssl

# Try to import ssl and create unverified context for older versions of Python
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Download NLTK resources
nltk.download('stopwords')
nltk.download('wordnet')
