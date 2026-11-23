import os, json, re, urllib.request
from flask import Flask, request, jsonify

app = Flask(__name__)

CODIGO_ACCESO = os.environ.get("C_PRE_CODIGO", "CPRE2026")

IDIOMAS = [
    ("Inglés", "Hello! Ready to practice real English?", "I am ready.", "Good morning", "Thank you", "I speak English every day.", {"to be": "Verbo ser/estar en presente: I am, you are, he/she/it is, we/they are.", "do": "Auxiliar para preguntas/negaciones en presente simple.", "can": "Indica habilidad o permiso ('puedo').", "hello": "Saludo estándar ('Hola').", "thank you": "Expresión clara de agradecimiento."}),
    ("Portugués", "Olá! Vamos praticar português?", "Eu estou pronto.", "Bom dia", "Obrigado", "Eu falo português com calma.", {"ser": "Indica identidade o algo estable.", "estar": "Indica estado temporal o ubicación actual.", "obrigado": "Gracias.", "olá": "Hola."}),
    ("Francés", "Bonjour ! Prêt pour le français ?", "Je suis prêt.", "Bonjour", "Merci", "Je parle français un peu.", {"être": "Verbo ser/estar: je suis, tu es, il/elle est.", "ne pas": "Negación alrededor del verbo.", "merci": "Gracias.", "bonjour": "Hola / Buenos días."}),
    ("Coreano", "안녕하세요 (Annyeonghaseyo)", "준비됐어요 (Junbi-dwaesseo-yo)", "좋은 아침 (Jo-eun achim)", "감사합니다 (Gamsahamnida)", "한국어를 공부해요 (Han-gu-geo-reul gong-bu-hae-yo)", {"hangul": "Alfabeto coreano por bloques silábicos.", "-yo": "Terminación de cortesía cotidiana.", "감사합니다": "Gracias.", "안녕하세요": "Hola."}),
    ("Chino Mandarín", "你好 (Nǐ hǎo)", "我准备好了 (Wǒ zhǔnbèi hǎo le)", "早上好 (Zǎoshang hǎo)", "谢谢 (Xièxie)", "我说中文 (Wǒ shuō zhōngwén)", {"tono": "Los tonos en Pinyin cambian el significado.", "ma": "Partícula final para formar preguntas.", "谢谢": "Gracias.", "你好": "Hola."}),
    ("Ruso", "Привет (Privet)", "Я готов (Ya gotov)", "Доброе утро (Dóbroye útro)", "Спасибо (Spasíbo)", "Я говорю по-русски (Ya govoryú po-rússki)", {"cirílico": "Alfabeto ruso; en presente suele omitirse 'ser/estar'.", "спасибо": "Gracias.", "привет": "Hola."}),
    ("Alemán", "Hallo! Lass uns Deutsch üben.", "Ich bin bereit.", "Guten Morgen", "Danke", "Ich spreche ein wenig Deutsch.", {"mayúscula": "Todos los sustantivos van con mayúscula inicial.", "verbo": "Ocupa la segunda posición en oraciones afirmativas.", "danke": "Gracias.", "hallo": "Hola."}),
    ("Italiano", "Ciao! Impariamo l'italiano?", "Sono pronto.", "Buongiorno", "Grazie", "Studio italiano ogni giorno.", {"essere": "Verbo ser/estar: io sono, tu sei.", "grazie": "Gracias.", "ciao": "Hola / Chao."}),
    ("Japonés", "こんにちは (Konnichiwa)", "じゅんびできました (Junbi dekimashita)", "おはようございます (Ohayō gozaimasu)", "ありがとう (Arigatō)", "にほんごをべんきょうします (Nihongo o benkyō shimasu)", {"partículas": "El verbo va al final; は marca el tema.", "ありがとう": "Gracias.", "こんにちは": "Hola."}),
    ("Árabe", "مرحباً (Marhaban)", "أنا مستعد (Anā musta'idd)", "صباح الخير (Sabāh al-khayr)", "شكراً (Shukran)", "أتعلم العربية (Ata'allam al-'arabiyyah)", {"escritura": "Se lee y escribe de derecha a izquierda.", "شكراً": "Gracias.", "مرحباً": "Hola."})
]

CURSOS = {}
for nombre, saludo, listo, manana, gracias, frase, notas in IDIOMAS:
    CURSOS[nombre] = {
        "saludo": saludo,
        "ramas": [
            {"titulo": "Rama 1 · Base y Cortesía", "explicacion": f"En {nombre}, dominar el saludo inicial, indicar que estás listo y agradecer te da base inmediata.", "esquema": f"[Saludo: {saludo}] -> [Listo: {listo}] -> [Cortesía: {gracias}]", "ejemplos": [f"{saludo} -> Hola", f"{listo} -> Estoy listo/a", f"{gracias} -> Gracias"], "eval": [{"q": f"¿Cómo dices 'Gracias' en {nombre}?", "ops": [gracias, saludo, manana], "ok": gracias, "exp": f"'{gracias}' se usa para agradecer."}, {"q": f"Elige el saludo inicial en {nombre}:", "ops": [saludo, gracias, listo], "ok": saludo, "exp": f"'{saludo}' es el saludo base."}, {"q": f"¿Cómo dices 'Estoy listo/a' en {nombre}?", "ops": [listo, manana, saludo], "ok": listo, "exp": f"'{listo}' expresa preparación."}]},
            {"titulo": "Rama 2 · Contexto Diario", "explicacion": f"Al avanzar en {nombre}, ubicas el momento del día y unes una frase completa con sentido práctico.", "esquema": f"[Mañana: {manana}] -> [Frase: {frase}] -> [Cierre: {gracias}]", "ejemplos": [f"{manana} -> Buenos días", f"{frase} -> Frase cotidiana"], "eval": [{"q": f"Saludo de mañana en {nombre}:", "ops": [manana, saludo, gracias], "ok": manana, "exp": f"'{manana}' corresponde a la mañana."}, {"q": f"Frase de práctica en {nombre}:", "ops": [frase, saludo, gracias], "ok": frase, "exp": f"'{frase}' es una frase modelo."}, {"q": f"Marca 'Estoy listo/a' en {nombre}:", "ops": [listo, gracias, manana], "ok": listo, "exp": f"'{listo}' indica que estás listo."}]},
            {"titulo": "Rama 3 · Precisión y Dominio", "explicacion": f"Aquí eliges la expresión exacta según la situación en {nombre}, consolidando seguridad y rapidez.", "esquema": f"[Situación] -> [Expresión Exacta] -> [Dominio]", "ejemplos": [f"{listo} · {gracias}", f"{manana} · {frase}"], "eval": [{"q": f"Selecciona la forma exacta para 'Estoy listo/a' en {nombre}:", "ops": [listo, manana, saludo], "ok": listo, "exp": f"'{listo}' es la respuesta correcta."}, {"q": f"Selecciona 'Gracias' en {nombre}:", "ops": [gracias, listo, frase], "ok": gracias, "exp": f"'{gracias}' significa gracias."}]}
        ],
        "diccionario": {"hola": f"{saludo} (Hola)", "gracias": f"{gracias} (Gracias)", "listo": f"{listo} (Estoy listo/a)", "mañana": f"{manana} (Buenos días)", "frase": f"{frase} (Ejemplo práctico)"},
        "notas": notas,
        "juegos": [
            {"n": 1, "t": "Reflejo", "r": f"Elige 'Gracias' en {nombre}:", "ops": [gracias, saludo, manana], "ok": gracias},
            {"n": 2, "t": "Saludo", "r": f"Elige el saludo en {nombre}:", "ops": [saludo, gracias, listo], "ok": saludo},
            {"n": 3, "t": "Listo", "r": f"Elige 'Estoy listo/a' en {nombre}:", "ops": [listo, manana, gracias], "ok": listo},
            {"n": 4, "t": "Mañana", "r": f"Elige saludo de mañana en {nombre}:", "ops": [manana, saludo, listo], "ok": manana},
            {"n": 5, "t": "Frase", "r": f"Elige la frase modelo en {nombre}:", "ops": [frase, saludo, gracias], "ok": frase},
            {"n": 6, "t": "Sentido 1", "r": f"¿Qué significa '{listo}'?", "ops": ["Estoy listo/a", "Gracias", "Buenos días"], "ok": "Estoy listo/a"},
            {"n": 7, "t": "Sentido 2", "r": f"¿Qué significa '{gracias}'?", "ops": ["Gracias", "Hola", "Estoy listo/a"], "ok": "Gracias"},
            {"n": 8, "t": "Sentido 3", "r": f"¿Qué significa '{manana}'?", "ops": ["Buenos días", "Gracias", "Estoy listo/a"], "ok": "Buenos días"},
            {"n": 9, "t": "Precisión", "r": f"Indica disponibilidad en {nombre}:", "ops": [listo, gracias, saludo], "ok": listo},
            {"n": 10, "t": "Cierre", "r": f"Da las gracias en {nombre}:", "ops": [gracias, manana, frase], "ok": gracias}
        ]
    }

def responder_pregunta_inteligente(idioma, texto, modo="profesor"):
    c = CURSOS.get(idioma, CURSOS["Inglés"])
    raw = (texto or "").strip()
    tl = raw.lower()
    if not raw:
        return f"[{idioma} · {modo.upper()}]\nEscribe o dicta una duda específica."
    for clave, desc in c["notas"].items():
        if clave in tl:
            return f"[{idioma} · {modo.upper()}]\nEsquema: [{clave.upper()}] -> [{desc}]\nEjemplo: {c['ramas'][0]['ejemplos'][0]}"
    for palabra, trad in c["diccionario"].items():
        if re.search(rf"\b{re.escape(palabra)}\b", tl) or palabra in tl:
            return f"[{idioma} · {modo.upper()}]\nEsquema: [{palabra.upper()}] -> [{trad}]\nFrase útil: {c['ramas'][1]['ejemplos'][1]}"
    limpio = re.sub(r"[^\w\sÀ-ÿء-ي一-龥가-힣а-яА-ЯёЁ¿?¡!.,]", "", raw).strip()
    return f"[{idioma} · {modo.upper()}]\nRespuesta a «{limpio}»: enfócate en el patrón base.\nEsquema: [Idea: {limpio[:36]}] -> [Base: {c['saludo']}]"

def consultar_ia(idioma, texto, modo="profesor"):
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        return responder_pregunta_inteligente(idioma, texto, modo)
    rol = f"Responde como profesor directo de {idioma} con respuesta breve y esquema de 4 líneas." if modo == "profesor" else f"Responde como buscador claro de {idioma} con significado y ejemplo."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
    body = json.dumps({"contents": [{"parts": [{"text": f"{rol}\nConsulta: {texto}"}]}]}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            res = json.loads(r.read().decode("utf-8"))
            return res["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        return responder_pregunta_inteligente(idioma, texto, modo)

HTML_PURE = """<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>C-PRE-LANGUAGES</title><style>
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,Arial,sans-serif;background:#ffffff;color:#000000}
header{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:#ffffff;color:#000000;position:sticky;top:0;z-index:10;border-bottom:1.5px solid #000000}
.wrap{max-width:680px;margin:auto;padding:16px}
.seccion{border:1px solid #000000;padding:14px;margin-bottom:14px;background:#ffffff}
.meta{display:flex;justify-content:space-between;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;margin-bottom:10px;border-bottom:1px solid #000000;padding-bottom:6px}
.caja-texto{background:#ffffff;border-left:2.5px solid #000000;padding:10px;font-size:13.5px;font-weight:500;margin:8px 0;line-height:1.45;white-space:pre-line}
h2{margin:0 0 8px 0;font-size:17px;font-weight:700;text-transform:uppercase}
p{margin:8px 0;font-size:14px;line-height:1.45}
button{width:100%;padding:11px;background:#000000;color:#ffffff;border:1px solid #000000;font-size:14px;font-weight:600;cursor:pointer;margin-top:8px}
button.sec{background:#ffffff;color:#000000;border:1px solid #000000}
.grid-btns{display:grid;grid-template-columns:1fr 1fr;gap:8px}
input{width:100%;padding:11px;border:1px solid #000000;background:#ffffff;color:#000000;font-size:14px;margin-bottom:8px}
select{padding:7px 8px;background:#ffffff;color:#000000;font-weight:600;border:1px solid #000000}
.modal{position:fixed;inset:0;background:#ffffff;display:flex;flex-direction:column;justify-content:center;align-items:center;z-index:100;padding:24px;text-align:center}
.modal.oculto{display:none}
.bienvenida{font-size:26px;font-weight:800;text-transform:uppercase;margin-bottom:14px;border-top:2px solid #000000;border-bottom:2px solid #000000;padding:18px 0;letter-spacing:1px}
.dueno{font-size:14px;font-weight:700;letter-spacing:2px;text-transform:uppercase}
</style></head><body>

<div id="pantallaBienvenida" class="modal">
    <div style="font-size:14px;font-weight:800;letter-spacing:1px;margin-bottom:10px">C-PRE-LANGUAGES · ACCESO</div>
    <input type="password" id="passIn" placeholder="Introduce el código..." style="max-width:300px">
    <button onclick="verificarAcceso()" style="max-width:300px">ENTRAR</button>
    <div id="errorCod" style="color:#000000;font-weight:700;margin-top:8px;display:none">Código incorrecto.</div>
</div>

<header>
    <strong style="letter-spacing:.6px">C-PRE-LANGUAGES</strong>
    <select id="langSelect" onchange="cambiarIdioma()">
        <option selected>Inglés</option><option>Portugués</option><option>Francés</option><option>Coreano</option><option>Chino Mandarín</option>
        <option>Ruso</option><option>Alemán</option><option>Italiano</option><option>Japonés</option><option>Árabe</option>
    </select>
</header>

<div class="wrap">
    <div class="seccion">
        <div class="meta">
            <span>NIVEL: <span id="valNivel">Medium</span></span>
            <span>DOMINIO: <span id="valDominio">0%</span></span>
            <span>RACHA: <span id="valRacha">0</span></span>
        </div>
        <h2 id="ramaTitulo">Rama 1 · Base y Cortesía</h2>
        <p id="ramaExplicacion"></p>
        <div id="ramaEsquema" class="caja-texto"></div>
        <div id="ramaEjemplos" class="caja-texto"></div>
    </div>

    <div class="seccion">
        <div class="meta"><span>EVALUACIÓN ALGORÍTMICA</span><span id="progEval">1/3</span></div>
        <p id="preguntaEval" style="font-weight:700;font-size:15px"></p>
        <div id="opcionesEval" class="grid-btns"></div>
        <div id="feedbackEval" class="caja-texto" style="margin-top:10px">Responde para evaluar tu progreso.</div>
    </div>

    <div class="seccion">
        <div class="meta"><span>10 JUEGOS ADAPTADOS</span><span id="puntosJuego">PTS: 0</span></div>
        <h3 id="tituloJuego" style="margin:0 0 8px 0;font-size:15px;text-transform:uppercase">Reflejo</h3>
        <p id="preguntaJuego" style="font-weight:700;font-size:15px"></p>
        <div id="opcionesJuego" class="grid-btns"></div>
        <div id="feedbackJuego" class="caja-texto" style="margin-top:10px">Selecciona una opción.</div>
    </div>

    <div class="seccion">
        <div class="meta"><span>PROFESOR Y BUSCADOR</span><span id="modoLabel">MODO: PROFESOR</span></div>
        <input type="text" id="consultaIn" placeholder="Escribe tu duda o palabra...">
        <div class="grid-btns">
            <button onclick="consultarIA('profesor')">PREGUNTAR</button>
            <button class="sec" onclick="consultarIA('buscador')">BUSCAR</button>
        </div>
        <div id="respuestaIA" class="caja-texto">Listo para responder tus dudas.</div>
    </div>
</div>

<script>
const CURSOS = __CURSOS_DATA__;
const CODIGO_VALIDO = __CODIGO_VALIDO__;
let idiomaActual = "Inglés";
let ramaIdx = 0, evalIdx = 0, juegoIdx = 0;
let aciertos = 0, intentos = 0, racha = 0, puntos = 0, nivelIndex = 0;
const NIVELES = ["Medium", "Hard", "Expert/Nativo"];

function verificarAcceso(){
    const input = document.getElementById("passIn").value.trim();
    if(input !== CODIGO_VALIDO){
        document.getElementById("errorCod").style.display = "block";
        return;
    }
    document.getElementById("errorCod").style.display = "none";
    iniciarBienvenida();
}

function iniciarBienvenida(){
    let segundos = 5;
    const modal = document.getElementById("pantallaBienvenida");
    function renderizarBienvenida(){
        if(segundos > 0){
            modal.innerHTML = `<div class="bienvenida">BIENVENIDOS A C-PRE-LANGUAGES</div><div class="dueno">DUEÑO CELSO</div><div style="margin-top:20px;font-weight:700">Iniciando en ${segundos}s...</div>`;
        } else {
            modal.classList.add("oculto");
            renderizarTodo();
        }
    }
    renderizarBienvenida();
    const timer = setInterval(() => {
        segundos--;
        renderizarBienvenida();
        if(segundos <= 0) clearInterval(timer);
    }, 1000);
}

function cambiarIdioma(){
    idiomaActual = document.getElementById("langSelect").value;
    ramaIdx = 0; evalIdx = 0; juegoIdx = 0;
    renderizarTodo();
}

function renderizarTodo(){
    const curso = CURSOS[idiomaActual];
    const rama = curso.ramas[ramaIdx];
    document.getElementById("ramaTitulo").textContent = rama.titulo;
    document.getElementById("ramaExplicacion").textContent = rama.explicacion;
    document.getElementById("ramaEsquema").textContent = "ESQUEMA:\n" + rama.esquema;
    document.getElementById("ramaEjemplos").textContent = "EJEMPLOS:\n• " + rama.ejemplos.join("\n• ");
    renderizarEval();
    renderizarJuego();
}

function renderizarEval(){
    const curso = CURSOS[idiomaActual];
    const lista = curso.ramas[ramaIdx].eval;
    const item = lista[evalIdx % lista.length];
    document.getElementById("progEval").textContent = `${(evalIdx % lista.length) + 1}/${lista.length}`;
    document.getElementById("preguntaEval").textContent = item.q;
    const opsDiv = document.getElementById("opcionesEval");
    opsDiv.innerHTML = "";
    item.ops.forEach(op => {
        const btn = document.createElement("button");
        btn.className = "sec";
        btn.textContent = op;
        btn.onclick = () => procesarEval(op === item.ok, item.exp);
        opsDiv.appendChild(btn);
    });
}

function procesarEval(esCorrecto, explicacion){
    intentos++;
    if(esCorrecto){ aciertos++; racha++; puntos += 10; } else { racha = 0; }
    document.getElementById("puntosJuego").textContent = "PTS: " + puntos;
    document.getElementById("valRacha").textContent = racha;
    const dominio = Math.round((aciertos / Math.max(1, intentos)) * 100);
    document.getElementById("valDominio").textContent = dominio + "%";
    let nuevoNivel = 0;
    if(dominio >= 85 && racha >= 3) nuevoNivel = 2;
    else if(dominio >= 65) nuevoNivel = 1;
    if(nuevoNivel > nivelIndex){
        nivelIndex = nuevoNivel;
        document.getElementById("valNivel").textContent = NIVELES[nivelIndex];
    }
    const fb = document.getElementById("feedbackEval");
    if(esCorrecto){
        const siguienteRamaIdx = (ramaIdx + 1) % CURSOS[idiomaActual].ramas.length;
        fb.innerHTML = `<strong>¡CORRECTO! (+10 PTS)</strong><br>${explicacion}<br><button onclick="ramaIdx=${siguienteRamaIdx};evalIdx=0;renderizarTodo()">PASAR A SIGUIENTE RAMA</button>`;
    } else {
        fb.innerHTML = `<strong>INCORRECTO.</strong><br>${explicacion}<br><button class="sec" onclick="evalIdx++;renderizarEval()">SIGUIENTE PREGUNTA</button>`;
    }
}

function renderizarJuego(){
    const curso = CURSOS[idiomaActual];
    const juego = curso.juegos[juegoIdx % curso.juegos.length];
    document.getElementById("tituloJuego").textContent = "JUEGO " + juego.n + "/10 · " + juego.t;
    document.getElementById("preguntaJuego").textContent = juego.r;
    const opsDiv = document.getElementById("opcionesJuego");
    opsDiv.innerHTML = "";
    juego.ops.forEach(op => {
        const btn = document.createElement("button");
        btn.className = "sec";
        btn.textContent = op;
        btn.onclick = () => procesarJuego(op === juego.ok, juego.ok);
        opsDiv.appendChild(btn);
    });
}

function procesarJuego(esCorrecto, respuestaCorrecta){
    if(esCorrecto) puntos += 10;
    document.getElementById("puntosJuego").textContent = "PTS: " + puntos;
    const fb = document.getElementById("feedbackJuego");
    const sigJuegoIdx = juegoIdx + 1;
    fb.innerHTML = `${esCorrecto ? '<strong>¡ACIERTO! +10 PTS</strong>' : '<strong>FALLASTE.</strong> Correcta: ' + respuestaCorrecta}<br><button class="sec" onclick="juegoIdx=${sigJuegoIdx};renderizarJuego()">SIGUIENTE RETO</button>`;
}

async function consultarIA(modo){
    const texto = document.getElementById("consultaIn").value.trim();
    if(!texto) return;
    document.getElementById("modoLabel").textContent = "MODO: " + modo.toUpperCase();
    document.getElementById("respuestaIA").textContent = "Procesando...";
    try {
        const r = await fetch("/api/ia", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({idioma: idiomaActual, texto, modo})
        });
        const d = await r.json();
        document.getElementById("respuestaIA").textContent = d.respuesta;
    } catch(e) {
        document.getElementById("respuestaIA").textContent = "Error al consultar.";
    }
}
</script></body></html>"""

@app.route("/")
def home():
    cursos_json = json.dumps(CURSOS, ensure_ascii=False)
    codigo_json = json.dumps(CODIGO_ACCESO, ensure_ascii=False)
    return HTML_PURE.replace("__CURSOS_DATA__", cursos_json).replace("__CODIGO_VALIDO__", codigo_json)

@app.route("/api/ia", methods=["POST"])
def api_ia():
    d = request.get_json() or {}
    return jsonify({"respuesta": consultar_ia(d.get("idioma"), d.get("texto"), d.get("modo"))})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
