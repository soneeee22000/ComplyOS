"use client";

import { useState } from "react";
import {
  ChevronDown,
  ChevronRight,
  AlertCircle,
  AlertTriangle,
  CheckCircle,
  HelpCircle,
  Info,
  ArrowRight,
} from "lucide-react";
import type { ArticleStatus, SubRequirementStatus } from "@/lib/api";

interface RequirementTreeProps {
  requirementStatuses: ArticleStatus[];
  overallScore: number;
}

const STATUS_CONFIG: Record<
  string,
  { icon: typeof CheckCircle; style: string; label: string }
> = {
  compliant: {
    icon: CheckCircle,
    style: "text-success bg-success/10 border-success/20",
    label: "Compliant",
  },
  partial: {
    icon: AlertTriangle,
    style: "text-amber-600 bg-amber-50 border-amber-200",
    label: "Partial",
  },
  non_compliant: {
    icon: AlertCircle,
    style: "text-destructive bg-destructive/10 border-destructive/20",
    label: "Non-compliant",
  },
  not_assessed: {
    icon: HelpCircle,
    style: "text-muted-foreground bg-secondary border-border",
    label: "Not assessed",
  },
};

const SEVERITY_STYLES: Record<string, string> = {
  critical: "bg-destructive/10 text-destructive",
  major: "bg-amber-50 text-amber-700",
  minor: "bg-primary/10 text-primary",
};

function StatusBadge({ status }: { status: string }) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.not_assessed;
  const Icon = config.icon;

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full border text-xs font-medium ${config.style}`}
    >
      <Icon className="w-3 h-3" />
      {config.label}
    </span>
  );
}

function SubRequirementRow({ sub }: { sub: SubRequirementStatus }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="border-l-2 border-border ml-4 pl-4">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-start gap-3 py-2.5 text-left group"
      >
        <div className="shrink-0 mt-0.5">
          {expanded ? (
            <ChevronDown className="w-3.5 h-3.5 text-muted-foreground" />
          ) : (
            <ChevronRight className="w-3.5 h-3.5 text-muted-foreground" />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-mono text-muted-foreground bg-secondary px-1.5 py-0.5 rounded">
              {sub.paragraph}
            </span>
            <span className="text-sm font-medium text-foreground">
              {sub.title}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {sub.severity !== "minor" && (
            <span
              className={`text-xs px-1.5 py-0.5 rounded font-medium ${SEVERITY_STYLES[sub.severity] || ""}`}
            >
              {sub.severity}
            </span>
          )}
          <StatusBadge status={sub.status} />
        </div>
      </button>

      {expanded && (
        <div className="ml-6 pb-3 flex flex-col gap-3">
          {sub.finding && (
            <div>
              <span className="text-xs font-medium text-muted-foreground uppercase">
                Finding
              </span>
              <p className="text-sm text-foreground mt-0.5">{sub.finding}</p>
            </div>
          )}
          {sub.remediation && (
            <div>
              <span className="text-xs font-medium text-muted-foreground uppercase">
                Remediation
              </span>
              <p className="text-sm text-foreground mt-0.5">
                {sub.remediation}
              </p>
            </div>
          )}
          <div className="flex gap-6">
            {sub.estimated_effort && (
              <div>
                <span className="text-xs font-medium text-muted-foreground uppercase">
                  Effort
                </span>
                <p className="text-sm text-foreground mt-0.5 capitalize">
                  {sub.estimated_effort}
                </p>
              </div>
            )}
          </div>
          {sub.evidence_required.length > 0 && (
            <div>
              <span className="text-xs font-medium text-muted-foreground uppercase">
                Evidence Required
              </span>
              <ul className="mt-1 flex flex-col gap-1">
                {sub.evidence_required.map((ev) => (
                  <li
                    key={ev}
                    className="text-xs text-muted-foreground flex items-start gap-1.5"
                  >
                    <ArrowRight className="w-3 h-3 mt-0.5 shrink-0" />
                    {ev}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ArticleSection({ articleStatus }: { articleStatus: ArticleStatus }) {
  const [expanded, setExpanded] = useState(
    articleStatus.article_status === "non_compliant",
  );

  const nonCompliantCount = articleStatus.sub_requirement_statuses.filter(
    (s) => s.status === "non_compliant",
  ).length;
  const totalCount = articleStatus.sub_requirement_statuses.length;

  return (
    <div className="rounded-xl border border-border bg-card overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 p-4 text-left hover:bg-secondary/30 transition-colors"
      >
        <div className="shrink-0">
          {expanded ? (
            <ChevronDown className="w-4 h-4 text-muted-foreground" />
          ) : (
            <ChevronRight className="w-4 h-4 text-muted-foreground" />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-foreground">
            {articleStatus.article_title}
          </h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            {articleStatus.article_id
              .replace("_", " ")
              .replace("article ", "Article ")}{" "}
            {nonCompliantCount > 0
              ? `${nonCompliantCount}/${totalCount} gaps found`
              : `${totalCount} requirements checked`}
          </p>
        </div>
        <StatusBadge status={articleStatus.article_status} />
      </button>

      {expanded && (
        <div className="border-t border-border px-4 py-2">
          {articleStatus.sub_requirement_statuses.map((sub) => (
            <SubRequirementRow key={sub.sub_requirement_id} sub={sub} />
          ))}
        </div>
      )}
    </div>
  );
}

export function RequirementTree({
  requirementStatuses,
  overallScore,
}: RequirementTreeProps) {
  const totalSubs = requirementStatuses.reduce(
    (acc, a) => acc + a.sub_requirement_statuses.length,
    0,
  );
  const compliantSubs = requirementStatuses.reduce(
    (acc, a) =>
      acc +
      a.sub_requirement_statuses.filter((s) => s.status === "compliant").length,
    0,
  );

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-foreground">Requirement Tree</h3>
          <p className="text-xs text-muted-foreground mt-0.5">
            {compliantSubs}/{totalSubs} sub-requirements compliant across{" "}
            {requirementStatuses.length} articles
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Score:</span>
          <span
            className={`text-lg font-bold ${
              overallScore >= 70
                ? "text-success"
                : overallScore >= 40
                  ? "text-amber-600"
                  : "text-destructive"
            }`}
          >
            {overallScore}%
          </span>
        </div>
      </div>

      {requirementStatuses.map((articleStatus) => (
        <ArticleSection
          key={articleStatus.article_id}
          articleStatus={articleStatus}
        />
      ))}
    </div>
  );
}
