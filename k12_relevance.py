#!/usr/bin/env python3
"""
Shared K-12 AI relevance test for the scanners.

Why this exists: the ArXiv queries used `... AND (education OR student OR
school OR "k-12" OR learning)`. The bare term `learning` matches "machine
learning", "reinforcement learning", "deep learning" - i.e. essentially every
paper in cs.CY - and the results were then appended with no filtering at all.
A single September run surfaced a culinary reward-map benchmark, a scam-call
analysis, a residential energy-pricing paper, and a mass-shooting risk
classifier, all labelled "K-12 AI education benchmarks".

is_k12_relevant() is the gate. A record passes when it shows either
  (a) one STRONG schooling signal ("k-12", "classroom", "pedagogy", ...), or
  (b) an education word PLUS a schooling-context word,
and does not look like a different domain wearing education vocabulary.

Tuned against the 37 records the 2026-09-08 run produced; see
test_relevance() at the bottom for the expectations that pin the behaviour.
"""

import re

# Unambiguous K-12 / schooling signals. Any one of these is sufficient.
STRONG = [
    r'\bk-?12\b', r'\bk\s*-\s*12\b',
    r'kindergarten', r'\bpre-?k\b',
    r'(elementary|middle|high|primary|secondary|grade)\s+school',
    r'\bclassroom', r'\bteacher', r'\bteaching\b', r'pedagog',
    r'\bcurriculum\b', r'\bcurricula\b',
    r'\btutor', r'intelligent tutoring',
    r'\bliteracy\b', r'\bnumeracy\b',
    r'\bedtech\b', r'educational technology',
    r'learning analytics', r'learning outcome',
    r'student achievement', r'formative assessment',
    r'school district', r'\bschooling\b',
    r'\blearner', r'\bschoolchild',
    # Explicit education compounds. A title that calls itself education-facing
    # is on-topic for this catalogue even when no other schooling word appears
    # ("ELBench: A Multi-Dimensional Benchmark for Education-Facing LLMs" was
    # being dropped). None of the known off-topic results contain "educat" at
    # all, and OFF_TOPIC still guards the edge cases.
    r'educational', r'education-facing', r'education-oriented',
    r'\bin education\b', r'for education\b', r'education\s+(benchmark|dataset|technology)',
]

# Education words that are too broad alone.
EDU_WEAK = [r'educat', r'\bschool\b', r'\bstudent', r'\bcourse\b',
            r'\blecture\b', r'\bexam\b', r'\bgrading\b', r'\bacademic\b']

# Schooling context that upgrades a weak education word.
EDU_CONTEXT = [r'\bstudent', r'\bschool', r'\bteach', r'\bclass\b',
               r'\bcourse\b', r'\blecture\b', r'\bassessment\b',
               r'\bgrade', r'\blearn', r'\binstruct', r'\btutor',
               r'\bchildren\b', r'\byouth\b', r'\bK-?12\b']

# Domains that borrow education vocabulary but are not K-12 AI resources.
OFF_TOPIC = [
    r'culinary', r'\brecipe', r'\bflavou?r',
    r'\benergy\b', r'electricity', r'\bpower grid\b', r'residential pricing',
    r'scam call', r'\bspam\b', r'\bphishing\b',
    r'mass[- ]shooting', r'\bweapon',
    r'\bclinical\b', r'\bpatient', r'\bcancer\b', r'parkinson', r'\bdiagnos(is|tic) of\b',
    r'autonomous (driving|vehicle)', r'\bagricultur', r'\bcrop\b',
    r'stock market', r'\btrading\b', r'cryptocurrenc',
    r'\bwildlife\b', r'\bastronom', r'protein folding',
    r'anthropocene', r'\bculinary\b',
]

# Search-result / index pages are never a resource in their own right.
NOT_A_RESOURCE_URL = [
    r'/search\?', r'/search/\?', r'\?q=', r'&q=',
    r'/competitions/search', r'/accounts/(login|signup)',
    r'openreview\.net/search', r'paperswithcode\.com/search',
    r'aclweb\.org/anthology/volumes/',
    # Conference and platform landing pages. A proceedings homepage is a place
    # to find benchmarks, not a benchmark - the same objection as a search page.
    r'^https?://(www\.)?aied\d{4}\.org/?$',
    r'^https?://[^/]+/?$',
]


# Site-chrome link text. scan-resources.py regexes every <a> on a page, so
# without this the header and footer of any monitored site arrive as resources.
# The 2026-09 inventory contained "Business", "Company", "Developers",
# "Security" and "Foundation (opens in a new window)" - all typed as Dataset.
NAV_LABELS = {
    'about', 'about us', 'ai adoption', 'api', 'applied ai', 'blog', 'business',
    'careers', 'company', 'contact', 'contact us', 'developers', 'docs',
    'documentation', 'download', 'engineering', 'enterprise', 'faq', 'features',
    'global affairs', 'help', 'home', 'jobs', 'legal', 'log in', 'login',
    'models', 'news', 'newsroom', 'overview', 'partners', 'press', 'pricing',
    'privacy', 'privacy policy', 'product', 'products', 'research', 'resources',
    'safety', 'security', 'services', 'sign in', 'sign up', 'solutions',
    'stories', 'support', 'team', 'terms', 'terms of use',
    # Plurals and section names seen from Papers with Code, AI2, and
    # learningcommons.org - all previously ingested as "Datasets".
    'datasets', 'dataset', 'benchmarks', 'leaderboards', 'papers',
    'daily papers', 'all projects', 'projects', 'inference providers',
    'knowledge graph', 'curriculum sync', 'methods', 'libraries', 'tasks',
    'spaces', 'collections', 'trending', 'browse', 'explore', 'search',
}


def is_nav_label(title):
    """True when the link text is site navigation rather than a resource name."""
    t = re.sub(r'\s*\(opens in a new window\)\s*', '', str(title or ''), flags=re.I)
    t = t.strip().strip('›»→|-').strip().lower()
    return t in NAV_LABELS or len(t) < 3


def keyword_matches(keywords, *fields):
    """Whole-word keyword match.

    Substring matching is why the OpenAI watchlist ingested an entire website:
    its keyword list included "ai", and `"ai" in "https://openai.com/business/"`
    is True for every link on the domain. Match on word boundaries, and never
    against the host portion of a URL.
    """
    parts = []
    for f in fields:
        s = str(f or '')
        # Strip scheme+host so a keyword can't match the domain name itself.
        s = re.sub(r'^https?://[^/]+', ' ', s)
        parts.append(s)
    text = ' '.join(parts).lower()
    return any(re.search(r'\b' + re.escape(str(kw).lower()) + r'\b', text)
               for kw in keywords)


def _hits(patterns, text):
    return [p for p in patterns if re.search(p, text, re.I)]


def is_search_page(url):
    """True for index/search URLs, which can't be a specific resource.

    CAUTION: this rejects bare domain roots (https://zenodo.org), which is
    right for the benchmark and leaderboard scanners - a homepage is not a
    benchmark - but WRONG for scan-data-catalogs.py, where the root of a
    catalogue is exactly the resource being catalogued. Only import this into
    the benchmark/leaderboard scanners.
    """
    u = str(url or '')
    return bool(_hits(NOT_A_RESOURCE_URL, u))


def is_k12_relevant(*fields):
    """True when the combined text plausibly describes a K-12 AI resource."""
    text = ' '.join(str(f) for f in fields if f)
    if not text.strip():
        return False

    if _hits(OFF_TOPIC, text):
        return False

    if _hits(STRONG, text):
        return True

    # Weak education word only counts alongside a schooling context word.
    if _hits(EDU_WEAK, text) and _hits(EDU_CONTEXT, text):
        return True

    return False


def explain(*fields):
    """Diagnostic helper: why did this pass or fail?"""
    text = ' '.join(str(f) for f in fields if f)
    return {
        'off_topic': _hits(OFF_TOPIC, text),
        'strong': _hits(STRONG, text),
        'edu_weak': _hits(EDU_WEAK, text),
        'edu_context': _hits(EDU_CONTEXT, text),
        'verdict': is_k12_relevant(*fields),
    }


def test_relevance():
    """Pin the behaviour against real records from the 2026-09-08 scan."""
    should_pass = [
        'Beyond Helpfulness: A Teaching-over-Solving Diagnostic for Measuring Educational value',
        'Breakable Machine: A K-12 Classroom Game for Transformative AI literacy',
        'Cite or Decline: A Strict Course-Grounded Chatbot for STEM Lecture Videos',
        'A Protocol for Evaluating the Accessibility of AI-Generated Educational Materials for students',
        'Measuring Whether LLM Tutors Teach or Solve: A Diagnostic for tutoring',
        'K-12 Mathematics Standards-Aligned Dataset',
        'The pedagogy benchmark is a test of how well AI models understand pedagogy',
        'ELBench: A Multi-Dimensional Benchmark for Education-Facing Large Language Models',
        'A Protocol for Evaluating the Accessibility of AI-Generated Educational Materials',
    ]
    should_fail = [
        'FlavourBench: Executable Culinary Reward Maps for Language Model Evaluation',
        'Anatomy of a Scam Call: What 10,000 real scam and spam calls reveal',
        'Reinforcement Learning and Rule-Based Peer-to-Peer Pricing in Residential energy',
        'MASH-Bench: Diagnosing Cross-Source Failure in Mass-Shooting Risk Classification',
        'MemTrapBench: Benchmarking Cognitive Traps in LLM Memory Use',
        'Office Comprehension Benchmark',
        'TerraNova: A Foundation Model for the Anthropocene',
        'Papers with Code: GLUE Leaderboard',
        'Fairness Pruning: Locating Demographic Bias in GLU-MLP Layers',
    ]

    failures = []
    for t in should_pass:
        if not is_k12_relevant(t):
            failures.append(('FALSE NEGATIVE', t, explain(t)))
    for t in should_fail:
        if is_k12_relevant(t):
            failures.append(('FALSE POSITIVE', t, explain(t)))

    for kind, t, why in failures:
        print(f'{kind}: {t[:70]}')
        print(f'   {why}')
    total = len(should_pass) + len(should_fail)
    print(f'\n{total - len(failures)}/{total} relevance cases pass')
    return not failures


if __name__ == '__main__':
    import sys
    sys.exit(0 if test_relevance() else 1)
