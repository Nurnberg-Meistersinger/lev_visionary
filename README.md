# The Visionary

The Visionary — an AI platform for automatic content aggregation and analysis: collects information from RSS sources and X/Twitter, processes it through the Claude API, and sends digests to Telegram.

---

## Project Structure

| Project | Source | What it does |
| --- | --- | --- |
| `project_a16z` | a16z Daily Newsletter | Downloads fresh articles, generates TL;DR + summary |
| `project_techcrunch_startup` | TechCrunch Startups | TL;DR + summary for startup publications |
| `project_techcrunch_venture` | TechCrunch Venture | TL;DR + summary for the Venture section |
| `project_twitter` | X/Twitter | Selects important tweets by account groups, analyzes via LLM |

---

## Quick Start

1. Python 3.12+ and virtual environment:

   ```bash
   python -m venv .the_vis && source ./.the_vis/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Fill in `.env` (see section [Configuration](#configuration-env))

4. Run:

   ```bash
   python visionary.py run --all
   ```

---

## CLI

```bash
# All projects
python visionary.py run --all

# Twitter by account sets
python visionary.py run --twitter --palantir
python visionary.py run --twitter --cypherpunk
python visionary.py run --twitter --blockchain
python visionary.py run --twitter --venture
python visionary.py run --twitter --entrepreneurs
python visionary.py run --twitter --hackers
python visionary.py run --twitter --lifestyle
python visionary.py run --twitter --protectorium
python visionary.py run --twitter --ycombinator
python visionary.py run --twitter --all  # top-2 from each set

# Individual projects
python visionary.py run --a16z
python visionary.py run --techcrunch_startup
python visionary.py run --techcrunch_venture
```

---

## Telegram Bot

The bot allows running all projects remotely via Telegram (requires a VPS).

### Commands

```bash
# Twitter digests
/digest palantir          — Palantir digest (top-10)
/digest blockchain        — Blockchain digest
/digest entrepreneurs     — Entrepreneurs digest
/digest hackers           — Hackers digest
/digest lifestyle         — Lifestyle digest
/digest protectorium      — Protectorium digest
/digest venture           — Venture digest
/digest ycombinator       — Y Combinator digest
/digest cypherpunk        — Cypherpunk digest
/digest all               — top-2 from each Twitter category

# Other projects
/digest a16z              — a16z Daily Newsletter
/digest techcrunch_startup    — TechCrunch Startups
/digest techcrunch_venture    — TechCrunch Venture

# Custom account sets
/newset <name> handle1 handle2 ...  — create a custom set
/addto <name> handle1 handle2 ...   — add accounts to a set
/delset <name>                      — delete a custom set

# Information
/projects                 — list of all projects (built-in + custom)
/help                     — help
```

### Running the bot on a VPS

```bash
cd the_visionary
source .venv/bin/activate
python -m project_twitter.bot
```

---

## `.env` Configuration

```env
# Claude API (Anthropic)
LLM_MODEL=claude-haiku-4-5-20251001
LLM_API_KEY=sk-ant-api03-...

# Telegram
TELEGRAM_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=-100xxxxxxxxxx

# Twitter (for project_twitter)
TWITTER_USERNAME=your_twitter_handle
TWITTER_EMAIL=your_email@example.com
TWITTER_PASSWORD=your_password

# Bot admin (for management via Telegram)
ADMIN_USER_ID=your_telegram_user_id

# Automatic digest schedule (optional)
SCHEDULE_ENABLED=true
SCHEDULE_TIME=18:00
SCHEDULE_TIMEZONE=Europe/Moscow
```

Timezones: `Europe/Moscow`, `UTC`, `Europe/Berlin`, `Asia/Tbilisi`, etc. (IANA standard).

### Getting keys

- **Claude API**: register at [console.anthropic.com](https://console.anthropic.com), top up balance from USD 5
- **Telegram**:
  - Create a bot via [@BotFather](https://t.me/BotFather), get `TELEGRAM_TOKEN`
  - Create a channel, add the bot as an administrator, get `TELEGRAM_CHAT_ID` (e.g., `-100xxxxxxxxxx`)
  - Find out your `ADMIN_USER_ID` via [@userinfobot](https://t.me/userinfobot)
- **Twitter**: credentials from an account (a separate account is recommended)

---

## Scheduled Auto-start

With `SCHEDULE_ENABLED=true`, the bot automatically runs all projects **sequentially** every day at the specified time and sends a report to the administrator:

```text
📅 Scheduled digest completed

✅ a16z
✅ techcrunch_startup
✅ techcrunch_venture
✅ twitter/palantir
✅ twitter/blockchain
...

✅ 12  ❌ 0  ⏱ ~24 min
```

Order: first three RSS projects (a16z, TechCrunch ×2) with a 60-second delay between them, then all Twitter sets with a 90-second delay. Manual `/digest` commands work independently.

---

## Twitter Account Sets

Built-in sets — files in `project_twitter/account_sets/*.json`:

```json
{
  "name": "Palantir",
  "description": "Palantir leadership and close communities",
  "accounts": [
    {"handle": "PalantirTech", "name": "Palantir Technologies"},
    {"handle": "ssankar", "name": "Shankar Sankar, Palantir, CTO"}
  ]
}
```

Custom sets are created via the bot (`/newset`) or manually — it is enough to add a JSON with the `"custom": true` flag. They automatically appear in `/projects` and participate in `/digest all`.

---

## LLM and Prompts

All projects use the Claude API (`anthropic`). Prompts:

- `project_*/summarizer.py` — TL;DR and summary for articles
- `project_twitter/llm_filter.py` — analysis and selection of important tweets

### Tweet selection criteria

The LLM evaluates each tweet on a scale of 0–10:

- Specific news: announcements, deals, partnerships, releases
- Insider information from company executives
- Analytics with numbers and metrics
- Strategic forecasts from experts

Not selected: retweets without comments, personal opinions without facts, jokes, memes.

---

## Cost

Claude Haiku 4.5: ~USD 0.25 per 1M input tokens, ~USD 1.25 per 1M output tokens.
With typical usage (several digests per day): **~USD 3–6/month**.

---

## Solution Analytical Passport

### 1. Task Context

**For whom:** an individual user or a small team that follows news in the fields of technology, the venture market, startups, and crypto/blockchain.

**Business context:** daily monitoring of 10+ sources takes 1–2 hours: you need to open several sites, scroll through the Twitter feed, select what is relevant, and read it. A significant portion of the content is irrelevant or of low quality.

**Task being solved:** automatically aggregate, filter, and summarize content from target sources, delivering a ready-made digest to Telegram.

---

### 2. Problem and Goal

**Pain / problem:**

- Manual news monitoring takes 60–120 minutes/day
- High "noise": the majority of publications carry no significant information
- Sources are fragmented: RSS feeds, Twitter, newsletters — each with its own interface
- There is no single place for content consumption

**Goal:** reduce monitoring time to 10–15 minutes/day through automatic aggregation and LLM summarization.

**KPIs:**

- Average digest reading time: ≤ 15 min/day
- Coverage of key sources: 4+ sources daily
- Fault tolerance: ≥ 95% successful daily runs
- LLM cost: ≤ USD 10/month

---

### 3. Constraints

| Category | Description |
| --- | --- |
| **Security** | Credentials (Twitter, Telegram, Claude API) are stored locally in `.env`, not committed to the repository |
| **Twitter ToS** | Automatic collection of tweets via `twikit` may violate X/Twitter rules at high request frequencies |
| **Rate limits** | Twitter limits the request rate — 90-second delays between sets are mandatory |
| **Budget** | Claude Haiku — minimum cost among Claude models; at current volume ~USD 3–6/month |
| **Infrastructure** | A VPS is required for 24/7 bot operation; a minimal server (1 CPU, 512 MB RAM) is sufficient |
| **External API dependency** | Failures of the Anthropic API or Telegram API interrupt the digest |

---

### 4. Architecture

#### 4.1 Data Flow Diagram

```text
Data sources
     │
     ├── RSS: a16z Newsletter ──────────────────────┐
     ├── RSS: TechCrunch Startups ──────────────────┤
     ├── RSS: TechCrunch Venture ───────────────────┤
     └── X/Twitter (twikit scraping) ───────────────┤
                                                     │
                                            Data collection layer
                                          (rss_reader / tc_reader /
                                            fetcher.py + twikit)
                                                     │
                                            Deduplication
                                          (processed_posts.json /
                                           processed_news.json)
                                                     │
                                            AI layer (Claude API)
                                          ┌──────────┴──────────┐
                                    Summarization          LLM filtering
                                   (summarizer.py)      (llm_filter.py)
                                    TL;DR + summary       top-N tweets
                                                     │
                                            Result delivery
                                          (telegram_sender.py)
                                                     │
                                         Telegram channel / DM
```

#### 4.2 Data Sources

| Source | Method | Format | Module |
| --- | --- | --- | --- |
| a16z Newsletter | feedparser (RSS) | Atom/RSS XML | `project_a16z/rss_reader.py` |
| TechCrunch Startups | feedparser (RSS) | Atom/RSS XML | `project_techcrunch_startup/tc_reader.py` |
| TechCrunch Venture | feedparser (RSS) | Atom/RSS XML | `project_techcrunch_venture/tc_reader.py` |
| X/Twitter | twikit (web scraping) | JSON (Twitter internal API) | `project_twitter/fetcher.py` |

#### 4.3 Automation Layer

- **Scheduler**: built-in job_queue from the `python-telegram-bot[job-queue]` library — daily run at a specified time (IANA timezone)
- **Triggers**: schedule (`SCHEDULE_ENABLED`) + manual commands via the Telegram bot (`/digest`)
- **Orchestrator**: `visionary.py run --all` for running from the CLI
- **Delays**: 60 sec between RSS projects, 90 sec between Twitter sets (rate limit protection)

#### 4.4 AI Layer

| Task | Module | Description |
| --- | --- | --- |
| Article summarization | `project_*/summarizer.py` | TL;DR (2 sentences), summary (5–7 sentences), 4–5 bullet points |
| Article ranking | `project_*/article_ranker.py` | Relevance scoring before summarization |
| Tweet filtering | `project_twitter/llm_filter.py` | Importance scoring 0–10, top-N selection, summary + insights generation |

Model: `claude-haiku-4-5-20251001` (configurable via `LLM_MODEL` in `.env`).

#### 4.5 Data Storage

| Data | Format | Location | Purpose |
| --- | --- | --- | --- |
| Processed article URLs | JSON (list of strings) | `project_*/processed_news.json` | Deduplication — an article is processed only once |
| Processed tweet IDs | JSON (list of strings) | `project_twitter/processed_posts.json` | Tweet deduplication |
| Custom account sets | JSON (object) | `project_twitter/account_sets/*.json` | Set description: name, accounts, custom flag |
| Twitter session | JSON (cookies) | `project_twitter/cookies.json` | Authorization without re-login |
| Configuration | `.env` | project root | All secrets and settings |

#### 4.6 Delivery Channels

- **Telegram channel**: main digest delivery channel (`TELEGRAM_CHAT_ID`)
- **Administrator DM**: report on scheduled run (`ADMIN_USER_ID`)
- **Telegram bot**: interactive management via commands

#### 4.7 Roles and Access

| Role | Access | Tool |
| --- | --- | --- |
| Administrator | All bot commands, receives reports | Telegram (`ADMIN_USER_ID`) |
| Channel reader | Read digests only | Telegram channel |
| System | Automatic scheduled runs | job_queue on VPS |

---

### 5. Scenario Descriptions

#### Scenario 1: Daily auto-digest on schedule

**Description:** every day at the specified time, the bot runs all projects sequentially and sends digests to the channel + a report to the administrator.

**Input data:** none (trigger — time by IANA timezone)

**Logic:**

1. Job scheduler fires at `SCHEDULE_TIME`
2. RSS projects are run: a16z → 60-sec delay → TechCrunch Startup → 60-sec delay → TechCrunch Venture
3. Twitter sets are run: each with a 90-sec delay
4. Errors are logged, they do not interrupt other projects
5. Final report is sent to the administrator

**Output:** a series of Telegram messages in the channel + a final report in the administrator's DM

---

#### Scenario 2: Digest by Telegram command

**Description:** the administrator manually runs the desired digest via `/digest <project>`.

**Input data:** Telegram command `/digest palantir` (or another project name)

**Logic:**

1. The bot checks `user_id == ADMIN_USER_ID` (otherwise — `⛔ Access denied`)
2. Parses the argument: Twitter set or another project
3. Sends status `⏳ Running: palantir...`
4. Runs `process_set_async(set_name, top_n=10)`
5. Upon completion updates status: `✅ Palantir digest sent to channel!`

**Output:** digest in the channel + updated status message in chat

---

#### Scenario 3: RSS summarization (a16z / TechCrunch)

**Description:** the agent reads the RSS feed, filters new articles, parses HTML, summarizes via Claude.

**Input data:** RSS feed URL (configured in `config.py` of each project)

**Logic:**

1. `rss_reader.py` / `tc_reader.py` — get the list of articles from RSS
2. Check `processed_news.json` — skip already processed ones
3. `article_parser.py` — extract text from the HTML page
4. `article_ranker.py` — evaluate relevance (optional)
5. `summarizer.py` → Claude API — generate TL;DR + summary + bullet points
6. `telegram_sender.py` — format and send to the channel
7. Save URL to `processed_news.json`

**Output:** Telegram message of the form:

```text
📰 Article title

💡 TL;DR: two sentences about the main point

📋 Summary: 5-7 sentences with key ideas

• Point 1
• Point 2
• ...

🔗 Read in full
```

---

#### Scenario 4: Twitter digest with LLM filtering

**Description:** collect tweets from a set of accounts, select important ones via LLM, send the digest.

**Input data:** account set JSON file (`account_sets/palantir.json`)

**Logic:**

1. `fetcher.py` — authenticate via twikit (cookies), get tweets from each account for the last N hours
2. Exclude already processed ones (post_tracker.py)
3. `llm_filter.py` → Claude API — evaluate each tweet (0–10), select top-N
4. `telegram_sender.py` — form and send the digest

**Output:** Telegram message with a list of selected tweets:

```text
🐦 Palantir Digest

1. Palantir contract with NATO for USD 500M
   📊 Summary: ...
   • Fact 1
   • Fact 2
   🔗 twitter.com/...

2. ...
```

---

#### Scenario 5: Managing custom account sets

**Description:** the administrator creates, edits, and deletes custom Twitter account sets via the bot.

**Commands and logic:**

| Command | Action | Result |
| --- | --- | --- |
| `/newset crypto elonmusk naval` | Creates `account_sets/crypto.json` with `"custom": true` | Confirmation + list of accounts |
| `/addto crypto pmarca` | Adds `pmarca` to the existing file | List of added + total |
| `/delset crypto` | Deletes the file (custom only) | Deletion confirmation |
| `/digest crypto` | Runs digest for the new set | Digest in the channel |

---

### 6. Prompt Engineering

#### 6.1 Prompt for article summarization (`summarizer.py`)

**Type:** zero-shot with strict output format (JSON)

```text
You are a professional technology news editor. Analyze the article and return ONLY JSON:

{
  "tldr": "2 sentences in Russian (max 200 characters)",
  "summary": "5-7 sentences in Russian with key ideas",
  "bullet_points": [
    "Point 1 (max 100 characters)",
    ...
  ]
}

REQUIREMENTS:
- TLDR: exactly 2 sentences, maximum 200 characters
- Summary: 5-7 sentences with key ideas
- Bullet points: strictly 4-5 points, each up to 100 characters
- All text ONLY in Russian
- NO markdown blocks
- ONLY a valid JSON object!

ARTICLE: {article text}
```

**Parameters:** `max_tokens=2048`, `temperature` — model default

---

#### 6.2 Prompt for LLM tweet filtering (`llm_filter.py`)

**Type:** few-shot with examples of good/bad responses, strict JSON output

```text
You are an analytical AI that studies tweets in the fields of technology, startups, and blockchain.

1. Evaluate the importance of each tweet on a scale of 0–10
   Importance criteria:
   - Specific news: product announcements, deals, partnerships, releases
   - Insider information: data from company executives
   - Analytics with figures: statistics, metrics, financial indicators
   - Strategic forecasts from industry experts

   Do NOT select: retweets without comments, personal opinions without facts, jokes, memes.

2. Select exactly {top_n} most important tweets (importance >= 6).

3. For each selected tweet provide (ALL IN RUSSIAN):
   • summary: 2–3 sentences (up to 300 characters)
   • insights: 2–3 key facts (each up to 100 characters)
   • short_tldr: the main essence in one phrase (up to 100 characters)

     GOOD examples of short_tldr:
     - "Palantir contract with NATO for USD 500M"
     - "AIP launch for commercial clients in Europe"

4. Return strictly JSON: { "important": [ {...} ] }
```

**Parameters:** `max_tokens=4096`, `temperature=0` (deterministic result)

---

### 7. Data and Data Model

#### 7.1 Stored Data

**`processed_news.json`** (project_a16z, project_techcrunch_*)

```json
["https://a16z.com/article-1", "https://techcrunch.com/article-2"]
```

List of URLs of already processed articles. Updated after each successful processing.

**`processed_posts.json`** (project_twitter)

```json
["1234567890", "9876543210"]
```

List of tweet IDs. Prevents repeated processing.

**`account_sets/*.json`** (project_twitter)

```json
{
  "name": "Palantir",
  "description": "Palantir leadership and close communities",
  "custom": false,
  "accounts": [
    {"handle": "PalantirTech", "name": "Palantir Technologies"},
    {"handle": "ssankar",      "name": "Shankar Sankar, CTO"}
  ]
}
```

Flag `"custom": true` — marks a custom set created via the bot.

**`cookies.json`** (project_twitter)
twikit Twitter session. Used for authorization without re-entering credentials.

#### 7.2 Data Retention Policy

- All data is stored locally on the server, in the project directory
- `processed_*.json` — not cleared automatically; to reset if needed — delete the file manually
- `cookies.json` — recreated automatically when the session expires
- Credentials in `.env` are never committed to git (`.gitignore`)
- Digests are not stored — they are sent to Telegram and saved no further

---

### 8. Ethics and Security

#### 8.1 Sensitive Data

| Data | Where stored | Sensitivity level |
| --- | --- | --- |
| `LLM_API_KEY` (Anthropic) | `.env` | High — leak = unauthorized charges |
| `TELEGRAM_TOKEN` | `.env` | High — leak = interception of bot control |
| `TWITTER_PASSWORD` | `.env` | High — leak = account compromise |
| `ADMIN_USER_ID` | `.env` | Medium — determines who controls the bot |
| `cookies.json` | file on server | Medium — active Twitter session |

#### 8.2 Protection Measures

- `.env` is added to `.gitignore` — not committed to the repository
- Access to bot commands — only for `ADMIN_USER_ID` (`@admin_only` decorator)
- Deletion of custom sets is protected: built-in sets cannot be deleted via the bot
- A separate Twitter account (not personal) is recommended for the system to operate

#### 8.3 Potential Risks

| Risk | Description | Mitigation |
| --- | --- | --- |
| Twitter ban | Automatic collection violates X/Twitter ToS | Delays between requests, separate account |
| Credentials leak | Compromise of `.env` or server | Store `.env` outside the repository, use keys with minimal permissions |
| False analytics | LLM may incorrectly rank tweets | Review results, tune prompts |
| API expenses | Volume growth → cost growth | Monitor usage in Anthropic Console |

---

### 9. Economics and Effect

#### 9.1 Labor Costs Before/After

| Activity | Before (manual) | After (automatic) |
| --- | --- | --- |
| Twitter monitoring | 30–60 min/day | 0 min (automatic) |
| Reading news (a16z, TC) | 20–40 min/day | 5–10 min (digest only) |
| Total per day | **60–120 min** | **5–15 min** |
| Total per month | **30–60 hours** | **2.5–7.5 hours** |

> Savings: ~50–55 hours/month

#### 9.2 Cost

| Item | Cost |
| --- | --- |
| Claude Haiku API | ~USD 3–6/month (with typical usage) |
| VPS (minimal) | ~USD 3–5/month |
| **Total** | **~USD 6–11/month** |

#### 9.3 Expected Effect

- **Speed**: time for daily monitoring is reduced by 4–10 times
- **Quality**: LLM filtering removes "noise" — only significant materials remain
- **Coverage**: the system monitors sources 24/7, missing no publications
- **Scalability**: adding a new source — create a JSON file with accounts

#### 9.4 Implementation Plan (2–3 weeks)

| Stage | Duration | Actions |
| --- | --- | --- |
| **1. Preparation** | 1–2 days | Get API keys (Claude, Telegram), create a separate Twitter account |
| **2. Deployment** | 1 day | Clone the repository, configure `.env`, run the bot on VPS |
| **3. Configuration** | 3–5 days | Add the required Twitter sets, configure schedule time, test |
| **4. Operation** | ongoing | Monitor operation, add new sources as needed |

---

### 10. Technology Stack

| Component | Technology | Version |
| --- | --- | --- |
| Language | Python | 3.12+ |
| LLM | Claude Haiku (Anthropic) | claude-haiku-4-5-20251001 |
| Telegram bot | python-telegram-bot | 21.10 |
| Twitter scraping | twikit | 2.3.3 |
| RSS parsing | feedparser | 6.0.12 |
| HTML parsing | BeautifulSoup4 + lxml | 4.14.3 / 6.0.2 |
| Configuration | python-dotenv | 1.2.1 |
| Scheduler | PTB job_queue (APScheduler) | built into PTB 21.x |
| Requests | requests | 2.32.5 |
| Data storage | JSON files | — |
| Deployment | VPS + systemd / screen | — |
