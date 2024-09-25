import os
import time
import streamlit as st
import firebase_admin
import uuid
from firebase_admin import credentials, firestore
from datetime import datetime
from groq import Groq, InternalServerError


# Función para resumir mensajes
def summarize_messages(messages):
    stop_words = {"el", "la", "y", "de", "que", "en", "a", "los", "las", "por", "con", "un", "una", "es", "se", "del", "al"}  # Ejemplo de stop words
    summary = []
    for msg in messages:
        # Filtrar mensajes y eliminar stop words
        filtered_content = ' '.join([word for word in msg['content'].split() if word.lower() not in stop_words])
        if filtered_content:  # Solo agregar si hay contenido relevante
            summary.append(f"{msg['role']}: {filtered_content}")
    return "\n".join(summary)


# Acceder a las credenciales de Firebase almacenadas como secreto
firebase_secrets = st.secrets["firebase"]

# Crear un objeto de credenciales de Firebase con los secretos
cred = credentials.Certificate({
    "type": firebase_secrets["type"],
    "project_id": firebase_secrets["project_id"],
    "private_key_id": firebase_secrets["private_key_id"],
    "private_key": firebase_secrets["private_key"],
    "client_email": firebase_secrets["client_email"],
    "client_id": firebase_secrets["client_id"],
    "auth_uri": firebase_secrets["auth_uri"],
    "token_uri": firebase_secrets["token_uri"],
    "auth_provider_x509_cert_url": firebase_secrets["auth_provider_x509_cert_url"],
    "client_x509_cert_url": firebase_secrets["client_x509_cert_url"]
})

# Inicializar la aplicación de Firebase con las credenciales
if not firebase_admin._apps:
    default_app = firebase_admin.initialize_app(cred)

# Acceder a la base de datos de Firestore
db = firestore.client()


# Acceder a la clave API almacenada como secreto
api_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=api_key)


# Display logo
logo_url= 'https://firebasestorage.googleapis.com/v0/b/diario-ad840.appspot.com/o/c8d5e737-bd01-40b0-8c9f-721d5f123f91.webp?alt=media&token=d01aeeac-48a2-41ca-82c4-ca092946bbc9'
st.image(logo_url, use_column_width=True)

with st.sidebar:
    st.write("   Groq chat-bot 🤖 IA + Desarrollo y creatividad")
    st.write("Se encuentra en etapa de prueba.")
    st.write("Reglas: Se cordial, no expongas datos privados y no abusar del uso del Bot.")
    st.write("El Bot se puede equivocar, siempre contrasta la info.")

# Generar o recuperar el UUID del usuario
if "user_uuid" not in st.session_state:
    st.session_state["user_uuid"] = str(uuid.uuid4())

st.title("Psycho Bot Rebelde 🤖")  # Cambiado el título para reflejar el nuevo enfoque

# Primero, renderizar el contenido con markdown en rojo
st.markdown("""
Guía para usar el bot rebelde

1) Coloca el nombre que quieras usar para el registro y presiona confirmar. No te preocupes si en la primera sesión dice: 'None'.

2) Luego de iniciar sesión, escribe tu mensaje en la casilla especial y presiona el botón enviar.

3) Luego espera la respuesta, y después de que el bot responda, borra el mensaje y escribe tu nuevo mensaje.

4) Cuando ya no quieras hablar con el bot, cierra sesión.

5) Siempre usa el mismo nombre de sesión, esto te ayudará a recuperar la sesión.
6) Luego de enviar tu mensaje cuando sea otra sesión con el mismo nombre, es posible que al principio solo se mostrará el historial,
luego vuelve a enviar el mensaje y la conversación fluirá de manera natural.""")

# Mensaje de sistema
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    system_message = f.read()

# Inicializar st.session_state
if "user_uuid" not in st.session_state:
    st.session_state["user_uuid"] = None  # Cambiado a None inicialmente
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None

# Configuración inicial de Firestore
now = datetime.now()
collection_name = "Groq_chatbot" + now.strftime("%Y-%m-%d")
document_name = st.session_state.get("user_uuid", str(uuid.uuid4()))
collection_ref = db.collection(collection_name)
document_ref = collection_ref.document(document_name)

# Gestión del Inicio de Sesión
if not st.session_state.get("logged_in", False):
    user_name = st.text_input("Introduce tu nombre para comenzar")
    confirm_button = st.button("Confirmar")
    if confirm_button and user_name:
        # Buscar en Firestore si el nombre de usuario ya existe
        user_query = db.collection("usuarios_gcb").where("nombre", "==", user_name).get()
        if user_query:
            # Usuario existente encontrado, usar el UUID existente
            user_info = user_query[0].to_dict()
            st.session_state["user_uuid"] = user_info["user_uuid"]
            st.session_state["user_name"] = user_name
        else:
            # Usuario nuevo, generar un nuevo UUID
            new_uuid = str(uuid.uuid4())
            st.session_state["user_uuid"] = new_uuid
            user_doc_ref = db.collection("usuarios_gcb").document(new_uuid)
            user_doc_ref.set({"nombre": user_name, "user_uuid": new_uuid})
        st.session_state["logged_in"] = True

        # Forzar a Streamlit a reejecutar el script
        st.rerun()

# Solo mostrar el historial de conversación y el campo de entrada si el usuario está "logged_in"
if st.session_state.get("logged_in", False):
    st.write(f"Bienvenido de nuevo, {st.session_state.get('user_name', 'Usuario')}!")
    
    doc_data = document_ref.get().to_dict()
    if doc_data and 'messages' in doc_data:
        st.session_state['messages'] = doc_data['messages']
    
    with st.container(border=True):
        st.markdown("### Historial de Conversación")
        for msg in st.session_state['messages']:
            col1, col2 = st.columns([1, 5])
            if msg["role"] == "user":
                with col1:
                    st.markdown("**Tú 🧑:**")
                with col2:
                    st.info(msg['content'])
            else:
                with col1:
                    st.markdown("**IA 🤖:**")
                with col2:
                    st.success(msg['content'])

    prompt = st.chat_input("Escribe tu mensaje:", key="new_chat_input")
    if prompt:
        # Añadir mensaje del usuario al historial inmediatamente
        st.session_state['messages'].append({"role": "user", "content": prompt})
        
        # Mostrar spinner mientras se espera la respuesta del bot
        with st.spinner('El bot está pensando...'):
            user_name = st.session_state.get("user_name", "Usuario desconocido")
            # Resumir los últimos mensajes relevantes
            relevant_messages = st.session_state['messages'][-5:]  # Obtener los últimos 5 mensajes
            summarized_context = summarize_messages(relevant_messages)  # Función para resumir mensajes
            internal_prompt = system_message + "\n\n" + summarized_context
            internal_prompt += f"\n\n{user_name}: {prompt}"

        # Cambiar aquí para incluir el argumento 'messages'
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": internal_prompt}
            ],
            model="llama-3.1-70b-versatile",
            temperature=0.88,
            max_tokens=2800,
            top_p=0.9,
            stop=None,
        )

        # Asegúrate de que la respuesta del bot se maneje correctamente
        if chat_completion.choices:
            generated_text = chat_completion.choices[0].message.content
        else:
            generated_text = "Lo siento, no pude generar una respuesta."

        # Añadir respuesta del bot al historial de mensajes
        st.session_state['messages'].append({"role": "assistant", "content": generated_text})
        document_ref.set({'messages': st.session_state['messages']})
        st.rerun()

# Gestión del Cierre de Sesión
if st.session_state.get("logged_in", False):
    if st.button("Cerrar Sesión"):
        keys_to_keep = []
        for key in list(st.session_state.keys()):
            if key not in keys_to_keep:
                del st.session_state[key]
        st.write("Sesión cerrada. ¡Gracias por usar el  Psycho_Chatbot!")
        st.rerun()
