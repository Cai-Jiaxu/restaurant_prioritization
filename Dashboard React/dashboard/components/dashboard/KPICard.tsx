import { TrendingUpIcon, TrendingDownIcon } from 'lucide-react';

interface KPICardProps {
    label: string;
    value: string | number;
    sublabel?: string;
    trending?: 'up' | 'down' | 'neutral';
    icon?: string;
    highlightColor?: string; // Tailwind text class e.g. 'text-primary-400'
}

export function KPICard({ label, value, sublabel, trending, icon, highlightColor }: KPICardProps) {
    return (
        <div className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 flex flex-col gap-2 shadow-sm hover:-translate-y-0.5 hover:shadow-md transition-all duration-200">
            <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-widest text-slate-500 dark:text-slate-400">
                    {label}
                </span>
                {icon && <span className="text-lg">{icon}</span>}
            </div>

            <div className={`text-3xl font-bold tracking-tight ${highlightColor ?? 'text-slate-900 dark:text-slate-50'}`}>
                {value}
            </div>

            {(sublabel || trending) && (
                <div className="flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400">
                    {trending === 'up' && <TrendingUpIcon className="w-3 h-3 text-emerald-500" />}
                    {trending === 'down' && <TrendingDownIcon className="w-3 h-3 text-red-500" />}
                    {sublabel && <span>{sublabel}</span>}
                </div>
            )}
        </div>
    );
}
