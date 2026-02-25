const express = require("express");
const fs = require("fs");
const path = require("path");
const app = express();

app.use(express.json());

const BAN_FILE = path.join("/disk", "bans.json");

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

app.get("/bans/:userId", (req, res) => {
    const userId = Number(req.params.userId);
    const bans = readBans().filter(b => b.userId === userId);
    res.json(bans);
});

app.listen(process.env.PORT || 3000, () => console.log("Server running"));