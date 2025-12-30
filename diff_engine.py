def diff(old, new):
    changes = {}

    for key in ["@id", "name", "@type", "description"]:
        if old.get(key) != new.get(key):
            changes[key] = {
                "before": old.get(key),
                "after": new.get(key)
            }

    old_url = old.get("detailedDescription", {}).get("url")
    new_url = new.get("detailedDescription", {}).get("url")

    if old_url != new_url:
        changes["authority_link"] = {
            "before": old_url,
            "after": new_url
        }

    return changes
