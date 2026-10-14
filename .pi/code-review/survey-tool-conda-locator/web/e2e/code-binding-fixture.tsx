import {createRoot} from "react-dom/client";
import {EnvironmentBindingsPanel} from "../src/EnvironmentBindingsPanel";
import "../src/styles.css";
createRoot(document.getElementById("root")!).render(<EnvironmentBindingsPanel projectPath="/fixture" initialWorkspaceId="W" onClose={()=>{}} onChanged={async()=>{}}/>);
