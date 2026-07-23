"""Default learning-track curricula seeded per user on demand.

Content mirrors the user's two study plans: the JS→Python bootcamp and the
French A1→CLB 7 roadmap. Weekday numbers follow Python's date.weekday()
(Mon=0 .. Sun=6). Both tracks run Mon/Tue/Wed/Sat/Sun — Thu/Fri (3, 4) are
rest days across every routine, freeing those two evenings for job-search
work / applications without breaking either streak.
"""

REST_WEEKDAYS = [3, 4]  # Thu, Fri off; active Mon, Tue, Wed, Sat, Sun

PYTHON_TRACK = {
    "slug": "python-bootcamp",
    "name": "Python Bootcamp (JS → Python)",
    "description": (
        "Four resources in parallel: the FreeCodeCamp JS→Python handbook "
        "(concept translation), python-patterns (idiomatic code & design "
        "patterns), Clean Code Python (used continuously), and a real backend "
        "— assay-qc-service (FastAPI, Postgres, SQLAlchemy, Alembic, Docker, "
        "pytest, Pydantic). Every topic: JS comparison → Python syntax → "
        "idiomatic Python → job-market usage → small exercise → real project "
        "application. No pointless calculator apps. 4 hours/day across two "
        "2-hour sessions — morning lesson + exercises, afternoon build & "
        "apply — 5 days/week (Mon, Tue, Wed, Sat, Sun), Thu/Fri off."
    ),
    "routines": [
        {
            "name": "Bootcamp session — lesson, exercises, review, refactor, commit",
            "minutes": 120,
            "rest_weekdays": REST_WEEKDAYS,
        },
        {
            "name": "Bootcamp session — build & apply",
            "minutes": 120,
            "rest_weekdays": REST_WEEKDAYS,
        },
    ],
    "sections": [
        {
            "section": "Week 1",
            "items": [
                {
                    "title": "Day 1 — Environment & fundamentals",
                    "details": (
                        "Set up Python 3.13, uv, VS Code, Git, ruff, pytest. "
                        "Variables (no let/const/var — names bound to objects), "
                        "print(), comments & docstrings, f-strings (always), "
                        "lists (.append vs .push), dicts vs JS objects, tuples, "
                        "sets. Exercise: employee.py — name, age, languages, "
                        "years_experience, currently_employed, printed with "
                        "f-strings."
                    ),
                    "learning_goal": (
                        "Get a working Python environment and understand how "
                        "Python's core building blocks differ from JavaScript's."
                    ),
                    "key_topics": [
                        "Python 3.13 + uv setup", "Variable binding vs let/const/var",
                        "f-strings", "Lists vs JS arrays", "Dicts vs JS objects",
                        "Tuples & sets",
                    ],
                },
                {
                    "title": "Day 2 — Control flow & functions",
                    "details": "Conditionals, loops, range, enumerate, functions.",
                    "learning_goal": (
                        "Write control flow and functions the Pythonic way "
                        "instead of transliterating JS syntax."
                    ),
                    "key_topics": [
                        "if/elif/else", "for/while loops", "range() and enumerate()",
                        "Function defaults", "*args/**kwargs",
                    ],
                },
                {
                    "title": "Day 3 — Comprehensions",
                    "details": (
                        "List comprehensions, dictionary comprehensions, set "
                        "comprehensions, generator expressions."
                    ),
                    "learning_goal": (
                        "Replace map/filter/reduce chains with Python's "
                        "comprehension syntax."
                    ),
                    "key_topics": [
                        "List comprehensions", "Dict comprehensions",
                        "Set comprehensions", "Generator expressions",
                    ],
                },
                {
                    "title": "Day 4 — Classes",
                    "details": "Classes, @dataclass, @property, @staticmethod.",
                    "learning_goal": (
                        "Model data and behavior with classes and understand "
                        "the decorators that make them idiomatic."
                    ),
                    "key_topics": [
                        "class & __init__", "@dataclass", "@property",
                        "@staticmethod vs @classmethod",
                    ],
                },
                {
                    "title": "Day 5 — Modules & packaging",
                    "details": "Modules, packages, imports, venv, pip, uv.",
                    "learning_goal": (
                        "Structure code across files and manage dependencies "
                        "the way real Python projects do."
                    ),
                    "key_topics": [
                        "Modules & packages", "import mechanics", "venv", "pip vs uv",
                    ],
                },
                {
                    "title": "Day 6 — Exceptions & I/O",
                    "details": "Exceptions, context managers, file handling.",
                    "learning_goal": (
                        "Handle failure paths and file I/O safely instead of "
                        "letting errors crash the program."
                    ),
                    "key_topics": [
                        "try/except/finally", "Custom exceptions",
                        "Context managers (with)", "File reading/writing",
                    ],
                },
                {
                    "title": "Day 7 — Mini project: Employee management CLI",
                    "details": "Pure Python, no framework.",
                    "learning_goal": (
                        "Combine the week's syntax into a small working "
                        "program without a framework."
                    ),
                    "key_topics": [
                        "CLI input loops", "Data modeling with classes",
                        "File persistence", "Putting week 1 together",
                    ],
                },
            ],
        },
        {
            "section": "Month 1 — Milestones",
            "items": [
                {
                    "title": "Variables, functions, classes", "details": None,
                    "learning_goal": "Confirm fluency in Python's core object model.",
                    "key_topics": ["Variable binding", "Function scope", "Class basics"],
                },
                {
                    "title": "Modules & packages", "details": None,
                    "learning_goal": "Confirm you can structure a multi-file project.",
                    "key_topics": ["Package layout", "Relative imports", "__init__.py"],
                },
                {
                    "title": "Comprehensions & generators", "details": None,
                    "learning_goal": "Confirm comfort writing comprehensions and lazy generators.",
                    "key_topics": ["Comprehension syntax", "yield", "Generator vs list tradeoffs"],
                },
                {
                    "title": "Exceptions", "details": None,
                    "learning_goal": "Confirm exception handling is second nature.",
                    "key_topics": ["Exception hierarchy", "Custom exceptions", "Context managers"],
                },
                {
                    "title": "Typing", "details": None,
                    "learning_goal": "Add static type hints to existing code.",
                    "key_topics": ["typing module", "Optional/Union", "Generic types", "mypy basics"],
                },
                {
                    "title": "Dataclasses", "details": None,
                    "learning_goal": "Use @dataclass to replace boilerplate __init__ methods.",
                    "key_topics": ["@dataclass", "field()", "frozen dataclasses"],
                },
                {
                    "title": "pathlib, itertools, collections", "details": None,
                    "learning_goal": "Use the standard library instead of reinventing common utilities.",
                    "key_topics": ["pathlib.Path", "itertools recipes", "collections.Counter/defaultdict"],
                },
                {
                    "title": "Decorators (basic)", "details": None,
                    "learning_goal": "Understand how decorators wrap functions.",
                    "key_topics": ["Function decorators", "functools.wraps", "Decorators with arguments"],
                },
            ],
        },
        {
            "section": "Month 2 — Backend (assay-qc-service)",
            "items": [
                {
                    "title": "FastAPI + Pydantic", "details": None,
                    "learning_goal": "Stand up a typed REST API.",
                    "key_topics": ["Path/query params", "Pydantic models", "Request validation"],
                },
                {
                    "title": "SQLAlchemy + Postgres", "details": None,
                    "learning_goal": "Persist data with an ORM instead of raw SQL strings.",
                    "key_topics": ["SQLAlchemy models", "Sessions", "Relationships"],
                },
                {
                    "title": "Alembic migrations", "details": None,
                    "learning_goal": "Version-control schema changes safely.",
                    "key_topics": ["Alembic revisions", "Autogenerate", "Upgrade/downgrade"],
                },
                {
                    "title": "Docker", "details": None,
                    "learning_goal": "Package the service so it runs the same everywhere.",
                    "key_topics": ["Dockerfile", "docker-compose", "Multi-stage builds"],
                },
                {
                    "title": "pytest", "details": None,
                    "learning_goal": "Write tests that give real confidence before deploys.",
                    "key_topics": ["Fixtures", "Parametrize", "Mocking"],
                },
                {
                    "title": "GitHub Actions CI", "details": None,
                    "learning_goal": "Automate tests running on every push.",
                    "key_topics": ["Workflow YAML", "Matrix builds", "Secrets"],
                },
                {
                    "title": "REST API design", "details": None,
                    "learning_goal": "Design endpoints the way a real product team would.",
                    "key_topics": ["Resource modeling", "Status codes", "Pagination"],
                },
                {
                    "title": "Authentication", "details": None,
                    "learning_goal": "Protect endpoints with real auth, not just an API key.",
                    "key_topics": ["JWT", "Password hashing", "Auth dependencies"],
                },
                {
                    "title": "Async programming", "details": None,
                    "learning_goal": "Understand when and why to use async in a FastAPI service.",
                    "key_topics": ["async/await", "Event loop", "Async SQLAlchemy"],
                },
                {
                    "title": "Ship assay-qc-service MVP",
                    "details": (
                        "The real backend replaces artificial tutorials — this "
                        "is what employers care about."
                    ),
                    "learning_goal": "Ship something a hiring manager could actually click through.",
                    "key_topics": ["End-to-end feature", "Deployment", "Demo-readiness"],
                },
            ],
        },
    ],
}

FRENCH_TRACK = {
    "slug": "french-a1-clb7",
    "name": "French — A1 → CLB 7 (Montréal)",
    "description": (
        "3 hours/day: 90 min cartoon listening + shadowing, 60 min textbook/"
        "grammar, 30 min Anki. 5 days/week — Mon, Tue, Wed, Sat, Sun; Thu/Fri "
        "off. Cartoon rotation: Mon Peppa Pig, Tue Petit Ours Brun, Wed "
        "Trotro, Sat repeat a favorite, Sun Caillou (québécois ear training). "
        "Listening block per episode: first pass with French subtitles, "
        "second pass without, shadow 3-5 sentences, extract 5-7 words to Anki."
    ),
    "routines": [
        {
            "name": "Cartoon listening + shadowing",
            "minutes": 90,
            "rest_weekdays": REST_WEEKDAYS,
        },
        {
            "name": "Textbook / grammar",
            "minutes": 60,
            "rest_weekdays": REST_WEEKDAYS,
        },
        {
            "name": "Anki",
            "minutes": 30,
            "rest_weekdays": REST_WEEKDAYS,
        },
    ],
    "sections": [
        {
            "section": "Phase 1 — A1 → A2 (weeks 1-14)",
            "items": [
                {
                    "title": "Cartoon immersion: Peppa Pig, Petit Ours Brun, Trotro",
                    "details": (
                        "Goal: understand 50% of each episode without "
                        "subtitles. Watch with French subtitles first, never "
                        "English."
                    ),
                    "learning_goal": (
                        "Train your ear on natural spoken French before "
                        "grammar rules make sense."
                    ),
                    "key_topics": [
                        "Everyday vocabulary", "Sentence rhythm & intonation",
                        "Listening without translating",
                    ],
                },
                {
                    "title": "Write 3 sentences per day about each episode",
                    "details": None,
                    "learning_goal": "Turn passive listening into active recall.",
                    "key_topics": [
                        "Present tense recall", "Basic sentence construction",
                        "Vocabulary retrieval",
                    ],
                },
                {
                    "title": "Complete French All-in-One ch. 1-15",
                    "details": (
                        "Prioritize what cartoons surface: present tense (ch. "
                        "10-11), aller + infinitive (ch. 13), avoir expressions "
                        "+ vouloir/pouvoir/devoir (ch. 12), reflexive verbs "
                        "(ch. 14), passé composé (ch. 15), question forms (ch. 7)."
                    ),
                    "learning_goal": (
                        "Build the grammar scaffolding the cartoons are "
                        "already surfacing."
                    ),
                    "key_topics": [
                        "Present tense", "aller + infinitive", "avoir expressions",
                        "Reflexive verbs", "passé composé", "Question forms",
                    ],
                },
                {
                    "title": "Caillou Sundays — québécois ear training",
                    "details": (
                        "Learn the Québec basics: c'est correct, déjeuner/dîner/"
                        "souper meal shifts, char, t'sais."
                    ),
                    "learning_goal": (
                        "Get comfortable with Québec-specific vocabulary and "
                        "slang, not just standard/Metropolitan French."
                    ),
                    "key_topics": [
                        "Québécois vocabulary", "c'est correct / t'sais",
                        "Meal-time vocabulary shifts",
                    ],
                },
            ],
        },
        {
            "section": "Phase 2 — A2 → B1 (weeks 15-34)",
            "items": [
                {
                    "title": "T'choupi, Caillou, Bluey (French dub)",
                    "details": (
                        "Goal: understand 70% of episodes; shadow whole "
                        "sentences."
                    ),
                    "learning_goal": (
                        "Push listening comprehension toward understanding "
                        "full sentences without help."
                    ),
                    "key_topics": [
                        "Extended listening stamina", "Shadowing full sentences",
                        "Faster natural speech patterns",
                    ],
                },
                {
                    "title": "Record yourself narrating episodes in your own words",
                    "details": None,
                    "learning_goal": (
                        "Force active production instead of passive recognition."
                    ),
                    "key_topics": [
                        "Spoken production", "Vocabulary retrieval under pressure",
                        "Self-correction",
                    ],
                },
                {
                    "title": "French Verb Tenses ch. 1-6", "details": None,
                    "learning_goal": (
                        "Lock down the tenses that come up constantly in "
                        "conversation."
                    ),
                    "key_topics": [
                        "Imparfait", "Futur simple", "Conditionnel", "Subjonctif (intro)",
                    ],
                },
            ],
        },
        {
            "section": "Phase 3 — B1 → B2 (weeks 35-62)",
            "items": [
                {
                    "title": "Transition to adult content",
                    "details": (
                        "RFI Journal en français facile, Français Authentique, "
                        "Easy French."
                    ),
                    "learning_goal": (
                        "Bridge from children's content to real adult-level "
                        "French media."
                    ),
                    "key_topics": [
                        "News French", "Slower authentic speech", "Formal register",
                    ],
                },
                {
                    "title": "French Verb Tenses ch. 7-11", "details": None,
                    "learning_goal": (
                        "Finish the verb tense system including irregular "
                        "patterns."
                    ),
                    "key_topics": [
                        "Passé simple (recognition)", "Advanced subjunctive",
                        "Irregular verb groups",
                    ],
                },
            ],
        },
        {
            "section": "Phase 4 — B2 → CLB 7 (weeks 63-74)",
            "items": [
                {
                    "title": "Native content: podcasts, news",
                    "details": None,
                    "learning_goal": (
                        "Handle full native-speed French without simplification."
                    ),
                    "key_topics": [
                        "Native-speed listening", "Idiomatic expressions",
                        "Regional accents",
                    ],
                },
                {
                    "title": "TEF preparation", "details": None,
                    "learning_goal": (
                        "Pass the TEF at the CLB 7 threshold needed for the goal."
                    ),
                    "key_topics": [
                        "TEF format", "Timed practice tests", "Exam strategy",
                    ],
                },
            ],
        },
    ],
}

DEFAULT_TRACKS = [PYTHON_TRACK, FRENCH_TRACK]
