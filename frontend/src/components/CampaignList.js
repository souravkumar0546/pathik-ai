import {
  useEffect,
  useState,
  forwardRef,
  useImperativeHandle,
} from "react";
import {
  getCampaigns,
  publishCampaign,
  pauseCampaign,
} from "../api/campaigns";

const CampaignList = forwardRef((props, ref) => {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);

  async function loadCampaigns() {
    try {
      setLoading(true);
      const data = await getCampaigns();
      setCampaigns(data);
    } catch (err) {
      alert(err.message || "Failed to load campaigns");
    } finally {
      setLoading(false);
    }
  }

  async function handlePublish(id) {
    try {
      setActionLoading(id);
      await publishCampaign(id);
      await loadCampaigns();
    } catch (err) {
      if (err.message?.includes("DEVELOPER_TOKEN_NOT_APPROVED")) {
        alert(
          "Publishing is disabled until Google Ads developer access is approved."
        );
      } else {
        alert(err.message || "Failed to publish campaign");
      }
    } finally {
      setActionLoading(null);
    }
  }

  async function handlePause(id) {
    try {
      setActionLoading(id);
      await pauseCampaign(id);
      await loadCampaigns();
    } catch (err) {
      alert(err.message || "Failed to pause campaign");
    } finally {
      setActionLoading(null);
    }
  }

  useImperativeHandle(ref, () => ({
    reload: loadCampaigns,
  }));

  useEffect(() => {
    loadCampaigns();
  }, []);

  if (loading) return <p>Loading campaigns…</p>;

  return (
    <div className="card">
      <h2>Campaigns</h2>

      <table className="campaign-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Objective</th>
            <th>Status</th>
            <th>Google ID</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {campaigns.length === 0 && (
            <tr>
              <td colSpan="5" style={{ textAlign: "center" }}>
                No campaigns found
              </td>
            </tr>
          )}

          {campaigns.map((c) => (
            <tr key={c.id}>
              <td>{c.name}</td>
              <td>{c.objective}</td>
              <td>
                <span className={`badge ${c.status.toLowerCase()}`}>
                  {c.status}
                </span>
              </td>
              <td className="mono">
                {c.google_campaign_id || "—"}
              </td>
              <td>
                {c.status === "DRAFT" && (
                  <button
                    disabled={actionLoading === c.id}
                    onClick={() => handlePublish(c.id)}
                  >
                    {actionLoading === c.id ? "Publishing…" : "Publish"}
                  </button>
                )}

                {c.status === "PUBLISHED" && (
                  <button
                    disabled={actionLoading === c.id}
                    onClick={() => handlePause(c.id)}
                  >
                    {actionLoading === c.id ? "Pausing…" : "Pause"}
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
});

export default CampaignList;