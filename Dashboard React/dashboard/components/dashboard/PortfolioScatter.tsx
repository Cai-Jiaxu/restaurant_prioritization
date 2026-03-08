'use client';
import {
    ScatterChart,
    Scatter,
    XAxis,
    YAxis,
    Tooltip,
    Legend,
    ResponsiveContainer,
    ZAxis,
} from 'recharts';
import type { Restaurant, Segment } from '@/data/restaurantTypes';
import { SEGMENT_COLORS } from '@/data/restaurantTypes';

interface PortfolioScatterProps {
    restaurants: Restaurant[];
}

const SEGMENTS: Segment[] = ['Rising', 'Hidden Gem', 'Stable', 'Declining'];

export function PortfolioScatter({ restaurants }: PortfolioScatterProps) {
    // Group by segment — use expected_kpi (mapped to internal_score) vs external_quality_score
    const groups = SEGMENTS.map((seg) => ({
        segment: seg,
        data: restaurants
            .filter(
                (r) =>
                    r.ML_Predicted_Segment === seg &&
                    r.internal_score != null &&
                    r.internal_score > 0 &&
                    r.external_quality_score != null &&
                    r.external_quality_score > 0,
            )
            .map((r) => ({
                x: r.internal_score!,
                y: r.external_quality_score!,
                z: r.ml_priority_score,
                name: r.restaurant_name,
            })),
    })).filter((g) => g.data.length > 0);

    if (groups.every((g) => g.data.length === 0)) {
        return (
            <div className="flex items-center justify-center h-64 text-slate-500 dark:text-slate-500 text-sm">
                Internal score data not available
            </div>
        );
    }

    return (
        <ResponsiveContainer width="100%" height={400}>
            <ScatterChart margin={{ top: 10, right: 24, bottom: 20, left: 8 }}>
                <XAxis
                    type="number"
                    dataKey="x"
                    name="Platform Performance"
                    domain={['auto', 'auto']}
                    tickFormatter={(val) => Math.round(val).toString()}
                    label={{ value: 'Platform Performance Score', position: 'insideBottom', offset: -10, fill: '#94a3b8', fontSize: 11 }}
                    tick={{ fontSize: 11, fill: '#94a3b8' }}
                    axisLine={false}
                    tickLine={false}
                />
                <YAxis
                    dataKey="y"
                    name="External Quality"
                    label={{ value: 'External Quality Score', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 11 }}
                    tick={{ fontSize: 11, fill: '#94a3b8' }}
                    axisLine={false}
                    tickLine={false}
                />
                <ZAxis dataKey="z" range={[30, 200]} name="Priority Score" />
                <Tooltip
                    contentStyle={{
                        background: '#0f172a',
                        border: '1px solid #1e293b',
                        borderRadius: '8px',
                        color: '#f1f5f9',
                        fontSize: '12px',
                    }}
                    cursor={{ strokeDasharray: '3 3', stroke: '#334155' }}
                    content={({ payload }) => {
                        if (!payload?.length) return null;
                        const d = payload[0]?.payload;
                        return (
                            <div className="bg-slate-900 border border-slate-700 rounded-lg p-3 text-xs text-slate-200 space-y-1">
                                <div className="font-semibold text-slate-100">{d?.name}</div>
                                <div>Exp. KPI: {d?.x?.toFixed(2)}</div>
                                <div>Ext. Quality: {d?.y?.toFixed(3)}</div>
                                <div>Score: {d?.z?.toFixed(1)}</div>
                            </div>
                        );
                    }}
                />
                <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: '12px', paddingTop: '16px' }} />
                {groups.map((g) => (
                    <Scatter
                        key={g.segment}
                        name={g.segment}
                        data={g.data}
                        fill={SEGMENT_COLORS[g.segment as Segment]}
                        fillOpacity={0.7}
                    />
                ))}
            </ScatterChart>
        </ResponsiveContainer>
    );
}
