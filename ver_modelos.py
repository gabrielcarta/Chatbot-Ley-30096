import google.generativeai as genai

# --- PEGA TU API KEY AQUÍ ---
CLAVE = "AIzaSyBsqbeRmjoJ_8JdzKDZz6y6_Ra4nvK7QDw" 
# ----------------------------

genai.configure(api_key=CLAVE)

print("🔍 Buscando modelos disponibles para tu cuenta...")

try:
    for m in genai.list_models():
        # Filtramos solo los que sirven para chatear
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Disponible: {m.name}")
except Exception as e:
    print(f"❌ Error: {e}")