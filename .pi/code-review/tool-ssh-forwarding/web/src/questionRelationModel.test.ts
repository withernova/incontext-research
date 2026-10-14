import {describe,expect,it} from "vitest";
import {filterRelationCandidates,mergeQuestionRelations,relationTypeFor} from "./questionRelationModel";

describe("question relation model",()=>{
 it("merges canonical and indexed relations without duplicates",()=>{const rows=mergeQuestionRelations({id:"Q-01",title:"Q",status:"open",papers:["paper1"]},[{id:"REL-1",from_object_id:"Q-01",to_object_id:"paper1",relation_type:"discusses",metadata:{authority:"question_frontmatter"}}],[{id:"paper1",type:"paper",title:"Paper",lifecycle_status:"reference",canonical_path:"",revision:1,created_at:"",updated_at:""}]);expect(rows).toHaveLength(1);expect(rows[0].relation?.id).toBe("REL-1")});
 it("filters candidates and keeps fixed semantics",()=>{const objects=[{id:"I-01",type:"idea",title:"Mechanism",lifecycle_status:"reference",canonical_path:"",revision:1,created_at:"",updated_at:""}];expect(filterRelationCandidates(objects,"idea","mech",[])).toHaveLength(1);expect(filterRelationCandidates(objects,"idea","",["I-01"])).toHaveLength(0);expect(relationTypeFor("idea")).toBe("derived_from");expect(relationTypeFor("experiment")).toBe("tests")});
});
