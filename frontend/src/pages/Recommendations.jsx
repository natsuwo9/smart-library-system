import { useEffect, useState } from "react";
import { getMembers, getMemberRecommendations, getLoans } from "../api";

export default function Recommendations() {
  const [members, setMembers] = useState([]);
  const [memberId, setMemberId] = useState("");
  const [recs, setRecs] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getMembers()
      .then((m) => {
        setMembers(m);
        if (m.length) setMemberId(String(m[0].id));
      })
      .catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    if (!memberId) return;
    setLoading(true);
    Promise.all([
      getMemberRecommendations(memberId, 8),
      getLoans({ member_id: memberId }),
    ])
      .then(([r, h]) => {
        setRecs(r);
        setHistory(h);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [memberId]);

  const selectedMember = members.find((m) => String(m.id) === String(memberId));

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Recommendations</h1>
          <p>Personalized picks from the recommendation engine</p>
        </div>
        <select
          value={memberId}
          onChange={(e) => setMemberId(e.target.value)}
          style={{ width: 240 }}
        >
          {members.map((m) => (
            <option key={m.id} value={m.id}>
              {m.name}
            </option>
          ))}
        </select>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {selectedMember && (
        <p className="muted">
          Showing recommendations for <strong>{selectedMember.name}</strong> based on{" "}
          {history.length} past loan{history.length === 1 ? "" : "s"}.
        </p>
      )}

      <div className="section-title">Recommended for this member</div>
      {loading ? (
        <div className="card empty">Loading…</div>
      ) : recs.length === 0 ? (
        <div className="card empty">No recommendations available.</div>
      ) : (
        <div className="grid book-grid">
          {recs.map((r) => (
            <div key={r.book.id} className="card rec-card">
              <div className="title">{r.book.title}</div>
              <div className="author">by {r.book.author}</div>
              <span className="badge genre" style={{ alignSelf: "flex-start" }}>
                {r.book.genre}
              </span>
              <div className="reason">{r.reason}</div>
              <div className="flex-between" style={{ marginTop: 4 }}>
                <span className="muted" style={{ fontSize: 12 }}>
                  match score
                </span>
                <span style={{ fontSize: 12, fontWeight: 600 }}>
                  {Math.round(r.score * 100)}%
                </span>
              </div>
              <div className="score-bar">
                <div style={{ width: `${Math.round(r.score * 100)}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="section-title">Borrowing history</div>
      <div className="card" style={{ padding: 0 }}>
        <table>
          <thead>
            <tr>
              <th>Book</th>
              <th>Genre</th>
              <th>Borrowed</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {history.map((l) => (
              <tr key={l.id}>
                <td>{l.book_title}</td>
                <td className="muted">{l.book_author}</td>
                <td className="muted">
                  {new Date(l.borrowed_at).toLocaleDateString()}
                </td>
                <td>
                  {l.returned_at ? (
                    <span className="badge muted">Returned</span>
                  ) : l.is_overdue ? (
                    <span className="badge danger">Overdue</span>
                  ) : (
                    <span className="badge success">On loan</span>
                  )}
                </td>
              </tr>
            ))}
            {history.length === 0 && (
              <tr>
                <td colSpan="4" className="empty">
                  No borrowing history — showing popular picks above.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}
