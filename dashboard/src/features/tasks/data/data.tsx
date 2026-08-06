import { TriangleAlert, CircleCheckBig, Clock, TrendingDown, CheckCircle2 } from 'lucide-react'

export const labels = [
  { value: 'bug', label: 'Bug' },
  { value: 'feature', label: 'Feature' },
  { value: 'documentation', label: 'Documentation' },
]

export type Severity = 'critical' | 'warning' | 'good' | 'neutral'

export const severityToBadgeVariant: Record<Severity, 'destructive' | 'warning' | 'success' | 'secondary'> = {
  critical: 'destructive',
  warning: 'warning',
  good: 'success',
  neutral: 'secondary',
}

// __STATUSES_BLOCK_START__
export const statuses: {
  label: string
  value: string
  icon: typeof TriangleAlert
  severity: Severity
}[] = [
  { label: 'Over Budget', value: 'over_budget:critical', icon: TriangleAlert, severity: 'critical' as Severity },
  { label: 'Margin Declining', value: 'margin_declining:warning', icon: TrendingDown, severity: 'warning' as Severity },
  { label: 'On Track', value: 'on_track:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Within Budget', value: 'within_budget:good', icon: CircleCheckBig, severity: 'good' as Severity },
  { label: 'Completed', value: 'completed:neutral', icon: CheckCircle2, severity: 'neutral' as Severity },
  { label: 'Pending', value: 'pending', icon: Clock, severity: 'neutral' as Severity },
]
// __STATUSES_BLOCK_END__
