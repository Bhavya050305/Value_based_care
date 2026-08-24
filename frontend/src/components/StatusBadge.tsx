import React from 'react';

interface StatusBadgeProps {
  type: 'risk' | 'status' | 'outcome' | 'priority';
  value: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ type, value }) => {
  const normalized = value.toUpperCase().trim();

  let classes = 'px-2.5 py-1 text-xs font-semibold rounded-full border ';

  if (type === 'risk' || type === 'priority') {
    if (normalized === 'HIGH' || normalized === 'AT RISK') {
      classes += 'bg-vbc-red-light text-vbc-red-dark border-vbc-red/20';
    } else if (normalized === 'MEDIUM' || normalized === 'NEEDS ATTENTION') {
      classes += 'bg-vbc-orange-light text-vbc-orange-dark border-vbc-orange/20';
    } else {
      classes += 'bg-vbc-green-light text-vbc-green-dark border-vbc-green/20';
    }
  } else if (type === 'outcome') {
    if (normalized === 'LOSS') {
      classes += 'bg-vbc-red-light text-vbc-red border-vbc-red/25';
    } else {
      classes += 'bg-vbc-green-light text-vbc-green border-vbc-green/25';
    }
  } else if (type === 'status') {
    if (normalized === 'AT RISK') {
      classes += 'bg-vbc-red-light text-vbc-red-dark border-vbc-red/20';
    } else if (normalized === 'NEEDS ATTENTION') {
      classes += 'bg-vbc-orange-light text-vbc-orange-dark border-vbc-orange/20';
    } else {
      classes += 'bg-vbc-green-light text-vbc-green-dark border-vbc-green/20';
    }
  }

  return <span className={classes}>{value}</span>;
};
export default StatusBadge;
