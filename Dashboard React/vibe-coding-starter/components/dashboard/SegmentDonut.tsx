'use client';
import {
    PieChart,
    Pie,
    Cell,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from 'recharts';
import type { SegmentCount, Segment } from '@/data/restaurantTypes';
import { SEGMENT_COLORS } from '@/data/restaurantTypes';

interface SegmentDonutProps {
    data: SegmentCount[];
    total: number;
}

export function SegmentDonut({ data, total }: SegmentDonutProps) {
    const chartData = data.filter((d) => d.count > 0);

    return (
        <div className="relative">
            <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                    <Pie
                        data={chartData}
                        dataKey="count"
                        nameKey="segment"
                        cx="50%"
                        cy="50%"
                        innerRadius="55%"
                        outerRadius="75%"
                        paddingAngle={2}
                        strokeWidth={0}
                    >
                        {chartData.map((entry) => (
                            <Cell
                                key={entry.segment}
                                fill={SEGMENT_COLORS[entry.segment as Segment]}
                            />
                        ))}
                    </Pie>
                    <Tooltip
                        contentStyle={{
                            background: '#0f172a',
                            border: '1px solid #1e293b',
                            borderRadius: '8px',
                            color: '#f1f5f9',
                            fontSize: '12px',
                        }}
                        formatter={(value: number, name: string) => [
                            `${value} (${((value / total) * 100).toFixed(0)}%)`,
                            name,
                        ]}
                    />
                    <Legend
                        iconType="circle"
                        iconSize={8}
                        wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }}
                    />
                </PieChart>
            </ResponsiveContainer>
            {/* Center label */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="text-center">
                    <div className="text-2xl font-bold text-slate-800 dark:text-slate-100">{total.toLocaleString()}</div>
                    <div className="text-xs text-slate-500 dark:text-slate-400">total</div>
                </div>
            </div>
        </div>
    );
}
