from flask import Flask, render_template, request, jsonify
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

app = Flask(__name__)


# TODO: Fetch dataset, initialize vectorizer and LSA here
newsgroups =  fetch_20newsgroups(subset='all', remove=('headers', 'footers', 'quotes'))
data= newsgroups.data

#initialize vectorizer
stop_words_list = stopwords.words('english')
vectorizer = TfidfVectorizer(stop_words=stop_words_list, max_features=5000)
X_tfidf = vectorizer.fit_transform(data)

# Apply Truncated SVD for LSA
n_components = 100  # You can adjust this number
svd_model = TruncatedSVD(n_components=n_components)
X_lsa = svd_model.fit_transform(X_tfidf)

# Normalize the LSA vectors
from sklearn.preprocessing import Normalizer
normalizer = Normalizer(copy=False)
X_lsa = normalizer.fit_transform(X_lsa)

def search_engine(query):
    """
    Function to search for top 5 similar documents given a query
    Input: query (str)
    Output: documents (list), similarities (list), indices (list)
    """
    # Transform the query using the same vectorizer and SVD model
    query_tfidf = vectorizer.transform([query])
    query_lsa = svd_model.transform(query_tfidf)
    query_lsa = normalizer.transform(query_lsa)
    
    # Compute cosine similarities
    similarities = np.dot(X_lsa, query_lsa.T).flatten()
    
    # Get the top 5 documents
    top_indices = similarities.argsort()[-5:][::-1]  # Indices of top 5 documents
    top_similarities = similarities[top_indices]  # Similarity scores of top documents
    top_documents = [data[i] for i in top_indices]  # Retrieve the actual documents
    
    return top_documents, top_similarities.tolist(), top_indices.tolist()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    documents, similarities, indices = search_engine(query)
    return jsonify({'documents': documents, 'similarities': similarities, 'indices': indices}) 

if __name__ == '__main__':
    app.run(debug=True)
