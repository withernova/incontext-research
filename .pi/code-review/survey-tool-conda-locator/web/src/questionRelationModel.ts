import type { V2Object, V2Relation } from "./api";
import type { Question } from "./types";

export type QuestionTargetType="paper"|"comparison"|"finding"|"experiment"|"idea"|"claim";
export type QuestionRelationView={targetId:string;targetType:QuestionTargetType;relationType:string;authority:"question_frontmatter"|"v2_navigation_index";relation?:V2Relation};
export const targetLabels:Record<QuestionTargetType,string>={paper:"论文",comparison:"对比",finding:"Finding",experiment:"实验",idea:"Idea",claim:"Claim"};
const fields:Partial<Record<QuestionTargetType,keyof Question>>={paper:"papers",comparison:"comparisons",finding:"findings",experiment:"experiments"};
export function relationTypeFor(type:QuestionTargetType){return type==="experiment"?"tests":type==="idea"?"derived_from":"discusses"}
export function mergeQuestionRelations(question:Question,indexRelations:V2Relation[],objects:V2Object[]):QuestionRelationView[]{
 const objectTypes=new Map(objects.map(item=>[item.id,item.type]));const merged=new Map<string,QuestionRelationView>();
 (Object.entries(fields) as Array<[QuestionTargetType,keyof Question]>).forEach(([type,field])=>((question[field] as string[]|undefined)||[]).forEach(targetId=>merged.set(targetId,{targetId,targetType:type,relationType:relationTypeFor(type),authority:"question_frontmatter"})));
 indexRelations.filter(item=>item.from_object_id===question.id).forEach(relation=>{const type=objectTypes.get(relation.to_object_id) as QuestionTargetType;if(!targetLabels[type])return;const current=merged.get(relation.to_object_id);merged.set(relation.to_object_id,{...current,targetId:relation.to_object_id,targetType:type,relationType:relation.relation_type,authority:(relation.metadata?.authority==="v2_navigation_index"?"v2_navigation_index":"question_frontmatter"),relation})});
 return [...merged.values()];
}
export function filterRelationCandidates(objects:V2Object[],type:QuestionTargetType,query:string,existingIds:Iterable<string>){const existing=new Set(existingIds);const needle=query.trim().toLowerCase();return objects.filter(item=>item.type===type&&!existing.has(item.id)&&(!needle||`${item.id} ${item.title}`.toLowerCase().includes(needle)))}
