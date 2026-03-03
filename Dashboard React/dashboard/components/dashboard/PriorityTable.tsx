'use client';
import { useState, useMemo } from 'react';
import type { Restaurant, Segment } from '@/data/restaurantTypes';
import { SegmentBadge } from './SegmentBadge';
import { Pagination } from './Pagination';
import { DownloadIcon } from 'lucide-react';

const PAGE_SIZE = 10;

interface PriorityTableProps {
    restaurants: Restaurant[];
    showAll: boolean;
}

function ScoreBar({ value, color }: { value: number; color: string }) {
    const pct = Math.min(Math.round(value * 100), 100);
    return (
        <div className="flex items-center gap-2 min-w-[80px]">
            <span className="text-xs text-slate-400 w-8 text-right">{pct}%</span>
            <div className="flex-1 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
            </div>
        </div>
    );
}

export function PriorityTable({ restaurants, showAll }: PriorityTableProps) {
    const [page, setPage] = useState(1);

    const display = useMemo(() => {
        const filtered = showAll
            ? restaurants
            : restaurants.filter((r) =>
                r.ML_Predicted_Segment === 'Rising' || r.ML_Predicted_Segment === 'Hidden Gem',
            );
        return filtered;
    }, [restaurants, showAll]);

    // Reset page when data changes
    const totalPages = Math.max(1, Math.ceil(display.length / PAGE_SIZE));
    const safePage = Math.min(page, totalPages);
    const pageRows = display.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);

    function downloadCSV() {
        const headers = ['Rank', 'Restaurant', 'Segment', 'Priority Score', 'Cuisine', 'Region', 'P(Rising)', 'P(Hidden Gem)'];
        const rows = display.map((r, i) =>
            [i + 1, r.restaurant_name, r.ML_Predicted_Segment, r.ml_priority_score.toFixed(1), r.cuisine, r.region,
            r.prob_rising.toFixed(3), r.prob_hidden_gem.toFixed(3)].join(','),
        );
        const csv = [headers.join(','), ...rows].join('\n');
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = 'hungryhub_priority_list.csv'; a.click();
        URL.revokeObjectURL(url);
    }

    return (
        <div className="flex flex-col gap-3">
            {/* Header row */}
            <div className="flex items-center justify-between flex-wrap gap-2">
                <span className="text-sm text-slate-500 dark:text-slate-400">
                    Showing <strong className="text-slate-800 dark:text-slate-200">{display.length}</strong> restaurants
                </span>
                <button
                    onClick={downloadCSV}
                    className="flex items-center gap-1.5 h-8 px-3 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-xs font-medium hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
                >
                    <DownloadIcon className="w-3.5 h-3.5" />
                    Export CSV
                </button>
            </div>

            {/* Table */}
            <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="bg-slate-100 dark:bg-slate-800/80 border-b border-slate-200 dark:border-slate-700">
                            {['#', 'Restaurant', 'Segment', 'Score', 'P(Rising)', 'P(Hidden Gem)', 'GMaps ★', 'Momentum']
                                .map((h) => (
                                    <th key={h} className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 whitespace-nowrap">
                                        {h}
                                    </th>
                                ))}
                        </tr>
                    </thead>
                    <tbody>
                        {pageRows.map((r, idx) => {
                            const globalRank = (safePage - 1) * PAGE_SIZE + idx + 1;
                            const scoreColor =
                                r.ml_priority_score > 70
                                    ? 'text-primary-600 dark:text-primary-400'
                                    : r.ml_priority_score > 40
                                        ? 'text-emerald-600 dark:text-emerald-400'
                                        : 'text-slate-500 dark:text-slate-400';
                            return (
                                <tr
                                    key={r.restaurant_id}
                                    className="border-b border-slate-100 dark:border-slate-800/60 hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors"
                                >
                                    <td className="px-4 py-3 text-xs text-slate-400 dark:text-slate-500">#{globalRank}</td>
                                    <td className="px-4 py-3">
                                        <div className="font-semibold text-slate-800 dark:text-slate-100 truncate max-w-[180px]">
                                            {r.restaurant_name}
                                        </div>
                                        <div className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">
                                            {r.cuisine} · {r.region}
                                        </div>
                                    </td>
                                    <td className="px-4 py-3">
                                        <SegmentBadge segment={r.ML_Predicted_Segment} />
                                    </td>
                                    <td className={`px-4 py-3 text-lg font-bold ${scoreColor}`}>
                                        {r.ml_priority_score.toFixed(1)}
                                    </td>
                                    <td className="px-4 py-3">
                                        <ScoreBar value={r.prob_rising} color="bg-emerald-500" />
                                    </td>
                                    <td className="px-4 py-3">
                                        <ScoreBar value={r.prob_hidden_gem} color="bg-violet-500" />
                                    </td>
                                    <td className="px-4 py-3 text-slate-600 dark:text-slate-300 text-sm">
                                        {r.gmaps_rating && r.gmaps_rating > 0 ? `${r.gmaps_rating.toFixed(1)} ⭐` : '—'}
                                    </td>
                                    <td className="px-4 py-3 text-slate-600 dark:text-slate-300 text-sm">
                                        {r.momentum_score != null ? r.momentum_score.toFixed(1) : '—'}
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>

            {/* Pagination */}
            <Pagination page={safePage} totalPages={totalPages} onPageChange={setPage} />
            <p className="text-center text-xs text-slate-400 dark:text-slate-600">
                Page {safePage} of {totalPages}
            </p>
        </div>
    );
}
