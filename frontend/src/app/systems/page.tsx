"use client";

import { useEffect, useState } from "react";
import { Plus, Loader2, Sparkles, Search } from "lucide-react";
import { RiskBadge } from "@/components/risk-badge";
import { SystemForm } from "@/components/system-form";
import { ClassificationPanel } from "@/components/classification-panel";
import { GapAnalysisPanel } from "@/components/gap-analysis-panel";
import type { AISystem, ClassificationResult } from "@/lib/api";
import { api } from "@/lib/api";

export default function SystemsPage() {
  const [systems, setSystems] = useState<AISystem[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [selectedSystem, setSelectedSystem] = useState<AISystem | null>(null);
  const [classificationResult, setClassificationResult] =
    useState<ClassificationResult | null>(null);
  const [classifying, setClassifying] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const loadSystems = () => {
    api
      .getSystems()
      .then(setSystems)
      .catch(() => setSystems([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadSystems();
  }, []);

  const handleSystemCreated = (system: AISystem) => {
    setSystems((prev) => [system, ...prev]);
    setShowForm(false);
  };

  const handleClassify = async (system: AISystem) => {
    setClassifying(system.id);
    setClassificationResult(null);
    setSelectedSystem(system);

    try {
      const result = await api.classifySystem(system.id);
      setClassificationResult(result);
      loadSystems();
    } catch (error) {
      console.error("Classification failed:", error);
    } finally {
      setClassifying(null);
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-foreground">AI Systems</h1>
          <p className="text-muted-foreground mt-1">
            Register and classify your AI systems
          </p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add System
        </button>
      </div>

      {showForm && (
        <SystemForm
          onCreated={handleSystemCreated}
          onCancel={() => setShowForm(false)}
        />
      )}

      <div className="flex gap-6">
        <div className="flex-1">
          {loading ? (
            <div className="text-center py-12 text-muted-foreground">
              <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
              Loading systems...
            </div>
          ) : systems.length === 0 ? (
            <div className="text-center py-12 rounded-xl border border-dashed border-border">
              <Search className="w-8 h-8 text-muted-foreground mx-auto mb-3" />
              <p className="text-muted-foreground">
                No AI systems registered yet
              </p>
              <p className="text-sm text-muted-foreground mt-1">
                Click &quot;Add System&quot; to get started
              </p>
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              {systems.map((system) => (
                <div
                  key={system.id}
                  className={`rounded-xl border p-4 transition-colors cursor-pointer ${
                    selectedSystem?.id === system.id
                      ? "border-primary bg-primary/5"
                      : "border-border bg-card hover:border-primary/30"
                  }`}
                  onClick={() => {
                    setSelectedSystem(system);
                    if (system.risk_level) {
                      setClassificationResult({
                        risk_level: system.risk_level,
                        annex_category: system.annex_category || "none",
                        confidence_score: system.confidence_score || 0,
                        reasoning: system.classification_reasoning || "",
                        cited_articles: [],
                        requires_compliance: system.risk_level === "high",
                      });
                    } else {
                      setClassificationResult(null);
                    }
                  }}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h3 className="font-medium text-foreground truncate">
                          {system.name}
                        </h3>
                        <RiskBadge level={system.risk_level} />
                      </div>
                      <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                        {system.description}
                      </p>
                      {system.department && (
                        <p className="text-xs text-muted-foreground mt-2">
                          {system.department}
                        </p>
                      )}
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleClassify(system);
                      }}
                      disabled={classifying === system.id}
                      className="ml-4 flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-secondary text-secondary-foreground text-xs font-medium hover:bg-secondary/80 transition-colors disabled:opacity-50 shrink-0"
                    >
                      {classifying === system.id ? (
                        <>
                          <Loader2 className="w-3 h-3 animate-spin" />
                          Classifying...
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-3 h-3" />
                          {system.risk_level ? "Re-classify" : "Classify"}
                        </>
                      )}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {(selectedSystem || classificationResult) && (
          <div className="w-96 shrink-0">
            <ClassificationPanel
              system={selectedSystem}
              result={classificationResult}
              loading={classifying !== null}
            />
            {selectedSystem && selectedSystem.risk_level === "high" && (
              <GapAnalysisPanel system={selectedSystem} />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
