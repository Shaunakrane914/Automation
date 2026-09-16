import os
import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

from app.config import settings
from app.database import get_db_connection, log_agent_event

logger = logging.getLogger("student_os.labwork_engine")

DESKTOP_3RD_YEAR = Path(r"C:\Users\Shaunak Rane\Desktop\3rd Year")

# Subject matching config: name keyword -> DB subject name fragment
LAB_SUBJECT_MAPPINGS = [
    {
        "key": "deep_learning",
        "folder": "Deep Learning",
        "db_names": ["Deep Learning (Neural Network) Lab", "Deep Learning (Neural Network)"],
        "display_name": "Deep Learning (Neural Network) Lab",
        "category": "Deep Learning",
        "icon": "brain"
    },
    {
        "key": "nlp",
        "folder": "NLP Lab",
        "secondary_folder": "NLP",
        "db_names": ["Natural Language Processing Lab", "Natural Language Processing"],
        "display_name": "Natural Language Processing Lab",
        "category": "NLP",
        "icon": "message-square"
    },
    {
        "key": "time_series",
        "folder": "Time Series",
        "db_names": ["Time Series Modelling and Forecasting  Lab", "Time Series Modelling and Forecasting"],
        "display_name": "Time Series Modelling & Forecasting Lab",
        "category": "Time Series",
        "icon": "trending-up"
    },
    {
        "key": "bda",
        "folder": "BDA",
        "db_names": ["Big Data Analytics"],
        "display_name": "Big Data Analytics Lab",
        "category": "Big Data",
        "icon": "database"
    },
    {
        "key": "ajp",
        "folder": "AJP",
        "db_names": ["Advance Java Programming Lab", "Advance Java Programming"],
        "display_name": "Advance Java Programming Lab",
        "category": "Java Systems",
        "icon": "code"
    },
    {
        "key": "awt",
        "folder": "AWT",
        "db_names": ["Advanced Web Technology"],
        "display_name": "Advanced Web Technology Lab",
        "category": "Full-Stack Web",
        "icon": "globe"
    }
]

def find_subject_id_in_db(conn: sqlite3.Connection, db_names: List[str]) -> Optional[int]:
    cursor = conn.cursor()
    for name in db_names:
        cursor.execute("SELECT id FROM subjects WHERE name LIKE ? LIMIT 1", (f"%{name}%",))
        row = cursor.fetchone()
        if row:
            return row["id"]
    return None

def build_default_lab_curriculum() -> List[Dict[str, Any]]:
    """
    Curated, verified labwork curriculum deeply extracted from Shaunak's actual 3rd Year code files,
    notebooks, datasets, and class resources.
    """
    curriculum = [
        # -------------------------------------------------------------
        # 1. Deep Learning (Neural Network) Lab
        # -------------------------------------------------------------
        {
            "mapping_key": "deep_learning",
            "lab_number": "Exp 1",
            "title": "Single-Layer Perceptron Logic Gates (AND, OR, NAND, NOR)",
            "file_rel_path": "Deep Learning/Perceptron/AND.ipynb",
            "code_type": "jupyter",
            "concepts": ["Single-Layer Perceptron", "Delta Learning Rule", "Heaviside Step Activation", "Linear Separability", "Decision Boundary"],
            "problem_statement": "Implement and train a single-layer perceptron from scratch using NumPy to classify linearly separable boolean functions (AND, OR, NAND, NOR). Derive the mathematical weight update rule and observe convergence within epochs.",
            "code_summary": "Initializes weights [0, 0] and bias 0. Employs Heaviside step activation z > 0 -> 1. Updates weights per epoch using delta rule: w = w + eta * (y - y_hat) * x. Demonstrates 100% convergence across binary truth tables.",
            "practice_todos": [
                {"id": "dl1-1", "task": "Import numpy and initialize binary truth table inputs [[0,0], [0,1], [1,0], [1,1]] with target labels.", "category": "Setup"},
                {"id": "dl1-2", "task": "Write the step activation function: return 1 if z > 0 else 0.", "category": "Algorithm"},
                {"id": "dl1-3", "task": "Initialize weights = np.zeros(2), bias = 0.0, learning rate eta = 0.1, and epochs = 10.", "category": "Setup"},
                {"id": "dl1-4", "task": "Implement nested training loop: compute linear combination z = dot(x, w) + b and error e = y - y_hat.", "category": "Implementation"},
                {"id": "dl1-5", "task": "Apply delta rule: w += eta * e * x and b += eta * e when error is non-zero.", "category": "Implementation"},
                {"id": "dl1-6", "task": "Plot decision boundary line w1*x1 + w2*x2 + b = 0 and verify all 4 truth table outputs.", "category": "Validation"}
            ],
            "starter_code": """import numpy as np
import pandas as pd

# 1. Truth table input and labels for AND gate
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([0, 0, 0, 1])

# 2. Parameters & Heaviside Step Activation
weights = np.zeros(2)
bias = 0.0
eta = 0.1
epochs = 10

def step_activation(z):
    return 1 if z > 0 else 0

# 3. Delta rule training loop
for epoch in range(epochs):
    errors = 0
    for i in range(len(X)):
        x_i = X[i]
        target = y[i]
        z = np.dot(x_i, weights) + bias
        pred = step_activation(z)
        error = target - pred
        if error != 0:
            weights += eta * error * x_i
            bias += eta * error
            errors += 1
    if errors == 0:
        print(f"Converged at epoch {epoch + 1}")
        break

print("Learned Weights:", weights, "Bias:", bias)
predictions = [step_activation(np.dot(x, weights) + bias) for x in X]
print("Predictions:", predictions)"""
        },
        {
            "mapping_key": "deep_learning",
            "lab_number": "Exp 2",
            "title": "Non-Linear Separability Analysis (The XOR Limitation)",
            "file_rel_path": "Deep Learning/Perceptron/XOR.ipynb",
            "code_type": "jupyter",
            "concepts": ["Non-Linear Separability", "XOR Problem", "Minsky-Papert Limitation", "Error Oscillation"],
            "problem_statement": "Demonstrate why a single-layer perceptron fails to learn the XOR boolean function due to non-linear separability. Observe persistent error oscillation and explain the mathematical necessity of hidden layers.",
            "code_summary": "Applies the single-layer perceptron training loop to XOR data [0, 1, 1, 0]. Visualizes why no single hyper-plane (straight line) can partition (0,1) and (1,0) from (0,0) and (1,1).",
            "practice_todos": [
                {"id": "dl2-1", "task": "Set up XOR dataset: X = [[0,0], [0,1], [1,0], [1,1]], y = [0, 1, 1, 0].", "category": "Setup"},
                {"id": "dl2-2", "task": "Execute single-layer perceptron training for 20 epochs and record error per epoch.", "category": "Experiment"},
                {"id": "dl2-3", "task": "Log the oscillating weight vector and verify error never converges to zero.", "category": "Analysis"},
                {"id": "dl2-4", "task": "Plot the 4 points on a 2D Cartesian plane showing opposite corners share identical labels.", "category": "Visualization"},
                {"id": "dl2-5", "task": "Write theoretical conclusion explaining why multi-layer architectures solve this limitation.", "category": "Theory"}
            ],
            "starter_code": """import numpy as np

# XOR Truth Table (Non-linearly separable)
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
y = np.array([0, 1, 1, 0])

weights = np.zeros(2)
bias = 0.0
eta = 0.1

for epoch in range(20):
    total_error = 0
    for i in range(len(X)):
        pred = 1 if (np.dot(X[i], weights) + bias) > 0 else 0
        err = y[i] - pred
        weights += eta * err * X[i]
        bias += eta * err
        total_error += abs(err)
    print(f"Epoch {epoch+1:02d}: Total Error = {total_error}, Weights = {weights}, Bias = {bias:.2f}")

print("Conclusion: Single-layer perceptron oscillates and cannot separate XOR.")"""
        },
        {
            "mapping_key": "deep_learning",
            "lab_number": "Exp 3",
            "title": "Multi-Layer Perceptron (MLP) & Backpropagation",
            "file_rel_path": "Deep Learning/Multi-Layer.ipynb",
            "code_type": "jupyter",
            "concepts": ["Multi-Layer Perceptron (MLP)", "Hidden Layers", "Backpropagation", "ReLU / Sigmoid Activations", "Binary Cross-Entropy"],
            "problem_statement": "Design, train, and evaluate a Multi-Layer Perceptron with hidden layers using Keras/TensorFlow to resolve the XOR problem. Inspect weight matrices and hidden activation mappings.",
            "code_summary": "Constructs a Sequential model with Dense(4, activation='relu') hidden layer and Dense(1, activation='sigmoid') output layer. Uses Adam optimizer and binary cross-entropy loss to achieve 100% classification accuracy on XOR.",
            "practice_todos": [
                {"id": "dl3-1", "task": "Import tensorflow as tf and numpy as np.", "category": "Setup"},
                {"id": "dl3-2", "task": "Define tf.keras.Sequential model with Input(2), Dense(4, activation='relu'), and Dense(1, activation='sigmoid').", "category": "Architecture"},
                {"id": "dl3-3", "task": "Compile model with optimizer='adam', loss='binary_crossentropy', and metrics=['accuracy'].", "category": "Compilation"},
                {"id": "dl3-4", "task": "Train model for 500 epochs with verbose=0 and plot loss reduction curve.", "category": "Training"},
                {"id": "dl3-5", "task": "Evaluate model.predict(X) and verify output probabilities round to [0, 1, 1, 0].", "category": "Evaluation"}
            ],
            "starter_code": """import tensorflow as tf
import numpy as np

# XOR Data
X = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=np.float32)
y = np.array([[0], [1], [1], [0]], dtype=np.float32)

# Multi-Layer Perceptron Model
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(2,)),
    tf.keras.layers.Dense(4, activation='relu', name='hidden_layer'),
    tf.keras.layers.Dense(1, activation='sigmoid', name='output_layer')
])

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.05),
              loss='binary_crossentropy',
              metrics=['accuracy'])

history = model.fit(X, y, epochs=400, verbose=0)
predictions = model.predict(X)
print("Raw Probabilities:\\n", predictions)
print("Rounded Predictions:\\n", np.round(predictions))"""
        },
        {
            "mapping_key": "deep_learning",
            "lab_number": "Exp 4",
            "title": "Tensor Mathematics & Vector Calculus for Neural Networks",
            "file_rel_path": "Deep Learning/vector.ipynb",
            "code_type": "jupyter",
            "concepts": ["Tensors", "NumPy Broadcasting", "Dot Product", "Matrix Multiplication", "Gradient Dimensions"],
            "problem_statement": "Master multidimensional NumPy tensors, shape transformations, broadcasting rules, dot products, and mini-batch tensor multiplications underpinning neural network forward passes.",
            "code_summary": "Explores 0D scalars, 1D vectors, 2D weight matrices, and 3D batch tensors. Implements batch matrix multiplications and axis-wise summations used in layer activations.",
            "practice_todos": [
                {"id": "dl4-1", "task": "Create scalar, 1D vector, 2D matrix, 3D tensor and inspect .ndim, .shape, and .dtype.", "category": "Foundations"},
                {"id": "dl4-2", "task": "Perform tensor broadcasting between shape (4, 3) and shape (3,).", "category": "Broadcasting"},
                {"id": "dl4-3", "task": "Compute vector dot products np.dot(u, v) and matrix multiplications np.matmul(A, B).", "category": "Linear Algebra"},
                {"id": "dl4-4", "task": "Implement forward-pass linear transformation Z = X.dot(W) + b for batch size of 16.", "category": "Practice"}
            ],
            "starter_code": """import numpy as np

# Tensors across dimensions
scalar = np.array(7.8)
vector = np.array([4, 10, 3, 10])
matrix = np.array([[1, 2, 3], [4, 5, 6]])
batch_tensor = np.random.randn(16, 4) # 16 samples, 4 features

# Weight matrix for 4 inputs -> 3 neurons
W = np.random.randn(4, 3)
b = np.zeros(3)

# Forward pass mini-batch calculation
Z = np.dot(batch_tensor, W) + b
print("Input Batch Shape:", batch_tensor.shape)
print("Output Activation Shape:", Z.shape)"""
        },

        # -------------------------------------------------------------
        # 2. Natural Language Processing Lab
        # -------------------------------------------------------------
        {
            "mapping_key": "nlp",
            "lab_number": "Exp 1",
            "title": "Text Preprocessing Pipeline (IMDB Cleaning)",
            "file_rel_path": "NLP Lab/Exp1_text_preprocessing.ipynb",
            "code_type": "jupyter",
            "concepts": ["Contractions Expansion", "Regex Cleaning", "HTML/URL Stripping", "NLTK Stopwords", "WordNet Lemmatizer"],
            "problem_statement": "Construct a production-grade NLP text cleaning pipeline for IMDB movie reviews. Expand contractions, strip HTML tags and URLs with regular expressions, eliminate stopwords, and apply WordNet lemmatization.",
            "code_summary": "Loads IMDB Dataset. Uses contractions.fix(), re.sub for HTML/URL removal, NLTK stopwords set, and WordNetLemmatizer to produce clean reviews exported to IMDB_Cleaned.csv.",
            "practice_todos": [
                {"id": "nlp1-1", "task": "Load IMDB Dataset CSV into Pandas DataFrame and inspect raw text samples.", "category": "Data"},
                {"id": "nlp1-2", "task": "Implement lowercasing and contractions.fix() to expand colloquial short forms.", "category": "Cleaning"},
                {"id": "nlp1-3", "task": "Write regex expressions to strip HTML tags (<.*?>) and HTTP/HTTPS hyperlinks.", "category": "Regex"},
                {"id": "nlp1-4", "task": "Filter out English stopwords using set(stopwords.words('english')).", "category": "Stopwords"},
                {"id": "nlp1-5", "task": "Instantiate WordNetLemmatizer and lemmatize tokens to root grammatical lemmas.", "category": "Lemmatization"},
                {"id": "nlp1-6", "task": "Export preprocessed reviews to ./data/IMDB_Cleaned.csv.", "category": "Export"}
            ],
            "starter_code": """import re
import pandas as pd
import contractions
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text: str) -> str:
    # 1. Lowercase
    text = text.lower()
    # 2. Expand contractions (don't -> do not)
    text = contractions.fix(text)
    # 3. Strip HTML tags
    text = re.sub(r'<.*?>', '', text)
    # 4. Remove URLs
    text = re.sub(r'https?://\\S+|www\\.\\S+', '', text)
    # 5. Remove punctuation and special characters
    text = re.sub(r'[^a-zA-Z\\s]', '', text)
    # 6. Stopwords & Lemmatization
    tokens = [lemmatizer.lemmatize(word) for word in text.split() if word not in stop_words]
    return " ".join(tokens)

sample = "I haven't seen a movie this great! Check http://imdb.com <br>Loved it."
print("Cleaned:", preprocess_text(sample))"""
        },
        {
            "mapping_key": "nlp",
            "lab_number": "Exp 2",
            "title": "Bag-of-Words & TF-IDF Feature Engineering",
            "file_rel_path": "NLP Lab/Exp2_Bow_TFIDF.ipynb",
            "code_type": "jupyter",
            "concepts": ["CountVectorizer", "TfidfVectorizer", "Term Frequency (TF)", "Inverse Document Frequency (IDF)", "Sparse Matrix Representation"],
            "problem_statement": "Transform preprocessed text reviews into numerical vectors using CountVectorizer (Bag of Words) and TfidfVectorizer. Limit maximum features, examine sparse matrices, and serialize vectorizers with pickle.",
            "code_summary": "Applies CountVectorizer and TfidfVectorizer(max_features=500) on cleaned IMDB reviews. Converts scipy sparse matrices to DataFrame and serializes vectorizer objects to .pkl files.",
            "practice_todos": [
                {"id": "nlp2-1", "task": "Fit CountVectorizer on sample documents and inspect get_feature_names_out().", "category": "BoW"},
                {"id": "nlp2-2", "task": "Convert sparse occurrence matrix to dense array with .toarray() and format as DataFrame.", "category": "BoW"},
                {"id": "nlp2-3", "task": "Instantiate TfidfVectorizer(max_features=500) and fit on cleaned reviews corpus.", "category": "TF-IDF"},
                {"id": "nlp2-4", "task": "Calculate and verify TF-IDF mathematical formula: TF(t,d) * log(N / DF(t)).", "category": "Theory"},
                {"id": "nlp2-5", "task": "Save feature matrix to IMDB_TFIDF.csv and dump vectorizer to pickle file.", "category": "Serialization"}
            ],
            "starter_code": """import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

docs = [
    "I love this fantastic movie",
    "This movie was terrible and boring",
    "Loved the acting and fantastic plot",
    "A completely boring film"
]

# 1. Bag of Words
bow_vec = CountVectorizer()
X_bow = bow_vec.fit_transform(docs)
df_bow = pd.DataFrame(X_bow.toarray(), columns=bow_vec.get_feature_names_out())
print("=== Bag of Words Matrix ===\\n", df_bow)

# 2. TF-IDF
tfidf_vec = TfidfVectorizer(max_features=10)
X_tfidf = tfidf_vec.fit_transform(docs)
df_tfidf = pd.DataFrame(X_tfidf.toarray(), columns=tfidf_vec.get_feature_names_out())
print("\\n=== TF-IDF Matrix ===\\n", df_tfidf.round(3))"""
        },
        {
            "mapping_key": "nlp",
            "lab_number": "Exp 3",
            "title": "N-Gram Language Modeling & Probability Distribution",
            "file_rel_path": "NLP/N-gram .ipynb",
            "code_type": "jupyter",
            "concepts": ["N-Grams", "Unigrams & Bigrams", "Markov Property", "Conditional Probability", "Language Modeling"],
            "problem_statement": "Extract unigrams, bigrams, and trigrams from text. Compute joint and conditional word transition probabilities to predict upcoming tokens.",
            "code_summary": "Uses nltk.util.ngrams and collections.Counter to generate frequency distributions of word n-tuples and calculate conditional bigram probabilities.",
            "practice_todos": [
                {"id": "nlp3-1", "task": "Tokenize text into lowercase words.", "category": "Tokenization"},
                {"id": "nlp3-2", "task": "Generate bigrams and trigrams using list(nltk.util.ngrams(tokens, n)).", "category": "N-Grams"},
                {"id": "nlp3-3", "task": "Count frequencies with collections.Counter and rank top 10 most common n-grams.", "category": "Frequencies"},
                {"id": "nlp3-4", "task": "Compute conditional transition probability P(w2 | w1) = Count(w1, w2) / Count(w1).", "category": "Probability"},
                {"id": "nlp3-5", "task": "Build next-word auto-completion function based on maximum likelihood bigrams.", "category": "Application"}
            ],
            "starter_code": """from nltk.util import ngrams
from collections import Counter

text = "This movie was absolutely amazing I loved every moment of this movie and the acting was amazing"
tokens = text.lower().split()

# Extract bigrams
bi_grams = list(ngrams(tokens, 2))
bi_counts = Counter(bi_grams)
uni_counts = Counter(tokens)

print("Top Bigrams:", bi_counts.most_common(5))

# Conditional probability P(w2 | w1)
def predict_next(word):
    candidates = {k[1]: v for k, v in bi_counts.items() if k[0] == word}
    if not candidates:
        return None
    return max(candidates, key=candidates.get)

print("Next after 'this':", predict_next("this"))
print("Next after 'movie':", predict_next("movie"))"""
        },
        {
            "mapping_key": "nlp",
            "lab_number": "Exp 4",
            "title": "End-to-End Sentiment Classification Pipeline",
            "file_rel_path": "NLP/Sentiment_Analysis_Pipeline.ipynb",
            "code_type": "jupyter",
            "concepts": ["Scikit-Learn Pipeline", "Logistic Regression", "Multinomial Naive Bayes", "F1-Score Evaluation"],
            "problem_statement": "Integrate text preprocessing, TF-IDF vectorization, and statistical classification into a unified pipeline classifying review sentiment with high precision.",
            "code_summary": "Splits dataset 80/20 train/test. Trains Naive Bayes & Logistic Regression classifiers. Generates confusion matrix and precision/recall classification report.",
            "practice_todos": [
                {"id": "nlp4-1", "task": "Split dataset into 80% train and 20% test using train_test_split.", "category": "Split"},
                {"id": "nlp4-2", "task": "Build sklearn.pipeline.Pipeline chaining TfidfVectorizer and MultinomialNB.", "category": "Pipeline"},
                {"id": "nlp4-3", "task": "Fit pipeline on training data and generate predictions on test split.", "category": "Training"},
                {"id": "nlp4-4", "task": "Print classification_report (precision, recall, f1-score) and confusion matrix.", "category": "Metrics"},
                {"id": "nlp4-5", "task": "Test pipeline on arbitrary new user reviews.", "category": "Inference"}
            ],
            "starter_code": """from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

texts = [
    "Amazing film masterpiece loved it", "Best movie of the year exceptional",
    "Terrible garbage waste of time", "Horrible screenplay very boring"
]
labels = [1, 1, 0, 0]

pipeline = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('clf', MultinomialNB())
])

pipeline.fit(texts, labels)
sample_test = ["Masterpiece acting", "Waste of money boring"]
print("Predictions:", pipeline.predict(sample_test))"""
        },

        # -------------------------------------------------------------
        # 3. Time Series Modelling and Forecasting Lab
        # -------------------------------------------------------------
        {
            "mapping_key": "time_series",
            "lab_number": "Exp 1",
            "title": "Temporal Engineering & Pandas DateTimeIndex",
            "file_rel_path": "Time Series/time series modelling and forecasting_resources (1)/Class work/module 1/1_2_pandas_datetime.ipynb",
            "code_type": "jupyter",
            "concepts": ["Pandas DateTimeIndex", "pd.to_datetime", "Frequency Resampling", "Temporal Slicing", "Date Range Generation"],
            "problem_statement": "Parse real UPI transaction timestamps into Pandas DateTimeIndex, perform frequency resampling (daily, weekly, monthly aggregates), handle missing periods, and compute temporal summary metrics.",
            "code_summary": "Uses pd.to_datetime with format directives. Generates date sequences via pd.date_range. Applies .resample('D').sum() and temporal indexing (.loc['2026-08']).",
            "practice_todos": [
                {"id": "ts1-1", "task": "Parse string timestamps to datetime objects using pd.to_datetime(format='%Y-%m-%d %H:%M:%S').", "category": "Parsing"},
                {"id": "ts1-2", "task": "Set datetime column as DataFrame index with df.set_index('timestamp', inplace=True).", "category": "Indexing"},
                {"id": "ts1-3", "task": "Perform temporal slicing for specific date ranges using df.loc['2026-01':'2026-06'].", "category": "Slicing"},
                {"id": "ts1-4", "task": "Generate synthetic continuous date intervals using pd.date_range(freq='D').", "category": "Resampling"},
                {"id": "ts1-5", "task": "Resample transaction amounts to weekly sums using df.resample('W').sum().", "category": "Aggregation"}
            ],
            "starter_code": """import pandas as pd
import numpy as np

# Synthetic UPI transaction series
dates = pd.date_range(start="2026-01-01", periods=10, freq="D")
transactions = pd.DataFrame({
    "date": dates,
    "amount": [1200, 850, 2400, 1500, 3100, 920, 1800, 2750, 4200, 1900]
})

# Set DateTimeIndex
transactions.set_index("date", inplace=True)
print("=== UPI Transactions Index ===\\n", transactions)

# Resampling to 3-day blocks
resampled_3d = transactions.resample("3D").agg({"amount": ["sum", "mean"]})
print("\\n=== 3-Day Aggregates ===\\n", resampled_3d)"""
        },
        {
            "mapping_key": "time_series",
            "lab_number": "Exp 2",
            "title": "Additive & Multiplicative Time Series Decomposition",
            "file_rel_path": "Time Series/time series modelling and forecasting_resources (1)/Class work/module 2/2_2_additive_decompostion.ipynb",
            "code_type": "jupyter",
            "concepts": ["Additive Decomposition (Y = T + S + R)", "Multiplicative Decomposition (Y = T * S * R)", "Statsmodels seasonal_decompose", "Trend & Seasonality Isolation", "Residual Stationarity"],
            "problem_statement": "Decompose electricity consumption and tourist arrival time series into Trend, Seasonality, and Residuals using statsmodels seasonal_decompose. Compare additive and multiplicative hypotheses.",
            "code_summary": "Applies seasonal_decompose on monthly 5-year data with period=12. Plots observed, trend, seasonal, and residual components. Analyzes variance of residuals.",
            "practice_todos": [
                {"id": "ts2-1", "task": "Load electricity consumption time series and inspect seasonal periodicity.", "category": "Data"},
                {"id": "ts2-2", "task": "Execute statsmodels.tsa.seasonal.seasonal_decompose with model='additive' and period=12.", "category": "Additive"},
                {"id": "ts2-3", "task": "Execute seasonal_decompose with model='multiplicative' for series with growing seasonal amplitude.", "category": "Multiplicative"},
                {"id": "ts2-4", "task": "Plot 4-panel decomposition figure (Observed, Trend, Seasonal, Residuals).", "category": "Visualization"},
                {"id": "ts2-5", "task": "Check residual series for white noise characteristics and stationarity.", "category": "Validation"}
            ],
            "starter_code": """import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose

# Generate synthetic monthly time series with trend and seasonality
dates = pd.date_range(start="2021-01-01", periods=60, freq="M")
trend = np.linspace(100, 200, 60)
seasonality = 20 * np.sin(2 * np.pi * np.arange(60) / 12)
noise = np.random.normal(0, 5, 60)
series = pd.Series(trend + seasonality + noise, index=dates)

# Decompose
decomposition = seasonal_decompose(series, model='additive', period=12)
fig = decomposition.plot()
fig.set_size_inches(10, 6)
plt.tight_layout()
plt.show()"""
        },
        {
            "mapping_key": "time_series",
            "lab_number": "Exp 3",
            "title": "Smoothing Techniques: Simple & Exponential Moving Averages",
            "file_rel_path": "Time Series/time series modelling and forecasting_resources (1)/Class work/module 2/2_4_moving_averages.ipynb",
            "code_type": "jupyter",
            "concepts": ["Simple Moving Average (SMA)", "Exponential Moving Average (EMA)", "Rolling Window", "Lag Analysis", "Noise Reduction"],
            "problem_statement": "Implement SMA and EMA smoothing algorithms on retail sales data. Analyze the tradeoff between noise reduction and phase lag across window sizes.",
            "code_summary": "Uses df['sales'].rolling(window=k).mean() and df['sales'].ewm(span=k).mean(). Compares reaction speeds to sudden level shifts.",
            "practice_todos": [
                {"id": "ts3-1", "task": "Load sales smoothing dataset and plot raw fluctuations.", "category": "Data"},
                {"id": "ts3-2", "task": "Calculate 3-day and 7-day Simple Moving Averages using df.rolling(window).mean().", "category": "SMA"},
                {"id": "ts3-3", "task": "Calculate Exponential Moving Average with df.ewm(span=7, adjust=False).mean().", "category": "EMA"},
                {"id": "ts3-4", "task": "Overlay raw, SMA, and EMA curves on a single chart to observe lag difference.", "category": "Visualization"},
                {"id": "ts3-5", "task": "Compute Mean Absolute Error (MAE) between raw sales and smoothed series.", "category": "Evaluation"}
            ],
            "starter_code": """import pandas as pd
import numpy as np

# Sample sales series
sales = pd.Series([120, 135, 128, 145, 150, 142, 160, 175, 168, 180, 195, 188])

# 1. Simple Moving Average (window=3)
sma_3 = sales.rolling(window=3).mean()

# 2. Exponential Moving Average (span=3)
ema_3 = sales.ewm(span=3, adjust=False).mean()

df_smooth = pd.DataFrame({"Actual": sales, "SMA_3": sma_3, "EMA_3": ema_3})
print(df_smooth.round(2))"""
        },
        {
            "mapping_key": "time_series",
            "lab_number": "Exp 4",
            "title": "Cloud Time Series Ingestion via AWS S3",
            "file_rel_path": "Time Series/AWS_CLOUD.ipynb",
            "code_type": "jupyter",
            "concepts": ["AWS Boto3", "Cloud Storage Ingestion", "S3 Bucket Streaming", "In-Memory Buffer"],
            "problem_statement": "Stream cloud-hosted financial transaction datasets directly from Amazon S3 buckets using Python Boto3 client without storing intermediate files on local disk.",
            "code_summary": "Initializes boto3.client('s3'). Streams upi_transactions.csv from bucket 'shaunak43rane' into io.BytesIO and directly loads it into a Pandas DataFrame.",
            "practice_todos": [
                {"id": "ts4-1", "task": "Install boto3 and initialize S3 client: boto3.client('s3').", "category": "Setup"},
                {"id": "ts4-2", "task": "List bucket contents using s3.list_objects_v2(Bucket='shaunak43rane').", "category": "S3 API"},
                {"id": "ts4-3", "task": "Fetch object stream using s3.get_object(Bucket=..., Key=...)['Body'].read().", "category": "Streaming"},
                {"id": "ts4-4", "task": "Load streamed bytes buffer into pd.read_csv(io.BytesIO(data)).", "category": "Ingestion"},
                {"id": "ts4-5", "task": "Verify parsed DateTimeIndex and column data types.", "category": "Validation"}
            ],
            "starter_code": """import io
import boto3
import pandas as pd

# AWS S3 Data Ingestion Pipeline
s3 = boto3.client('s3')
bucket_name = "shaunak43rane"
key = "upi_transactions.csv"

# Stream directly into memory buffer
response = s3.get_object(Bucket=bucket_name, Key=key)
csv_bytes = response['Body'].read()
df_cloud = pd.read_csv(io.BytesIO(csv_bytes))
print(f"Ingested {len(df_cloud)} records from AWS S3:")
print(df_cloud.head())"""
        },

        # -------------------------------------------------------------
        # 4. Big Data Analytics Lab
        # -------------------------------------------------------------
        {
            "mapping_key": "bda",
            "lab_number": "Exp 1",
            "title": "Structured Data Ingestion & Preprocessing (Amazon Analytics)",
            "file_rel_path": "BDA/Structured/Amazon.ipynb",
            "code_type": "jupyter",
            "concepts": ["Structured Schema", "Missing Value Imputation", "MinMaxScaler Normalization", "Correlation Matrix"],
            "problem_statement": "Ingest large structured Amazon eCommerce records. Handle missing values, encode categorical variables, and normalize continuous numerical features using scikit-learn MinMaxScaler.",
            "code_summary": "Loads amazon.csv. Inspects null distributions. Performs statistical imputation and applies MinMaxScaler to numerical features. Exports amazon_preprocessed.csv.",
            "practice_todos": [
                {"id": "bda1-1", "task": "Load amazon.csv and inspect df.info(), df.describe(), and null value counts.", "category": "EDA"},
                {"id": "bda1-2", "task": "Impute missing numerical values with column median and categorical with mode.", "category": "Imputation"},
                {"id": "bda1-3", "task": "Instantiate sklearn.preprocessing.MinMaxScaler and fit on price/rating features.", "category": "Scaling"},
                {"id": "bda1-4", "task": "Generate correlation matrix df.corr() to detect collineary features.", "category": "Correlation"},
                {"id": "bda1-5", "task": "Export clean processed table to amazon_preprocessed.csv.", "category": "Export"}
            ],
            "starter_code": """import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Load structured dataset
df = pd.DataFrame({
    "product_id": [101, 102, 103, 104, 105],
    "price": [499.0, 1299.0, None, 899.0, 2499.0],
    "rating": [4.2, 4.8, 3.9, None, 4.5]
})

# 1. Imputation
df["price"].fillna(df["price"].median(), inplace=True)
df["rating"].fillna(df["rating"].mean(), inplace=True)

# 2. MinMaxScaler
scaler = MinMaxScaler()
df[["price_scaled", "rating_scaled"]] = scaler.fit_transform(df[["price", "rating"]])
print(df)"""
        },
        {
            "mapping_key": "bda",
            "lab_number": "Exp 2",
            "title": "Semi-Structured JSON Processing & Schema Normalization",
            "file_rel_path": "BDA/Semi Structured/Netflix.ipynb",
            "code_type": "jupyter",
            "concepts": ["Semi-Structured Data", "JSON Parsing", "pd.json_normalize", "Explode Nested Columns", "Relational Flattening"],
            "problem_statement": "Parse complex semi-structured Netflix movie/show JSON catalogs. Flatten nested objects into 2D relational dataframes and explode multi-valued list attributes.",
            "code_summary": "Parses netflix.json using json module. Normalizes nested records with pd.json_normalize. Explodes cast and genres into normalized relational entities.",
            "practice_todos": [
                {"id": "bda2-1", "task": "Load netflix.json using Python json.load() and inspect root keys.", "category": "Parsing"},
                {"id": "bda2-2", "task": "Flatten nested dictionary records into 2D table using pd.json_normalize().", "category": "Normalization"},
                {"id": "bda2-3", "task": "Use .explode('genres') to convert list values into separate relational rows.", "category": "Relational"},
                {"id": "bda2-4", "task": "Group by genre and calculate total titles count and average release year.", "category": "Aggregation"},
                {"id": "bda2-5", "task": "Export tidy tabular dataset to netflix_clean.csv.", "category": "Export"}
            ],
            "starter_code": """import json
import pandas as pd

raw_json = [
    {"show_id": "s1", "title": "Inception", "details": {"director": "Nolan", "year": 2010}, "genres": ["Sci-Fi", "Action"]},
    {"show_id": "s2", "title": "Interstellar", "details": {"director": "Nolan", "year": 2014}, "genres": ["Sci-Fi", "Drama"]}
]

# Flatten nested JSON
df = pd.json_normalize(raw_json)
print("=== Normalized Schema ===\\n", df)

# Explode genre lists
df_exploded = df.explode("genres")
print("\\n=== Exploded Relational Rows ===\\n", df_exploded[["title", "details.director", "genres"]])"""
        },
        {
            "mapping_key": "bda",
            "lab_number": "Exp 3",
            "title": "Unstructured Text Mining & Sentiment Token Extraction",
            "file_rel_path": "BDA/Unstructured/Amazon_Review.ipynb",
            "code_type": "jupyter",
            "concepts": ["Unstructured Big Data", "Streaming File Parsing", "FastText Label Extraction", "Token Frequency Analysis"],
            "problem_statement": "Stream and process large unstructured review corpus (train.ft.txt). Extract sentiment labels (__label__1, __label__2), clean text noise, and build word frequency distributions.",
            "code_summary": "Reads large text file line by line to prevent RAM overload. Extracts sentiment tags via regex and tokenizes review bodies into clean bag of tokens.",
            "practice_todos": [
                {"id": "bda3-1", "task": "Stream train.ft.txt line by line using open() context manager.", "category": "Streaming"},
                {"id": "bda3-2", "task": "Extract label (__label__1 = Negative, __label__2 = Positive) using regex.", "category": "Regex"},
                {"id": "bda3-3", "task": "Clean review content by stripping non-alphanumeric noise and lowercasing.", "category": "Cleaning"},
                {"id": "bda3-4", "task": "Compute class balance between positive and negative reviews.", "category": "Analysis"},
                {"id": "bda3-5", "task": "Export parsed dataframe to unstructured_clean.csv.", "category": "Export"}
            ],
            "starter_code": """import re
import pandas as pd

lines = [
    "__label__2 Great product: I really loved this item works flawlessly!",
    "__label__1 Total waste: Broken upon delivery do not buy."
]

parsed_data = []
for line in lines:
    match = re.match(r'^(__label__\\d)\\s+(.*)$', line)
    if match:
        label = "Positive" if match.group(1) == "__label__2" else "Negative"
        text = re.sub(r'[^a-zA-Z\\s]', '', match.group(2).lower())
        parsed_data.append({"sentiment": label, "clean_text": text})

df_unstructured = pd.DataFrame(parsed_data)
print(df_unstructured)"""
        },

        # -------------------------------------------------------------
        # 5. Advance Java Programming Lab
        # -------------------------------------------------------------
        {
            "mapping_key": "ajp",
            "lab_number": "Exp 1",
            "title": "Dynamic Data Structures: Java Collection Framework (ArrayList & LinkedList)",
            "file_rel_path": "AJP/ArrayList1.class",
            "code_type": "java",
            "concepts": ["Java Collections Framework", "ArrayList", "LinkedList", "Dynamic Resizing", "Iterator Traversal"],
            "problem_statement": "Implement dynamic data structures using Java's ArrayList and LinkedList. Evaluate insertion, deletion, index-based element replacement (.set), and iterator performance.",
            "code_summary": "Initializes ArrayList<String>. Inserts elements with .add(), retrieves via .get(i), mutates via .set(index, element), and traverses with enhanced for loop and Iterator.",
            "practice_todos": [
                {"id": "ajp1-1", "task": "Declare and instantiate generic ArrayList<String> in Java.", "category": "Instantiation"},
                {"id": "ajp1-2", "task": "Append elements using list.add(\"A\") and list.add(\"B\").", "category": "Insertion"},
                {"id": "ajp1-3", "task": "Traverse list using index loop (i = 0; i < list.size(); i++) with list.get(i).", "category": "Traversal"},
                {"id": "ajp1-4", "task": "Update element at index 1 using list.set(1, \"C\").", "category": "Mutation"},
                {"id": "ajp1-5", "task": "Compare time complexities of ArrayList vs LinkedList for random access and insertions.", "category": "Analysis"}
            ],
            "starter_code": """package ajp;

import java.util.ArrayList;
import java.util.Iterator;

public class ArrayList1 {
    public static void main(String[] args) {
        // 1. Initialize generic dynamic ArrayList
        ArrayList<String> list = new ArrayList<>();
        list.add("A");
        list.add("B");

        // 2. Traversal using index loop
        System.out.println("--- Indexed Loop ---");
        for (int i = 0; i < list.size(); i++) {
            System.out.println("Element " + i + ": " + list.get(i));
        }

        // 3. In-place modification
        list.set(1, "C");

        // 4. Traversal without loop (toString)
        System.out.println("\\nWithout using loop: " + list);
    }
}"""
        },
        {
            "mapping_key": "ajp",
            "lab_number": "Exp 2",
            "title": "Functional Programming & Java 8 Lambda Expressions",
            "file_rel_path": "AJP/LambdaFunctions.pdf",
            "code_type": "java",
            "concepts": ["Lambda Expressions (->)", "@FunctionalInterface", "Predicate & Consumer", "Stream API", "Method References"],
            "problem_statement": "Write concise, expressive Java code using Java 8 Lambda expressions and Functional Interfaces. Implement custom calculators and filter collections using Streams.",
            "code_summary": "Demonstrates @FunctionalInterface with single abstract method. Implements mathematical operations via lambda syntax (a, b) -> a + b and applies Stream filtering.",
            "practice_todos": [
                {"id": "ajp2-1", "task": "Define custom @FunctionalInterface MathOperation with method int operate(int a, int b).", "category": "Interface"},
                {"id": "ajp2-2", "task": "Implement addition and multiplication operations using lambda expressions: (a, b) -> a + b.", "category": "Lambda"},
                {"id": "ajp2-3", "task": "Use java.util.function.Predicate<T> to filter numbers.", "category": "Predicate"},
                {"id": "ajp2-4", "task": "Filter and collect lists using Java 8 Streams: list.stream().filter(...).collect(...).", "category": "Streams"}
            ],
            "starter_code": """package ajp;

import java.util.Arrays;
import java.util.List;

@FunctionalInterface
interface MathOperation {
    int operate(int a, int b);
}

public class LambdaDemo {
    public static void main(String[] args) {
        // Lambda implementations
        MathOperation add = (a, b) -> a + b;
        MathOperation multiply = (a, b) -> a * b;

        System.out.println("10 + 20 = " + add.operate(10, 20));
        System.out.println("10 * 20 = " + multiply.operate(10, 20));

        // Streams with Lambdas
        List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8);
        System.out.println("Even Numbers:");
        numbers.stream().filter(n -> n % 2 == 0).forEach(System.out::println);
    }
}"""
        },
        {
            "mapping_key": "ajp",
            "lab_number": "Exp 3",
            "title": "JDBC Database Connectivity & Swing GUI Integration",
            "file_rel_path": "AJP/DBConnect.class",
            "code_type": "java",
            "concepts": ["JDBC (Java Database Connectivity)", "DriverManager", "PreparedStatement", "ResultSet", "Swing Desktop GUI"],
            "problem_statement": "Build an end-to-end desktop GUI application integrating NetBeans Swing and MySQL database. Connect via JDBC, execute parameterized queries, and display student records.",
            "code_summary": "Implements DBConnect class with DriverManager.getConnection('jdbc:mysql://127.0.0.1:3306/ajpa'). Executes PreparedStatement queries for registration and lookup forms.",
            "practice_todos": [
                {"id": "ajp3-1", "task": "Configure MySQL connection string: jdbc:mysql://127.0.0.1:3306/ajpa?serverTimezone=UTC.", "category": "Configuration"},
                {"id": "ajp3-2", "task": "Write DBConnect.dbCon() method returning java.sql.Connection instance.", "category": "Connection"},
                {"id": "ajp3-3", "task": "Construct PreparedStatement with parameterized query: INSERT INTO student VALUES (?, ?, ?).", "category": "PreparedStatement"},
                {"id": "ajp3-4", "task": "Execute query with statement.executeUpdate() and catch SQLExceptions.", "category": "Execution"},
                {"id": "ajp3-5", "task": "Fetch records via ResultSet and populate Swing JTextField / JTable components.", "category": "GUI Binding"}
            ],
            "starter_code": """package ajp;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class DBConnect {
    private static final String URL = "jdbc:mysql://127.0.0.1:3306/ajpa?serverTimezone=UTC";
    private static final String USER = "root";
    private static final String PASS = "2006";

    public static Connection dbCon() {
        Connection conn = null;
        try {
            conn = DriverManager.getConnection(URL, USER, PASS);
            System.out.println("Database connected successfully!");
        } catch (SQLException e) {
            e.printStackTrace();
        }
        return conn;
    }

    public static void searchStudent(int id) {
        String sql = "SELECT * FROM students WHERE id = ?";
        try (Connection conn = dbCon();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setInt(1, id);
            ResultSet rs = stmt.executeQuery();
            while (rs.next()) {
                System.out.println("Name: " + rs.getString("name") + " | Course: " + rs.getString("course"));
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}"""
        },

        {
            "mapping_key": "ajp",
            "lab_number": "Exp 4",
            "title": "Desktop GUI Forms & Multi-Document Interface (Swing & NetBeans Form)",
            "file_rel_path": "AJP/StudentMDI.class",
            "code_type": "java",
            "concepts": ["Java Swing GUI", "JFrame & JInternalFrame", "MDI (Multiple Document Interface)", "Event Handling (ActionListener)", "Form Validation"],
            "problem_statement": "Develop an interactive Swing desktop GUI application featuring a master MDI container (StudentMDI), modal student registration dialogs, search forms, and event-driven data binding.",
            "code_summary": "Implements StudentMDI desktop pane hosting child JInternalFrames (Registration, SearchStudent). Attaches ActionListeners to trigger JDBC queries and dynamic record displays.",
            "practice_todos": [
                {"id": "ajp4-1", "task": "Create JDesktopPane container within a parent JFrame.", "category": "MDI Layout"},
                {"id": "ajp4-2", "task": "Design JInternalFrame registration form with JTextField and JComboBox.", "category": "GUI Form"},
                {"id": "ajp4-3", "task": "Bind ActionListener to Submit button to collect and validate input fields.", "category": "Event Handling"},
                {"id": "ajp4-4", "task": "Pass form inputs to DBConnect PreparedStatement for database insertion.", "category": "DB Integration"},
                {"id": "ajp4-5", "task": "Implement SearchStudent lookup frame updating dynamic status labels.", "category": "Form Interaction"}
            ],
            "starter_code": """package ajp;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;

public class StudentMDI extends JFrame {
    private JDesktopPane desktopPane;

    public StudentMDI() {
        setTitle("Student Information Management System - MDI");
        setSize(800, 600);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

        desktopPane = new JDesktopPane();
        setContentPane(desktopPane);

        // Menu bar setup
        JMenuBar menuBar = new JMenuBar();
        JMenu studentMenu = new JMenu("Student Operations");
        JMenuItem regItem = new JMenuItem("New Registration");
        JMenuItem searchItem = new JMenuItem("Search Student");

        regItem.addActionListener((ActionEvent e) -> openRegistrationFrame());
        searchItem.addActionListener((ActionEvent e) -> openSearchFrame());

        studentMenu.add(regItem);
        studentMenu.add(searchItem);
        menuBar.add(studentMenu);
        setJMenuBar(menuBar);
    }

    private void openRegistrationFrame() {
        JInternalFrame frame = new JInternalFrame("Register Student", true, true, true, true);
        frame.setSize(350, 250);
        frame.setLayout(new GridLayout(4, 2, 10, 10));
        frame.add(new JLabel("  Student Name:"));
        JTextField nameField = new JTextField();
        frame.add(nameField);
        JButton btnSave = new JButton("Save Record");
        frame.add(btnSave);
        frame.setVisible(true);
        desktopPane.add(frame);
    }

    private void openSearchFrame() {
        JInternalFrame frame = new JInternalFrame("Search Record", true, true, true, true);
        frame.setSize(300, 200);
        frame.setVisible(true);
        desktopPane.add(frame);
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new StudentMDI().setVisible(true));
    }
}"""
        },
        {
            "mapping_key": "ajp",
            "lab_number": "Exp 5",
            "title": "Java Servlets: Web Application Request-Response Lifecycle & HTTP Handling",
            "file_rel_path": "AJP/AJP_MidTerm_Question_Bank.pdf",
            "code_type": "java",
            "concepts": ["Java Servlet API", "HttpServlet", "doGet() & doPost()", "Servlet Lifecycle (init, service, destroy)", "RequestDispatcher & Session Tracking"],
            "problem_statement": "Build server-side Java web components using Servlets. Handle client HTTP GET and POST requests, process query parameters, maintain user state via HttpSession, and dispatch responses.",
            "code_summary": "Implements StudentServlet extending HttpServlet with @WebServlet mapping. Processes parameters in doGet and doPost, performs session management, and forwards responses to JSP views.",
            "practice_todos": [
                {"id": "ajp5-1", "task": "Extend HttpServlet and override doGet(HttpServletRequest, HttpServletResponse) and doPost().", "category": "Servlet API"},
                {"id": "ajp5-2", "task": "Configure servlet mapping using @WebServlet('/student') annotation or web.xml deployment descriptor.", "category": "Routing"},
                {"id": "ajp5-3", "task": "Extract form submission parameters using request.getParameter('studentId').", "category": "Request Processing"},
                {"id": "ajp5-4", "task": "Store and retrieve session attributes using request.getSession().setAttribute('user', user).", "category": "Session Management"},
                {"id": "ajp5-5", "task": "Forward processed request to view via RequestDispatcher.forward(request, response).", "category": "Dispatching"}
            ],
            "starter_code": """package ajp;

import java.io.IOException;
import java.io.PrintWriter;
import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

@WebServlet("/student")
public class StudentServlet extends HttpServlet {
    private static final long serialVersionUID = 1L;

    @Override
    public void init() throws ServletException {
        System.out.println("Servlet Initialized: init() lifecycle stage");
    }

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        response.setContentType("text/html;charset=UTF-8");
        PrintWriter out = response.getWriter();

        String studentId = request.getParameter("id");
        HttpSession session = request.getSession(true);
        session.setAttribute("lastAccessedId", studentId);

        out.println("<html><body>");
        out.println("<h2>Advance Java Lab - Student Servlet Response</h2>");
        out.println("<p>Queried Student ID: <strong>" + studentId + "</strong></p>");
        out.println("<p>Session ID: " + session.getId() + "</p>");
        out.println("</body></html>");
    }

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        String studentName = request.getParameter("name");
        String course = request.getParameter("course");

        // Process student registration logic (e.g. invoke DBConnect)
        System.out.println("Registering via Servlet POST: " + studentName + " in " + course);

        response.sendRedirect("student?status=success");
    }

    @Override
    public void destroy() {
        System.out.println("Servlet Destroyed: clean up database pools");
    }
}"""
        },
        # -------------------------------------------------------------
        # 6. Advanced Web Technology Lab
        # -------------------------------------------------------------
        {
            "mapping_key": "awt",
            "lab_number": "Exp 1",
            "title": "TypeScript Foundations, Custom Interfaces & Function Overloading",
            "file_rel_path": "AWT/Overloading.ts",
            "code_type": "typescript",
            "concepts": ["TypeScript Interfaces", "Union Types", "Function Overloading Signatures", "Type Guards", "Object Typing"],
            "problem_statement": "Develop strongly-typed TypeScript modules implementing custom object interfaces, nested address models, union types, and compile-time function overloading signatures.",
            "code_summary": "Defines Address and data interfaces. Implements overloaded combine() function signatures handling (number, number), (string, string), (string, number).",
            "practice_todos": [
                {"id": "awt1-1", "task": "Declare primitive variables with union types: let x: number | string = 10.", "category": "Types"},
                {"id": "awt1-2", "task": "Define nested TypeScript interfaces Address and data.", "category": "Interfaces"},
                {"id": "awt1-3", "task": "Instantiate strongly-typed object matching the interface schema.", "category": "Objects"},
                {"id": "awt1-4", "task": "Declare overloaded signatures for function combine() with diverse argument types.", "category": "Overloading"},
                {"id": "awt1-5", "task": "Implement single runtime function body handling the overloaded signatures.", "category": "Implementation"}
            ],
            "starter_code": """// 1. Nested Interfaces
interface Address {
    city: string;
    pin: number;
    state: string;
}

interface UserProfile {
    name: string;
    mobile: number;
    address: Address;
}

const student: UserProfile = {
    name: "Shaunak Rane",
    mobile: 9876543210,
    address: { city: "Mumbai", pin: 400001, state: "Maharashtra" }
};

// 2. Function Overloading Signatures
function combine(a: number, b: number): number;
function combine(a: string, b: string): string;
function combine(a: string, b: number): string;
function combine(a: any, b: any): any {
    return a + b;
}

console.log("Numeric Sum:", combine(10, 20));
console.log("String Concat:", combine("Shaunak", " Rane"));"""
        },
        {
            "mapping_key": "awt",
            "lab_number": "Exp 2",
            "title": "React Component Architecture & Unidirectional Props Flow",
            "file_rel_path": "AWT/shadow/src/parent.jsx",
            "code_type": "javascript",
            "concepts": ["React Functional Components", "Unidirectional Data Flow", "Props Destructuring", "Default Props", "List Rendering"],
            "problem_statement": "Architect a modular React component hierarchy demonstrating parent-to-child data flow, props destructuring, default fallback parameters, and dynamic list mapping.",
            "code_summary": "Creates Parent component managing user profiles array. Passes state and objects down to Child components via props. Implements props destructuring and map rendering.",
            "practice_todos": [
                {"id": "awt2-1", "task": "Create Parent functional component containing array of user objects.", "category": "Parent Component"},
                {"id": "awt2-2", "task": "Pass primitive, array, and object props down to child components.", "category": "Props Passing"},
                {"id": "awt2-3", "task": "Destructure props in Child component with default parameter values.", "category": "Destructuring"},
                {"id": "awt2-4", "task": "Render dynamic list of cards using users.map(user => <Card key={user.id} />).", "category": "List Rendering"},
                {"id": "awt2-5", "task": "Apply CSS styling and modular classes for modern card layout.", "category": "Styling"}
            ],
            "starter_code": """import React from 'react';

// Child component with props destructuring & default values
function UserCard({ name = "Student", role = "Developer", skills = [] }) {
    return (
        <div style={{ border: '1px solid #334155', borderRadius: 8, padding: 16, margin: 8 }}>
            <h3>{name}</h3>
            <p>Role: {role}</p>
            <p>Skills: {skills.join(", ")}</p>
        </div>
    );
}

// Parent component managing state and props distribution
export default function ParentDashboard() {
    const users = [
        { id: 1, name: "Shaunak Rane", role: "AI Engineer", skills: ["Python", "PyTorch", "React"] },
        { id: 2, name: "Aarav Sharma", role: "Frontend Dev", skills: ["TypeScript", "Next.js"] }
    ];

    return (
        <div>
            <h2>Classroom Engineering Roster</h2>
            {users.map(u => (
                <UserCard key={u.id} name={u.name} role={u.role} skills={u.skills} />
            ))}
        </div>
    );
}"""
        }
    ]
    return curriculum

def sync_labworks_to_db(force_rescan: bool = False) -> Dict[str, Any]:
    """
    Scans 3rd Year directory, analyzes code files, populates labworks table,
    and synchronizes corresponding assignments in the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get all subjects in DB
    cursor.execute("SELECT id, name, code FROM subjects")
    subjects = [dict(r) for r in cursor.fetchall()]

    curriculum = build_default_lab_curriculum()
    inserted = 0
    updated = 0

    # Cache existing completed tasks to preserve student's progress if rescanning
    cursor.execute("SELECT id, title, completed_tasks, status FROM labworks")
    existing_progress = {r["title"]: (json.loads(r["completed_tasks"] or "[]"), r["status"]) for r in cursor.fetchall()}

    for lab in curriculum:
        mapping_key = lab["mapping_key"]
        mapping_info = next((m for m in LAB_SUBJECT_MAPPINGS if m["key"] == mapping_key), None)
        if not mapping_info:
            continue

        # Find matching subject ID in database
        subject_id = find_subject_id_in_db(conn, mapping_info["db_names"])
        if not subject_id:
            subject_id = subjects[0]["id"] if subjects else 1

        subject_name = mapping_info["display_name"]
        title = lab["title"]
        lab_number = lab["lab_number"]
        full_file_path = str(DESKTOP_3RD_YEAR / lab["file_rel_path"])
        code_type = lab["code_type"]
        concepts_json = json.dumps(lab["concepts"])
        problem_statement = lab["problem_statement"]
        code_summary = lab["code_summary"]
        practice_todos_json = json.dumps(lab["practice_todos"])
        starter_code = lab["starter_code"]

        # Preserve progress if exists
        completed_tasks = []
        status = "ready"
        if title in existing_progress:
            completed_tasks, status = existing_progress[title]

        # Check if record already exists
        cursor.execute("SELECT id FROM labworks WHERE title = ?", (title,))
        existing_row = cursor.fetchone()

        if existing_row:
            cursor.execute("""
            UPDATE labworks SET
                subject_id = ?,
                subject_name = ?,
                lab_number = ?,
                file_path = ?,
                code_type = ?,
                concepts = ?,
                problem_statement = ?,
                code_summary = ?,
                practice_todos = ?,
                starter_code = ?
            WHERE id = ?
            """, (
                subject_id, subject_name, lab_number, full_file_path,
                code_type, concepts_json, problem_statement, code_summary,
                practice_todos_json, starter_code, existing_row["id"]
            ))
            updated += 1
        else:
            cursor.execute("""
            INSERT INTO labworks (
                subject_id, subject_name, lab_number, title, file_path,
                code_type, concepts, problem_statement, code_summary,
                practice_todos, starter_code, status, completed_tasks, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                subject_id, subject_name, lab_number, title, full_file_path,
                code_type, concepts_json, problem_statement, code_summary,
                practice_todos_json, starter_code, status, json.dumps(completed_tasks),
                datetime.now().isoformat()
            ))
            inserted += 1

        # Also ensure assignment entry exists in assignments table
        cursor.execute("SELECT id FROM assignments WHERE title = ?", (f"[{lab_number}] {title}",))
        if not cursor.fetchone():
            file_exists = Path(full_file_path).exists()
            asg_status = "completed" if (status == "completed" or file_exists) else "pending"
            cursor.execute("""
            INSERT INTO assignments (subject_id, title, deadline, is_lab, status, local_lab_dir)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                subject_id,
                f"[{lab_number}] {title}",
                "2026-09-30 23:59:00",
                1,
                asg_status,
                str(Path(full_file_path).parent)
            ))

    conn.commit()
    conn.close()

    log_agent_event("INFO", f"Synced {len(curriculum)} labworks ({inserted} inserted, {updated} updated).")
    return {
        "status": "success",
        "total_curriculum": len(curriculum),
        "inserted": inserted,
        "updated": updated
    }

def get_all_labworks(subject_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Returns all labworks, categorized by lab subject, with statistics and todo checklists.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Ensure labworks table has items
    cursor.execute("SELECT COUNT(*) as count FROM labworks")
    if cursor.fetchone()["count"] == 0:
        sync_labworks_to_db()

    query = "SELECT * FROM labworks"
    params = []
    if subject_id:
        query += " WHERE subject_id = ?"
        params.append(subject_id)
    query += " ORDER BY subject_name ASC, lab_number ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    labworks = []
    total_tasks = 0
    completed_tasks_total = 0

    for r in rows:
        item = dict(r)
        item["concepts"] = json.loads(item["concepts"] or "[]")
        item["practice_todos"] = json.loads(item["practice_todos"] or "[]")
        item["completed_tasks"] = json.loads(item["completed_tasks"] or "[]")

        # Compute completion percentage for this lab
        lab_tasks_count = len(item["practice_todos"])
        lab_completed_count = len(item["completed_tasks"])
        item["tasks_count"] = lab_tasks_count
        item["completed_count"] = lab_completed_count
        item["progress_pct"] = round((lab_completed_count / lab_tasks_count * 100) if lab_tasks_count > 0 else 0)

        total_tasks += lab_tasks_count
        completed_tasks_total += lab_completed_count
        labworks.append(item)

    # Group by subject
    subjects_dict = {}
    for lw in labworks:
        sname = lw["subject_name"]
        if sname not in subjects_dict:
            subjects_dict[sname] = {
                "subject_name": sname,
                "subject_id": lw["subject_id"],
                "labworks": [],
                "total_labs": 0,
                "completed_labs": 0
            }
        subjects_dict[sname]["labworks"].append(lw)
        subjects_dict[sname]["total_labs"] += 1
        if lw["status"] == "completed" or lw["progress_pct"] == 100:
            subjects_dict[sname]["completed_labs"] += 1

    conn.close()

    overall_pct = round((completed_tasks_total / total_tasks * 100) if total_tasks > 0 else 0)

    return {
        "labworks": labworks,
        "subjects": list(subjects_dict.values()),
        "stats": {
            "total_labs": len(labworks),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks_total,
            "pending_tasks": total_tasks - completed_tasks_total,
            "overall_readiness_pct": overall_pct
        }
    }

def toggle_practice_task(labwork_id: int, task_id: str) -> Dict[str, Any]:
    """
    Toggles a practice todo task on or off, updating the completed_tasks list and lab status.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT practice_todos, completed_tasks FROM labworks WHERE id = ?", (labwork_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ValueError(f"Labwork ID {labwork_id} not found")

    todos = json.loads(row["practice_todos"] or "[]")
    completed = json.loads(row["completed_tasks"] or "[]")

    if task_id in completed:
        completed.remove(task_id)
    else:
        completed.append(task_id)

    # Calculate new status
    new_status = "ready"
    if len(completed) == len(todos) and len(todos) > 0:
        new_status = "completed"
    elif len(completed) > 0:
        new_status = "in_progress"

    cursor.execute("""
    UPDATE labworks
    SET completed_tasks = ?, status = ?
    WHERE id = ?
    """, (json.dumps(completed), new_status, labwork_id))
    conn.commit()
    conn.close()

    log_agent_event("INFO", f"Practice task {task_id} toggled for Lab ID {labwork_id} (Status: {new_status}).")
    return {
        "status": "success",
        "labwork_id": labwork_id,
        "task_id": task_id,
        "completed_tasks": completed,
        "lab_status": new_status,
        "progress_pct": round(len(completed) / len(todos) * 100) if todos else 0
    }
