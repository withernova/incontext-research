import { CheckCircle2, Database, Link2, TriangleAlert } from "lucide-react";
import type { V2ObjectIndex } from "./api";

export function V2IndexNote({ index, type, legacyCount }: { index: V2ObjectIndex | null | undefined; type: string; legacyCount: number }) {
  if (!index?.initialized) return null;
  const nativeCount = index.summary[type] ?? 0;
  const ids = new Set(index.objects.filter((object) => object.type === type).map((object) => object.id));
  const typeRelations = index.relations.filter((relation) => ids.has(relation.from_object_id) || ids.has(relation.to_object_id)).length;
  const matched = nativeCount === legacyCount;
  return (
    <div className={`v2-index-note ${matched ? "matched" : "mismatch"}`}>
      {matched ? <CheckCircle2 size={15} /> : <TriangleAlert size={15} />}
      <span>
        <strong>{matched ? "v2 索引一致" : "v2 索引待核对"}</strong>
        <small>native {type} {nativeCount} / legacy {legacyCount} · 关系 {typeRelations} 条 · 正文 authority 不变</small>
      </span>
      <Link2 size={14} />
    </div>
  );
}
