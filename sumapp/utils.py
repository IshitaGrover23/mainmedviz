import fitz  
import re
import spacy
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from transformers import BartTokenizer, BartForConditionalGeneration

# Load spaCy model for named entity recognition
nlp = spacy.load("en_core_web_sm")

# Load BART model and tokenizer
tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

def extract_text_from_pdf(pdf_file):
    try:
        text = ''
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
        pdf_document.close()
        if not text.strip():
            raise ValueError("No text extracted from PDF.")
        return text
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from PDF: {e}")

def preprocess_text(text):
    # Remove extra spaces, new lines, and other unwanted characters
    processed_text = re.sub(r'\s+', ' ', text).strip()
    return processed_text

def extract_named_entities(text):
    doc = nlp(text)
    entities = {}
    for ent in doc.ents:
        if ent.label_ not in entities:
            entities[ent.label_] = []
        entities[ent.label_].append(ent.text)
    return entities

def summarize_text(text, num_sentences=5):
    # Split the text into sentences
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    
    # If there are fewer sentences than requested, return all sentences
    if len(sentences) <= num_sentences:
        return " ".join(sentences)
    
    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(sentences)
    
    # Perform K-means clustering
    num_clusters = min(len(sentences), num_sentences)
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    kmeans.fit(X)
    
    # Get the sentences closest to the cluster centers
    order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
    
    summary_sentences = []
    for i in range(num_clusters):
        for idx in order_centroids[i]:
            if idx < len(sentences):
                summary_sentences.append(sentences[idx])
                break
    
    # Sort the summary sentences based on their original order in the text
    summary_sentences.sort(key=lambda x: sentences.index(x))
    
    return " ".join(summary_sentences)

def extract_key_points(text):
    # Extract named entities
    entities = extract_named_entities(text)
    
    # Summarize the text
    summary = summarize_text(text)
    
    # Split the summary into sentences
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', summary)
    
    key_points = {}
    for i, sentence in enumerate(sentences, 1):
        key_points[f'Key Point {i}'] = sentence
    
    # Add named entities to key points
    for entity_type, entity_list in entities.items():
        if entity_list:
            key_points[f'{entity_type} Entities'] = ', '.join(set(entity_list))
    
    return key_points