'use client';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    Cell,
    LabelList,
} from 'recharts';
import type { CuisineScore } from '@/data/restaurantTypes';

interface CuisineBarProps {
    data: CuisineScore[];
    topCuisine: string;
}

export function CuisineBar({ data, topCuisine }: CuisineBarProps) {
    return (
        <ResponsiveContainer width="100%" height={240}>
            <BarChart data={data} margin={{ top: 20, right: 16, bottom: 0, left: 0 }}>
                <XAxis
                    dataKey="cuisine"
                    tick={{ fontSize: 11, fill: '#64748b' }}
                    axisLine={false}
                    tickLine={false}
                />
                <YAxis hide />
                <Tooltip
                    contentStyle={{
                        background: '#0f172a',
                        border: '1px solid #1e293b',
                        borderRadius: '8px',
                        color: '#f1f5f9',
                        fontSize: '12px',
                    }}
                    formatter={(v: number) => [v.toFixed(1), 'Avg Priority Score']}
                />
                <Bar dataKey="avgScore" radius={[6, 6, 0, 0]} maxBarSize={48}>
                    <LabelList
                        dataKey="avgScore"
                        position="top"
                        formatter={(v: number) => v.toFixed(0)}
                        style={{ fill: '#64748b', fontSize: 11 }}
                    />
                    {data.map((entry) => (
                        <Cell
                            key={entry.cuisine}
                            fill={entry.cuisine === topCuisine ? '#d4f03f' : '#334155'}
                        />
                    ))}
                </Bar>
            </BarChart>
        </ResponsiveContainer>
    );
}
