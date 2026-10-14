import { createRoot } from "react-dom/client";
import { AiDiscussionPanel } from "../src/AiDiscussionPanel";
import "../src/styles.css";
createRoot(document.getElementById("root")!).render(<AiDiscussionPanel targetType="experiment" targetId="E-test" targetLabel="测试提问" projectPath="/fixture" onClose={()=>{}}/>);
