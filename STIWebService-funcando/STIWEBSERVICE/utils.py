import joblib

# Cargar el modelo, vectorizador y encoder
modelo = joblib.load("modelo_prioridad.pkl")
vectorizer = joblib.load("vectorizer.pkl")
label_encoder = joblib.load("label_encoder.pkl")

def predecir_prioridad(titulo, descripcion):
    """
    Función para predecir la prioridad de un ticket basado en su título y descripción.
    """
    # Preprocesar texto
    texto = titulo + " " + descripcion
    texto_tfidf = vectorizer.transform([texto])

    # Hacer predicción
    prediccion = modelo.predict(texto_tfidf)
    prioridad = label_encoder.inverse_transform(prediccion)[0]
    return prioridad
