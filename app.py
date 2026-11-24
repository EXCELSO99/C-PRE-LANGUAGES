import os
import json
import urllib.request
from flask import Flask, request, jsonify

app = Flask(__name__)

PORT = int(os.environ.get("PORT", 5000))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

CURSO_INGLES = {
    "Easy": [
        {
            "rama": "Rama 1: Verbo To Be e Identidad",
            "clases": [
                "Clase 1: 'I am' significa 'Yo soy' o 'Yo estoy'. Ejemplo: I am a student.",
                "Clase 2: 'You are' significa 'Tú eres' o 'Tú estás'. Ejemplo: You are ready.",
                "Clase 3: 'He is / She is' se usa para él o ella. Ejemplo: She is my friend.",
                "Clase 4: Para negar agrega 'not'. Ejemplo: I am not tired.",
                "Clase 5: Para preguntar invierte el orden. Ejemplo: Are you ready?"
            ],
            "preguntas": [
                {"q": "Verdadero o Falso: 'I am a student' significa 'Soy estudiante'.", "ops": ["Verdadero", "Falso"], "ok": "Verdadero"},
                {"q": "Completa: ___ are my friend.", "ops": ["You", "Am"], "ok": "You"},
                {"q": "Identifica la forma negativa correcta:", "ops": ["I am not tired", "I no am tired"], "ok": "I am not tired"},
                {"q": "Escribe en inglés: 'Yo soy' (dos palabras):", "tipo": "texto", "ok": "i am"},
                {"q": "Verdadero o Falso: 'Are you ready?' es una pregunta.", "ops": ["Verdadero", "Falso"], "ok": "Verdadero"}
            ]
        },
        {
            "rama": "Rama 2: Saludos y Cortesía",
            "clases": [
                "Clase 1: 'Hello' y 'Hi' significan 'Hola'.",
                "Clase 2: 'Good morning' se usa en la mañana (Buenos días).",
                "Clase 3: 'Good afternoon' (Buenas tardes) y 'Good night' (Buenas noches).",
                "Clase 4: 'Thank you' o 'Thanks' significa 'Gracias'.",
                "Clase 5: 'Please' (Por favor) y 'You are welcome' (De nada)."
            ],
            "preguntas": [
                {"q": "Verdadero o Falso: 'Good morning' significa 'Buenas noches'.", "ops": ["Verdadero", "Falso"], "ok": "Falso"},
                {"q": "Completa para agradecer: _____ you.", "ops": ["Thank", "Hello"], "ok": "Thank"},
                {"q": "Identifica cómo decir 'De nada':", "ops": ["You are welcome", "Good morning"], "ok": "You are welcome"},
                {"q": "Escribe 'Hola' en inglés:", "tipo": "texto", "ok": "hello"},
                {"q": "Verdadero o Falso: 'Please' significa 'Por favor'.", "ops": ["Verdadero", "Falso"], "ok": "Verdadero"}
            ]
        },
        {
            "rama": "Rama 3: Números Básicos",
            "clases": [
                "Clase 1: 1 = One, 2 = Two, 3 = Three.",
                "Clase 2: 4 = Four, 5 = Five, 6 = Six.",
                "Clase 3: 7 = Seven, 8 = Eight, 9 = Nine, 10 = Ten.",
                "Clase 4: Se usan para edad y cantidades. Ejemplo: I have two books.",
                "Clase 5: Para preguntar cantidad usa 'How many?'. Ejemplo: How many apples?"
            ],
            "preguntas": [
                {"q": "Verdadero o Falso: 'Three' es el número 3.", "ops": ["Verdadero", "Falso"], "ok": "Verdadero"},
                {"q": "Completa la secuencia: One, Two, _____, Four.", "ops": ["Three", "Five"], "ok": "Three"},
                {"q": "Identifica el número 10 en inglés:", "ops": ["Ten", "Eight"], "ok": "Ten"},
                {"q": "Escribe el número 5 en inglés:", "tipo": "texto", "ok": "five"},
                {"q": "Verdadero o Falso: 'Seven' significa 6.", "ops": ["Verdadero", "Falso"], "ok": "Falso"}
            ]
        },
        {
            "rama": "Rama 4: Pronombres y Posesivos",
            "clases": [
                "Clase 1: 'My' = Mi / Mis. Ejemplo: My house (Mi casa).",
                "Clase 2: 'Your' = Tu / Tus. Ejemplo: Your book (Tu libro).",
                "Clase 3: 'His' = Su (de él) y 'Her' = Su (de ella).",
                "Clase 4: 'Our' = Nuestro. Ejemplo: Our class (Nuestra clase).",
                "Clase 5: 'Their' = Su (de ellos). Ejemplo: Their car (Su carro)."
            ],
            "preguntas": [
                {"q": "Verdadero o Falso: 'My house' significa 'Mi casa'.", "ops": ["Verdadero", "Falso"], "ok": "Verdadero"},
                {"q": "Completa para decir 'Tu libro': ____ book.", "ops": ["Your", "His"], "ok": "Your"},
                {"q": "Identifica el posesivo para 'de ella':", "ops": ["Her", "His"], "ok": "Her"},
                {"q": "Escribe 'Mi' en inglés:", "tipo": "texto", "ok": "my"},
                {"q": "Verdadero o Falso: 'Our' significa 'Nuestro'.", "ops": ["Verdadero", "Falso"], "ok": "Verdadero"}
            ]
        },
        {
            "rama": "Rama 5: Presente Simple (Rutinas)",
            "clases": [
                "Clase 1: Se usa para hábitos diarios. Ejemplo: I study English every day.",
                "Clase 2: Con 'He / She / It' agrega '-s' al verbo. Ejemplo: She works here.",
                "Clase 3: Para negar usa 'don't' (I/You/We/They). Ejemplo: I don't smoke.",
                "Clase 4: Para negar con 'He/She' usa 'doesn't'. Ejemplo: He doesn't play.",
                "Clase 5: Para preguntar usa 'Do' o 'Does' al inicio. Ejemplo: Do you speak English?"
            ],
            "preguntas": [
                {"q": "Verdadero o Falso: Con 'She' el verbo lleva '-s' (She works).", "ops": ["Verdadero", "Falso"], "ok": "Verdadero"},
                {"q": "Completa: ___ you speak English?", "ops": ["Do", "Are"], "ok": "Do"},
                {"q": "Identifica la negación correcta con 'He':", "ops": ["He doesn't play", "He don't play"], "ok": "He doesn't play"},
                {"q": "Escribe el verbo 'estudiar' en inglés:", "tipo": "texto", "ok": "study"},
                {"q": "Verdadero o Falso: 'Every day' significa 'todos los días'.", "ops": ["Verdadero", "Falso"], "ok": "Verdadero"}
            ]
        }
    ],
    "Medium": [
        {
            "rama": "Rama 1: Pasado Simple",
            "clases": [
                "Clase 1: Verbos regulares terminan en '-ed'. Ejemplo: I worked yesterday.",
                "Clase 2: Verbos irregulares cambian. Ejemplo: Go -> Went (I went home).",
                "Clase 3: Para negar en pasado usa 'didn't' + verbo base. Ejemplo: I didn't go.",
                "Clase 4: Para preguntar usa 'Did' al inicio. Ejemplo: Did you study?",
                "Clase 5: Palabras clave: Yesterday (ayer), Last night (anoche), Ago (hace)."
            ],
            "preguntas": [
                {"q": "Verdadero o Falso: 'Went' es el pasado de 'Go'.", "ops": ["Verdadero", "Falso"], "ok": "Verdadero"},
                {"q": "Completa: I _____ work yesterday (negativo).", "ops": ["didn't", "don't"], "ok": "didn't"},
                {"q": "Identifica la pregunta en pasado:", "ops": ["Did you study?", "Do you studied?"], "ok": "Did you study?"},
                {"q": "Escribe 'ayer' en inglés:", "tipo": "texto", "ok": "yesterday"},
                {"q": "Verdadero o Falso: Después de 'didn't' el verbo va en forma base.", "ops": ["Verdadero", "Falso"], "ok": "Verdadero"}
            ]
        },
        {
            "rama": "Rama 2: Futuro (Will y Going to)",
            "clases": [
                "Clase 1: 'Will' se usa para decisiones rápidas o promesas. Ejemplo: I will help you.",
                "Clase 2: 'Going to' se usa para planes ya decididos. Ejemplo: I am going to travel.",
                "Clase 3: Negación con Will: 'won't'. Ejemplo: It won't rain.",
                "Clase 4: Pregunta con Will: 'Will you come tomorrow?'",
                "Clase 5: Expresiones de futuro: Tomorrow (mañana), Next week (próxima semana)."
            ],
            "preguntas": [
                {"q": "Verdadero o Falso: 'Won't' es la forma negativa de 'Will'.", "ops": ["Verdadero", "Falso"], "ok": "Verdadero"},
                {"q": "Completa el plan: I am _____ to study.", "ops": ["going", "will"], "ok": "going"},
                {"q": "Identifica la expresión 'mañana':", "ops": ["Tomorrow", "Yesterday"], "ok": "Tomorrow"},
                {"q": "Escribe el auxiliar de futuro simple (4 letras):", "tipo": "texto", "ok": "will"},
                {"q": "Verdadero o Falso: 'Going to' expresa planes futuros.", "ops": ["Verdadero", "Falso"], "ok": "Verdadero"}
            ]
        },
        {
            "rama": "Rama 3: Verbos Modales (Can, Should, Must)",
            "clases": [
                "Clase 1: 'Can' indica habilidad o permiso. Ejemplo: I can speak English.",
                "Clase 2: 'Should' sirve para dar consejos. Ejemplo: You should practice daily.",
                "Clase 3: 'Must' indica obligación fuerte. Ejemplo: You must wear a seatbelt.",
                "Clase 4: Los modales no llevan '-s' en tercera persona. Ejemplo: She can swim.",
                "Clase 5: Negativos: Can't, Shouldn't, Mustn't."
            ],
            "preguntas": [
                {"q": "Verdadero o Falso: 'Should' se usa para dar consejos.", "ops": ["Verdadero", "Falso"], "ok": "Verdadero"},
                {"q": "Completa: She ___ swim very fast.", "ops": ["can", "cans"], "ok": "can"},
                {"q": "Identifica el modal de obligación:", "ops": ["Must", "Can"], "ok": "Must"},
                {"q": "Escribe 'poder' en inglés (3 letras):", "tipo": "texto", "ok": "can"},
                {"q": "Verdadero o Falso: 'Can't' significa 'no poder'.", "ops": ["Verdadero", "Falso"], "ok": "Verdadero"}
            ]
        }
    ],
    "Hard": [
        {
            "rama": "Rama 1: Presente Perfecto",
            "clases": [
                "Clase 1: Estructura: Have / Has + Participio Pasado. Ejemplo: I have studied.",
                "Clase 2: Con 'He / She / It' usa 'Has'. Ejemplo: She has finished.",
                "Clase 3: 'Already' (ya) y 'Yet' (todavía/aún en negativas y preguntas).",
                "Clase 4: 'For' indica duración (for two years) y 'Since' punto de inicio (since 2020).",
                "Clase 5: Conecta acciones pasadas con el presente."
            ],
            "preguntas": [
                {"q": "Verdadero o Falso: Con 'She' se usa 'has' en presente perfecto.", "ops": ["Verdadero", "Falso"], "ok": "Verdadero"},
                {"q": "Completa: I have lived here _____ 2022.", "ops": ["since", "for"], "ok": "since"},
                {"q": "Identifica la oración correcta:", "ops": ["She has finished", "She have finished"], "ok": "She has finished"},
                {"q": "Escribe 'desde' en inglés (5 letras):", "tipo": "texto", "ok": "since"},
                {"q": "Verdadero o Falso: 'For' se usa para períodos de tiempo.", "ops": ["Verdadero", "Falso"], "ok": "Verdadero"}
            ]
        },
        {
            "rama": "Rama 2: Condicionales (If)",
            "clases": [
                "Clase 1: Primer condicional (real): If + Presente, Will + Verbo. Ejemplo: If I study, I will pass.",
                "Clase 2: Segundo condicional (hipotético): If + Pasado, Would + Verbo.",
                "Clase 3: Ejemplo segundo condicional: If I had time, I would travel.",
                "Clase 4: Nunca pongas 'will' justo después de 'If'.",
                "Clase 5: Puedes invertir el orden sin coma: I will pass if I study."
            ],
            "preguntas": [
                {"q": "Verdadero o Falso: 'If I study, I will pass' es primer condicional.", "ops": ["Verdadero", "Falso"], "ok": "Verdadero"},
                {"q": "Completa: If I had money, I _____ buy a car.", "ops": ["would", "will"], "ok": "would"},
                {"q": "Identifica la forma correcta:", "ops": ["If it rains, I will stay", "If it will rain, I stay"], "ok": "If it rains, I will stay"},
                {"q": "Escribe 'si' condicional en inglés (2 letras):", "tipo": "texto", "ok": "if"},
                {"q": "Verdadero o Falso: 'Would' expresa situaciones hipotéticas.", "ops": ["Verdadero", "Falso"], "ok": "Verdadero"}
            ]
        }
    ],
    "Expert/Nativo": [
        {
            "rama": "Rama 1: Phrasal Verbs y Modismos",
            "clases": [
                "Clase 1: 'Give up' = Rendirse. Ejemplo: Never give up.",
                "Clase 2: 'Figure out' = Resolver o entender algo. Ejemplo: I figured it out.",
                "Clase 3: 'Piece of cake' = Algo muy fácil (pan comido).",
                "Clase 4: 'Hit the nail on the head' = Dar en el clavo.",
                "Clase 5: 'Get the hang of it' = Agarrarle el truco a algo."
            ],
            "preguntas": [
                {"q": "Verdadero o Falso: 'Give up' significa 'rendirse'.", "ops": ["Verdadero", "Falso"], "ok": "Verdadero"},
                {"q": "Completa el modismo para decir 'pan comido': Piece of _____.", "ops": ["cake", "bread"], "ok": "cake"},
                {"q": "Identifica qué significa 'Figure out':", "ops": ["Resolver / Entender", "Salir corriendo"], "ok": "Resolver / Entender"},
                {"q": "Escribe el verbo frasal 'rendirse' (give __):", "tipo": "texto", "ok": "give up"},
                {"q": "Verdadero o Falso: 'Get the hang of it' significa agarrarle el truco.", "ops": ["Verdadero", "Falso"], "ok": "Verdadero"}
            ]
        }
    ]
}

JUEGOS = [
    {"n": 1, "q": "¿Cómo se dice 'Hola' en inglés?", "ops": ["Hello", "Thanks", "Goodbye"], "ok": "Hello"},
    {"n": 2, "q": "¿Qué número es 'Four'?", "ops": ["4", "5", "3"], "ok": "4"},
    {"n": 3, "q": "Traduce: 'Thank you'", "ops": ["Gracias", "Por favor", "De nada"], "ok": "Gracias"},
    {"n": 4, "q": "¿Cuál es el pasado de 'Go'?", "ops": ["Went", "Gone", "Goes"], "ok": "Went"},
    {"n": 5, "q": "¿Qué significa 'Tomorrow'?", "ops": ["Mañana", "Ayer", "Hoy"], "ok": "Mañana"},
    {"n": 6, "q": "Completa: I ___ a student.", "ops": ["am", "is", "are"], "ok": "am"},
    {"n": 7, "q": "¿Qué significa 'Give up'?", "ops": ["Rendirse", "Subir", "Regalar"], "ok": "Rendirse"},
    {"n": 8, "q": "Traduce: 'Water'", "ops": ["Agua", "Fuego", "Tierra"], "ok": "Agua"},
    {"n": 9, "q": "¿Qué significa 'Piece of cake'?", "ops": ["Pan comido / Muy fácil", "Un problema", "Tengo hambre"], "ok": "Pan comido / Muy fácil"},
    {"n": 10, "q": "Completa: She ___ English every day.", "ops": ["speaks", "speak", "speaking"], "ok": "speaks"}
]

HTML_PAGE = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>C-PRE "LENGUAJES" - INGLÉS</title>
<style>
* { box-sizing: border-box; }
body { margin: 0; background: #09090b; color: #f4f4f5; font-family: system-ui, Arial, sans-serif; padding-bottom: 50px; }
header { background: #000; border-bottom: 1px solid #27272a; padding: 14px; text-align: center; }
header h1 { margin: 0; font-size: 18px; letter-spacing: 1px; color: #fff; }
header p { margin: 4px 0 0; font-size: 12px; color: #a1a1aa; }
.wrap { max-width: 720px; margin: 0 auto; padding: 14px; }
.card { background: #121215; border: 1px solid #27272a; padding: 14px; margin-bottom: 14px; border-radius: 6px; }
.row { display: flex; gap: 8px; flex-wrap: wrap; }
select, input[type="text"], button { width: 100%; padding: 11px; font-size: 14px; border-radius: 5px; border: 1px solid #52525b; background: #18181b; color: #fff; margin-top: 8px; }
button { background: #fff; color: #09090b; font-weight: 700; border: none; cursor: pointer; }
button.sec { background: #27272a; color: #fff; border: 1px solid #52525b; }
.clase { background: #09090b; border-left: 3px solid #fff; padding: 9px 11px; margin: 7px 0; font-size: 13.5px; }
.preg { background: #18181b; border: 1px solid #3f3f46; padding: 10px; margin: 8px 0; border-radius: 4px; }
.nota-box { background: #18181b; border: 1px solid #fff; padding: 12px; margin-top: 10px; font-weight: 700; }
.dueno { position: fixed; right: 12px; bottom: 8px; font-size: 11px; font-weight: 800; color: #a1a1aa; background: #09090b; padding: 3px 7px; border: 1px solid #27272a; }
</style>
</head>
<body>
<header>
  <h1>BIENVENIDO A C-PRE "LENGUAJES"</h1>
  <p>Creaciones de Celso · Curso Directo de Inglés</p>
</header>

<div class="wrap">
  <div class="card">
    <strong>Selecciona Nivel y Rama:</strong>
    <div class="row">
      <select id="selNivel" onchange="cambiarNivel()"></select>
      <select id="selRama" onchange="renderizarRama()"></select>
    </div>
    <p id="lblEstado" style="font-size:13px;color:#a1a1aa;margin:8px 0 0;">Nota actual: 0/20 (Apruebas desde 10/20)</p>
  </div>

  <div class="card">
    <h2 id="tituloRama" style="margin:0 0 10px;font-size:16px;"></h2>
    <div id="listaClases"></div>
    <button type="button" onclick="abrirExamen()">PRESENTAR EVALUACIÓN (20 PTS)</button>
    <div id="zonaExamen" style="display:none;margin-top:12px;"></div>
  </div>

  <div class="card">
    <h3 style="margin:0 0 6px;font-size:15px;">JUEGOS RÁPIDOS DE INGLÉS (10 RETOS)</h3>
    <p id="juegoTitulo" style="font-size:13px;color:#a1a1aa;margin:0 0 6px;"></p>
    <p id="juegoPreg" style="font-weight:700;margin:6px 0;"></p>
    <div id="juegoOps"></div>
    <p id="juegoFeedback" style="font-size:13px;margin:8px 0 0;color:#d4d4d8;">Elige una respuesta.</p>
  </div>

  <div class="card">
    <h3 style="margin:0 0 6px;font-size:15px;">PROFESOR / BUSCADOR DE INGLÉS</h3>
    <input type="text" id="txtConsulta" placeholder="Escribe una palabra o duda en inglés...">
    <button type="button" onclick="consultarProfesor()">PREGUNTAR AL PROFESOR</button>
    <div id="resConsulta" class="clase" style="margin-top:10px;">Escribe tu duda arriba y pulsa preguntar.</div>
  </div>
</div>

<div class="dueno">DUEÑO CELSO</div>

<script>
const CURSO = __CURSO_JSON__;
const JUEGOS = __JUEGOS_JSON__;

let nivelActual = "Easy";
let ramaIdx = 0;
let juegoIdx = 0;
let juegoPts = 0;

function iniciar() {
  const selN = document.getElementById("selNivel");
  Object.keys(CURSO).forEach(nv => {
    const op = document.createElement("option");
    op.value = nv;
    op.textContent = "Nivel: " + nv;
    selN.appendChild(op);
  });
  cargarRamas();
  renderizarJuego();
}

function cambiarNivel() {
  nivelActual = document.getElementById("selNivel").value;
  ramaIdx = 0;
  cargarRamas();
}

function cargarRamas() {
  const selR = document.getElementById("selRama");
  selR.innerHTML = "";
  CURSO[nivelActual].forEach((r, i) => {
    const op = document.createElement("option");
    op.value = i;
    op.textContent = r.rama;
    selR.appendChild(op);
  });
  renderizarRama();
}

function renderizarRama() {
  ramaIdx = parseInt(document.getElementById("selRama").value || "0", 10);
  const data = CURSO[nivelActual][ramaIdx];
  document.getElementById("tituloRama").textContent = data.rama;
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

function abrirExamen() {
  const data = CURSO[nivelActual][ramaIdx];
  const zona = document.getElementById("zonaExamen");
  zona.style.display = "block";
  let html = "<strong>Evaluación (4 pts cada pregunta · Total 20 pts):</strong>";
  data.preguntas.forEach((p, idx) => {
    html += `<div class="preg"><div>${idx + 1}. ${p.q}</div>`;
    if (p.tipo === "texto") {
      html += `<input type="text" id="ex_txt_${idx}" placeholder="Escribe tu respuesta...">`;
    } else {
      p.ops.forEach((op, j) => {
        html += `<label style="display:block;margin-top:6px;"><input type="radio" name="ex_rad_${idx}" value="${op}" ${j === 0 ? "checked" : ""}> ${op}</label>`;
      });
    }
    html += `</div>`;
  });
  html += `<button type="button" onclick="calificar()">CALIFICAR EXAMEN</button><div id="resExamen"></div>`;
  zona.innerHTML = html;
}

function calificar() {
  const data = CURSO[nivelActual][ramaIdx];
  let nota = 0;
  data.preguntas.forEach((p, idx) => {
    if (p.tipo === "texto") {
      const val = (document.getElementById("ex_txt_" + idx).value || "").trim().toLowerCase();
      if (val === p.ok.toLowerCase()) nota += 4;
    } else {
      const sel = document.querySelector(`input[name="ex_rad_${idx}"]:checked`);
      if (sel && sel.value === p.ok) nota += 4;
    }
  });
  const aprobo = nota >= 10;
  document.getElementById("lblEstado").textContent = `Última nota: ${nota}/20 (${aprobo ? "APROBADO" : "REPROBADO"})`;
  let extraBtn = "";
  if (aprobo && ramaIdx + 1 < CURSO[nivelActual].length) {
    extraBtn = `<button type="button" onclick="siguienteRama()">PASAR A LA SIGUIENTE RAMA</button>`;
  }
  document.getElementById("resExamen").innerHTML = `<div class="nota-box">Resultado: ${nota}/20 — ${aprobo ? "¡APROBADO!" : "Reprobado (necesitas mínimo 10/20)"}</div>${extraBtn}`;
}

function siguienteRama() {
  document.getElementById("selRama").value = String(ramaIdx + 1);
  renderizarRama();
}

function renderizarJuego() {
  const j = JUEGOS[juegoIdx % JUEGOS.length];
  document.getElementById("juegoTitulo").textContent = `Reto ${j.n}/10 · Puntos: ${juegoPts}`;
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
        juegoPts += 10;
        document.getElementById("juegoFeedback").textContent = "¡Correcto! +10 puntos.";
      } else {
        document.getElementById("juegoFeedback").textContent = "Incorrecto. Era: " + j.ok;
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
  box.textContent = "Consultando...";
  try {
    const r = await fetch("/api/preguntar", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({pregunta: txt})
    });
    const d = await r.json();
    box.textContent = d.respuesta;
  } catch (e) {
    box.textContent = "No se pudo conectar con el servidor.";
  }
}

iniciar();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    html = HTML_PAGE.replace("__CURSO_JSON__", json.dumps(CURSO_INGLES, ensure_ascii=True))
    html = html.replace("__JUEGOS_JSON__", json.dumps(JUEGOS, ensure_ascii=True))
    return html

@app.route("/api/preguntar", methods=["POST"])
def preguntar():
    data = request.get_json(silent=True) or {}
    pregunta = (data.get("pregunta") or "").strip()
    if not pregunta:
        return jsonify({"respuesta": "Escribe una duda primero."})

    if GEMINI_API_KEY:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
        payload = json.dumps({
            "contents": [{"parts": [{"text": f"Eres profesor de inglés. Responde breve y claro en español con ejemplos en inglés: {pregunta}"}]}]
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                txt = res.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                if txt:
                    return jsonify({"respuesta": txt.strip()})
        except Exception:
            pass

    return jsonify({"respuesta": f"Profesor Inglés: Sobre '{pregunta}', recuerda practicar la estructura en presente, pasado y futuro usando ejemplos cortos."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
