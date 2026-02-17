import random
import time
import os
import json
from config import Config

# Optional: Real AI Library
try:
    import google.generativeai as genai
except ImportError:
    genai = None

class AIEngine:
    def __init__(self):
        self.provider = Config.AI_PROVIDER
        self.api_key = os.environ.get('GEMINI_API_KEY')
        
        if self.provider == "gemini" and self.api_key and genai:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')

        # --- COMPREHENSIVE OFFLINE KNOWLEGE BASE ---
        self.kb = {
            # --- Cloud Computing ---
            "cc1": {
                "title": "Cloud Architecture & Service Models",
                "explanation": "Cloud computing is typically defined by its service models: IaaS (Infrastructure as a Service), PaaS (Platform as a Service), and SaaS (Software as a Service). **IaaS** provides virtualized computing resources over the internet. **PaaS** offers hardware and software tools over the internet. **SaaS** provides software via a third-party over the internet. Understanding these layers is fundamental to architecting cloud solutions.",
                "key_points": [
                    "IaaS: AWS EC2, Google Compute Engine (Raw Power)",
                    "PaaS: Google App Engine, Heroku (Dev Platform)",
                    "SaaS: Google Drive, Slack (End User App)",
                    "Shared Responsibility Model applies differently to each."
                ],
                "example": "Netflix usage of AWS for IaaS to stream video, vs you using Gmail (SaaS) for email.",
                "quiz": {
                    "Easy": [
                        {"q": "Which model provides raw computing power?", "options": ["IaaS", "SaaS", "PaaS", "FaaS"], "a": "IaaS", "img": "https://placehold.co/600x300/16213e/FFF?text=IaaS+Layering"},
                        {"q": "Gmail is an example of?", "options": ["SaaS", "PaaS", "IaaS", "DBaaS"], "a": "SaaS", "img": None}
                    ],
                    "Moderate": [
                        {"q": "In which model does the consumer manage the O/S?", "options": ["IaaS", "PaaS", "SaaS", "None"], "a": "IaaS", "img": None},
                        {"q": "Which is NOT a cloud deployment model?", "options": ["Internet Cloud", "Public Cloud", "Private Cloud", "Hybrid Cloud"], "a": "Internet Cloud", "img": None}
                    ],
                    "Hard": [
                        {"q": "Which characteristic allows resource scaling up/down?", "options": ["Rapid Elasticity", "Broad Network Access", "Measured Service", "Pooling"], "a": "Rapid Elasticity", "img": None}
                    ]
                }
            },
            "cc2": {
                "title": "Virtualization Technology",
                "explanation": "Virtualization is the creation of a virtual (rather than actual) version of something, such as an operating system, a server, or storage device. It allows a single physical machine to act as multiple virtual machines, increasing efficiency and reducing costs. The **Hypervisor** (VMM) is the software that creates and manages VMs.",
                "key_points": ["Type 1 Hypervisor: Bare Metal (ESXi)", "Type 2 Hypervisor: Hosted (VirtualBox)", "Enables Cloud Multi-tenancy", "Hardware Abstraction"],
                "example": "Running Windows on a Macbook using Parallels or running multiple Linux servers on one physical Dell server.",
                "quiz": {
                    "Easy": [{"q": "What creates and manages VMs?", "options": ["Hypervisor", "Supervisor", "Manager", "Kernel"], "a": "Hypervisor", "img": None}],
                    "Moderate": [{"q": "Which is a Type-1 Hypervisor?", "options": ["VMware ESXi", "VirtualBox", "QEMU", "Parallels"], "a": "VMware ESXi", "img": "https://placehold.co/600x300/16213e/FFF?text=Hypervisor+Types"}],
                    "Hard": [{"q": "What is 'Live Migration'?", "options": ["Moving running VM between hosts", "Copying files", "Rebooting VM", "Installing OS"], "a": "Moving running VM between hosts", "img": None}]
                }
            },
            # --- AI & ML ---
            "ai1": {
                "title": "Supervised vs Unsupervised Learning",
                "explanation": "**Supervised Learning** involves training a model on a labeled dataset (Input->Output is known). **Unsupervised Learning** involves finding patterns in unlabeled data (grouping similar things). This is the foundational split in Machine Learning tasks.",
                "key_points": ["Supervised: Regression, Classification", "Unsupervised: Clustering, Dimensionality Reduction", "Labels are the key difference", "Semi-supervised exists as a middle ground"],
                "example": "Supervised: Predicting house prices (Regression). Unsupervised: Grouping customers by purchasing behavior (Clustering).",
                "quiz": {
                    "Easy": [{"q": "Which requires labeled data?", "options": ["Supervised", "Unsupervised", "Reinforcement", "None"], "a": "Supervised", "img": None}],
                    "Moderate": [{"q": "K-Means is an algorithm for?", "options": ["Clustering", "Regression", "Classification", "Planning"], "a": "Clustering", "img": "https://placehold.co/600x300/16213e/FFF?text=K-Means+Clustering"}],
                    "Hard": [{"q": "Which is a Classification metric?", "options": ["Accuracy/F1-Score", "MSE", "R-Squared", "Euclidean Distance"], "a": "Accuracy/F1-Score", "img": None}]
                }
            },
            "ai2": {
                "title": "Neural Networks & Deep Learning",
                "explanation": "Deep Learning mimics the human brain using artificial **Neural Networks**. A network consists of layers of nodes (neurons): an input layer, one or more hidden layers, and an output layer. 'Deep' refers to the number of hidden layers.",
                "key_points": ["Perceptron: Simplest neural network", "Activation Function: Introduces non-linearity (ReLU, Sigmoid)", "Backpropagation: Learning algorithm", "CNN: For Images, RNN: For Text"],
                "example": "FaceID on your iPhone uses a Deep Neural Network (CNN) to recognize facial features.",
                "quiz": {
                     "Easy": [{"q": "What is the basic unit of a NN?", "options": ["Neuron", "Pixel", "Kernel", "Bit"], "a": "Neuron", "img": "https://placehold.co/600x300/16213e/FFF?text=Neuron+Structure"}],
                     "Moderate": [{"q": "Function that decides if a neuron fires?", "options": ["Activation", "Loss", "Optimizer", "Linear"], "a": "Activation", "img": None}],
                     "Hard": [{"q": "Which solves the Vanishing Gradient problem?", "options": ["ReLU", "Sigmoid", "Tanh", "Step"], "a": "ReLU", "img": None}]
                }
            },
            # --- Java ---
             "j1": {
                "title": "J2EE & Servlets",
                "explanation": "Java 2 Platform, Enterprise Edition (J2EE) is used for building web services and networking applications. **Servlets** are Java classes that handle HTTP requests and implement the web server interface. They are the foundation of modern Java web frameworks.",
                "key_points": ["Servlet Lifecycle: init(), service(), destroy()", "JSP: Java Server Pages (View layer)", "Runs on Web Container (Tomcat)", "Stateless nature of HTTP"],
                "example": "When you submit a login form, a Servlet receives the POST request, checks the DB, and redirects you.",
                "quiz": {
                    "Easy": [{"q": "Servlets run on?", "options": ["Web Server/Container", "Browser", "Database", "Client"], "a": "Web Server/Container", "img": None}],
                    "Moderate": [{"q": "Which method handles requests?", "options": ["service()", "run()", "main()", "execute()"], "a": "service()", "img": None}],
                    "Hard": [{"q": "Object used to read form data?", "options": ["HttpServletRequest", "HttpServletResponse", "Session", "Config"], "a": "HttpServletRequest", "img": None}]
                }
            },
             # --- Bio ---
            "bio1": {
                "title": "Business Models in Biotech",
                "explanation": "Biotech entrepreneurship involves converting scientific discoveries into marketable products. Business models include: **Product-based** (selling a drug), **Platform-based** (selling a technology for others to use), and **Service-based** (CROs).",
                "key_points": ["High R&D cost and risk", "Long gestation period", "Regulatory hurdles (FDA)", "Intellectual Property is a key asset"],
                "example": "Moderna developed an mRNA platform (Platform model) which allowed them to quickly create a Covid vaccine (Product).",
                "quiz": {
                    "Easy": [{"q": "CRO stands for?", "options": ["Contract Research Org", "Clinical Research Org", "Central Research Org", "None"], "a": "Contract Research Org", "img": None}],
                    "Moderate": [{"q": "Key asset in Biotech?", "options": ["IP/Patents", "Office Space", "Raw Material", "Trucks"], "a": "IP/Patents", "img": None}],
                    "Hard": [{"q": "Phase I Clinical Trials test for?", "options": ["Safety", "Efficacy", "Comparison", "Marketing"], "a": "Safety", "img": None}]
                }
            },
             "bio2": {
                "title": "IPR & Patenting",
                "explanation": "Intellectual Property Rights (IPR) protect creations of the mind. In biotech, patents prevent others from using your invention for 20 years. This monopoly aims to recover the high R&D costs.",
                "key_points": ["Patentability criteria: Novelty, Non-obviousness, Utility", "Trade Secrets (e.g. Coca Cola recipe)", "Copyright (Written work)", "Geographical Indications"],
                "example": "A specific gene sequence modification can be patented if it's novel and useful.",
                "quiz": {
                     "Easy": [{"q": "Standard Patent term?", "options": ["20 Years", "50 Years", "Lifetime", "10 Years"], "a": "20 Years", "img": None}],
                     "Moderate": [{"q": "Not a criteria for patent?", "options": ["Abstract Idea", "Novelty", "Utility", "Non-obviousness"], "a": "Abstract Idea", "img": None}],
                     "Hard": [{"q": "Agreement for international patents?", "options": ["PCT", "NATO", "UNICEF", "WHO"], "a": "PCT", "img": None}]
                }
            }
        }

    def generate_explanation(self, topic_name, student_level="Beginner"):
        """
        Real AI or Robust Mock Fallback.
        """
        # Try finding subject ID in syllabus if name is passed, or lookup by ID directly
        topic_id = self._find_id_by_name(topic_name)
        
        if self.provider == "gemini" and self.model:
             try:
                 # Real Generation Logic (Simplified)
                 prompt = f"Explain {topic_name} for a college student. content: title, explanation, key_points, example."
                 response = self.model.generate_content(prompt)
                 return self._parse_gemini(response.text)
             except Exception as e:
                 print(f"AI Error: {e}")
        
        # Fallback to Knowledge Base
        return self._get_kb_content(topic_id, topic_name)

    def generate_quiz(self, topic_name, difficulty="Easy", num_questions=25, global_seed=0):
        topic_id = self._find_id_by_name(topic_name)
        
        # KB Lookup
        kb_questions = []
        if topic_id in self.kb and "quiz" in self.kb[topic_id]:
             kb_questions = self.kb[topic_id]["quiz"].get(difficulty, [])
             if not kb_questions: # Fallback to any difficulty
                 kb_questions = self.kb[topic_id]["quiz"].get("Easy", []) + self.kb[topic_id]["quiz"].get("Moderate", [])
        
        # Format KB questions
        formatted = []
        for i, q in enumerate(kb_questions):
            formatted.append({
                "id": i+1,
                "question": q['q'],
                "image": q.get('img'),
                "options": self._shuffle_options(q['options']),
                "answer": q['a']
            })
        
        # AI Generation if needed (if gemini is available)
        if len(formatted) < num_questions and self.provider == "gemini" and self.model:
            try:
                needed = num_questions - len(formatted)
                prompt = f"Generate {needed} MCQ questions for {topic_name} at {difficulty} level. Return JSON list of {{q, options[], a}}."
                response = self.model.generate_content(prompt)
                ai_questions = self._parse_quiz_json(response.text)
                for i, q in enumerate(ai_questions):
                    formatted.append({
                        "id": len(formatted)+1,
                        "question": q['q'],
                        "options": self._shuffle_options(q['options']),
                        "answer": q['a']
                    })
            except Exception as e:
                print(f"AI Quiz Gen Error: {e}")
 
        # Supplement with dynamic mock questions if still short
        while len(formatted) < num_questions:
            idx = len(formatted) + global_seed
            q_data = self._smart_mock_question(topic_name, idx, difficulty)
            formatted.append({
                "id": len(formatted) + 1,
                "question": q_data['q'],
                "options": q_data['options'], # Already shuffled/varied in helper
                "answer": q_data['a']
            })
             
        return formatted[:num_questions]

    def _smart_mock_question(self, topic, index, difficulty):
        # Use a hash of (topic + index) to ensure unique templates and variations
        import hashlib
        h = int(hashlib.md5(f"{topic}-{index}".encode()).hexdigest(), 16)
        
        templates = [
            {"q": "What is the primary objective of {topic}?", "a": "Efficiency and Optimization"},
            {"q": "Which component is most critical for {topic}?", "a": "Architecture Layer"},
            {"q": "A common challenge in {topic} implementation is:", "a": "Data Consistency"},
            {"q": "Which characteristic defines {topic} at a {difficulty} level?", "a": "Core Principles"},
            {"q": "How does {topic} impact modern system design?", "a": "Scalability Support"},
            {"q": "The fundamental concept behind {topic} is:", "a": "Abstraction"},
            {"q": "Which tool is best suited for managing {topic}?", "a": "Integrated Framework"},
            {"q": "In the context of MSc Computer Science, {topic} focuses on:", "a": "Enterprise Solutions"},
            {"q": "What is a major advantage of using {topic}?", "a": "Reduced Complexity"},
            {"q": "Which best describes a {difficulty} application of {topic}?", "a": "System Integration"},
            {"q": "The most important metric for {topic} performance is:", "a": "Latency/Throughput"},
            {"q": "Which protocol is often used in {topic} communication?", "a": "Standardized Interface"}
        ]
        
        distractors_pool = [
            "Hardware Limit", "Static Configuration", "Manual Entry", "Visual Design",
            "Color Palette", "Font Styling", "Legacy Documentation", "External Plugins",
            "Client Interface", "Simple Scripts", "Basic Operations", "Local Storage",
            "Minor Updates", "Initial Planning", "Concept Phase", "Generic Tools"
        ]
        
        # Select template
        tpl = templates[h % len(templates)]
        ans = tpl['a']
        
        # Select 3 unique distractors from pool (ensure they aren't the answer)
        random.seed(h)
        distractors = random.sample([d for d in distractors_pool if d != ans], 3)
        
        options = distractors + [ans]
        random.shuffle(options)
        
        return {
            "q": tpl['q'].format(topic=topic, difficulty=difficulty),
            "options": options,
            "a": ans
        }

    def _get_kb_content(self, topic_id, topic_name):
        if topic_id in self.kb:
            return self.kb[topic_id]
        
        # Smart Generic Generator if not in DB
        return {
            "title": f"Concept: {topic_name}",
            "explanation": f"**{topic_name}** is a key subject in your syllabus. While our specific database is updating for this topic, remember that it generally involves analyzing system components and optimizing performance.",
            "key_points": ["Definition and Scope", "Key Characteristics", "Advantages & Disadvantages", "Real-world Applications"],
            "example": "Refer to your standard textbook (Chapters 1-3) for a concrete example.",
            "summary": "Focus on the definitions and core principles."
        }
    
    def _generic_quiz(self, topic_name, difficulty):
        return [
            {"id": 1, "question": f"What is the primary purpose of {topic_name}?", "options": ["Optimization", "Security", "Storage", "Networking"], "answer": "Optimization", "image": None},
            {"id": 2, "question": f"True or False: {topic_name} is complex.", "options": ["True", "False"], "answer": "True", "image": None}
        ]

    def _find_id_by_name(self, name):
        # Reverse lookup helper (In real app, pass ID directly)
        for tid, data in self.kb.items():
            if data['title'].lower() in name.lower() or name.lower() in data['title'].lower():
                return tid
        return name.lower().replace(" ", "")

    def _shuffle_options(self, options):
        # Create a copy and shuffle
        opts = options.copy()
        random.shuffle(opts)
        return opts

    def _parse_gemini(self, text):
        # Placeholder for complex parsing. In a real app, you'd extract sections.
        return {
            "title": "AI Generated Content",
            "explanation": text,
            "key_points": ["Review generated text for key points"],
            "example": "See text above",
            "summary": "AI summary"
        }

    def _parse_quiz_json(self, text):
        try:
            # Try to find JSON block in markdown
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            return json.loads(text)
        except:
            return []

    def analyze_performance(self, scores_data):
        total_score = sum(s['score'] for s in scores_data)
        total_possible = sum(s['total'] for s in scores_data)
        avg_percent = (total_score / total_possible * 100) if total_possible > 0 else 0
        
        level = "Excellent" if avg_percent >= 60 else "Low level understanding"
        
        return {
            "level": level,
            "feedback": f"Based on your recent tests, your understanding is **{level}** ({int(avg_percent)}% avg).",
            "weak_topics": [s.get('topic_id', 'Unknown') for s in scores_data if s['score'] < s['total']*0.6]
        }

    def get_chat_response(self, user_query):
        """Handle student doubts with AI or mock response."""
        if self.provider == "gemini" and self.model:
            try:
                chat_prompt = f"You are a helpful study assistant for a Computer Science student. Answer this doubt concisely: {user_query}"
                response = self.model.generate_content(chat_prompt)
                return response.text
            except Exception as e:
                print(f"Chat AI Error: {e}")
        
        # Smart Mock Response
        keywords = {
            "java": "Java is an object-oriented programming language. For your syllabus, focus on Servlets and the J2EE stack.",
            "cloud": "Cloud Computing provides on-demand resources like IaaS, PaaS, and SaaS. AWS and Google Cloud are major providers.",
            "ai": "Artificial Intelligence involves machines mimicking human cognitive functions. ML and Deep Learning are its core subsets.",
            "bio": "Biotech entrepreneurship combines biology and business. IP rights (patents) are crucial for biotech startups.",
            "quiz": "You can take a quiz for any topic on the Dashboard to test your knowledge.",
            "exam": "The Semester Exam Mode provides a comprehensive 25-question test covering the entire syllabus."
        }
        
        for key, resp in keywords.items():
            if key in user_query.lower():
                return f"I can help with that! {resp}"
        
        return f"That's an interesting question about '{user_query}'. I recommend checking the specific study module on your dashboard for a detailed explanation, or ask me about Java, Cloud, AI, or Biotech!"
