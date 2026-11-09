export interface Draw {
  id: string;
  index: number;
  drawTime: string;
  winningNumber: number;
  date?: string;
}

export interface PredictionResult {
  numbers: number[];
  names: string[];
  reversal: number[];
  reversalNames: string[];
  analysis: string;
  drawTime: string;
  fallback?: boolean;
}

export interface SymbolMeaning {
  number: number;
  name: string;
  keywords: string[];
  emoji?: string;
  major?: string[];
  minor?: string[];
}

export type Strategy = "math" | "dream" | "hybrid";

export type View = "engine" | "dream" | "results" | "chart";

export type LayerName = "math" | "domain" | "superstition" | "root" | "timeseries" | "astro";

export interface StrategyStreak {
  status: "hot" | "neutral" | "cold";
  lastHits?: number;
  lastMisses?: number;
}

export type StrategyOutputType = "ranked_numbers" | "gap_range" | "range_pick" | "followers";

export interface StrategyOutput {
  type: StrategyOutputType;
  numbers?: number[];
  topPicks?: number[];
  biggestGaps?: number[];
  smallestGaps?: number[];
  recommendedRange?: string;
  rangeLabel?: string;
  distribution?: Record<string, number>;
  afterNumber?: number;
  followers?: number[];
  counts?: number[];
  currentPhase?: string;
}

export interface StrategyCard {
  id: string;
  name: string;
  glyph: string;
  layer: LayerName;
  streak: StrategyStreak;
  output: StrategyOutput;
}

export interface StrategyDashboard {
  targetDow: string;
  strategies: StrategyCard[];
}

export interface AccuracyStats {
  totalPredictions: number;
  totalHits: number;
  hitRate: number;
  byStrategy: Record<string, { hits: number; total: number; hitRate: number }>;
  byLayer: Record<string, number>;
  bySlot: Record<string, number>;
}

export interface AstroContext {
  date: string;
  dayOfWeek: string;
  moonPhase: string;
  moonIllumination: number;
  planetaryRuler: string;
  activePlanetaryHour: string;
}

export interface ForecastStep {
  step: number;
  number: number;
  name: string;
  confidence: number;
  score: number;
}

export interface ForecastResult {
  forecast: ForecastStep[];
  targetDow: string;
}
