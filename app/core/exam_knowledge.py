"""Curated SSC and Banking exam knowledge used to ground agent responses."""

from __future__ import annotations


TOPIC_WEIGHTAGES: dict[str, list[dict[str, str]]] = {
    "Quantitative Aptitude": [
        {"topic": "Number System", "weightage": "8-10%"},
        {"topic": "Percentage", "weightage": "5-7%"},
        {"topic": "Profit, Loss & Discount", "weightage": "5-7%"},
        {"topic": "Simple & Compound Interest", "weightage": "5-8%"},
        {"topic": "Ratio, Proportion & Partnership", "weightage": "5-7%"},
        {"topic": "Time, Speed & Distance", "weightage": "6-8%"},
        {"topic": "Time & Work + Pipes & Cisterns", "weightage": "5-6%"},
        {"topic": "Algebra & Equations", "weightage": "6-8%"},
        {"topic": "Geometry", "weightage": "8-10%", "note": "SSC-heavy"},
        {"topic": "Mensuration 2D & 3D", "weightage": "5-7%"},
        {"topic": "Trigonometry & Heights/Distances", "weightage": "5-8%", "note": "SSC-heavy"},
        {"topic": "Data Interpretation", "weightage": "15-20%", "note": "Banking-heavy"},
        {"topic": "Statistics", "weightage": "paper-specific", "note": "JSO/RBI Grade B"},
        {"topic": "Probability, Permutation & Combination", "weightage": "3-5%"},
        {"topic": "Sequence, Series & Progressions", "weightage": "3-4%"},
        {"topic": "Set Theory & Venn Diagrams", "weightage": "3-5%"},
    ],
    "Reasoning": [
        {"topic": "Verbal Reasoning", "weightage": "15-20%"},
        {
            "topic": "Puzzles & Seating Arrangement",
            "weightage": "20-25%",
            "note": "Banking mains-heavy",
        },
        {"topic": "Non-Verbal Reasoning", "weightage": "10-15%", "note": "SSC"},
        {"topic": "Input-Output & Machine Input", "weightage": "5%"},
        {"topic": "Data Sufficiency", "weightage": "5%"},
    ],
    "English Language": [
        {"topic": "Grammar - Core Rules", "weightage": "15-20%"},
        {"topic": "Vocabulary - Deep & Advanced", "weightage": "10-12%"},
        {"topic": "Reading Comprehension", "weightage": "15-20%"},
        {"topic": "Cloze Test & Fill in the Blanks", "weightage": "8-10%"},
        {"topic": "Para Jumbles & Sentence Ordering", "weightage": "5-8%"},
        {"topic": "Descriptive English", "weightage": "25 marks", "note": "SBI PO mains"},
    ],
    "General Awareness": [
        {"topic": "History", "weightage": "5-8%"},
        {"topic": "Geography", "weightage": "5-7%"},
        {"topic": "Polity & Constitution", "weightage": "5-8%"},
        {"topic": "Economics & Economy", "weightage": "8-12%", "note": "Banking-heavy"},
        {"topic": "Science", "weightage": "5-8%", "note": "Physics, Chemistry, Biology"},
        {"topic": "Banking Awareness", "weightage": "15-20%", "note": "Banking GA"},
        {"topic": "Current Affairs & Static GK", "weightage": "10-15%"},
        {"topic": "Computer Awareness", "weightage": "5-10%", "note": "Banking mains"},
    ],
}

SUBTOPIC_EXAMPLES: dict[str, list[str]] = {
    "Number System": [
        "Natural, whole, integer, rational, and irrational numbers",
        "LCM and HCF",
        "Divisibility rules",
        "Remainders and Fermat's Little Theorem",
        "Digital root",
        "Base number system",
        "Surds and indices",
        "Prime number properties",
        "Factorials",
        "Euler's Totient",
    ],
    "Data Interpretation": [
        "Bar, line, pie, table, mixed, and caselet DI",
        "Missing data DI",
        "Data sufficiency DI",
        "Ratio-chain DI",
        "Production-sale-stock DI",
        "Caselet DI for Banking mains",
    ],
    "Banking Awareness": [
        "RBI functions",
        "Types of banks",
        "NPA, IBC, and SARFAESI",
        "Basel norms",
        "Payment systems: NEFT, RTGS, UPI",
        "Priority sector lending",
        "KYC and AML",
        "RBI acts",
        "NABARD and SIDBI",
    ],
}

ROADMAP: list[dict[str, object]] = [
    {
        "phase": "Foundation",
        "weeks": "1-4",
        "items": [
            "Number System",
            "HCF/LCM",
            "Percentage and Ratio",
            "Basic grammar rules",
            "Static GK overview",
            "Basic arithmetic",
            "Beginner reasoning",
        ],
    },
    {
        "phase": "Core Syllabus",
        "weeks": "5-10",
        "items": [
            "Geometry and Mensuration",
            "Trigonometry",
            "Time, Speed and Work",
            "Algebra",
            "Syllogism and Blood Relations",
            "Vocabulary",
            "Geography and Science",
        ],
    },
    {
        "phase": "Advanced Topics",
        "weeks": "11-16",
        "items": [
            "All DI types",
            "Complex puzzles and seating",
            "Deep Banking Awareness",
            "RC, Cloze and Para Jumbles",
            "Statistics",
            "Computer Awareness",
        ],
    },
    {
        "phase": "Integration",
        "weeks": "17-22",
        "items": [
            "3-4 full mock tests weekly",
            "Daily current affairs",
            "Last 5 years PYQ analysis",
            "Weak-topic revision",
            "Caselet DI and advanced reasoning",
            "Descriptive writing",
        ],
    },
    {
        "phase": "Final Sprint",
        "weeks": "23-26",
        "items": [
            "Daily mocks and analysis",
            "Error-log review",
            "Speed drills",
            "6-month current-affairs revision",
            "Topic-wise flash revision",
            "Interview preparation for Banking",
        ],
    },
]

EXAM_WEIGHTAGES: dict[str, dict[str, str]] = {
    "SSC CGL Tier-1": {
        "quant": "20%",
        "reasoning": "25%",
        "english": "25%",
        "gk": "25%",
        "other": "5%",
    },
    "SSC CGL Tier-2": {
        "quant": "30%",
        "reasoning": "15%",
        "english": "30%",
        "gk": "5%",
        "other": "20%",
    },
    "IBPS PO Prelims": {"quant": "35%", "reasoning": "35%", "english": "30%", "gk": "0%"},
    "IBPS PO Mains": {
        "quant": "20%",
        "reasoning": "20%",
        "english": "20%",
        "gk": "25%",
        "other": "15%",
    },
    "SBI PO Prelims": {"quant": "35%", "reasoning": "35%", "english": "30%", "gk": "0%"},
    "SBI PO Mains": {
        "quant": "20%",
        "reasoning": "20%",
        "english": "20%",
        "gk": "20%",
        "other": "20%",
    },
    "RBI Grade B Phase-1": {
        "quant": "30%",
        "reasoning": "20%",
        "english": "20%",
        "gk": "20%",
        "other": "10%",
    },
}


def _resource(source_type: str, title: str, url: str, tags: str) -> dict[str, str]:
    return {"type": source_type, "title": title, "url": url, "tags": tags}


RESOURCES: list[dict[str, str]] = [
    _resource("official", "SSC official", "https://ssc.gov.in", "ssc"),
    _resource("official", "IBPS", "https://www.ibps.in/", "banking,ibps"),
    _resource("official", "SBI Careers", "https://sbi.co.in/careers", "banking,sbi"),
    _resource(
        "official",
        "RBI Careers",
        "https://www.rbi.org.in/Scripts/Careers.aspx",
        "banking,rbi",
    ),
    _resource("mock", "Testbook", "https://testbook.com/", "ssc,banking,mock"),
    _resource("mock", "Oliveboard", "https://www.oliveboard.in/", "banking,rbi,mock"),
    _resource("mock", "Adda247", "https://www.adda247.com/", "ssc,banking,mock"),
    _resource("mock", "Smartkeeda", "https://www.smartkeeda.com/", "di,puzzles,banking"),
    _resource("mock", "PracticeMock", "https://www.practicemock.com/", "ssc,banking,mock"),
    _resource("pyq", "AffairsCloud", "https://affairscloud.com/", "current-affairs,banking"),
    _resource("pyq", "IndiaBix", "https://www.indiabix.com/", "aptitude,reasoning"),
    _resource(
        "pyq",
        "GeeksforGeeks SSC Banking",
        "https://www.geeksforgeeks.org/ssc-banking/",
        "ssc,banking",
    ),
    _resource("pyq", "Jagran Josh", "https://www.jagranjosh.com/", "gk,current-affairs"),
    _resource("pyq", "GKToday", "https://www.gktoday.in/", "gk,current-affairs"),
    _resource(
        "notes",
        "NCERT textbooks",
        "https://www.ncert.nic.in/textbook.php",
        "gk,science,history,geography",
    ),
    _resource("youtube", "Vidyagram", "https://www.youtube.com/@vidyagram_ar", "regional"),
    _resource(
        "youtube",
        "Adda247 Telugu",
        "https://www.youtube.com/@adda247telugu",
        "regional,telugu",
    ),
    _resource(
        "youtube",
        "Everest Coaching Point",
        "https://www.youtube.com/EVERESTCOACHINGPOINT",
        "regional",
    ),
    _resource("youtube", "Parmar SSC", "https://www.youtube.com/@parmarssc", "ssc,gk"),
    _resource(
        "youtube",
        "Ramesh Sir Maths Class",
        "https://www.youtube.com/channel/UCWKWBq9tXVs_BRNev86taLQ",
        "maths",
    ),
    _resource(
        "youtube",
        "IACE",
        "https://www.youtube.com/channel/UCf0tcNw0YzQwbnNMiioyRCg",
        "banking",
    ),
    _resource(
        "youtube",
        "SREEDHAR'S CCE",
        "https://www.youtube.com/user/SreedharsCCE",
        "banking,regional",
    ),
    _resource(
        "youtube",
        "Abhinay Maths",
        "https://www.youtube.com/channel/UCdVmeIX3xVnQcTa5OMRz-hw",
        "maths,ssc",
    ),
    _resource(
        "youtube",
        "Gagan Pratap Maths",
        "https://www.youtube.com/channel/UCS2rhpz4RJEmb9CV7TPzBIg",
        "maths,ssc",
    ),
    _resource("youtube", "Amar Sir", "https://www.youtube.com/user/amarksaba", "maths"),
    _resource(
        "topic",
        "Testbook Quant Practice",
        "https://testbook.com/railway-coaching/quantitative-aptitude",
        "quant",
    ),
    _resource(
        "topic",
        "IndiaBix Number System",
        "https://www.indiabix.com/aptitude/numbers/",
        "number-system",
    ),
    _resource(
        "topic",
        "Oliveboard Algebra",
        "https://www.oliveboard.in/blog/ssc-cgl-algebra-questions/",
        "algebra,ssc",
    ),
    _resource(
        "topic",
        "Smartkeeda Profit/Loss",
        "https://www.smartkeeda.com/quantitative-aptitude/profit-and-loss-questions",
        "profit-loss",
    ),
    _resource(
        "topic",
        "Oliveboard Banking Awareness",
        "https://www.oliveboard.in/blog/banking-awareness/",
        "banking-awareness",
    ),
    _resource(
        "topic",
        "Bankersadda Banking Notes",
        "https://www.bankersadda.com/banking-awareness/",
        "banking-awareness",
    ),
    _resource(
        "topic",
        "GKToday Ancient History",
        "https://www.gktoday.in/ancient-history/",
        "history,gk",
    ),
]


def _is_supported_curated_exam(exam_type: str) -> bool:
    normalized = exam_type.lower()
    return any(
        keyword in normalized
        for keyword in ("ssc", "bank", "ibps", "sbi", "rbi")
    )


def _resource_matches_exam(resource: dict[str, str], exam_type: str) -> bool:
    normalized_exam = exam_type.lower()
    tags = resource["tags"].lower()
    if "ssc" in normalized_exam:
        return "ssc" in tags or resource["type"] in {"official", "notes", "pyq"}
    if any(keyword in normalized_exam for keyword in ("bank", "ibps", "sbi", "rbi")):
        return any(tag in tags for tag in ("banking", "ibps", "sbi", "rbi")) or resource[
            "type"
        ] in {"official", "notes", "pyq"}
    return False


def format_curated_exam_knowledge(exam_type: str) -> str:
    """Return compact curated knowledge for SSC and Banking exam agents."""

    if not _is_supported_curated_exam(exam_type):
        return (
            "No curated offline syllabus pack is available for this exam type. "
            "Use live search evidence, uploaded notes, and official-source caveats."
        )

    lines = [
        "Curated SSC CGL + Banking knowledge pack:",
        "",
        "Topic weightages:",
    ]
    for subject, topics in TOPIC_WEIGHTAGES.items():
        lines.append(f"- {subject}:")
        for item in topics:
            note = f" ({item['note']})" if "note" in item else ""
            lines.append(f"  - {item['topic']}: {item['weightage']}{note}")

    lines.extend(["", "Subtopic examples:"])
    for topic, subtopics in SUBTOPIC_EXAMPLES.items():
        lines.append(f"- {topic}: {', '.join(subtopics)}")

    lines.extend(["", "26-week roadmap:"])
    for phase in ROADMAP:
        lines.append(f"- {phase['phase']} (Weeks {phase['weeks']}): {', '.join(phase['items'])}")

    lines.extend(["", "Exam-level weightages:"])
    for exam, weightage in EXAM_WEIGHTAGES.items():
        parts = ", ".join(f"{section}: {value}" for section, value in weightage.items())
        lines.append(f"- {exam}: {parts}")

    lines.extend(["", "Relevant resource URLs:"])
    matching_resources = [
        resource for resource in RESOURCES if _resource_matches_exam(resource, exam_type)
    ]
    for resource in matching_resources:
        lines.append(f"- [{resource['type']}] {resource['title']}: {resource['url']}")

    lines.extend(
        [
            "",
            "Important caveat: this curated pack provides preparation guidance and "
            "known resource URLs. For current official notification dates, "
            "vacancies, eligibility, fees, and final syllabus PDFs, "
            "verify against the official exam-body website before giving a definitive answer.",
        ]
    )
    return "\n".join(lines)
