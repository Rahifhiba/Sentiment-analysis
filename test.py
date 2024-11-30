import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string

# Exemple de prétraitement
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

text = "Ceci est un exemple de texte brut à prétraiter."
# Tokenisation
tokens = word_tokenize(text.lower())
# Suppression de la ponctuation et des stopwords
stop_words = set(stopwords.words('french'))
tokens = [word for word in tokens if word not in stop_words and word not in string.punctuation]
# Lemmatisation
lemmatizer = WordNetLemmatizer()
tokens = [lemmatizer.lemmatize(word) for word in tokens]
print(tokens)
