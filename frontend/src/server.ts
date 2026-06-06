import express, { Request, Response } from "express";
import path from "path";

const app = express();
const API = "http://localhost:8000";

app.use(express.json());
app.use(express.static(path.join(__dirname, "..", "public")));

// Work orders that have been invoiced and await review
app.get("/api/pending", async (_req: Request, res: Response) => {
  const r = await fetch(`${API}/work-orders?status=invoiced`);
  res.status(r.status).json(await r.json());
});

// The generated invoice + lines for one work order
app.get("/api/orders/:id/invoice", async (req: Request, res: Response) => {
  const r = await fetch(`${API}/work-orders/${req.params.id}/invoice`);
  res.status(r.status).json(await r.json());
});

// Approve it
app.post("/api/orders/:id/approve", async (req: Request, res: Response) => {
  const r = await fetch(`${API}/work-orders/${req.params.id}/approve`, { method: "POST" });
  res.status(r.status).json(await r.json());
});

const PORT = 3000;
app.listen(PORT, () => console.log(`Dashboard at http://localhost:${PORT}`));