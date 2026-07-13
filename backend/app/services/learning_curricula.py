"""Default learning-track curricula seeded per user on demand.

Content mirrors the user's two study plans: the JS→Python bootcamp and the
French A1→CLB 7 roadmap. Weekday numbers follow Python's date.weekday()
(Mon=0 .. Sun=6).
"""

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
        "application. No pointless calculator apps."
    ),
    "routines": [
        {
            "name": "Bootcamp session — lesson, exercises, review, refactor, commit",
            "minutes": 60,
            "rest_weekdays": None,
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
                },
                {
                    "title": "Day 2 — Control flow & functions",
                    "details": "Conditionals, loops, range, enumerate, functions.",
                },
                {
                    "title": "Day 3 — Comprehensions",
                    "details": (
                        "List comprehensions, dictionary comprehensions, set "
                        "comprehensions, generator expressions."
                    ),
                },
                {
                    "title": "Day 4 — Classes",
                    "details": "Classes, @dataclass, @property, @staticmethod.",
                },
                {
                    "title": "Day 5 — Modules & packaging",
                    "details": "Modules, packages, imports, venv, pip, uv.",
                },
                {
                    "title": "Day 6 — Exceptions & I/O",
                    "details": "Exceptions, context managers, file handling.",
                },
                {
                    "title": "Day 7 — Mini project: Employee management CLI",
                    "details": "Pure Python, no framework.",
                },
            ],
        },
        {
            "section": "Month 1 — Milestones",
            "items": [
                {"title": "Variables, functions, classes", "details": None},
                {"title": "Modules & packages", "details": None},
                {"title": "Comprehensions & generators", "details": None},
                {"title": "Exceptions", "details": None},
                {"title": "Typing", "details": None},
                {"title": "Dataclasses", "details": None},
                {"title": "pathlib, itertools, collections", "details": None},
                {"title": "Decorators (basic)", "details": None},
            ],
        },
        {
            "section": "Month 2 — Backend (assay-qc-service)",
            "items": [
                {"title": "FastAPI + Pydantic", "details": None},
                {"title": "SQLAlchemy + Postgres", "details": None},
                {"title": "Alembic migrations", "details": None},
                {"title": "Docker", "details": None},
                {"title": "pytest", "details": None},
                {"title": "GitHub Actions CI", "details": None},
                {"title": "REST API design", "details": None},
                {"title": "Authentication", "details": None},
                {"title": "Async programming", "details": None},
                {
                    "title": "Ship assay-qc-service MVP",
                    "details": (
                        "The real backend replaces artificial tutorials — this "
                        "is what employers care about."
                    ),
                },
            ],
        },
    ],
}

FRENCH_TRACK = {
    "slug": "french-a1-clb7",
    "name": "French — A1 → CLB 7 (Montréal)",
    "description": (
        "2 hours/day: 60 min cartoon listening + shadowing, 45 min textbook/"
        "grammar, 15 min Anki. Cartoon rotation: Mon Peppa Pig, Tue Petit Ours "
        "Brun, Wed Trotro, Thu T'choupi, Fri Caillou (québécois — Montréal "
        "ear training), Sat repeat a favorite, Sun rest (Anki only). Listening "
        "block per episode: first pass with French subtitles, second pass "
        "without, shadow 3-5 sentences, extract 5-7 words to Anki."
    ),
    "routines": [
        {
            "name": "Cartoon listening + shadowing",
            "minutes": 60,
            "rest_weekdays": [6],
        },
        {
            "name": "Textbook / grammar",
            "minutes": 45,
            "rest_weekdays": [6],
        },
        {
            "name": "Anki",
            "minutes": 15,
            "rest_weekdays": None,
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
                },
                {
                    "title": "Write 3 sentences per day about each episode",
                    "details": None,
                },
                {
                    "title": "Complete French All-in-One ch. 1-15",
                    "details": (
                        "Prioritize what cartoons surface: present tense (ch. "
                        "10-11), aller + infinitive (ch. 13), avoir expressions "
                        "+ vouloir/pouvoir/devoir (ch. 12), reflexive verbs "
                        "(ch. 14), passé composé (ch. 15), question forms (ch. 7)."
                    ),
                },
                {
                    "title": "Caillou Fridays — québécois ear training",
                    "details": (
                        "Learn the Québec basics: c'est correct, déjeuner/dîner/"
                        "souper meal shifts, char, t'sais."
                    ),
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
                },
                {
                    "title": "Record yourself narrating episodes in your own words",
                    "details": None,
                },
                {"title": "French Verb Tenses ch. 1-6", "details": None},
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
                },
                {"title": "French Verb Tenses ch. 7-11", "details": None},
            ],
        },
        {
            "section": "Phase 4 — B2 → CLB 7 (weeks 63-74)",
            "items": [
                {
                    "title": "Native content: podcasts, news",
                    "details": None,
                },
                {"title": "TEF preparation", "details": None},
            ],
        },
    ],
}

DEFAULT_TRACKS = [PYTHON_TRACK, FRENCH_TRACK]
