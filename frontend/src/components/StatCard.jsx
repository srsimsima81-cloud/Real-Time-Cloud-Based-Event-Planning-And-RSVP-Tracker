export default function StatCard({label,value,accent}){return <div className="stat"><span>{label}</span><strong style={{color:accent||'inherit'}}>{value}</strong></div>}
