"use client";

/**
 * BrainView — Karpathy-style LLM-brain 3D knowledge graph visualization.
 *
 * Uses Three.js force-directed layout with InstancedMesh for performance.
 * Mounts into a div ref; full lifecycle cleanup on unmount.
 *
 * URL params consumed:
 *   ?highlight=slug1,slug2,...   — persistently highlights those nodes on load.
 *
 * Props:
 *   highlight  — comma-separated slugs to highlight (from URL param).
 *
 * Architecture notes:
 * - Nodes: ONE InstancedMesh (one draw call for all spheres). Per-instance color
 *   via instanceColor. Hover/highlight via matrix scale in the base matrix array.
 * - Edges: ONE LineSegments with a single BufferGeometry (one draw call for all edges).
 *   Positions updated in-place during simulation; needsUpdate = true per frame.
 * - Force layout: simple spring-repulsion, O(N²) repulsion, runs 200 warm-up ticks
 *   synchronously before first render, then 1-2 ticks/frame until convergence.
 * - Emissive glow: MeshStandardMaterial with emissive matching node type color at 0.3
 *   intensity. Per-instance emissive is not natively supported in Three.js r157 without
 *   shader patching; we achieve the glow by setting emissiveIntensity uniformly and
 *   letting instanceColor drive the visible color difference. Hover/highlight override
 *   uses a second pass: hovered node gets scaled up and its instance color brightened
 *   by mutating the instanceColor buffer directly.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface GraphNode {
  slug: string;
  title: string;
  type: string;
  path: string;
  summary: string;
  corpus: string;
}

interface GraphEdge {
  source: string;
  target: string;
}

interface GraphData {
  schema_version: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  adjacency: Record<string, string[]>;
}

interface WikiStats {
  total_pages: number;
  last_commit_sha: string;
  last_commit_date: string;
  last_commit_message: string;
}

// ---------------------------------------------------------------------------
// Type-color palette (Karpathy minimalist monochrome accents)
// ---------------------------------------------------------------------------

const TYPE_COLORS: Record<string, string> = {
  programs: "#4a90d9",
  targets: "#e07b54",
  methods: "#5cb85c",
  platforms: "#9b59b6",
  concepts: "#e8c84a",
  decisions: "#e74c3c",
  equipment: "#1abc9c",
  references: "#95a5a6",
  protocols: "#f39c12",
  output: "#888888",
};

const DEFAULT_COLOR = "#888888";

function typeColor(type: string): string {
  return TYPE_COLORS[type] ?? DEFAULT_COLOR;
}

// ---------------------------------------------------------------------------
// Force layout helpers
// ---------------------------------------------------------------------------

interface NodePos {
  x: number;
  y: number;
  z: number;
  vx: number;
  vy: number;
  vz: number;
}

const K_REPULSION = 150;
const K_SPRING = 0.02;
const REST_LENGTH = 60;
const DAMPING = 0.85;

function initPositions(n: number): NodePos[] {
  const positions: NodePos[] = [];
  const radius = Math.sqrt(n) * 20;
  for (let i = 0; i < n; i++) {
    // Fibonacci sphere distribution for even spread
    const phi = Math.acos(1 - (2 * (i + 0.5)) / n);
    const theta = Math.PI * (1 + Math.sqrt(5)) * i;
    positions.push({
      x: radius * Math.sin(phi) * Math.cos(theta),
      y: radius * Math.sin(phi) * Math.sin(theta),
      z: radius * Math.cos(phi),
      vx: 0,
      vy: 0,
      vz: 0,
    });
  }
  return positions;
}

function tickForce(
  positions: NodePos[],
  edgeIndices: [number, number][],
  count: number = 1,
): number {
  let maxMove = 0;
  for (let t = 0; t < count; t++) {
    const n = positions.length;
    const fx = new Float64Array(n);
    const fy = new Float64Array(n);
    const fz = new Float64Array(n);

    // Repulsion: all pairs
    for (let i = 0; i < n; i++) {
      for (let j = i + 1; j < n; j++) {
        const dx = positions[i].x - positions[j].x;
        const dy = positions[i].y - positions[j].y;
        const dz = positions[i].z - positions[j].z;
        const distSq = dx * dx + dy * dy + dz * dz + 0.001;
        const dist = Math.sqrt(distSq);
        const force = K_REPULSION / distSq;
        const nx = (dx / dist) * force;
        const ny = (dy / dist) * force;
        const nz = (dz / dist) * force;
        fx[i] += nx;
        fy[i] += ny;
        fz[i] += nz;
        fx[j] -= nx;
        fy[j] -= ny;
        fz[j] -= nz;
      }
    }

    // Spring attraction along edges
    for (const [a, b] of edgeIndices) {
      const dx = positions[b].x - positions[a].x;
      const dy = positions[b].y - positions[a].y;
      const dz = positions[b].z - positions[a].z;
      const dist = Math.sqrt(dx * dx + dy * dy + dz * dz) + 0.001;
      const stretch = dist - REST_LENGTH;
      const force = K_SPRING * stretch;
      fx[a] += (dx / dist) * force;
      fy[a] += (dy / dist) * force;
      fz[a] += (dz / dist) * force;
      fx[b] -= (dx / dist) * force;
      fy[b] -= (dy / dist) * force;
      fz[b] -= (dz / dist) * force;
    }

    // Integrate
    maxMove = 0;
    for (let i = 0; i < n; i++) {
      positions[i].vx = (positions[i].vx + fx[i]) * DAMPING;
      positions[i].vy = (positions[i].vy + fy[i]) * DAMPING;
      positions[i].vz = (positions[i].vz + fz[i]) * DAMPING;
      positions[i].x += positions[i].vx;
      positions[i].y += positions[i].vy;
      positions[i].z += positions[i].vz;
      const move = Math.sqrt(
        positions[i].vx ** 2 + positions[i].vy ** 2 + positions[i].vz ** 2,
      );
      if (move > maxMove) maxMove = move;
    }
  }
  return maxMove;
}

// ---------------------------------------------------------------------------
// BFS subgraph helper
// ---------------------------------------------------------------------------

function bfsDepth2(
  startIdx: number,
  adjacencyByIndex: number[][],
): Set<number> {
  const visited = new Set<number>();
  const queue: Array<{ idx: number; depth: number }> = [
    { idx: startIdx, depth: 0 },
  ];
  while (queue.length > 0) {
    const item = queue.shift()!;
    if (visited.has(item.idx)) continue;
    visited.add(item.idx);
    if (item.depth < 2) {
      for (const nb of adjacencyByIndex[item.idx]) {
        if (!visited.has(nb)) {
          queue.push({ idx: nb, depth: item.depth + 1 });
        }
      }
    }
  }
  return visited;
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

interface BrainViewProps {
  highlight?: string; // comma-separated slugs
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function BrainView({ highlight = "" }: BrainViewProps) {
  const router = useRouter();
  const mountRef = useRef<HTMLDivElement | null>(null);

  // UI state (React-controlled overlay)
  const [tooltip, setTooltip] = useState<{
    x: number;
    y: number;
    text: string;
  } | null>(null);
  const [filterMode, setFilterMode] = useState<"all" | "subgraph">("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  // Refs for Three.js objects shared between setup and animation loop
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const instancedMeshRef = useRef<THREE.InstancedMesh | null>(null);
  const lineSegmentsRef = useRef<THREE.LineSegments | null>(null);
  const rafIdRef = useRef<number>(0);
  const statsIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Simulation state in refs (not React state — no re-renders)
  const positionsRef = useRef<NodePos[]>([]);
  const edgeIndicesRef = useRef<[number, number][]>([]);
  const nodeDataRef = useRef<GraphNode[]>([]);
  const baseMatricesRef = useRef<THREE.Matrix4[]>([]);
  const nodeRadiiRef = useRef<number[]>([]);
  const nodeColorsRef = useRef<THREE.Color[]>([]);
  const adjacencyByIndexRef = useRef<number[][]>([]);
  const simulationDoneRef = useRef(false);
  const hoveredIndexRef = useRef<number>(-1);
  const selectedIndexRef = useRef<number>(-1);
  const highlightSlugsRef = useRef<Set<string>>(new Set());
  const filterModeRef = useRef<"all" | "subgraph">("all");
  const searchQueryRef = useRef<string>("");
  const lastShaRef = useRef<string>("");
  const pulseStartRef = useRef<number>(0);
  const isPulsingRef = useRef(false);
  const idleTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const autoRotateRef = useRef(true);

  // Keep filter/search refs in sync with state
  useEffect(() => {
    filterModeRef.current = filterMode;
  }, [filterMode]);

  useEffect(() => {
    searchQueryRef.current = searchQuery;
  }, [searchQuery]);

  // ---------------------------------------------------------------------------
  // Main Three.js setup effect
  // ---------------------------------------------------------------------------
  useEffect(() => {
    if (!mountRef.current) return;
    const mount = mountRef.current;

    // -- Fetch graph data ---------------------------------------------------
    fetch("/api/graph/json", { cache: "no-store" })
      .then((r) => {
        if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
        return r.json() as Promise<GraphData>;
      })
      .then((data) => {
        setupScene(mount, data);
        setLoading(false);
      })
      .catch((err: unknown) => {
        setLoadError(err instanceof Error ? err.message : String(err));
        setLoading(false);
      });

    return () => {
      cleanup();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ---------------------------------------------------------------------------
  // Highlight slugs from URL param
  // ---------------------------------------------------------------------------
  useEffect(() => {
    const slugSet = new Set(
      highlight
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
    );
    highlightSlugsRef.current = slugSet;
    // If mesh already exists, refresh instance colors
    refreshInstanceColors();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [highlight]);

  // ---------------------------------------------------------------------------
  // Poll wiki stats for shimmer-on-update
  // ---------------------------------------------------------------------------
  useEffect(() => {
    const poll = async () => {
      try {
        const r = await fetch("/api/wiki/stats", { cache: "no-store" });
        if (!r.ok) return;
        const stats = (await r.json()) as WikiStats;
        if (lastShaRef.current && stats.last_commit_sha !== lastShaRef.current) {
          // New commit detected — pulse all nodes
          pulseStartRef.current = performance.now();
          isPulsingRef.current = true;
        }
        lastShaRef.current = stats.last_commit_sha;
      } catch {
        // Network error — skip
      }
    };
    poll();
    statsIntervalRef.current = setInterval(poll, 15000);
    return () => {
      if (statsIntervalRef.current !== null) {
        clearInterval(statsIntervalRef.current);
      }
    };
  }, []);

  // ---------------------------------------------------------------------------
  // Three.js scene setup
  // ---------------------------------------------------------------------------
  const setupScene = useCallback(
    (mount: HTMLDivElement, data: GraphData) => {
      const W = mount.clientWidth;
      const H = mount.clientHeight;

      // -- Renderer ----------------------------------------------------------
      const renderer = new THREE.WebGLRenderer({ antialias: true });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.setSize(W, H);
      renderer.setClearColor(0x0d0d0d, 1);
      mount.appendChild(renderer.domElement);
      rendererRef.current = renderer;

      // -- Scene -------------------------------------------------------------
      const scene = new THREE.Scene();
      sceneRef.current = scene;

      // Ambient + directional light for metallic look
      scene.add(new THREE.AmbientLight(0xffffff, 0.6));
      const dir = new THREE.DirectionalLight(0xffffff, 1.0);
      dir.position.set(100, 200, 150);
      scene.add(dir);

      // -- Camera ------------------------------------------------------------
      const camera = new THREE.PerspectiveCamera(60, W / H, 0.1, 10000);
      const camDist = Math.sqrt(data.nodes.length) * 30 + 100;
      camera.position.set(camDist, camDist * 0.6, camDist);
      camera.lookAt(0, 0, 0);
      cameraRef.current = camera;

      // -- OrbitControls -----------------------------------------------------
      const controls = new OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.autoRotate = true;
      controls.autoRotateSpeed = 0.5;
      controlsRef.current = controls;

      // Track user interaction to pause/resume auto-rotate
      const onUserInteract = () => {
        autoRotateRef.current = false;
        controls.autoRotate = false;
        if (idleTimerRef.current !== null) clearTimeout(idleTimerRef.current);
        idleTimerRef.current = setTimeout(() => {
          autoRotateRef.current = true;
          controls.autoRotate = true;
        }, 5000);
      };
      renderer.domElement.addEventListener("pointerdown", onUserInteract);

      // -- Compute in-degrees ------------------------------------------------
      const slugIndex = new Map<string, number>();
      data.nodes.forEach((n, i) => slugIndex.set(n.slug, i));

      const inDegree = new Array<number>(data.nodes.length).fill(0);
      for (const edge of data.edges) {
        const si = slugIndex.get(edge.source);
        const ti = slugIndex.get(edge.target);
        if (si !== undefined) inDegree[si]++;
        if (ti !== undefined) inDegree[ti]++;
      }

      // -- Build adjacency by index ------------------------------------------
      const adjByIdx: number[][] = data.nodes.map(() => []);
      for (const edge of data.edges) {
        const si = slugIndex.get(edge.source);
        const ti = slugIndex.get(edge.target);
        if (si !== undefined && ti !== undefined) {
          adjByIdx[si].push(ti);
          adjByIdx[ti].push(si);
        }
      }
      adjacencyByIndexRef.current = adjByIdx;

      // -- Build edge index list ---------------------------------------------
      const edgeIndices: [number, number][] = [];
      for (const edge of data.edges) {
        const si = slugIndex.get(edge.source);
        const ti = slugIndex.get(edge.target);
        if (si !== undefined && ti !== undefined) {
          edgeIndices.push([si, ti]);
        }
      }
      edgeIndicesRef.current = edgeIndices;
      nodeDataRef.current = data.nodes;

      // -- Compute node radii -----------------------------------------------
      const radii = data.nodes.map((_, i) =>
        Math.max(3, Math.min(20, 3 + inDegree[i] * 0.8)),
      );
      nodeRadiiRef.current = radii;

      // -- Compute node colors -----------------------------------------------
      const colors = data.nodes.map((n) => new THREE.Color(typeColor(n.type)));
      nodeColorsRef.current = colors;

      // -- Initialize positions + warm-up simulation -------------------------
      const positions = initPositions(data.nodes.length);
      positionsRef.current = positions;

      // 200 warm-up ticks synchronously (runs in <1.5s for 500 nodes)
      for (let t = 0; t < 200; t++) {
        tickForce(positions, edgeIndices, 1);
      }

      // -- InstancedMesh for nodes -------------------------------------------
      const sphereGeo = new THREE.SphereGeometry(1, 8, 8);
      const sphereMat = new THREE.MeshStandardMaterial({
        metalness: 0.3,
        roughness: 0.6,
        emissive: new THREE.Color(0x222222),
        emissiveIntensity: 0.3,
      });
      const count = data.nodes.length;
      const instancedMesh = new THREE.InstancedMesh(sphereGeo, sphereMat, count);
      instancedMesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
      instancedMesh.instanceColor = new THREE.InstancedBufferAttribute(
        new Float32Array(count * 3),
        3,
      );

      // Store base matrices (position + scale from in-degree)
      const baseMatrices: THREE.Matrix4[] = [];
      const tempMatrix = new THREE.Matrix4();
      const tempScale = new THREE.Vector3();

      for (let i = 0; i < count; i++) {
        const r = radii[i];
        tempScale.set(r, r, r);
        tempMatrix.makeScale(r, r, r);
        tempMatrix.setPosition(positions[i].x, positions[i].y, positions[i].z);
        instancedMesh.setMatrixAt(i, tempMatrix);
        instancedMesh.setColorAt(i, colors[i]);
        baseMatrices.push(tempMatrix.clone());
      }
      baseMatricesRef.current = baseMatrices;
      instancedMesh.instanceMatrix.needsUpdate = true;
      if (instancedMesh.instanceColor) instancedMesh.instanceColor.needsUpdate = true;
      scene.add(instancedMesh);
      instancedMeshRef.current = instancedMesh;

      // -- LineSegments for edges --------------------------------------------
      const edgePositions = new Float32Array(edgeIndices.length * 6);
      const edgeGeo = new THREE.BufferGeometry();
      edgeGeo.setAttribute(
        "position",
        new THREE.BufferAttribute(edgePositions, 3).setUsage(
          THREE.DynamicDrawUsage,
        ),
      );
      const edgeMat = new THREE.LineBasicMaterial({
        color: 0xffffff,
        transparent: true,
        opacity: 0.15,
      });
      const lineSegments = new THREE.LineSegments(edgeGeo, edgeMat);
      scene.add(lineSegments);
      lineSegmentsRef.current = lineSegments;

      // Update edge positions from current node positions
      updateEdgePositions(edgePositions, positions, edgeIndices);
      edgeGeo.getAttribute("position").needsUpdate = true;

      // -- Raycaster setup --------------------------------------------------
      const raycaster = new THREE.Raycaster();
      const mouse = new THREE.Vector2();

      const onMouseMove = (e: MouseEvent) => {
        const rect = renderer.domElement.getBoundingClientRect();
        mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const hits = raycaster.intersectObject(instancedMesh);

        if (hits.length > 0 && hits[0].instanceId !== undefined) {
          const idx = hits[0].instanceId;
          if (hoveredIndexRef.current !== idx) {
            hoveredIndexRef.current = idx;
            refreshInstanceColors();
          }
          const node = data.nodes[idx];
          const tipText = [
            node.title,
            node.slug,
            node.summary || node.type,
          ].join("\n");
          setTooltip({ x: e.clientX - rect.left, y: e.clientY - rect.top, text: tipText });
        } else {
          if (hoveredIndexRef.current !== -1) {
            hoveredIndexRef.current = -1;
            refreshInstanceColors();
          }
          setTooltip(null);
        }
      };

      const onClick = (e: MouseEvent) => {
        const rect = renderer.domElement.getBoundingClientRect();
        mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
        raycaster.setFromCamera(mouse, camera);
        const hits = raycaster.intersectObject(instancedMesh);
        if (hits.length > 0 && hits[0].instanceId !== undefined) {
          const idx = hits[0].instanceId;
          selectedIndexRef.current = idx;
          router.push(`/wiki?slug=${data.nodes[idx].slug}`);
        }
      };

      renderer.domElement.addEventListener("mousemove", onMouseMove);
      renderer.domElement.addEventListener("click", onClick);

      // -- Resize handler ---------------------------------------------------
      const onResize = () => {
        const W2 = mount.clientWidth;
        const H2 = mount.clientHeight;
        camera.aspect = W2 / H2;
        camera.updateProjectionMatrix();
        renderer.setSize(W2, H2);
      };
      window.addEventListener("resize", onResize);

      // -- Animation loop ---------------------------------------------------
      let lastTime = performance.now();

      const animate = () => {
        rafIdRef.current = requestAnimationFrame(animate);
        const now = performance.now();
        const dt = now - lastTime;
        lastTime = now;

        // Run 1-2 simulation ticks until converged
        if (!simulationDoneRef.current) {
          const maxMove = tickForce(positions, edgeIndices, 1);
          if (maxMove < 0.1) {
            simulationDoneRef.current = true;
          }
          // Update node matrices
          for (let i = 0; i < count; i++) {
            const r = radii[i];
            const isHovered = hoveredIndexRef.current === i;
            const isHighlighted =
              highlightSlugsRef.current.has(data.nodes[i].slug) ||
              (filterModeRef.current === "all" &&
                searchQueryRef.current &&
                data.nodes[i].title
                  .toLowerCase()
                  .includes(searchQueryRef.current.toLowerCase()));

            const scale = isHovered ? r * 1.4 : isHighlighted ? r * 1.3 : r;
            tempMatrix.makeScale(scale, scale, scale);
            tempMatrix.setPosition(positions[i].x, positions[i].y, positions[i].z);
            baseMatricesRef.current[i] = tempMatrix.clone();
            instancedMesh.setMatrixAt(i, tempMatrix);
          }
          instancedMesh.instanceMatrix.needsUpdate = true;

          // Update edge positions
          updateEdgePositions(edgePositions, positions, edgeIndices);
          (edgeGeo.getAttribute("position") as THREE.BufferAttribute).needsUpdate = true;
        } else if (
          hoveredIndexRef.current !== -1 ||
          highlightSlugsRef.current.size > 0 ||
          searchQueryRef.current
        ) {
          // Still update matrices for visual effects even when settled
          for (let i = 0; i < count; i++) {
            const r = radii[i];
            const isHovered = hoveredIndexRef.current === i;
            const isHighlighted =
              highlightSlugsRef.current.has(data.nodes[i].slug) ||
              (filterModeRef.current === "all" &&
                searchQueryRef.current &&
                data.nodes[i].title
                  .toLowerCase()
                  .includes(searchQueryRef.current.toLowerCase()));
            const scale = isHovered ? r * 1.4 : isHighlighted ? r * 1.3 : r;
            baseMatricesRef.current[i].makeScale(scale, scale, scale);
            baseMatricesRef.current[i].setPosition(
              positions[i].x,
              positions[i].y,
              positions[i].z,
            );
            instancedMesh.setMatrixAt(i, baseMatricesRef.current[i]);
          }
          instancedMesh.instanceMatrix.needsUpdate = true;
        }

        // Pulse animation (wiki update shimmer)
        if (isPulsingRef.current) {
          const elapsed = now - pulseStartRef.current;
          const pulseDuration = 800; // ms
          if (elapsed < pulseDuration) {
            // scale oscillation: 1.0 → 1.5 → 1.0 over pulseDuration
            const t = elapsed / pulseDuration;
            const pulse = 1.0 + 0.5 * Math.sin(t * Math.PI);
            for (let i = 0; i < count; i++) {
              const r = radii[i] * pulse;
              const m = new THREE.Matrix4();
              m.makeScale(r, r, r);
              m.setPosition(positions[i].x, positions[i].y, positions[i].z);
              instancedMesh.setMatrixAt(i, m);
            }
            instancedMesh.instanceMatrix.needsUpdate = true;
          } else {
            isPulsingRef.current = false;
            // Restore normal matrices
            for (let i = 0; i < count; i++) {
              const r = radii[i];
              const m = new THREE.Matrix4();
              m.makeScale(r, r, r);
              m.setPosition(positions[i].x, positions[i].y, positions[i].z);
              baseMatricesRef.current[i] = m;
              instancedMesh.setMatrixAt(i, m);
            }
            instancedMesh.instanceMatrix.needsUpdate = true;
          }
        }

        // Subgraph visibility filter
        if (filterModeRef.current === "subgraph" && selectedIndexRef.current !== -1) {
          const visible = bfsDepth2(
            selectedIndexRef.current,
            adjacencyByIndexRef.current,
          );
          for (let i = 0; i < count; i++) {
            if (!visible.has(i)) {
              // Push node far away (invisible) — use opacity via instanceColor instead
              instancedMesh.setColorAt(i, new THREE.Color(0x000000));
            }
          }
          if (instancedMesh.instanceColor) {
            instancedMesh.instanceColor.needsUpdate = true;
          }
        }

        // Update dt to avoid unused variable warning
        void dt;

        controls.update();
        renderer.render(scene, camera);
      };
      animate();

      // -- Cleanup closure ---------------------------------------------------
      // Store cleanup fn on ref to bridge between setup closure and cleanup fn
      // any cast is intentional: rendererRef is WebGLRenderer | null, we bolt on a custom prop
      (rendererRef as unknown as { _cleanup: () => void })._cleanup = () => {
        cancelAnimationFrame(rafIdRef.current);
        window.removeEventListener("resize", onResize);
        renderer.domElement.removeEventListener("mousemove", onMouseMove);
        renderer.domElement.removeEventListener("click", onClick);
        renderer.domElement.removeEventListener("pointerdown", onUserInteract);
        if (idleTimerRef.current !== null) clearTimeout(idleTimerRef.current);
        controls.dispose();
        sphereGeo.dispose();
        sphereMat.dispose();
        edgeGeo.dispose();
        edgeMat.dispose();
        renderer.dispose();
        if (mount.contains(renderer.domElement)) {
          mount.removeChild(renderer.domElement);
        }
      };
    },
    // router is stable ref; highlight handled via separate effect
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [router],
  );

  // ---------------------------------------------------------------------------
  // Cleanup helper
  // ---------------------------------------------------------------------------
  const cleanup = useCallback(() => {
    const cleanupFn = (rendererRef as unknown as { _cleanup?: () => void })._cleanup;
    if (typeof cleanupFn === "function") {
      cleanupFn();
    }
    if (statsIntervalRef.current !== null) {
      clearInterval(statsIntervalRef.current);
    }
  }, []);

  // ---------------------------------------------------------------------------
  // Refresh instance colors (called on hover / highlight / search changes)
  // ---------------------------------------------------------------------------
  const refreshInstanceColors = useCallback(() => {
    const mesh = instancedMeshRef.current;
    if (!mesh || !mesh.instanceColor) return;
    const nodes = nodeDataRef.current;
    const colors = nodeColorsRef.current;
    const hovered = hoveredIndexRef.current;
    const highlights = highlightSlugsRef.current;
    const query = searchQueryRef.current;
    const hasSearch = query.length > 0;
    const hasHighlight = highlights.size > 0;

    for (let i = 0; i < nodes.length; i++) {
      const node = nodes[i];
      const baseColor = colors[i];
      const isHovered = hovered === i;
      const isHighlighted = highlights.has(node.slug);
      const matchesSearch =
        hasSearch &&
        node.title.toLowerCase().includes(query.toLowerCase());

      if (isHovered) {
        // Brighter: lerp toward white
        const bright = baseColor.clone().lerp(new THREE.Color(0xffffff), 0.5);
        mesh.setColorAt(i, bright);
      } else if (isHighlighted || matchesSearch) {
        // Slightly brighter
        const bright = baseColor.clone().lerp(new THREE.Color(0xffffff), 0.25);
        mesh.setColorAt(i, bright);
      } else if ((hasSearch || hasHighlight) && !isHighlighted && !matchesSearch) {
        // Dim non-matching nodes
        const dim = baseColor.clone().multiplyScalar(0.2);
        mesh.setColorAt(i, dim);
      } else {
        mesh.setColorAt(i, baseColor);
      }
    }
    mesh.instanceColor.needsUpdate = true;
  }, []);

  // Re-run color refresh when search or filter changes
  useEffect(() => {
    refreshInstanceColors();
  }, [searchQuery, filterMode, refreshInstanceColors]);

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  if (loadError) {
    return (
      <div className="brain-view-container flex items-center justify-center">
        <div className="text-red-400 text-sm font-mono p-4 border border-red-800 rounded bg-black/60">
          Failed to load graph data: {loadError}
        </div>
      </div>
    );
  }

  return (
    <div className="brain-view-container" ref={mountRef}>
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center z-20">
          <span className="text-white/50 text-sm font-mono">Loading graph…</span>
        </div>
      )}

      {/* Overlay controls */}
      <div className="brain-view-controls">
        <input
          type="text"
          className="brain-view-search"
          placeholder="Search nodes…"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          aria-label="Search nodes"
        />
        <button
          type="button"
          className={`brain-view-btn${filterMode === "all" ? " active" : ""}`}
          onClick={() => setFilterMode("all")}
        >
          All
        </button>
        <button
          type="button"
          className={`brain-view-btn${filterMode === "all" ? " active" : ""}`}
          onClick={() => {
            setFilterMode("all");
            setSearchQuery("");
          }}
        >
          By category
        </button>
        <button
          type="button"
          className={`brain-view-btn${filterMode === "subgraph" ? " active" : ""}`}
          onClick={() => setFilterMode("subgraph")}
        >
          Subgraph
        </button>
      </div>

      {/* Tooltip */}
      {tooltip && (
        <div
          className="brain-view-tooltip"
          style={{ left: tooltip.x + 14, top: tooltip.y - 10 }}
        >
          {tooltip.text}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Edge position update helper (outside component to avoid closure capture)
// ---------------------------------------------------------------------------

function updateEdgePositions(
  buffer: Float32Array,
  positions: NodePos[],
  edgeIndices: [number, number][],
): void {
  let offset = 0;
  for (const [a, b] of edgeIndices) {
    buffer[offset++] = positions[a].x;
    buffer[offset++] = positions[a].y;
    buffer[offset++] = positions[a].z;
    buffer[offset++] = positions[b].x;
    buffer[offset++] = positions[b].y;
    buffer[offset++] = positions[b].z;
  }
}
