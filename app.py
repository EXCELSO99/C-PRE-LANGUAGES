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
        "vocab_extra": {
            "hola": "你好 (Nǐ hǎo)",
            "gracias": "谢谢 (Xièxie)",
            "uno": "一 (Yī)",
            "dos": "二 (Èr)",
            "tres": "三 (Sān)",
            "agua": "水 (Shuǐ)",
            "casa": "家 (Jiā)",
            "libro": "书 (Shū)",
            "amigo": "朋友 (Péngyou)",
            "tiempo": "时间 (Shíjiān)",
        },
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
        "vocab_extra": {
            "hola": "こんにちは (Konnichiwa)",
            "gracias": "ありがとう (Arigatō)",
            "uno": "いち (Ichi)",
            "dos": "に (Ni)",
            "tres": "さん (San)",
            "agua": "みず (Mizu)",
            "casa": "いえ (Ie)",
            "libro": "ほん (Hon)",
            "amigo": "ともだち (Tomodachi)",
            "tiempo": "じかん (Jikan)",
        },
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
        "vocab_extra": {
            "hola": "안녕하세요 (Annyeonghaseyo)",
            "gracias": "감사합니다 (Gamsahamnida)",
            "uno": "하나 (Hana)",
            "dos": "둘 (Dul)",
            "tres": "셋 (Set)",
            "agua": "물 (Mul)",
            "casa": "집 (Jip)",
            "libro": "책 (Chaek)",
            "amigo": "친구 (Chingu)",
            "tiempo": "시간 (Sigan)",
        },
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
        "vocab_extra": {
            "hola": "مرحباً (Marhaban)",
            "gracias": "شكراً (Shukran)",
            "uno": "واحد (Wāḥid)",
            "dos": "اثنان (Ithnān)",
            "tres": "ثلاثة (Thalāthah)",
            "agua": "ماء (Mā')",
            "casa": "بيت (Bayt)",
            "libro": "كتاب (Kitāb)",
            "amigo": "صديق (Ṣadīq)",
            "tiempo": "وقت (Waqt)",
        },
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
        "vocab_extra": {
            "hola": "Привет (Privet)",
            "gracias": "Спасибо (Spasíbo)",
            "uno": "Один (Odín)",
            "dos": "Два (Dva)",
            "tres": "Три (Tri)",
            "agua": "Вода (Vodá)",
            "casa": "Дом (Dom)",
            "libro": "Книга (Kníga)",
            "amigo": "Друг (Drug)",
            "tiempo": "Время (Vrémya)",
        },
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
        "vocab_extra": {
            "hola": "नमस्ते (Namaste)",
            "gracias": "धन्यवाद (Dhanyavaad)",
            "uno": "एक (Ek)",
            "dos": "दो (Do)",
            "tres": "तीन (Teen)",
            "agua": "पानी (Paani)",
            "casa": "घर (Ghar)",
            "libro": "किताब (Kitaab)",
            "amigo": "दोस्त (Dost)",
            "tiempo": "समय (Samay)",
        },
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
        "vocab_extra": {
            "hola": "নমস্কার (Nomoshkar)",
            "gracias": "ধন্যবাদ (Dhonnobad)",
            "uno": "এক (Ek)",
            "dos": "দুই (Dui)",
            "tres": "তিন (Tin)",
            "agua": "জল (Jol)",
            "casa": "বাড়ি (Bari)",
            "libro": "বই (Boi)",
            "amigo": "বন্ধু (Bondhu)",
            "tiempo": "সময় (Shomoy)",
        },
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
        "vocab_extra": {
            "hola": "Merhaba",
            "gracias": "Teşekkürler",
            "uno": "Bir",
            "dos": "İki",
            "tres": "Üç",
            "agua": "Su",
            "casa": "Ev",
            "libro": "Kitap",
            "amigo": "Arkadaş",
            "tiempo": "Zaman",
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
        "vocab_extra": {
            "hola": "Hallo",
            "gracias": "Dank je",
            "uno": "Een",
            "dos": "Twee",
            "tres": "Drie",
            "agua": "Water",
            "casa": "Huis",
            "libro": "Boek",
            "amigo": "Vriend",
            "tiempo": "Tijd",
        },
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
        "vocab_extra": {
            "hola": "Cześć",
            "gracias": "Dziękuję",
            "uno": "Jeden",
            "dos": "Dwa",
            "tres": "Trzy",
            "agua": "Woda",
            "casa": "Dom",
            "libro": "Książka",
            "amigo": "Przyjaciel",
            "tiempo": "Czas",
        },
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
        "vocab_extra": {
            "hola": "Hej",
            "gracias": "Tack",
            "uno": "Ett",
            "dos": "Två",
            "tres": "Tre",
            "agua": "Vatten",
            "casa": "Hus",
            "libro": "Bok",
            "amigo": "Vän",
            "tiempo": "Tid",
        },
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
        "vocab_extra": {
            "hola": "Γεια σου (Geia sou)",
            "gracias": "Ευχαριστώ (Efcharistó)",
            "uno": "Ένα (Éna)",
            "dos": "Δύο (Dýo)",
            "tres": "Τρία (Tría)",
            "agua": "Νερό (Neró)",
            "casa": "Σπίτι (Spíti)",
            "libro": "Βιβλίο (Vivlío)",
            "amigo": "Φίλος (Fílos)",
            "tiempo": "Χρόνος (Chrónos)",
        },
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
        "vocab_extra": {
            "hola": "Xin chào",
            "gracias": "Cảm ơn",
            "uno": "Một",
            "dos": "Hai",
            "tres": "Ba",
            "agua": "Nước",
            "casa": "Nhà",
            "libro": "Sách",
            "amigo": "Bạn",
            "tiempo": "Thời gian",
        },
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
        "vocab_extra": {
            "hola": "سلام (Salām)",
            "gracias": "ممنون (Mamnoon)",
            "uno": "یک (Yek)",
            "dos": "دو (Do)",
            "tres": "سه (Seh)",
            "agua": "آب (Āb)",
            "casa": "خانه (Khāneh)",
            "libro": "کتاب (Ketāb)",
            "amigo": "دوست (Doost)",
            "tiempo": "زمان (Zamān)",
        },
    },
]

NOTICIAS_DIARIAS = [
    "Noticia diaria (Inglés): Reading short headlines every morning builds natural recognition of real English phrases.",
    "Noticia diaria (Inglés): Listening to short spoken clips and repeating them aloud trains clarity and rhythm.",
    "Noticia diaria (Inglés): Writing three lines daily about your routine strengthens core verb usage.",
    "Noticia diaria (Inglés): Learning expressions grouped by situation prevents mixing unrelated vocabulary.",
    "Noticia diaria (Inglés): Reviewing missed exam questions turns weak spots into permanent knowledge.",
    "Noticia diaria (Inglés): Practicing simple affirmative and negative sentences early speeds up conversation.",
    "Noticia diaria (Inglés): Fifteen focused minutes every day outperforms cramming once a week.",
    "Noticia diaria (Inglés): Paying attention to context helps you choose the exact phrase native speakers expect.",
    "Noticia diaria (Inglés): Mastering numbers early helps with time, prices, dates, and daily communication.",
    "Noticia diaria (Inglés): Advancing step by step from Easy to Expert builds solid long-term fluency.",
]

TACTICAS_DIARIAS = [
    "Táctica del día: Completa las 5 clases de la rama actual antes de abrir la hoja de examen.",
    "Táctica del día: Si eliges saltar Easy, concentra tu atención en cada punto porque necesitas mínimo 10/20.",
    "Táctica del día: En cada pregunta del examen verifica qué estructura pertenece realmente al tema estudiado.",
    "Táctica del día: Usa los números en voz alta después de estudiar la Rama 3 de Easy.",
    "Táctica del día: Analiza cada punto perdido en el desglose de calificación para subir a 20/20.",
    "Táctica del día: Cambia de idioma en el menú superior para comparar cómo se expresa la misma idea.",
    "Táctica del día: Alterna entre ramas teóricas y los 10 juegos adaptados para fijar memoria rápida.",
    "Táctica del día: No saltes preguntas de escritura; escribir fija ortografía y orden gramatical.",
    "Táctica del día: Mantén coherencia temática: cada rama trabaja un solo bloque sin mezclar conceptos.",
    "Táctica del día: Repasa el esquema de 3 pasos al final de cada rama antes de evaluarte.",
]

TRUCOS_DIARIOS = [
    "Truco del día: Asocia cada expresión nueva con una situación real en lugar de traducir palabra por palabra.",
    "Truco del día: En Verdadero o Falso, comprueba si la frase corresponde exactamente al tema de esa rama.",
    "Truco del día: Cuando escribas tu respuesta en el examen, revisa que no falten letras clave.",
    "Truco del día: Usa el botón PREGUNTAR para dudas de gramática y BUSCAR para significado y ejemplo.",
    "Truco del día: Practica la Rama 3 de Easy hasta dominar los números sin dudar.",
    "Truco del día: Si sacas de 0 a 9 puntos, vuelve a leer las clases de esa rama y presenta de nuevo.",
    "Truco del día: Observa el contraste entre la expresión principal y la alternativa en cada rama.",
    "Truco del día: En los niveles Hard y Expert/Nativo, fíjate en los matices y expresiones idiomáticas.",
    "Truco del día: Usa los juegos diarios como calentamiento rápido antes de presentar una evaluación.",
    "Truco del día: Mantén una meta clara: aprobar cada rama con 10/20 o más hasta llegar a Expert/Nativo.",
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
            "explicacion": f"La expresión correcta para completar este bloque es '{principal}'.",
        },
        {
            "numero": 3,
            "tipo": "identificar",
            "puntos": 4,
            "enunciado": f"Identifica la expresión correcta de '{tema}' en {idioma}:",
            "opciones": [principal, contraste, "Ninguna de las anteriores"],
            "correcta": principal,
            "explicacion": f"'{principal}' identifica correctamente el patrón de '{tema}'.",
        },
        {
            "numero": 4,
            "tipo": "escribir",
            "puntos": 4,
            "enunciado": f"Escribe la expresión clave trabajada en '{tema}' ({idioma}):",
            "aceptadas": [principal.lower(), base_corta],
            "muestra": principal,
            "explicacion": f"Respuesta esperada: {principal}.",
        },
        {
            "numero": 5,
            "tipo": "verdadero_falso",
            "puntos": 4,
            "enunciado": f"Verdadero o Falso: '{contraste}' es idéntico en función a '{principal}'.",
            "opciones": ["Verdadero", "Falso"],
            "correcta": "Falso",
            "explicacion": f"'{principal}' y '{contraste}' cumplen funciones distintas en {idioma}.",
        },
    ]

def construir_cinco_clases(idioma, nivel, subtema, principal, contraste):
    return [
        f"Clase 1 ({nivel} · {subtema}): Identifica la expresión central '{principal}' en {idioma} y su sentido exacto.",
        f"Clase 2 (Diferenciación): Compara '{principal}' con '{contraste}' para distinguir cuándo usar cada una.",
        f"Clase 3 (Aplicación real): Ubica '{principal}' dentro de una situación cotidiana en {idioma}.",
        f"Clase 4 (Control de errores): Mantén el foco solo en '{subtema}' sin mezclar temas ajenos.",
        f"Clase 5 (Cierre de rama): Repasa '{principal}' antes de presentar la evaluación sobre 20 puntos.",
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
            "titulo": "Rama 2 · Saludos y Cortesía",
            "subtema": "Saludos y cortesía",
            "principal": cfg["saludo"],
            "contraste": cfg["gracias"],
            "esquema": f"[Easy · Rama 2] -> [Saludo: {cfg['saludo']}] -> [Cortesía: {cfg['gracias']}]",
            "ejemplos": [f"Saludo: {cfg['saludo']}", f"Cortesía: {cfg['gracias']}"],
        },
        {
            "numero": 3,
            "titulo": "Rama 3 · Números",
            "subtema": "Números",
            "principal": cfg["numeros"],
            "contraste": cfg["identidad"],
            "esquema": f"[Easy · Rama 3] -> [Números: {cfg['numeros']}]",
            "ejemplos": [f"Números: {cfg['numeros']}", f"Referencia: {cfg['identidad']}"],
        },
        {
            "numero": 4,
            "titulo": "Rama 4 · Saludo de la Mañana",
            "subtema": "Saludo de la mañana",
            "principal": cfg["manana"],
            "contraste": cfg["saludo"],
            "esquema": f"[Easy · Rama 4] -> [Mañana: {cfg['manana']}]",
            "ejemplos": [f"Mañana: {cfg['manana']}", f"Saludo general: {cfg['saludo']}"],
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
            "titulo": "Rama 6 · Estar Listo y Disposición",
            "subtema": "Estar listo y disposición",
            "principal": cfg["listo"],
            "contraste": cfg["frase"],
            "esquema": f"[Easy · Rama 6] -> [Listo: {cfg['listo']}]",
            "ejemplos": [f"Listo: {cfg['listo']}", f"Práctica: {cfg['frase']}"],
        },
        {
            "numero": 7,
            "titulo": "Rama 7 · Oraciones Cotidianas",
            "subtema": "Oraciones cotidianas",
            "principal": cfg["frase"],
            "contraste": cfg["numeros"],
            "esquema": f"[Easy · Rama 7] -> [Oración: {cfg['frase']}]",
            "ejemplos": [f"Oración: {cfg['frase']}", f"Números: {cfg['numeros']}"],
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
            "titulo": "Rama 3 · Acción en Curso",
            "subtema": "Acción en curso",
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
            "ejemplos": [f"Comparación: {cfg['comparativo']}", f"Conteo: {cfg['numeros']}"],
        },
        {
            "numero": 5,
            "titulo": "Rama 5 · Verbos Modales y Deber",
            "subtema": "Verbos modales y deber",
            "principal": cfg["modal"],
            "contraste": cfg["listo"],
            "esquema": f"[Medium · Rama 5] -> [Modal: {cfg['modal']}]",
            "ejemplos": [f"Modal: {cfg['modal']}", f"Disposición: {cfg['listo']}"],
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
        {"n": 2, "t": "Gracias", "r": f"Elige cómo agradecer en {nombre}:", "ops": [cfg["gracias"], cfg["saludo"], cfg["manana"]], "ok": cfg["gracias"]},
        {"n": 3, "t": "Números", "r": f"Selecciona los números en {nombre}:", "ops": [cfg["numeros"], cfg["saludo"], cfg["pasado"]], "ok": cfg["numeros"]},
        {"n": 4, "t": "Mañana", "r": f"Elige el saludo de mañana en {nombre}:", "ops": [cfg["manana"], cfg["gracias"], cfg["futuro"]], "ok": cfg["manana"]},
        {"n": 5, "t": "Listo", "r": f"Elige cómo indicar que estás listo en {nombre}:", "ops": [cfg["listo"], cfg["modismo"], cfg["manana"]], "ok": cfg["listo"]},
        {"n": 6, "t": "Identidad", "r": f"Elige la frase de identidad en {nombre}:", "ops": [cfg["identidad"], cfg["gracias"], cfg["pasiva"]], "ok": cfg["identidad"]},
        {"n": 7, "t": "Frase Diaria", "r": f"Selecciona la frase diaria en {nombre}:", "ops": [cfg["frase"], cfg["numeros"], cfg["saludo"]], "ok": cfg["frase"]},
        {"n": 8, "t": "Futuro", "r": f"Elige la expresión de futuro en {nombre}:", "ops": [cfg["futuro"], cfg["pasado"], cfg["saludo"]], "ok": cfg["futuro"]},
        {"n": 9, "t": "Condicional", "r": f"Selecciona la estructura condicional en {nombre}:", "ops": [cfg["condicional"], cfg["gracias"], cfg["numeros"]], "ok": cfg["condicional"]},
        {"n": 10, "t": "Nativo", "r": f"Elige la expresión nativa en {nombre}:", "ops": [cfg["nativo"], cfg["manana"], cfg["identidad"]], "ok": cfg["nativo"]},
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
            f"Actúa como profesor experto de {idioma}. Responde de manera clara, estructurada y directa sobre: {texto}"
            if modo_ok == "profesor"
            else f"Actúa como buscador de {idioma}. Explica '{texto}' con su uso y un ejemplo real en {idioma}."
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
            f"Base del idioma -> Saludo: '{curso['saludo']}' | Números: '{curso['numeros']}' | Frase: '{curso['frase']}'."
        )
    return (
        f"[PROFESOR · {idioma.upper()}]\n"
        f"Duda: {texto_limpio}\n"
        f"Explicación: En {idioma}, trabaja esta idea apoyándote en estructuras reales como '{curso['frase']}' y avanza rama por rama."
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
    <div id="lblCuenta" style="font-size:13px;color:#a1a1aa">Iniciando...</div>
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
        return el ? JSON.parse(el.textContent) : respaldo;
    } catch (e) {
        return respaldo;
    }
}

var CURSOS = leerJsonSeguro("datosCursosJson", {});
var NOTICIAS = leerJsonSeguro("datosNoticiasJson", []);
var TACTICAS = leerJsonSeguro("datosTacticasJson", []);
var TRUCOS = leerJsonSeguro("datosTrucosJson", []);
var NIVELES = leerJsonSeguro("datosNivelesJson", ["Easy", "Medium", "Hard", "Expert/Nativo"]);
var ORDINALES = leerJsonSeguro("datosOrdinalesJson", {});

var estado = {
    idioma: "Inglés",
    nivelIdx: 0,
    ramaIdx: 0,
    juegoIdx: 0,
    puntosJuego: 0,
    ultimaNota: 0
};

function iniciarBienvenidaDirecta() {
    var bienvenida = document.getElementById("viewBienvenida");
    var seg = 2;
    var actualizarCuenta = function() {
        document.getElementById("lblCuenta").textContent = "Entrando... " + seg + "s";
    };
    actualizarCuenta();

    var timer = setInterval(function() {
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

function cargarSelectorIdiomas() {
    var sel = document.getElementById("selectIdioma");
    sel.innerHTML = "";
    Object.keys(CURSOS).forEach(function(nombre) {
        var opt = document.createElement("option");
        opt.value = nombre;
        opt.textContent = nombre;
        if (nombre === estado.idioma) opt.selected = true;
        sel.appendChild(opt);
    });
}

function mostrarFelicitacion(mensaje) {
    var el = document.getElementById("bannerFelicitacion");
    el.textContent = mensaje;
    el.classList.remove("hidden-view");
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
    var hoy = new Date();
    var inicioAno = new Date(hoy.getFullYear(), 0, 0);
    var diaDelAno = Math.floor((hoy - inicioAno) / 86400000);
    document.getElementById("metaDia").textContent = hoy.toLocaleDateString("es-VE");
    if (NOTICIAS.length) document.getElementById("boxNoticia").textContent = NOTICIAS[diaDelAno % NOTICIAS.length];
    if (TACTICAS.length) document.getElementById("boxTactica").textContent = TACTICAS[diaDelAno % TACTICAS.length];
    if (TRUCOS.length) document.getElementById("boxTruco").textContent = TRUCOS[diaDelAno % TRUCOS.length];
}

function renderizarApp() {
    var curso = CURSOS[estado.idioma];
    if (!curso) return;
    var nombreNivel = NIVELES[estado.nivelIdx];
    var ramas = curso.niveles[nombreNivel];
    var rama = ramas[estado.ramaIdx % ramas.length];

    document.getElementById("metaNivel").textContent = nombreNivel;
    document.getElementById("metaRama").textContent = rama.numero + "/" + ramas.length;
    document.getElementById("metaNota").textContent = estado.ultimaNota + "/20";
    document.getElementById("tituloRamaActual").textContent = rama.titulo;
    document.getElementById("subtemaRamaActual").textContent = "Tema de la rama: " + rama.subtema;

    var clasesCont = document.getElementById("contenedorClases");
    clasesCont.innerHTML = "";
    rama.clases.forEach(function(lineaClase) {
        var div = document.createElement("div");
        div.className = "clase-card";
        div.textContent = lineaClase;
        clasesCont.appendChild(div);
    });

    document.getElementById("esquemaRamaActual").textContent = "ESQUEMA:\n" + rama.esquema;
    document.getElementById("ejemplosRamaActual").textContent = "EJEMPLOS:\n• " + rama.ejemplos.join("\n• ");

    document.getElementById("panelExamen").classList.add("hidden-view");
    document.getElementById("panelPreparacion").classList.remove("hidden-view");

    renderizarDiarios();
    renderizarJuego();
}

function iniciarExamen(esSaltoEasy) {
    var nombreNivel = NIVELES[estado.nivelIdx];
    var ramas = CURSOS[estado.idioma].niveles[nombreNivel];
    var rama = ramas[estado.ramaIdx % ramas.length];

    document.getElementById("panelPreparacion").classList.add("hidden-view");
    var panelEx = document.getElementById("panelExamen");
    panelEx.classList.remove("hidden-view");

    var html = '<div class="examen-hoja">' +
        '<div class="card-meta">' +
        '<span>HOJA DE EXAMEN · ' + estado.idioma.toUpperCase() + '</span>' +
        '<span>TOTAL: 20 PTS</span>' +
        '</div>' +
        '<p style="font-weight:700;color:#ffffff">' + (esSaltoEasy ? "Evaluación para saltar Easy a Medium (aprueba desde 10/20)" : rama.titulo + " — Aprueba desde 10/20") + '</p>';

    rama.eval.forEach(function(preg, idx) {
        var tipoEtiqueta = preg.tipo.replace("_", " ");
        html += '<div class="panel-nota"><strong>Pregunta ' + preg.numero + ' (' + preg.puntos + ' pts · ' + tipoEtiqueta + '):</strong><br>' + preg.enunciado + '<br>';
        if (preg.tipo === "escribir") {
            html += '<input type="text" id="resp_preg_' + idx + '" placeholder="Escribe tu respuesta...">';
        } else {
            preg.opciones.forEach(function(op, j) {
                var seguro = op.replace(/"/g, "&quot;");
                html += '<label style="display:block;margin:6px 0;cursor:pointer"><input type="radio" name="radio_preg_' + idx + '" value="' + seguro + '" ' + (j === 0 ? "checked" : "") + '> ' + op + '</label>';
            });
        }
        html += '</div>';
    });

    html += '<button type="button" onclick="calificarExamen(' + (esSaltoEasy ? "true" : "false") + ')">ENTREGAR EVALUACIÓN</button></div>';
    panelEx.innerHTML = html;
}

function calificarExamen(esSaltoEasy) {
    var nombreNivel = NIVELES[estado.nivelIdx];
    var ramas = CURSOS[estado.idioma].niveles[nombreNivel];
    var rama = ramas[estado.ramaIdx % ramas.length];

    var puntaje = 0;
    var desglose = "";

    rama.eval.forEach(function(preg, idx) {
        var acerto = false;
        if (preg.tipo === "escribir") {
            var elem = document.getElementById("resp_preg_" + idx);
            var val = (elem ? elem.value : "").trim().toLowerCase();
            acerto = preg.aceptadas.some(function(acc) {
                return val === acc || (acc.length > 3 && val.indexOf(acc) !== -1);
            });
        } else {
            var marcado = document.querySelector('input[name="radio_preg_' + idx + '"]:checked');
            acerto = Boolean(marcado && marcado.value === preg.correcta);
        }

        if (acerto) {
            puntaje += preg.puntos;
            desglose += "• Pregunta " + preg.numero + ": +" + preg.puntos + " pts (Aprobada)\n";
        } else {
            desglose += "• Pregunta " + preg.numero + ": 0 pts (-" + preg.puntos + " pts) -> " + preg.explicacion + "\n";
        }
    });

    estado.ultimaNota = puntaje;
    document.getElementById("metaNota").textContent = puntaje + "/20";
    var porcentaje = Math.max(0, Math.min(100, Math.round((puntaje / 20) * 100)));
    var aprobo = puntaje >= 10;

    var cierreHtml = "";
    if (esSaltoEasy) {
        if (aprobo) {
            estado.nivelIdx = 1;
            estado.ramaIdx = 0;
            mostrarFelicitacion("Felicitaciones, nuevo nivel: pasaste a Medium con " + puntaje + "/20.");
            cierreHtml = '<button type="button" onclick="renderizarApp()">CONTINUAR EN MEDIUM</button>';
        } else {
            estado.nivelIdx = 0;
            estado.ramaIdx = 0;
            cierreHtml = '<p style="font-weight:700;color:#ffffff">No alcanzaste los 10/20 (' + puntaje + '/20). Debes ver las 7 ramas del modo Easy desde la Rama 1.</p><button type="button" onclick="renderizarApp()">IR A RAMA 1 DE EASY</button>';
        }
    } else if (aprobo) {
        if (estado.ramaIdx + 1 < ramas.length) {
            estado.ramaIdx += 1;
            var ord = ORDINALES[String(estado.ramaIdx + 1)] || (estado.ramaIdx + 1) + "a";
            mostrarFelicitacion("Felicitaciones, " + ord + " rama del modo " + nombreNivel + " (Nota: " + puntaje + "/20).");
            cierreHtml = '<button type="button" onclick="renderizarApp()">PASAR A LA SIGUIENTE RAMA</button>';
        } else if (estado.nivelIdx + 1 < NIVELES.length) {
            estado.nivelIdx += 1;
            estado.ramaIdx = 0;
            mostrarFelicitacion("Felicitaciones, nuevo nivel: " + NIVELES[estado.nivelIdx] + " (Nota: " + puntaje + "/20).");
            cierreHtml = '<button type="button" onclick="renderizarApp()">ENTRAR AL NUEVO NIVEL</button>';
        } else {
            mostrarFelicitacion("Felicitaciones, completaste " + nombreNivel + " con " + puntaje + "/20.");
            cierreHtml = '<button type="button" onclick="estado.ramaIdx=0;renderizarApp()">REINICIAR RAMAS DEL NIVEL</button>';
        }
    } else {
        cierreHtml = '<p style="font-weight:700;color:#ffffff">Reprobaste con ' + puntaje + '/20 (se aprueba desde 10/20). Repasa las clases de esta rama e inténtalo de nuevo.</p><button type="button" class="sec" onclick="iniciarExamen(false)">REPETIR EVALUACIÓN</button>';
    }

    document.getElementById("panelExamen").innerHTML = '<div class="examen-hoja">' +
        '<h3>CALIFICACIÓN: ' + puntaje + '/20 (' + (aprobo ? "APROBADO" : "REPROBADO") + ')</h3>' +
        '<div class="barra-fondo"><div class="barra-relleno" style="width:' + porcentaje + '%"></div></div>' +
        '<div class="panel-nota">' + desglose + '</div>' +
        cierreHtml +
        '</div>';
}

function renderizarJuego() {
    var juegos = CURSOS[estado.idioma].juegos;
    var actual = juegos[estado.juegoIdx % juegos.length];

    document.getElementById("tituloJuegoActual").textContent = "JUEGO " + actual.n + "/10 · " + actual.t;
    document.getElementById("enunciadoJuegoActual").textContent = actual.r;

    var contOps = document.getElementById("opcionesJuegoActual");
    contOps.innerHTML = "";
    actual.ops.forEach(function(op) {
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "sec";
        btn.textContent = op;
        btn.onclick = function() {
            if (op === actual.ok) {
                estado.puntosJuego += 10;
                document.getElementById("metaJuegoPts").textContent = "PTS: " + estado.puntosJuego;
                document.getElementById("feedbackJuegoActual").textContent = "¡Correcto! +10 pts.";
            } else {
                document.getElementById("feedbackJuegoActual").textContent = "Incorrecto. Respuesta correcta: " + actual.ok + ".";
            }
            estado.juegoIdx += 1;
            renderizarJuego();
        };
        contOps.appendChild(btn);
    });
}

async function enviarConsultaLibre(modo) {
    var texto = document.getElementById("inputPreguntaLibre").value.trim();
    if (!texto) return;
    document.getElementById("metaModoConsulta").textContent = "MODO: " + modo.toUpperCase();
    document.getElementById("respuestaConsultaLibre").textContent = "Consultando...";
    try {
        var res = await fetch("/api/consulta", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                idioma: estado.idioma,
                texto: texto,
                modo: modo
            })
        });
        var data = await res.json();
        document.getElementById("respuestaConsultaLibre").textContent = data.respuesta;
    } catch (err) {
        document.getElementById("respuestaConsultaLibre").textContent = "Error al consultar.";
    }
}

cargarSelectorIdiomas();
renderizarApp();
iniciarBienvenidaDirecta();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    cursos_serializados = json.dumps(BASE_CURSOS, ensure_ascii=False).replace("</", "<\\/")
    noticias_serializadas = json.dumps(NOTICIAS_DIARIAS, ensure_ascii=False).replace("</", "<\\/")
    tacticas_serializadas = json.dumps(TACTICAS_DIARIAS, ensure_ascii=False).replace("</", "<\\/")
    trucos_serializadas = json.dumps(TRUCOS_DIARIOS, ensure_ascii=False).replace("</", "<\\/")
    niveles_serializados = json.dumps(NIVELES_SISTEMA, ensure_ascii=False).replace("</", "<\\/")
    ordinales_serializados = json.dumps(ORDINALES_RAMAS, ensure_ascii=False).replace("</", "<\\/")

    return (
        HTML_PAGINA
        .replace("__CURSOS_JSON__", cursos_serializados)
        .replace("__NOTICIAS_JSON__", noticias_serializadas)
        .replace("__TACTICAS_JSON__", tacticas_serializadas)
        .replace("__TRUCOS_JSON__", trucos_serializados)
        .replace("__NIVELES_JSON__", niveles_serializados)
        .replace("__ORDINALES_JSON__", ordinales_serializados)
    )

@app.route("/api/consulta", methods=["POST"])
def api_consulta():
    datos = request.get_json(silent=True) or {}
    respuesta = responder_consulta_idioma(
        datos.get("idioma"),
        datos.get("texto"),
        datos.get("modo"),
    )
    return jsonify({
        "respuesta": respuesta,
        "timestamp": datetime.utcnow().isoformat(),
    })

if __name__ == "__main__":
    app.run(host=HOST_SERVIDOR, port=PUERTO_SERVIDOR)
