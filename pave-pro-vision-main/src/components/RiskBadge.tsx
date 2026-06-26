import type { RiskLevel } from '@/lib/types';
import { cn } from '@/lib/utils';

const riskStyles: Record<RiskLevel, string> = {
  Low: 'bg-risk-low/15 text-risk-low border-risk-low/30',
  Medium: 'bg-risk-medium/15 text-risk-medium border-risk-medium/30',
  High: 'bg-risk-high/15 text-risk-high border-risk-high/30',
};

export function RiskBadge({ level, className }: { level: RiskLevel; className?: string }) {
  return (
    <span className={cn('inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border', riskStyles[level], className)}>
      <span className={cn('w-1.5 h-1.5 rounded-full', {
        'bg-risk-low': level === 'Low',
        'bg-risk-medium': level === 'Medium',
        'bg-risk-high': level === 'High',
      })} />
      {level}
    </span>
  );
}
