const express = require("express");
const fs = require("fs");
const path = require("path");
const cors = require("cors");
const app = express();

app.use(express.json());
app.use(cors());

const BAN_FILE = path.join("/var/data", "bans.json");

if (!fs.existsSync(BAN_FILE)) fs.writeFileSync(BAN_FILE, "[]");

function readBans() {
    const data = fs.readFileSync(BAN_FILE, "utf-8");
    return JSON.parse(data);
}

function writeBans(bans) {
    fs.writeFileSync(BAN_FILE, JSON.stringify(bans, null, 2));
}

app.post("/ban", (req, res) => {
    const { userId, username, reason, moderatorId } = req.body;
    const bans = readBans();
    if (!bans.find(b => b.userId === userId)) {
        bans.push({ userId, username, reason, moderatorId, timestamp: Date.now() });
        writeBans(bans);
    }
    res.json({ success: true });
});

app.post("/unban", (req, res) => {
    const { userId } = req.body;
    let bans = readBans();
    bans = bans.filter(b => b.userId !== userId);
    writeBans(bans);
    res.json({ success: true });
});

app.get("/bans/:userId", (req, res) => {
    const userId = Number(req.params.userId);
    const bans = readBans().filter(b => b.userId === userId);
    res.json(bans);
});

app.get("/healthz", (req, res) => res.send("OK"));

app.listen(process.env.PORT || 3000, () => console.log("Ban service running"));
