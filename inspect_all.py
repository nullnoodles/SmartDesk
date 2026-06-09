import re

def inspect_all():
    content = open("app/ui/styles/style.qss", encoding="utf-8").read()
    blocks = content.split("}")
    for b in blocks:
        if "{" not in b:
            continue
        sel, body = b.split("{", 1)
        sel = sel.strip()
        body = body.strip()
        
        # Check if selector contains QWidget, QFrame, QLabel, or * (wildcard selector)
        # We want to check if any of these words exist as a standalone token or word in the selector
        # (e.g. QFrame, but not QFrame#right_workspace or QFrame::up-button, although QFrame#id might inherit)
        words = re.findall(r'\b(QWidget|QFrame|QLabel)\b|(\*)', sel)
        if words and "border" in body:
            # check if the border is not none/transparent
            border_rules = re.findall(r'border(?:-[a-z]+)?\s*:\s*([^;]+);', body)
            has_visible_border = False
            for rule in border_rules:
                rule = rule.strip()
                if rule not in ["none", "transparent", "0", "0px"]:
                    has_visible_border = True
            
            print(f"Selector: {sel}")
            print(f"Body:\n{body}")
            print(f"Has visible border: {has_visible_border}")
            print("-" * 50)

if __name__ == "__main__":
    inspect_all()
