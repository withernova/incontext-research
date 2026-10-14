/** Display-only project path. Backend revalidates containment and symlinks. */
export function projectRepositoryPath(codeRoot:string,workspaceId:string,repositoryUrl:string):string {
 const url=repositoryUrl.trim().replace(/\.git$/,"");
 const match=url.match(/^https:\/\/github\.com\/[A-Za-z0-9_.-]+\/([A-Za-z0-9][A-Za-z0-9._-]{0,159})$/);
 if(!codeRoot.startsWith("/")||/[\x00-\x1f]/.test(codeRoot)||!match||!/^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$/.test(workspaceId))return "";
 return `${codeRoot.replace(/\/+$/,"")}/${workspaceId}/${match[1]}`;
}
