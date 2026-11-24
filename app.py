import os
import json
import re
import urllib.request
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

PUERTO_SERVIDOR = int(os.environ.get("PORT", 5000))
HOST_SERVIDOR = os.environ.get("HOST", "0.0.0.0")
MODELO_GEMINI = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
CLAVE_GEMINI = os.environ.get("GEMINI_API_KEY", "").strip()

NIVELES_SISTEMA = [
    "Easy",
    "Medium",
    "Hard",
    "Expert/Nativo",
]

ORDINALES_RAMAS = {
    "1": "primera",
    "2": "segunda",
    "3": "tercera",
    "4": "cuarta",
    "5": "quinta",
    "6": "sexta",
    "7": "séptima",
}

IDIOMAS_CONFIG = [
    {
        "nombre": "Inglés",
        "codigo": "en",
        "saludo": "Hello",
        "listo": "I am ready",
        "manana": "Good morning",
        "gracias": "Thank you",
        "frase": "I speak English every day",
        "numeros": "One, two, three, four, five",
        "identidad": "I am a student",
        "pasado": "Yesterday I practiced English",
        "futuro": "I am going to study tomorrow",
        "continuo": "I am learning right now",
        "comparativo": "Practice is better than theory",
        "modal": "You should practice daily",
        "perfecto": "I have studied English",
        "condicional": "If I practice, I improve",
        "pasiva": "English is spoken worldwide",
        "compuesto": "Keep up the good work",
        "modismo": "Piece of cake",
        "nativo": "I get the hang of it quickly",
        "vocab_extra": {
            "hola": "Hello",
            "gracias": "Thank you",
            "uno": "One",
            "dos": "Two",
            "tres": "Three",
            "agua": "Water",
            "casa": "House",
            "libro": "Book",
            "amigo": "Friend",
            "tiempo": "Time",
        },
    },
    {
        "nombre": "Español",
        "codigo": "es",
        "saludo": "Hola",
        "listo": "Estoy listo",
        "manana": "Buenos días",
        "gracias": "Gracias",
        "frase": "Hablo español todos los días",
        "numeros": "Uno, dos, tres, cuatro, cinco",
        "identidad": "Soy estudiante",
        "pasado": "Ayer practiqué español",
        "futuro": "Voy a estudiar mañana",
        "continuo": "Estoy aprendiendo ahora mismo",
        "comparativo": "Practicar es mejor que memorizar",
        "modal": "Debes practicar cada día",
        "perfecto": "He estudiado español",
        "condicional": "Si practico, avanzo más rápido",
        "pasiva": "El español se habla en muchos países",
        "compuesto": "Seguir adelante con constancia",
        "modismo": "Pan comido",
        "nativo": "Le agarro el hilo rápido",
        "vocab_extra": {
            "hola": "Hola",
            "gracias": "Gracias",
            "uno": "Uno",
            "dos": "Dos",
            "tres": "Tres",
            "agua": "Agua",
            "casa": "Casa",
            "libro": "Libro",
            "amigo": "Amigo",
            "tiempo": "Tiempo",
        },
    },
    {
        "nombre": "Portugués",
        "codigo": "pt",
        "saludo": "Olá",
        "listo": "Estou pronto",
        "manana": "Bom dia",
        "gracias": "Obrigado",
        "frase": "Eu falo português todos os dias",
        "numeros": "Um, dois, três, quatro, cinco",
        "identidad": "Eu sou estudante",
        "pasado": "Ontem eu pratiquei português",
        "futuro": "Eu vou estudar amanhã",
        "continuo": "Estou aprendendo agora",
        "comparativo": "Praticar é melhor que decorar",
        "modal": "Você deve praticar todo dia",
        "perfecto": "Eu tenho estudado português",
        "condicional": "Se eu praticar, eu melhoro",
        "pasiva": "O português é falado no Brasil",
        "compuesto": "Manter o ritmo de estudo",
        "modismo": "Moleza",
        "nativo": "Pego o jeito rapidinho",
        "vocab_extra": {
            "hola": "Olá",
            "gracias": "Obrigado / Obrigada",
            "uno": "Um",
            "dos": "Dois",
            "tres": "Três",
            "agua": "Água",
            "casa": "Casa",
            "libro": "Livro",
            "amigo": "Amigo",
            "tiempo": "Tempo",
        },
    },
    {
        "nombre": "Francés",
        "codigo": "fr",
        "saludo": "Bonjour",
        "listo": "Je suis prêt",
        "manana": "Bonjour",
        "gracias": "Merci",
        "frase": "Je parle français chaque jour",
        "numeros": "Un, deux, trois, quatre, cinq",
        "identidad": "Je suis étudiant",
        "pasado": "Hier j'ai pratiqué le français",
        "futuro": "Je vais étudier demain",
        "continuo": "J'apprends maintenant",
        "comparativo": "Pratiquer est mieux que réciter",
        "modal": "Tu dois pratiquer tous les jours",
        "perfecto": "J'ai étudié le français",
        "condicional": "Si je pratique, je progresse",
        "pasiva": "Le français est parlé partout",
        "compuesto": "Garder le bon rythme",
        "modismo": "C'est du gâteau",
        "nativo": "Je prends le coup de main vite",
        "vocab_extra": {
            "hola": "Bonjour",
            "gracias": "Merci",
            "uno": "Un",
            "dos": "Deux",
            "tres": "Trois",
            "agua": "Eau",
            "casa": "Maison",
            "libro": "Livre",
            "amigo": "Ami",
            "tiempo": "Temps",
        },
    },
    {
        "nombre": "Alemán",
        "codigo": "de",
        "saludo": "Hallo",
        "listo": "Ich bin bereit",
        "manana": "Guten Morgen",
        "gracias": "Danke",
        "frase": "Ich spreche jeden Tag Deutsch",
        "numeros": "Eins, zwei, drei, vier, fünf",
        "identidad": "Ich bin Schüler",
        "pasado": "Gestern habe ich Deutsch geübt",
        "futuro": "Ich werde morgen lernen",
        "continuo": "Ich lerne gerade",
        "comparativo": "Üben ist besser als auswendig lernen",
        "modal": "Du solltest täglich üben",
        "perfecto": "Ich habe Deutsch gelernt",
        "condicional": "Wenn ich übe, werde ich besser",
        "pasiva": "Deutsch wird in Deutschland gesprochen",
        "compuesto": "Dranbleiben beim Lernen",
        "modismo": "Ein Kinderspiel",
        "nativo": "Ich habe den Dreh schnell raus",
        "vocab_extra": {
            "hola": "Hallo",
            "gracias": "Danke",
            "uno": "Eins",
            "dos": "Zwei",
            "tres": "Drei",
            "agua": "Wasser",
            "casa": "Haus",
            "libro": "Buch",
            "amigo": "Freund",
            "tiempo": "Zeit",
        },
    },
    {
        "nombre": "Italiano",
        "codigo": "it",
        "saludo": "Ciao",
        "listo": "Sono pronto",
        "manana": "Buongiorno",
        "gracias": "Grazie",
        "frase": "Studio italiano ogni giorno",
        "numeros": "Uno, due, tre, quattro, cinque",
        "identidad": "Sono uno studente",
        "pasado": "Ieri ho praticato italiano",
        "futuro": "Studierò domani",
        "continuo": "Sto imparando adesso",
        "comparativo": "Praticare è meglio che ripetere",
        "modal": "Devi esercitarti ogni giorno",
        "perfecto": "Ho studiato italiano",
        "condicional": "Se mi esercito, miglioro",
        "pasiva": "L'italiano si parla in Italia",
        "compuesto": "Tenere alto il ritmo",
        "modismo": "Un gioco da ragazzi",
        "nativo": "Ci prendo subito la mano",
        "vocab_extra": {
            "hola": "Ciao",
            "gracias": "Grazie",
            "uno": "Uno",
            "dos": "Due",
            "tres": "Tre",
            "agua": "Acqua",
            "casa": "Casa",
            "libro": "Libro",
            "amigo": "Amico",
            "tiempo": "Tempo",
        },
    },
    {
        "nombre": "Chino Mandarín",
        "codigo": "zh",
        "saludo": "Ni hao",
        "listo": "Wo zhunbei hao le",
        "manana": "Zaoshang hao",
        "gracias": "Xiexie",
        "frase": "Wo meitian shuo zhongwen",
        "numeros": "yi, er, san, si, wu",
        "identidad": "Wo shi xuesheng",
        "pasado": "Zuotian wo lianxi le zhongwen",
        "futuro": "Wo mingtian yao xuexi",
        "continuo": "Wo zhengzai xuexi",
        "comparativo": "Lianxi bi siji genghao",
        "modal": "Ni yinggai meitian lianxi",
        "perfecto": "Wo xueguo zhongwen",
        "condicional": "Ruguo wo lianxi jiu hui jinbu",
        "pasiva": "Zhongwen bei guangfan shiyong",
        "compuesto": "Jianchi meitian lianxi",
        "modismo": "Xiao cai yi die",
        "nativo": "Wo hen kuai jiu neng zhangwo qiaomen",
        "vocab_extra": {
            "hola": "Ni hao",
            "gracias": "Xiexie",
            "uno": "yi",
            "dos": "er",
            "tres": "san",
            "agua": "shui",
            "casa": "jia",
            "libro": "shu",
            "amigo": "pengyou",
            "tiempo": "shijian",
        },
    },
    {
        "nombre": "Japonés",
        "codigo": "ja",
        "saludo": "Konnichiwa",
        "listo": "Junbi dekimashita",
        "manana": "Ohayo gozaimasu",
        "gracias": "Arigato",
        "frase": "Mainichi nihongo o renshu shimasu",
        "numeros": "ichi, ni, san, shi, go",
        "identidad": "Watashi wa gakusei desu",
        "pasado": "Kino nihongo o renshu shimashita",
        "futuro": "Ashita benkyo shimasu",
        "continuo": "Ima benkyo shite imasu",
        "comparativo": "Renshu wa anki yori ii desu",
        "modal": "Mainichi renshu subeki desu",
        "perfecto": "Nihongo o benkyo shita koto ga arimasu",
        "condicional": "Renshu sureba jotatsu shimasu",
        "pasiva": "Nihongo wa nihon de hanasaremasu",
        "compuesto": "Kotsukotsu tsuzukeru",
        "modismo": "Ocha-no-ko saisai",
        "nativo": "Sugu kotsu o tsukamimasu",
        "vocab_extra": {
            "hola": "Konnichiwa",
            "gracias": "Arigato",
            "uno": "ichi",
            "dos": "ni",
            "tres": "san",
            "agua": "mizu",
            "casa": "ie",
            "libro": "hon",
            "amigo": "tomodachi",
            "tiempo": "jikan",
        },
    },
    {
        "nombre": "Coreano",
        "codigo": "ko",
        "saludo": "Annyeonghaseyo",
        "listo": "Junbi-dwaesseo-yo",
        "manana": "Jo-eun achim",
        "gracias": "Gamsahamnida",
        "frase": "Maeil han-gu-geo-reul yeon-seup-hae-yo",
        "numeros": "ha-na, dul, set, net, da-seot",
        "identidad": "Jeo-neun hak-saeng-i-e-yo",
        "pasado": "Eo-je han-gu-geo-reul gong-bu-haet-seo-yo",
        "futuro": "Nae-il gong-bu-hal geo-ye-yo",
        "continuo": "Ji-geum bae-u-go is-seo-yo",
        "comparativo": "Yeon-seub-i am-gi-bo-da jo-a-yo",
        "modal": "Maeil yeon-seub-hae-ya hae-yo",
        "perfecto": "Han-gu-geo-reul gong-bu-hae bwat-seo-yo",
        "condicional": "Yeon-seub-ha-myeon sil-ryeog-i neur-eo-yo",
        "pasiva": "Han-gu-geo-neun han-guk-e-seo sa-yong-dwae-yo",
        "compuesto": "Kku-jun-hi i-eo-ga-gi",
        "modismo": "Sik-eun juk meok-gi",
        "nativo": "Yo-ryeong-eul geum-bang jab-a-yo",
        "vocab_extra": {
            "hola": "Annyeonghaseyo",
            "gracias": "Gamsahamnida",
            "uno": "hana",
            "dos": "dul",
            "tres": "set",
            "agua": "mul",
            "casa": "jip",
            "libro": "chaek",
            "amigo": "chingu",
            "tiempo": "sigan",
        },
    },
    {
        "nombre": "Árabe",
        "codigo": "ar",
        "saludo": "Marhaban",
        "listo": "Ana musta'idd",
        "manana": "Sabah al-khayr",
        "gracias": "Shukran",
        "frase": "Atadarrab ala al-arabiyyah kull yawm",
        "numeros": "wahid, ithnan, thalathah, arba'ah, khamsah",
        "identidad": "Ana talib",
        "pasado": "Tadarrabtu bil-ams ala al-arabiyyah",
        "futuro": "Sa'adrusu ghadan",
        "continuo": "Ata'allam al-an",
        "comparativo": "At-tadrib afdal min al-hifz",
        "modal": "Yajibu an tatadarraba yawmiyyan",
        "perfecto": "Laqad darastu al-arabiyyah",
        "condicional": "Idha tadarrabtu fa-sa'utqin",
        "pasiva": "Tustakhdam al-arabiyyah fi buldan kathirah",
        "compuesto": "Al-istimrar bi-thabat",
        "modismo": "Ashal min shurbat ma'",
        "nativo": "Afham al-fikrah bi-sur'ah",
        "vocab_extra": {
            "hola": "Marhaban",
            "gracias": "Shukran",
            "uno": "wahid",
            "dos": "ithnan",
            "tres": "thalathah",
            "agua": "ma'",
            "casa": "bayt",
            "libro": "kitab",
            "amigo": "sadiq",
            "tiempo": "waqt",
        },
    },
    {
        "nombre": "Ruso",
        "codigo": "ru",
        "saludo": "Privet",
        "listo": "Ya gotov",
        "manana": "Dobroye utro",
        "gracias": "Spasibo",
        "frase": "Ya kazhdyy den uchu russkiy",
        "numeros": "odin, dva, tri, chetyre, pyat",
        "identidad": "Ya student",
        "pasado": "Vchera ya zanimalsya russkim",
        "futuro": "Zavtra ya budu zanimatsya",
        "continuo": "Ya seychas uchus",
        "comparativo": "Praktika luchshe zubryozhki",
        "modal": "Nuzhno zanimatsya kazhdyy den",
        "perfecto": "Ya uzhe uchil russkiy",
        "condicional": "Esli budu zanimatsya, uluchshu",
        "pasiva": "Russkiy yazyk izuchayut vezde",
        "compuesto": "Sokranyat temp zanyatiy",
        "modismo": "Proshche prostogo",
        "nativo": "Bystro skhvatyvayu sut",
        "vocab_extra": {
            "hola": "Privet",
            "gracias": "Spasibo",
            "uno": "odin",
            "dos": "dva",
            "tres": "tri",
            "agua": "voda",
            "casa": "dom",
            "libro": "kniga",
            "amigo": "drug",
            "tiempo": "vremya",
        },
    },
    {
        "nombre": "Hindi",
        "codigo": "hi",
        "saludo": "Namaste",
        "listo": "Main taiyaar hoon",
        "manana": "Suprabhat",
        "gracias": "Dhanyavaad",
        "frase": "Main roz Hindi ka abhyaas karta hoon",
        "numeros": "ek, do, teen, chaar, paanch",
        "identidad": "Main chhatra hoon",
        "pasado": "Kal maine Hindi ka abhyaas kiya",
        "futuro": "Main kal padhaai karoonga",
        "continuo": "Main abhi seekh raha hoon",
        "comparativo": "Abhyaas ratne se behtar hai",
        "modal": "Tumhein roz abhyaas karna chahiye",
        "perfecto": "Maine Hindi seekhi hai",
        "condicional": "Agar main abhyaas karoonga to sudhaar hoga",
        "pasiva": "Hindi Bharat mein boli jaati hai",
        "compuesto": "Nirantar abhyaas banaaye rakhna",
        "modismo": "Baayein haath ka khel",
        "nativo": "Main jaldi tareeqa samajh leta hoon",
        "vocab_extra": {
            "hola": "Namaste",
            "gracias": "Dhanyavaad",
            "uno": "ek",
            "dos": "do",
            "tres": "teen",
            "agua": "paani",
            "casa": "ghar",
            "libro": "kitaab",
            "amigo": "dost",
            "tiempo": "samay",
        },
    },
    {
        "nombre": "Bengalí",
        "codigo": "bn",
        "saludo": "Nomoshkar",
        "listo": "Ami prostut",
        "manana": "Shubho shokal",
        "gracias": "Dhonnobad",
        "frase": "Ami protidin Bangla onushilon kori",
        "numeros": "ek, dui, tin, char, pach",
        "identidad": "Ami chhatro",
        "pasado": "Gotokal ami Bangla onushilon korechi",
        "futuro": "Ami agamikal porbo",
        "continuo": "Ami ekhon shikhchi",
        "comparativo": "Onushilon mukhostho korar cheye bhalo",
        "modal": "Tomar protidin onushilon kora uchit",
        "perfecto": "Ami Bangla shikhechi",
        "condicional": "Ami onushilon korle unnoti korbo",
        "pasiva": "Bangla bhasha byapokbhabe bola hoy",
        "compuesto": "Niyomito onushilon bojay rakha",
        "modismo": "Bam hater khel",
        "nativo": "Ami druto koushol dhore feli",
        "vocab_extra": {
            "hola": "Nomoshkar",
            "gracias": "Dhonnobad",
            "uno": "ek",
            "dos": "dui",
            "tres": "tin",
            "agua": "jol",
            "casa": "bari",
            "libro": "boi",
            "amigo": "bondhu",
            "tiempo": "shomoy",
        },
    },
    {
        "nombre": "Turco",
        "codigo": "tr",
        "saludo": "Merhaba",
        "listo": "Hazirim",
        "manana": "Gunaydin",
        "gracias": "Tesekkurler",
        "frase": "Her gun Turkce pratik yapiyorum",
        "numeros": "bir, iki, uc, dort, bes",
        "identidad": "Ben ogrenciyim",
        "pasado": "Dun Turkce calistim",
        "futuro": "Yarin calisacagim",
        "continuo": "Su an ogreniyorum",
        "comparativo": "Pratik yapmak ezberlemekten iyidir",
        "modal": "Her gun pratik yapmalisin",
        "perfecto": "Turkce ogrendim",
        "condicional": "Pratik yaparsam gelisirim",
        "pasiva": "Turkce Turkiye'de konusurul",
        "compuesto": "Duzenli calismayi surdurmek",
        "modismo": "Cocuk oyuncagi",
        "nativo": "Isin mantigini cabuk kaparim",
        "vocab_extra": {
            "hola": "Merhaba",
            "gracias": "Tesekkurler",
            "uno": "bir",
            "dos": "iki",
            "tres": "uc",
            "agua": "su",
            "casa": "ev",
            "libro": "kitap",
            "amigo": "arkadas",
            "tiempo": "zaman",
        },
    },
    {
        "nombre": "Neerlandés",
        "codigo": "nl",
        "saludo": "Hallo",
        "listo": "Ik ben klaar",
        "manana": "Goedemorgen",
        "gracias": "Dank je",
        "frase": "Ik oefen elke dag Nederlands",
        "numeros": "een, twee, drie, vier, vijf",
        "identidad": "Ik ben student",
        "pasado": "Gisteren heb ik Nederlands geoefend",
        "futuro": "Ik ga morgen studeren",
        "continuo": "Ik leer nu",
        "comparativo": "Oefenen is beter dan uit je hoofd leren",
        "modal": "Je moet dagelijks oefenen",
        "perfecto": "Ik heb Nederlands gestudeerd",
        "condicional": "Als ik oefen, word ik beter",
        "pasiva": "Nederlands wordt in Nederland gesproken",
        "compuesto": "Het ritme vasthouden",
        "modismo": "Een fluitje van een cent",
        "nativo": "Ik heb de slag snel te pakken",
        "vocab_extra": {
            "hola": "Hallo",
            "gracias": "Dank je",
            "uno": "een",
            "dos": "twee",
            "tres": "drie",
            "agua": "water",
            "casa": "huis",
            "libro": "boek",
            "amigo": "vriend",
            "tiempo": "tijd",
        },
    },
    {
        "nombre": "Polaco",
        "codigo": "pl",
        "saludo": "Czesc",
        "listo": "Jestem gotowy",
        "manana": "Dzien dobry",
        "gracias": "Dziekuje",
        "frase": "Codziennie cwicze polski",
        "numeros": "jeden, dwa, trzy, cztery, piec",
        "identidad": "Jestem studentem",
        "pasado": "Wczoraj cwiczylem polski",
        "futuro": "Bede sie uczyc jutro",
        "continuo": "Teraz sie ucze",
        "comparativo": "Cwiczenie jest lepsze niz wkuwanie",
        "modal": "Powinienes cwiczc codziennie",
        "perfecto": "Uczylem sie polskiego",
        "condicional": "Jesli bede cwiczc, zrobie postep",
        "pasiva": "Po polsku mowi sie w Polsce",
        "compuesto": "Utrzymac stale tempo",
        "modismo": "Bulka z maslem",
        "nativo": "Szybko lapie sedno",
        "vocab_extra": {
            "hola": "Czesc",
            "gracias": "Dziekuje",
            "uno": "jeden",
            "dos": "dwa",
            "tres": "trzy",
            "agua": "woda",
            "casa": "dom",
            "libro": "ksiazka",
            "amigo": "przyjaciel",
            "tiempo": "czas",
        },
    },
    {
        "nombre": "Sueco",
        "codigo": "sv",
        "saludo": "Hej",
        "listo": "Jag ar redo",
        "manana": "God morgon",
        "gracias": "Tack",
        "frase": "Jag ovar svenska varje dag",
        "numeros": "ett, tva, tre, fyra, fem",
        "identidad": "Jag ar student",
        "pasado": "Igar ovade jag svenska",
        "futuro": "Jag ska plugga imorgon",
        "continuo": "Jag lar mig just nu",
        "comparativo": "Att ova ar battre an att rabbla",
        "modal": "Du bor ova varje dag",
        "perfecto": "Jag har studerat svenska",
        "condicional": "Om jag ovar sa blir jag battre",
        "pasiva": "Svenska talas i Sverige",
        "compuesto": "Halla jamnt tempo",
        "modismo": "En barnlek",
        "nativo": "Jag far klam pa det snabbt",
        "vocab_extra": {
            "hola": "Hej",
            "gracias": "Tack",
            "uno": "ett",
            "dos": "tva",
            "tres": "tre",
            "agua": "vatten",
            "casa": "hus",
            "libro": "bok",
            "amigo": "van",
            "tiempo": "tid",
        },
    },
    {
        "nombre": "Griego",
        "codigo": "el",
        "saludo": "Geia sou",
        "listo": "Eimai etoimos",
        "manana": "Kalimera",
        "gracias": "Efcharisto",
        "frase": "Exaskoumai sta ellinika kathe mera",
        "numeros": "ena, dyo, tria, tessera, pente",
        "identidad": "Eimai foititis",
        "pasado": "Chthes exaskithika sta ellinika",
        "futuro": "Tha diavaso avrio",
        "continuo": "Mathaino tora",
        "comparativo": "I exaskisi einai kalyteri apo tin apostithisi",
        "modal": "Prepei na exaskeise kathimerina",
        "perfecto": "Echo spoudasei ellinika",
        "condicional": "An exaskitho, tha veltiottho",
        "pasiva": "Ta ellinika miliounte stin Ellada",
        "compuesto": "Diatirisi statherou rythmou",
        "modismo": "Paichnidaki",
        "nativo": "Piano grigora to noima",
        "vocab_extra": {
            "hola": "Geia sou",
            "gracias": "Efcharisto",
            "uno": "ena",
            "dos": "dyo",
            "tres": "tria",
            "agua": "nero",
            "casa": "spiti",
            "libro": "vivlio",
            "amigo": "filos",
            "tiempo": "chronos",
        },
    },
    {
        "nombre": "Vietnamita",
        "codigo": "vi",
        "saludo": "Xin chao",
        "listo": "Toi da san sang",
        "manana": "Chao buoi sang",
        "gracias": "Cam on",
        "frase": "Toi luyen tieng Viet moi ngay",
        "numeros": "mot, hai, ba, bon, nam",
        "identidad": "Toi la sinh vien",
        "pasado": "Hom qua toi da luyen tieng Viet",
        "futuro": "Ngay mai toi se hoc",
        "continuo": "Toi dang hoc ngay bay gio",
        "comparativo": "Luyen tap tot hon hoc vet",
        "modal": "Ban nen luyen tap moi ngay",
        "perfecto": "Toi da hoc tieng Viet",
        "condicional": "Neu toi luyen tap, toi se tien bo",
        "pasiva": "Tieng Viet duoc noi o Viet Nam",
        "compuesto": "Duy tri nhip do deu dan",
        "modismo": "De nhu an keo",
        "nativo": "Toi nam bat cach lam rat nhanh",
        "vocab_extra": {
            "hola": "Xin chao",
            "gracias": "Cam on",
            "uno": "mot",
            "dos": "hai",
            "tres": "ba",
            "agua": "nuoc",
            "casa": "nha",
            "libro": "sach",
            "amigo": "ban",
            "tiempo": "thoi gian",
        },
    },
    {
        "nombre": "Persa",
        "codigo": "fa",
        "saludo": "Salam",
        "listo": "Amadeh-am",
        "manana": "Sobh be-kheyr",
        "gracias": "Mamnoon",
        "frase": "Har rooz Farsi tamrin mikonam",
        "numeros": "yek, do, seh, chahar, panj",
        "identidad": "Man daneshjoo hastam",
        "pasado": "Dirooz Farsi tamrin kardam",
        "futuro": "Farda dars mikhanam",
        "continuo": "Alan dar hal-e yadgiri hastam",
        "comparativo": "Tamrin kardan behtar az hefz kardan ast",
        "modal": "Bayad har rooz tamrin koni",
        "perfecto": "Farsi khandeh-am",
        "condicional": "Agar tamrin konam pishraft mikonam",
        "pasiva": "Farsi dar Iran sohbat mishavad",
        "compuesto": "Hefz-e peyvastegi dar motale'eh",
        "modismo": "Mesl-e ab khordan",
        "nativo": "Zood qoloq-e kar dastam miayad",
        "vocab_extra": {
            "hola": "Salam",
            "gracias": "Mamnoon",
            "uno": "yek",
            "dos": "do",
            "tres": "seh",
            "agua": "ab",
            "casa": "khaneh",
            "libro": "ketab",
            "amigo": "doost",
            "tiempo": "zaman",
        },
    },
]

NOTICIAS_DIARIAS = [
    "Noticia diaria (Ingles): Reading short headlines every morning builds natural recognition of real English phrases.",
    "Noticia diaria (Ingles): Listening to short spoken clips and repeating them aloud trains clarity and rhythm.",
    "Noticia diaria (Ingles): Writing three lines daily about your routine strengthens core verb usage.",
    "Noticia diaria (Ingles): Learning expressions grouped by situation prevents mixing unrelated vocabulary.",
    "Noticia diaria (Ingles): Reviewing missed exam questions turns weak spots into permanent knowledge.",
    "Noticia diaria (Ingles): Practicing simple affirmative and negative sentences early speeds up conversation.",
    "Noticia diaria (Ingles): Fifteen focused minutes every day outperforms cramming once a week.",
    "Noticia diaria (Ingles): Paying attention to context helps you choose the exact phrase native speakers expect.",
    "Noticia diaria (Ingles): Mastering numbers early helps with time, prices, dates, and daily communication.",
    "Noticia diaria (Ingles): Advancing step by step from Easy to Expert builds solid long-term fluency.",
]

TACTICAS_DIARIAS = [
    "Tactica del dia: Completa las 5 clases de la rama actual antes de abrir la hoja de examen.",
    "Tactica del dia: Si eliges saltar Easy, concentra tu atencion en cada punto porque necesitas minimo 10/20.",
    "Tactica del dia: En cada pregunta del examen verifica que estructura pertenece realmente al tema estudiado.",
    "Tactica del dia: Usa los numeros en voz alta despues de estudiar la Rama 3 de Easy.",
    "Tactica del dia: Analiza cada punto perdido en el desglose de calificacion para subir a 20/20.",
    "Tactica del dia: Cambia de idioma en el menu superior para comparar como se expresa la misma idea.",
    "Tactica del dia: Alterna entre ramas teoricas y los 10 juegos adaptados para fijar memoria rapida.",
    "Tactica del dia: No saltes preguntas de escritura; escribir fija ortografia y orden gramatical.",
    "Tactica del dia: Manten coherencia tematica: cada rama trabaja un solo bloque sin mezclar conceptos.",
    "Tactica del dia: Repasa el esquema de 3 pasos al final de cada rama antes de evaluarte.",
]

TRUCOS_DIARIOS = [
    "Truco del dia: Asocia cada expresion nueva con una situacion real en lugar de traducir palabra por palabra.",
    "Truco del dia: En Verdadero o Falso, comprueba si la frase corresponde exactamente al tema de esa rama.",
    "Truco del dia: Cuando escribas tu respuesta en el examen, revisa que no falten letras clave.",
    "Truco del dia: Usa el boton PREGUNTAR para dudas de gramatica y BUSCAR para significado y ejemplo.",
    "Truco del dia: Practica la Rama 3 de Easy hasta dominar los numeros sin dudar.",
    "Truco del dia: Si sacas de 0 a 9 puntos, vuelve a leer las clases de esa rama y presenta de nuevo.",
    "Truco del dia: Observa el contraste entre la expresion principal y la alternativa en cada rama.",
    "Truco del dia: En los niveles Hard y Expert/Nativo, fijate en los matices y expresiones idiomaticas.",
    "Truco del dia: Usa los juegos diarios como calentamiento rapido antes de presentar una evaluacion.",
    "Truco del dia: Manten una meta clara: aprobar cada rama con 10/20 o mas hasta llegar a Expert/Nativo.",
]

def construir_preguntas_examen(idioma, tema, principal, contraste):
    base_corta = principal.split("(")[0].strip().lower()
    return [
        {
            "numero": 1,
            "tipo": "verdadero_falso",
            "puntos": 4,
            "enunciado": f"Verdadero o Falso: En {idioma}, '{principal}' corresponde al tema '{tema}'.",
            "opciones": ["Verdadero", "Falso"],
            "correcta": "Verdadero",
            "explicacion": f"'{principal}' pertenece directamente al tema '{tema}' en {idioma}.",
        },
        {
            "numero": 2,
            "tipo": "completar",
            "puntos": 4,
            "enunciado": f"Completa el bloque correspondiente a '{tema}' en {idioma}: [ __________ ]",
            "opciones": [principal, contraste],
            "correcta": principal,
            "explicacion": f"La expresion correcta para completar este bloque es '{principal}'.",
        },
        {
            "numero": 3,
            "tipo": "identificar",
            "puntos": 4,
            "enunciado": f"Identifica la expresion correcta de '{tema}' en {idioma}:",
            "opciones": [principal, contraste, "Ninguna de las anteriores"],
            "correcta": principal,
            "explicacion": f"'{principal}' identifica correctamente el patron de '{tema}'.",
        },
        {
            "numero": 4,
            "tipo": "escribir",
            "puntos": 4,
            "enunciado": f"Escribe la expresion clave trabajada en '{tema}' ({idioma}):",
            "aceptadas": [principal.lower(), base_corta],
            "muestra": principal,
            "explicacion": f"Respuesta esperada: {principal}.",
        },
        {
            "numero": 5,
            "tipo": "verdadero_falso",
            "puntos": 4,
            "enunciado": f"Verdadero o Falso: '{contraste}' es identico en funcion a '{principal}'.",
            "opciones": ["Verdadero", "Falso"],
            "correcta": "Falso",
            "explicacion": f"'{principal}' y '{contraste}' cumplen funciones distintas en {idioma}.",
        },
    ]

def construir_cinco_clases(idioma, nivel, subtema, principal, contraste):
    return [
        f"Clase 1 ({nivel} · {subtema}): Identifica la expresion central '{principal}' en {idioma} y su sentido exacto.",
        f"Clase 2 (Diferenciacion): Compara '{principal}' con '{contraste}' para distinguir cuando usar cada una.",
        f"Clase 3 (Aplicacion real): Ubica '{principal}' dentro de una situacion cotidiana en {idioma}.",
        f"Clase 4 (Control de errores): Manten el foco solo en '{subtema}' sin mezclar temas ajenos.",
        f"Clase 5 (Cierre de rama): Repasa '{principal}' antes de presentar la evaluacion sobre 20 puntos.",
    ]

def compilar_idioma(cfg):
    nombre = cfg["nombre"]
    plan_easy = [
        {
            "numero": 1,
            "titulo": "Rama 1 · Verbo Ser e Identidad",
            "subtema": "Verbo ser e identidad",
            "principal": cfg["identidad"],
            "contraste": cfg["saludo"],
            "esquema": f"[Easy · Rama 1] -> [Identidad: {cfg['identidad']}]",
            "ejemplos": [f"Identidad: {cfg['identidad']}", f"Contraste: {cfg['saludo']}"],
        },
        {
            "numero": 2,
            "titulo": "Rama 2 · Saludos y Cortesia",
            "subtema": "Saludos y cortesia",
            "principal": cfg["saludo"],
            "contraste": cfg["gracias"],
            "esquema": f"[Easy · Rama 2] -> [Saludo: {cfg['saludo']}] -> [Cortesia: {cfg['gracias']}]",
            "ejemplos": [f"Saludo: {cfg['saludo']}", f"Cortesia: {cfg['gracias']}"],
        },
        {
            "numero": 3,
            "titulo": "Rama 3 · Numeros",
            "subtema": "Numeros",
            "principal": cfg["numeros"],
            "contraste": cfg["identidad"],
            "esquema": f"[Easy · Rama 3] -> [Numeros: {cfg['numeros']}]",
            "ejemplos": [f"Numeros: {cfg['numeros']}", f"Referencia: {cfg['identidad']}"],
        },
        {
            "numero": 4,
            "titulo": "Rama 4 · Saludo de la Manana",
            "subtema": "Saludo de la manana",
            "principal": cfg["manana"],
            "contraste": cfg["saludo"],
            "esquema": f"[Easy · Rama 4] -> [Manana: {cfg['manana']}]",
            "ejemplos": [f"Manana: {cfg['manana']}", f"Saludo general: {cfg['saludo']}"],
        },
        {
            "numero": 5,
            "titulo": "Rama 5 · Agradecimiento",
            "subtema": "Agradecimiento",
            "principal": cfg["gracias"],
            "contraste": cfg["listo"],
            "esquema": f"[Easy · Rama 5] -> [Gracias: {cfg['gracias']}]",
            "ejemplos": [f"Agradecer: {cfg['gracias']}", f"Disponibilidad: {cfg['listo']}"],
        },
        {
            "numero": 6,
            "titulo": "Rama 6 · Estar Listo y Disposicion",
            "subtema": "Estar listo y disposicion",
            "principal": cfg["listo"],
            "contraste": cfg["frase"],
            "esquema": f"[Easy · Rama 6] -> [Listo: {cfg['listo']}]",
            "ejemplos": [f"Listo: {cfg['listo']}", f"Practica: {cfg['frase']}"],
        },
        {
            "numero": 7,
            "titulo": "Rama 7 · Oraciones Cotidianas",
            "subtema": "Oraciones cotidianas",
            "principal": cfg["frase"],
            "contraste": cfg["numeros"],
            "esquema": f"[Easy · Rama 7] -> [Oracion: {cfg['frase']}]",
            "ejemplos": [f"Oracion: {cfg['frase']}", f"Numeros: {cfg['numeros']}"],
        },
    ]

    plan_medium = [
        {
            "numero": 1,
            "titulo": "Rama 1 · Tiempo Pasado",
            "subtema": "Tiempo pasado",
            "principal": cfg["pasado"],
            "contraste": cfg["frase"],
            "esquema": f"[Medium · Rama 1] -> [Pasado: {cfg['pasado']}]",
            "ejemplos": [f"Pasado: {cfg['pasado']}", f"Presente: {cfg['frase']}"],
        },
        {
            "numero": 2,
            "titulo": "Rama 2 · Futuro y Planes",
            "subtema": "Futuro y planes",
            "principal": cfg["futuro"],
            "contraste": cfg["pasado"],
            "esquema": f"[Medium · Rama 2] -> [Futuro: {cfg['futuro']}]",
            "ejemplos": [f"Futuro: {cfg['futuro']}", f"Pasado: {cfg['pasado']}"],
        },
        {
            "numero": 3,
            "titulo": "Rama 3 · Accion en Curso",
            "subtema": "Accion en curso",
            "principal": cfg["continuo"],
            "contraste": cfg["frase"],
            "esquema": f"[Medium · Rama 3] -> [Continuo: {cfg['continuo']}]",
            "ejemplos": [f"Ahora: {cfg['continuo']}", f"Rutina: {cfg['frase']}"],
        },
        {
            "numero": 4,
            "titulo": "Rama 4 · Comparativos",
            "subtema": "Comparativos",
            "principal": cfg["comparativo"],
            "contraste": cfg["numeros"],
            "esquema": f"[Medium · Rama 4] -> [Comparativo: {cfg['comparativo']}]",
            "ejemplos": [f"Comparacion: {cfg['comparativo']}", f"Conteo: {cfg['numeros']}"],
        },
        {
            "numero": 5,
            "titulo": "Rama 5 · Verbos Modales y Deber",
            "subtema": "Verbos modales y deber",
            "principal": cfg["modal"],
            "contraste": cfg["listo"],
            "esquema": f"[Medium · Rama 5] -> [Modal: {cfg['modal']}]",
            "ejemplos": [f"Modal: {cfg['modal']}", f"Disposicion: {cfg['listo']}"],
        },
    ]

    plan_hard = [
        {
            "numero": 1,
            "titulo": "Rama 1 · Tiempos Perfectos",
            "subtema": "Tiempos perfectos",
            "principal": cfg["perfecto"],
            "contraste": cfg["pasado"],
            "esquema": f"[Hard · Rama 1] -> [Perfecto: {cfg['perfecto']}]",
            "ejemplos": [f"Perfecto: {cfg['perfecto']}", f"Pasado simple: {cfg['pasado']}"],
        },
        {
            "numero": 2,
            "titulo": "Rama 2 · Condicionales",
            "subtema": "Condicionales",
            "principal": cfg["condicional"],
            "contraste": cfg["futuro"],
            "esquema": f"[Hard · Rama 2] -> [Condicional: {cfg['condicional']}]",
            "ejemplos": [f"Condicional: {cfg['condicional']}", f"Futuro: {cfg['futuro']}"],
        },
        {
            "numero": 3,
            "titulo": "Rama 3 · Voz Pasiva",
            "subtema": "Voz pasiva",
            "principal": cfg["pasiva"],
            "contraste": cfg["frase"],
            "esquema": f"[Hard · Rama 3] -> [Pasiva: {cfg['pasiva']}]",
            "ejemplos": [f"Pasiva: {cfg['pasiva']}", f"Activa: {cfg['frase']}"],
        },
    ]

    plan_expert = [
        {
            "numero": 1,
            "titulo": "Rama 1 · Expresiones Compuestas",
            "subtema": "Expresiones compuestas",
            "principal": cfg["compuesto"],
            "contraste": cfg["modal"],
            "esquema": f"[Expert/Nativo · Rama 1] -> [Compuesta: {cfg['compuesto']}]",
            "ejemplos": [f"Compuesta: {cfg['compuesto']}", f"Modal: {cfg['modal']}"],
        },
        {
            "numero": 2,
            "titulo": "Rama 2 · Modismos y Giros",
            "subtema": "Modismos y giros",
            "principal": cfg["modismo"],
            "contraste": cfg["comparativo"],
            "esquema": f"[Expert/Nativo · Rama 2] -> [Modismo: {cfg['modismo']}]",
            "ejemplos": [f"Modismo: {cfg['modismo']}", f"Comparativo: {cfg['comparativo']}"],
        },
        {
            "numero": 3,
            "titulo": "Rama 3 · Dominio Nativo Final",
            "subtema": "Dominio nativo final",
            "principal": cfg["nativo"],
            "contraste": cfg["condicional"],
            "esquema": f"[Expert/Nativo · Rama 3] -> [Nativo: {cfg['nativo']}]",
            "ejemplos": [f"Nativo: {cfg['nativo']}", f"Condicional: {cfg['condicional']}"],
        },
    ]

    niveles_crudos = {
        "Easy": plan_easy,
        "Medium": plan_medium,
        "Hard": plan_hard,
        "Expert/Nativo": plan_expert,
    }

    niveles_compilados = {}
    for nivel_nom, ramas_lista in niveles_crudos.items():
        ramas_procesadas = []
        for r in ramas_lista:
            ramas_procesadas.append({
                "numero": r["numero"],
                "titulo": r["titulo"],
                "subtema": r["subtema"],
                "clases": construir_cinco_clases(nombre, nivel_nom, r["subtema"], r["principal"], r["contraste"]),
                "esquema": r["esquema"],
                "ejemplos": r["ejemplos"],
                "eval": construir_preguntas_examen(nombre, r["subtema"], r["principal"], r["contraste"]),
            })
        niveles_compilados[nivel_nom] = ramas_procesadas

    juegos_adaptados = [
        {"n": 1, "t": "Saludo", "r": f"Elige el saludo en {nombre}:", "ops": [cfg["saludo"], cfg["gracias"], cfg["numeros"]], "ok": cfg["saludo"]},
        {"n": 2, "t": "Gracias", "r": f"Elige como agradecer en {nombre}:", "ops": [cfg["gracias"], cfg["saludo"], cfg["manana"]], "ok": cfg["gracias"]},
        {"n": 3, "t": "Numeros", "r": f"Selecciona los numeros en {nombre}:", "ops": [cfg["numeros"], cfg["saludo"], cfg["pasado"]], "ok": cfg["numeros"]},
        {"n": 4, "t": "Manana", "r": f"Elige el saludo de manana en {nombre}:", "ops": [cfg["manana"], cfg["gracias"], cfg["futuro"]], "ok": cfg["manana"]},
        {"n": 5, "t": "Listo", "r": f"Elige como indicar que estas listo en {nombre}:", "ops": [cfg["listo"], cfg["modismo"], cfg["manana"]], "ok": cfg["listo"]},
        {"n": 6, "t": "Identidad", "r": f"Elige la frase de identidad en {nombre}:", "ops": [cfg["identidad"], cfg["gracias"], cfg["pasiva"]], "ok": cfg["identidad"]},
        {"n": 7, "t": "Frase Diaria", "r": f"Selecciona la frase diaria en {nombre}:", "ops": [cfg["frase"], cfg["numeros"], cfg["saludo"]], "ok": cfg["frase"]},
        {"n": 8, "t": "Futuro", "r": f"Elige la expresion de futuro en {nombre}:", "ops": [cfg["futuro"], cfg["pasado"], cfg["saludo"]], "ok": cfg["futuro"]},
        {"n": 9, "t": "Condicional", "r": f"Selecciona la estructura condicional en {nombre}:", "ops": [cfg["condicional"], cfg["gracias"], cfg["numeros"]], "ok": cfg["condicional"]},
        {"n": 10, "t": "Nativo", "r": f"Elige la expresion nativa en {nombre}:", "ops": [cfg["nativo"], cfg["manana"], cfg["identidad"]], "ok": cfg["nativo"]},
    ]

    return {
        "nombre": nombre,
        "codigo": cfg["codigo"],
        "saludo": cfg["saludo"],
        "frase": cfg["frase"],
        "numeros": cfg["numeros"],
        "vocab_extra": cfg["vocab_extra"],
        "niveles": niveles_compilados,
        "juegos": juegos_adaptados,
    }

BASE_CURSOS = {item["nombre"]: compilar_idioma(item) for item in IDIOMAS_CONFIG}

def responder_consulta_idioma(idioma, pregunta, modo="profesor"):
    curso = BASE_CURSOS.get(idioma) or BASE_CURSOS["Inglés"]
    texto = (pregunta or "").strip()
    modo_ok = "buscador" if (modo or "").strip().lower() == "buscador" else "profesor"

    if not texto:
        return f"[{idioma} · {modo_ok.upper()}] Escribe una pregunta o palabra sobre {idioma}."

    if CLAVE_GEMINI:
        instruccion = (
            f"Actua como profesor experto de {idioma}. Responde de manera clara, estructurada y directa sobre: {texto}"
            if modo_ok == "profesor"
            else f"Actua como buscador de {idioma}. Explica '{texto}' con su uso y un ejemplo real en {idioma}."
        )
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO_GEMINI}:generateContent?key={CLAVE_GEMINI}"
        cuerpo = json.dumps({
            "contents": [{"parts": [{"text": instruccion}]}]
        }).encode("utf-8")
        peticion = urllib.request.Request(
            url,
            data=cuerpo,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(peticion, timeout=10) as respuesta_http:
                datos = json.loads(respuesta_http.read().decode("utf-8"))
                partes = datos.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                if partes and partes[0].get("text"):
                    return partes[0]["text"].strip()
        except Exception:
            pass

    clave_buscada = texto.lower()
    for esp, trad in curso.get("vocab_extra", {}).items():
        if esp in clave_buscada or clave_buscada in esp:
            return (
                f"[{modo_ok.upper()} · {idioma.upper()}]\n"
                f"Coincidencia directa: '{esp}' -> '{trad}'\n"
                f"Ejemplo en contexto: '{curso['frase']}'."
            )

    texto_limpio = re.sub(r"\s+", " ", texto)
    if modo_ok == "buscador":
        return (
            f"[BUSCADOR · {idioma.upper()}]\n"
            f"Consulta: {texto_limpio}\n"
            f"Base del idioma -> Saludo: '{curso['saludo']}' | Numeros: '{curso['numeros']}' | Frase: '{curso['frase']}'."
        )
    return (
        f"[PROFESOR · {idioma.upper()}]\n"
        f"Duda: {texto_limpio}\n"
        f"Explicacion: En {idioma}, trabaja esta idea apoyandote en estructuras reales como '{curso['frase']}' y avanza rama por rama."
    )

HTML_PAGINA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>C-PRE "LENGUAJES"</title>
<style>
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #09090b; color: #f4f4f5; font-family: system-ui, -apple-system, Arial, sans-serif; }
header { display: flex; justify-content: space-between; align-items: center; padding: 12px 14px; background: #000000; border-bottom: 1px solid #27272a; position: sticky; top: 0; z-index: 25; }
.brand-title { font-size: 14px; font-weight: 800; letter-spacing: 0.6px; color: #ffffff; }
select { background: #18181b; color: #ffffff; border: 1px solid #52525b; padding: 7px 10px; font-size: 13px; font-weight: 700; max-width: 56%; }
.main-wrap { max-width: 760px; margin: 0 auto; padding: 14px 14px 58px; }
.card { background: #111114; border: 1px solid #27272a; padding: 14px; margin-bottom: 14px; }
.card-meta { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 8px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: #a1a1aa; border-bottom: 1px solid #27272a; padding-bottom: 8px; margin-bottom: 10px; }
.panel-nota { background: #09090b; border-left: 3px solid #ffffff; padding: 10px 12px; margin: 8px 0; font-size: 13.5px; line-height: 1.45; white-space: pre-line; color: #e4e4e7; }
.clase-card { background: #18181b; border: 1px solid #27272a; padding: 9px 11px; margin: 6px 0; font-size: 13.5px; line-height: 1.42; color: #f4f4f5; }
h2 { margin: 0 0 8px; font-size: 17px; font-weight: 800; text-transform: uppercase; color: #ffffff; }
h3 { margin: 0 0 8px; font-size: 15px; font-weight: 800; text-transform: uppercase; color: #ffffff; }
p { margin: 8px 0; font-size: 14px; line-height: 1.45; color: #d4d4d8; }
button { width: 100%; padding: 11px 12px; background: #ffffff; color: #09090b; border: 1px solid #ffffff; font-size: 14px; font-weight: 700; cursor: pointer; margin-top: 8px; }
button.sec { background: #18181b; color: #f4f4f5; border: 1px solid #52525b; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
input[type="text"] { width: 100%; padding: 11px 12px; background: #09090b; color: #ffffff; border: 1px solid #71717a; font-size: 15px; margin-bottom: 8px; }
.examen-hoja { background: #18181b; border: 2px solid #ffffff; padding: 14px; margin-top: 10px; }
.barra-fondo { width: 100%; height: 14px; background: #27272a; border: 1px solid #52525b; margin: 8px 0; }
.barra-relleno { height: 100%; background: #ffffff; width: 0%; }
.banner-progreso { background: #18181b; border: 1px solid #ffffff; padding: 12px; margin-bottom: 14px; font-size: 13.5px; font-weight: 700; color: #ffffff; }
.modal-screen { position: fixed; inset: 0; background: #09090b; z-index: 100; display: flex; flex-direction: column; justify-content: flex-start; align-items: center; padding: 36px 20px 24px; text-align: center; overflow-y: auto; }
.hidden-view { display: none !important; }
.bienvenida-caja { font-size: 24px; font-weight: 900; text-transform: uppercase; border-top: 2px solid #ffffff; border-bottom: 2px solid #ffffff; padding: 14px 10px; margin-bottom: 10px; color: #ffffff; }
.creacion-sub { font-size: 14px; font-weight: 600; color: #d4d4d8; letter-spacing: 0.8px; margin-bottom: 16px; }
.dueno-corner { position: fixed; right: 12px; bottom: 8px; font-size: 11px; font-weight: 800; letter-spacing: 1.5px; text-transform: uppercase; color: #a1a1aa; background: #09090b; padding: 2px 6px; z-index: 35; }
</style>
</head>
<body>

<div id="viewBienvenida" class="modal-screen">
    <div class="bienvenida-caja">BIENVENIDO A C-PRE "LENGUAJES"</div>
    <div class="creacion-sub">Creaciones de Celso</div>
    <div id="lblCuenta" style="font-size:13px;color:#a1a1aa">Entrando...</div>
    <button type="button" onclick="saltarBienvenidaYAbrir()" style="max-width:300px;margin-top:14px">ENTRAR AHORA</button>
</div>

<div id="viewDecisionEasy" class="modal-screen hidden-view">
    <div class="card" style="max-width:460px;width:100%">
        <h3>INICIO DE NIVEL</h3>
        <p style="font-weight:700;color:#ffffff">¿Quieres saltarte el modo Easy? Para saltártelo tienes que presentar la evaluación. Si pasas la evaluación puedes pasar al nivel Medium.</p>
        <button type="button" onclick="elegirSaltarEasy()">SALTAR MODO EASY (PRESENTAR EVALUACIÓN)</button>
        <button type="button" class="sec" onclick="elegirModoEasyNormal()">EMPEZAR EN MODO EASY</button>
    </div>
</div>

<header>
    <span class="brand-title">C-PRE "LENGUAJES"</span>
    <select id="selectIdioma" onchange="alCambiarIdioma()"></select>
</header>

<main class="main-wrap">
    <div id="bannerFelicitacion" class="banner-progreso hidden-view"></div>

    <section class="card">
        <div class="card-meta">
            <span>NIVEL: <strong id="metaNivel" style="color:#ffffff">Easy</strong></span>
            <span>RAMA: <strong id="metaRama" style="color:#ffffff">1/7</strong></span>
            <span>NOTA: <strong id="metaNota" style="color:#ffffff">0/20</strong></span>
        </div>
        <h2 id="tituloRamaActual"></h2>
        <p id="subtemaRamaActual"></p>
        <div id="contenedorClases"></div>
        <div id="esquemaRamaActual" class="panel-nota"></div>
        <div id="ejemplosRamaActual" class="panel-nota"></div>

        <div id="panelPreparacion" class="panel-nota">
            <strong>¿Estás preparado para la evaluación?</strong>
            <button type="button" onclick="iniciarExamen(false)">SÍ, PRESENTAR EVALUACIÓN (20 PTS)</button>
        </div>
        <div id="panelExamen" class="hidden-view"></div>
    </section>

    <section class="card">
        <div class="card-meta">
            <span>NOTICIAS · TÁCTICAS · TRUCOS DIARIOS</span>
            <span id="metaDia"></span>
        </div>
        <div id="boxNoticia" class="panel-nota"></div>
        <div id="boxTactica" class="panel-nota"></div>
        <div id="boxTruco" class="panel-nota"></div>
    </section>

    <section class="card">
        <div class="card-meta">
            <span>10 JUEGOS ADAPTADOS</span>
            <span id="metaJuegoPts">PTS: 0</span>
        </div>
        <h3 id="tituloJuegoActual"></h3>
        <p id="enunciadoJuegoActual" style="font-weight:700;color:#ffffff"></p>
        <div id="opcionesJuegoActual" class="grid-2"></div>
        <div id="feedbackJuegoActual" class="panel-nota">Elige una opción para jugar.</div>
    </section>

    <section class="card">
        <div class="card-meta">
            <span>BUSCADOR Y PREGUNTAS LIBRES</span>
            <span id="metaModoConsulta">MODO: PROFESOR</span>
        </div>
        <input type="text" id="inputPreguntaLibre" placeholder="Pregunta o busca lo que quieras del idioma actual...">
        <div class="grid-2">
            <button type="button" onclick="enviarConsultaLibre('profesor')">PREGUNTAR</button>
            <button type="button" class="sec" onclick="enviarConsultaLibre('buscador')">BUSCAR</button>
        </div>
        <div id="respuestaConsultaLibre" class="panel-nota">Escribe tu consulta sobre el idioma seleccionado.</div>
    </section>
</main>

<div class="dueno-corner">DUEÑO CELSO</div>

<script id="datosCursosJson" type="application/json">__CURSOS_JSON__</script>
<script id="datosNoticiasJson" type="application/json">__NOTICIAS_JSON__</script>
<script id="datosTacticasJson" type="application/json">__TACTICAS_JSON__</script>
<script id="datosTrucosJson" type="application/json">__TRUCOS_JSON__</script>
<script id="datosNivelesJson" type="application/json">__NIVELES_JSON__</script>
<script id="datosOrdinalesJson" type="application/json">__ORDINALES_JSON__</script>

<script>
function leerJsonSeguro(idElemento, respaldo) {
    try {
        var el = document.getElementById(idElemento);
        if (!el || !el.textContent || el.textContent.indexOf("__") === 0) return respaldo;
        return JSON.parse(el.textContent);
    } catch (e) {
        return respaldo;
    }
}

var CURSOS = leerJsonSeguro("datosCursosJson", {});
var NOTICIAS = leerJsonSeguro("datosNoticiasJson", []);
var TACTICAS = leerJsonSeguro("datosTacticasJson", []);
var TRUCOS = leerJsonSeguro("datosTrucosJson", []);
var NIVELES = leerJsonSeguro("datosNivelesJson", ["Easy", "Medium", "Hard", "Expert/Nativo"]);
var ORDINALES = leerJsonSeguro("datosOrdinalesJson", {"1":"primera","2":"segunda","3":"tercera","4":"cuarta","5":"quinta","6":"sexta","7":"septima"});

var estado = {
    idioma: Object.keys(CURSOS).length ? Object.keys(CURSOS)[0] : "Inglés",
    nivelIdx: 0,
    ramaIdx: 0,
    juegoIdx: 0,
    puntosJuego: 0,
    ultimaNota: 0
};

var timerBienvenida = null;

function saltarBienvenidaYAbrir() {
    if (timerBienvenida) {
        clearInterval(timerBienvenida);
        timerBienvenida = null;
    }
    var bienvenida = document.getElementById("viewBienvenida");
    var decision = document.getElementById("viewDecisionEasy");
    if (bienvenida) bienvenida.classList.add("hidden-view");
    if (decision) decision.classList.remove("hidden-view");
}

function iniciarBienvenidaDirecta() {
    var bienvenida = document.getElementById("viewBienvenida");
    var lbl = document.getElementById("lblCuenta");
    if (!bienvenida) return;
    var seg = 2;
    if (lbl) lbl.textContent = "Entrando... " + seg + "s";

    timerBienvenida = setInterval(function() {
        seg -= 1;
        if (seg > 0) {
            if (lbl) lbl.textContent = "Entrando... " + seg + "s";
        } else {
            saltarBienvenidaYAbrir();
        }
    }, 1000);
}

function cargarSelectorIdiomas() {
    var sel = document.getElementById("selectIdioma");
    if (!sel) return;
    sel.innerHTML = "";
    var nombres = Object.keys(CURSOS);
    if (!nombres.length) {
        var optDef = document.createElement("option");
        optDef.value = "Inglés";
        optDef.
