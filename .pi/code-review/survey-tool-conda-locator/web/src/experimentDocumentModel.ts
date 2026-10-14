// Resolve only local Markdown navigation. The server independently enforces the Experiment boundary.
export function resolveExperimentDocumentLink(currentPath:string,href:string):string|null {
  if(!href||href.startsWith("#")||href.startsWith("/")||href.includes("\\")||/^[a-z][a-z0-9+.-]*:/i.test(href))return null;
  try{
    const decoded=decodeURIComponent(href.split(/[?#]/)[0]);
    if(decoded.startsWith("/")||decoded.includes("\\")||decoded.includes("\0"))return null;
    const parts=currentPath.split("/").slice(0,-1);
    for(const part of decoded.split("/")){
      if(!part||part===".")continue;
      if(part===".."){if(!parts.length)return null;parts.pop();continue}
      if(part.startsWith(".")||part.includes(":")||/^E-\d+$/i.test(part))return null;
      parts.push(part);
    }
    const path=parts.join("/");
    return /\.md$/i.test(path)?path:null;
  }catch{return null}
}
export function stripDocumentProperties(content:string):string {
  return content.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/,"");
}
