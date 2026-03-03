import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';
import Papa from 'papaparse';
import type { Restaurant, Segment, DashboardData, CuisineScore, SegmentCount } from '@/data/restaurantTypes';
import { REGION_MAP, CUISINE_MAP } from '@/data/restaurantTypes';

// Path to data files — up two levels from the Next.js project root
const DATA_DIR = path.join(process.cwd(), '..', '..', 'Data', 'Processed');

function readCSV(filename: string): Record<string, string>[] {
    const fullPath = path.join(DATA_DIR, filename);
    const content = fs.readFileSync(fullPath, 'utf-8');
    const result = Papa.parse<Record<string, string>>(content, {
        header: true,
        skipEmptyLines: true,
    });
    return result.data;
}

export async function GET() {
    try {
        // Read predictions CSV
        const predictions = readCSV('Dashboard_Predictions.csv');

        // Read master data CSV for extra columns
        const masterRaw = readCSV('master_all_data.csv');
        const masterMap = new Map<string, Record<string, string>>();
        for (const row of masterRaw) {
            if (row.restaurant_id) masterMap.set(row.restaurant_id, row);
        }

        // Merge + decode
        const restaurants: Restaurant[] = predictions
            .filter((r) => r.restaurant_id && r.ml_priority_score)
            .map((r) => {
                const master = masterMap.get(r.restaurant_id) ?? {};
                const regionKey = parseInt(r.region_encoded ?? '0');
                const cuisineKey = parseInt(r.cuisine_encoded ?? '0');
                const rawName =
                    master.restaurant_name_en ||
                    master.name ||
                    r.restaurant_name_en ||
                    `Restaurant ${r.restaurant_id}`;

                return {
                    restaurant_id: parseFloat(r.restaurant_id),
                    restaurant_name: rawName,
                    ML_Predicted_Segment: (r.ML_Predicted_Segment || r.target_label || 'Stable') as Segment,
                    ml_priority_score: parseFloat(r.ml_priority_score) || 0,
                    overall_rank: parseFloat(r.overall_rank) || 0,
                    cuisine: CUISINE_MAP[cuisineKey] ?? 'Other',
                    region: REGION_MAP[regionKey] ?? 'Unknown',
                    prob_rising: parseFloat(r.prob_rising) || 0,
                    prob_hidden_gem: parseFloat(r.prob_hidden_gem) || 0,
                    prob_stable: parseFloat(r.prob_stable) || 0,
                    prob_declining: parseFloat(r.prob_declining) || 0,
                    gmaps_rating: parseFloat(r.gmaps_rating || master.gmaps_rating) || undefined,
                    momentum_score: parseFloat(r.momentum_score) || undefined,
                    internal_score: parseFloat(r.expected_kpi) || undefined,          // expected_kpi used as 'internal' axis
                    weighted_rating_score: parseFloat(r.weighted_rating_score) || undefined,
                    external_quality_score: parseFloat(r.external_quality_score) || undefined,
                    total_revenue: parseFloat(master.total_revenue) || undefined,
                    total_bookings: parseFloat(master.total_bookings) || undefined,
                    avg_revenue_per_booking: parseFloat(master.avg_revenue_per_booking) || undefined,
                    no_show_rate: parseFloat(master.no_show_rate) || undefined,
                } satisfies Restaurant;
            })
            .sort((a, b) => b.ml_priority_score - a.ml_priority_score);

        // Build KPIs
        const total = restaurants.length;
        const rising = restaurants.filter((r) => r.ML_Predicted_Segment === 'Rising').length;
        const hiddenGem = restaurants.filter((r) => r.ML_Predicted_Segment === 'Hidden Gem').length;
        const stable = restaurants.filter((r) => r.ML_Predicted_Segment === 'Stable').length;
        const declining = restaurants.filter((r) => r.ML_Predicted_Segment === 'Declining').length;
        const avgScore = total > 0 ? restaurants.reduce((s, r) => s + r.ml_priority_score, 0) / total : 0;

        // Cuisine avg scores
        const cuisineGroups: Record<string, number[]> = {};
        for (const r of restaurants) {
            if (!cuisineGroups[r.cuisine]) cuisineGroups[r.cuisine] = [];
            cuisineGroups[r.cuisine].push(r.ml_priority_score);
        }
        const cuisineScores: CuisineScore[] = Object.entries(cuisineGroups)
            .map(([cuisine, scores]) => ({
                cuisine,
                avgScore: scores.reduce((a, b) => a + b, 0) / scores.length,
            }))
            .sort((a, b) => b.avgScore - a.avgScore);

        const topCuisine = cuisineScores[0]?.cuisine ?? '';

        // Segment counts for donut
        const segmentCounts: SegmentCount[] = (
            ['Rising', 'Hidden Gem', 'Stable', 'Declining'] as Segment[]
        ).map((segment) => ({
            segment,
            count: restaurants.filter((r) => r.ML_Predicted_Segment === segment).length,
        }));

        const data: DashboardData = {
            restaurants: restaurants.slice(0, 300), // top 300 for performance
            kpis: { total, rising, hiddenGem, stable, declining, actionable: rising + hiddenGem, avgScore, topCuisine },
            cuisineScores,
            segmentCounts,
        };

        return NextResponse.json(data);
    } catch (err) {
        console.error('Dashboard API error:', err);
        return NextResponse.json({ error: String(err) }, { status: 500 });
    }
}
