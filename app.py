import os
import json
import re
import urllib.request
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

CODIGO_ACCESO = os.environ.get("C_PRE_CODIGO", "CPRE2026")
PUERTO_APP = int(os.environ.get("PORT", 5000))
HOST_APP = os.environ.get("HOST", "0.0.0.0")
MODELO_IA = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
API_KEY_IA = os.environ.get("GEMINI_API_KEY", "").strip()

ORDEN_NIVELES = [
    "Easy",
    "Medium",
    "Hard",
    "Expert/Nativo",
]

NOMBRES_RAMA_ORDINAL = {
    1: "primera",
    2: "segunda",
    3: "tercera",
    4: "cuarta",
    5: "quinta",
    6: "sexta",
    7: "séptima",
}

CATALOGO_IDIOMAS = [
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
        "condicional": "Se eu praticar, eu melho",
        "pasiva": "O português é falado no Brasil",
        "compuesto": "Manter o ritmo de estudo",
        "modismo": "Moleza",
        "nativo": "Pego o jeito rapidinho",
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
    },
    {
        "nombre": "Chino Mandarín",
        "codigo": "zh",
        "saludo": "你好 (Nǐ hǎo)",
        "listo": "我准备好了 (Wǒ zhǔnbèi hǎo le)",
        "manana": "早上好 (Zǎoshang hǎo)",
        "gracias": "谢谢 (Xièxie)",
        "frase": "我每天说中文 (Wǒ měitiān shuō zhōngwén)",
        "numeros": "一, 二, 三, 四, 五 (yī, èr, sān, sì, wǔ)",
        "identidad": "我是学生 (Wǒ shì xuésheng)",
        "pasado": "昨天我练习了中文 (Zuótiān wǒ liànxí le zhōngwén)",
        "futuro": "我明天要学习 (Wǒ míngtiān yào xuéxí)",
        "continuo": "我正在学习 (Wǒ zhèngzài xuéxí)",
        "comparativo": "练习比死记更好 (Liànxí bǐ sǐjì gèng hǎo)",
        "modal": "你应该每天练习 (Nǐ yīnggāi měitiān liànxí)",
        "perfecto": "我学过中文 (Wǒ xuéguò zhōngwén)",
        "condicional": "如果我练习就会进步 (Rúguǒ wǒ liànxí jiù huì jìnbù)",
        "pasiva": "中文被广泛使用 (Zhōngwén bèi guǎngfàn shǐyòng)",
        "compuesto": "坚持每天练习 (Jiānchí měitiān liànxí)",
        "modismo": "小菜一碟 (Xiǎo cài yī dié)",
        "nativo": "我很快就能掌握窍门 (Wǒ hěn kuài jiù néng zhǎngwò qiàomén)",
    },
    {
        "nombre": "Japonés",
        "codigo": "ja",
        "saludo": "こんにちは (Konnichiwa)",
        "listo": "じゅんびできました (Junbi dekimashita)",
        "manana": "おはようございます (Ohayō gozaimasu)",
        "gracias": "ありがとう (Arigatō)",
        "frase": "まいにちにほんごをれんしゅうします (Mainichi nihongo o renshū shimasu)",
        "numeros": "いち、に、さん、し、ご (ichi, ni, san, shi, go)",
        "identidad": "わたしはがくせいです (Watashi wa gakusei desu)",
        "pasado": "きのうにほんごをれんしゅうしました (Kinō nihongo o renshū shimashita)",
        "futuro": "あしたべんきょうします (Ashita benkyō shimasu)",
        "continuo": "いまべんきょうしています (Ima benkyō shite imasu)",
        "comparativo": "れんしゅうはあんきよりいいです (Renshū wa anki yori ii desu)",
        "modal": "まいにちれんしゅうすべきです (Mainichi renshū subeki desu)",
        "perfecto": "にほんごをべんきょうしたことがあります (Nihongo o benkyō shita koto ga arimasu)",
        "condicional": "れんしゅうすればじょうたつします (Renshū sureba jōtatsu shimasu)",
        "pasiva": "にほんごはにほんではなされます (Nihongo wa nihon de hanasaremasu)",
        "compuesto": "コツコツつづける (Kotsukotsu tsuzukeru)",
        "modismo": "おちゃのこさいさい (Ocha-no-ko saisai)",
        "nativo": "すぐこつをつかみます (Sugu kotsu o tsukamimasu)",
    },
    {
        "nombre": "Coreano",
        "codigo": "ko",
        "saludo": "안녕하세요 (Annyeonghaseyo)",
        "listo": "준비됐어요 (Junbi-dwaesseo-yo)",
        "manana": "좋은 아침 (Jo-eun achim)",
        "gracias": "감사합니다 (Gamsahamnida)",
        "frase": "매일 한국어를 연습해요 (Maeil han-gu-geo-reul yeon-seup-hae-yo)",
        "numeros": "하나, 둘, 셋, 넷, 다섯 (ha-na, dul, set, net, da-seot)",
        "identidad": "저는 학생이에요 (Jeo-neun hak-saeng-i-e-yo)",
        "pasado": "어제 한국어를 공부했어요 (Eo-je han-gu-geo-reul gong-bu-haet-seo-yo)",
        "futuro": "내일 공부할 거예요 (Nae-il gong-bu-hal geo-ye-yo)",
        "continuo": "지금 배우고 있어요 (Ji-geum bae-u-go is-seo-yo)",
        "comparativo": "연습이 암기보다 좋아요 (Yeon-seub-i am-gi-bo-da jo-a-yo)",
        "modal": "매일 연습해야 해요 (Maeil yeon-seub-hae-ya hae-yo)",
        "perfecto": "한국어를 공부해 봤어요 (Han-gu-geo-reul gong-bu-hae bwat-seo-yo)",
        "condicional": "연습하면 실력이 늘어요 (Yeon-seub-ha-myeon sil-ryeog-i neur-eo-yo)",
        "pasiva": "한국어는 한국에서 사용돼요 (Han-gu-geo-neun han-guk-e-seo sa-yong-dwae-yo)",
        "compuesto": "꾸준히 이어가기 (Kku-jun-hi i-eo-ga-gi)",
        "modismo": "식은 죽 먹기 (Sik-eun juk meok-gi)",
        "nativo": "요령을 금방 잡아요 (Yo-ryeong-eul geum-bang jab-a-yo)",
    },
    {
        "nombre": "Árabe",
        "codigo": "ar",
        "saludo": "مرحباً (Marhaban)",
        "listo": "أنا مستعد (Anā musta'idd)",
        "manana": "صباح الخير (Sabāh al-khayr)",
        "gracias": "شكراً (Shukran)",
        "frase": "أتدرب على العربية كل يوم (Atadarrab 'alā al-'arabiyyah kull yawm)",
        "numeros": "واحد، اثنان، ثلاثة، أربعة، خمسة (wāḥid, ithnān, thalāthah, arba'ah, khamsah)",
        "identidad": "أنا طالب (Anā ṭālib)",
        "pasado": "تدربت بالأمس على العربية (Tadarrabtu bil-ams 'alā al-'arabiyyah)",
        "futuro": "سأدرس غداً (Sa'adrusu ghadan)",
        "continuo": "أتعلم الآن (Ata'allam al-ān)",
        "comparativo": "التدريب أفضل من الحفظ (At-tadrīb afḍal min al-ḥifẓ)",
        "modal": "يجب أن تتدرب يومياً (Yajibu an tatadarraba yawmiyyan)",
        "perfecto": "لقد درست العربية (Laqad darastu al-'arabiyyah)",
        "condicional": "إذا تدربت فسأتقن (Idhā tadarrabtu fa-sa'utqin)",
        "pasiva": "تُستخدم العربية في بلدان كثيرة (Tustakhdam al-'arabiyyah fī buldān kathīrah)",
        "compuesto": "الاستمرار بثبات (Al-istimrār bi-thabāt)",
        "modismo": "أسهل من شربة ماء (Ashal min shurbat mā')",
        "nativo": "أفهم الفكرة بسرعة (Afham al-fikrah bi-sur'ah)",
    },
    {
        "nombre": "Ruso",
        "codigo": "ru",
        "saludo": "Привет (Privet)",
        "listo": "Я готов (Ya gotov)",
        "manana": "Доброе утро (Dóbroye útro)",
        "gracias": "Спасибо (Spasíbo)",
        "frase": "Я каждый день учу русский (Ya kázhdyy den' uchú rússkiy)",
        "numeros": "Один, два, три, четыре, пять (odín, dva, tri, chetýre, pyat')",
        "identidad": "Я студент (Ya studént)",
        "pasado": "Вчера я занимался русским (Vcherá ya zanimálsya rússkim)",
        "futuro": "Завтра я буду заниматься (Závtra ya búdu zanimát'sya)",
        "continuo": "Я сейчас учусь (Ya seychás uchús')",
        "comparativo": "Практика лучше зубрёжки (Práktika lúchshe zubryózhki)",
        "modal": "Нужно заниматься каждый день (Núzhno zanimát'sya kázhdyy den')",
        "perfecto": "Я уже учил русский (Ya uzhé uchíl rússkiy)",
        "condicional": "Если буду заниматься, улучшу (Yésli búdu zanimát'sya, ulúchshu)",
        "pasiva": "Русский язык изучают везде (Rússkiy yazýk izucháyut vezdé)",
        "compuesto": "Сохранять темп занятий (Sokhranyát' temp zanyátiy)",
        "modismo": "Проще простого (Próshche prostógo)",
        "nativo": "Быстро схватываю суть (Býstro skhvátývayu sut')",
    },
    {
        "nombre": "Hindi",
        "codigo": "hi",
        "saludo": "नमस्ते (Namaste)",
        "listo": "मैं तैयार हूँ (Main taiyaar hoon)",
        "manana": "सुप्रभात (Suprabhat)",
        "gracias": "धन्यवाद (Dhanyavaad)",
        "frase": "मैं रोज़ हिंदी का अभ्यास करता हूँ (Main roz Hindi ka abhyaas karta hoon)",
        "numeros": "एक, दो, तीन, चार, पाँच (ek, do, teen, chaar, paanch)",
        "identidad": "मैं छात्र हूँ (Main chhatra hoon)",
        "pasado": "कल मैंने हिंदी का अभ्यास किया (Kal maine Hindi ka abhyaas kiya)",
        "futuro": "मैं कल पढ़ाई करूँगा (Main kal padhaai karoonga)",
        "continuo": "मैं अभी सीख रहा हूँ (Main abhi seekh raha hoon)",
        "comparativo": "अभ्यास रटने से बेहतर है (Abhyaas ratne se behtar hai)",
        "modal": "तुम्हें रोज़ अभ्यास करना चाहिए (Tumhein roz abhyaas karna chahiye)",
        "perfecto": "मैंने हिंदी सीखी है (Maine Hindi seekhi hai)",
        "condicional": "अगर मैं अभ्यास करूँगा तो सुधार होगा (Agar main abhyaas karoonga to sudhaar hoga)",
        "pasiva": "हिंदी भारत में बोली जाती है (Hindi Bharat mein boli jaati hai)",
        "compuesto": "निरंतर अभ्यास बनाए रखना (Nirantar abhyaas banaaye rakhna)",
        "modismo": "बायें हाथ का खेल (Baayein haath ka khel)",
        "nativo": "मैं जल्दी तरीका समझ लेता हूँ (Main jaldi tareeqa samajh leta hoon)",
    },
    {
        "nombre": "Bengalí",
        "codigo": "bn",
        "saludo": "নমস্কার (Nomoshkar)",
        "listo": "আমি প্রস্তুত (Ami prostut)",
        "manana": "শুভ সকাল (Shubho shokal)",
        "gracias": "ধন্যবাদ (Dhonnobad)",
        "frase": "আমি প্রতিদিন বাংলা অনুশীলন করি (Ami protidin Bangla onushilon kori)",
        "numeros": "এক, দুই, তিন, চার, পাঁচ (ek, dui, tin, char, pach)",
        "identidad": "আমি ছাত্র (Ami chhatro)",
        "pasado": "গতকাল আমি বাংলা অনুশীলন করেছি (Gotokal ami Bangla onushilon korechi)",
        "futuro": "আমি আগামীকাল পড়ব (Ami agamikal porbo)",
        "continuo": "আমি এখন শিখছি (Ami ekhon shikhchi)",
        "comparativo": "অনুশীলন মুখস্থ করার চেয়ে ভালো (Onushilon mukhostho korar cheye bhalo)",
        "modal": "তোমার প্রতিদিন অনুশীলন করা উচিত (Tomar protidin onushilon kora uchit)",
        "perfecto": "আমি বাংলা শিখেছি (Ami Bangla shikhechi)",
        "condicional": "আমি অনুশীলন করলে উন্নতি করব (Ami onushilon korle unnoti korbo)",
        "pasiva": "বাংলা ভাষা ব্যাপকভাবে বলা হয় (Bangla bhasha byapokbhabe bola hoy)",
        "compuesto": "নিয়মিত অনুশীলন বজায় রাখা (Niyomito onushilon bojay rakha)",
        "modismo": "বাম হাতের খেল (Bam hater khel)",
        "nativo": "আমি দ্রুত কৌশল ধরে ফেলি (Ami druto koushol dhore feli)",
    },
    {
        "nombre": "Turco",
        "codigo": "tr",
        "saludo": "Merhaba",
        "listo": "Hazırım",
        "manana": "Günaydın",
        "gracias": "Teşekkürler",
        "frase": "Her gün Türkçe pratik yapıyorum",
        "numeros": "Bir, iki, üç, dört, beş",
        "identidad": "Ben öğrenciyim",
        "pasado": "Dün Türkçe çalıştım",
        "futuro": "Yarın çalışacağım",
        "continuo": "Şu an öğreniyorum",
        "comparativo": "Pratik yapmak ezberlemekten iyidir",
        "modal": "Her gün pratik yapmalısın",
        "perfecto": "Türkçe öğrendim",
        "condicional": "Pratik yaparsam gelişirim",
        "pasiva": "Türkçe Türkiye'de konuşulur",
        "compuesto": "Düzenli çalışmayı sürdürmek",
        "modismo": "Çocuk oyuncağı",
        "nativo": "İşin mantığını çabuk kaparım",
    },
    {
        "nombre": "Neerlandés",
        "codigo": "nl",
        "saludo": "Hallo",
        "listo": "Ik ben klaar",
        "manana": "Goedemorgen",
        "gracias": "Dank je",
        "frase": "Ik oefen elke dag Nederlands",
        "numeros": "Een, twee, drie, vier, vijf",
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
    },
    {
        "nombre": "Polaco",
        "codigo": "pl",
        "saludo": "Cześć",
        "listo": "Jestem gotowy",
        "manana": "Dzień dobry",
        "gracias": "Dziękuję",
        "frase": "Codziennie ćwiczę polski",
        "numeros": "Jeden, dwa, trzy, cztery, pięć",
        "identidad": "Jestem studentem",
        "pasado": "Wczoraj ćwiczyłem polski",
        "futuro": "Będę się uczyć jutro",
        "continuo": "Teraz się uczę",
        "comparativo": "Ćwiczenie jest lepsze niż wkuwanie",
        "modal": "Powinieneś ćwiczyć codziennie",
        "perfecto": "Uczyłem się polskiego",
        "condicional": "Jeśli będę ćwiczyć, zrobię postęp",
        "pasiva": "Po polsku mówi się w Polsce",
        "compuesto": "Utrzymać stałe tempo",
        "modismo": "Bułka z masłem",
        "nativo": "Szybko łapię sedno",
    },
    {
        "nombre": "Sueco",
        "codigo": "sv",
        "saludo": "Hej",
        "listo": "Jag är redo",
        "manana": "God morgon",
        "gracias": "Tack",
        "frase": "Jag övar svenska varje dag",
        "numeros": "Ett, två, tre, fyra, fem",
        "identidad": "Jag är student",
        "pasado": "Igår övade jag svenska",
        "futuro": "Jag ska plugga imorgon",
        "continuo": "Jag lär mig just nu",
        "comparativo": "Att öva är bättre än att rabbla",
        "modal": "Du bör öva varje dag",
        "perfecto": "Jag har studerat svenska",
        "condicional": "Om jag övar så blir jag bättre",
        "pasiva": "Svenska talas i Sverige",
        "compuesto": "Hålla jämnt tempo",
        "modismo": "En barnlek",
        "nativo": "Jag får kläm på det snabbt",
    },
    {
        "nombre": "Griego",
        "codigo": "el",
        "saludo": "Γεια σου (Geia sou)",
        "listo": "Είμαι έτοιμος (Eímai étoimos)",
        "manana": "Καλημέρα (Kaliméra)",
        "gracias": "Ευχαριστώ (Efcharistó)",
        "frase": "Εξασκούμαι στα ελληνικά κάθε μέρα (Exaskoúmai sta elliniká káthe méra)",
        "numeros": "Ένα, δύο, τρία, τέσσερα, πέντε (éna, dýo, tría, téssera, pénte)",
        "identidad": "Είμαι φοιτητής (Eímai foititís)",
        "pasado": "Χθες εξασκήθηκα στα ελληνικά (Chthés exaskíthika sta elliniká)",
        "futuro": "Θα διαβάσω αύριο (Tha diaváso ávrio)",
        "continuo": "Μαθαίνω τώρα (Mathaíno tóra)",
        "comparativo": "Η εξάσκηση είναι καλύτερη από την αποστήθιση (I exáskisi eínai kalýteri apó tin apostíthisi)",
        "modal": "Πρέπει να εξασκείσαι καθημερινά (Prépei na exaskeíse kathimeriná)",
        "perfecto": "Έχω σπουδάσει ελληνικά (Écho spoudásei elliniká)",
        "condicional": "Αν εξασκηθώ, θα βελτιωθώ (An exaskithó, tha veltiotthó)",
        "pasiva": "Τα ελληνικά μιλιούνται στην Ελλάδα (Ta elliniká milioúnte stin Elláda)",
        "compuesto": "Διατήρηση σταθερού ρυθμού (Diatírisi statheroú rythmoú)",
        "modismo": "Παιχνιδάκι (Paichnidáki)",
        "nativo": "Πιάνω γρήγορα το νόημα (Piáno grígora to nóima)",
    },
    {
        "nombre": "Vietnamita",
        "codigo": "vi",
        "saludo": "Xin chào",
        "listo": "Tôi đã sẵn sàng",
        "manana": "Chào buổi sáng",
        "gracias": "Cảm ơn",
        "frase": "Tôi luyện tiếng Việt mỗi ngày",
        "numeros": "Một, hai, ba, bốn, năm",
        "identidad": "Tôi là sinh viên",
        "pasado": "Hôm qua tôi đã luyện tiếng Việt",
        "futuro": "Ngày mai tôi sẽ học",
        "continuo": "Tôi đang học ngay bây giờ",
        "comparativo": "Luyện tập tốt hơn học vẹt",
        "modal": "Bạn nên luyện tập mỗi ngày",
        "perfecto": "Tôi đã học tiếng Việt",
        "condicional": "Nếu tôi luyện tập, tôi sẽ tiến bộ",
        "pasiva": "Tiếng Việt được nói ở Việt Nam",
        "compuesto": "Duy trì nhịp độ đều đặn",
        "modismo": "Dễ như ăn kẹo",
        "nativo": "Tôi nắm bắt cách làm rất nhanh",
    },
    {
        "nombre": "Persa",
        "codigo": "fa",
        "saludo": "سلام (Salām)",
        "listo": "آماده‌ام (Āmādeh-am)",
        "manana": "صبح بخیر (Sobh be-kheyr)",
        "gracias": "ممنون (Mamnoon)",
        "frase": "هر روز فارسی تمرین می‌کنم (Har rooz Fārsi tamrīn mikonam)",
        "numeros": "یک، دو، سه، چهار، پنج (yek, do, seh, chahār, panj)",
        "identidad": "من دانشجو هستم (Man dāneshjoo hastam)",
        "pasado": "دیروز فارسی تمرین کردم (Dīrooz Fārsi tamrīn kardam)",
        "futuro": "فردا درس می‌خوانم (Fardā dars mikhānam)",
        "continuo": "الان در حال یادگیری هستم (Alān dar hāl-e yādgīrī hastam)",
        "comparativo": "تمرین کردن بهتر از حفظ کردن است (Tamrīn kardan behtar az hefz kardan ast)",
        "modal": "باید هر روز تمرین کنی (Bāyad har rooz tamrīn konī)",
        "perfecto": "فارسی خوانده‌ام (Fārsi khāndeh-am)",
        "condicional": "اگر تمرین کنم پیشرفت می‌کنم (Agar tamrīn konam pīshraft mikonam)",
        "pasiva": "فارسی در ایران صحبت می‌شود (Fārsi dar Īrān sohbat mīshavad)",
        "compuesto": "حفظ پیوستگی در مطالعه (Hefz-e peyvastegī dar motāle'eh)",
        "modismo": "مثل آب خوردن (Mesl-e āb khordan)",
        "nativo": "زود قلق کار دستم می‌آید (Zood qoloq-e kār dastam mīāyad)",
    },
]

NOTICIAS_DIARIAS = [
    "Noticia diaria (Inglés): Daily reading of short headlines helps you recognize real English vocabulary faster.",
    "Noticia diaria (Inglés): Listening to short native clips and repeating aloud builds clear pronunciation naturally.",
    "Noticia diaria (Inglés): Writing three sentences every day about your routine reinforces core verb structures.",
    "Noticia diaria (Inglés): Grouping expressions by real situations makes recall easier than isolated lists.",
    "Noticia diaria (Inglés): Reviewing missed exam items turns mistakes into solid rules for next time.",
    "Noticia diaria (Inglés): Speaking simple ideas out loud early prevents freezing when a conversation starts.",
    "Noticia diaria (Inglés): Consistent 15-minute sessions beat long irregular cramming sessions.",
]

TACTICAS_DIARIAS = [
    "Táctica del día: Trabaja una rama a la vez y domina su idea central antes de ir a la evaluación.",
    "Táctica del día: Si vas a intentar saltar Easy, revisa bien la estructura base para superar los 10/20.",
    "Táctica del día: Compara la expresión correcta con las distractores en cada pregunta de la hoja de examen.",
    "Táctica del día: Aplica los números y frases de la rama en ejemplos tuyos antes de cerrar la sesión.",
    "Táctica del día: Revisa qué pregunta te quitó puntos cuando tu nota sea menor a 20/20.",
    "Táctica del día: Cambia de idioma en el selector superior para ver cómo se adapta todo el sistema.",
    "Táctica del día: Combina las ramas con los 10 juegos para fijar reflejo y comprensión.",
]

TRUCOS_DIARIOS = [
    "Truco del día: Conecta cada palabra nueva con una situación real en vez de traducir palabra por palabra.",
    "Truco del día: Al escribir en la hoja de examen, revisa mayúsculas, ortografía y claridad de la respuesta.",
    "Truco del día: En las preguntas de Verdadero o Falso, lee si la afirmación coincide con el tema de la rama.",
    "Truco del día: Usa el modo Profesor para explicaciones y el modo Buscador para consultar términos puntuales.",
    "Truco del día: Repasa los números en la Rama 3 de Easy para ganar seguridad al contar.",
    "Truco del día: Si repruebas con menos de 10/20, vuelve a leer las 5 clases de la rama antes de reintentar.",
    "Truco del día: Mantén la constancia diaria para subir de Easy a Medium, Hard y Expert/Nativo.",
]

def construir_hoja_20_puntos(idioma, tema, ejemplo_principal, ejemplo_contraste):
    return [
        {
            "numero": 1,
            "tipo": "verdadero_falso",
            "puntos": 4,
            "enunciado": f"Verdadero o Falso: En {idioma}, '{ejemplo_principal}' corresponde al tema '{tema}'.",
            "opciones": ["Verdadero", "Falso"],
            "correcta": "Verdadero",
            "explicacion": f"Correcto: '{ejemplo_principal}' está directamente vinculado con {tema} en {idioma}.",
        },
        {
            "numero": 2,
            "tipo": "completar",
            "puntos": 4,
            "enunciado": f"Completa la expresión para '{tema}' en {idioma}: [ __________ ]",
            "opciones": [ejemplo_principal, ejemplo_contraste],
            "correcta": ejemplo_principal,
            "explicacion": f"La expresión que completa este bloque es '{ejemplo_principal}'.",
        },
        {
            "numero": 3,
            "tipo": "identificar",
            "puntos": 4,
            "enunciado": f"Identifica la opción adecuada para '{tema}' en {idioma}:",
            "opciones": [ejemplo_principal, ejemplo_contraste, "Ninguna opción coincide"],
            "correcta": ejemplo_principal,
            "explicacion": f"'{ejemplo_principal}' es la forma que identifica este tema en {idioma}.",
        },
        {
            "numero": 4,
            "tipo": "escribir",
            "puntos": 4,
            "enunciado": f"Escribe la expresión clave de '{tema}' en {idioma}:",
            "aceptadas": [
                ejemplo_principal.lower(),
                ejemplo_principal.lower().split("(")[0].strip(),
            ],
            "muestra": ejemplo_principal,
            "explicacion": f"Respuesta esperada para esta pregunta: {ejemplo_principal}.",
        },
        {
            "numero": 5,
            "tipo": "verdadero_falso",
            "puntos": 4,
            "enunciado": f"Verdadero o Falso: '{ejemplo_contraste}' tiene exactamente el mismo uso que '{ejemplo_principal}'.",
            "opciones": ["Verdadero", "Falso"],
            "correcta": "Falso",
            "explicacion": f"'{ejemplo_principal}' y '{ejemplo_contraste}' representan usos o contrastes distintos en {idioma}.",
        },
    ]

def construir_clases_rama(idioma, subtema, principal, contraste, nivel_nombre):
    return [
        f"Clase 1 ({nivel_nombre} · {subtema}): Observa la estructura principal '{principal}' en {idioma} y su propósito.",
        f"Clase 2 (Análisis de forma): Compara '{principal}' frente a '{contraste}' para no confundirlos.",
        f"Clase 3 (Uso práctico): Piensa en cuándo usar '{principal}' dentro de una conversación real en {idioma}.",
        f"Clase 4 (Precisión y errores): Evita mezclar '{principal}' con temas ajenos a '{subtema}'.",
        f"Clase 5 (Preparación para evaluación): Verifica que domines '{principal}' antes de presentar la hoja de 20 puntos.",
    ]

def construir_curso_completo(entry):
    nombre = entry["nombre"]
    easy_ramas = [
        {
            "numero": 1,
            "titulo": "Rama 1 · Verbo Ser e Identidad",
            "subtema": "Verbo ser e identidad",
            "principal": entry["identidad"],
            "contraste": entry["saludo"],
            "esquema": f"[Easy · Rama 1] -> [Identidad: {entry['identidad']}]",
            "ejemplos": [
                f"Identidad base: {entry['identidad']}",
                f"Contraste inicial: {entry['saludo']}",
            ],
        },
        {
            "numero": 2,
            "titulo": "Rama 2 · Saludos y Cortesía",
            "subtema": "Saludos y cortesía",
            "principal": entry["saludo"],
            "contraste": entry["gracias"],
            "esquema": f"[Easy · Rama 2] -> [Saludo: {entry['saludo']}] -> [Cortesía: {entry['gracias']}]",
            "ejemplos": [
                f"Saludo: {entry['saludo']}",
                f"Cortesía: {entry['gracias']}",
            ],
        },
        {
            "numero": 3,
            "titulo": "Rama 3 · Números",
            "subtema": "Números",
            "principal": entry["numeros"],
            "contraste": entry["identidad"],
            "esquema": f"[Easy · Rama 3] -> [Números: {entry['numeros']}]",
            "ejemplos": [
                f"Números: {entry['numeros']}",
                f"En contexto de identidad: {entry['identidad']}",
            ],
        },
        {
            "numero": 4,
            "titulo": "Rama 4 · Momentos de la Mañana",
            "subtema": "Momentos de la mañana",
            "principal": entry["manana"],
            "contraste": entry["saludo"],
            "esquema": f"[Easy · Rama 4] -> [Mañana: {entry['manana']}]",
            "ejemplos": [
                f"Mañana: {entry['manana']}",
                f"Saludo general: {entry['saludo']}",
            ],
        },
        {
            "numero": 5,
            "titulo": "Rama 5 · Agradecimiento",
            "subtema": "Agradecimiento",
            "principal": entry["gracias"],
            "contraste": entry["listo"],
            "esquema": f"[Easy · Rama 5] -> [Agradecimiento: {entry['gracias']}]",
            "ejemplos": [
                f"Agradecimiento: {entry['gracias']}",
                f"Disponibilidad: {entry['listo']}",
            ],
        },
        {
            "numero": 6,
            "titulo": "Rama 6 · Estar Listo y Disposición",
            "subtema": "Estar listo y disposición",
            "principal": entry["listo"],
            "contraste": entry["frase"],
            "esquema": f"[Easy · Rama 6] -> [Listo: {entry['listo']}]",
            "ejemplos": [
                f"Listo: {entry['listo']}",
                f"Práctica diaria: {entry['frase']}",
            ],
        },
        {
            "numero": 7,
            "titulo": "Rama 7 · Oraciones Diarias Simples",
            "subtema": "Oraciones diarias simples",
            "principal": entry["frase"],
            "contraste": entry["numeros"],
            "esquema": f"[Easy · Rama 7] -> [Oración: {entry['frase']}]",
            "ejemplos": [
                f"Oración: {entry['frase']}",
                f"Apoyo numérico: {entry['numeros']}",
            ],
        },
    ]

    medium_ramas = [
        {
            "numero": 1,
            "titulo": "Rama 1 · Tiempo Pasado",
            "subtema": "Tiempo pasado",
            "principal": entry["pasado"],
            "contraste": entry["frase"],
            "esquema": f"[Medium · Rama 1] -> [Pasado: {entry['pasado']}]",
            "ejemplos": [
                f"Pasado: {entry['pasado']}",
                f"Presente habitual: {entry['frase']}",
            ],
        },
        {
            "numero": 2,
            "titulo": "Rama 2 · Planes y Futuro",
            "subtema": "Planes y futuro",
            "principal": entry["futuro"],
            "contraste": entry["pasado"],
            "esquema": f"[Medium · Rama 2] -> [Futuro: {entry['futuro']}]",
            "ejemplos": [
                f"Futuro: {entry['futuro']}",
                f"Referencia pasada: {entry['pasado']}",
            ],
        },
        {
            "numero": 3,
            "titulo": "Rama 3 · Acción en Curso vs Rutina",
            "subtema": "Acción en curso vs rutina",
            "principal": entry["continuo"],
            "contraste": entry["frase"],
            "esquema": f"[Medium · Rama 3] -> [En curso: {entry['continuo']}]",
            "ejemplos": [
                f"En curso: {entry['continuo']}",
                f"Rutina: {entry['frase']}",
            ],
        },
        {
            "numero": 4,
            "titulo": "Rama 4 · Comparaciones",
            "subtema": "Comparaciones",
            "principal": entry["comparativo"],
            "contraste": entry["numeros"],
            "esquema": f"[Medium · Rama 4] -> [Comparación: {entry['comparativo']}]",
            "ejemplos": [
                f"Comparación: {entry['comparativo']}",
                f"Conteo base: {entry['numeros']}",
            ],
        },
        {
            "numero": 5,
            "titulo": "Rama 5 · Recomendación y Deber",
            "subtema": "Recomendación y deber",
            "principal": entry["modal"],
            "contraste": entry["listo"],
            "esquema": f"[Medium · Rama 5] -> [Modal: {entry['modal']}]",
            "ejemplos": [
                f"Modal: {entry['modal']}",
                f"Disposición: {entry['listo']}",
            ],
        },
    ]

    hard_ramas = [
        {
            "numero": 1,
            "titulo": "Rama 1 · Tiempos Perfectos",
            "subtema": "Tiempos perfectos",
            "principal": entry["perfecto"],
            "contraste": entry["pasado"],
            "esquema": f"[Hard · Rama 1] -> [Perfecto: {entry['perfecto']}]",
            "ejemplos": [
                f"Perfecto: {entry['perfecto']}",
                f"Pasado simple: {entry['pasado']}",
            ],
        },
        {
            "numero": 2,
            "titulo": "Rama 2 · Estructuras Condicionales",
            "subtema": "Estructuras condicionales",
            "principal": entry["condicional"],
            "contraste": entry["futuro"],
            "esquema": f"[Hard · Rama 2] -> [Condicional: {entry['condicional']}]",
            "ejemplos": [
                f"Condicional: {entry['condicional']}",
                f"Proyección futura: {entry['futuro']}",
            ],
        },
        {
            "numero": 3,
            "titulo": "Rama 3 · Voz Pasiva y Formalidad",
            "subtema": "Voz pasiva y formalidad",
            "principal": entry["pasiva"],
            "contraste": entry["frase"],
            "esquema": f"[Hard · Rama 3] -> [Pasiva: {entry['pasiva']}]",
            "ejemplos": [
                f"Pasiva: {entry['pasiva']}",
                f"Forma activa: {entry['frase']}",
            ],
        },
    ]

    expert_ramas = [
        {
            "numero": 1,
            "titulo": "Rama 1 · Expresiones Compuestas",
            "subtema": "Expresiones compuestas",
            "principal": entry["compuesto"],
            "contraste": entry["modal"],
            "esquema": f"[Expert/Nativo · Rama 1] -> [Compuesta: {entry['compuesto']}]",
            "ejemplos": [
                f"Compuesta: {entry['compuesto']}",
                f"Consejo: {entry['modal']}",
            ],
        },
        {
            "numero": 2,
            "titulo": "Rama 2 · Modismos del Idioma",
            "subtema": "Modismos del idioma",
            "principal": entry["modismo"],
            "contraste": entry["comparativo"],
            "esquema": f"[Expert/Nativo · Rama 2] -> [Modismo: {entry['modismo']}]",
            "ejemplos": [
                f"Modismo: {entry['modismo']}",
                f"Comparación: {entry['comparativo']}",
            ],
        },
        {
            "numero": 3,
            "titulo": "Rama 3 · Precisión Nativa Final",
            "subtema": "Precisión nativa final",
            "principal": entry["nativo"],
            "contraste": entry["condicional"],
            "esquema": f"[Expert/Nativo · Rama 3] -> [Nativo: {entry['nativo']}]",
            "ejemplos": [
                f"Nativo: {entry['nativo']}",
                f"Condicional: {entry['condicional']}",
            ],
        },
    ]

    grupos_crudos = {
        "Easy": easy_ramas,
        "Medium": medium_ramas,
        "Hard": hard_ramas,
        "Expert/Nativo": expert_ramas,
    }

    niveles_armados = {}
    for nivel_nom, lista_ramas in grupos_crudos.items():
        ramas_finales = []
        for r in lista_ramas:
            ramas_finales.append({
                "numero": r["numero"],
                "titulo": r["titulo"],
                "subtema": r["subtema"],
                "clases": construir_clases_rama(nombre, r["subtema"], r["principal"], r["contraste"], nivel_nom),
                "esquema": r["esquema"],
                "ejemplos": r["ejemplos"],
                "eval": construir_hoja_20_puntos(nombre, r["subtema"], r["principal"], r["contraste"]),
            })
        niveles_armados[nivel_nom] = ramas_finales

    juegos_10 = [
        {"n": 1, "t": "Saludo Rápido", "r": f"Elige el saludo en {nombre}:", "ops": [entry["saludo"], entry["gracias"], entry["numeros"]], "ok": entry["saludo"]},
        {"n": 2, "t": "Agradecimiento", "r": f"Elige cómo dar las gracias en {nombre}:", "ops": [entry["gracias"], entry["saludo"], entry["manana"]], "ok": entry["gracias"]},
        {"n": 3, "t": "Números", "r": f"Selecciona los números en {nombre}:", "ops": [entry["numeros"], entry["saludo"], entry["pasado"]], "ok": entry["numeros"]},
        {"n": 4, "t": "Mañana", "r": f"Elige el saludo de mañana en {nombre}:", "ops": [entry["manana"], entry["gracias"], entry["futuro"]], "ok": entry["manana"]},
        {"n": 5, "t": "Estar Listo", "r": f"Elige cómo decir que estás listo en {nombre}:", "ops": [entry["listo"], entry["modismo"], entry["manana"]], "ok": entry["listo"]},
        {"n": 6, "t": "Identidad", "r": f"Elige la frase de identidad en {nombre}:", "ops": [entry["identidad"], entry["gracias"], entry["pasiva"]], "ok": entry["identidad"]},
        {"n": 7, "t": "Rutina Diaria", "r": f"Selecciona la frase diaria en {nombre}:", "ops": [entry["frase"], entry["numeros"], entry["saludo"]], "ok": entry["frase"]},
        {"n": 8, "t": "Pasado y Futuro", "r": f"Elige la expresión de futuro en {nombre}:", "ops": [entry["futuro"], entry["pasado"], entry["saludo"]], "ok": entry["futuro"]},
        {"n": 9, "t": "Condicional", "r": f"Selecciona la estructura condicional en {nombre}:", "ops": [entry["condicional"], entry["gracias"], entry["numeros"]], "ok": entry["condicional"]},
        {"n": 10, "t": "Toque Nativo", "r": f"Elige la expresión nativa en {nombre}:", "ops": [entry["nativo"], entry["manana"], entry["identidad"]], "ok": entry["nativo"]},
    ]

    return {
        "nombre": nombre,
        "codigo": entry["codigo"],
        "saludo": entry["saludo"],
        "frase": entry["frase"],
        "numeros": entry["numeros"],
        "niveles": niveles_armados,
        "juegos": juegos_10,
    }

CURSOS_INDEX = {item["nombre"]: construir_curso_completo(item) for item in CATALOGO_IDIOMAS}

def generar_respuesta_consulta(idioma, texto, modo="profesor"):
    curso = CURSOS_INDEX.get(idioma) or CURSOS_INDEX["Inglés"]
    consulta = (texto or "").strip()
    modo_limpio = "buscador" if (modo or "").strip().lower() == "buscador" else "profesor"

    if not consulta:
        return f"[{idioma} · {modo_limpio.upper()}] Escribe tu pregunta o palabra sobre {idioma}."

    if API_KEY_IA:
        prompt = (
            f"Actúa como profesor experto de {idioma}. Responde de forma clara y directa a: {consulta}"
            if modo_limpio == "profesor"
            else f"Actúa como buscador de {idioma}. Explica '{consulta}' y da un ejemplo concreto en {idioma}."
        )
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO_IA}:generateContent?key={API_KEY_IA}"
        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}]
        }).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                partes = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                if partes and partes[0].get("text"):
                    return partes[0]["text"].strip()
        except Exception:
            pass

    limpio = re.sub(r"\s+", " ", consulta)
    if modo_limpio == "buscador":
        return (
            f"[BUSCADOR · {idioma.upper()}]\n"
            f"Término buscado: {limpio}\n"
            f"Referencia del idioma: '{curso['frase']}' | Saludo: '{curso['saludo']}' | Números: '{curso['numeros']}'."
        )
    return (
        f"[PROFESOR · {idioma.upper()}]\n"
        f"Pregunta: {limpio}\n"
        f"Respuesta: Practica '{limpio}' dentro del contexto de {idioma}, apoyándote en '{curso['frase']}' y avanzando rama por rama."
    )

HTML_TEMPLATE = """<!doctype html>
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
.main-wrap { max-width: 760px; margin: 0 auto; padding: 14px 14px 56px; }
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

<div id="viewAcceso" class="modal-screen">
    <div style="font-size:14px;font-weight:800;letter-spacing:1px;margin-bottom:10px;color:#e4e4e7">C-PRE "LENGUAJES" · ACCESO</div>
    <input type="text" id="inputClave" placeholder="Escribe CPRE2026" autocapitalize="characters" autocorrect="off" style="max-width:320px">
    <button onclick="procesarAcceso()" style="max-width:320px">ENTRAR</button>
    <div id="errorClave" style="color:#d4d4d8;font-weight:700;margin-top:10px;display:none">Código incorrecto. Usa CPRE2026.</div>
</div>

<div id="viewBienvenida" class="modal-screen hidden-view">
    <div class="bienvenida-caja">BIENVENIDO A C-PRE "LENGUAJES"</div>
    <div class="creacion-sub">Creaciones de Celso</div>
    <div id="lblCuenta" style="font-size:13px;color:#a1a1aa">Iniciando...</div>
</div>

<div id="viewDecisionEasy" class="modal-screen hidden-view">
    <div class="card" style="max-width:460px;width:100%">
        <h3>INICIO DE NIVEL</h3>
        <p style="font-weight:700;color:#ffffff">¿Quieres saltarte el modo Easy? Para saltártelo tienes que presentar la evaluación. Si pasas la evaluación puedes pasar al nivel Medium.</p>
        <button onclick="elegirSaltarEasy()">SALTAR MODO EASY (PRESENTAR EVALUACIÓN)</button>
        <button class="sec" onclick="elegirModoEasyNormal()">EMPEZAR EN MODO EASY</button>
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
            <button onclick="iniciarExamen(false)">SÍ, PRESENTAR EVALUACIÓN (20 PTS)</button>
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
            <button onclick="enviarConsultaLibre('profesor')">PREGUNTAR</button>
            <button class="sec" onclick="enviarConsultaLibre('buscador')">BUSCAR</button>
        </div>
        <div id="respuestaConsultaLibre" class="panel-nota">Escribe tu consulta sobre el idioma seleccionado.</div>
    </section>
</main>

<div class="dueno-corner">DUEÑO CELSO</div>

<script>
const CURSOS = __CURSOS_JSON__;
const CLAVE_ESPERADA = __CLAVE_JSON__;
const NOTICIAS = __NOTICIAS_JSON__;
const TACTICAS = __TACTICAS_JSON__;
const TRUCOS = __TRUCOS_JSON__;
const NIVELES = __NIVELES_JSON__;
const ORDINALES = __ORDINALES_JSON__;

let estado = {
    idioma: "Inglés",
    nivelIdx: 0,
    ramaIdx: 0,
    juegoIdx: 0,
    puntosJuego: 0,
    ultimaNota: 0
};

function cargarSelectorIdiomas() {
    const sel = document.getElementById("selectIdioma");
    sel.innerHTML = "";
    Object.keys(CURSOS).forEach((nombre) => {
        const opt = document.createElement("option");
        opt.value = nombre;
        opt.textContent = nombre;
        if (nombre === estado.idioma) opt.selected = true;
        sel.appendChild(opt);
    });
}

function mostrarFelicitacion(mensaje) {
    const el = document.getElementById("bannerFelicitacion");
    el.textContent = mensaje;
    el.classList.remove("hidden-view");
}

function procesarAcceso() {
    const ing = document.getElementById("inputClave").value.trim().toUpperCase();
    if (ing !== String(CLAVE_ESPERADA).trim().toUpperCase()) {
        document.getElementById("errorClave").style.display = "block";
        return;
    }
    document.getElementById("errorClave").style.display = "none";
    document.getElementById("viewAcceso").classList.add("hidden-view");

    const bienvenida = document.getElementById("viewBienvenida");
    bienvenida.classList.remove("hidden-view");
    let seg = 3;
    const actualizarCuenta = () => {
        document.getElementById("lblCuenta").textContent = `Cargando... ${seg}s`;
    };
    actualizarCuenta();

    const timer = setInterval(() => {
        seg -= 1;
        if (seg > 0) {
            actualizarCuenta();
        } else {
            clearInterval(timer);
            bienvenida.classList.add("hidden-view");
            document.getElementById("viewDecisionEasy").classList.remove("hidden-view");
        }
    }, 1000);
}

function elegirModoEasyNormal() {
    estado.nivelIdx = 0;
    estado.ramaIdx = 0;
    document.getElementById("viewDecisionEasy").classList.add("hidden-view");
    renderizarApp();
}

function elegirSaltarEasy() {
    estado.nivelIdx = 0;
    estado.ramaIdx = 0;
    document.getElementById("viewDecisionEasy").classList.add("hidden-view");
    renderizarApp();
    iniciarExamen(true);
}

function alCambiarIdioma() {
    estado.idioma = document.getElementById("selectIdioma").value;
    estado.ramaIdx = 0;
    estado.juegoIdx = 0;
    renderizarApp();
}

function renderizarDiarios() {
    const hoy = new Date();
    const inicioAno = new Date(hoy.getFullYear(), 0, 0);
    const diaDelAno = Math.floor((hoy - inicioAno) / 86400000);
    document.getElementById("metaDia").textContent = hoy.toLocaleDateString("es-VE");
    document.getElementById("boxNoticia").textContent = NOTICIAS[diaDelAno % NOTICIAS.length];
    document.getElementById("boxTactica").textContent = TACTICAS[diaDelAno % TACTICAS.length];
    document.getElementById("boxTruco").textContent = TRUCOS[diaDelAno % TRUCOS.length];
}

function renderizarApp() {
    const nombreNivel = NIVELES[estado.nivelIdx];
    const ramas = CURSOS[estado.idioma].niveles[nombreNivel];
    const rama = ramas[estado.ramaIdx % ramas.length];

    document.getElementById("metaNivel").textContent = nombreNivel;
    document.getElementById("metaRama").textContent = `${rama.numero}/${ramas.length}`;
    document.getElementById("metaNota").textContent = `${estado.ultimaNota}/20`;
    document.getElementById("tituloRamaActual").textContent = rama.titulo;
    document.getElementById("subtemaRamaActual").textContent = `Tema de la rama: ${rama.subtema}`;

    const clasesCont = document.getElementById("contenedorClases");
    clasesCont.innerHTML = "";
    rama.clases.forEach((lineaClase) => {
        const div = document.createElement("div");
        div.className = "clase-card";
        div.textContent = lineaClase;
        clasesCont.appendChild(div);
    });

    document.getElementById("esquemaRamaActual").textContent = `ESQUEMA:\n${rama.esquema}`;
    document.getElementById("ejemplosRamaActual").textContent = `EJEMPLOS:\n• ${rama.ejemplos.join("\n• ")}`;

    document.getElementById("panelExamen").classList.add("hidden-view");
    document.getElementById("panelPreparacion").classList.remove("hidden-view");

    renderizarDiarios();
    renderizarJuego();
}

function iniciarExamen(esSaltoEasy) {
    const nombreNivel = NIVELES[estado.nivelIdx];
    const ramas = CURSOS[estado.idioma].niveles[nombreNivel];
    const rama = ramas[estado.ramaIdx % ramas.length];

    document.getElementById("panelPreparacion").classList.add("hidden-view");
    const panelEx = document.getElementById("panelExamen");
    panelEx.classList.remove("hidden-view");

    let html = `<div class="examen-hoja">
        <div class="card-meta">
            <span>HOJA DE EXAMEN · ${estado.idioma.toUpperCase()}</span>
            <span>TOTAL: 20 PTS</span>
        </div>
        <p style="font-weight:700;color:#ffffff">${esSaltoEasy ? "Evaluación para saltar Easy a Medium (aprueba desde 10/20)" : `${rama.titulo} — Aprueba desde 10/20`}</p>`;

    rama.eval.forEach((preg, idx) => {
        const tipoEtiqueta = preg.tipo.replace("_", " ");
        html += `<div class="panel-nota"><strong>Pregunta ${preg.numero} (${preg.puntos} pts · ${tipoEtiqueta}):</strong><br>${preg.enunciado}<br>`;
        if (preg.tipo === "escribir") {
            html += `<input type="text" id="resp_preg_${idx}" placeholder="Escribe tu respuesta...">`;
        } else {
            preg.opciones.forEach((op, j) => {
                const seguro = op.replace(/"/g, "&quot;");
                html += `<label style="display:block;margin:6px 0;cursor:pointer"><input type="radio" name="radio_preg_${idx}" value="${seguro}" ${j === 0 ? "checked" : ""}> ${op}</label>`;
            });
        }
        html += `</div>`;
    });

    html += `<button onclick="calificarExamen(${esSaltoEasy ? "true" : "false"})">ENTREGAR EVALUACIÓN</button></div>`;
    panelEx.innerHTML = html;
}

function calificarExamen(esSaltoEasy) {
    const nombreNivel = NIVELES[estado.nivelIdx];
    const ramas = CURSOS[estado.idioma].niveles[nombreNivel];
    const rama = ramas[estado.ramaIdx % ramas.length];

    let puntaje = 0;
    let desglose = "";

    rama.eval.forEach((preg, idx) => {
        let acerto = false;
        if (preg.tipo === "escribir") {
            const elem = document.getElementById(`resp_preg_${idx}`);
            const val = (elem ? elem.value : "").trim().toLowerCase();
            acerto = preg.aceptadas.some((acc) => val === acc || (acc.length > 3 && val.includes(acc)));
        } else {
            const marcado = document.querySelector(`input[name="radio_preg_${idx}"]:checked`);
            acerto = Boolean(marcado && marcado.value === preg.correcta);
        }

        if (acerto) {
            puntaje += preg.puntos;
            desglose += `• Pregunta ${preg.numero}: +${preg.puntos} pts (Aprobada)\n`;
        } else {
            desglose += `• Pregunta ${preg.numero}: 0 pts (-${preg.puntos} pts) -> ${preg.explicacion}\n`;
        }
    });

    estado.ultimaNota = puntaje;
    document.getElementById("metaNota").textContent = `${puntaje}/20`;
    const porcentaje = Math.max(0, Math.min(100, Math.round((puntaje / 20) * 100)));
    const aprobo = puntaje >= 10;

    let cierreHtml = "";
    if (esSaltoEasy) {
        if (aprobo) {
            estado.nivelIdx = 1;
            estado.ramaIdx = 0;
            mostrarFelicitacion(`Felicitaciones, nuevo nivel: pasaste a Medium con ${puntaje}/20.`);
            cierreHtml = `<button onclick="renderizarApp()">CONTINUAR EN MEDIUM</button>`;
        } else {
            estado.nivelIdx = 0;
            estado.ramaIdx = 0;
            cierreHtml = `<p style="font-weight:700;color:#ffffff">No alcanzaste los 10/20 (${puntaje}/20). Debes ver las 7 ramas del modo Easy desde la Rama 1.</p><button onclick="renderizarApp()">IR A RAMA 1 DE EASY</button>`;
        }
    } else if (aprobo) {
        if (estado.ramaIdx + 1 < ramas.length) {
            estado.ramaIdx += 1;
            const ord = ORDINALES[String(estado.ramaIdx + 1)] || `${estado.ramaIdx + 1}a`;
            mostrarFelicitacion(`Felicitaciones, ${ord} rama del modo ${nombreNivel} (Nota: ${puntaje}/20).`);
            cierreHtml = `<button onclick="renderizarApp()">PASAR A LA SIGUIENTE RAMA</button>`;
        } else if (estado.nivelIdx + 1 < NIVELES.length) {
            estado.nivelIdx += 1;
            estado.ramaIdx = 0;
            mostrarFelicitacion(`Felicitaciones, nuevo nivel: ${NIVELES[estado.nivelIdx]} (Nota: ${puntaje}/20).`);
            cierreHtml = `<button onclick="renderizarApp()">ENTRAR AL NUEVO NIVEL</button>`;
        } else {
            mostrarFelicitacion(`Felicitaciones, completaste ${nombreNivel} con ${puntaje}/20.`);
            cierreHtml = `<button onclick="estado.ramaIdx=0;renderizarApp()">REINICIAR RAMAS DEL NIVEL</button>`;
        }
    } else {
        cierreHtml = `<p style="font-weight:700;color:#ffffff">Reprobaste con ${puntaje}/20 (se aprueba desde 10/20). Repasa las clases de esta rama e inténtalo de nuevo.</p><button class="sec" onclick="iniciarExamen(false)">REPETIR EVALUACIÓN</button>`;
    }

    document.getElementById("panelExamen").innerHTML = `<div class="examen-hoja">
        <h3>CALIFICACIÓN: ${puntaje}/20 (${aprobo ? "APROBADO" : "REPROBADO"})</h3>
        <div class="barra-fondo"><div class="barra-relleno" style="width:${porcentaje}%"></div></div>
        <div class="panel-nota">${desglose}</div>
        ${cierreHtml}
    </div>`;
}

function renderizarJuego() {
    const juegos = CURSOS[estado.idioma].juegos;
    const actual = juegos[estado.juegoIdx % juegos.length];

    document.getElementById("tituloJuegoActual").textContent = `JUEGO ${actual.n}/10 · ${actual.t}`;
    document.getElementById("enunciadoJuegoActual").textContent = actual.r;

    const contOps = document.getElementById("opcionesJuegoActual");
    contOps.innerHTML = "";
    actual.ops.forEach((op) => {
        const btn = document.createElement("button");
        btn.className = "sec";
        btn.textContent = op;
        btn.onclick = () => {
            if (op === actual.ok) {
                estado.puntosJuego += 10;
                document.getElementById("metaJuegoPts").textContent = `PTS: ${estado.puntosJuego}`;
                document.getElementById("feedbackJuegoActual").textContent = `¡Correcto! +10 pts.`;
            } else {
                document.getElementById("feedbackJuegoActual").textContent = `Incorrecto. Respuesta correcta: ${actual.ok}.`;
            }
            estado.juegoIdx += 1;
            renderizarJuego();
        };
        contOps.appendChild(btn);
    });
}

async function enviarConsultaLibre(modo) {
    const texto = document.getElementById("inputPreguntaLibre").value.trim();
    if (!texto) return;
    document.getElementById("metaModoConsulta").textContent = `MODO: ${modo.toUpperCase()}`;
    document.getElementById("respuestaConsultaLibre").textContent = "Consultando...";
    try {
        const res = await fetch("/api/consulta", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                idioma: estado.idioma,
                texto: texto,
                modo: modo
            })
        });
        const data = await res.json();
        document.getElementById("respuestaConsultaLibre").textContent = data.respuesta;
    } catch (err) {
        document.getElementById("respuestaConsultaLibre").textContent = "Error al consultar.";
    }
}

cargarSelectorIdiomas();
renderizarApp();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return (
        HTML_TEMPLATE
        .replace("__CURSOS_JSON__", json.dumps(CURSOS_INDEX, ensure_ascii=False))
        .replace("__CLAVE_JSON__", json.dumps(CODIGO_ACCESO, ensure_ascii=False))
        .replace("__NOTICIAS_JSON__", json.dumps(NOTICIAS_DIARIAS, ensure_ascii=False))
        .replace("__TACTICAS_JSON__", json.dumps(TACTICAS_DIARIAS, ensure_ascii=False))
        .replace("__TRUCOS_JSON__", json.dumps(TRUCOS_DIARIOS, ensure_ascii=False))
        .replace("__NIVELES_JSON__", json.dumps(ORDEN_NIVELES, ensure_ascii=False))
        .replace("__ORDINALES_JSON__", json.dumps(NOMBRES_RAMA_ORDINAL, ensure_ascii=False))
    )

@app.route("/api/consulta", methods=["POST"])
def api_consulta():
    payload = request.get_json(silent=True) or {}
    respuesta = generar_respuesta_consulta(
        payload.get("idioma"),
        payload.get("texto"),
        payload.get("modo"),
    )
    return jsonify({"respuesta": respuesta, "timestamp": datetime.utcnow().isoformat()})

if __name__ == "__main__":
    app.run(host=HOST_APP, port=PUERTO_APP)
