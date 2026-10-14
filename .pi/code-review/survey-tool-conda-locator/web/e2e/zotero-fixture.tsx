import { useState } from "react";
import { createRoot } from "react-dom/client";
import { ZoteroBrowser } from "../src/ZoteroBrowser";
import type { StoredPaperCandidate } from "../src/api";
import "../src/styles.css";

function Fixture() {
  const [saved, setSaved] = useState<Map<string, StoredPaperCandidate>>(new Map());
  const [failedOnce, setFailedOnce] = useState(false);
  return <div style={{containerType:"inline-size",containerName:"finder-dialog",padding:12}}><ZoteroBrowser
    items={[
      {id:1,title:"Local PDF Paper",authors:["Ada"],has_pdf:true,already_in:false},
      {id:2,title:"Metadata Only",authors:[],has_pdf:false,already_in:false},
      {id:3,title:"Retry Paper",authors:[],has_pdf:true,already_in:false},
      {id:4,title:"Existing Paper",authors:[],has_pdf:true,already_in:true},
    ]} loading={false} enabled saved={saved} onView={()=>{}}
    onAdd={async item=>{
      if(item.id===3&&!failedOnce){setFailedOnce(true);return false;}
      const source_url=`https://www.zotero.org/items/${item.id}`;
      setSaved(current=>new Map(current).set(source_url,{id:`PC-${item.id}`,source_url,verification_status:"unverified"} as StoredPaperCandidate));
      return true;
    }}/></div>;
}
createRoot(document.getElementById("root")!).render(<Fixture/>);
