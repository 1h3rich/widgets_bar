.pragma library

var BAR_W = 920
var BAR_H = 170
var RADIUS = 16
var MARGIN = 16
var TRIGGER_ABOVE = 80
var HIDE_DELAY = 1500
var REVEAL_DURATION = 220

var BG_COLOR = Qt.rgba(12 / 255, 12 / 255, 22 / 255, 218 / 255)
var BORDER_COLOR = Qt.rgba(1, 1, 1, 22 / 255)
var ACCENT = "#9580FF"
var TEXT_PRI = "#E0E0F0"
var TEXT_SEC = "#7070A0"
var TEXT_WARN = "#FF9060"
var TEXT_HIGH = "#FFD060"

function pctColor(pct, warn, crit) {
    if (pct === null || pct === undefined) return TEXT_SEC
    warn = warn === undefined ? 85 : warn
    crit = crit === undefined ? 95 : crit
    if (pct >= crit) return TEXT_WARN
    if (pct >= warn) return TEXT_HIGH
    return TEXT_PRI
}

function tempColor(t, warn, crit) {
    if (t === null || t === undefined) return TEXT_SEC
    warn = warn === undefined ? 80 : warn
    crit = crit === undefined ? 90 : crit
    if (t >= crit) return TEXT_WARN
    if (t >= warn) return TEXT_HIGH
    return TEXT_PRI
}

function formatSpeed(bps) {
    if (bps === null || bps === undefined) return "--"
    if (bps < 1024) return bps.toFixed(0) + " B/s"
    if (bps < 1024 * 1024) return (bps / 1024).toFixed(1) + " KB/s"
    return (bps / 1024 / 1024).toFixed(1) + " MB/s"
}
