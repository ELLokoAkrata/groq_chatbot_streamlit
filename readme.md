# Psycho Bot Rebelde 🤖

## Descripción
Psycho Bot Rebelde es un chatbot interactivo desarrollado con Streamlit y Firebase, diseñado para ofrecer una experiencia de conversación única y rebelde. Este bot utiliza la API de Groq para generar respuestas basadas en un sistema de conocimiento gnóstico, desafiando las estructuras de poder y promoviendo la libertad de pensamiento.

## Características
- Interacción en tiempo real con un chatbot.
- Almacenamiento de conversaciones en Firestore.
- Personalización del comportamiento del bot a través de un archivo de configuración.
- Interfaz amigable y fácil de usar.
- El contexto de la conversación se limita a las cinco
  últimas interacciones guardadas en Firebase.

## Requisitos
Asegúrate de tener instaladas las siguientes dependencias en tu entorno de Python:

- Python 3.7 o superior
- Streamlit
- Firebase Admin SDK
- Groq

## Instalación
1. Clona este repositorio:
   ```bash
  https://github.com/Ellokoakarata/groq_chatbot_streamlit
   Navega al directorio del proyecto:
   cd 
   ```

2. Crea un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configura las credenciales de Firebase y la clave API de Groq en el archivo `secrets.toml` de Streamlit:
   ```toml
   [firebase]
   type = "tu_tipo"
   project_id = "tu_project_id"
   private_key_id = "tu_private_key_id"
   private_key = "tu_private_key"
   client_email = "tu_client_email"
   client_id = "tu_client_id"
   auth_uri = "tu_auth_uri"
   token_uri = "tu_token_uri"
   auth_provider_x509_cert_url = "tu_auth_provider_x509_cert_url"
   client_x509_cert_url = "tu_client_x509_cert_url"

   [GROQ_API_KEY]
   GROQ_API_KEY = "tu_groq_api_key"
   ```

## Uso
1. Inicia la aplicación Streamlit:
   ```bash
   streamlit run chat_bot.py
   ```

2. Abre tu navegador y ve a `http://localhost:8501`.

3. Introduce tu nombre para comenzar la conversación con el bot.
4. El comportamiento del bot se define en `system_prompt.txt`, que puedes modificar para adaptar su personalidad.

## Contribuciones
Las contribuciones son bienvenidas. Si deseas contribuir, por favor abre un issue o envía un pull request.

## Licencia
Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.