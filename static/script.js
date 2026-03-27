const token = window.REMOTE_TOKEN || "";

// ===== Helpers HTTP =====
async function act(cmd){
  const r = await fetch(`/action/${cmd}?t=${encodeURIComponent(token)}`, {method:'POST'});
  if(!r.ok) alert('Error '+r.status);
}

async function move(dx, dy){
  await fetch(`/mouse/move?t=${encodeURIComponent(token)}`, {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({dx, dy})
  });
}

async function clickBtn(btn){
  const r = await fetch(`/mouse/click?t=${encodeURIComponent(token)}&btn=${btn}`, {method:'POST'});
  if(!r.ok) alert('Error '+r.status);
}

async function scrollY(delta){
  await fetch(`/mouse/scroll?t=${encodeURIComponent(token)}`, {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({delta})
  });
}

// ===== Touchpad =====
const pad = document.getElementById("pad");
let lastX=null, lastY=null;
let startX=0, startY=0, startTime=0;
let fingers=0;
const SPEED = 1.8;    // sensibilidad (sube/baja a gusto)
const TAP_MS = 200;   // umbral tap
const TAP_DIST = 12;  // umbral movimiento para considerar tap
const LONG_MS = 500;  // long-press = clic derecho

pad.addEventListener("touchstart", e=>{
  fingers = e.touches.length;
  const t = e.touches[0];
  lastX = startX = t.clientX;
  lastY = startY = t.clientY;
  startTime = Date.now();
});

pad.addEventListener("touchmove", e=>{
  // 1 dedo = mover mouse, 2 dedos = scroll
  e.preventDefault();
  if (e.touches.length === 1){
    const t = e.touches[0];
    const dx = (t.clientX - lastX) * SPEED;
    const dy = (t.clientY - lastY) * SPEED;
    lastX = t.clientX; lastY = t.clientY;
    move(dx, dy);
  } else if (e.touches.length === 2){
    // prom/centro de los dos dedos
    const t1 = e.touches[0], t2 = e.touches[1];
    const avgY = (t1.clientY + t2.clientY) / 2;
    const dy = (avgY - lastY) * 2.5;   // sensibilidad scroll
    lastY = avgY;
    // rueda: múltiplos de 120; aproximamos
    const delta = Math.round(dy / 120) * 120 || (dy>0?120:-120);
    scrollY(-delta); // invertimos para que gesto hacia arriba = scroll arriba
  }
});

pad.addEventListener("touchend", e=>{
  // Tap (clic izq.) si fue corto y casi sin mover
  const dt = Date.now() - startTime;
  const dist = Math.hypot((lastX - startX), (lastY - startY));

  if (fingers === 1 && dt <= TAP_MS && dist <= TAP_DIST){
    clickBtn("left");
  } else if (fingers === 1 && dt >= LONG_MS && dist <= TAP_DIST){
    clickBtn("right"); // long-press = clic derecho
  }
  fingers = Math.max(0, fingers - 1);
});
