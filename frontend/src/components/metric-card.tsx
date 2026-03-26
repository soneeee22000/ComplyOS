import type { LucideIcon } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  variant?: "default" | "warning" | "danger" | "success";
}

const variantStyles = {
  default: "bg-card border-border",
  warning: "bg-accent/5 border-accent/20",
  danger: "bg-destructive/5 border-destructive/20",
  success: "bg-success/5 border-success/20",
};

const iconVariantStyles = {
  default: "bg-secondary text-secondary-foreground",
  warning: "bg-accent/10 text-accent",
  danger: "bg-destructive/10 text-destructive",
  success: "bg-success/10 text-success",
};

export function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = "default",
}: MetricCardProps) {
  return (
    <div className={`rounded-xl border p-5 ${variantStyles[variant]}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-muted-foreground">{title}</p>
          <p className="text-3xl font-bold mt-1 text-foreground">{value}</p>
          {subtitle && (
            <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
          )}
        </div>
        <div
          className={`w-10 h-10 rounded-lg flex items-center justify-center ${iconVariantStyles[variant]}`}
        >
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </div>
  );
}
