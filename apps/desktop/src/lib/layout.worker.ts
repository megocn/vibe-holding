/** Web Worker：力导向布局，避免主线程长时间占用。 */

export interface LayoutNodeIn {
  id: string;
  /** 可选初始位置 */
  x?: number;
  y?: number;
  /** 节点视觉半径（含标签预留），用于碰撞 */
  radius?: number;
}

export interface LayoutEdgeIn {
  source: string;
  target: string;
}

export interface LayoutRequest {
  nodes: LayoutNodeIn[];
  edges: LayoutEdgeIn[];
  width: number;
  height: number;
  iterations?: number;
}

export type LayoutPositions = Record<string, { x: number; y: number }>;

function layoutForce(req: LayoutRequest): LayoutPositions {
  const { nodes, edges, width, height } = req;
  const n = nodes.length;
  if (n === 0) return {};

  // 密图多跑几轮，保证斥力收敛到可辨识间距
  const iterations = req.iterations ?? Math.min(220, 80 + n * 4);
  const pos = new Map<string, { x: number; y: number; vx: number; vy: number; r: number }>();
  const cx = width / 2;
  const cy = height / 2;
  // 初始环半径随节点数放大，避免一开始就挤在中心
  const R = Math.min(width, height) * (0.28 + Math.min(n, 40) * 0.008);

  nodes.forEach((node, i) => {
    const a = (i / Math.max(n, 1)) * Math.PI * 2 + (i % 3) * 0.17;
    const ring = 0.55 + (i % 5) * 0.09;
    pos.set(node.id, {
      x: node.x ?? cx + Math.cos(a) * R * ring,
      y: node.y ?? cy + Math.sin(a) * R * ring,
      vx: 0,
      vy: 0,
      // 圆半径 + 下方标签预留，避免文字叠在一起
      r: node.radius ?? 48,
    });
  });

  const ids = nodes.map((x) => x.id);
  // 斥力随图规模增强；弹簧理想长度按面积均分
  const kRep = 5200 + n * 180;
  const kSpring = 0.028;
  const areaPer = (width * height) / Math.max(n, 1);
  const ideal = Math.max(110, Math.min(220, Math.sqrt(areaPer) * 0.85));
  const damp = 0.86;
  const maxSpeed = Math.max(24, ideal * 0.35);

  for (let iter = 0; iter < iterations; iter++) {
    // 后半程冷却变慢，保留碰撞分离能力
    const t = iter / iterations;
    const cool = 0.35 + 0.65 * (1 - t) * (1 - t);

    for (let i = 0; i < ids.length; i++) {
      const idA = ids[i];
      if (idA == null) continue;
      const a = pos.get(idA);
      if (!a) continue;
      for (let j = i + 1; j < ids.length; j++) {
        const idB = ids[j];
        if (idB == null) continue;
        const b = pos.get(idB);
        if (!b) continue;
        let dx = a.x - b.x;
        let dy = a.y - b.y;
        let dist = Math.hypot(dx, dy);
        if (dist < 0.01) {
          // 完全重合时给一个随机微扰方向
          const ang = ((i * 17 + j * 31 + iter) % 360) * (Math.PI / 180);
          dx = Math.cos(ang);
          dy = Math.sin(ang);
          dist = 0.01;
        }
        const minDist = a.r + b.r;
        // Coulomb 斥力
        const fRep = (kRep / (dist * dist)) * cool;
        // 硬碰撞：进入最小间距时额外强推
        const overlap = minDist - dist;
        const fColl = overlap > 0 ? overlap * 0.55 * (0.5 + cool) : 0;
        const f = fRep + fColl;
        dx = (dx / dist) * f;
        dy = (dy / dist) * f;
        a.vx += dx;
        a.vy += dy;
        b.vx -= dx;
        b.vy -= dy;
      }
    }

    for (const e of edges) {
      const a = pos.get(e.source);
      const b = pos.get(e.target);
      if (!a || !b) continue;
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const dist = Math.hypot(dx, dy) || 0.01;
      // 边弹簧：理想长度至少覆盖两端碰撞半径
      const edgeIdeal = Math.max(ideal, a.r + b.r + 24);
      const f = (dist - edgeIdeal) * kSpring * cool;
      const fx = (dx / dist) * f;
      const fy = (dy / dist) * f;
      a.vx += fx;
      a.vy += fy;
      b.vx -= fx;
      b.vy -= fy;
    }

    for (const id of ids) {
      const p = pos.get(id);
      if (!p) continue;
      // 弱向心力，防止散出画布过远
      p.vx += (cx - p.x) * 0.0012;
      p.vy += (cy - p.y) * 0.0012;
      p.vx *= damp;
      p.vy *= damp;
      const speed = Math.hypot(p.vx, p.vy);
      if (speed > maxSpeed) {
        p.vx = (p.vx / speed) * maxSpeed;
        p.vy = (p.vy / speed) * maxSpeed;
      }
      p.x += p.vx;
      p.y += p.vy;
    }
  }

  // 收尾：再做一轮硬碰撞投影，清掉残留重叠
  for (let pass = 0; pass < 8; pass++) {
    for (let i = 0; i < ids.length; i++) {
      const idA = ids[i];
      if (idA == null) continue;
      const a = pos.get(idA);
      if (!a) continue;
      for (let j = i + 1; j < ids.length; j++) {
        const idB = ids[j];
        if (idB == null) continue;
        const b = pos.get(idB);
        if (!b) continue;
        let dx = a.x - b.x;
        let dy = a.y - b.y;
        let dist = Math.hypot(dx, dy);
        const minDist = a.r + b.r;
        if (dist < 0.01) {
          dx = 1;
          dy = 0;
          dist = 0.01;
        }
        if (dist >= minDist) continue;
        const push = (minDist - dist) / 2;
        const ux = dx / dist;
        const uy = dy / dist;
        a.x += ux * push;
        a.y += uy * push;
        b.x -= ux * push;
        b.y -= uy * push;
      }
    }
  }

  const out: LayoutPositions = {};
  for (const [id, p] of pos) out[id] = { x: p.x, y: p.y };
  return out;
}

self.onmessage = (ev: MessageEvent<LayoutRequest>) => {
  const positions = layoutForce(ev.data);
  postMessage(positions);
};
