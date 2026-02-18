const SUPABASE_URL = "https://goabrqjuguybmvjlqylq.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdvYWJycWp1Z3V5Ym12amxxeWxxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEyNjMxOTgsImV4cCI6MjA4NjgzOTE5OH0.INEv8kOskPZO6fU6827a9XZkkl8Smzqht5_KVDzQ_Ro";

const mppCharts = {};

async function fetchMaxProfitPoints() {
  const res = await fetch(
    `${SUPABASE_URL}/rest/v1/max_profit_points?order=timestamp.asc`,
    {
      headers: {
        apikey: SUPABASE_ANON_KEY,
        Authorization: `Bearer ${SUPABASE_ANON_KEY}`
      }
    }
  );
  return await res.json();
}

async function buildCharts() {
  const data = await fetchMaxProfitPoints();
  if (!data || data.length === 0) return;

  const timestamps = data.map(d =>
    new Date(d.timestamp * 1000).toLocaleTimeString()
  );
  const spreads = data.map(d => d.spread);
  const volumes = data.map(d => d.volume);
  const profits = data.map(d => d.profit);

  createMppChart("mppSpreadChart", "Spread", timestamps, spreads, "rgb(255,200,0)");
  createMppChart("mppVolumeChart", "Volume", timestamps, volumes, "rgb(0,255,100)");
  createMppChart("mppProfitChart", "Profit", timestamps, profits, "rgb(0,200,255)");
}

function createMppChart(canvasId, label, labels, data, color) {
  if (mppCharts[canvasId]) {
    mppCharts[canvasId].destroy();
    mppCharts[canvasId] = null;
  }
  const el = document.getElementById(canvasId);
  if (!el) return;
  mppCharts[canvasId] = new Chart(el, {
    type: "line",
    data: {
      labels,
      datasets: [{
        label,
        data,
        borderColor: color,
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: { display: true, color: "rgba(255,255,255,0.12)", borderDash: [4, 4] },
          ticks: { color: "white" }
        },
        y: {
          grid: { display: true, color: "rgba(255,255,255,0.12)", borderDash: [4, 4] },
          ticks: { color: "white" }
        }
      },
      plugins: {
        legend: { labels: { color: "white" } }
      }
    }
  });
}

buildCharts();
setInterval(buildCharts, 600000);
