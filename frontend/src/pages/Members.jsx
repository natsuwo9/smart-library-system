import { useEffect, useState } from "react";
import { getMembers, createMember, deleteMember } from "../api";
import Modal from "../components/Modal.jsx";

export default function Members() {
  const [members, setMembers] = useState([]);
  const [adding, setAdding] = useState(false);
  const [form, setForm] = useState({ name: "", email: "" });
  const [formError, setFormError] = useState("");
  const [error, setError] = useState("");

  const load = () =>
    getMembers().then(setMembers).catch((e) => setError(e.message));

  useEffect(() => {
    load();
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    setFormError("");
    try {
      await createMember(form);
      setAdding(false);
      setForm({ name: "", email: "" });
      load();
    } catch (err) {
      setFormError(err.response?.data?.detail || err.message);
    }
  };

  const handleDelete = async (m) => {
    if (!window.confirm(`Remove member "${m.name}"?`)) return;
    try {
      await deleteMember(m.id);
      load();
    } catch (err) {
      window.alert(err.response?.data?.detail || err.message);
    }
  };

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Members</h1>
          <p>{members.length} registered members</p>
        </div>
        <button className="btn" onClick={() => setAdding(true)}>
          + Add Member
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="card" style={{ padding: 0 }}>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Joined</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {members.map((m) => (
              <tr key={m.id}>
                <td>{m.name}</td>
                <td className="muted">{m.email}</td>
                <td className="muted">
                  {new Date(m.joined_at).toLocaleDateString()}
                </td>
                <td style={{ textAlign: "right" }}>
                  <button
                    className="btn danger small"
                    onClick={() => handleDelete(m)}
                  >
                    Remove
                  </button>
                </td>
              </tr>
            ))}
            {members.length === 0 && (
              <tr>
                <td colSpan="4" className="empty">
                  No members yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {adding && (
        <Modal
          title="Add Member"
          onClose={() => {
            setAdding(false);
            setFormError("");
          }}
        >
          <form onSubmit={submit}>
            {formError && <div className="error-banner">{formError}</div>}
            <div className="field" style={{ marginBottom: 14 }}>
              <label>Name</label>
              <input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                required
              />
            </div>
            <div className="field">
              <label>Email</label>
              <input
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                required
              />
            </div>
            <div className="modal-actions">
              <button
                type="button"
                className="btn secondary"
                onClick={() => setAdding(false)}
              >
                Cancel
              </button>
              <button type="submit" className="btn">
                Save
              </button>
            </div>
          </form>
        </Modal>
      )}
    </>
  );
}
