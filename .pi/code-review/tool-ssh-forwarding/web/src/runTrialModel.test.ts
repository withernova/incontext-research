import {describe,expect,it} from "vitest";
import {parseTrialAxes,trialCount} from "./runTrialModel";

describe("run trial matrix",()=>{
  it("parses typed axes and computes cartesian size",()=>{const axes=parseTrialAxes("variant = baseline, query_permuted\nseed = 1, 2, 3\nuse_cache = true, false");expect(axes[1].values).toEqual([1,2,3]);expect(axes[2].values).toEqual([true,false]);expect(trialCount(axes)).toBe(12)});
  it("rejects duplicate names and oversized matrices",()=>{expect(()=>parseTrialAxes("seed=1\nseed=2")).toThrow(/重复/);expect(()=>parseTrialAxes(`a=${Array.from({length:9},(_,i)=>i).join(",")}\nb=${Array.from({length:9},(_,i)=>i).join(",")}`)).toThrow(/64/)})
});
