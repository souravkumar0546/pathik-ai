const API_BASE_URL =process.env.REACT_APP_API_BASE_URL || "http://backend:5001/api";
export async function createCampaign(data) {
  const response = await fetch(`${API_BASE_URL}/campaigns`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to create campaign");
  }

  return response.json();
}

export async function getCampaigns() {
  const response = await fetch(`${API_BASE_URL}/campaigns`);

  if (!response.ok) {
    throw new Error("Failed to fetch campaigns");
  }

  return response.json();
}

export async function publishCampaign(campaignId) {
  const response = await fetch(
    `${API_BASE_URL}/campaigns/${campaignId}/publish`,
    { method: "POST" }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to publish campaign");
  }

  return response.json();
}

export async function pauseCampaign(campaignId) {
  const response = await fetch(
    `${API_BASE_URL}/campaigns/${campaignId}/pause`,
    { method: "POST" }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || "Failed to pause campaign");
  }

  return response.json();
}