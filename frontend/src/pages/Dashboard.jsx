import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import {
  getSummary,
  getPopularBooks,
  getGenreDistribution,
  getLoanTrends,
  getTopMembers,
} from "../api";

const COLORS = [
  "#4f46e5",
  "#0ea5e9",
  "#16a34a",
  "#d97706",
  "#dc2626",
  "#9333ea",
  "#0891b2",
  "#ca8a04",
  "#db2777",
];

function StatCard({ label, value, tone }) {
  return (
    <div className="card stat-card">
      <div className="label">{label}</div>
      <div className={`value ${tone || ""}`}>{value}</div>
    </div>
  );
}

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [popular, setPopular] = useState([]);
  const [genres, setGenres] = useState([]);
  const [trends, setTrends] = useState([]);
  const [topMembers, setTopMembers] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      getSummary(),
      getPopularBooks(7),
      getGenreDistribution(),
      getLoanTrends(12),
      getTopMembers(5),
    ])
      .then(([s, p, g, t, m]) => {
        setSummary(s);
        setPopular(p);
        setGenres(g);
        setTrends(t);
        setTopMembers(m);
      })
      .catch((e) => setError(e.message));
  }, []);

  const trendData = trends.map((t) => ({
    week: t.week.slice(5),
    Loans: t.loan_count,
  }));

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Analytics Dashboard</h1>
          <p>Library activity at a glance</p>
        </div>
      </div>

      {error && <div className="error-banner">Failed to load data: {error}</div>}

      {summary && (
        <div className="grid stat-grid">
          <StatCard label="Total Titles" value={summary.total_books} />
          <StatCard label="Total Copies" value={summary.total_copies} />
          <StatCard
            label="Available Now"
            value={summary.available_copies}
            tone="success"
          />
          <StatCard label="Active Loans" value={summary.active_loans} />
          <StatCard
            label="Overdue"
            value={summary.overdue_loans}
            tone={summary.overdue_loans > 0 ? "danger" : ""}
          />
          <StatCard label="Members" value={summary.total_members} />
        </div>
      )}

      <div className="grid charts-grid">
        <div className="card chart-card">
          <h3>Loan Trends (last 12 weeks)</h3>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#eef2f7" />
              <XAxis dataKey="week" fontSize={12} />
              <YAxis allowDecimals={false} fontSize={12} />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="Loans"
                stroke="#4f46e5"
                strokeWidth={2}
                dot={{ r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="card chart-card">
          <h3>Most Borrowed Titles</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={popular} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#eef2f7" />
              <XAxis type="number" allowDecimals={false} fontSize={12} />
              <YAxis
                type="category"
                dataKey="title"
                width={140}
                fontSize={11}
                tickFormatter={(v) => (v.length > 20 ? v.slice(0, 19) + "…" : v)}
              />
              <Tooltip />
              <Bar dataKey="loan_count" name="Loans" fill="#0ea5e9" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card chart-card">
          <h3>Loans by Genre</h3>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={genres}
                dataKey="loan_count"
                nameKey="genre"
                cx="50%"
                cy="50%"
                outerRadius={90}
                label={(e) => e.genre}
                fontSize={11}
              >
                {genres.map((entry, i) => (
                  <Cell key={entry.genre} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card chart-card">
          <h3>Top Members</h3>
          {topMembers.length === 0 ? (
            <p className="muted">No loan activity yet.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Member</th>
                  <th>Email</th>
                  <th>Loans</th>
                </tr>
              </thead>
              <tbody>
                {topMembers.map((m) => (
                  <tr key={m.id}>
                    <td>{m.name}</td>
                    <td className="muted">{m.email}</td>
                    <td>
                      <span className="badge muted">{m.loan_count}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </>
  );
}
