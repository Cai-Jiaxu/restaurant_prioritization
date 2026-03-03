'use client';
import type { Segment } from '@/data/restaurantTypes';
import { SlidersHorizontalIcon, ChevronDownIcon } from 'lucide-react';

const ALL_SEGMENTS: Segment[] = ['Rising', 'Hidden Gem', 'Stable', 'Declining'];

interface SidebarFiltersProps {
    segments: string[];
    regions: string[];
    cuisines: string[];
    minScore: number;
    maxScore: number;

    selectedSegments: Segment[];
    selectedRegions: string[];
    selectedCuisines: string[];
    selectedMinScore: number;

    onSegmentsChange: (v: Segment[]) => void;
    onRegionsChange: (v: string[]) => void;
    onCuisinesChange: (v: string[]) => void;
    onMinScoreChange: (v: number) => void;
}

function MultiSelect({
    label,
    options,
    selected,
    onChange,
}: {
    label: string;
    options: string[];
    selected: string[];
    onChange: (v: string[]) => void;
}) {
    const allSelected = selected.length === options.length;
    const toggle = (opt: string) => {
        if (selected.includes(opt)) {
            const next = selected.filter((s) => s !== opt);
            onChange(next.length ? next : options); // prevent empty
        } else {
            onChange([...selected, opt]);
        }
    };

    return (
        <div className="flex flex-col gap-1">
            <div className="flex items-center justify-between">
                <span className="text-[10px] font-semibold uppercase tracking-widest text-slate-500 dark:text-slate-400">
                    {label}
                </span>
                <button
                    onClick={() => onChange(allSelected ? [options[0]] : options)}
                    className="text-[10px] text-primary-600 dark:text-primary-500 hover:underline"
                >
                    {allSelected ? 'None' : 'All'}
                </button>
            </div>
            <div className="flex flex-wrap gap-1.5">
                {options.map((opt) => {
                    const active = selected.includes(opt);
                    return (
                        <button
                            key={opt}
                            onClick={() => toggle(opt)}
                            className={`px-2 py-0.5 rounded-full text-xs border transition-colors ${active
                                ? 'bg-primary-100 dark:bg-primary-500/20 border-primary-500/50 text-primary-700 dark:text-primary-300'
                                : 'bg-transparent border-slate-300 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:border-slate-400 dark:hover:border-slate-500'
                                }`}
                        >
                            {opt}
                        </button>
                    );
                })}
            </div>
        </div>
    );
}

export function SidebarFilters({
    segments, regions, cuisines, minScore, maxScore,
    selectedSegments, selectedRegions, selectedCuisines, selectedMinScore,
    onSegmentsChange, onRegionsChange, onCuisinesChange, onMinScoreChange,
}: SidebarFiltersProps) {
    return (
        <div className="flex flex-col gap-5">
            <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300 font-semibold text-sm">
                <SlidersHorizontalIcon className="w-4 h-4 text-primary-600 dark:text-primary-400" />
                Filters
            </div>

            <MultiSelect
                label="Segment"
                options={ALL_SEGMENTS}
                selected={selectedSegments}
                onChange={onSegmentsChange as (v: string[]) => void}
            />

            <MultiSelect
                label="Region"
                options={regions}
                selected={selectedRegions}
                onChange={onRegionsChange}
            />

            <MultiSelect
                label="Cuisine"
                options={cuisines}
                selected={selectedCuisines}
                onChange={onCuisinesChange}
            />

            {/* Min Score Slider */}
            <div className="flex flex-col gap-2">
                <div className="flex items-center justify-between">
                    <span className="text-[10px] font-semibold uppercase tracking-widest text-slate-500 dark:text-slate-400">
                        Min Priority Score
                    </span>
                    <span className="text-xs font-bold text-primary-600 dark:text-primary-400">≥ {selectedMinScore}</span>
                </div>
                <input
                    type="range"
                    min={0}
                    max={maxScore}
                    step={1}
                    value={selectedMinScore}
                    onChange={(e) => onMinScoreChange(Number(e.target.value))}
                    className="w-full h-1.5 appearance-none cursor-pointer bg-slate-300 dark:bg-slate-700 rounded-full accent-primary-600 dark:accent-primary-500"
                />
                <div className="flex justify-between text-[10px] text-slate-600">
                    <span>0</span>
                    <span>{Math.round(maxScore)}</span>
                </div>
            </div>
        </div>
    );
}
