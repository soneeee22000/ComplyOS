"use client";

import { Loader2, BookOpen, AlertTriangle, CheckCircle } from "lucide-react";
import { RiskBadge } from "@/components/risk-badge";
import type { AISystem, ClassificationResult } from "@/lib/api";

interface ClassificationPanelProps {
  system: AISystem | null;
  result: ClassificationResult | null;
  loading: boolean;
}

export function ClassificationPanel({
  system,
  result,
  loading,
}: ClassificationPanelProps) {
  if (!system) return null;

  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <h3 className="font-semibold text-foreground mb-1">{system.name}</h3>
      <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
        {system.description}
      </p>

      {loading && !result && (
        <div className="text-center py-8">
          <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2 text-primary" />
          <p className="text-sm text-muted-foreground">
            Analyzing against EU AI Act...
          </p>
          <p className="text-xs text-muted-foreground mt-1">
            RAG over 113 articles + 13 annexes
          </p>
        </div>
      )}

      {result && (
        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Risk Level</span>
            <RiskBadge level={result.risk_level} size="md" />
          </div>

          {result.annex_category !== "none" && (
            <div>
              <span className="text-sm text-muted-foreground">Category</span>
              <p className="text-sm font-medium text-foreground mt-0.5 capitalize">
                {result.annex_category.replace(/_/g, " ")}
              </p>
            </div>
          )}

          <div>
            <span className="text-sm text-muted-foreground">Confidence</span>
            <div className="flex items-center gap-2 mt-1">
              <div className="flex-1 h-2 rounded-full bg-secondary">
                <div
                  className="h-2 rounded-full bg-primary transition-all"
                  style={{ width: `${result.confidence_score * 100}%` }}
                />
              </div>
              <span className="text-xs font-medium text-foreground">
                {Math.round(result.confidence_score * 100)}%
              </span>
            </div>
          </div>

          <div>
            <span className="text-sm text-muted-foreground">
              Classification Reasoning
            </span>
            <p className="text-sm text-foreground mt-1 leading-relaxed">
              {result.reasoning}
            </p>
          </div>

          {result.cited_articles.length > 0 && (
            <div>
              <span className="text-sm text-muted-foreground flex items-center gap-1">
                <BookOpen className="w-3 h-3" />
                Cited Articles
              </span>
              <div className="flex flex-wrap gap-1.5 mt-1.5">
                {result.cited_articles.map((article) => (
                  <span
                    key={article}
                    className="px-2 py-0.5 rounded text-xs bg-secondary text-secondary-foreground font-mono"
                  >
                    {article}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="pt-3 border-t border-border">
            {result.requires_compliance ? (
              <div className="flex items-start gap-2 text-destructive">
                <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0" />
                <p className="text-sm">
                  This system requires full EU AI Act compliance including risk
                  management, technical documentation, and conformity
                  assessment.
                </p>
              </div>
            ) : (
              <div className="flex items-start gap-2 text-success">
                <CheckCircle className="w-4 h-4 mt-0.5 shrink-0" />
                <p className="text-sm">
                  This system has minimal compliance obligations. No conformity
                  assessment required.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {!loading && !result && (
        <div className="text-center py-6 text-muted-foreground">
          <p className="text-sm">
            Click &quot;Classify&quot; to analyze this system
          </p>
        </div>
      )}
    </div>
  );
}
