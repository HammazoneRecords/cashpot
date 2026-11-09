#!/usr/bin/env python3
"""
Cash Pot Prediction Engine — 100 mathematical strategies + superstition/metaphysical layer.

Layers:
  1. MATH (100 strategies): frequency, hot/cold, cycles, patterns, Markov chains,
     day-of-week bias, draw-slot bias, gap analysis, moving averages, etc.
  2. DOMAIN: element patterns, domain rotation, energy cycles, planetary.
  3. SUPERSTITION: dream book correlation, African diaspora energy, number pairing.
  4. ROOT REDUCTION: single-digit root (1-9) analysis, DOW dominance, gap tracking.
  5. TIME SERIES: multi-step forecasting, confidence decay, day pattern matching.
  6. ASTRO: moon phase, planetary ruler, planetary hour, void-of-course.
  F-01. MOMENTUM: live feedback loop — strategies that score hits get boosted.

Commands: predict | root | reading | strategies | forecast | accuracy | moon |
          json | strategy | domain | dream | momentum | backtest | help

Output: ranked predictions with confidence scores and reasoning.
"""

import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from itertools import combinations

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from dream_book import (DREAM_BOOK, ALL_DOMAINS, DOMAIN_NUMBERS, ELEMENT_NUMBERS, ENERGY_NUMBERS)

DRAW_ORDER = ["Early Bird", "Morning", "Midday", "Mid-Afternoon", "Drivetime", "Evening"]
DOWS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# ── Root Reduction (1-9) ──
ROOT_NUMBERS = {}
for n in range(1, 37):
    if n < 10:
        root = n
    else:
        root = n // 10 + n % 10
        if root >= 10:
            root = root // 10 + root % 10
    ROOT_NUMBERS.setdefault(root, []).append(n)
NUMBER_ROOT = {n: r for r, nums in ROOT_NUMBERS.items() for n in nums}

ROOT_NAMES = {1: "Leader", 2: "Balancer", 3: "Creator", 4: "Builder",
              5: "Changer", 6: "Nurturer", 7: "Seeker", 8: "Power", 9: "Completer"}

# DOW → strongest root (from 3,370-draw data — updated 2026-06-22)
# Tuesday R5 = 65x vs 53.3 (+11.7), Friday R4 = 62x vs 52.7 (+9.3), Sunday R4 = 65x vs 54.7 (+10.3)
DOW_STRONG_ROOT = {"Tuesday": 5, "Friday": 4, "Sunday": 4}
DOW_MODERATE_ROOT = {"Monday": 5, "Wednesday": 4, "Thursday": 3, "Saturday": 2}


def load_results():
    path = os.path.join(SCRIPT_DIR, 'cash_pot_results.json')
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_json(filename):
    path = os.path.join(SCRIPT_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def load_momentum():
    """Load strategy momentum from file (F-01)."""
    path = os.path.join(SCRIPT_DIR, 'strategy_momentum.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"strategies": {}, "last_updated": None, "total_hits": 0, "total_misses": 0}


def save_momentum(data):
    path = os.path.join(SCRIPT_DIR, 'strategy_momentum.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════
#  LAYER 1: 100 MATH STRATEGIES
# ═══════════════════════════════════════════════════════════════

class MathStrategies:
    def __init__(self, records):
        self.records = sorted(records, key=lambda r: r['draw_number'])
        self.numbers = [r['number'] for r in self.records]
        self.dates = [r['date'] for r in self.records]
        self.draw_names = [r['draw_name'] for r in self.records]
    
    # --- Frequency-based (strategies 1-15) ---
    
    def s01_overall_frequency(self):
        """Most common numbers overall."""
        c = Counter(self.numbers)
        return sorted(c.most_common(), key=lambda x: (-x[1], x[0]))
    
    def s02_cold_numbers(self):
        """Least common numbers — due to appear."""
        c = Counter(self.numbers)
        return sorted(c.most_common(), key=lambda x: (x[1], x[0]))
    
    def s03_hot_streak(self, window=10):
        """Numbers that appeared most in last N draws."""
        c = Counter(self.numbers[-window:])
        return sorted(c.most_common(), key=lambda x: (-x[1], x[0]))
    
    def s04_cold_streak(self, window=30):
        """Numbers that appeared least in last N draws."""
        recent = set(self.numbers[-window:])
        return [(n, 0) for n in range(1, 37) if n not in recent]
    
    def s05_frequency_momentum(self):
        """Numbers whose frequency is increasing (last 30 vs prior 30)."""
        if len(self.numbers) < 60:
            return []
        prior = Counter(self.numbers[-60:-30])
        recent = Counter(self.numbers[-30:])
        momentum = []
        for n in range(1, 37):
            diff = recent.get(n, 0) - prior.get(n, 0)
            if diff > 0:
                momentum.append((n, diff))
        return sorted(momentum, key=lambda x: -x[1])
    
    def s06_frequency_decline(self):
        """Numbers whose frequency is declining — may rest."""
        if len(self.numbers) < 60:
            return []
        prior = Counter(self.numbers[-60:-30])
        recent = Counter(self.numbers[-30:])
        decline = []
        for n in range(1, 37):
            diff = prior.get(n, 0) - recent.get(n, 0)
            if diff > 0:
                decline.append((n, diff))
        return sorted(decline, key=lambda x: -x[1])
    
    # --- Gap analysis (strategies 7-20) ---
    
    def s07_longest_gap(self):
        """Numbers with the longest gap since last appearance."""
        last_seen = {}
        for i, n in enumerate(self.numbers):
            last_seen[n] = i
        gaps = []
        for n in range(1, 37):
            if n in last_seen:
                gap = len(self.numbers) - 1 - last_seen[n]
                gaps.append((n, gap))
            else:
                gaps.append((n, len(self.numbers)))
        return sorted(gaps, key=lambda x: -x[1])
    
    def s08_median_gap(self):
        """Numbers with gap exceeding their median gap."""
        gaps = defaultdict(list)
        last = {}
        for i, n in enumerate(self.numbers):
            if n in last:
                gaps[n].append(i - last[n])
            last[n] = i
        
        result = []
        for n in range(1, 37):
            if n in gaps and len(gaps[n]) >= 5:
                g = sorted(gaps[n])
                median = g[len(g) // 2]
                current_gap = len(self.numbers) - 1 - last.get(n, len(self.numbers))
                if current_gap > median * 1.5:
                    result.append((n, current_gap, median))
        return sorted(result, key=lambda x: -(x[1] - x[2]))
    
    def s09_expected_soon(self):
        """Numbers whose current gap is close to their average gap."""
        gaps = defaultdict(list)
        last = {}
        for i, n in enumerate(self.numbers):
            if n in last:
                gaps[n].append(i - last[n])
            last[n] = i
        
        result = []
        for n in range(1, 37):
            if n in gaps and len(gaps[n]) >= 3:
                avg_gap = sum(gaps[n]) / len(gaps[n])
                current_gap = len(self.numbers) - 1 - last.get(n, 0)
                if current_gap >= avg_gap * 0.8 and current_gap <= avg_gap * 1.3:
                    result.append((n, current_gap, round(avg_gap, 1)))
        return sorted(result, key=lambda x: x[1] / max(x[2], 1), reverse=True)
    
    def s10_repeat_pattern(self):
        """Numbers that often repeat within short spans (cluster)."""
        clusters = defaultdict(int)
        for i in range(1, len(self.numbers)):
            if self.numbers[i] == self.numbers[i-1]:
                clusters[self.numbers[i]] += 1
        return sorted(clusters.items(), key=lambda x: -x[1])
    
    # --- Day-of-week patterns (strategies 11-17) ---
    
    def s11_dow_frequency(self, day_name):
        """Most common numbers on a specific day of week."""
        day_nums = [r['number'] for r in self.records if r['day_of_week'] == day_name]
        if not day_nums:
            return []
        c = Counter(day_nums)
        return sorted(c.most_common(), key=lambda x: (-x[1], x[0]))
    
    def s12_dow_unseen(self, day_name):
        """Numbers that haven't appeared on a given day in 4+ weeks."""
        recent = set()
        for r in self.records[-28*6:]:
            if r['day_of_week'] == day_name:
                recent.add(r['number'])
        return [(n, 0) for n in range(1, 37) if n not in recent]
    
    def s13_weekend_vs_weekday(self):
        """Numbers that prefer weekends (Sat/Sun) over weekdays."""
        weekend = Counter(r['number'] for r in self.records if r['day_of_week'] in ('Saturday', 'Sunday'))
        weekday = Counter(r['number'] for r in self.records if r['day_of_week'] not in ('Saturday', 'Sunday'))
        bias = []
        for n in range(1, 37):
            wend = weekend.get(n, 0)
            wday = weekday.get(n, 0)
            if wend + wday > 3:
                ratio = wend / max(wday, 1)
                bias.append((n, round(ratio, 2), wend, wday))
        return sorted(bias, key=lambda x: -x[1])
    
    # --- Draw-slot patterns (strategies 14-20) ---
    
    def s14_slot_frequency(self, draw_name):
        """Most common numbers in a specific draw slot."""
        slot_nums = [r['number'] for r in self.records if r['draw_name'] == draw_name]
        if not slot_nums:
            return []
        c = Counter(slot_nums)
        return sorted(c.most_common(), key=lambda x: (-x[1], x[0]))
    
    def s15_slot_hot(self, draw_name, window=30):
        """Hot numbers in a specific slot over last N appearances."""
        slot = [r['number'] for r in self.records if r['draw_name'] == draw_name]
        if not slot:
            return []
        c = Counter(slot[-window:])
        return sorted(c.most_common(), key=lambda x: (-x[1], x[0]))
    
    # --- Sequence/pair patterns (strategies 16-30) ---
    
    def s16_frequent_pairs(self, top_n=20):
        """Most common number pairs (any order, any distance)."""
        pairs = Counter()
        for i in range(len(self.numbers) - 1):
            a, b = sorted([self.numbers[i], self.numbers[i+1]])
            pairs[(a, b)] += 1
        return sorted(pairs.most_common(top_n), key=lambda x: -x[1])
    
    def s17_consecutive_draw_pair(self):
        """Most common consecutive draw number pairs."""
        pairs = Counter()
        for i in range(len(self.numbers) - 1):
            pairs[(self.numbers[i], self.numbers[i+1])] += 1
        return sorted(pairs.most_common(15), key=lambda x: -x[1])
    
    def s18_followers(self, target_num):
        """What numbers most often follow a specific number."""
        followers = Counter()
        for i in range(len(self.numbers) - 1):
            if self.numbers[i] == target_num:
                followers[self.numbers[i+1]] += 1
        return sorted(followers.most_common(10), key=lambda x: -x[1])
    
    def s19_leaders(self, target_num):
        """What numbers most often precede a specific number."""
        leaders = Counter()
        for i in range(1, len(self.numbers)):
            if self.numbers[i] == target_num:
                leaders[self.numbers[i-1]] += 1
        return sorted(leaders.most_common(10), key=lambda x: -x[1])
    
    def s20_same_day_repeats(self):
        """Numbers that often repeat within the same day."""
        by_date = defaultdict(list)
        for r in self.records:
            by_date[r['date']].append(r['number'])
        repeats = Counter()
        for nums in by_date.values():
            seen = set()
            for n in nums:
                if n in seen:
                    repeats[n] += 1
                seen.add(n)
        return sorted(repeats.most_common(10), key=lambda x: -x[1])
    
    def s21_triple_patterns(self, top_n=10):
        """Most common 3-number sequences."""
        triples = Counter()
        for i in range(len(self.numbers) - 2):
            triples[(self.numbers[i], self.numbers[i+1], self.numbers[i+2])] += 1
        return sorted(triples.most_common(top_n), key=lambda x: -x[1])
    
    # --- Cycle detection (strategies 22-28) ---
    
    def s22_number_cycle(self, target_num):
        """Find the average gap cycle for a specific number."""
        gaps = []
        last_idx = None
        for i, n in enumerate(self.numbers):
            if n == target_num:
                if last_idx is not None:
                    gaps.append(i - last_idx)
                last_idx = i
        if not gaps:
            return None, None
        return sum(gaps) / len(gaps), gaps[-1] if gaps else None
    
    def s23_due_by_cycle(self):
        """Numbers that are due based on their personal cycle."""
        result = []
        for n in range(1, 37):
            avg, current = self.s22_number_cycle(n)
            if avg and current and current >= avg * 1.2:
                result.append((n, round(current), round(avg, 1)))
        return sorted(result, key=lambda x: x[1] / max(x[2], 1), reverse=True)
    
    def s24_moving_average_crossover(self, short=7, long=21):
        """Numbers where short-term frequency crosses above long-term."""
        if len(self.numbers) < long * 2:
            return []
        short_c = Counter(self.numbers[-short:])
        long_c = Counter(self.numbers[-long:])
        cross = []
        for n in range(1, 37):
            s_freq = short_c.get(n, 0) / short
            l_freq = long_c.get(n, 0) / long
            if s_freq > l_freq * 1.3:
                cross.append((n, round(s_freq, 3), round(l_freq, 3)))
        return sorted(cross, key=lambda x: -(x[1] - x[2]))
    
    # --- Parity and range (strategies 25-35) ---
    
    def s25_odd_even_balance(self):
        """Predict next draw's parity based on recent balance."""
        recent = self.numbers[-20:]
        odd_count = sum(1 for n in recent if n % 2 == 1)
        even_count = len(recent) - odd_count
        expected_parity = 'odd' if even_count > odd_count else 'even'
        matching = [n for n in range(1, 37) if (n % 2 == 1) == (expected_parity == 'odd')]
        return matching, expected_parity, odd_count, even_count
    
    def s26_low_mid_high(self):
        """Distribution of low(1-12), mid(13-24), high(25-36) in last 30."""
        recent = self.numbers[-30:]
        low = sum(1 for n in recent if n <= 12)
        mid = sum(1 for n in recent if 13 <= n <= 24)
        high = sum(1 for n in recent if n >= 25)
        lowest = min(low, mid, high)
        if lowest == low:
            target_range = list(range(1, 13))
            label = 'low (1-12)'
        elif lowest == mid:
            target_range = list(range(13, 25))
            label = 'mid (13-24)'
        else:
            target_range = list(range(25, 37))
            label = 'high (25-36)'
        return target_range, label, low, mid, high
    
    def s27_sum_trend(self):
        """Trend of sum of last N draws."""
        windows = [3, 5, 10, 20]
        result = {}
        for w in windows:
            if len(self.numbers) >= w * 2:
                prev_sum = sum(self.numbers[-(w*2):-w])
                curr_sum = sum(self.numbers[-w:])
                result[w] = {'prev': prev_sum, 'curr': curr_sum, 'trend': 'up' if curr_sum > prev_sum else 'down'}
        return result
    
    # --- Mirror and complement (strategies 28-35) ---
    
    def s28_mirror_numbers(self):
        """Numbers whose mirror (37-n) has been hitting."""
        recent_10 = set(self.numbers[-10:])
        mirrors = []
        for n in recent_10:
            mirror = 37 - n
            if mirror != n and mirror >= 1 and mirror <= 36:
                if mirror not in recent_10:
                    mirrors.append((mirror, n))
        return mirrors
    
    def s29_position_pairing(self):
        """Numbers that appear at the same draw position across days."""
        by_slot = defaultdict(list)
        for r in self.records:
            by_slot[r['draw_name']].append(r['number'])
        result = {}
        for slot, nums in by_slot.items():
            if len(nums) >= 5:
                c = Counter(nums[-10:])
                result[slot] = c.most_common(3)
        return result
    
    def s30_monthly_hot(self):
        """Hottest numbers in the current month vs overall."""
        if not self.records:
            return []
        current_month = self.records[-1]['date'][:7]
        month_nums = [r['number'] for r in self.records if r['date'].startswith(current_month)]
        overall = Counter(self.numbers)
        month_c = Counter(month_nums)
        result = []
        for n in range(1, 37):
            m_freq = month_c.get(n, 0) / max(len(month_nums), 1)
            o_freq = overall.get(n, 0) / max(len(self.numbers), 1)
            if m_freq > o_freq * 1.5 and month_c.get(n, 0) >= 2:
                result.append((n, round(m_freq * 100, 1), round(o_freq * 100, 1)))
        return sorted(result, key=lambda x: -(x[1] - x[2]))


# ═══════════════════════════════════════════════════════════════
#  LAYER 1.5: TIME SERIES ANALYSIS (Southwest)
# ═══════════════════════════════════════════════════════════════

class TimeSeriesAnalysis:
    """Multi-step forecasting and temporal pattern detection."""
    
    def __init__(self, records):
        self.records = sorted(records, key=lambda r: r['draw_number'])
        self.numbers = [r['number'] for r in self.records]
        self.dates = [r['date'] for r in self.records]
    
    def s31_multi_step_trend(self, lookback=60):
        """S31: ARIMA-style trend per number — score rising numbers."""
        if len(self.numbers) < lookback * 2:
            return []
        prior = Counter(self.numbers[-lookback*2:-lookback])
        recent = Counter(self.numbers[-lookback:])
        trends = []
        for n in range(1, 37):
            p = prior.get(n, 0) / max(lookback, 1)
            r = recent.get(n, 0) / max(lookback, 1)
            if r > p * 1.2:
                trends.append((n, round(r - p, 3), round(r * 100, 1)))
        return sorted(trends, key=lambda x: -x[1])
    
    def s32_confidence_decay(self, steps_ahead, base_confidence=0.95):
        """S32: Confidence multiplier drops per step into future."""
        decay = base_confidence - (steps_ahead - 1) * 0.05
        return max(decay, 0.35)
    
    def s33_slot_trend(self, slot_name, window=30):
        """S33: Per-slot trend — is a draw slot trending high or low?"""
        slot_nums = [r['number'] for r in self.records if r['draw_name'] == slot_name]
        if len(slot_nums) < window * 2:
            return None, []
        prev_avg = sum(slot_nums[-window*2:-window]) / window
        curr_avg = sum(slot_nums[-window:]) / window
        trend = "up" if curr_avg > prev_avg * 1.05 else ("down" if curr_avg < prev_avg * 0.95 else "flat")
        return trend, slot_nums[-window:]
    
    def s34_day_pattern(self, recent_draws=3, top_matches=5):
        """S34: Match today's pattern against history."""
        if len(self.numbers) < recent_draws + 30:
            return []
        today = tuple(self.numbers[-recent_draws:])
        followers = Counter()
        for i in range(len(self.numbers) - recent_draws - 1):
            window = tuple(self.numbers[i:i+recent_draws])
            if window == today and i + recent_draws < len(self.numbers):
                followers[self.numbers[i+recent_draws]] += 1
        return followers.most_common(top_matches)


# ═══════════════════════════════════════════════════════════════
#  LAYER 2: DOMAIN & ELEMENT ANALYSIS
# ═══════════════════════════════════════════════════════════════

class DomainAnalysis:
    def __init__(self, records):
        self.records = records
        self.all_numbers = [r['number'] for r in records]
    
    def element_distribution(self, window=None):
        """Which elements are most/least common recently."""
        nums = self.all_numbers[-window:] if window else self.all_numbers
        el_count = Counter()
        for n in nums:
            el_count[DREAM_BOOK[n]['element']] += 1
        return el_count.most_common()
    
    def element_due(self):
        """Elements that are underrepresented recently."""
        total = Counter()
        recent = Counter()
        half = len(self.all_numbers) // 2
        for n in self.all_numbers[:half]:
            total[DREAM_BOOK[n]['element']] += 1
        for n in self.all_numbers[half:]:
            recent[DREAM_BOOK[n]['element']] += 1
        
        due = []
        for el in ['Fire', 'Water', 'Earth', 'Air', 'Metal', 'Wood']:
            diff = recent.get(el, 0) / max(half, 1) - total.get(el, 0) / max(half, 1)
            if diff < -0.02:
                due.append((el, ELEMENT_NUMBERS.get(el, []), round(diff, 3)))
        return sorted(due, key=lambda x: x[2])
    
    def domain_rotation(self, window=6):
        """Track which domains appeared in last N draws, predict rotation."""
        recent_domains = Counter()
        for r in self.records[-window:]:
            for dom in r.get('domains', []):
                recent_domains[dom] += 1
        
        # Domains that haven't appeared recently
        missing = []
        all_appearing = set()
        for r in self.records[-window:]:
            all_appearing.update(r.get('domains', []))
        
        for dom in ALL_DOMAINS:
            if dom not in all_appearing:
                nums = DOMAIN_NUMBERS.get(dom, [])
                missing.append((dom, nums))
        
        return sorted(missing, key=lambda x: len(x[1]), reverse=True)[:10]
    
    def domain_daily_presence(self, date_str):
        """Check which domains appeared on a specific date."""
        day_records = [r for r in self.records if r['date'] == date_str]
        domains = set()
        for r in day_records:
            domains.update(r.get('domains', []))
        return list(domains)
    
    def domain_streak(self, domain_name):
        """How many consecutive draws has a domain appeared."""
        streak = 0
        for r in reversed(self.records):
            if domain_name in r.get('domains', []):
                streak += 1
            else:
                break
        return streak
    
    def energy_shift(self):
        """Detect shifts in energy types (from dream book energies)."""
        recent_energies = Counter()
        for r in self.records[-30:]:
            recent_energies[DREAM_BOOK[r['number']]['energy']] += 1
        return recent_energies.most_common()


# ═══════════════════════════════════════════════════════════════
#  LAYER 3: SUPERSTITION / METAPHYSICAL
# ═══════════════════════════════════════════════════════════════

class SuperstitionLayer:
    def __init__(self, records):
        self.records = records
    
    def dream_pairing(self, number):
        """Find numbers whose dream meanings relate to a given number."""
        target_domains = set(DREAM_BOOK[number]['domains'])
        target_element = DREAM_BOOK[number]['element']
        
        related = []
        for n in range(1, 37):
            if n == number:
                continue
            d = DREAM_BOOK[n]
            shared_domains = target_domains & set(d['domains'])
            same_element = 1 if d['element'] == target_element else 0
            score = len(shared_domains) * 2 + same_element * 3
            if score > 0:
                related.append((n, score, list(shared_domains)))
        return sorted(related, key=lambda x: -x[1])
    
    def opposite_forces(self, number):
        """Find the opposing/complementary number based on elements."""
        el = DREAM_BOOK[number]['element']
        opposites = {
            'Fire': 'Water', 'Water': 'Fire',
            'Earth': 'Air', 'Air': 'Earth',
            'Metal': 'Wood', 'Wood': 'Metal',
        }
        opp_el = opposites.get(el, '')
        return ELEMENT_NUMBERS.get(opp_el, [])
    
    def ancestor_numbers(self):
        """Numbers connected to ancestral/spirit energy — Duppy, Dead, Parson, etc."""
        spirit_domains = ['Spirit/Ancestor', 'Spirit/Religion', 'Spirit/Occult', 'Spirit/Ritual', 'Spirit/God']
        numbers = set()
        for domain in spirit_domains:
            numbers.update(DOMAIN_NUMBERS.get(domain, []))
        return sorted(numbers)
    
    def money_numbers(self):
        """Numbers connected to wealth, gold, money."""
        money_domains = ['Money/Wealth', 'Commerce/Business', 'Gambling']
        numbers = set()
        for domain in money_domains:
            numbers.update(DOMAIN_NUMBERS.get(domain, []))
        return sorted(numbers)
    
    def birth_numbers(self):
        """Numbers connected to birth, children, new beginnings."""
        birth_domains = ['Birth/Children', 'Pregnancy/Birth', 'Youth/Children']
        numbers = set()
        for domain in birth_domains:
            numbers.update(DOMAIN_NUMBERS.get(domain, []))
        return sorted(numbers)
    
    def death_numbers(self):
        """Numbers connected to death, endings, transformation."""
        death_domains = ['Death/Ending', 'Death/Mourning', 'Death/Burial']
        numbers = set()
        for domain in death_domains:
            numbers.update(DOMAIN_NUMBERS.get(domain, []))
        return sorted(numbers)
    
    def dream_correlation(self, dream_text):
        """Given dream keywords, find which numbers match."""
        dream_lower = dream_text.lower()
        scores = {}
        for n, d in DREAM_BOOK.items():
            score = 0
            for word in dream_lower.split():
                if word in d['major'].lower():
                    score += 3
                if word in d['minor'].lower():
                    score += 1
            if score > 0:
                scores[n] = score
        return sorted(scores.items(), key=lambda x: -x[1])
    
    def diaspora_reading(self):
        """Today's African diaspora energy reading based on recent draws."""
        recent = self.records[-12:] if len(self.records) >= 12 else self.records
        elements = Counter(DREAM_BOOK[r['number']]['element'] for r in recent)
        planets = Counter(DREAM_BOOK[r['number']]['planet'] for r in recent)
        
        dominant_el = elements.most_common(1)[0][0]
        dominant_planet = planets.most_common(1)[0][0]
        
        interpretations = {
            ('Water', 'Moon'): "Oshun/Yemaya energy flowing — emotion, intuition, abundance from the depths.",
            ('Fire', 'Mars'): "Shango's fire active — justice, transformation through heat, warrior energy rising.",
            ('Earth', 'Saturn'): "Ancestral grounding — the bones speaking. Patience and structure needed.",
            ('Air', 'Mercury'): "Eshu at the crossroads — communication, choice, trickster wisdom.",
            ('Metal', 'Sun'): "Ogun's iron — cutting through obstacles, technology, clear path forward.",
        }
        
        return {
            'dominant_element': dominant_el,
            'dominant_planet': dominant_planet,
            'reading': interpretations.get((dominant_el, dominant_planet), f"{dominant_el} energy with {dominant_planet} influence — read the signs carefully."),
            'elements': elements.most_common(),
        }


# ═══════════════════════════════════════════════════════════════
#  LAYER 3.5: ASTRO / PLANETARY (Northeast)
# ═══════════════════════════════════════════════════════════════

def moon_phase(date_obj):
    """Calculate moon phase (0-7) for a given date. Pure math — no API."""
    import math as _math
    y, m, d = date_obj.year, date_obj.month, date_obj.day
    if m < 3:
        y -= 1
        m += 12
    a = int(y / 100)
    b = int(a / 4)
    c = 2 - a + b
    e = int(365.25 * (y + 4716))
    f = int(30.6001 * (m + 1))
    jd = c + d + e + f - 1524.5
    days_since_new = jd - 2451549.5
    new_moons = days_since_new / 29.53
    phase = (new_moons - int(new_moons)) * 29.53
    if phase < 1.84566:
        return "New Moon"
    elif phase < 5.53699:
        return "Waxing Crescent"
    elif phase < 9.22831:
        return "First Quarter"
    elif phase < 12.91963:
        return "Waxing Gibbous"
    elif phase < 16.61096:
        return "Full Moon"
    elif phase < 20.30228:
        return "Waning Gibbous"
    elif phase < 23.99361:
        return "Last Quarter"
    else:
        return "Waning Crescent"

MOON_PHASES = ["New Moon", "Waxing Crescent", "First Quarter",
               "Waxing Gibbous", "Full Moon", "Waning Gibbous",
               "Last Quarter", "Waning Crescent"]

PLANETARY_RULERS = {
    "Monday": "Moon", "Tuesday": "Mars", "Wednesday": "Mercury",
    "Thursday": "Jupiter", "Friday": "Venus", "Saturday": "Saturn", "Sunday": "Sun",
}

PLANETARY_HOURS_ORDER = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]

def planetary_hour(date_obj, hour):
    """Calculate planetary hour for a given date and hour."""
    # Sunrise approx 6am — first planetary hour = day ruler
    if hour < 6:
        return None
    hour_index = (hour - 6) % 7
    return PLANETARY_HOURS_ORDER[hour_index]

class AstroAnalysis:
    """S35-S38: Astro/planetary strategies using existing dream_book data."""
    
    def __init__(self, records):
        self.records = records
    
    def s35_moon_phase(self, target_date=None):
        """S35: Numbers historically hot in current moon phase."""
        if target_date is None:
            target_date = datetime.now()
        current = moon_phase(target_date)
        phase_nums = Counter()
        for r in self.records:
            rd = datetime.strptime(r['date'], '%Y-%m-%d')
            if moon_phase(rd) == current:
                phase_nums[r['number']] += 1
        return current, phase_nums.most_common(6)
    
    def s35b_moon_direction(self, target_date=None):
        """S35b: Numbers that prefer Waxing vs Waning based on current direction."""
        if target_date is None:
            target_date = datetime.now()
        current = moon_phase(target_date)
        # Determine waxing vs waning
        waxing_phases = {"New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous"}
        is_waxing = current in waxing_phases
        
        waxing_counter = Counter()
        waning_counter = Counter()
        for r in self.records:
            rd = datetime.strptime(r['date'], '%Y-%m-%d')
            phase = moon_phase(rd)
            if phase in waxing_phases:
                waxing_counter[r['number']] += 1
            else:
                waning_counter[r['number']] += 1
        
        result = []
        for n in range(1, 37):
            w = waxing_counter.get(n, 0)
            wa = waning_counter.get(n, 0)
            total = w + wa
            if total < 5:
                continue
            wax_ratio = w / total
            # If currently waxing, boost numbers that prefer waxing
            if is_waxing and wax_ratio > 0.55:
                result.append((n, round(wax_ratio * 100), "waxing"))
            elif not is_waxing and wax_ratio < 0.45:
                result.append((n, round((1 - wax_ratio) * 100), "waning"))
        return current, is_waxing, sorted(result, key=lambda x: -x[1])[:6]
    
    def s35c_full_moon_proximity(self, target_date=None):
        """S35c: Score numbers based on distance to nearest Full/New Moon."""
        if target_date is None:
            target_date = datetime.now()
        # Moon age in days (0-29.53)
        y, m, d = target_date.year, target_date.month, target_date.day
        if m < 3:
            y -= 1; m += 12
        a = int(y / 100); b = int(a / 4); c = 2 - a + b
        jd = c + d + int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) - 1524.5
        moon_age = ((jd - 2451549.5) / 29.53) % 1 * 29.53
        # Days to nearest full moon (age ~14.77) and new moon (age ~0 or ~29.53)
        to_full = abs(moon_age - 14.77)
        to_new = min(moon_age, abs(moon_age - 29.53))
        proximity = min(to_full, to_new)
        moon_context = "full" if to_full < to_new else "new"
        return round(moon_age, 1), round(proximity, 1), moon_context
    
    def s36_planetary_ruler(self, dow):
        """S36: Boost numbers whose dream_book planet matches day's ruler."""
        ruler = PLANETARY_RULERS.get(dow, "Sun")
        matches = []
        for n in range(1, 37):
            if DREAM_BOOK[n]['planet'] == ruler:
                matches.append(n)
        return ruler, matches
    
    def s37_planetary_hour(self, draw_slot):
        """S37: Map draw slot to planetary hour — boost matching numbers."""
        slot_hours = {"Early Bird": 8, "Morning": 10, "Midday": 13,
                       "Mid-Afternoon": 15, "Drivetime": 17, "Evening": 20}
        hour = slot_hours.get(draw_slot, 12)
        p_hour = planetary_hour(datetime.now(), hour)
        if not p_hour:
            return None, []
        matches = [n for n in range(1, 37) if DREAM_BOOK[n]['planet'] == p_hour]
        return p_hour, matches
    
    def s38_void_of_course(self):
        """S38: Moon VOC — penalty to Water element numbers (traditional)."""
        return ELEMENT_NUMBERS.get("Water", [])


# ═══════════════════════════════════════════════════════════════
#  LAYER 4: ROOT REDUCTION (1-9)
# ═══════════════════════════════════════════════════════════════

class RootReduction:
    """Root (1-9) analysis layer. Compresses 36 numbers into 9 roots."""
    
    def __init__(self, records):
        self.records = sorted(records, key=lambda r: r['draw_number'])
        self.numbers = [r['number'] for r in self.records]
        self.roots = [NUMBER_ROOT[n] for n in self.numbers]
        
        # Load pre-computed data
        self.root_gaps = load_json('root_gaps.json')
        self.root_freq = load_json('root_frequency.json')
        self.root_seqs = load_json('root_sequences.json')
        self.clustering = load_json('root_number_dow_clustering.json')
        
        # Calculate current root gaps
        self._current_gaps = self._calc_current_gaps()
    
    def _calc_current_gaps(self):
        """How many draws since each root last appeared."""
        gaps = {}
        total = len(self.roots)
        for r in range(1, 10):
            last_seen = None
            for i in range(total - 1, -1, -1):
                if self.roots[i] == r:
                    last_seen = i
                    break
            if last_seen is not None:
                gaps[r] = total - 1 - last_seen
            else:
                gaps[r] = total
        return gaps
    
    def root_of(self, number):
        return NUMBER_ROOT.get(number, number)
    
    def numbers_for_root(self, root):
        return ROOT_NUMBERS.get(root, [])
    
    def root_gap_status(self):
        """All roots with current gap and status."""
        result = []
        for r in range(1, 10):
            gap = self._current_gaps.get(r, 0)
            avg_gap = 8.9  # average gap across all roots
            if self.root_gaps and str(r) in self.root_gaps.get('gap_stats', {}):
                avg_gap = self.root_gaps['gap_stats'][str(r)].get('mean_gap', 8.9)
            
            status = "DUE" if gap > avg_gap else "normal"
            if gap > avg_gap * 1.3:
                status = "OVERDUE"
            
            result.append({
                'root': r,
                'name': ROOT_NAMES.get(r, ''),
                'numbers': ROOT_NUMBERS.get(r, []),
                'current_gap': gap,
                'avg_gap': round(avg_gap, 1),
                'status': status,
            })
        return sorted(result, key=lambda x: x['current_gap'], reverse=True)
    
    def dow_root_boost(self, dow):
        """Get root boost numbers for a specific DOW."""
        boost = []
        
        # STRONG signal — boost hard
        strong_root = DOW_STRONG_ROOT.get(dow)
        if strong_root:
            for n in ROOT_NUMBERS.get(strong_root, []):
                boost.append((n, 2, f"DOW strong: {dow} favours Root {strong_root} ({ROOT_NAMES[strong_root]})"))
        
        # MODERATE signal — boost lightly
        mod_root = DOW_MODERATE_ROOT.get(dow)
        if mod_root:
            for n in ROOT_NUMBERS.get(mod_root, []):
                boost.append((n, 1, f"DOW moderate: {dow} leans Root {mod_root} ({ROOT_NAMES[mod_root]})"))
        
        return boost
    
    def root_pair_transition(self, last_number):
        """Given last draw's number, return most likely next roots."""
        last_root = self.root_of(last_number)
        # From data: top transitions
        transitions = self.root_seqs.get('top_root_pairs', []) if self.root_seqs else []
        
        followers = Counter()
        for pair, count in transitions:
            if pair[0] == last_root:
                followers[pair[1]] += count
        
        return followers.most_common(5)
    
    def score_root_layer(self, score_fn, target_dow=None):
        """Apply all root-based scoring.
        
        R-02: Root gap scoring — overdue roots get boost
        R-03: Root DOW scoring — DOW-dominant roots get boost
        R-04: Root number clustering — root numbers ABOVE expected on this DOW get boost
        R-05: Root number avoidance — root numbers BELOW expected on this DOW get penalty
        """
        # R-02: Root gap scoring
        for entry in self.root_gap_status():
            r = entry['root']
            if entry['status'] == 'OVERDUE':
                for n in ROOT_NUMBERS.get(r, []):
                    score_fn(n, 2, f"Root {r} ({ROOT_NAMES[r]}) OVERDUE: gap {entry['current_gap']} vs avg {entry['avg_gap']}", "R02-RootGap")
            elif entry['status'] == 'DUE':
                for n in ROOT_NUMBERS.get(r, []):
                    score_fn(n, 1, f"Root {r} ({ROOT_NAMES[r]}) due: gap {entry['current_gap']}", "R02-RootGap")
        
        # R-03: DOW root scoring
        if target_dow:
            for num, pts, reason in self.dow_root_boost(target_dow):
                score_fn(num, pts, reason, "R03-RootDOW")
        
        # R-04 + R-05: Root number DOW clustering/avoidance
        if target_dow and self.clustering:
            per_dow = self.clustering.get('per_dow', {}).get(target_dow, {})
            
            # R-04: Cluster boosts
            for entry in per_dow.get('boost', []):
                for n in entry.get('numbers', []):
                    score_fn(n, entry['boost'], f"Root {entry['root']} ({entry['name']}) clusters on {target_dow} (+{entry['boost']})", "R04-Cluster")
            
            # R-05: Avoid penalties
            for entry in per_dow.get('avoid', []):
                for n in entry.get('numbers', []):
                    score_fn(n, entry['penalty'], f"Root {entry['root']} ({entry['name']}) avoids {target_dow} ({entry['penalty']})", "R05-Avoid")
        
        # Root pair transition from last draw
        if len(self.numbers) >= 1:
            last_num = self.numbers[-1]
            for next_root, count in self.root_pair_transition(last_num)[:3]:
                for n in ROOT_NUMBERS.get(next_root, []):
                    score_fn(n, 1, f"Root {self.root_of(last_num)}->{next_root} pair ({count}x)", "R-RootPair")
    
    def root_prediction(self, top_n=3):
        """Predict the most likely roots with their numbers.
        Used by the --root CLI flag.
        """
        gap_status = self.root_gap_status()
        
        # Score each root: gap severity + pair transition + DOW
        root_scores = defaultdict(lambda: {'score': 0, 'reasons': []})
        today_dow = datetime.now().strftime('%A') if self.records else None
        
        for entry in gap_status:
            r = entry['root']
            if entry['status'] == 'OVERDUE':
                root_scores[r]['score'] += 3
                root_scores[r]['reasons'].append(f"OVERDUE: gap {entry['current_gap']} vs avg {entry['avg_gap']}")
            elif entry['status'] == 'DUE':
                root_scores[r]['score'] += 1
                root_scores[r]['reasons'].append(f"DUE: gap {entry['current_gap']}")
        
        # DOW boost
        if today_dow:
            strong = DOW_STRONG_ROOT.get(today_dow)
            if strong:
                root_scores[strong]['score'] += 2
                root_scores[strong]['reasons'].append(f"DOW strong: {today_dow} favours Root {strong}")
            mod = DOW_MODERATE_ROOT.get(today_dow)
            if mod:
                root_scores[mod]['score'] += 1
                root_scores[mod]['reasons'].append(f"DOW moderate: {today_dow} leans Root {mod}")
        
        # Pair transition
        if len(self.numbers) >= 1:
            last_num = self.numbers[-1]
            for next_root, count in self.root_pair_transition(last_num)[:2]:
                root_scores[next_root]['score'] += 1
                root_scores[next_root]['reasons'].append(f"Follows Root {self.root_of(last_num)} ({count}x)")
        
        ranked = sorted(root_scores.items(), key=lambda x: -x[1]['score'])
        
        result = []
        for root, data in ranked[:top_n]:
            result.append({
                'root': root,
                'name': ROOT_NAMES.get(root, ''),
                'numbers': ROOT_NUMBERS.get(root, []),
                'score': data['score'],
                'reasons': data['reasons'],
            })
        return result


# ═══════════════════════════════════════════════════════════════
#  PREDICTION ENGINE (combines all layers)
# ═══════════════════════════════════════════════════════════════

class PredictionEngine:
    def __init__(self, records):
        self.math = MathStrategies(records)
        self.domain = DomainAnalysis(records)
        self.superstition = SuperstitionLayer(records)
        self.root = RootReduction(records)
        self.timeseries = TimeSeriesAnalysis(records)
        self.astro = AstroAnalysis(records)
        self.records = records
        self.momentum = load_momentum()
    
    def run_full_prediction(self, top_n=10, target_dow=None, modifier=1.0, target_date=None):
        """Run all strategies and aggregate into ranked predictions.
        
        target_dow: 'Monday'|... — enables DOW-specific root strategies
        modifier: global weight multiplier (0.5-3.0) — year-modifier for era shifts
        target_date: datetime for moon/astro (default: now)
        """
        scores = defaultdict(lambda: {'total': 0, 'reasons': []})
        
        def score(num, points, reason, strategy_name):
            scaled = round(points * modifier)  # apply global modifier
            if scaled == 0 and points != 0:
                scaled = 1 if points > 0 else -1  # don't zero out non-zero weights
            scores[num]['total'] += scaled
            scores[num]['reasons'].append(f"[{strategy_name}] {reason}")

        # --- MATH STRATEGIES (weights 1-3) ---
        
        # S01: Overall frequency
        for num, count in self.math.s01_overall_frequency()[:10]:
            score(num, 2, f"Top 10 overall: {count}x", "S01-Freq")
        
        # S02: Cold numbers (due)
        for num, count in self.math.s02_cold_numbers()[:10]:
            score(num, 3, f"Cold number due: only {count}x", "S02-Cold")
        
        # S03: Hot streak
        for num, count in self.math.s03_hot_streak(10)[:5]:
            score(num, 2, f"Hot in last 10: {count}x", "S03-HotStreak")
        
        # S04: Cold streak
        for num, _ in self.math.s04_cold_streak(30)[:5]:
            score(num, 3, f"Not seen in last 30 draws", "S04-ColdStreak")
        
        # S05: Momentum
        for num, diff in self.math.s05_frequency_momentum()[:8]:
            score(num, 1, f"Momentum +{diff}", "S05-Momentum")
        
        # S07: Longest gap
        for num, gap in self.math.s07_longest_gap()[:10]:
            score(num, 3, f"Gap of {gap} draws", "S07-Gap")
        
        # S09: Expected soon by cycle
        for num, current, avg in self.math.s09_expected_soon()[:8]:
            score(num, 2, f"Due by cycle: gap {current} vs avg {avg}", "S09-Cycle")
        
        # S10: Repeat pattern
        for num, count in self.math.s10_repeat_pattern()[:5]:
            score(num, 1, f"Often repeats: {count}x", "S10-Repeat")
        
        # S16: Frequent pairs
        for (a, b), count in self.math.s16_frequent_pairs(20):
            score(a, 1, f"Frequent pair with {b}", "S16-Pairs")
            score(b, 1, f"Frequent pair with {a}", "S16-Pairs")
        
        # S17: Consecutive pairs
        last_num = self.records[-1]['number']
        for next_num, count in self.math.s18_followers(last_num):
            score(next_num, 2, f"Often follows {last_num}: {count}x", "S18-Follower")
        
        # S20: Same-day repeats
        for num, count in self.math.s20_same_day_repeats()[:5]:
            score(num, 2, f"Often repeats same day: {count}x", "S20-SameDay")
        
        # S23: Due by personal cycle
        for num, current, avg in self.math.s23_due_by_cycle()[:8]:
            score(num, 2, f"Cycle: gap {current} vs avg {avg}", "S23-Personal")
        
        # S24: Moving average crossover
        for num, short_f, long_f in self.math.s24_moving_average_crossover()[:5]:
            score(num, 1, f"Short-term rising: {short_f} vs {long_f}", "S24-MACross")
        
        # S26: Low/Mid/High balance
        target_range, label, _, _, _ = self.math.s26_low_mid_high()
        for n in target_range:
            score(n, 1, f"Range balance favors {label}", "S26-Range")
        
        # S28: Mirror numbers
        for mirror, original in self.math.s28_mirror_numbers():
            score(mirror, 1, f"Mirror of recent #{original}", "S28-Mirror")
        
        # S30: Monthly hot
        for num, m_freq, o_freq in self.math.s30_monthly_hot()[:5]:
            score(num, 1, f"This month hot: {m_freq}% vs {o_freq}%", "S30-Monthly")
        
        # --- DOMAIN/SUPERSTITION (weights 1-3) ---
        
        # Element due
        for el, nums, diff in self.domain.element_due():
            for n in nums[:6]:
                score(n, 1, f"Element {el} underrepresented ({diff})", "D01-Element")
        
        # Domain rotation
        for dom, nums in self.domain.domain_rotation(12)[:5]:
            for n in nums[:3]:
                score(n, 2, f"Domain '{dom}' hasn't appeared recently", "D02-Domain")
        
        # --- ROOT REDUCTION LAYER (R-02 gap + R-03 DOW) ---
        self.root.score_root_layer(score, target_dow=target_dow)

        # --- TIME SERIES LAYER (S31-S34, Southwest) ---
        for num, trend, pct in self.timeseries.s31_multi_step_trend()[:6]:
            score(num, 2, f"Trend rising: +{trend} ({pct}%)", "S31-MultiStep")
        for num, count in self.timeseries.s34_day_pattern(3, 6):
            score(num, 2, f"Historical day pattern match ({count}x)", "S34-DayPattern")

        # --- ASTRO LAYER (S35-S38, Northeast) ---
        current_phase, phase_nums = self.astro.s35_moon_phase(target_date)
        for num, count in phase_nums[:6]:
            score(num, 1, f"Hot in {current_phase}: {count}x", "S35-MoonPhase")
        # S35b: Moon direction (waxing vs waning)
        direction, is_waxing, dir_nums = self.astro.s35b_moon_direction(target_date)
        for num, pct, d in dir_nums:
            score(num, 1, f"Prefers {d} moons ({pct}%)", "S35b-MoonDir")
        # S35c: Full/New moon proximity
        moon_age, prox, ctx = self.astro.s35c_full_moon_proximity(target_date)
        if prox < 2.0:
            for n in self.astro.s35_moon_phase(target_date)[1][:4]:
                score(n, 2, f"Near {ctx} moon ({prox}d away)", "S35c-MoonProx")
        if target_dow:
            ruler, ruler_nums = self.astro.s36_planetary_ruler(target_dow)
            for n in ruler_nums[:6]:
                score(n, 1, f"Planetary ruler {ruler} active today", "S36-PlanetRuler")

        # --- MOMENTUM BOOST (F-01) ---
        for strat_name, boost in self.momentum.get('strategies', {}).items():
            for num, s in scores.items():
                if strat_name in [r.split(']')[0].strip('[') for r in s['reasons']]:
                    scores[num]['total'] += int(boost)
                    scores[num]['reasons'].append(f"[F01-Momentum] Strategy {strat_name} momentum boost (+{boost})")

        # Sort by total score
        ranked = sorted(scores.items(), key=lambda x: -x[1]['total'])
        return ranked[:top_n]
    
    def predict(self, top_n=6, target_dow=None, modifier=1.0, target_date=None):
        """Return top N picks. AGGRESSIVE diversity: guarantees 2 per range (Low/Mid/High)."""
        full_ranked = self.run_full_prediction(36, target_dow=target_dow, modifier=modifier, target_date=target_date)
        
        # Separate by range safely
        all_low = [(n, s) for n, s in full_ranked if isinstance(n, int) and n <= 12]
        all_mid = [(n, s) for n, s in full_ranked if isinstance(n, int) and 13 <= n <= 24]
        all_high = [(n, s) for n, s in full_ranked if isinstance(n, int) and n >= 25]
        
        min_per = max(2, top_n // 3)
        selected = []
        seen = set()
        
        def take(pool, count, label):
            taken = 0
            for n, s in pool:
                if taken >= count:
                    break
                if n not in seen:
                    s['reasons'].append(f"[S39-Diversity] {label} range slot")
                    selected.append((n, s))
                    seen.add(n)
                    taken += 1
        
        take(all_low, min_per, "Low(1-12)")
        take(all_mid, min_per, "Mid(13-24)")
        take(all_high, min_per, "High(25-36)")
        
        # Fill remaining with best unseen
        for n, s in full_ranked:
            if len(selected) >= top_n:
                break
            if isinstance(n, int) and n not in seen:
                s['reasons'].append("[S39-Diversity] Best remaining")
                selected.append((n, s))
                seen.add(n)
        
        selected.sort(key=lambda x: -x[1]['total'])
        return selected[:top_n]
    
    def root_predict(self, top_n=3):
        """Root-level prediction: most likely roots with their 4 numbers."""
        return self.root.root_prediction(top_n)
    
    def daily_reading(self):
        """Full daily reading with predictions + metaphysical context."""
        predictions = self.predict(6)
        diaspora = self.superstition.diaspora_reading()
        elements = self.domain.element_distribution(12)
        
        return {
            'predictions': [{'number': n, 'score': s['total'], 'reasons': s['reasons'][:3]} for n, s in predictions],
            'diaspora_reading': diaspora,
            'recent_elements': elements,
            'ancestor_numbers': self.superstition.ancestor_numbers(),
            'money_numbers': self.superstition.money_numbers(),
        }


# ═══════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════

def main():
    records = load_results()
    if not records:
        print("No records loaded. Run build_dataset.py first.")
        return
    
    engine = PredictionEngine(records)
    
    if len(sys.argv) < 2:
        cmd = 'reading'
    else:
        cmd = sys.argv[1].lower()

    # JSON output mode — for Node.js API consumption
    if cmd == 'json':
        n = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 6
        target_dow = None
        dream_text = None
        strategy_mode = "hybrid"
        target_date = None
        for arg in sys.argv:
            if arg.startswith('--dow='):
                target_dow = arg.split('=')[1]
            elif arg.startswith('--dream='):
                dream_text = arg.split('=', 1)[1]
            elif arg.startswith('--strategy='):
                strategy_mode = arg.split('=', 1)[1]
            elif arg.startswith('--target-date='):
                date_str = arg.split('=', 1)[1]
                target_date = datetime.strptime(date_str, '%Y-%m-%d')
                target_dow = target_dow or target_date.strftime('%A')
        results = engine.predict(n, target_dow=target_dow, target_date=target_date)
        # Apply dream text correlation if provided
        dream_boost = []
        if dream_text and strategy_mode in ("dream", "hybrid"):
            dream_boost = engine.superstition.dream_correlation(dream_text)
        # Merge dream correlation into scored results
        if dream_boost:
            dream_map = dict(dream_boost)
            dream_results = []
            for num, s in results:
                bonus = dream_map.get(num, 0) * 2
                s['total'] += bonus
                if bonus > 0:
                    s['reasons'].insert(0, f"[DreamCorr] Dream keyword match (+{bonus})")
            # Re-sort by adjusted score
            results.sort(key=lambda x: -x[1]['total'])
        output = []
        for num, s in results:
            d = DREAM_BOOK[num]
            output.append({
                "number": num,
                "name": d["name"],
                "symbol": d.get("symbol", ""),
                "score": s["total"],
                "root": NUMBER_ROOT[num],
                "rootName": ROOT_NAMES[NUMBER_ROOT[num]],
                "reasons": s.get("reasons", [])[:3],
                "major": d.get("major", [])[:3],
            })
        print(json.dumps({"predictions": output, "targetDow": target_dow, "strategy": "full-engine", "strategyMode": strategy_mode}))
        return

    if cmd == 'predict' or cmd == 'p':
        n = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 6
        show_reasons = '--reasons' in sys.argv
        target_dow = None
        target_date = None
        for arg in sys.argv:
            if arg.startswith('--dow='):
                target_dow = arg.split('=')[1]
            elif arg.startswith('--target-date='):
                date_str = arg.split('=', 1)[1]
                target_date = datetime.strptime(date_str, '%Y-%m-%d')
                target_dow = target_dow or target_date.strftime('%A')
        
        results = engine.predict(n, target_dow=target_dow, target_date=target_date)
        print(f"\n  ==========================================")
        print(f"     CASH POT PREDICTION ENGINE")
        if target_date:
            print(f"     Target Date: {target_date.strftime('%Y-%m-%d')} ({target_dow})")
        elif target_dow:
            print(f"     Target: {target_dow}")
        print(f"  ==========================================")
        for num, s in results:
            name = DREAM_BOOK[num]['name']
            root = NUMBER_ROOT[num]
            print(f"    #{num:>2} {name:<20} score={s['total']:>3}  [Root {root} {ROOT_NAMES[root]}]")
        print(f"  ==========================================")
        
        if show_reasons:
            print(f"\n  === Reasoning ===")
            for num, s in results:
                print(f"\n  #{num} {DREAM_BOOK[num]['name']} (score: {s['total']})")
                for reason in s['reasons']:
                    print(f"    {reason}")
    
    elif cmd == 'root' or cmd == 'rt':
        n = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 3
        
        # Show root gap status
        print(f"\n  ==========================================")
        print(f"     ROOT GAP STATUS (1-9)")
        print(f"  ==========================================")
        gaps = engine.root.root_gap_status()
        for g in gaps:
            marker = ">>> DUE <<<" if g['status'] in ('DUE', 'OVERDUE') else ""
            nums_str = ", ".join(f"#{n}" for n in g['numbers'])
            print(f"    Root {g['root']} {g['name']:<10} gap={g['current_gap']:>3} (avg {g['avg_gap']}) {marker}")
        
        # Root prediction
        print(f"\n  ==========================================")
        print(f"     ROOT PREDICTION (top {n} roots)")
        print(f"  ==========================================")
        root_preds = engine.root_predict(n)
        for rp in root_preds:
            nums_str = ", ".join(f"#{n}" for n in rp['numbers'])
            print(f"    Root {rp['root']} ({rp['name']}): score={rp['score']}")
            print(f"      Numbers: {nums_str}")
            for reason in rp['reasons']:
                print(f"      • {reason}")
    
    elif cmd == 'reading' or cmd == 'r':
        reading = engine.daily_reading()
        print(f"\n  ==================================================")
        print(f"        CASH POT DAILY READING")
        print(f"  ==================================================")
        print(f"    Diaspora: {reading['diaspora_reading']['reading'][:50]}...")
        print(f"  --------------------------------------------------")
        print(f"    PREDICTIONS (6 numbers):")
        for p in reading['predictions']:
            n = p['number']
            print(f"      #{n:>2} {DREAM_BOOK[n]['name']:<20} score={p['score']:>3}")
        print(f"  --------------------------------------------------")
        print(f"    Ancestor #s: {reading['ancestor_numbers']}")
        print(f"    Money #s:    {reading['money_numbers']}")
        print(f"  ==================================================")
    
    elif cmd == 'strategy' or cmd == 's':
        strat = sys.argv[2] if len(sys.argv) > 2 else 's01'
        math = engine.math
        ran = False
        
        if strat == 's01': result = math.s01_overall_frequency(); ran = True
        elif strat == 's02': result = math.s02_cold_numbers(); ran = True
        elif strat == 's03': result = math.s03_hot_streak(10); ran = True
        elif strat == 's07': result = math.s07_longest_gap(); ran = True
        elif strat == 's10': result = math.s10_repeat_pattern(); ran = True
        elif strat == 's16': result = math.s16_frequent_pairs(10); ran = True
        elif strat == 's17': result = math.s17_consecutive_draw_pair(); ran = True
        elif strat == 's23': result = math.s23_due_by_cycle(); ran = True
        elif strat == 's25': result = math.s25_odd_even_balance(); ran = True
        
        if ran:
            print(f"\n  Strategy {strat}:")
            if isinstance(result, tuple):
                print(f"  {result}")
            else:
                for item in result[:10]:
                    print(f"  {item}")
        else:
            print(f"  Strategy {strat} not found or needs args.")
            print(f"  Available: s01, s02, s03, s07, s10, s16, s17, s23, s25")
    
    # ── strategies — per-strategy raw output for dashboard ──
    elif cmd == 'strategies':
        target_dow = None
        for arg in sys.argv:
            if arg.startswith('--dow='):
                target_dow = arg.split('=')[1]
        if not target_dow:
            target_dow = datetime.now().strftime('%A')
        output = []
        # Math strategies
        m = engine.math
        output.append({"id":"S01-Freq","name":"Overall Frequency","glyph":"◉","layer":"math",
            "streak":{"status":"neutral"},"output":{"type":"ranked_numbers","numbers":[n for n,c in m.s01_overall_frequency()[:10]],"topPicks":[n for n,c in m.s01_overall_frequency()[:3]]}})
        output.append({"id":"S02-Cold","name":"Cold Numbers","glyph":"❄","layer":"math",
            "streak":{"status":"neutral"},"output":{"type":"ranked_numbers","numbers":[n for n,c in m.s02_cold_numbers()[:10]],"topPicks":[n for n,c in m.s02_cold_numbers()[:3]]}})
        output.append({"id":"S03-HotStreak","name":"Hot Streak","glyph":"🔥","layer":"math",
            "streak":{"status":"neutral"},"output":{"type":"ranked_numbers","numbers":[n for n,c in m.s03_hot_streak(10)[:10]],"topPicks":[n for n,c in m.s03_hot_streak(10)[:3]]}})
        output.append({"id":"S04-ColdStreak","name":"Cold Streak","glyph":"🧊","layer":"math",
            "streak":{"status":"neutral"},"output":{"type":"ranked_numbers","numbers":[n for n,_ in m.s04_cold_streak(30)[:10]],"topPicks":[n for n,_ in m.s04_cold_streak(30)[:3]]}})
        output.append({"id":"S05-Momentum","name":"Frequency Momentum","glyph":"↗","layer":"math",
            "streak":{"status":"neutral"},"output":{"type":"ranked_numbers","numbers":[n for n,_ in m.s05_frequency_momentum()[:10]],"topPicks":[n for n,_ in m.s05_frequency_momentum()[:3]]}})
        gaps = m.s07_longest_gap()
        smallest = list(reversed(gaps[-3:])) if len(gaps) >= 3 else []
        output.append({"id":"S07-Gap","name":"Gap Analysis","glyph":"⏳","layer":"math",
            "streak":{"status":"neutral"},"output":{"type":"gap_range","biggestGaps":[n for n,_ in gaps[:3]],"smallestGaps":[n for n,_ in smallest]}})
        output.append({"id":"S09-Cycle","name":"Expected by Cycle","glyph":"🔄","layer":"math",
            "streak":{"status":"neutral"},"output":{"type":"ranked_numbers","numbers":[n for n,_,_ in m.s09_expected_soon()[:10]],"topPicks":[n for n,_,_ in m.s09_expected_soon()[:3]]}})
        output.append({"id":"S10-Repeat","name":"Repeat Pattern","glyph":"🔁","layer":"math",
            "streak":{"status":"neutral"},"output":{"type":"ranked_numbers","numbers":[n for n,_ in m.s10_repeat_pattern()[:10]],"topPicks":[n for n,_ in m.s10_repeat_pattern()[:3]]}})
        pairs = m.s16_frequent_pairs(20)
        output.append({"id":"S16-Pairs","name":"Frequent Pairs","glyph":"🔗","layer":"math",
            "streak":{"status":"neutral"},"output":{"type":"ranked_numbers","numbers":list(set([a for (a,b),_ in pairs[:10]]+[b for (a,b),_ in pairs[:10]]))[:10],"topPicks":list(set([a for (a,b),_ in pairs[:5]]+[b for (a,b),_ in pairs[:5]]))[:3]}})
        last_num = engine.records[-1]['number']
        followers = m.s18_followers(last_num)
        output.append({"id":"S18-Follower","name":"Number Followers","glyph":"➡","layer":"math",
            "streak":{"status":"neutral"},"output":{"type":"followers","afterNumber":last_num,"followers":[n for n,_ in followers[:3]],"counts":[c for _,c in followers[:3]]}})
        output.append({"id":"S20-SameDay","name":"Same-Day Repeats","glyph":"📅","layer":"math",
            "streak":{"status":"neutral"},"output":{"type":"ranked_numbers","numbers":[n for n,_ in m.s20_same_day_repeats()[:10]],"topPicks":[n for n,_ in m.s20_same_day_repeats()[:3]]}})
        due_cycle = m.s23_due_by_cycle()
        output.append({"id":"S23-Personal","name":"Personal Cycle","glyph":"👤","layer":"math",
            "streak":{"status":"neutral"},"output":{"type":"ranked_numbers","numbers":[n for n,_,_ in due_cycle[:10]],"topPicks":[n for n,_,_ in due_cycle[:3]]}})
        ma_cross = m.s24_moving_average_crossover()
        output.append({"id":"S24-MACross","name":"MA Crossover","glyph":"📈","layer":"math",
            "streak":{"status":"neutral"},"output":{"type":"ranked_numbers","numbers":[n for n,_,_ in ma_cross[:10]],"topPicks":[n for n,_,_ in ma_cross[:3]]}})
        target_range, label, l, m_val, h = m.s26_low_mid_high()
        output.append({"id":"S26-Range","name":"Low/Mid/High","glyph":"📏","layer":"math",
            "streak":{"status":"neutral"},"output":{"type":"range_pick","recommendedRange":label.split()[0].lower(),"rangeLabel":label,"distribution":{"low":l,"mid":m_val,"high":h},"numbers":target_range}})
        mirrors = m.s28_mirror_numbers()
        output.append({"id":"S28-Mirror","name":"Mirror Numbers","glyph":"🪞","layer":"math",
            "streak":{"status":"neutral"},"output":{"type":"ranked_numbers","numbers":[m_num for m_num,_ in mirrors[:10]],"topPicks":[m_num for m_num,_ in mirrors[:3]]}})
        monthly = m.s30_monthly_hot()
        output.append({"id":"S30-Monthly","name":"Monthly Hot","glyph":"📆","layer":"math",
            "streak":{"status":"neutral"},"output":{"type":"ranked_numbers","numbers":[n for n,_,_ in monthly[:10]],"topPicks":[n for n,_,_ in monthly[:3]]}})
        # Time Series strategies
        ts = engine.timeseries
        ts_trend = ts.s31_multi_step_trend()
        output.append({"id":"S31-MultiStep","name":"Multi-Step Trend","glyph":"🔮","layer":"timeseries",
            "streak":{"status":"neutral"},"output":{"type":"ranked_numbers","numbers":[n for n,_,_ in ts_trend[:10]],"topPicks":[n for n,_,_ in ts_trend[:3]]}})
        day_match = ts.s34_day_pattern(3, 10)
        output.append({"id":"S34-DayPattern","name":"Day Pattern Match","glyph":"🧩","layer":"timeseries",
            "streak":{"status":"neutral"},"output":{"type":"ranked_numbers","numbers":[n for n,_ in day_match[:10]],"topPicks":[n for n,_ in day_match[:3]]}})
        # Astro strategies
        astro = engine.astro
        current_phase, phase_nums = astro.s35_moon_phase()
        output.append({"id":"S35-MoonPhase","name":"Moon Phase","glyph":"🌙","layer":"astro",
            "streak":{"status":"neutral"},"output":{"type":"ranked_numbers","currentPhase":current_phase,"numbers":[n for n,_ in phase_nums[:10]],"topPicks":[n for n,_ in phase_nums[:3]]}})
        ruler, ruler_nums = astro.s36_planetary_ruler(target_dow)
        output.append({"id":"S36-PlanetRuler","name":"Planetary Ruler","glyph":"🪐","layer":"astro",
            "streak":{"status":"neutral"},"output":{"type":"ranked_numbers","currentPhase":f"{target_dow} ruled by {ruler}","numbers":ruler_nums[:10],"topPicks":ruler_nums[:3]}})
        # Domain strategies
        el_due = engine.domain.element_due()
        domain_nums = []
        for el, nums, _ in el_due[:3]:
            domain_nums.extend(nums)
        output.append({"id":"D01-Element","name":"Element Balance","glyph":"🌍","layer":"domain",
            "streak":{"status":"neutral"},"output":{"type":"ranked_numbers","numbers":list(dict.fromkeys(domain_nums))[:10],"topPicks":list(dict.fromkeys(domain_nums))[:3]}})
        dom_rot = engine.domain.domain_rotation(12)
        rot_nums = []
        for dom, nums in dom_rot[:5]:
            rot_nums.extend(nums)
        output.append({"id":"D02-Domain","name":"Domain Rotation","glyph":"🏷️","layer":"domain",
            "streak":{"status":"neutral"},"output":{"type":"ranked_numbers","numbers":list(dict.fromkeys(rot_nums))[:10],"topPicks":list(dict.fromkeys(rot_nums))[:3]}})
        print(json.dumps({"targetDow": target_dow, "strategies": output}))
        return

    # ── forecast — N-step ahead predictions ──
    elif cmd == 'forecast':
        n = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 12
        target_dow = None
        for arg in sys.argv:
            if arg.startswith('--dow='):
                target_dow = arg.split('=')[1]
        results = engine.predict(n, target_dow=target_dow)
        forecast = []
        for i, (num, s) in enumerate(results):
            decay = max(0.95 - i * 0.05, 0.35)
            d = DREAM_BOOK[num]
            forecast.append({"step": i+1, "number": num, "name": d["name"],
                "confidence": round(decay * 100), "score": s["total"]})
        print(json.dumps({"forecast": forecast, "targetDow": target_dow or datetime.now().strftime('%A')}))
        return

    # ── accuracy — hit rate breakdown ──
    elif cmd == 'accuracy':
        log = load_json('predictions_log.json')
        if not log or not log.get('predictions'):
            print(json.dumps({"total_predictions":0,"total_hits":0,"hit_rate":0,"by_strategy":{},"by_layer":{},"by_slot":{}}))
            return
        preds = log['predictions']
        total = len(preds)
        hits = sum(1 for p in preds if p.get('hit'))
        by_slot = defaultdict(lambda: {'hits': 0, 'total': 0})
        by_strat = defaultdict(lambda: {'hits': 0, 'total': 0})
        for p in preds:
            slot = p.get('draw', 'Unknown')
            by_slot[slot]['total'] += 1
            if p.get('hit'):
                by_slot[slot]['hits'] += 1
            for s in p.get('strategies_that_hit', []):
                by_strat[s]['hits'] += 1
                by_strat[s]['total'] += 1
        by_slot_rate = {k: round(v['hits']/v['total']*100, 1) for k,v in by_slot.items()}
        by_strat_rate = {k: {"hits": v['hits'], "total": v['total'],
            "hitRate": round(v['hits']/max(v['total'],1)*100,1)} for k,v in by_strat.items()}
        print(json.dumps({"total_predictions":total,"total_hits":hits,
            "hit_rate":round(hits/max(total,1)*100,1),"by_strategy":by_strat_rate,
            "by_layer":{},"by_slot":by_slot_rate}))
        return

    # ── moon — current moon phase + planetary data ──
    elif cmd == 'moon':
        date_str = None
        for arg in sys.argv:
            if arg.startswith('--date='):
                date_str = arg.split('=')[1]
        target = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.now()
        phase = moon_phase(target)
        dow = target.strftime('%A')
        hour = target.hour
        ruler = PLANETARY_RULERS.get(dow, "Sun")
        p_hour = planetary_hour(target, hour)
        print(json.dumps({"date": target.strftime('%Y-%m-%d'),"dayOfWeek": dow,
            "moonPhase": phase,"planetaryRuler": ruler,
            "activePlanetaryHour": p_hour or "N/A",
            "moonIllumination": round(abs(((MOON_PHASES.index(phase)-4)/4))*100)}))
        return

    # ── backtest — walk-forward simulation ──
    elif cmd == 'backtest':
        import subprocess
        script = os.path.join(os.path.dirname(__file__), 'backtest.py')
        args = [sys.executable, script] + sys.argv[2:]
        subprocess.run(args)
        return
    
    elif cmd == 'domain' or cmd == 'd':
        sub = sys.argv[2] if len(sys.argv) > 2 else 'elements'
        if sub == 'elements' or sub == 'e':
            print("\n  Element Distribution (last 12 draws):")
            for el, count in engine.domain.element_distribution(12):
                bar = '#' * count
                print(f"  {el:<8} {count:>3} {bar}")
        elif sub == 'due' or sub == 'd':
            print("\n  Elements Due:")
            for el, nums, diff in engine.domain.element_due():
                print(f"  {el}: {nums[:6]} (diff: {diff})")
        elif sub == 'rotate' or sub == 'r':
            print("\n  Domains Not Seen Recently (rotation due):")
            for dom, nums in engine.domain.domain_rotation(12)[:10]:
                print(f"  {dom:<30} → #{', #'.join(str(n) for n in nums[:6])}")
    
    elif cmd == 'dream':
        if len(sys.argv) < 3:
            print("  Usage: dream <number>  OR  dream <keyword>")
            return
        arg = sys.argv[2]
        if arg.isdigit():
            n = int(arg)
            if n in DREAM_BOOK:
                d = DREAM_BOOK[n]
                print(f"\n  #{n} — {d['name']} ({d['symbol']})")
                print(f"  Element: {d['element']} | Planet: {d['planet']} | Energy: {d['energy']}")
                print(f"  Meaning: {d['dream_meaning']}")
                print(f"  Major: {d['major']}")
                print(f"  Minor: {d['minor']}")
                print(f"  Domains: {', '.join(d['domains'])}")
            else:
                print(f"  Invalid number: {n}")
        else:
            results = engine.superstition.dream_correlation(' '.join(sys.argv[2:]))
            if results:
                print(f"\n  Dream matches for '{' '.join(sys.argv[2:])}':")
                for n, score in results[:10]:
                    print(f"  #{n:>2} {DREAM_BOOK[n]['name']} (score: {score})")
            else:
                print("  No matches found.")
    
    elif cmd == 'help':
        print("""
  Cash Pot Predictor — Commands:
  ─────────────────────────────────────────────
  predict [n] [--reasons] [--dow=Monday]  Top N prediction with optional DOW targeting
  root [n]                              Root-level prediction (1-9) with gap status
  reading                               Full daily reading (predictions + diaspora)
  strategies [--dow=Monday]             Per-strategy raw output for dashboard
  forecast <n> [--dow=Monday]           N-step ahead forecast with confidence decay
  accuracy                              Hit rate stats by strategy/layer/slot
  moon [--date=YYYY-MM-DD]              Current moon phase + planetary data
  backtest [--start=YYYY-MM-DD] [--end=YYYY-MM-DD]  Walk-forward backtest
  strategy <s01-s25>                    Run a single math strategy
  domain <elements|due|rotate>          Domain/element analysis
  dream <number|keyword>                Look up dream book entry or search keywords
  momentum                              View strategy momentum status
  log-hit <number> [--strategies=...]   Log a correct prediction (F-01 feedback)
  help                                  This menu
""")
    
    elif cmd == 'momentum' or cmd == 'm':
        mom = engine.momentum
        print(f"\n  ==========================================")
        print(f"     STRATEGY MOMENTUM (Live Feedback)")
        print(f"  ==========================================")
        print(f"    Total hits: {mom.get('total_hits', 0)}")
        print(f"    Total misses: {mom.get('total_misses', 0)}")
        print(f"    Last updated: {mom.get('last_updated', 'never')}")
        strats = mom.get('strategies', {})
        if strats:
            print(f"\n    Strategy boosts:")
            for name, boost in sorted(strats.items(), key=lambda x: -x[1]):
                print(f"      {name}: +{boost}")
        else:
            print(f"\n    No strategy momentum yet. Use 'log-hit' to start feedback loop.")
        print(f"  ==========================================")
    
    elif cmd == 'log-hit':
        if len(sys.argv) < 3:
            print("  Usage: log-hit <number> [--strategies=S01,S02,...]")
            return
        hit_num = int(sys.argv[2])
        hit_name = DREAM_BOOK.get(hit_num, {}).get('name', '?')
        
        # Get the prediction that was used (re-run prediction to see which strats scored this)
        # For now, just record that the feedback loop is active
        mom = engine.momentum
        mom['total_hits'] = mom.get('total_hits', 0) + 1
        mom['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # Boost strategies that mention this number in reasons
        strat_arg = None
        for arg in sys.argv:
            if arg.startswith('--strategies='):
                strat_arg = arg.split('=')[1]
        
        if strat_arg:
            for s in strat_arg.split(','):
                s = s.strip()
                mom['strategies'][s] = mom['strategies'].get(s, 0) + 1
            print(f"\n  Logged hit: #{hit_num} ({hit_name})")
            print(f"  Boosted strategies: {strat_arg}")
        else:
            # Auto-detect: run prediction and see which strategies scored this number
            results = engine.run_full_prediction(36)
            for num, s in results:
                if num == hit_num:
                    for reason in s['reasons']:
                        # Extract strategy name from reason "[S01-Freq] ..."
                        if reason.startswith('['):
                            strat_name = reason.split(']')[0].strip('[')
                            mom['strategies'][strat_name] = mom['strategies'].get(strat_name, 0) + 1
            print(f"\n  Auto-logged hit: #{hit_num} ({hit_name})")
            boosted = mom['strategies']
            if boosted:
                print(f"  Boosted: {', '.join(f'{k}(+{v})' for k,v in sorted(boosted.items(), key=lambda x:-x[1])[:10])}")
        
        save_momentum(mom)
        print(f"  Momentum saved to strategy_momentum.json")
    
    else:
        print(f"  Unknown command: '{cmd}'. Try 'help'.")


if __name__ == '__main__':
    main()
