import type { RunTrialValue } from "./types";

export type TrialAxis={name:string;values:RunTrialValue[]};

const scalar=(raw:string):RunTrialValue=>{
  const value=raw.trim();
  if(/^(true|false)$/i.test(value))return value.toLowerCase()==="true";
  if(/^-?(?:\d+\.?\d*|\.\d+)$/.test(value))return Number(value);
  return value;
};

export function parseTrialAxes(text:string):TrialAxis[]{
  const seen=new Set<string>();
  const axes=text.split("\n").map(line=>line.trim()).filter(Boolean).map((line,index)=>{
    const split=line.indexOf("=");
    if(split<1)throw new Error(`第 ${index+1} 行应为 参数名 = 值1, 值2`);
    const name=line.slice(0,split).trim();
    if(!/^[A-Za-z][A-Za-z0-9_.-]{0,63}$/.test(name)||seen.has(name))throw new Error(`第 ${index+1} 行参数名无效或重复`);
    const values=line.slice(split+1).split(",").map(scalar).filter(value=>String(value).trim()!=="");
    if(!values.length)throw new Error(`参数 ${name} 没有值`);
    seen.add(name);return{name,values:[...new Map(values.map(value=>[JSON.stringify(value),value])).values()]};
  });
  if(!axes.length)throw new Error("请至少填写一个参数轴");
  const count=axes.reduce((total,axis)=>total*axis.values.length,1);
  if(count>64)throw new Error("参数组合最多 64 个 Trials");
  return axes;
}

export const trialCount=(axes:TrialAxis[])=>axes.reduce((total,axis)=>total*axis.values.length,1);
