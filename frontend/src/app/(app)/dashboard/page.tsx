"use client";

import { useEffect, useState } from "react";
import {
  Server,
  AlertTriangle,
  Shield,
  Clock,
  TrendingUp,
  AlertCircle,
} from "lucide-react";
import { MetricCard } from "@/components/metric-card";
import type { DashboardMetrics } from "@/lib/api";
import { api } from "@/lib/api";

const FALLBACK_METRICS: DashboardMetrics = {
  total_systems: 0,
  high_risk_count: 0,
  limited_risk_count: 0,
  minimal_risk_count: 0,
  unclassified_count: 0,
  average_compliance_score: 0,
  days_until_deadline: Math.ceil(
    (new Date("2026-08-02").getTime() - Date.now()) / (1000 * 60 * 60 * 24),
  ),
  critical_gaps_count: 0,
};

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics>(FALLBACK_METRICS);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getDashboard()
      .then(setMetrics)
      .catch(() => setMetrics(FALLBACK_METRICS))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-foreground">
          Compliance Dashboard
        </h1>
        <p className="text-muted-foreground mt-1">
          EU AI Act compliance status across your AI systems
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        <MetricCard
          title="Total AI Systems"
          value={loading ? "..." : metrics.total_systems}
          subtitle="Registered for assessment"
          icon={Server}
        />
        <MetricCard
          title="High-Risk Systems"
          value={loading ? "..." : metrics.high_risk_count}
          subtitle="Require full compliance"
          icon={AlertTriangle}
          variant={metrics.high_risk_count > 0 ? "danger" : "default"}
        />
        <MetricCard
          title="Avg Compliance Score"
          value={
            loading ? "..." : `${Math.round(metrics.average_compliance_score)}%`
          }
          subtitle="Across assessed systems"
          icon={TrendingUp}
          variant={
            metrics.average_compliance_score >= 70
              ? "success"
              : metrics.average_compliance_score >= 40
                ? "warning"
                : "danger"
          }
        />
        <MetricCard
          title="Days Until Deadline"
          value={loading ? "..." : metrics.days_until_deadline}
          subtitle="August 2, 2026"
          icon={Clock}
          variant={metrics.days_until_deadline < 90 ? "danger" : "warning"}
        />
        <MetricCard
          title="Critical Gaps"
          value={loading ? "..." : metrics.critical_gaps_count}
          subtitle="Blocking compliance"
          icon={AlertCircle}
          variant={metrics.critical_gaps_count > 0 ? "danger" : "success"}
        />
        <MetricCard
          title="Compliant Systems"
          value={
            loading
              ? "..."
              : metrics.minimal_risk_count + metrics.limited_risk_count
          }
          subtitle="Limited or minimal risk"
          icon={Shield}
          variant="success"
        />
      </div>

      <div className="rounded-xl border border-border bg-card p-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">
          Getting Started
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0">
              <span className="text-sm font-bold text-primary-foreground">
                1
              </span>
            </div>
            <div>
              <h3 className="font-medium text-foreground">Register Systems</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Add your AI systems with descriptions of what they do and how
                they are used.
              </p>
            </div>
          </div>
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0">
              <span className="text-sm font-bold text-primary-foreground">
                2
              </span>
            </div>
            <div>
              <h3 className="font-medium text-foreground">Classify Risk</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Our AI agent classifies each system per the EU AI Act with cited
                legal reasoning.
              </p>
            </div>
          </div>
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0">
              <span className="text-sm font-bold text-primary-foreground">
                3
              </span>
            </div>
            <div>
              <h3 className="font-medium text-foreground">Get Compliant</h3>
              <p className="text-sm text-muted-foreground mt-1">
                Review gaps, generate documentation, and track progress toward
                the August 2026 deadline.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
