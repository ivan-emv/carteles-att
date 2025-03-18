import streamlit as st
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from datetime import datetime
import os
import tempfile

def obtener_dia_semana(fecha, idiomas):
    dias = {
        "Español": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
        "Portugués": ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"],
        "Inglés": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    }
    try:
        fecha_dt = datetime.strptime(fecha, "%d/%m/%Y")
        dias_traducidos = [dias.get(idioma, dias["Español"])[fecha_dt.weekday()] for idioma in idiomas]
        return f"{' / '.join(dias_traducidos)} - {fecha}"
    except ValueError:
        return "Día inválido"

def generar_cartel(ciudad, fecha, actividad, hora_encuentro, punto_encuentro, nombre_guia, idiomas, archivo):
    # Guardar el archivo cargado en un directorio temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
        tmp_file.write(archivo.getvalue())
        tmp_file_path = tmp_file.name

    if not os.path.exists(tmp_file_path):
        return "Error: No se encuentra el archivo base. Asegúrate de que el archivo está cargado correctamente."
    
    doc = Document(tmp_file_path)
    
    fecha_formateada = obtener_dia_semana(fecha, idiomas)
    
    traducciones = {
        "Español": {"Bienvenidos": "¡Bienvenidos!", "Guía": "GUÍA", "Actividad": "Actividad", "Salida": "Salida", "PuntodeEncuentro": "Punto de Encuentro", "HoradeEncuentro": "Hora de Encuentro"},
        "Portugués": {"Bienvenidos": "Bem-Vindos!", "Guía": "GUIA", "Actividad": "Atividade", "Salida": "Saída", "PuntodeEncuentro": "Ponto de Encontro", "HoradeEncuentro": "Hora de Encontro"},
        "Inglés": {"Bienvenidos": "Welcome!", "Guía": "GUIDE", "Actividad": "Activity", "Salida": "Departure", "PuntodeEncuentro": "Meeting Point", "HoradeEncuentro": "Meeting Hour"}
    }
    
    textos_traducidos = [traducciones.get(idioma, traducciones["Español"]) for idioma in idiomas]
    
    bienvenida = " / ".join([texto['Bienvenidos'] for texto in textos_traducidos])
    guia_traducido = " / ".join([texto['Guía'] for texto in textos_traducidos])
    actividad_traducida = " / ".join([texto['Actividad'] for texto in textos_traducidos]) + f":\n - {actividad}"
    punto_de_encuentro = " / ".join([texto['PuntodeEncuentro'] for texto in textos_traducidos])
    hora_de_encuentro = " / ".join([texto['HoradeEncuentro'] for texto in textos_traducidos])
    
    reemplazos = {
        "(BIENVENIDA)": bienvenida,
        "(CIUDAD)": f"{ciudad}",
        "📅": f"📅 {fecha_formateada}",
        "🚌": f"🚌 {actividad_traducida}\n",
        "⏰": f"⏰ {hora_de_encuentro}: {hora_encuentro}",
        "📍": f"📍 {punto_de_encuentro}: {punto_encuentro}\n",
        "🧑‍💼": f"🧑‍💼 {guia_traducido}: {nombre_guia}"
    }
    
    for p in doc.paragraphs:
        for key, value in reemplazos.items():
            if key in p.text:
                p.text = p.text.replace(key, value)
                for run in p.runs:
                    if key in ["(BIENVENIDA)", "(CIUDAD)"]:
                        run.font.name = "Arial Black"
                        run.font.size = Pt(18)
                        run.font.color.rgb = RGBColor(44, 66, 148)
                        p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                    elif key == "📅":
                        run.font.name = "Arial Black"
                        run.font.size = Pt(14)
                        run.font.color.rgb = RGBColor(44, 66, 148)
                        p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                    elif key == "🚌":
                        run.font.name = "Arial Black"
                        run.font.size = Pt(14)
                        run.font.color.rgb = RGBColor(44, 66, 148)
                        p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                    elif "⏰" in p.text:
                        run.font.name = "Arial Black"
                        run.font.size = Pt(16)
                        run.font.color.rgb = RGBColor(44, 66, 148)
                        p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                    else:
                        run.font.name = "Arial Black"
                        run.font.size = Pt(14)
                        run.font.color.rgb = RGBColor(44, 66, 148)
                        p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
    
    output_path = os.path.join(os.getcwd(), f"Cartel_{ciudad}_{'_'.join(idiomas)}.docx")
    doc.save(output_path)
    return output_path

st.title("Generador de Carteles para Pasajeros")

idiomas_disponibles = ["Español", "Portugués", "Inglés"]
idiomas_seleccionados = st.multiselect("Seleccione los idiomas:", idiomas_disponibles, default=["Español"])

archivo = st.file_uploader("Cargue el archivo base", type=["docx"])

if len(idiomas_seleccionados) == 0:
    st.warning("Debe seleccionar al menos un idioma para generar el cartel.")
elif archivo is None:
    st.warning("Debe cargar el archivo base.")
else:
    ciudad = st.text_input("Ingrese la ciudad:")
    fecha = st.text_input("Ingrese la fecha (dd/mm/aaaa):")
    actividad = st.text_input("Ingrese el nombre de la actividad principal:")
    hora_encuentro = st.text_input("Ingrese la hora de encuentro:")
    punto_encuentro = st.text_input("Ingrese el punto de encuentro:")
    nombre_guia = st.text_input("Ingrese el nombre del guía:")

    if st.button("Generar Cartel"):
        archivo_generado = generar_cartel(ciudad, fecha, actividad, hora_encuentro, punto_encuentro, nombre_guia, idiomas_seleccionados, archivo)
        if archivo_generado.startswith("Error"):
            st.error(archivo_generado)
        else:
            with open(archivo_generado, "rb") as file:
                st.download_button(label="Descargar Cartel", data=file, file_name=os.path.basename(archivo_generado), mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
