import { ChevronLeftIcon, ChevronRightIcon } from 'lucide-react';

interface PaginationProps {
    page: number;
    totalPages: number;
    onPageChange: (page: number) => void;
}

function getPageRange(cur: number, total: number, wing = 2): (number | '…')[] {
    if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
    const pages: (number | '…')[] = [1];
    const lo = Math.max(2, cur - wing);
    const hi = Math.min(total - 1, cur + wing);
    if (lo > 2) pages.push('…');
    for (let p = lo; p <= hi; p++) pages.push(p);
    if (hi < total - 1) pages.push('…');
    pages.push(total);
    return pages;
}

export function Pagination({ page, totalPages, onPageChange }: PaginationProps) {
    if (totalPages <= 1) return null;
    const range = getPageRange(page, totalPages);

    const btnBase =
        'w-8 h-8 flex items-center justify-center rounded-lg text-xs font-medium transition-colors';
    const btnActive =
        'bg-primary-500 text-slate-950 font-bold shadow-sm cursor-default';
    const btnInactive =
        'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700';
    const btnDisabled =
        'bg-slate-100 dark:bg-slate-800 text-slate-400 dark:text-slate-600 opacity-50 cursor-not-allowed';

    return (
        <div className="flex items-center justify-center gap-1 py-3">
            <button
                onClick={() => onPageChange(page - 1)}
                disabled={page <= 1}
                className={`${btnBase} ${page <= 1 ? btnDisabled : btnInactive}`}
            >
                <ChevronLeftIcon className="w-4 h-4" />
            </button>

            {range.map((p, i) =>
                p === '…' ? (
                    <span key={`ellipsis-${i}`} className="w-8 h-8 flex items-center justify-center text-slate-400 dark:text-slate-600 text-sm">
                        …
                    </span>
                ) : (
                    <button
                        key={p}
                        onClick={() => onPageChange(p)}
                        className={`${btnBase} ${p === page ? btnActive : btnInactive}`}
                    >
                        {p}
                    </button>
                ),
            )}

            <button
                onClick={() => onPageChange(page + 1)}
                disabled={page >= totalPages}
                className={`${btnBase} ${page >= totalPages ? btnDisabled : btnInactive}`}
            >
                <ChevronRightIcon className="w-4 h-4" />
            </button>
        </div>
    );
}
