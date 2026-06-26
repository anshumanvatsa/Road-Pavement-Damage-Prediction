import { cn } from '@/lib/utils';
import { LucideIcon } from 'lucide-react';
import { motion } from 'framer-motion';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  variant?: 'default' | 'primary' | 'risk-low' | 'risk-medium' | 'risk-high';
}

const variantStyles = {
  default: 'border-border',
  primary: 'border-primary/30 glow-primary',
  'risk-low': 'border-risk-low/30 glow-risk-low',
  'risk-medium': 'border-risk-medium/30 glow-risk-medium',
  'risk-high': 'border-risk-high/30 glow-risk-high',
};

const iconStyles = {
  default: 'bg-muted text-muted-foreground',
  primary: 'bg-primary/15 text-primary',
  'risk-low': 'bg-risk-low/15 text-risk-low',
  'risk-medium': 'bg-risk-medium/15 text-risk-medium',
  'risk-high': 'bg-risk-high/15 text-risk-high',
};

export function StatCard({ title, value, subtitle, icon: Icon, variant = 'default' }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn('bg-card border rounded-lg p-5', variantStyles[variant])}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-mono uppercase tracking-widest text-muted-foreground mb-2">{title}</p>
          <p className="text-3xl font-bold tracking-tight text-foreground">{value}</p>
          {subtitle && <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>}
        </div>
        <div className={cn('w-10 h-10 rounded-lg flex items-center justify-center', iconStyles[variant])}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </motion.div>
  );
}
