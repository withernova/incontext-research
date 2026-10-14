import { useState } from "react";
import { createRoot } from "react-dom/client";
import { ExperimentHandoffPanel } from "../src/ExperimentHandoffPanel";
import type { Experiment } from "../src/types";
import "../src/styles.css";
function Fixture(){
  const [experiment,setExperiment]=useState<Experiment>({id:"E-012",title:"Handoff",status:"planned",workflow_stage:"awaiting_confirmation",agent_handoff:{contract:"survey-tool.experiment-handoff/v1",experiment_id:"E-012",verified_facts:[{label:"代码入口",value:"已核验",evidence:"repo/entry.py"}],proposal:{objective:"验证 head 路径",implementation_scope:"新增独立模块",evaluation:"比较 clean 与 rescue"},questions:[],risks:["存在分布外风险"]}});
  return <ExperimentHandoffPanel key={experiment.workflow_stage} experiment={experiment} saving={false} onConfirm={(proposal,answers)=>setExperiment(current=>({...current,...proposal,user_answers:answers,workflow_stage:"confirmed"}))}/>;
}
createRoot(document.getElementById("root")!).render(<Fixture/>);
