# Restaurant Prioritization Dashboard — Demo Guide

> Prepared for the IS455 project demo. Covers the full context needed to walk stakeholders through the dashboard: what it does, how the numbers are calculated, and what each feature shows.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [Dataset at a Glance](#3-dataset-at-a-glance)
4. [KPI Cards — What We Highlight](#4-kpi-cards--what-we-highlight)
5. [The Priority Score — How It Is Calculated](#5-the-priority-score--how-it-is-calculated)
6. [The Four Segments — What They Mean & How We Classify Them](#6-the-four-segments--what-they-mean--how-we-classify-them)
7. [Why Only Rising & Hidden Gem Are Actionable](#7-why-only-rising--hidden-gem-are-actionable)
8. [Feature: Priority List](#8-feature-priority-list)
9. [Feature: Portfolio Map](#9-feature-portfolio-map)
10. [Feature: Segment Analysis](#10-feature-segment-analysis)
11. [Feature: Restaurant Explorer](#11-feature-restaurant-explorer)
12. [Sidebar Filters](#12-sidebar-filters)
13. [Unique Points to Highlight in the Demo](#13-unique-points-to-highlight-in-the-demo)

---

## 1. Project Overview

Hungry Hub has **3,727 restaurant partners** on its platform. The top 20% of partners generate **95.1% of total revenue**, which means the marketing team cannot afford to spray-and-pray across the entire portfolio. They need to know *which specific restaurants to invest in right now*.

This system uses a **machine learning pipeline** (LightGBM multiclass classifier) to assign every restaurant into one of four strategic segments, then computes a **priority score** to rank the ones worth acting on. The dashboard is the front-end interface for marketing teams to explore and action those insights.

---

## 2. Tech Stack

### ML Pipeline (Backend Data Generation)

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Data Cleaning | Python · Pandas · NumPy | Aggregation, GMV filtering, deduplication |
| Web Scraping | Apify (Google Maps actor) | External reputation data |
| Sentiment Analysis | VADER (NLTK) | NLP on Google Maps review text |
| Scoring | Custom min-max formulas | 3 composite scores → priority score |
| Feature Engineering | Pandas · NumPy · Scikit-learn | Encoding, ratios, OOF stacking |
| ML Classification | LightGBM · Stratified 5-Fold CV | Multiclass segment prediction (78.7% CV accuracy) |

### Dashboard (Frontend)

| Layer | Technology | Version |
|-------|-----------|---------|
| Framework | Next.js (App Router) | 15.x |
| Language | TypeScript | 5.x |
| Styling | Tailwind CSS | 3.x |
| Charts | Recharts | 2.x |
| UI Components | Radix UI primitives | — |
| Icons | Lucide React | — |
| Animations | Framer Motion | 12.x |
| Table utilities | TanStack Table | 8.x |
| Runtime | Node.js ≥ 22 | — |

> **How data flows into the dashboard:** The ML pipeline writes two CSV files (`Dashboard_List_1_Retention.csv` and `Dashboard_Predictions.csv`). A Next.js API route (`/api/dashboard`) reads and parses these CSVs at request time using **PapaParse** and serves them as a single JSON payload to the client.

---

## 3. Dataset at a Glance

| Metric | Value |
|--------|-------|
| Total restaurant partners | **3,727** |
| Revenue concentration | **95.1%** from top 20% of partners |
| Date range | Single aggregated snapshot |
| Google Maps coverage | 373 restaurants (10%) |
| NLP sentiment coverage | 323 restaurants (8.7%) |
| KOL data coverage | 196 restaurants (5.3%) |
| ML features used | **17** (fully leakage-free) |
| CV accuracy | **78.7%** (Stratified 5-Fold) |
| Actionable targets surfaced | **103** (80 Rising + 23 Hidden Gem) |

---

## 4. KPI Cards — What We Highlight

Six summary cards are displayed at the top of the dashboard, reacting live to sidebar filters:

| Card | What It Shows | Why It Matters |
|------|--------------|----------------|
| **Total** | Count of restaurants in current filter view | Shows scope of the selection |
| **Rising Stars ⚡** | Count of Rising-segment restaurants in view | Primary marketing investment targets |
| **Hidden Gems ◆** | Count of Hidden Gem restaurants in view | Exposure campaign targets |
| **Declining ⚠️** | Count of Declining restaurants in view | At-risk partners — not marketing targets |
| **Actionable 🎯** | Rising + Hidden Gem combined | The true action queue size |
| **Avg Score 📊** | Mean ML priority score across current view | Overall portfolio health indicator |

> **Key talking point:** "Actionable" is intentionally only 103 out of 3,727 — the system deliberately narrows focus to where marketing spend has the highest expected return.

---

## 5. The Priority Score — How It Is Calculated

The `ml_priority_score` (0–100 scale) is the final number used to rank all restaurants. It is built in two stages.

### Stage 1: Three Composite Scores (Rule-Based)

#### A. Internal Score — *Business Performance on Hungry Hub*
Measures how well the restaurant performs within the platform.

```
internal_raw  = log(1 + total_revenue) × 0.7 + log(1 + total_bookings) × 0.3
internal_score = min-max scale of internal_raw → 0–100
```

- Revenue weighted 70%, bookings 30% (revenue = direct business impact)
- Log transform compresses extreme outliers
- Coverage: **97.7%** of restaurants (near-universal)

#### B. Momentum Score — *KOL / Social Media Buzz*
Measures social media activity from Key Opinion Leader partnerships.

```
scaled_reach      = min-max scale of log(1 + kol_views)
scaled_engagement = min-max scale of log(1 + kol_likes + kol_comments)
momentum_score    = scaled_reach × 0.4 + scaled_engagement × 0.6
```

- Engagement (likes + comments) weighted higher than raw reach — quality over volume
- Coverage: **5.3%** (KOL data is sparse — most restaurants have no KOL activity)

#### C. External Quality Score — *Public Reputation*
Measures the restaurant's public-facing quality via Google Maps.

```
sentiment_rating = sentiment_score / 20     # converts 0–100 VADER score to 0–5 scale

w_gmaps = 0.6 × (1 if gmaps_rating > 0)    # dynamic: only counts if data exists
w_sens  = 0.4 × (1 if sentiment > 0)       # dynamic

composite = (gmaps_rating × w_gmaps + sentiment_rating × w_sens) / (w_gmaps + w_sens)
reliability_factor = log(1 + gmaps_review_count)   # more reviews = more trustworthy

external_quality_score = min-max scale of (composite × reliability_factor)
```

- **Dynamic weighting:** If a restaurant only has Google Maps data (no NLP sentiment), the 60% GMaps weight becomes 100% — it is not penalised for missing data.
- **Reliability factor:** A restaurant with 500 reviews is weighted more than one with 5, but with diminishing returns.
- Coverage: **10%** (only scraped restaurants)

### Stage 2: ML Priority Score (Model Output)

The LightGBM classifier produces class probabilities for all 4 segments per restaurant. The priority score combines the two **actionable** class probabilities:

```
ml_priority_score = (P(Rising) × 0.6 + P(Hidden Gem) × 0.4) × 100
```

- **Rising weighted higher (60%):** Rising partners need marketing investment to grow — the clearest ROI signal.
- **Hidden Gem (40%):** Needs a different strategy (exposure campaigns), still actionable.
- **Range:** 0–100. Top-ranked restaurants score ~58.5.
- Stable and Declining restaurants naturally score near 0 (low Rising/Hidden Gem probabilities).

---

## 6. The Four Segments — What They Mean & How We Classify Them

Segments are first assigned by **rule-based MECE labeling** (ground truth), then predicted by the **LightGBM ML model** for every restaurant (including ones the rules cannot reach).

### Rule-Based Labels (Ground Truth for ML Training)

Labels are assigned in strict priority order — the first matching rule wins (MECE: Mutually Exclusive, Collectively Exhaustive).

| Priority | Segment | Classification Rule | Business Meaning |
|----------|---------|---------------------|-----------------|
| 1 | **Hidden Gem** | `external_quality_score > 75th percentile` (among peers with data) AND `internal_score < 40th percentile` | High public quality, underperforming commercially — needs *exposure*, not operational fixes |
| 2 | **Declining** | `internal_score > 60th percentile` AND (`no_show_rate > 75th percentile` OR `avg_revenue_per_booking < 25th percentile`) | Historically strong but showing operational warning signs — needs ops attention, not marketing |
| 3 | **Rising** | `internal_score` between 25th–50th percentile AND `booking_conversion_rate > 0` | Mid-low performance base with measurable digital traction — prime marketing investment targets |
| 4 | **Stable** | All remaining | Performing within normal expectations — maintain current support |

**Why percentile-based thresholds?** Absolute numbers (e.g., "revenue > 500,000 THB") break across different restaurant sizes and data coverage. Percentiles adapt to the actual data distribution and use internal KPIs that are available for 97.7% of restaurants.

### ML Predicted Distribution (Final Output)

| Segment | Rule-Based Count | ML Predicted | Share |
|---------|-----------------|--------------|-------|
| Stable | 2,982 | 3,256 | 87.4% |
| Declining | 633 | 368 | 9.9% |
| **Rising** | 89 | **80** | **2.1%** |
| **Hidden Gem** | 23 | **23** | **0.6%** |

---

## 7. Why Only Rising & Hidden Gem Are Actionable

This is a key design decision worth emphasising in the demo.

**Marketing spend has the highest expected ROI on restaurants that are:**
- **Not already maxing out** — Stable restaurants are already performing well; extra marketing yields diminishing returns.
- **Not broken operationally** — Declining restaurants have high no-show rates or low per-booking revenue. Pouring marketing budget into a restaurant with operational problems will not fix those problems.
- **Showing latent potential** — Rising restaurants are converting web visitors to bookings (digital traction signal). Hidden Gems already have strong public reviews. Both have a clear, addressable gap between current performance and their potential.

```
Actionable = Rising + Hidden Gem = 80 + 23 = 103 restaurants
```

The dashboard's default filter (Priority List tab) shows only these 103. Marketing teams can toggle "Show all segments" if they need to see the full portfolio.

---

## 8. Feature: Priority List

**Tab:** Priority List | **Default view**

### What It Is
A ranked, paginated table showing the **103 actionable restaurants** (Rising + Hidden Gem), ordered by `ml_priority_score` descending — the direct action queue for the marketing team.

### What Each Column Shows

| Column | Explanation |
|--------|------------|
| **# (Rank)** | Priority ranking within the current filtered view |
| **Restaurant** | Name, cuisine type, and Bangkok zone |
| **Segment** | ML-predicted segment badge (Rising ⚡ / Hidden Gem ◆) |
| **Score** | `ml_priority_score` (0–100). Colour-coded: >70 = yellow, >40 = green, else grey |
| **P(Rising)** | Model's probability this restaurant is Rising — shown as a progress bar |
| **P(Hidden Gem)** | Model's probability this restaurant is a Hidden Gem — shown as a progress bar |
| **GMaps ★** | Google Maps star rating (dash if not scraped) |
| **Momentum** | KOL momentum score — social media buzz indicator |

### Additional Elements
- **Avg Score by Cuisine bar chart** — shows which cuisine type has the highest average priority score overall; the top cuisine is highlighted
- **Total Actionable counter** — large number showing Rising + Hidden Gem count in current filter
- **"Show all segments" toggle** — expands the table to include Stable and Declining
- **Export CSV button** — downloads the current view as `hungryhub_priority_list.csv` with rank, name, segment, score, cuisine, region, and probabilities

### Pagination
10 rows per page with full page navigation.

---

## 9. Feature: Portfolio Map

**Tab:** Portfolio Map

### What It Is
A bubble scatter plot that positions every restaurant in a two-dimensional risk/opportunity space, making the full portfolio visible at once.

### Axes & Encoding

| Dimension | Maps To | Interpretation |
|-----------|---------|---------------|
| **X-axis** | `expected_kpi` (internal performance score) | How well the restaurant performs inside Hungry Hub |
| **Y-axis** | `external_quality_score` | How well-regarded the restaurant is publicly (Google Maps + NLP) |
| **Bubble size** | `ml_priority_score` | Larger = higher ML priority score |
| **Colour** | `ML_Predicted_Segment` | Green=Rising, Purple=Hidden Gem, Red=Declining, Grey=Stable |

> Only restaurants with both `internal_score > 0` AND `external_quality_score > 0` are plotted (requires Google Maps data).

### Quadrant Interpretation

| Quadrant | Meaning |
|----------|---------|
| 🟢 **Top-Right** (high internal + high external) | Strong commercial performance + great public reputation → Cash Cows |
| 🟣 **Bottom-Right** (low internal + high external) | Great public reputation but underperforming commercially → **Hidden Gems** to invest in |
| 🔴 **Top-Left** (high internal + low external) | Strong internally but deteriorating public signals → At-Risk / Declining |
| ⚪ **Bottom-Left** (low internal + low external) | Average or early-stage → Stable / background noise |

### What to Say in the Demo
> "Each dot is a restaurant. Dots in the bottom-right corner are our Hidden Gems — they're loved publicly but not getting enough bookings through Hungry Hub. These are the ones where a targeted campaign on our platform can have a significant impact."

---

## 10. Feature: Segment Analysis

**Tab:** Segment Analysis

### What It Is
Three visualisations giving a high-level breakdown of the portfolio's health and composition.

### Component 1: Segment Distribution Donut Chart
A donut chart showing the count and percentage share of each segment in the current filtered view. Segments are colour-coded consistently across the whole dashboard.

### Component 2: Avg Priority Score by Cuisine Bar Chart
A horizontal bar chart ranking all cuisine types by their **average ML priority score**. The cuisine type with the highest average score is highlighted (labelled in the chart subtitle). Useful for identifying which food categories have the most concentrated marketing opportunity.

### Component 3: Segment Summary Table
A tabular breakdown showing, for each segment:

| Column | Description |
|--------|-------------|
| **Segment** | Colour-coded badge |
| **Count** | Absolute number of restaurants in this segment (within filter) |
| **Share** | Percentage of the filtered portfolio |
| **Avg Score** | Mean `ml_priority_score` for this segment |

The table renders in order: Rising → Hidden Gem → Stable → Declining (most-to-least-actionable).

### What to Say in the Demo
> "Even though only 2.7% of all restaurants are flagged as actionable, these are not random — the cuisine breakdown shows clear clusters where opportunity is concentrated. We can use this to target cuisine-specific campaigns."

---

## 11. Feature: Restaurant Explorer

**Tab:** Restaurant Explorer

### What It Is
A search-and-drill-down tool allowing stakeholders to look up any specific restaurant from the full 3,727-restaurant dataset and see its complete ML profile.

### How It Works
1. Type at least 2 characters into the search box — a real-time fuzzy dropdown shows up to 8 matching results
2. Each result shows the restaurant name, cuisine, region, and segment badge
3. Clicking a result populates a full **detail card**

### Detail Card: What It Contains

#### Header
- Restaurant name, segment badge, cuisine label, Bangkok zone

#### Priority Score
- Large numeric display of `ml_priority_score` (e.g., `42.3`)
- Overall portfolio rank (e.g., `Rank #7`)

#### Prediction Confidence Section
Four progress bars showing the model's class probability breakdown:

| Bar | Colour | What It Means |
|-----|--------|--------------|
| **P(Rising)** | Green | Probability this is a Rising restaurant |
| **P(Hidden Gem)** | Violet | Probability this is a Hidden Gem |
| **P(Stable)** | Slate | Probability this is Stable |
| **P(Declining)** | Red | Probability this is Declining |

The bars always sum to 100%. A restaurant classified as Rising with 90% confidence is a very different priority target from one at 51%.

#### Business Metrics Section
Four KPI tiles (shown only if data is available):

| Metric | Unit | Notes |
|--------|------|-------|
| **Revenue** | ฿ (Thai Baht) | Total GMV on Hungry Hub |
| **Bookings** | Count | Total confirmed bookings |
| **No-Show Rate** | % | Percentage of bookings that were no-shows |
| **GMaps Rating** | Stars (0–5) | Google Maps star rating |

### What to Say in the Demo
> "If a sales manager wants to understand why a specific restaurant is ranked #7, they can search for it here and see the confidence breakdown. A restaurant with 70% Rising probability is a very different story from one at 52% — the explorer makes that visible."

---

## 12. Sidebar Filters

The sidebar (always visible on desktop, accessible via the burger menu on mobile) contains global filters that affect **all four tabs simultaneously**.

| Filter | Type | Effect |
|--------|------|--------|
| **Segment** | Multi-select checkboxes | Show/hide restaurants by ML segment |
| **Region** | Multi-select checkboxes | Filter by Bangkok zone (CBD, Sukhumvit, Silom/Sathon, Riverside, North/Ari, Ratchada/Rama9, Outer Bangkok, Provincial, Other) |
| **Cuisine** | Multi-select checkboxes | Filter by primary cuisine type |
| **Min Priority Score** | Slider | Set a floor on `ml_priority_score` — useful to focus only on the highest-confidence targets |

The sidebar also shows a persistent **Active Segments** overview panel with live counts for all four segments.

---

## 13. Unique Points to Highlight in the Demo

### 1. The Actionable Funnel
> From **3,727 total restaurants** → the system identifies **103 worth marketing to right now**. That's a 97% reduction in scope with a principled, ML-backed justification for every exclusion.

### 2. MECE Segmentation
Every restaurant falls into exactly one segment. There are no overlaps and no uncategorised restaurants. The priority ordering ensures Hidden Gems (rarest, highest value) are identified first.

### 3. Dynamic Weighting for Sparse Data
90% of restaurants have no Google Maps data. Rather than marking those as "bad", the scoring formula dynamically adjusts weights — a restaurant is only evaluated on the signals available to it. This prevents the sparsity of external data from systematically penalising restaurants that are simply hard to scrape.

### 4. Leakage-Free ML Training
The ML model never sees the internal operational metrics (revenue, bookings, no-show rate) used to construct the labels. It predicts from observable, external signals only. This means the predictions are deployable in scenarios where internal data is unavailable or stale.

### 5. Export-Ready for Downstream Use
The Priority List tab exports a clean CSV (`hungryhub_priority_list.csv`) with ranks, names, segments, scores, cuisine, region, and model probabilities. This is ready to be handed to a campaign manager or imported into a CRM.

### 6. CV Accuracy of 78.7%
The honest, unbiased metric. Measured via Stratified 5-Fold cross-validation to ensure all 4 segments (including minority classes with as few as 23 samples) are represented in every evaluation fold.

---

*Dashboard running at: `http://localhost:6006` · ML Pipeline v3 · Built with Next.js 15 & LightGBM*
