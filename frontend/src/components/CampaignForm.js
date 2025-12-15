import { useState } from "react";
import { createCampaign } from "../api/campaigns";

function CampaignForm({ onCreated }) {
  const [form, setForm] = useState({
    name: "",
    objective: "Traffic",
    campaign_type: "Search",
    daily_budget: "",
    start_date: "",
    end_date: "",
    ad_group_name: "",
    ad_headline: "",
    ad_description: "",
    asset_url: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    try {
      setLoading(true);
      await createCampaign(form);
      onCreated();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h2>Create Campaign</h2>

      {error && <p className="error">{error}</p>}

      {/* Campaign Info */}
      <div className="section">
        <h3>Campaign Info</h3>

        <input
          name="name"
          placeholder="Campaign name"
          value={form.name}
          onChange={handleChange}
          required
        />

        <div className="row">
          <select
            name="objective"
            value={form.objective}
            onChange={handleChange}
          >
            <option value="Traffic">Traffic</option>
            <option value="Leads">Leads</option>
            <option value="Sales">Sales</option>
          </select>

          <input
            type="number"
            name="daily_budget"
            placeholder="Daily budget"
            value={form.daily_budget}
            onChange={handleChange}
            required
          />
        </div>

        <div className="row">
          <input
            type="date"
            name="start_date"
            value={form.start_date}
            onChange={handleChange}
            required
          />
          <input
            type="date"
            name="end_date"
            value={form.end_date}
            onChange={handleChange}
          />
        </div>
      </div>

      {/* Ad Info */}
      <div className="section">
        <h3>Ad Details</h3>

        <input
          name="ad_group_name"
          placeholder="Ad group name"
          value={form.ad_group_name}
          onChange={handleChange}
          required
        />

        <input
          name="ad_headline"
          placeholder="Ad headline"
          value={form.ad_headline}
          onChange={handleChange}
          required
        />

        <textarea
          name="ad_description"
          placeholder="Ad description"
          value={form.ad_description}
          onChange={handleChange}
          required
        />

        <input
          name="asset_url"
          placeholder="Landing page URL"
          value={form.asset_url}
          onChange={handleChange}
        />
      </div>

      <button className="primary" type="submit" disabled={loading}>
        {loading ? "Creating…" : "Create Campaign"}
      </button>
    </form>
  );
}

export default CampaignForm;