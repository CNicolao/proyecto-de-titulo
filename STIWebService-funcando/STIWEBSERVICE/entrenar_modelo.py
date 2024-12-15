import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Cargar datos históricos (asegúrate de tener el archivo tickets.csv)
data = pd.read_csv("tickets.csv")

# Unir título y descripción
data['texto'] = data['titulo'] + " " + data['descripcion']

# Separar características (X) y etiquetas (y)
X = data['texto']
y = data['prioridad']

# Convertir etiquetas en valores numéricos
le = LabelEncoder()
y = le.fit_transform(y)

# Dividir datos en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Vectorizar texto
vectorizer = TfidfVectorizer()
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# Entrenar el modelo
modelo = MultinomialNB()
modelo.fit(X_train_tfidf, y_train)

# Evaluar el modelo
y_pred = modelo.predict(X_test_tfidf)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred, target_names=le.classes_))

# Guardar modelo, vectorizador y encoder
joblib.dump(modelo, "modelo_prioridad.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")
joblib.dump(le, "label_encoder.pkl")
