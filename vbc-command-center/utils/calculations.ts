import { ProviderRecord } from '../types/provider';

export function calculatePaymentPerBeneficiary(totalPayment: number, totalBenes: number): number {
  if (!totalBenes || totalBenes <= 0) return 0;
  return totalPayment / totalBenes;
}

export function calculateServicesPerBeneficiary(totalServices: number, totalBenes: number): number {
  if (!totalBenes || totalBenes <= 0) return 0;
  return totalServices / totalBenes;
}

export function calculateDualEligibilityRate(dualCnt: number, nonDualCnt: number): { dualPct: number; nonDualPct: number } {
  const total = dualCnt + nonDualCnt;
  if (!total || total <= 0) return { dualPct: 0, nonDualPct: 100 };
  return {
    dualPct: Number(((dualCnt / total) * 100).toFixed(1)),
    nonDualPct: Number(((nonDualCnt / total) * 100).toFixed(1)),
  };
}

export function calculateGenderDistribution(femaleCnt: number, maleCnt: number): { femalePct: number; malePct: number } {
  const total = femaleCnt + maleCnt;
  if (!total || total <= 0) return { femalePct: 50, malePct: 50 };
  return {
    femalePct: Number(((femaleCnt / total) * 100).toFixed(1)),
    malePct: Number(((maleCnt / total) * 100).toFixed(1)),
  };
}

export function calculatePaymentVariance(payment: number, allowed: number): number {
  if (!allowed || allowed <= 0) return 0;
  return ((payment - allowed) / allowed) * 100;
}
