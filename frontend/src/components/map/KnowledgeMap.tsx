"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge as RFEdge,
  ReactFlowProvider,
  useReactFlow,
} from "reactflow";
import dagre from "dagre";
import "reactflow/dist/style.css";

import KCNode from "./KCNode";
import { api } from "@/lib/api";
import { GraphData, MasteryEntry, MasteryStatus, Route } from "@/lib/types";
import { useLearnerStore } from "@/store/learnerStore";

const nodeTypes = { kcNode: KCNode };

const NODE_WIDTH = 160;
const NODE_HEIGHT = 72;

function getLayoutedNodes(nodes: Node[], edges: RFEdge[]): Node[] {
  const g = new dagre.graphlib.Graph();
  g.setDefaultEdgeLabel(() => ({}));
  g.setGraph({ rankdir: "TB", ranksep: 80, nodesep: 50 });
  nodes.forEach((n) => g.setNode(n.id, { width: NODE_WIDTH, height: NODE_HEIGHT }));
  edges.forEach((e) => g.setEdge(e.source, e.target));
  dagre.layout(g);
  return nodes.map((n) => {
    const pos = g.node(n.id);
    return { ...n, position: { x: pos.x - NODE_WIDTH / 2, y: pos.y - NODE_HEIGHT / 2 } };
  });
}

function MapInner({
  graphData,
  masteryList,
  route,
}: {
  graphData: GraphData;
  masteryList: MasteryEntry[];
  route: Route | null;
}) {
  const { fitView } = useReactFlow();
  const { currentKcId, routeKcIds } = useLearnerStore();

  const masteryMap = useMemo(() => {
    const m: Record<number, MasteryEntry> = {};
    masteryList.forEach((e) => (m[e.kc_id] = e));
    return m;
  }, [masteryList]);

  const routeSet = useMemo(() => new Set(routeKcIds), [routeKcIds]);
  const activeRouteEdgeSet = useMemo(() => {
    if (!route) return new Set<string>();
    const s = new Set<string>();
    for (let i = 0; i < route.ordered_kc_ids.length - 1; i++) {
      s.add(`${route.ordered_kc_ids[i]}-${route.ordered_kc_ids[i + 1]}`);
    }
    return s;
  }, [route]);

  const rawNodes: Node[] = useMemo(
    () =>
      graphData.kcs.map((kc) => {
        const entry = masteryMap[kc.kc_id];
        const status: MasteryStatus = entry?.status ?? "locked";
        const pMastery = entry?.p_mastery ?? kc.p_l0;
        return {
          id: String(kc.kc_id),
          type: "kcNode",
          data: {
            label: kc.name,
            status,
            pMastery,
            isCurrent: kc.kc_id === currentKcId,
            isOnRoute: routeSet.has(kc.kc_id),
          },
          position: { x: 0, y: 0 },
        };
      }),
    [graphData, masteryMap, currentKcId, routeSet]
  );

  const rawEdges: RFEdge[] = useMemo(
    () =>
      graphData.edges.map((e) => {
        const key = `${e.from_kc_id}-${e.to_kc_id}`;
        const isRoute = activeRouteEdgeSet.has(key);
        return {
          id: `e-${e.edge_id}`,
          source: String(e.from_kc_id),
          target: String(e.to_kc_id),
          animated: isRoute,
          style: isRoute
            ? { stroke: "#3b82f6", strokeWidth: 2.5, strokeDasharray: "6 3" }
            : { stroke: "#cbd5e1", strokeWidth: 1.5 },
        };
      }),
    [graphData, activeRouteEdgeSet]
  );

  const nodes = useMemo(() => getLayoutedNodes(rawNodes, rawEdges), [rawNodes, rawEdges]);

  useEffect(() => {
    setTimeout(() => fitView({ padding: 0.15 }), 50);
  }, [fitView, nodes.length]);

  return (
    <ReactFlow
      nodes={nodes}
      edges={rawEdges}
      nodeTypes={nodeTypes}
      fitView
      fitViewOptions={{ padding: 0.15 }}
      nodesDraggable={false}
      nodesConnectable={false}
      elementsSelectable={false}
    >
      <Background color="#e2e8f0" gap={20} />
      <Controls />
      <MiniMap nodeColor={(n) => {
        const status: MasteryStatus = n.data?.status ?? "locked";
        const colors: Record<MasteryStatus, string> = {
          locked: "#94a3b8",
          available: "#60a5fa",
          in_progress: "#fbbf24",
          mastered: "#34d399",
        };
        return colors[status];
      }} />
    </ReactFlow>
  );
}

export default function KnowledgeMap() {
  const { learnerId } = useLearnerStore();
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [masteryList, setMasteryList] = useState<MasteryEntry[]>([]);
  const [route, setRoute] = useState<Route | null>(null);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    try {
      const [graph, mastery] = await Promise.all([
        api.getGraph(),
        learnerId ? api.getMastery(learnerId) : Promise.resolve(null),
      ]);
      setGraphData(graph);
      if (mastery) setMasteryList(mastery.masteries);

      if (learnerId) {
        const r = await api.getRoute(learnerId).catch(() => null);
        setRoute(r);
      }
    } catch {
      setError("Failed to load graph data. Is the backend running?");
    }
  }, [learnerId]);

  useEffect(() => { load(); }, [load]);

  if (error) return <div className="text-red-500 text-sm p-4">{error}</div>;
  if (!graphData) return <div className="text-slate-500 text-sm p-4">Loading map...</div>;

  return (
    <div className="w-full h-[600px] rounded-2xl border border-slate-200 overflow-hidden bg-white shadow-sm">
      <ReactFlowProvider>
        <MapInner graphData={graphData} masteryList={masteryList} route={route} />
      </ReactFlowProvider>
    </div>
  );
}
