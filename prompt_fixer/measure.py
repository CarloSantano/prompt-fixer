"""Full-path token ledger; reported telemetry is never fabricated from text length."""
from .validation import PackageError

def count(value, label):
    if value is None:
        return None
    if type(value) is not int or value<0:
        raise PackageError(label+" must be a nonnegative integer or null")
    return value

def arm_total(arm):
    steps = arm.get("steps")
    if not isinstance(steps,list) or not steps:
        raise PackageError("Each arm needs every observed pipeline step")
    total, missing, stages = 0, [], []
    for index, step in enumerate(steps):
        if not isinstance(step,dict) or not isinstance(step.get("stage"),str) or not step["stage"].strip():
            raise PackageError("Every step needs a stage")
        stages.append(step["stage"])
        incoming = count(step.get("input_tokens"),"input_tokens")
        outgoing = count(step.get("output_tokens"),"output_tokens")
        cached = count(step.get("cached_input_tokens"),"cached_input_tokens")
        reasoning = count(step.get("reasoning_tokens"),"reasoning_tokens")
        if cached is not None and incoming is not None and cached>incoming:
            raise PackageError("cached_input_tokens is a subset of input_tokens")
        if reasoning is not None and outgoing is not None and reasoning>outgoing:
            raise PackageError("Use this ledger only when reasoning_tokens is included in output_tokens")
        if incoming is None or outgoing is None:
            missing.append(index)
        else:
            total += incoming+outgoing
    return {"known_subtotal_tokens":total,"total_tokens":None if missing else total,"missing_usage_steps":missing,"stages":stages,"step_count":len(steps)}

def compare_ledger(data):
    if type(data.get("schema_version")) is not int or data.get("schema_version")!=1 or not all(isinstance(data.get(k),str) and data[k].strip() for k in ("task_id","condition_id")):
        raise PackageError("Expected schema_version=1, task_id and condition_id")
    if not isinstance(data.get("direct"),dict) or not isinstance(data.get("fixed"),dict):
        raise PackageError("Both direct and fixed arms are required")
    direct, fixed = data["direct"],data["fixed"]
    a,b = arm_total(direct),arm_total(fixed)
    reasons = []
    if not isinstance(direct.get("execution_model"),str) or not direct["execution_model"].strip() or direct.get("execution_model")!=fixed.get("execution_model"):
        reasons.append("execution_model_not_matched")
    for name, arm in (("direct",direct),("fixed",fixed)):
        if arm.get("passed") is not True or not isinstance(arm.get("outcome_evidence"),str) or not arm["outcome_evidence"].strip():
            reasons.append(name+"_successful_outcome_not_evidenced")
    if a["missing_usage_steps"] or b["missing_usage_steps"]:
        reasons.append("incomplete_usage")
    if any(x in ("fix","compile") for x in a["stages"]):
        reasons.append("direct_arm_contains_fixer_step")
    if not any(x in ("fix","compile","combined") for x in b["stages"]):
        reasons.append("fixed_arm_missing_fixer_or_combined_usage")
    if data.get("synthetic") is True:
        reasons.append("synthetic_fixture")
    eligible = not reasons
    delta = b["total_tokens"]-a["total_tokens"] if eligible else None
    percent = (a["total_tokens"]-b["total_tokens"])/a["total_tokens"]*100 if eligible and a["total_tokens"] else None
    return {"task_id":data["task_id"],"condition_id":data["condition_id"],"direct":a,"fixed":b,"comparison_eligible":eligible,"ineligible_reasons":reasons,"fixed_minus_direct_tokens":delta,"reported_saving_percent":percent,"source":"caller-supplied usage and outcome evidence; not independently captured or verified by this helper","money_saving":"not calculated; token totals are not a billing estimate","scope":"Includes provided fixer, execution and repair steps. Missing steps cannot be discovered automatically. Cache/reasoning subsets are not double counted. No provider/API calls."}
