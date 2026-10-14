import type { DiscussionFocus, DiscussionMode, DiscussionTargetType, DiscussionTask } from "./api";

export const RUN_IMPLEMENTATION_DEFAULT_REQUEST="按当前 Run 已登记的设计完成实际算法实现，重点落实数据流、损失/梯度、干预逻辑与指标计算。复用有效检查证据，只验证本次改动的具体正确性风险；不新增占位文件或重复 smoke。完成后提交代码，并按已有授权推进。";

export function initialDiscussionRequest(task:DiscussionTask){
  return task==="run_implementation"?RUN_IMPLEMENTATION_DEFAULT_REQUEST:"";
}

export function discussionPreviewPayload(targetType:DiscussionTargetType,targetId:string,mode:DiscussionMode,task:DiscussionTask,request:string,focus:DiscussionFocus,referenceIds:string[]=[],discussionSummary="",codeRepositoryId=""){
  return {target_type:targetType,target_id:targetId,mode,task,request,focus,reference_ids:referenceIds,discussion_summary:discussionSummary,...(codeRepositoryId?{code_repository_id:codeRepositoryId}:{})};
}
