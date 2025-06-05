import os
import time
import streamlit as st
import firebase_admin
import uuid
from firebase_admin import credentials, firestore
from datetime import datetime
import random
from groq import Groq, InternalServerError

# -------------------------
# Configuración del System Prompt
# -------------------------
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    system_message = f.read()

# -------------------------
# Metaprompt opcional (contexto interno)
# -------------------------
metaprompt = """
Eres un asistente conversacional creativo, rebelde y subversivo. Evita repetir información innecesaria y sé conciso.
Verifica la info antes de decirla. Tienes hasta 5 conversaciones anteriores para crear contexto.
"""

# -------------------------
# Inicialización de Firebase
# -------------------------
firebase_secrets = st.secrets["firebase"]
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
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# -------------------------
# Inicialización de Groq
# -------------------------
api_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=api_key)

# -------------------------
# Interfaz de usuario con Streamlit
# -------------------------
# Mostrar logo
logo_url = (
    "https://firebasestorage.googleapis.com/v0/b/diario-ad840.appspot.com/o/"
    "c8d5e737-bd01-40b0-8c9f-721d5f123f91.webp?alt=media&token="
    "d01aeeac-48a2-41ca-82c4-ca092946bbc9"
)
st.image(logo_url, use_container_width=True)

with st.sidebar:
    st.write("   Groq chat-bot 🤖 IA + Desarrollo y creatividad")
    st.write("Se encuentra en etapa de prueba.")
    st.write("Reglas: Sé cordial, no expongas datos privados y no abuses del uso del Bot.")
    st.write("El Bot puede equivocarse, contrasta la info.")

# Generar o recuperar el UUID del usuario
if "user_uuid" not in st.session_state:
    st.session_state["user_uuid"] = str(uuid.uuid4())

st.title("Psycho Bot Rebelde 🤖")

st.markdown("""
**Guía para usar el bot rebelde:**

1. Ingresa el nombre que deseas usar y presiona **Confirmar**.
2. Escribe tu mensaje en la casilla y presiona **Enviar**.
3. Espera la respuesta del bot y sigue la conversación.
4. Usa siempre el mismo nombre para recuperar tu historial.
5. Cuando desees cerrar sesión, presiona **Cerrar Sesión**.
""")

# -------------------------
# Inicialización del estado de sesión
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# -------------------------
# Configuración Firestore
# -------------------------
now = datetime.now()
collection_name = "Groq_chatbot" + now.strftime("%Y-%m-%d")
document_name = st.session_state.get("user_uuid", str(uuid.uuid4()))
collection_ref = db.collection(collection_name)
document_ref = collection_ref.document(document_name)

# -------------------------
# Gestión del inicio de sesión
# -------------------------
if not st.session_state["logged_in"]:
    user_name = st.text_input("Introduce tu nombre para comenzar")
    confirm_button = st.button("Confirmar")
    if confirm_button and user_name:
        user_query = db.collection("usuarios_gcb").where("nombre", "==", user_name).get()
        if user_query:
            user_info = user_query[0].to_dict()
            st.session_state["user_uuid"] = user_info["user_uuid"]
            st.session_state["user_name"] = user_name
        else:
            new_uuid = str(uuid.uuid4())
            st.session_state["user_uuid"] = new_uuid
            user_doc_ref = db.collection("usuarios_gcb").document(new_uuid)
            user_doc_ref.set({"nombre": user_name, "user_uuid": new_uuid})
        st.session_state["logged_in"] = True
        st.rerun()

# Función para obtener un saludo rebelde aleatorio
def get_random_greeting():
    greetings = [
        "¡Saludazos, compa! ¿Listo para romper cadenas?",
        "Loquillo, ¿qué onda? ¡A reventar el sistema!",
        "¡Token al aire, psycho! Bienvenido a la revolución digital.",
        "¿Qué hay, mi hermano rebelde? ¡Vamos a desatar el caos!",
        "¡Epa, pandilla de mentes libres! La opresión se queda atrás."
    ]
    return random.choice(greetings)

# -------------------------
# Mostrar historial y campo de entrada
# -------------------------
if st.session_state["logged_in"]:
    st.write(f"Bienvenido de nuevo, {st.session_state.get('user_name', 'Usuario')}!")
    
    # Cargar mensajes previos de Firestore
    doc_data = document_ref.get().to_dict()
    if doc_data and "messages" in doc_data:
        st.session_state["messages"] = doc_data["messages"]
    
    # Si es la primera vez, insertar un saludo rebelde
    if not st.session_state["messages"]:
        st.session_state["messages"].append({"role": "assistant", "content": get_random_greeting()})
    
    with st.container():
        st.markdown("### Historial de Conversación")
        for msg in st.session_state["messages"]:
            col1, col2 = st.columns([1, 5])
            if msg["role"] == "user":
                with col1:
                    st.markdown("**Tú 🧑:**")
                with col2:
                    st.info(msg["content"])
            else:
                with col1:
                    st.markdown("**IA 🤖:**")
                with col2:
                    st.success(msg["content"])

    # Entrada de mensaje
    prompt = st.chat_input("Escribe tu mensaje:", key="new_chat_input")
    if prompt:
        st.session_state["messages"].append({"role": "user", "content": prompt})
        context = st.session_state["messages"][-5:]
        with st.spinner("El bot está pensando..."):
            messages_to_send = [
                {"role": "system", "content": system_message},
                {"role": "system", "content": metaprompt},
            ] + context

            chat_completion = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=messages_to_send,
                temperature=1,
                max_completion_tokens=6080,
                top_p=1,
                stream=False,
                stop=None,
            )
        
        if chat_completion.choices:
            generated_text = chat_completion.choices[0].message.content
        else:
            generated_text = "Lo siento, no pude generar una respuesta."
        
        st.session_state["messages"].append({"role": "assistant", "content": generated_text})
        document_ref.set({"messages": st.session_state["messages"]})
        st.rerun()

# -------------------------
# Gestión del cierre de sesión
# -------------------------
if st.session_state["logged_in"]:
    if st.button("Cerrar Sesión"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.write("Sesión cerrada. ¡Gracias por usar el Psycho_Chatbot!")
        st.rerun()
