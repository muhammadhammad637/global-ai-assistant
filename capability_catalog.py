"""Reviewable technology and design catalogs; entries describe work, not fake integrations."""

import colorsys
import csv
import html
import io

SOCIAL_PROVIDERS = [
    "Google", "Apple", "Microsoft", "GitHub", "GitLab", "LinkedIn", "Facebook",
    "X", "Discord", "Slack", "Amazon", "Yahoo", "Reddit", "Twitch", "Spotify",
    "Zoom", "Dropbox", "Box", "Salesforce", "Atlassian", "Okta", "Auth0",
    "Keycloak", "GitHub Enterprise", "GitLab Self-Managed", "Microsoft Entra ID",
    "AWS Cognito", "Firebase Authentication", "Supabase Auth", "Clerk",
    "Hugging Face", "Mastodon", "Bluesky", "Pinterest", "Snapchat", "TikTok",
    "Telegram", "WhatsApp", "WeChat", "LINE", "Kakao", "PayPal", "Stripe",
    "Shopify", "WordPress.com", "Wikimedia", "GitBucket", "Bitbucket",
    "Gitea", "Forgejo", "SourceHut", "Discourse", "Stack Exchange",
    "Medium", "Dev.to", "Behance", "Dribbble", "Figma", "Canva", "Notion",
    "Miro", "Asana", "Trello", "Monday.com", "Linear", "Airtable", "Intercom",
    "Zendesk", "HubSpot", "Oracle", "SAP", "IBM", "Cloudflare", "DigitalOcean",
    "Heroku", "Vercel", "Netlify", "Render", "Fly.io", "Authsignal",
    "WorkOS", "FusionAuth", "Zitadel", "Ping Identity", "OneLogin",
    "JumpCloud", "Duo Security", "Keycloak Cloud", "Apple Business Manager",
    "Google Workspace", "Microsoft 365", "Amazon Business", "eBay",
    "Etsy", "Booking.com", "Airbnb", "Tripadvisor", "Strava", "Garmin",
    "Peloton", "Duolingo", "Coursera", "edX", "Khan Academy", "Udemy",
    "Salesforce Marketing Cloud", "Mailchimp", "SendGrid", "Twilio",
    "Vonage", "Yandex", "VK", "Odnoklassniki", "Weibo", "Baidu",
    "Gitee", "Coding.net", "Launchpad", "SourceForge", "OpenStreetMap",
    "Mapbox", "Foursquare", "Eventbrite", "Meetup", "Patreon", "Ko-fi",
    "Substack", "Tidal", "SoundCloud", "Deezer", "Epic Games", "Steam",
    "Battle.net", "Roblox", "Unity", "Unreal Engine", "Autodesk",
    "Intuit", "Xero", "QuickBooks", "Plaid", "Wise", "Revolut",
    "Monzo", "Mercado Libre", "Klarna", "Adyen", "Razorpay", "Payoneer",
    "Keycloak OIDC", "Generic OpenID Connect",
]

SECURITY_TOPICS = [
    "enable phishing-resistant multi-factor authentication",
    "review account recovery and trusted contacts",
    "configure secure session expiry",
    "audit least-privilege access",
    "protect secrets outside source control",
    "rotate exposed credentials safely",
    "validate uploaded file types and sizes",
    "protect forms against cross-site request forgery",
    "encode untrusted text before rendering",
    "parameterize database queries",
    "rate-limit sensitive authentication endpoints",
    "monitor repeated sign-in failures",
    "review security event logs",
    "encrypt backups and test recovery",
    "secure cookies with HttpOnly and SameSite",
    "verify dependencies and update vulnerable packages",
    "document a privacy and data-retention policy",
    "minimize personal information collected",
    "secure administrative access with separate accounts",
    "create an incident response checklist",
]

FRONTEND_TOPICS = [
    "build keyboard-accessible navigation",
    "design responsive layouts for small screens",
    "add clear form validation and error messages",
    "create reusable accessible components",
    "optimize images and page loading",
    "add a searchable topic catalogue",
    "support right-to-left layouts",
    "create a consistent design-token system",
    "add dark and light themes",
    "improve screen-reader labels",
    "add a multilingual language selector",
    "design helpful empty states",
    "add mobile-friendly data tables",
    "create accessible notification patterns",
    "add an offline-friendly loading state",
    "test color contrast and focus visibility",
    "build a useful profile settings page",
    "create a privacy-aware chat interface",
    "add filterable cards and categories",
    "test layouts at multiple viewport sizes",
]

BACKEND_TOPICS = [
    "design a versioned REST API",
    "add server-side request validation",
    "use database transactions for writes",
    "add pagination and stable sorting",
    "create a safe background job queue",
    "add structured application logging",
    "implement role-based authorization checks",
    "write database migrations with rollback plans",
    "add idempotency for retryable requests",
    "design a health-check endpoint",
    "add database indexes for common queries",
    "build resilient external-service timeouts",
    "validate webhook signatures",
    "add API usage quotas",
    "create privacy-safe audit events",
    "write integration tests for critical flows",
    "add a configurable cache layer",
    "manage application configuration securely",
    "implement bulk import with validation reports",
    "design a disaster-recovery restore procedure",
]

FILE_EXTENSIONS = [
    "txt", "md", "rst", "log", "csv", "tsv", "json", "jsonl", "xml", "yaml",
    "yml", "toml", "ini", "cfg", "conf", "html", "htm", "css", "scss", "sass",
    "less", "js", "mjs", "cjs", "jsx", "ts", "tsx", "vue", "svelte", "py",
    "pyi", "ipynb", "java", "kt", "kts", "scala", "groovy", "c", "h", "cc",
    "cpp", "hpp", "cs", "fs", "vb", "go", "rs", "rb", "php", "phtml", "swift",
    "m", "mm", "pl", "pm", "r", "rmd", "jl", "lua", "sql", "graphql", "gql",
    "proto", "sh", "bash", "zsh", "fish", "ps1", "psm1", "bat", "cmd", "dockerfile",
    "makefile", "mk", "gradle", "properties", "env.example", "gitignore", "editorconfig",
    "tex", "bib", "org", "adoc", "asciidoc", "svg", "png", "jpg", "jpeg", "webp",
    "gif", "bmp", "tif", "tiff", "ico", "avif", "heic", "heif", "pdf", "docx",
    "xlsx", "pptx", "odt", "ods", "odp", "rtf", "epub", "mobi", "mp3", "wav",
    "ogg", "m4a", "flac", "aac", "mp4", "webm", "mov", "mkv", "avi", "mpeg",
    "mpg", "3gp", "zip", "tar", "gz", "bz2", "7z", "rar", "parquet", "feather",
    "arrow", "sqlite", "db", "wasm", "bin", "dat", "ics", "vcf", "eml", "msg",
]

AUDIENCES = ("beginners", "students", "small teams", "maintainers", "accessibility teams")

LANGUAGES = {
    "af": "Afrikaans", "sq": "Albanian", "am": "Amharic", "ar": "Arabic",
    "hy": "Armenian", "az": "Azerbaijani", "eu": "Basque", "be": "Belarusian",
    "bn": "Bengali", "bs": "Bosnian", "bg": "Bulgarian", "ca": "Catalan",
    "ceb": "Cebuano", "zh": "Chinese", "zh-TW": "Chinese (Traditional)",
    "co": "Corsican", "hr": "Croatian", "cs": "Czech", "da": "Danish",
    "nl": "Dutch", "en": "English", "eo": "Esperanto", "et": "Estonian",
    "fi": "Finnish", "fr": "French", "fy": "Frisian", "gl": "Galician",
    "ka": "Georgian", "de": "German", "el": "Greek", "gu": "Gujarati",
    "ht": "Haitian Creole", "ha": "Hausa", "haw": "Hawaiian", "he": "Hebrew",
    "hi": "Hindi", "hmn": "Hmong", "hu": "Hungarian", "is": "Icelandic",
    "ig": "Igbo", "id": "Indonesian", "ga": "Irish", "it": "Italian",
    "ja": "Japanese", "jv": "Javanese", "kn": "Kannada", "kk": "Kazakh",
    "km": "Khmer", "rw": "Kinyarwanda", "ko": "Korean", "ku": "Kurdish",
    "ky": "Kyrgyz", "lo": "Lao", "la": "Latin", "lv": "Latvian",
    "lt": "Lithuanian", "lb": "Luxembourgish", "mk": "Macedonian",
    "mg": "Malagasy", "ms": "Malay", "ml": "Malayalam", "mt": "Maltese",
    "mi": "Maori", "mr": "Marathi", "mn": "Mongolian", "my": "Myanmar",
    "ne": "Nepali", "no": "Norwegian", "ny": "Nyanja", "or": "Odia",
    "ps": "Pashto", "fa": "Persian", "pl": "Polish", "pt": "Portuguese",
    "pa": "Punjabi", "ro": "Romanian", "ru": "Russian", "sm": "Samoan",
    "gd": "Scots Gaelic", "sr": "Serbian", "st": "Sesotho", "sn": "Shona",
    "sd": "Sindhi", "si": "Sinhala", "sk": "Slovak", "sl": "Slovenian",
    "so": "Somali", "es": "Spanish", "su": "Sundanese", "sw": "Swahili",
    "sv": "Swedish", "tl": "Tagalog", "tg": "Tajik", "ta": "Tamil",
    "tt": "Tatar", "te": "Telugu", "th": "Thai", "tr": "Turkish",
    "tk": "Turkmen", "uk": "Ukrainian", "ur": "Urdu", "ug": "Uyghur",
    "uz": "Uzbek", "vi": "Vietnamese", "cy": "Welsh", "xh": "Xhosa",
    "yi": "Yiddish", "yo": "Yoruba", "zu": "Zulu",
}


def build_task_modules(category, topics):
    rows = []
    for topic in topics:
        for audience in AUDIENCES:
            number = len(rows) + 1
            rows.append({
                "id": f"{category.lower()}-{number:03d}",
                "category": category,
                "title": f"{topic.title()} for {audience.title()}",
                "description": f"A practical {category.lower()} checklist for {audience}.",
            })
    return rows


def build_color_schemes():
    schemes = []
    variants = ("Aurora", "Ocean", "Dusk", "Forest", "Cosmic")
    for index in range(100):
        hue = (index * 0.61803398875) % 1.0
        h1 = colorsys.hsv_to_rgb(hue, 0.68, 0.30)
        h2 = colorsys.hsv_to_rgb((hue + 0.12) % 1.0, 0.72, 0.48)
        h3 = colorsys.hsv_to_rgb((hue + 0.54) % 1.0, 0.62, 0.42)
        colors = ["#%02x%02x%02x" % tuple(round(channel * 255) for channel in rgb) for rgb in (h1, h2, h3)]
        schemes.append({
            "id": f"scheme-{index + 1:03d}",
            "name": f"{variants[index % len(variants)]} {index + 1:03d}",
            "background": colors[0],
            "primary": colors[1],
            "accent": colors[2],
            "css": (
                f"radial-gradient(ellipse at 14% 12%, {colors[1]}70 0%, transparent 42%), "
                f"radial-gradient(ellipse at 86% 20%, {colors[2]}70 0%, transparent 44%), "
                f"linear-gradient(125deg, {colors[0]} 0%, #080b18 62%, {colors[2]} 135%)"
            ),
        })
    return schemes


def build_artwork_catalog(category_names):
    """Create distinct lightweight SVG illustrations locally without external image hosts."""
    symbols = ("✦", "⌂", "↗", "♧", "◈", "◎", "文", "♡", "⚖", "✈")
    art = []
    themes = build_color_schemes()
    for index in range(120):
        theme = themes[index % len(themes)]
        symbol = symbols[index % len(symbols)]
        category = category_names[index % len(category_names)]
        motif_index = index % 6
        if motif_index == 0:
            motif = (
                f'<path d="M{300 + index % 70} -30 L{510 + index % 90} 390" '
                'stroke="white" stroke-width="2" opacity=".22"/>'
                f'<path d="M{400 + index % 60} -30 L{610 + index % 50} 390" '
                'stroke="white" stroke-width="34" opacity=".08"/>'
            )
        elif motif_index == 1:
            motif = (
                f'<circle cx="{430 + index % 100}" cy="{70 + index % 160}" '
                f'r="{48 + index % 28}" fill="none" stroke="white" stroke-width="2" opacity=".28"/>'
                f'<circle cx="{430 + index % 100}" cy="{70 + index % 160}" '
                f'r="{82 + index % 34}" fill="none" stroke="white" stroke-width="1" opacity=".18"/>'
            )
        elif motif_index == 2:
            motif = (
                f'<path d="M320 310 Q{390 + index % 45} {150 + index % 70} '
                f'{455 + index % 55} 275 T640 210 V360 H320Z" '
                'fill="white" opacity=".10"/>'
            )
        elif motif_index == 3:
            motif = (
                f'<path d="M{360 + index % 40} 0 V360 M{430 + index % 45} 0 V360 '
                f'M500 0 V360 M570 0 V360" stroke="white" stroke-width="1" opacity=".15"/>'
                '<path d="M320 90 H640 M320 170 H640 M320 250 H640" '
                'stroke="white" stroke-width="1" opacity=".12"/>'
            )
        elif motif_index == 4:
            motif = (
                f'<path d="M{390 + index % 60} 35 l12 34 36 2-28 22 9 35-29-20-30 20 '
                '9-35-28-22 36-2Z" fill="white" opacity=".19"/>'
            )
        else:
            motif = (
                f'<ellipse cx="{480 + index % 80}" cy="{100 + index % 140}" '
                f'rx="{95 + index % 30}" ry="{35 + index % 22}" '
                'transform="rotate(-28 520 170)" fill="none" stroke="white" '
                'stroke-width="18" opacity=".10"/>'
            )
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360">'
            f'<defs><linearGradient id="g" x2="1" y2="1"><stop stop-color="{theme["primary"]}"/>'
            f'<stop offset="1" stop-color="{theme["accent"]}"/></linearGradient></defs>'
            '<rect width="640" height="360" rx="28" fill="url(#g)"/>'
            '<circle cx="520" cy="85" r="95" fill="#ffffff" opacity=".14"/>'
            '<circle cx="580" cy="280" r="120" fill="#ffffff" opacity=".10"/>'
            '<path d="M0 280 Q140 180 300 280 T640 240 V360 H0Z" fill="#07111f" opacity=".38"/>'
            f'{motif}'
            f'<text x="54" y="158" fill="white" font-size="82">{symbol}</text>'
            f'<text x="54" y="230" fill="white" font-size="27" font-family="sans-serif" font-weight="700">{html.escape(category)}</text>'
            '</svg>'
        )
        art.append({"id": f"art-{index + 1:03d}", "category": category, "svg": svg})
    return art


def catalog_csv(rows):
    output = io.StringIO(newline="")
    fields = ("id", "category", "title", "description")
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8-sig")
