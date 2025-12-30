from diff_engine import diff

def confidence(entity):
    if entity is None:
        return "LOW"
    if entity.get("@id"):
        return "HIGH"
    return "MEDIUM"

def narrative(entity):
    if not entity:
        return "Entity not recognized by Google Knowledge Graph."
    if entity.get("@id") and entity.get("detailedDescription"):
        return "Entity is recognized with canonical identity but lacks strong authority linkage."
    return "Entity is partially recognized with weak canonical signals."

def generate(name, today, yesterday):
    report = []
    report.append(f"ENTITY: {name}")
    report.append(f"STATUS: {'Present' if today else 'Absent'}")
    report.append(f"CONFIDENCE: {confidence(today)}")

    if today:
        report.append(f"KG ID: {today.get('@id','None')}")
        report.append(f"TYPE: {', '.join(today.get('@type',[]))}")
        report.append(f"DESCRIPTION: {today.get('description','N/A')}")

    changes = diff(yesterday or {}, today or {})
    if changes:
        report.append("CHANGES DETECTED:")
        for k, v in changes.items():
            report.append(f" - {k}: {v['before']} → {v['after']}")
    else:
        report.append("NO CHANGES SINCE LAST REPORT")

    report.append("INTERPRETATION:")
    report.append(narrative(today))

    return "\n".join(report)
