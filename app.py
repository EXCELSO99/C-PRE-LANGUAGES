import os
import json
import re
import urllib.request
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

PORT = int(os.environ.get("PORT", 5000))
HOST = os.environ.get("HOST", "0.0.0.0")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

NIVELES_ORDEN = ["Easy", "Medium", "Hard", "Expert/Nativo"]

IDIOMAS_DATOS = [
    ("Inglés", "en-US", "Hello", "I am a student", "One, two, three, four, five", "Thank you", "I practice English every day", "Yesterday I studied English", "Tomorrow I will practice more", "If I practice daily, I improve fast", "Piece of cake"),
    ("Español", "es-ES", "Hola", "Soy estudiante", "Uno, dos, tres, cuatro, cinco", "Gracias", "Practico español todos los días", "Ayer estudié español", "Mañana practicaré más", "Si practico a diario, avanzo rápido", "Pan comido"),
    ("Portugués", "pt-BR", "Olá", "Eu sou estudante", "Um, dois, três, quatro, cinco", "Obrigado", "Eu pratico português todo dia", "Ontem eu estudei português", "Amanhã vou praticar mais", "Se eu praticar todo dia, melhoro rápido", "Moleza"),
    ("Francés", "fr-FR", "Bonjour", "Je suis étudiant", "Un, deux, trois, quatre, cinq", "Merci", "Je pratique le français chaque jour", "Hier j'ai étudié le français", "Demain je pratiquerai plus", "Si je pratique chaque jour, je progresse", "C'est du gâteau"),
    ("Alemán", "de-DE", "Hallo", "Ich bin Schüler", "Eins, zwei, drei, vier, fünf", "Danke", "Ich übe jeden Tag Deutsch", "Gestern habe ich Deutsch gelernt", "Morgen werde ich mehr üben", "Wenn ich täglich übe, werde ich besser", "Ein Kinderspiel"),
    ("Italiano", "it-IT", "Ciao", "Sono uno studente", "Uno, due, tre, quattro, cinque", "Grazie", "Pratico italiano ogni giorno", "Ieri ho studiato italiano", "Domani praticherò di più", "Se mi esercito ogni giorno, miglioro", "Un gioco da ragazzi"),
    ("Chino Mandarín", "zh-CN", "Ni hao", "Wo shi xuesheng", "yi, er, san, si, wu", "Xiexie", "Wo meitian lianxi zhongwen", "Zuotian wo xuexi le zhongwen", "Mingtian wo hui duo lianxi", "Ruguo wo meitian lianxi jiu hui jinbu", "Xiao cai yi die"),
    ("Japonés", "ja-JP", "Konnichiwa", "Watashi wa gakusei desu", "ichi, ni, san, shi, go", "Arigato", "Mainichi nihongo o renshu shimasu", "Kino nihongo o benkyo shimashita", "Ashita motto renshu shimasu", "Mainichi renshu sureba jotatsu shimasu", "Ocha-no-ko saisai"),
    ("Coreano", "ko-KR", "Annyeonghaseyo", "Jeo-neun hak-saeng-i-e-yo", "ha-na, dul, set, net, da-seot", "Gamsahamnida", "Maeil han-gu-geo-reul yeon-seup-hae-yo", "Eo-je han-gu-geo-reul gong-bu-haet-seo-yo", "Nae-il deo yeon-seup-hal geo-ye-yo", "Maeil yeon-seup-ha-myeon neur-eo-yo", "Sik-eun juk meok-gi"),
    ("Árabe", "ar-SA", "Marhaban", "Ana talib", "wahid, ithnan, thalathah, arba'ah, khamsah", "Shukran", "Atadarrab ala al-arabiyyah kull yawm", "Darastu al-arabiyyah bil-ams", "Sa'atadarrab akthar ghadan", "Idha tadarrabtu yawmiyyan ataqaddam", "Ashal min shurbat ma'"),
    ("Ruso", "ru-RU", "Privet", "Ya student", "odin, dva, tri, chetyre, pyat", "Spasibo", "Ya kazhdyy den treniruyus", "Vchera ya uchil russkiy", "Zavtra ya budu trenirovatsya bolshe", "Esli treniruyus kazhdyy den, uluchshu", "Proshche prostogo"),
    ("Hindi", "hi-IN", "Namaste", "Main chhatra hoon", "ek, do, teen, chaar, paanch", "Dhanyavaad", "Main roz abhyaas karta hoon", "Kal maine padhaai ki", "Kal main aur abhyaas karoonga", "Agar roz abhyaas karoonga to sudhaar hoga", "Baayein haath ka khel"),
    ("Bengalí", "bn-BD", "Nomoshkar", "Ami chhatro", "ek, dui, tin, char, pach", "Dhonnobad", "Ami protidin onushilon kori", "Gotokal ami porechi", "Agamikal aro onushilon korbo", "Protidin onushilon korle unnoti hobe", "Bam hater khel"),
    ("Turco", "tr-TR", "Merhaba", "Ben ogrenciyim", "bir, iki, uc, dort, bes", "Tesekkurler", "Her gun pratik yapiyorum", "Dun ders calistim", "Yarin daha cok pratik yapacagim", "Her gun pratik yaparsam gelisirim", "Cocuk oyuncagi"),
    ("Neerlandés", "nl-NL", "Hallo", "Ik ben student", "een, twee, drie, vier, vijf", "Dank je", "Ik oefen elke dag", "Gisteren heb ik gestudeerd", "Morgen ga ik meer oefenen", "Als ik dagelijks oefen, word ik beter", "Een fluitje van een cent"),
    ("Polaco", "pl-PL", "Czesc", "Jestem studentem", "jeden, dwa, trzy, cztery, piec", "Dziekuje", "Codziennie cwicze", "Wczoraj sie uczylem", "Jutro bede cwiczyc wiecej", "Jesli cwicze codziennie, robie postep", "Bulka z maslem"),
    ("Sueco", "sv-SE", "Hej", "Jag ar student", "ett, tva, tre, fyra, fem", "Tack", "Jag ovar varje dag", "Igar pluggade jag", "Imorgon ska jag ova mer", "Om jag ovar varje dag blir jag battre", "En barnlek"),
    ("Griego", "el-GR", "Geia sou", "Eimai foititis", "ena, dyo, tria, tessera, pente", "Efcharisto", "Exaskoumai kathe mera", "Chthes diavasa", "Avrio tha exaskitho perissotero", "An exaskoumai kathimerina veltionomai", "Paichnidaki"),
    ("Vietnamita", "vi-VN", "Xin chao", "Toi la sinh vien", "mot, hai, ba, bon, nam", "Cam on", "Toi luyen tap moi ngay", "Hom qua toi da hoc", "Ngay mai toi se luyen tap them", "Neu luyen tap moi ngay toi se tien bo", "De nhu an keo"),
    ("Persa", "fa-IR", "Salam", "Man daneshjoo hastam", "yek, do, seh, chahar, panj", "Mamnoon", "Har rooz tamrin mikonam", "Dirooz dars khandam", "Farda bishtar tamrin mikonam", "Agar har rooz tamrin konam pishraft mikonam", "Mesl-e ab khordan"),
]

DICCIONARIO_GLOBAL = {
    "hello": ("Hola", "Saludo estándar en inglés (formal e informal).", "Hello! How are you doing today?"),
    "hi": ("Hola", "Saludo corto y cercano en inglés.", "Hi, nice to meet you!"),
    "good morning": ("Buenos días", "Saludo usado desde que amanece hasta el mediodía.", "Good morning, class!"),
    "good afternoon": ("Buenas tardes", "Saludo desde el mediodía hasta el atardecer.", "Good afternoon, sir."),
    "good night": ("Buenas noches", "Despedida al final del día o antes de dormir.", "Good night, sleep well."),
    "thank you": ("Gracias", "Expresión general para agradecer.", "Thank you very much for your help."),
    "thanks": ("Gracias", "Forma breve y cotidiana de agradecer.", "Thanks for coming!"),
    "please": ("Por favor", "Palabra de cortesía al pedir algo.", "Water, please."),
    "sorry": ("Lo siento / Perdón", "Para pedir disculpas.", "Sorry, I didn't understand."),
    "yes": ("Sí", "Afirmación directa.", "Yes, I am ready."),
    "no": ("No", "Negación directa.", "No, thank you."),
    "water": ("Agua", "Sustantivo incontable básico.", "I drink water every morning."),
    "house": ("Casa", "Vivienda o hogar físico.", "My house is near the park."),
    "book": ("Libro", "Sustantivo contable.", "This book is very useful."),
    "friend": ("Amigo / Amiga", "Persona cercana.", "He is my best friend."),
    "time": ("Tiempo / Hora", "Se usa tanto para el tiempo como para la hora.", "What time is it?"),
    "student": ("Estudiante", "Persona que cursa estudios.", "I am a dedicated student."),
    "practice": ("Practicar / Práctica", "Funciona como verbo y sustantivo.", "Practice makes progress."),
    "one": ("Uno (1)", "Primer número cardinal.", "I have one question."),
    "two": ("Dos (2)", "Segundo número cardinal.", "Give me two minutes."),
    "three": ("Tres (3)", "Tercer número cardinal.", "Three books on the table."),
    "four": ("Cuatro (4)", "Cuarto número cardinal.", "Four seasons in a year."),
    "five": ("Cinco (5)", "Quinto número cardinal.", "Five days a week."),
    "piece of cake": ("Pan comido / Muy fácil", "Modismo nativo para algo sencillo de hacer.", "The exam was a piece of cake."),
}

NOTICIAS = [
    "Tip diario: Leer 5 frases en voz alta cada día mejora tu fluidez y seguridad al hablar.",
    "Tip diario: No traduzcas palabra por palabra; aprende bloques completos como saludos y respuestas.",
    "Tip diario: Domina primero los números y presentaciones antes de pasar a tiempos complejos.",
    "Tip diario: Cuando falles una pregunta en el examen, lee la explicación para fijar la regla.",
    "Tip diario: Usa los 10 juegos rápidos después de cada rama para reforzar tu memoria.",
]

def construir_curso(nombre, lang_code, saludo, identidad, numeros, gracias, rutina, pasado, futuro, condicional, modismo):
    def crear_rama(num, titulo, tema, clave, distractor):
        clases = [
            f"Clase 1 · Base: En {nombre}, la expresión clave para '{tema}' es: \"{clave}\".",
            f"Clase 2 · Contraste: No la confundas con \"{distractor}\", que cumple otra función distinta.",
            f"Clase 3 · Uso real: Imagina una conversación cotidiana y aplica \"{clave}\" con naturalidad.",
            f"Clase 4 · Estructura: Observa el orden exacto de las palabras en \"{clave}\".",
            f"Clase 5 · Listo para evaluar: Repasa \"{clave}\" antes de abrir el examen de 20 puntos."
        ]
        preguntas = [
            {
                "q": f"Verdadero o Falso: \"{clave}\" corresponde al tema de {tema} en {nombre}.",
                "ops": ["Verdadero", "Falso"],
                "ok": "Verdadero",
                "exp": f"Correcto: \"{clave}\" es la expresión trabajada en {tema}."
            },
            {
                "q": f"Selecciona la expresión correcta de {tema} en {nombre}:",
                "ops": [clave, distractor],
                "ok": clave,
                "exp": f"La opción correcta es \"{clave}\"."
            },
            {
                "q": f"¿Cuál de estas frases sirve como contraste (tema diferente) frente a \"{clave}\"?",
                "ops": [distractor, clave],
                "ok": distractor,
                "exp": f"\"{distractor}\" pertenece a otro bloque temático."
            },
            {
                "q": f"Escribe la expresión clave de esta rama en {nombre}:",
                "tipo": "texto",
                "ok": clave.lower(),
                "exp": f"Se esperaba escribir: {clave}"
            },
            {
                "q": f"Verdadero o Falso: \"{distractor}\" significa lo mismo que \"{clave}\".",
                "ops": ["Verdadero", "Falso"],
                "ok": "Falso",
                "exp": f"Falso: ambas expresiones tienen significados y usos distintos."
            }
        ]
        return {
            "rama": f"Rama {num}: {titulo}",
            "clave": clave,
            "clases": clases,
            "preguntas": preguntas
        }

    niveles = {
        "Easy": [
            crear_rama(1, "Identidad y Presentación", "identidad", identidad, saludo),
            crear_rama(2, "Saludos Básicos", "saludos", saludo, gracias),
            crear_rama(3, "Números", "números", numeros, rutina),
            crear_rama(4, "Agradecimiento y Cortesía", "agradecimiento", gracias, saludo),
            crear_rama(5, "Rutina Diaria", "rutina", rutina, pasado),
            crear_rama(6, "Conversación Inicial", "inicio de diálogo", saludo, futuro),
            crear_rama(7, "Cierre Nivel Easy", "práctica básica", rutina, modismo),
        ],
        "Medium": [
            crear_rama(1, "Tiempo Pasado", "pasado", pasado, rutina),
            crear_rama(2, "Tiempo Futuro", "futuro", futuro, pasado),
            crear_rama(3, "Contraste Presente / Pasado", "tiempos verbales", rutina, pasado),
            crear_rama(4, "Planes y Metas", "planes futuros", futuro, gracias),
            crear_rama(5, "Cierre Nivel Medium", "fluidez intermedia", pasado, modismo),
        ],
        "Hard": [
            crear_rama(1, "Condicionales", "condicionales", condicional, rutina),
            crear_rama(2, "Causa y Efecto", "argumentación", condicional, pasado),
            crear_rama(3, "Cierre Nivel Hard", "dominio avanzado", condicional, futuro),
        ],
        "Expert/Nativo": [
            crear_rama(1, "Modismos Reales", "modismos", modismo, rutina),
            crear_rama(2, "Expresión Natural", "giros nativos", modismo, condicional),
            crear_rama(3, "Maestría Final", "dominio nativo", modismo, pasado),
        ]
    }

    juegos = [
        {"n": 1, "t": "Saludo", "q": f"¿Cómo saludas en {nombre}?", "ops": [saludo, gracias, numeros], "ok": saludo},
        {"n": 2, "t": "Números", "q": f"Selecciona los números en {nombre}:", "ops": [numeros, saludo, pasado], "ok": numeros},
        {"n": 3, "t": "Gracias", "q": f"¿Cómo agradeces en {nombre}?", "ops": [gracias, identidad, futuro], "ok": gracias},
        {"n": 4, "t": "Identidad", "q": f"Elige la frase de presentación en {nombre}:", "ops": [identidad, modismo, gracias], "ok": identidad},
        {"n": 5, "t": "Rutina", "q": f"Selecciona la acción cotidiana en {nombre}:", "ops": [rutina, numeros, saludo], "ok": rutina},
        {"n": 6, "t": "Pasado", "q": f"¿Cuál expresa una acción en pasado en {nombre}?", "ops": [pasado, futuro, saludo], "ok": pasado},
        {"n": 7, "t": "Futuro", "q": f"¿Cuál expresa un plan a futuro en {nombre}?", "ops": [futuro, pasado, gracias], "ok": futuro},
        {"n": 8, "t": "Condicional", "q": f"Elige la estructura condicional en {nombre}:", "ops": [condicional, identidad, numeros], "ok": condicional},
        {"n": 9, "t": "Modismo", "q": f"Selecciona la expresión idiomática en {nombre}:", "ops": [modismo, saludo, rutina], "ok": modismo},
        {"n": 10, "t": "Desafío Final", "q": f"Identifica la frase nativa de dominio en {nombre}:", "ops": [modismo, gracias, numeros], "ok": modismo},
    ]

    return {
        "nombre": nombre,
        "lang_code": lang_code,
        "saludo": saludo,
        "rutina": rutina,
        "numeros": numeros,
        "niveles": niveles,
        "juegos": juegos
    }

CURSOS_COMPLETOS = {item[0]: construir_curso(*item) for item in IDIOMAS_DATOS}

def consultar_profesor_ia(idioma, pregunta):
    q = (pregunta or "").strip()
    if not q:
        return "Escribe una palabra, frase o duda para ayudarte."

    if GEMINI_API_KEY:
        prompt = (
            f"Actúa como un profesor de {idioma} claro, cercano y preciso. "
            f"Responde en español. Si el alumno escribe una palabra o frase (ej. 'hello'), "
            f"indica su traducción exacta, cuándo se usa, una guía breve de pronunciación y un ejemplo real. "
            f"Si hace una pregunta de gramática o vocabulario, respóndela directamente y sin rodeos. "
            f"Idioma seleccionado: {idioma}. Consulta del alumno: {q}"
        )
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
        payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                txt = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                if txt:
                    return txt.strip()
        except Exception:
            pass

    limpia = re.sub(r"[^a-zA-Z\s]", "", q).strip().lower()
    if limpia in DICCIONARIO_GLOBAL:
        trad, uso, ej = DICCIONARIO_GLOBAL[limpia]
        return f"• Significado: {trad}\n• Uso: {uso}\n• Ejemplo: {ej}"

    curso = CURSOS_COMPLETOS.get(idioma) or CURSOS_COMPLETOS["Inglés"]
    if any(w in q.lower() for w in ["hola", "hello", "hi", "buenas", "que tal", "qué tal"]):
        return (
            f"¡Hola! En {idioma} saludas diciendo \"{curso['saludo']}\".\n"
            f"¿Quieres que te explique alguna palabra, verbo o frase de {idioma}?"
        )

    if "numero" in q.lower() or "número" in q.lower() or "contar" in q.lower():
        return f"Los números del 1 al 5 en {idioma} son: {curso['numeros']}."

    return (
        f"Consulta sobre {idioma}: \"{q}\"\n"
        f"• Frase modelo en {idioma}: {curso['rutina']}\n"
        f"• Consejo: Escribe una palabra específica (por ejemplo 'hello', 'thank you', 'water') o una duda concreta de gramática para darte la explicación exacta."
    )

HTML_PAGE = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>C-PRE "LENGUAJES"</title>
<style>
* { box-sizing: border-box; }
body {
  margin: 0;
  background: #09090b;
  color: #f4f4f5;
  font-family: system-ui, -apple-system, Arial, sans-serif;
  font-size: 16px;
  padding-bottom: 68px;
}
header {
  background: #000000;
  border-bottom: 1px solid #27272a;
  padding: 16px 14px;
  text-align: center;
}
header h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 900;
  letter-spacing: 0.8px;
  color: #ffffff;
}
header p {
  margin: 5px 0 0;
  font-size: 14px;
  color: #a1a1aa;
}
.wrap {
  max-width: 760px;
  margin: 0 auto;
  padding: 14px;
}
.card {
  background: #121215;
  border: 1px solid #27272a;
  padding: 16px;
  margin-bottom: 16px;
  border-radius: 10px;
}
.stats-bar {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}
.stat-box {
  background: #09090b;
  border: 1px solid #27272a;
  border-radius: 8px;
  padding: 10px 8px;
  text-align: center;
}
.stat-box span {
  display: block;
  font-size: 11px;
  text-transform: uppercase;
  color: #a1a1aa;
}
.stat-box strong {
  display: block;
  font-size: 16px;
  color: #ffffff;
  margin-top: 2px;
}
label.lbl {
  display: block;
  font-size: 14px;
  color: #e4e4e7;
  margin-top: 10px;
  font-weight: 700;
}
select, input[type="text"], button {
  width: 100%;
  padding: 13px 14px;
  font-size: 16px;
  border-radius: 8px;
  border: 1px solid #52525b;
  background: #18181b;
  color: #ffffff;
  margin-top: 8px;
}
button {
  background: #ffffff;
  color: #09090b;
  font-weight: 800;
  border: none;
  cursor: pointer;
}
button:active { opacity: 0.85; }
button.sec {
  background: #27272a;
  color: #ffffff;
  border: 1px solid #52525b;
}
.row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.frase-destacada {
  background: #18181b;
  border: 1px solid #ffffff;
  border-radius: 8px;
  padding: 12px;
  margin: 10px 0;
  font-size: 17px;
  font-weight: 800;
  color: #ffffff;
}
.clase {
  background: #09090b;
  border-left: 4px solid #ffffff;
  padding: 11px 12px;
  margin: 8px 0;
  font-size: 15px;
  line-height: 1.45;
  border-radius: 0 6px 6px 0;
}
.preg {
  background: #18181b;
  border: 1px solid #3f3f46;
  padding: 12px;
  margin: 10px 0;
  border-radius: 8px;
  font-size: 15px;
}
.preg label {
  display: block;
  margin-top: 9px;
  padding: 6px 4px;
  cursor: pointer;
}
.nota-box {
  background: #18181b;
  border: 2px solid #ffffff;
  padding: 14px;
  margin-top: 12px;
  border-radius: 8px;
  font-size: 15px;
  line-height: 1.45;
  white-space: pre-line;
}
.barra-bg {
  width: 100%;
  height: 12px;
  background: #27272a;
  border-radius: 6px;
  overflow: hidden;
  margin: 8px 0;
}
.barra-fill {
  height: 100%;
  background: #ffffff;
  width: 0%;
}
.tip-diario {
  font-size: 14px;
  color: #d4d4d8;
  background: #09090b;
  border: 1px dashed #52525b;
  padding: 10px 12px;
  border-radius: 8px;
  margin-top: 10px;
}
.dueno {
  position: fixed;
  right: 12px;
  bottom: 10px;
  font-size: 12px;
  font-weight: 800;
  color: #ffffff;
  background: #09090b;
  padding: 5px 9px;
  border: 1px solid #52525b;
  border-radius: 5px;
  z-index: 40;
}
</style>
</head>
<body>
<header>
  <h1>BIENVENIDO A C-PRE "LENGUAJES"</h1>
  <p>Creaciones de Celso</p>
</header>

<div class="wrap">
  <div class="card">
    <div class="stats-bar">
      <div class="stat-box"><span>Nivel</span><strong id="statNivel">Easy</strong></div>
      <div class="stat-box"><span>Rama</span><strong id="statRama">1/7</strong></div>
      <div class="stat-box"><span>Nota</span><strong id="statNota">0/20</strong></div>
    </div>

    <label class="lbl" for="selIdioma">Idioma (20 disponibles):</label>
    <select id="selIdioma" onchange="cambiarIdioma()"></select>

    <label class="lbl" for="selNivel">Nivel (se desbloquean al aprobar):</label>
    <select id="selNivel" onchange="cambiarNivel()"></select>

    <label class="lbl" for="selRama">Rama actual:</label>
    <select id="selRama" onchange="renderizarRama()"></select>

    <div id="boxTip" class="tip-diario"></div>
  </div>

  <div class="card">
    <h2 id="tituloRama" style="margin:0 0 8px;font-size:19px;"></h2>
    <div id="fraseClaveBox" class="frase-destacada"></div>
    <button type="button" class="sec" onclick="escucharFrase()">🔊 ESCUCHAR PRONUNCIACIÓN</button>

    <div id="listaClases" style="margin-top:10px;"></div>

    <button type="button" onclick="abrirExamen(false)">PRESENTAR EVALUACIÓN (20 PTS)</button>
    <button type="button" class="sec" onclick="abrirExamenSaltoEasy()">SALTAR EASY (EXAMEN A MEDIUM)</button>
    <div id="zonaExamen" style="display:none;margin-top:14px;"></div>
  </div>

  <div class="card">
    <div class="stats-bar" style="grid-template-columns: 1fr 1fr;">
      <div class="stat-box"><span>Reto Adaptado</span><strong id="juegoNum">1/10</strong></div>
      <div class="stat-box"><span>Puntos / Racha</span><strong id="juegoPts">0 pts · 🔥0</strong></div>
    </div>
    <p id="juegoPreg" style="font-weight:800;margin:8px 0;font-size:17px;color:#ffffff;"></p>
    <div id="juegoOps"></div>
    <div id="juegoFeedback" class="clase" style="margin-top:10px;">Elige una respuesta para ganar puntos.</div>
  </div>

  <div class="card">
    <h3 style="margin:0 0 6px;font-size:18px;">PROFESOR DE IDIOMAS</h3>
    <p style="margin:0 0 8px;font-size:14px;color:#a1a1aa;">Pregunta vocabulario (ej. "hello"), gramática o cualquier duda.</p>
    <input type="text" id="txtConsulta" placeholder="Escribe aquí tu pregunta o palabra...">
    <button type="button" onclick="consultarProfesor()">PREGUNTAR AL PROFESOR</button>
    <div id="resConsulta" class="clase" style="margin-top:12px;white-space:pre-line;">Listo para responder tus dudas.</div>
  </div>
</div>

<div class="dueno">DUEÑO CELSO</div>

<script id="jsonCursos" type="application/json">__CURSOS_JSON__</script>
<script id="jsonNoticias" type="application/json">__NOTICIAS_JSON__</script>

<script>
const CURSOS = JSON.parse(document.getElementById("jsonCursos").textContent);
const NOTICIAS = JSON.parse(document.getElementById("jsonNoticias").textContent);
const NIVELES = ["Easy", "Medium", "Hard", "Expert/Nativo"];

let idiomaActual = "Inglés";
let nivelDesbloqueadoIdx = 0;
let nivelActual = "Easy";
let ramaIdx = 0;
let modoSalto = false;
let ultimaNota = 0;
let juegoIdx = 0;
let juegoPts = 0;
let juegoRacha = 0;

function iniciarApp() {
  const selI = document.getElementById("selIdioma");
  Object.keys(CURSOS).forEach(nom => {
    const op = document.createElement("option");
    op.value = nom;
    op.textContent = nom;
    if (nom === idiomaActual) op.selected = true;
    selI.appendChild(op);
  });
  const dia = new Date().getDate();
  document.getElementById("boxTip").textContent = NOTICIAS[dia % NOTICIAS.length];
  cargarNiveles();
  renderizarJuego();
}

function cambiarIdioma() {
  idiomaActual = document.getElementById("selIdioma").value;
  nivelDesbloqueadoIdx = 0;
  nivelActual = "Easy";
  ramaIdx = 0;
  juegoIdx = 0;
  cargarNiveles();
  renderizarJuego();
}

function cargarNiveles() {
  const selN = document.getElementById("selNivel");
  selN.innerHTML = "";
  NIVELES.forEach((nv, idx) => {
    const op = document.createElement("option");
    op.value = nv;
    const bloqueado = idx > nivelDesbloqueadoIdx;
    op.textContent = bloqueado ? `${nv} (Bloqueado)` : nv;
    op.disabled = bloqueado;
    if (nv === nivelActual) op.selected = true;
    selN.appendChild(op);
  });
  cargarRamas();
}

function cambiarNivel() {
  const elegido = document.getElementById("selNivel").value;
  const idx = NIVELES.indexOf(elegido);
  if (idx > nivelDesbloqueadoIdx) return;
  nivelActual = elegido;
  ramaIdx = 0;
  cargarRamas();
}

function cargarRamas() {
  const selR = document.getElementById("selRama");
  selR.innerHTML = "";
  const ramas = CURSOS[idiomaActual].niveles[nivelActual];
  ramas.forEach((r, i) => {
    const op = document.createElement("option");
    op.value = i;
    op.textContent = r.rama;
    if (i === ramaIdx) op.selected = true;
    selR.appendChild(op);
  });
  renderizarRama();
}

function renderizarRama() {
  ramaIdx = parseInt(document.getElementById("selRama").value || "0", 10);
  const ramas = CURSOS[idiomaActual].niveles[nivelActual];
  const data = ramas[ramaIdx];

  document.getElementById("statNivel").textContent = nivelActual;
  document.getElementById("statRama").textContent = `${ramaIdx + 1}/${ramas.length}`;
  document.getElementById("statNota").textContent = `${ultimaNota}/20`;

  document.getElementById("tituloRama").textContent = data.rama;
  document.getElementById("fraseClaveBox").textContent = data.clave;

  const cont = document.getElementById("listaClases");
  cont.innerHTML = "";
  data.clases.forEach(c => {
    const d = document.createElement("div");
    d.className = "clase";
    d.textContent = c;
    cont.appendChild(d);
  });
  document.getElementById("zonaExamen").style.display = "none";
}

function escucharFrase() {
  const curso = CURSOS[idiomaActual];
  const data = curso.niveles[nivelActual][ramaIdx];
  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel();
    const msg = new SpeechSynthesisUtterance(data.clave);
    msg.lang = curso.lang_code;
    window.speechSynthesis.speak(msg);
  }
}

function abrirExamenSaltoEasy() {
  nivelActual = "Easy";
  ramaIdx = 0;
  cargarRamas();
  abrirExamen(true);
}

function abrirExamen(esSalto) {
  modoSalto = Boolean(esSalto);
  const data = CURSOS[idiomaActual].niveles[nivelActual][ramaIdx];
  const zona = document.getElementById("zonaExamen");
  zona.style.display = "block";

  let html = `<div style="font-weight:800;margin-bottom:8px;">${modoSalto ? "Examen para saltar Easy a Medium (aprueba desde 10/20)" : "Examen de la rama (4 pts c/u · Total 20 pts)"}</div>`;
  data.preguntas.forEach((p, idx) => {
    html += `<div class="preg"><div><strong>${idx + 1}.</strong> ${p.q}</div>`;
    if (p.tipo === "texto") {
      html += `<input type="text" id="ex_txt_${idx}" placeholder="Escribe tu respuesta...">`;
    } else {
      p.ops.forEach(op => {
        const safe = op.replace(/"/g, "&quot;");
        html += `<label><input type="radio" name="ex_rad_${idx}" value="${safe}"> ${op}</label>`;
      });
    }
    html += `</div>`;
  });
  html += `<button type="button" onclick="calificar()">ENTREGAR EXAMEN</button><div id="resExamen"></div>`;
  zona.innerHTML = html;
}

function calificar() {
  const data = CURSOS[idiomaActual].niveles[nivelActual][ramaIdx];
  let nota = 0;
  let detalle = "";

  data.preguntas.forEach((p, idx) => {
    let ok = false;
    if (p.tipo === "texto") {
      const val = (document.getElementById("ex_txt_" + idx)?.value || "").trim().toLowerCase();
      ok = Boolean(val && val === p.ok.toLowerCase());
    } else {
      const sel = document.querySelector(`input[name="ex_rad_${idx}"]:checked`);
      ok = Boolean(sel && sel.value === p.ok);
    }
    if (ok) {
      nota += 4;
      detalle += `• Pregunta ${idx + 1}: +4 pts\n`;
    } else {
      detalle += `• Pregunta ${idx + 1}: 0 pts (${p.exp})\n`;
    }
  });

  ultimaNota = nota;
  document.getElementById("statNota").textContent = `${nota}/20`;
  const aprobo = nota >= 10;
  const pct = Math.round((nota / 20) * 100);
  let btnSiguiente = "";

  if (modoSalto) {
    if (aprobo) {
      nivelDesbloqueadoIdx = Math.max(nivelDesbloqueadoIdx, 1);
      nivelActual = "Medium";
      ramaIdx = 0;
      cargarNiveles();
      btnSiguiente = `<button type="button" onclick="cargarNiveles()">ENTRAR A MEDIUM DESBLOQUEADO</button>`;
    } else {
      nivelActual = "Easy";
      ramaIdx = 0;
      cargarRamas();
      btnSiguiente = `<div style="margin-top:8px;">No alcanzaste 10/20. Debes completar Easy desde la Rama 1.</div>`;
    }
  } else if (aprobo) {
    const ramasNivel = CURSOS[idiomaActual].niveles[nivelActual];
    if (ramaIdx + 1 < ramasNivel.length) {
      ramaIdx += 1;
      btnSiguiente = `<button type="button" onclick="cargarRamas()">CONTINUAR A LA SIGUIENTE RAMA</button>`;
    } else {
      const idxActual = NIVELES.indexOf(nivelActual);
      if (idxActual + 1 < NIVELES.length) {
        nivelDesbloqueadoIdx = Math.max(nivelDesbloqueadoIdx, idxActual + 1);
        nivelActual = NIVELES[idxActual + 1];
        ramaIdx = 0;
        btnSiguiente = `<button type="button" onclick="cargarNiveles()">DESBLOQUEAR ${nivelActual.toUpperCase()}</button>`;
      } else {
        btnSiguiente = `<button type="button" onclick="ramaIdx=0;cargarRamas()">REINICIAR NIVEL</button>`;
      }
    }
  } else {
    btnSiguiente = `<button type="button" class="sec" onclick="abrirExamen(${modoSalto})">REPETIR EXAMEN</button>`;
  }

  document.getElementById("resExamen").innerHTML =
    `<div class="nota-box"><strong>Resultado: ${nota}/20 (${aprobo ? "APROBADO" : "REPROBADO"})</strong>` +
    `<div class="barra-bg"><div class="barra-fill" style="width:${pct}%"></div></div>` +
    `${detalle}</div>${btnSiguiente}`;
}

function renderizarJuego() {
  const juegos = CURSOS[idiomaActual].juegos;
  const j = juegos[juegoIdx % juegos.length];
  document.getElementById("juegoNum").textContent = `${j.n}/10 · ${j.t}`;
  document.getElementById("juegoPts").textContent = `${juegoPts} pts · 🔥${juegoRacha}`;
  document.getElementById("juegoPreg").textContent = j.q;

  const box = document.getElementById("juegoOps");
  box.innerHTML = "";
  j.ops.forEach(op => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "sec";
    b.textContent = op;
    b.onclick = () => {
      if (op === j.ok) {
        juegoRacha += 1;
        juegoPts += 10;
        document.getElementById("juegoFeedback").textContent = `¡Correcto! +10 pts (Racha: ${juegoRacha}).`;
      } else {
        juegoRacha = 0;
        document.getElementById("juegoFeedback").textContent = `Incorrecto. La respuesta correcta en ${idiomaActual} es: "${j.ok}".`;
      }
      juegoIdx += 1;
      renderizarJuego();
    };
    box.appendChild(b);
  });
}

async function consultarProfesor() {
  const txt = document.getElementById("txtConsulta").value.trim();
  if (!txt) return;
  const box = document.getElementById("resConsulta");
  box.textContent = "Consultando al profesor...";
  try {
    const r = await fetch("/api/preguntar", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ pregunta: txt, idioma: idiomaActual })
    });
    const d = await r.json();
    box.textContent = d.respuesta;
  } catch (e) {
    box.textContent = "No se pudo conectar con el servidor.";
  }
}

document.getElementById("txtConsulta").addEventListener("keydown", function(ev) {
  if (ev.key === "Enter") {
    ev.preventDefault();
    consultarProfesor();
  }
});

iniciarApp();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    cursos_json = json.dumps(CURSOS_COMPLETOS, ensure_ascii=True).replace("</", "<\\/")
    noticias_json = json.dumps(NOTICIAS, ensure_ascii=True).replace("</", "<\\/")
    return HTML_PAGE.replace("__CURSOS_JSON__", cursos_json).replace("__NOTICIAS_JSON__", noticias_json)

@app.route("/api/preguntar", methods=["POST"])
def preguntar():
    data = request.get_json(silent=True) or {}
    return jsonify({"respuesta": consultar_profesor_ia(data.get("idioma") or "Inglés", data.get("pregunta") or "")})

if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
