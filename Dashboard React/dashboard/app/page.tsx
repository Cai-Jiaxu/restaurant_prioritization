'use client';

import { useState, useEffect, useMemo } from 'react';
import {
  LayoutDashboardIcon,
  MapIcon,
  BarChart3Icon,
  SearchIcon,
  MenuIcon,
  XIcon,
  UtensilsIcon,
  TrendingUpIcon,
  StarIcon,
  AlertTriangleIcon,
  ZapIcon,
  GemIcon,
} from 'lucide-react';
import { ThemeSwitch } from '@/components/shared/ThemeSwitch';
import { KPICard } from '@/components/dashboard/KPICard';
import { SegmentBadge } from '@/components/dashboard/SegmentBadge';
import { PriorityTable } from '@/components/dashboard/PriorityTable';
import { SegmentDonut } from '@/components/dashboard/SegmentDonut';
import { CuisineBar } from '@/components/dashboard/CuisineBar';
import { PortfolioScatter } from '@/components/dashboard/PortfolioScatter';
import { SidebarFilters } from '@/components/dashboard/SidebarFilters';
import type { DashboardData, Restaurant, Segment } from '@/data/restaurantTypes';

type Tab = 'priority' | 'portfolio' | 'segments' | 'explorer';

export default function DashboardPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<Tab>('priority');
  const [showAll, setShowAll] = useState(false);
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter state
  const [selectedSegments, setSelectedSegments] = useState<Segment[]>(['Rising', 'Hidden Gem', 'Stable', 'Declining']);
  const [selectedRegions, setSelectedRegions] = useState<string[]>([]);
  const [selectedCuisines, setSelectedCuisines] = useState<string[]>([]);
  const [minScore, setMinScore] = useState(0);

  // Explorer state
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRestaurant, setSelectedRestaurant] = useState<Restaurant | null>(null);

  useEffect(() => {
    fetch('/api/dashboard')
      .then((r) => r.json())
      .then((d: DashboardData) => {
        setData(d);
        // Init filter options from data
        const regions = [...new Set(d.restaurants.map((r) => r.region))].sort();
        const cuisines = [...new Set(d.restaurants.map((r) => r.cuisine))].sort();
        setSelectedRegions(regions);
        setSelectedCuisines(cuisines);
        setLoading(false);
      })
      .catch((e) => {
        setError(String(e));
        setLoading(false);
      });
  }, []);

  const allRegions = useMemo(
    () => [...new Set(data?.restaurants.map((r) => r.region) ?? [])].sort(),
    [data],
  );
  const allCuisines = useMemo(
    () => [...new Set(data?.restaurants.map((r) => r.cuisine) ?? [])].sort(),
    [data],
  );
  const maxScore = useMemo(
    () => Math.ceil(data?.restaurants[0]?.ml_priority_score ?? 100),
    [data],
  );

  // Filtered restaurants
  const filteredRestaurants = useMemo(() => {
    if (!data) return [];
    return data.restaurants.filter(
      (r) =>
        selectedSegments.includes(r.ML_Predicted_Segment) &&
        selectedRegions.includes(r.region) &&
        selectedCuisines.includes(r.cuisine) &&
        r.ml_priority_score >= minScore,
    );
  }, [data, selectedSegments, selectedRegions, selectedCuisines, minScore]);

  // Explorer search
  const searchResults = useMemo(() => {
    if (!data || searchQuery.length < 2) return [];
    const q = searchQuery.toLowerCase();
    return data.restaurants.filter((r) => r.restaurant_name.toLowerCase().includes(q)).slice(0, 8);
  }, [data, searchQuery]);

  const kpis = data?.kpis;

  const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
    { id: 'priority', label: 'Priority List', icon: <LayoutDashboardIcon className="w-4 h-4" /> },
    { id: 'portfolio', label: 'Portfolio Map', icon: <MapIcon className="w-4 h-4" /> },
    { id: 'segments', label: 'Segment Analysis', icon: <BarChart3Icon className="w-4 h-4" /> },
    { id: 'explorer', label: 'Restaurant Explorer', icon: <SearchIcon className="w-4 h-4" /> },
  ];

  return (
    <div className="min-h-screen w-full bg-white dark:bg-slate-950 text-slate-900 dark:text-slate-50 transition-colors">
      <div className="flex h-screen overflow-hidden">
        {/* ─── Sidebar ─── */}
        <aside
          className={`
            fixed lg:relative inset-y-0 left-0 z-50 w-72 shrink-0
            bg-slate-50 dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800
            flex flex-col overflow-y-auto transition-transform duration-300
            ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          `}
        >
          {/* Logo */}
          <div className="flex items-center justify-between px-5 py-5 border-b border-slate-200 dark:border-slate-800">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center text-slate-950 font-bold text-sm">
                HH
              </div>
              <div>
                <div className="text-sm font-bold text-slate-800 dark:text-slate-100">HungryHub</div>
                <div className="text-[10px] text-slate-400 uppercase tracking-widest">CRM Dashboard</div>
              </div>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden p-1 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-800 transition-colors"
            >
              <XIcon className="w-4 h-4 text-slate-500" />
            </button>
          </div>

          {/* Segment overview tiles */}
          {kpis && (
            <div className="px-4 py-4 border-b border-slate-200 dark:border-slate-800 space-y-1.5">
              <div className="text-[10px] font-semibold uppercase tracking-widest text-slate-400 mb-2">
                Active Segments
              </div>
              {[
                { label: 'Rising', value: kpis.rising, color: 'text-emerald-600 dark:text-emerald-400', bg: 'bg-emerald-100 dark:bg-emerald-950/60', icon: '⚡' },
                { label: 'Hidden Gem', value: kpis.hiddenGem, color: 'text-violet-600 dark:text-violet-300', bg: 'bg-violet-100 dark:bg-violet-950/60', icon: '◆' },
                { label: 'Stable', value: kpis.stable, color: 'text-slate-600 dark:text-slate-400', bg: 'bg-slate-200 dark:bg-slate-800/60', icon: '●' },
                { label: 'Declining', value: kpis.declining, color: 'text-red-600 dark:text-red-400', bg: 'bg-red-100 dark:bg-red-950/60', icon: '⚠️' },
              ].map((s) => (
                <div key={s.label} className={`flex items-center justify-between px-3 py-2 rounded-lg ${s.bg}`}>
                  <span className={`text-sm font-medium ${s.color}`}>{s.icon} {s.label}</span>
                  <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${s.bg} ${s.color} border border-current/20`}>{s.value}</span>
                </div>
              ))}
            </div>
          )}

          {/* Filters */}
          <div className="px-4 py-4 flex-1">
            <SidebarFilters
              segments={['Rising', 'Hidden Gem', 'Stable', 'Declining']}
              regions={allRegions}
              cuisines={allCuisines}
              minScore={0}
              maxScore={maxScore}
              selectedSegments={selectedSegments}
              selectedRegions={selectedRegions}
              selectedCuisines={selectedCuisines}
              selectedMinScore={minScore}
              onSegmentsChange={(v) => setSelectedSegments(v as Segment[])}
              onRegionsChange={setSelectedRegions}
              onCuisinesChange={setSelectedCuisines}
              onMinScoreChange={setMinScore}
            />
          </div>

          {/* Footer */}
          <div className="px-4 py-3 border-t border-slate-200 dark:border-slate-800">
            <div className="text-[10px] text-slate-400 text-center">ML Pipeline v3 · LightGBM</div>
          </div>
        </aside>

        {/* Overlay */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 bg-black/50 z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* ─── Main Content ─── */}
        <main className="flex-1 overflow-y-auto">
          {/* Top Bar */}
          <div className="sticky top-0 z-30 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 px-6 py-4 flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                <MenuIcon className="w-5 h-5 text-slate-600 dark:text-slate-300" />
              </button>
              <div>
                <h1 className="text-xl font-bold text-slate-800 dark:text-slate-100">Restaurant Prioritization</h1>
                <p className="text-xs text-slate-400 dark:text-slate-500">
                  {loading ? 'Loading data…' : `${filteredRestaurants.length.toLocaleString()} restaurants · ML-driven marketing allocation`}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 bg-primary-100 dark:bg-primary-500/10 border border-primary-500/30 rounded-full">
                <div className="w-1.5 h-1.5 bg-primary-600 dark:bg-primary-400 rounded-full animate-pulse" />
                <span className="text-xs font-medium text-primary-600 dark:text-primary-400">Live</span>
              </div>
              <ThemeSwitch />
            </div>
          </div>

          <div className="px-6 py-6 space-y-6 max-w-7xl">
            {/* Loading / Error */}
            {loading && (
              <div className="flex items-center justify-center h-64 text-slate-400 dark:text-slate-600">
                <div className="text-center space-y-2">
                  <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto" />
                  <p className="text-sm">Loading restaurant data…</p>
                </div>
              </div>
            )}

            {error && (
              <div className="flex items-center gap-3 p-4 bg-red-950/20 border border-red-800/40 rounded-xl text-red-400 text-sm">
                <AlertTriangleIcon className="w-5 h-5 shrink-0" />
                <span>Failed to load data: {error}</span>
              </div>
            )}

            {!loading && !error && kpis && (
              <>
                {/* ── KPI Cards ── */}
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                  <KPICard label="Total" value={filteredRestaurants.length.toLocaleString()} sublabel="in view" icon="🍽️" />
                  <KPICard label="Rising Stars" value={filteredRestaurants.filter(r => r.ML_Predicted_Segment === 'Rising').length} sublabel="high-growth" icon="⚡" highlightColor="text-emerald-600 dark:text-emerald-400" />
                  <KPICard label="Hidden Gems" value={filteredRestaurants.filter(r => r.ML_Predicted_Segment === 'Hidden Gem').length} sublabel="underexploited" icon="◆" highlightColor="text-violet-600 dark:text-violet-400" />
                  <KPICard label="Declining" value={filteredRestaurants.filter(r => r.ML_Predicted_Segment === 'Declining').length} sublabel="at risk" icon="⚠️" highlightColor="text-red-600 dark:text-red-400" />
                  <KPICard label="Actionable" value={filteredRestaurants.filter(r => ['Rising', 'Hidden Gem'].includes(r.ML_Predicted_Segment)).length} sublabel="targets" icon="🎯" highlightColor="text-primary-600 dark:text-primary-400" />
                  <KPICard label="Avg Score" value={filteredRestaurants.length > 0 ? (filteredRestaurants.reduce((a, r) => a + r.ml_priority_score, 0) / filteredRestaurants.length).toFixed(1) : '—'} sublabel="priority" icon="📊" />
                </div>

                {/* ── Tabs ── */}
                <div className="flex gap-1 p-1 bg-slate-100 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 w-fit flex-wrap">
                  {tabs.map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === tab.id
                        ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-50 shadow-sm'
                        : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
                        }`}
                    >
                      {tab.icon}
                      {tab.label}
                    </button>
                  ))}
                </div>

                {/* ── Tab: Priority List ── */}
                {activeTab === 'priority' && (
                  <div className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-4">
                    <div className="flex items-center justify-between flex-wrap gap-3">
                      <div>
                        <h2 className="text-base font-semibold text-slate-800 dark:text-slate-100">Priority Marketing List</h2>
                        <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">
                          Ranked by ML priority score · the action queue for marketing allocation
                        </p>
                      </div>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <div
                          onClick={() => setShowAll((v) => !v)}
                          className={`relative w-9 h-5 rounded-full transition-colors ${showAll ? 'bg-primary-500' : 'bg-slate-300 dark:bg-slate-700'}`}
                        >
                          <div className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ${showAll ? 'translate-x-4' : ''}`} />
                        </div>
                        <span className="text-xs text-slate-500 dark:text-slate-400">Show all segments</span>
                      </label>
                    </div>

                    {/* Chart summary row */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-2">Avg Score by Cuisine</p>
                        <CuisineBar data={data!.cuisineScores} topCuisine={kpis.topCuisine} />
                        <p className="text-xs text-slate-500 dark:text-slate-400 text-center mt-1">
                          Highlighted: <strong className="text-primary-600 dark:text-primary-400">{kpis.topCuisine}</strong> (highest avg. priority score)
                        </p>
                      </div>
                      <div className="flex flex-col justify-center gap-2 px-4">
                        <div className="text-center">
                          <div className="text-4xl font-bold text-primary-600 dark:text-primary-400">{filteredRestaurants.filter(r => ['Rising', 'Hidden Gem'].includes(r.ML_Predicted_Segment)).length}</div>
                          <div className="text-xs text-slate-500 dark:text-slate-400 uppercase tracking-widest mt-1">Total Actionable Partners</div>
                        </div>
                      </div>
                    </div>

                    <PriorityTable restaurants={filteredRestaurants} showAll={showAll} />
                  </div>
                )}

                {/* ── Tab: Portfolio Map ── */}
                {activeTab === 'portfolio' && (
                  <div className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-4">
                    <div>
                      <h2 className="text-base font-semibold text-slate-800 dark:text-slate-100">Portfolio Risk & Opportunity Map</h2>
                      <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">
                        X = platform performance · Y = external quality (Google Maps) · Bubble size = priority score · Only restaurants with Google Maps data are plotted (~10% of portfolio)
                      </p>
                    </div>
                    <PortfolioScatter restaurants={filteredRestaurants} />
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                      <div className="p-2 bg-slate-100 dark:bg-slate-800/50 rounded-lg border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300">↗ Top-Right: High platform performance + strong public reputation</div>
                      <div className="p-2 bg-slate-100 dark:bg-slate-800/50 rounded-lg border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300">↖ Top-Left: Well-regarded publicly, underperforming on platform → Hidden Gems cluster here</div>
                      <div className="p-2 bg-slate-100 dark:bg-slate-800/50 rounded-lg border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300">↘ Bottom-Right: Strong platform performer, limited external signal</div>
                      <div className="p-2 bg-slate-100 dark:bg-slate-800/50 rounded-lg border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300">↙ Bottom-Left: Low on both — background portfolio</div>
                    </div>
                  </div>
                )}

                {/* ── Tab: Segment Analysis ── */}
                {activeTab === 'segments' && (
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                      <div className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm">
                        <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">Segment Distribution</h2>
                        <SegmentDonut
                          data={data!.segmentCounts.map(s => ({
                            ...s,
                            count: filteredRestaurants.filter(r => r.ML_Predicted_Segment === s.segment).length,
                          }))}
                          total={filteredRestaurants.length}
                        />
                      </div>
                      <div className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm">
                        <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">Avg Priority Score by Cuisine</h2>
                        <CuisineBar data={data!.cuisineScores} topCuisine={kpis.topCuisine} />
                      </div>
                    </div>
                    {/* Segment stats table */}
                    <div className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm">
                      <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-4">Segment Summary</h2>
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                          <thead>
                            <tr className="border-b border-slate-200 dark:border-slate-800">
                              {['Segment', 'Count', 'Share', 'Avg Score'].map(h => (
                                <th key={h} className="px-4 py-2 text-left text-xs font-semibold uppercase tracking-wider text-slate-400">{h}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {(['Rising', 'Hidden Gem', 'Stable', 'Declining'] as Segment[]).map(seg => {
                              const segRest = filteredRestaurants.filter(r => r.ML_Predicted_Segment === seg);
                              const avg = segRest.length > 0 ? (segRest.reduce((a, r) => a + r.ml_priority_score, 0) / segRest.length).toFixed(1) : '—';
                              const pct = filteredRestaurants.length > 0 ? ((segRest.length / filteredRestaurants.length) * 100).toFixed(0) : '0';
                              return (
                                <tr key={seg} className="border-b border-slate-100 dark:border-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800/50 transition-colors">
                                  <td className="px-4 py-3"><SegmentBadge segment={seg} /></td>
                                  <td className="px-4 py-3 font-semibold text-slate-700 dark:text-slate-200">{segRest.length.toLocaleString()}</td>
                                  <td className="px-4 py-3 text-slate-500 dark:text-slate-400">{pct}%</td>
                                  <td className="px-4 py-3 text-slate-600 dark:text-slate-300">{avg}</td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                )}

                {/* ── Tab: Explorer ── */}
                {activeTab === 'explorer' && (
                  <div className="space-y-4">
                    <div className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm">
                      <h2 className="text-base font-semibold text-slate-800 dark:text-slate-100 mb-3">Restaurant Deep Dive</h2>
                      <div className="relative">
                        <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                        <input
                          type="text"
                          placeholder="Search restaurant name…"
                          value={searchQuery}
                          onChange={(e) => { setSearchQuery(e.target.value); setSelectedRestaurant(null); }}
                          className="w-full h-10 pl-9 pr-4 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm text-slate-800 dark:text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-primary-500/40 focus:border-primary-500 transition-all"
                        />
                      </div>

                      {/* Search results */}
                      {searchResults.length > 0 && !selectedRestaurant && (
                        <div className="mt-2 border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">
                          {searchResults.map((r) => (
                            <button
                              key={r.restaurant_id}
                              onClick={() => { setSelectedRestaurant(r); setSearchQuery(r.restaurant_name); }}
                              className="w-full flex items-center justify-between px-4 py-3 hover:bg-slate-100 dark:hover:bg-slate-800 border-b border-slate-100 dark:border-slate-800 last:border-0 transition-colors text-left"
                            >
                              <div>
                                <div className="text-sm font-medium text-slate-800 dark:text-slate-100">{r.restaurant_name}</div>
                                <div className="text-xs text-slate-400">{r.cuisine} · {r.region}</div>
                              </div>
                              <SegmentBadge segment={r.ML_Predicted_Segment} />
                            </button>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Detail card */}
                    {selectedRestaurant && (
                      <div className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-5">
                        <div className="flex items-start justify-between gap-4 flex-wrap">
                          <div>
                            <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100">{selectedRestaurant.restaurant_name}</h3>
                            <div className="flex items-center gap-2 mt-2 flex-wrap">
                              <SegmentBadge segment={selectedRestaurant.ML_Predicted_Segment} />
                              <span className="text-xs text-slate-400 bg-slate-200 dark:bg-slate-800 px-2 py-0.5 rounded-full">{selectedRestaurant.cuisine}</span>
                              <span className="text-xs text-slate-400 bg-slate-200 dark:bg-slate-800 px-2 py-0.5 rounded-full">📍 {selectedRestaurant.region}</span>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-4xl font-black text-slate-800 dark:text-slate-50 tracking-tight">
                              {selectedRestaurant.ml_priority_score.toFixed(1)}
                            </div>
                            <div className="text-[10px] uppercase tracking-widest text-slate-500 dark:text-slate-400">Priority Score</div>
                            {selectedRestaurant.overall_rank > 0 && (
                              <div className="text-xs text-primary-600 dark:text-primary-400 mt-1">Rank #{Math.round(selectedRestaurant.overall_rank)}</div>
                            )}
                          </div>
                        </div>

                        {/* Class probabilities */}
                        <div>
                          <div className="text-[10px] font-semibold uppercase tracking-widest text-slate-400 mb-3">Prediction Confidence</div>
                          <div className="grid grid-cols-2 gap-3">
                            {([['Rising', selectedRestaurant.prob_rising, 'bg-emerald-500'], ['Hidden Gem', selectedRestaurant.prob_hidden_gem, 'bg-violet-500'], ['Stable', selectedRestaurant.prob_stable, 'bg-slate-500'], ['Declining', selectedRestaurant.prob_declining, 'bg-red-500']] as [string, number, string][]).map(([label, prob, color]) => (
                              <div key={label}>
                                <div className="flex justify-between text-xs mb-1">
                                  <span className="text-slate-500 dark:text-slate-400">{label}</span>
                                  <span className="font-medium text-slate-700 dark:text-slate-300">{(prob * 100).toFixed(0)}%</span>
                                </div>
                                <div className="h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                                  <div className={`h-full ${color} rounded-full transition-all`} style={{ width: `${prob * 100}%` }} />
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Business metrics */}
                        {(selectedRestaurant.total_revenue || selectedRestaurant.total_bookings) && (
                          <div>
                            <div className="text-[10px] font-semibold uppercase tracking-widest text-slate-400 mb-3">Business Metrics</div>
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                              {[
                                ['Revenue', selectedRestaurant.total_revenue ? `฿${selectedRestaurant.total_revenue.toLocaleString()}` : '—'],
                                ['Bookings', selectedRestaurant.total_bookings ? selectedRestaurant.total_bookings.toLocaleString() : '—'],
                                ['No-Show Rate', selectedRestaurant.no_show_rate ? `${(selectedRestaurant.no_show_rate * 100).toFixed(1)}%` : '—'],
                                ['GMaps Rating', selectedRestaurant.gmaps_rating ? `${selectedRestaurant.gmaps_rating.toFixed(1)} ⭐` : '—'],
                              ].map(([label, value]) => (
                                <div key={label} className="bg-white dark:bg-slate-800 rounded-xl p-3 border border-slate-200 dark:border-slate-700">
                                  <div className="text-[10px] uppercase tracking-wider text-slate-400 mb-1">{label}</div>
                                  <div className="text-base font-bold text-slate-700 dark:text-slate-200">{value}</div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {!selectedRestaurant && !searchQuery && (
                      <div className="flex items-center justify-center h-40 text-slate-400 dark:text-slate-600 text-sm text-center">
                        <div>
                          <SearchIcon className="w-8 h-8 mx-auto mb-2 opacity-40" />
                          Search for a restaurant above to see its full profile
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </>
            )}
          </div>

          {/* Footer */}
          <div className="border-t border-slate-200 dark:border-slate-800 px-6 py-4 text-center text-xs text-slate-400 dark:text-slate-600">
            HungryHub Restaurant Prioritization System · ML Pipeline v3 · Built with Next.js & LightGBM
          </div>
        </main>
      </div>
    </div>
  );
}
