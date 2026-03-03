import type { Segment } from '@/data/restaurantTypes';

interface SegmentBadgeProps {
    segment: Segment;
}

const styles: Record<Segment, string> = {
    Rising:
        'bg-emerald-950 text-emerald-400 border border-emerald-800/50',
    'Hidden Gem':
        'bg-violet-950 text-violet-300 border border-violet-800/50',
    Stable:
        'bg-slate-800 text-slate-400 border border-slate-700/50',
    Declining:
        'bg-red-950 text-red-400 border border-red-800/50',
};

const icons: Record<Segment, string> = {
    Rising: '⚡',
    'Hidden Gem': '◆',
    Stable: '●',
    Declining: '⚠️',
};

export function SegmentBadge({ segment }: SegmentBadgeProps) {
    return (
        <span
            className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold whitespace-nowrap ${styles[segment]}`}
        >
            <span className="text-[10px]">{icons[segment]}</span>
            {segment}
        </span>
    );
}
