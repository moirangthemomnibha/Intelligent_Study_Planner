export function StatCard({ label, value, helper }) {
  return <article className="stat-card"><small>{label}</small><strong>{value}</strong><p>{helper}</p></article>;
}
