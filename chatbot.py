"""
University FAQ Chatbot (English + Roman Urdu)
Approach: intent classification
  text -> cleaning -> TF-IDF (word + char n-grams) -> Logistic Regression
  low confidence -> fallback reply
"""
import json
import random
import re
from pathlib import Path

import numpy as np
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

DATA_FILE = Path(__file__).parent / "intents.json"
THRESHOLD = 0.30  # below this confidence -> fallback

FALLBACKS = [
    "Maaf kijiye, offline FAQ mein is sawal ka jawab nahi mila. Aam sawalon ke liye OPENAI_API_KEY configure karke sidebar mein 'Use online AI' on karein.",
    "Yeh chatbot abhi limited offline FAQ mode mein hai. Is sawal ka jawab dene ke liye online AI enable karein ya apne sawal ko FAQ ke mutabiq dobara likhein.",
]

# small normalization for common Roman Urdu spelling variants
VARIANTS = {
    "kese": "kaise", "kesay": "kaise", "kesy": "kaise", "kaisay": "kaise",
    "hy": "hai", "he": "hai", "hn": "hun", "hoon": "hun",
    "kb": "kab", "kia": "kya", "kiya": "kya", "krna": "karna", "kru": "karun",
    "krun": "karun", "karoon": "karun", "fees": "fee", "plz": "please", "shukria": "shukriya", "kese": "kaise",
}

GLOBAL_MODULES = [
    {
        "tag": "global_travel_visa",
        "title": "Travel & Visa",
        "response": "For travel questions, check passport validity, visa rules, vaccination requirements, and airline booking deadlines. For country-specific rules, use official embassy or immigration websites before traveling.",
        "topics": ["visa application", "passport renewal", "flight booking", "travel insurance", "hotel booking", "immigration rules", "travel budget planning", "visa interview", "eVisa", "international trip"],
    },
    {
        "tag": "global_healthcare",
        "title": "Healthcare & Wellness",
        "response": "Use verified local clinics, hospital helplines, and public health guidance for emergencies. Keep vaccination records, emergency contacts, and insurance details ready for travel or relocation.",
        "topics": ["telemedicine", "doctor consultation", "health insurance", "vaccination", "mental wellness", "first aid", "emergency care", "nutrition plan", "pharmacy access", "online health checkup"],
    },
    {
        "tag": "global_finance",
        "title": "Finance & Money",
        "response": "Budgeting, savings, and investment decisions should be based on verified local laws and your own risk profile. Keep digital banking secure, track monthly spending, and compare interest rates before borrowing.",
        "topics": ["budgeting", "saving money", "credit score", "investing", "insurance", "bank account opening", "emergency fund", "digital wallets", "loan approval", "tax filing"],
    },
    {
        "tag": "global_remote_work",
        "title": "Remote Work",
        "response": "Remote work success depends on internet stability, time-zone coordination, portfolio proof, and legal work status. Use secure tools, time tracking, and clear communication for international collaboration.",
        "topics": ["remote jobs", "freelance income", "digital nomad visa", "online work", "time zone management", "job portfolio", "team communication", "home office setup", "freelancer taxes", "remote team tools"],
    },
    {
        "tag": "global_education",
        "title": "Global Education",
        "response": "Education support includes scholarships, application deadlines, credit transfer, language requirements, and student visa documentation. Compare institutions carefully and verify accreditation.",
        "topics": ["study abroad", "scholarship application", "student visa", "course selection", "language exam", "university ranking", "credit transfer", "research funding", "online learning", "student accommodation"],
    },
    {
        "tag": "global_jobs",
        "title": "Jobs & Careers",
        "response": "Job searches improve with a tailored resume, portfolio proof, interview practice, and networking. Use verified hiring portals and be careful about scams or fake recruitment offers.",
        "topics": ["job search", "resume writing", "linkedin profile", "career growth", "interview preparation", "work permit", "salary negotiation", "contract jobs", "skills training", "remote hiring"],
    },
    {
        "tag": "global_technology",
        "title": "Technology & AI",
        "response": "Technology adoption works best with security basics: backups, multi-factor authentication, safe browsing, and strong device setup. Learn core tools before advanced AI workflows.",
        "topics": ["AI tools", "cybersecurity", "cloud storage", "software setup", "automation workflow", "data privacy", "device protection", "coding career", "digital certificates", "online productivity"],
    },
    {
        "tag": "global_environment",
        "title": "Environment & Sustainability",
        "response": "Sustainable living can include energy reduction, recycling, public transport, and climate-aware food choices. Small everyday changes can reduce waste and improve local resilience.",
        "topics": ["climate action", "renewable energy", "water conservation", "waste reduction", "solar panels", "eco travel", "green living", "carbon footprint", "recycling tips", "sustainable cities"],
    },
    {
        "tag": "global_business",
        "title": "Business & Startups",
        "response": "Starting a business needs a clear value proposition, legal registration, market research, and cash-flow planning. Validate demand before scaling and protect customer data from day one.",
        "topics": ["startup ideas", "business plan", "market research", "small business loan", "brand strategy", "customer validation", "digital marketing", "sales funnel", "company registration", "business licensing"],
    },
    {
        "tag": "global_family",
        "title": "Family & Parenting",
        "response": "Strong family routines support health, education, and emotional wellbeing. Keep communication clear, set realistic goals, and seek local support when life stress increases.",
        "topics": ["childcare", "parenting tips", "family budgeting", "school planning", "home routines", "emotional support", "elder care", "parent teacher meeting", "meal planning", "family communication"],
    },
    {
        "tag": "global_legal",
        "title": "Legal & Rights",
        "response": "Legal matters require up-to-date information from official sources and licensed professionals. Document agreements, keep copies of records, and understand local rights before signing documents.",
        "topics": ["tenant rights", "employment law", "contract review", "consumer rights", "dispute resolution", "legal document", "witness support", "court process", "small claims", "citizen rights"],
    },
    {
        "tag": "global_food",
        "title": "Food & Nutrition",
        "response": "Healthy eating varies by age, activity, culture, and medical conditions. Focus on balanced meals, hydration, and practical habits you can sustain every week.",
        "topics": ["healthy meals", "meal prep", "protein intake", "hydration", "vegan nutrition", "weight loss", "food safety", "restaurant choices", "diet plan", "local food habits"],
    },
    {
        "tag": "global_transport",
        "title": "Transport & Mobility",
        "response": "Transport planning depends on local infrastructure, cost, and safety. Use official routes, real-time updates, and verified drivers for safer city travel and long-distance movement.",
        "topics": ["public transport", "ride booking", "traffic rules", "vehicle maintenance", "fuel costs", "car insurance", "bicycle commuting", "student transport", "city navigation", "road safety"],
    },
    {
        "tag": "global_housing",
        "title": "Housing & Living",
        "response": "Housing decisions should consider rent affordability, commute time, safety, and tenancy rights. Always verify lease terms, deposits, and neighborhood conditions before signing.",
        "topics": ["rent agreement", "house hunting", "student housing", "utility bills", "moving checklist", "neighborhood safety", "shared housing", "home maintenance", "landlord issues", "roommate agreement"],
    },
    {
        "tag": "global_sports",
        "title": "Sports & Fitness",
        "response": "Fitness works best with steady practice, recovery, and realistic goals. Choose activities you can sustain, and combine cardio, strength, flexibility, and sleep for lasting results.",
        "topics": ["fitness training", "weight loss workout", "home exercise", "sports injury", "running plan", "yoga practice", "strength training", "marathon prep", "recovery routines", "team sport coaching"],
    },
    {
        "tag": "global_culture",
        "title": "Culture & Communication",
        "response": "Cross-cultural communication improves with curiosity, listening, and respect. Learn local greetings, etiquette, and practical language basics to reduce friction in everyday interactions.",
        "topics": ["cross cultural communication", "international etiquette", "language learning", "conflict resolution", "public speaking", "community integration", "cultural sensitivity", "global networking", "festival etiquette", "daily greetings"],
    },
    {
        "tag": "global_cyber_security",
        "title": "Cyber Security",
        "response": "Protect accounts with strong passwords, multi-factor authentication, and regular backups. Be careful with suspicious links, fake QR codes, and requests for one-time verification codes.",
        "topics": ["online scam", "password manager", "two factor authentication", "malware protection", "safe browsing", "fake websites", "data backup", "social media safety", "device encryption", "phishing alert"],
    },
    {
        "tag": "global_language",
        "title": "Language & Learning",
        "response": "Language learning improves through consistent daily practice, listening, speaking, and real-life communication. Keep vocabulary focused on useful conversations and practical situations.",
        "topics": ["language learning", "english speaking", "grammar practice", "pronunciation", "vocabulary builder", "translation tools", "language exchange", "daily speaking practice", "fluency tips", "accent improvement"],
    },
    {
        "tag": "global_disability_support",
        "title": "Disability Support",
        "response": "Accessible support includes ramps, assistive technology, inclusive learning tools, and respectful communication. Local service centers can help with legal and practical needs.",
        "topics": ["accessible education", "assistive devices", "inclusive workplace", "disability rights", "mobility support", "screen reader", "hearing support", "accessible travel", "community resources", "inclusive design"],
    },
    {
        "tag": "global_agriculture",
        "title": "Agriculture & Food Security",
        "response": "Agricultural planning depends on soil quality, climate, irrigation, and market demand. Use local extension services to improve yield, water use, and crop resilience.",
        "topics": ["crop planning", "soil health", "organic farming", "irrigation tips", "seed selection", "greenhouse setup", "pest control", "farm marketing", "water management", "agri finance"],
    },
    {
        "tag": "global_community",
        "title": "Community & Volunteering",
        "response": "Community work becomes stronger with empathy, trust, and local coordination. Volunteers are most effective when they align with real needs and support local leaders.",
        "topics": ["volunteering", "community project", "social impact", "charity support", "local events", "youth programs", "community garden", "donation drives", "women support", "public service"],
    },
    {
        "tag": "global_religion",
        "title": "Faith & Wellbeing",
        "response": "Faith and wellbeing often coexist through reflection, service, and community. Respect differences, avoid judgment, and find practices that support inner peace and social balance.",
        "topics": ["spiritual guidance", "prayer routine", "meditation practice", "faith and mental health", "community worship", "family values", "ethical living", "mindfulness", "daily reflection", "interfaith respect"],
    },
    {
        "tag": "global_media",
        "title": "Media & Content",
        "response": "Content creation works when it is useful, original, and honest. Build trust with clear messaging, audience research, and consistent publishing habits.",
        "topics": ["content strategy", "video creation", "social media growth", "personal branding", "podcast setup", "blogging", "digital storytelling", "editing tools", "online audience", "creative workflow"],
    },
    {
        "tag": "video_generation",
        "title": "Video Generation",
        "response": "Video generation is in the Creation Studio under Video generation. Enter a text prompt and start a Runway job; check its status there to view or download the result. This requires RUNWAYML_API_SECRET, internet access, and may incur Runway charges.",
        "topics": ["AI video generation", "text to video", "generate a video from a prompt", "Runway video generation"],
        "patterns": [
            "generate a video", "generate video", "create a video", "create video",
            "how do i make a video", "how can i generate a video",
            "how to create a video", "how to generate a video",
            "i want a video generated", "make me a video",
            "generate video from a prompt", "video generate karna hai",
            "video banani hai", "video kaise banaye", "video bana do",
        ],
    },
    {
        "tag": "voice_generation",
        "title": "Voice & Speech",
        "response": "Voice input and read-aloud are available in Chat and in Creation Studio under Voice assistant. To make and download an MP3 from text, use Generate voice audio there; that feature requires OPENAI_API_KEY and may incur provider charges.",
        "topics": ["text to speech", "generate speech from text", "voice generation", "speech recognition"],
        "patterns": [
            "generate voice", "generate speech", "create a voice clip",
            "make an mp3 from text", "turn text into speech",
            "read this answer aloud", "speak this answer",
            "how do i generate voice audio", "voice input microphone",
            "speech to text", "audio bana do", "voice mein jawab",
            "awaaz mein jawab", "jawab sunao", "bol kar sunao",
            "speech generate karna",
        ],
    },
    {
        "tag": "global_ai_literacy",
        "title": "AI Literacy",
        "response": "AI literacy means using tools responsibly, understanding limitations, and verifying outputs. Learn prompt design, privacy basics, and ethical use before automation at scale.",
        "topics": ["AI prompt writing", "chatgpt usage", "AI ethics", "AI for study", "AI for business", "AI productivity", "AI safety", "AI tools for work", "machine learning basics", "online AI learning"],
    },
    {
        "tag": "global_logistics",
        "title": "Logistics & Supply Chain",
        "response": "Logistics success depends on planning, inventory tracking, supplier reliability, and customer communication. Use clear documentation and data to reduce delays and errors.",
        "topics": ["inventory management", "warehouse setup", "shipping tracking", "supplier negotiation", "delivery planning", "last mile delivery", "supply chain tools", "order fulfillment", "packing workflow", "vendor records"],
    },
]


def _build_global_patterns(module):
    starters = [
        "how can i", "how do i", "how to", "what is the best way to",
        "can i", "where can i", "when should i", "kya main"
    ]
    endings = ["", " quickly", " safely", " step by step"]
    patterns = []
    for topic in module["topics"]:
        for starter in starters:
            for ending in endings:
                patterns.append(f"{starter} {topic}{ending}".strip())
                patterns.append(f"{topic} {ending}".strip())
                patterns.append(f"{starter} {topic} step by step".strip())
                patterns.append(f"{topic} kaise hota hai".strip())
                patterns.append(f"{topic} kya hai".strip())
    patterns.extend(module.get("patterns", []))
    seen = set()
    normalized = []
    for item in patterns:
        value = item.strip().lower()
        if len(value) > 4 and value not in seen:
            seen.add(value)
            normalized.append(value)
    return normalized


def build_global_intents():
    intents = []
    for module in GLOBAL_MODULES:
        patterns = _build_global_patterns(module)
        intents.append({
            "tag": module["tag"],
            "title": module["title"],
            "response": module["response"],
            "patterns": patterns[:1200],
        })
    return intents


def clean(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    words = [VARIANTS.get(w, w) for w in text.split()]
    return " ".join(words)


class FAQBot:
    def __init__(self, data_file: Path = DATA_FILE):
        with open(data_file, encoding="utf-8") as f:
            intents = json.load(f)["intents"]

        global_intents = build_global_intents()
        intents.extend(global_intents)

        self.responses = {i["tag"]: i["response"] for i in intents}
        self.topic_titles = {i["tag"]: i.get("title", i["tag"]) for i in intents}
        self.X_text, self.y = [], []
        for i in intents:
            for p in i["patterns"]:
                self.X_text.append(clean(p))
                self.y.append(i["tag"])

        # word-level + character-level features (char n-grams handle spelling mistakes)
        self.word_vec = TfidfVectorizer(ngram_range=(1, 2))
        self.char_vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))
        self.model = LogisticRegression(max_iter=1000, C=10)

    def get_topics(self):
        return sorted(self.topic_titles.items(), key=lambda x: x[1])

    def _features(self, texts, fit=False):
        if fit:
            w = self.word_vec.fit_transform(texts)
            c = self.char_vec.fit_transform(texts)
        else:
            w = self.word_vec.transform(texts)
            c = self.char_vec.transform(texts)
        return hstack([w, c]).tocsr()

    def train(self):
        self.model.fit(self._features(self.X_text, fit=True), self.y)
        return self

    def evaluate(self, test_size=0.25, seed=42):
        """Hold-out evaluation (for the report)."""
        X_tr, X_te, y_tr, y_te = train_test_split(
            self.X_text, self.y, test_size=test_size, random_state=seed, stratify=self.y
        )
        tmp = FAQBot()
        tmp.model.fit(tmp._features(X_tr, fit=True), y_tr)
        pred = tmp.model.predict(tmp._features(X_te))
        print(f"Accuracy: {accuracy_score(y_te, pred):.2%}")
        print(classification_report(y_te, pred, zero_division=0))

    def predict(self, message: str):
        """Returns (tag, confidence)."""
        probs = self.model.predict_proba(self._features([clean(message)]))[0]
        idx = int(np.argmax(probs))
        return self.model.classes_[idx], float(probs[idx])

    def reply(self, message: str) -> str:
        if not clean(message):
            return "Kuch likhein, phir main jawab dunga."
        tag, conf = self.predict(message)
        if conf < THRESHOLD:
            return random.choice(FALLBACKS)
        return self.responses[tag]


if __name__ == "__main__":
    bot = FAQBot().train()
    print("=== Evaluation ===")
    bot.evaluate()
    print("=== Chat (type 'quit' to exit) ===")
    while True:
        msg = input("You: ")
        if msg.strip().lower() in {"quit", "exit"}:
            break
        tag, conf = bot.predict(msg)
        print(f"Bot: {bot.reply(msg)}   [intent={tag}, conf={conf:.2f}]")
