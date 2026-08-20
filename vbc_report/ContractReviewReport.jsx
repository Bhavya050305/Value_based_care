/*
Contract Review Report — renders the API response as tables/cards,
not walls of text. Two data sources per section, deliberately kept
separate:
  - report.data.*      -> exact numbers, rendered directly in <table>s
  - report.narrative.*  -> LLM-generated short insights/recommendations

Drop this into your Next.js project (e.g. components/ContractReviewReport.jsx)
and use it like:  <ContractReviewReport acoId="A1001" performanceYear={2023} />

Assumes Tailwind is already set up (matches your stated stack). No other
dependencies required — plain fetch, no extra libraries.
*/
import { useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_REPORT_API_URL || "http://localhost:8001";

const statusColor = {
  GOOD: "bg-green-100 text-green-800",
  ATTENTION: "bg-yellow-100 text-yellow-800",
  HIGH_RISK: "bg-red-100 text-red-800",
};

function StatusBadge({ status }) {
  return (
    <span className={`px-3 py-1 rounded-full text-sm font-semibold ${statusColor[status] || "bg-gray-100 text-gray-800"}`}>
      {status?.replace("_", " ") || "Unknown"}
    </span>
  );
}

function Section({ title, children }) {
  return (
    <div className="mb-8 border rounded-lg p-5 bg-white shadow-sm">
      <h2 className="text-lg font-semibold mb-3 text-gray-800">{title}</h2>
      {children}
    </div>
  );
}

function KeyValueTable({ rows }) {
  return (
    <table className="w-full text-sm">
      <tbody>
        {rows.map(([label, value], i) => (
          <tr key={i} className="border-b last:border-0">
            <td className="py-1.5 text-gray-500">{label}</td>
            <td className="py-1.5 text-right font-medium text-gray-900">{value ?? "Not available"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default function ContractReviewReport({ acoId, performanceYear = 2023 }) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch(`${API_BASE}/api/aco/${acoId}/report?performance_year=${performanceYear}`)
      .then((res) => {
        if (!res.ok) throw new Error(`Report request failed (${res.status})`);
        return res.json();
      })
      .then(setReport)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [acoId, performanceYear]);

  if (loading) return <div className="p-8 text-center text-gray-500">Generating contract review report…</div>;
  if (error) return <div className="p-8 text-center text-red-600">Error: {error}</div>;
  if (!report) return null;

  const { narrative, data } = report;
  const fin = data.financial || {};
  const qual = data.quality || {};
  const util = data.utilization || {};
  const pop = data.population || {};
  const ml = data.ml_segmentation || {};
  const anomaly = data.ml_anomaly || {};
  const profile = data.profile || {};

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* HEADER */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{profile.ACO_Name || acoId}</h1>
            <p className="text-gray-500 text-sm">
              ACO ID: {acoId} · State: {profile.ACO_State || "N/A"} · Year: {performanceYear} · Track: {profile.Current_Track || "N/A"}
            </p>
          </div>
          <StatusBadge status={narrative.overall_status} />
        </div>
        <div className="mt-3 text-3xl font-bold text-gray-800">{narrative.overall_score}/100</div>
        <p className="mt-2 text-gray-700 italic">{narrative.headline}</p>
      </div>

      {/* EXECUTIVE SUMMARY CARDS */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="border rounded-lg p-4 bg-white shadow-sm">
          <div className="text-xs text-gray-500 uppercase mb-1">Strengths</div>
          <ul className="text-sm space-y-1">
            {(narrative.strengths || []).map((s, i) => (
              <li key={i}>✓ {s}</li>
            ))}
          </ul>
        </div>
        <div className="border rounded-lg p-4 bg-white shadow-sm">
          <div className="text-xs text-gray-500 uppercase mb-1">Concerns</div>
          <ul className="text-sm space-y-1">
            {(narrative.concerns || []).map((c, i) => (
              <li key={i}>⚠ {c}</li>
            ))}
          </ul>
        </div>
        <div className="border rounded-lg p-4 bg-white shadow-sm">
          <div className="text-xs text-gray-500 uppercase mb-1">Priority Focus</div>
          <p className="text-sm">{narrative.priority_focus}</p>
        </div>
      </div>

      {/* FINANCIAL */}
      <Section title="Financial Performance">
        <KeyValueTable
          rows={[
            ["Benchmark", fin.ABtotBnchmk ? `$${Number(fin.ABtotBnchmk).toLocaleString()}` : null],
            ["Actual Expenditure", fin.ABtotExp ? `$${Number(fin.ABtotExp).toLocaleString()}` : null],
            ["Savings/Loss", fin.GenSaveLoss ? `$${Number(fin.GenSaveLoss).toLocaleString()}` : null],
            ["Earned Shared Savings", fin.EarnSaveLoss ? `$${Number(fin.EarnSaveLoss).toLocaleString()}` : null],
            ["Savings Rate", fin.SavingsLossPct != null ? `${fin.SavingsLossPct.toFixed(1)}%` : null],
            ["Expenditure Variance", fin.ExpenditureVariancePct != null ? `${fin.ExpenditureVariancePct.toFixed(1)}%` : null],
            ["PMPM", fin.PMPM != null ? `$${fin.PMPM.toFixed(2)}` : null],
            ["Benchmark PMPM", fin.BenchmarkPMPM != null ? `$${fin.BenchmarkPMPM.toFixed(2)}` : null],
          ]}
        />
        <p className="mt-3 text-sm text-gray-600">{narrative.financial_insight}</p>

        {data.financial_trend && data.financial_trend.length > 0 && (
          <table className="w-full text-sm mt-4 border-t pt-3">
            <thead>
              <tr className="text-left text-gray-500">
                <th className="py-1">Year</th>
                <th className="py-1 text-right">Benchmark</th>
                <th className="py-1 text-right">Expenditure</th>
                <th className="py-1 text-right">Savings</th>
                <th className="py-1 text-right">Savings %</th>
              </tr>
            </thead>
            <tbody>
              {data.financial_trend.map((row, i) => (
                <tr key={i} className="border-t">
                  <td className="py-1">{row.performance_year}</td>
                  <td className="py-1 text-right">${Number(row.benchmark || 0).toLocaleString()}</td>
                  <td className="py-1 text-right">${Number(row.expenditure || 0).toLocaleString()}</td>
                  <td className="py-1 text-right">${Number(row.savings || 0).toLocaleString()}</td>
                  <td className="py-1 text-right">{row.savings_rate != null ? `${(row.savings_rate * 100).toFixed(1)}%` : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Section>

      {/* QUALITY */}
      <Section title="Quality Performance">
        <KeyValueTable
          rows={[
            ["Quality Score", qual.quality_score],
            ["Previous Year", qual.previous_quality_score],
            ["YoY Change", qual.quality_change_yoy],
            ["Category", qual.quality_performance_category],
            ["Measures Improving", qual.measures_increasing],
            ["Measures Declining", qual.measures_decreasing],
            ["Attention Areas", qual.attention_area_count],
          ]}
        />
        <p className="mt-3 text-sm text-gray-600">{narrative.quality_insight}</p>
      </Section>

      {/* UTILIZATION */}
      <Section title="Utilization Performance">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500">
              <th className="py-1">Metric</th>
              <th className="py-1 text-right">Current</th>
              <th className="py-1 text-right">YoY Change</th>
            </tr>
          </thead>
          <tbody>
            {[
              ["ED visits / beneficiary", util.ed_visits_per_beneficiary, util.ed_utilization_change_yoy],
              ["Admissions / beneficiary", util.admissions_per_beneficiary, util.admission_change_yoy],
              ["SNF admissions / beneficiary", util.snf_admissions_per_beneficiary, null],
              ["Advanced imaging / beneficiary", util.advanced_imaging_per_beneficiary, util.advanced_imaging_change_yoy],
              ["EM visit intensity", util.em_visit_intensity, util.em_utilization_change_yoy],
            ].map(([label, val, change], i) => (
              <tr key={i} className="border-t">
                <td className="py-1.5">{label}</td>
                <td className="py-1.5 text-right">{val != null ? Number(val).toFixed(3) : "—"}</td>
                <td className={`py-1.5 text-right ${change > 0 ? "text-red-600" : change < 0 ? "text-green-600" : ""}`}>
                  {change != null ? `${(change * 100).toFixed(1)}%` : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="mt-2 text-xs text-gray-500">Utilization category: {util.utilization_category || "Not available"}</div>
        <p className="mt-3 text-sm text-gray-600">{narrative.utilization_insight}</p>
      </Section>

      {/* POPULATION */}
      <Section title="Population & Risk Profile">
        <KeyValueTable
          rows={[
            ["Assigned Beneficiaries", pop.assigned_beneficiaries],
            ["Age 65-74", pop.age_65_74_pct != null ? `${pop.age_65_74_pct.toFixed(1)}%` : null],
            ["Age 75-84", pop.age_75_84_pct != null ? `${pop.age_75_84_pct.toFixed(1)}%` : null],
            ["Age 85+", pop.age_85_plus_pct != null ? `${pop.age_85_plus_pct.toFixed(1)}%` : null],
            ["Dual Eligible", pop.dual_eligible_pct != null ? `${pop.dual_eligible_pct.toFixed(1)}%` : null],
            ["Disabled", pop.disabled_pct != null ? `${pop.disabled_pct.toFixed(1)}%` : null],
            ["ESRD", pop.esrd_pct != null ? `${pop.esrd_pct.toFixed(1)}%` : null],
            ["Average Risk Score", pop.average_available_risk_score],
            ["Risk Category", pop.risk_profile_category],
          ]}
        />
        <p className="mt-3 text-sm text-gray-600">{narrative.population_insight}</p>
      </Section>

      {/* PROVIDER COMPOSITION + SERVICE VARIATION */}
      <Section title="Provider Composition & Service Variation">
        <KeyValueTable
          rows={[
            ["Hospitals", profile.N_Hosp],
            ["PCPs", profile.N_PCP],
            ["Specialists", profile.N_Spec],
            ["Nurse Practitioners", profile.N_NP],
            ["Physician Assistants", profile.N_PA],
          ]}
        />
        {data.service_variation && data.service_variation.length > 0 && (
          <table className="w-full text-sm mt-4 border-t pt-3">
            <thead>
              <tr className="text-left text-gray-500">
                <th className="py-1">Service</th>
                <th className="py-1 text-right">Total Payment</th>
                <th className="py-1 text-right">Utilization Δ</th>
                <th className="py-1">Flag</th>
              </tr>
            </thead>
            <tbody>
              {data.service_variation.map((row, i) => (
                <tr key={i} className="border-t">
                  <td className="py-1">{row.HCPCS_Desc || row.service_category}</td>
                  <td className="py-1 text-right">${Number(row.total_payment || 0).toLocaleString()}</td>
                  <td className="py-1 text-right">{row.utilization_change_pct != null ? `${row.utilization_change_pct.toFixed(1)}%` : "—"}</td>
                  <td className="py-1">{row.high_cost_service ? "🔴 High cost" : ""}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Section>

      {/* DRIVERS */}
      <Section title="Performance Drivers">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-xs text-green-700 uppercase mb-2">Positive Drivers</div>
            <ul className="text-sm space-y-1">
              {(data.drivers?.positive_drivers || []).map((d, i) => (
                <li key={i}>🟢 {d.driver}: {d.value}{d.unit}</li>
              ))}
            </ul>
          </div>
          <div>
            <div className="text-xs text-red-700 uppercase mb-2">Attention Drivers</div>
            <ul className="text-sm space-y-1">
              {(data.drivers?.attention_drivers || []).map((d, i) => (
                <li key={i}>🔴 {d.driver}: {d.value}{d.unit}</li>
              ))}
            </ul>
          </div>
        </div>
      </Section>

      {/* ML ASSESSMENT */}
      <Section title="ML Risk Assessment">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <div className="text-xs text-gray-500 uppercase mb-1">Performance Segment</div>
            <div className="text-lg font-semibold">{ml.performance_segment || "Not available"}</div>
            <div className="text-sm text-gray-500">Cluster {ml.cluster_id ?? "—"} · Index {ml.performance_index?.toFixed(2) ?? "—"}</div>
          </div>
          <div>
            <div className="text-xs text-gray-500 uppercase mb-1">Anomaly Status</div>
            <div className="text-lg font-semibold">
              {anomaly.is_anomaly ? "⚠️ Anomaly Detected" : "No Anomaly Detected"}
            </div>
            <div className="text-sm text-gray-500">
              {anomaly.severity ? `Severity: ${anomaly.severity}` : `Risk Level: ${anomaly.risk_level || "—"}`}
            </div>
          </div>
        </div>
        <p className="mt-3 text-sm text-gray-600">{narrative.ml_segmentation_explanation}</p>
        <p className="mt-1 text-sm text-gray-600">{narrative.anomaly_explanation}</p>
      </Section>

      {/* PEER TARGETS (placeholder until Part 6 is built) */}
      <Section title="Peer Benchmark & Target Finder">
        <p className="text-sm text-gray-500 italic">Not available yet — peer target finder is still in progress.</p>
      </Section>

      {/* RECOMMENDATIONS */}
      <Section title="Recommended Actions">
        <div className="space-y-3">
          {(narrative.recommendations || []).map((rec, i) => (
            <div key={i} className="border-l-4 pl-3" style={{ borderColor: rec.priority === "HIGH" ? "#dc2626" : rec.priority === "MEDIUM" ? "#f59e0b" : "#10b981" }}>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold uppercase">{rec.priority}</span>
                <span className="font-medium">{rec.issue}</span>
              </div>
              <p className="text-sm text-gray-600">Evidence: {rec.evidence}</p>
              <p className="text-sm text-gray-800">Action: {rec.action}</p>
            </div>
          ))}
        </div>
      </Section>

      {/* MEETING QUESTIONS */}
      <Section title="Provider Review Meeting Questions">
        <ul className="text-sm space-y-2 list-disc list-inside">
          {(narrative.meeting_questions || []).map((q, i) => (
            <li key={i}>{q}</li>
          ))}
        </ul>
      </Section>
    </div>
  );
}
