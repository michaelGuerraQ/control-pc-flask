from flask import Flask, request, jsonify, render_template, abort
import ctypes
import os
import socket
    
TOKEN = "1234"     
PORT = 8765

app = Flask(__name__, static_folder="static", template_folder="templates")


VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP       = 0xB2
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_VOLUME_MUTE      = 0xAD
VK_VOLUME_DOWN      = 0xAE
VK_VOLUME_UP        = 0xAF


MOUSEEVENTF_MOVE      = 0x0001
MOUSEEVENTF_LEFTDOWN  = 0x0002
MOUSEEVENTF_LEFTUP    = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP   = 0x0010
MOUSEEVENTF_WHEEL     = 0x0800

KEYEVENTF_KEYUP = 0x0002
user32 = ctypes.WinDLL('user32', use_last_error=True)

def press_vk(vk_code: int):
    user32.keybd_event(vk_code, 0, 0, 0)
    user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)

def mouse_move(dx: int, dy: int):
    user32.mouse_event(MOUSEEVENTF_MOVE, dx, dy, 0, 0)

def mouse_click(btn: str):
    if btn == "left":
        user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        user32.mouse_event(MOUSEEVENTF_LEFTUP,   0, 0, 0, 0)
    elif btn == "right":
        user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        user32.mouse_event(MOUSEEVENTF_RIGHTUP,   0, 0, 0, 0)

def mouse_scroll(delta: int):
    user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, delta, 0)

def require_token():
    t = request.args.get("t", "")
    if TOKEN and t != TOKEN:
        abort(403)

@app.after_request
def no_cache(resp):
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.route("/")
def index():
    require_token()
    return render_template("index.html", token=request.args.get("t"))

@app.route("/action/<cmd>", methods=["POST"])
def action(cmd):
    require_token()
    if   cmd == "playpause": press_vk(VK_MEDIA_PLAY_PAUSE)
    elif cmd == "next":      press_vk(VK_MEDIA_NEXT_TRACK)
    elif cmd == "prev":      press_vk(VK_MEDIA_PREV_TRACK)
    elif cmd == "stop":      press_vk(VK_MEDIA_STOP)
    elif cmd == "mute":      press_vk(VK_VOLUME_MUTE)
    elif cmd == "volup":     press_vk(VK_VOLUME_UP)
    elif cmd == "voldown":   press_vk(VK_VOLUME_DOWN)
    elif cmd == "lock":      user32.LockWorkStation()
    elif cmd == "shutdown":  os.system("shutdown /s /t 0")
    else: return jsonify({"ok": False, "error": "cmd desconocido"}), 400
    return jsonify({"ok": True})

@app.route("/mouse/move", methods=["POST"])
def route_mouse_move():
    require_token()
    data = request.get_json(silent=True) or {}
    dx = int(float(data.get("dx", 0)))
    dy = int(float(data.get("dy", 0)))
    mouse_move(dx, dy)
    return jsonify({"ok": True})

@app.route("/mouse/click", methods=["POST"])
def route_mouse_click():
    require_token()
    btn = request.args.get("btn", "left")
    if btn not in ("left", "right"):
        return jsonify({"ok": False, "error": "btn inválido"}), 400
    mouse_click(btn)
    return jsonify({"ok": True})

@app.route("/mouse/scroll", methods=["POST"])
def route_mouse_scroll():
    require_token()
    data = request.get_json(silent=True) or {}
    delta = int(float(data.get("delta", 120)))
    mouse_scroll(delta)
    return jsonify({"ok": True})

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

if __name__ == "__main__":
    ip = get_local_ip()
    print(f"Abre desde tu cel: http://{ip}:{PORT}/?t={TOKEN}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
