import { createRoot } from "react-dom/client";
import { ExperimentWorkspace } from "../src/ExperimentWorkspace";
import type { WorkspaceData } from "../src/types";
import "../src/styles.css";

const data={project:{path:"/fixture",name:"文档测试"},dashboard:{experiments:[{id:"E-012",title:"独立实验十二",objective:"验证文档定位",status:"planned"},{id:"E-013",title:"独立实验十三",objective:"验证隔离",status:"planned"}],runs:[]}} as unknown as WorkspaceData;
createRoot(document.getElementById("root")!).render(<ExperimentWorkspace data={data} onBack={()=>{}} onChanged={async()=>{}}/>);
