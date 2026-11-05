"""A browsable, generated catalog of practical global-help modules."""

import csv
import io

CATEGORIES = {
    "Travel & Visa": [
        "prepare visa documents", "renew a passport", "plan an affordable trip",
        "compare travel insurance", "prepare for a visa interview", "check entry requirements",
        "book accessible accommodation", "organize an international move",
    ],
    "Healthcare & Wellness": [
        "find reliable local healthcare", "prepare for a doctor visit", "compare health coverage",
        "build a daily wellbeing routine", "find mental health support", "plan accessible care",
        "prepare a family health record", "find emergency health services",
    ],
    "Finance & Money": [
        "create a monthly budget", "build an emergency fund", "compare banking options",
        "understand a credit report", "plan debt repayment", "track household expenses",
        "prepare for tax filing", "compare savings goals",
    ],
    "Remote Work": [
        "find legitimate remote work", "build a freelance portfolio", "coordinate across time zones",
        "prepare a home workspace", "manage international payments", "plan digital nomad work",
        "avoid remote job scams", "improve online teamwork",
    ],
    "Global Education": [
        "compare study destinations", "find suitable scholarships", "prepare an application timeline",
        "check institution accreditation", "plan credit transfer", "prepare for a language exam",
        "organize student accommodation", "find accessible learning resources",
    ],
    "Jobs & Careers": [
        "prepare a role-specific resume", "practice for an interview", "research salary ranges",
        "plan a career change", "verify a job offer", "build a professional portfolio",
        "prepare for international hiring", "identify in-demand skills",
    ],
    "Technology & AI": [
        "choose useful productivity tools", "protect personal data", "automate a routine task",
        "learn coding fundamentals", "compare cloud storage options", "use AI responsibly",
        "back up important devices", "choose accessible technology",
    ],
    "Environment & Sustainability": [
        "reduce household energy use", "save water at home", "plan lower-impact travel",
        "reduce food waste", "compare renewable energy options", "start a recycling routine",
        "prepare for local climate risks", "make a community garden plan",
    ],
    "Business & Startups": [
        "validate a business idea", "write a simple business plan", "research a target market",
        "plan startup cash flow", "register a small business", "protect customer information",
        "create an ethical marketing plan", "compare small-business funding",
    ],
    "Family & Parenting": [
        "organize a family routine", "plan childcare options", "support a child's learning",
        "plan care for an older relative", "prepare a family budget", "find local family services",
        "improve family communication", "prepare for a family move",
    ],
    "Legal & Rights": [
        "prepare questions for a lawyer", "understand a rental agreement",
        "document a consumer complaint", "organize employment records",
        "find local legal aid", "prepare for a small-claims process",
        "check official legal information", "keep important documents organized",
    ],
    "Food & Nutrition": [
        "plan balanced meals on a budget", "prepare safe meals for travel",
        "compare dietary choices", "organize weekly meal preparation",
        "find local food assistance", "plan nutritious family meals",
        "reduce household food waste", "understand food labels",
    ],
    "Transport & Mobility": [
        "plan a safe public-transit route", "compare commuting costs",
        "prepare a vehicle for a long trip", "find accessible transport",
        "plan a bicycle commute", "understand local road rules",
        "organize a car-free week", "check transport options in a new city",
    ],
    "Housing & Living": [
        "compare rental options", "review a lease checklist", "plan a safe move",
        "estimate monthly utility costs", "find accessible housing",
        "organize a shared household", "document a maintenance issue",
        "research a neighborhood before moving",
    ],
    "Sports & Fitness": [
        "build a beginner fitness routine", "prepare for a community sports event",
        "choose safe home exercise", "plan recovery and rest",
        "find inclusive sports programs", "prepare for a long-distance run",
        "track sustainable fitness goals", "choose accessible outdoor activities",
    ],
    "Culture & Communication": [
        "prepare for a new cultural setting", "learn practical local greetings",
        "resolve a communication misunderstanding", "practice public speaking",
        "build respectful international connections", "learn workplace etiquette",
        "plan a language-exchange routine", "communicate across time zones",
    ],
    "Cyber Security": [
        "secure personal online accounts", "recognize suspicious messages",
        "set up a password manager", "protect a small business website",
        "back up personal files safely", "check privacy settings",
        "secure a shared family device", "respond to a suspected account compromise",
    ],
    "Language & Learning": [
        "create a daily language practice plan", "improve listening comprehension",
        "practice useful conversations", "prepare for a language test",
        "build a focused vocabulary routine", "find accessible learning materials",
        "plan a peer-learning group", "practice pronunciation confidently",
    ],
    "Disability Support": [
        "find local accessibility services", "choose assistive technology",
        "request an accessible workplace adjustment", "plan an accessible trip",
        "make learning materials more accessible", "find inclusive community programs",
        "prepare questions about disability rights", "improve digital accessibility",
    ],
    "Agriculture & Food Security": [
        "plan crops for a local season", "improve soil health",
        "use irrigation water efficiently", "compare climate-resilient crops",
        "prepare a small farm budget", "find agricultural extension support",
        "reduce post-harvest food loss", "plan a community food garden",
    ],
    "Community & Volunteering": [
        "organize a local volunteer event", "identify community needs respectfully",
        "start a neighborhood support group", "plan an inclusive public event",
        "coordinate a community donation drive", "find trusted local charities",
        "measure a community project's impact", "support youth participation",
    ],
    "Faith & Wellbeing": [
        "build a reflective daily routine", "find a welcoming local community",
        "support interfaith understanding", "balance spiritual and personal wellbeing",
        "plan a community service activity", "find culturally respectful support",
        "practice mindful reflection", "support respectful family conversations",
    ],
    "Media & Content": [
        "plan an original educational video", "start a responsible podcast",
        "build an accessible content strategy", "check facts before publishing",
        "protect privacy in online content", "plan a community storytelling project",
        "create a sustainable publishing routine", "understand basic media rights",
    ],
    "AI Literacy": [
        "write clearer AI prompts", "check AI-generated information",
        "use AI safely for learning", "protect private data when using AI",
        "compare AI tools for a task", "understand responsible AI use",
        "document AI assistance transparently", "identify AI output limitations",
    ],
    "Logistics & Supply Chain": [
        "track small-business inventory", "compare reliable shipping options",
        "prepare an order-fulfillment checklist", "organize supplier records",
        "reduce last-mile delivery delays", "plan resilient sourcing",
        "prepare goods for international shipping", "improve warehouse safety",
    ],
}

AUDIENCES = (
    "beginners",
    "students",
    "families",
    "small businesses",
    "newcomers",
)


def build_catalog():
    """Return 1,000 distinct topic/audience catalog entries."""
    catalog = []
    for category, topics in CATEGORIES.items():
        for topic in topics:
            for audience in AUDIENCES:
                number = len(catalog) + 1
                catalog.append({
                    "id": f"module-{number:04d}",
                    "category": category,
                    "title": f"{topic.title()} for {audience.title()}",
                    "question": f"How can {audience} {topic}?",
                })
    if len(catalog) != 1000:
        raise ValueError(f"Expected 1,000 catalog entries, found {len(catalog)}")
    return catalog


def catalog_csv():
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=("id", "category", "title", "question"))
    writer.writeheader()
    writer.writerows(build_catalog())
    return output.getvalue().encode("utf-8-sig")
