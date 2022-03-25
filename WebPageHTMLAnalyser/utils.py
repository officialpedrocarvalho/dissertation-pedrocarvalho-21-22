import lxml.html

unwantedTags = [
    "SCRIPT",
    "B",
    "STRONG",
    "EM",
    "MARK",
    "SMALL",
    "DEL",
    "INS",
    "SUB",
    "SUP",
    "STYLE",
    "NOSCRIPT",
]


def json_to_array(json, tag, children):
    """Recursively fetch values from nested JSON."""
    values = []

    def extract(json, values):
        for element in json[children]:
            values.append(element[tag])
            extract(element, values)
        return values

    values = extract(json, values)
    return values


def json_count_elements(json, tag, children):
    return len(json_to_array(json, tag, children))


def html_to_json(html):
    return {
        "tag": html.tag,
        "classes": html.get('class').split(" ") if html.get('class') else [],
        "id": html.get('id').split(" ") if html.get('id') else [],
        "children": list(filter(filter_unwanted_tags, map(node, html.getchildren())))
    }


def node(element):
    if isinstance(element, lxml.html.HtmlElement):
        return html_to_json(element)


def filter_unwanted_tags(element):
    if element and element["tag"].upper() not in unwantedTags:
        return element


def canonical_extraction(json):
    """Recursively builds a string representing the canonical form of a html web page structure."""
    values = []

    def extract(json, values):
        """Compares classes and id from the actual element with the previous one and:
            - if one of these matches the element is ignored"""
        if json["children"]:
            values.append("(")
        for count, element in enumerate(json["children"]):
            if count != 0:
                if len(element["classes"]) != 0:
                    if json["children"][count - 1]["tag"] != element["tag"] or set(
                            json["children"][count - 1]["classes"]) != set(element["classes"]):
                        values.append(element["tag"])
                        extract(element, values)
                elif len(element["id"]) != 0:
                    if json["children"][count - 1]["tag"] != element["tag"] or set(
                            json["children"][count - 1]["id"]) != set(element["id"]):
                        values.append(element["tag"])
                        extract(element, values)
                else:
                    values.append(element["tag"])
                    extract(element, values)
            else:
                values.append(element["tag"])
                extract(element, values)
        if json["children"]:
            values.append(")")
        return values

    values.append(json["tag"])
    values = extract(json, values)
    return ' '.join(values)
