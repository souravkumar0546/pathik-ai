import { useRef, useState } from "react";
import CampaignForm from "./components/CampaignForm";
import CampaignList from "./components/CampaignList";
import "./App.css";

function App() {
  const listRef = useRef();
  const [activeTab, setActiveTab] = useState("create");

  return (
    <div className="container">
      <h1>Pathik AI — Campaigns</h1>

      {/* Tabs */}
      <div className="tabs">
        <button
          className={activeTab === "create" ? "active" : ""}
          onClick={() => setActiveTab("create")}
        >
          Create Campaign
        </button>

        <button
          className={activeTab === "list" ? "active" : ""}
          onClick={() => setActiveTab("list")}
        >
          View Campaigns
        </button>
      </div>

      {/* Content */}
      {activeTab === "create" && (
        <CampaignForm
          onCreated={() => {
            listRef.current?.reload();
            setActiveTab("list");
          }}
        />
      )}

      {activeTab === "list" && <CampaignList ref={listRef} />}
    </div>
  );
}

export default App;