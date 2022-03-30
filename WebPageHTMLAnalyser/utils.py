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


def html_to_json_improved(html):
    return {
        "tag": html.tag,
        "classes": html.get('class').split(" ") if html.get('class') else [],
        "id": html.get('id').split(" ") if html.get('id') else [],
        "children": canonical(list(filter(filter_unwanted_tags_canonical, html.getchildren())))
    }


def canonical(children):
    result = []
    for index, child in enumerate(children):
        if isinstance(child, lxml.html.HtmlElement):
            if index != 0:
                previous_child = children[index - 1]
                previous_classes = previous_child.get('class').split(" ") if previous_child.get('class') else []
                previous_ids = previous_child.get('id').split(" ") if previous_child.get('id') else []
                actual_classes = child.get('class').split(" ") if child.get('class') else []
                actual_ids = child.get('id').split(" ") if child.get('id') else []
                if len(actual_classes) != 0:
                    if previous_child.tag != child.tag or set(previous_classes) != set(actual_classes):
                        result.append(html_to_json_improved(child))
                elif len(actual_ids) != 0:
                    if previous_child.tag != child.tag or set(previous_ids) != set(actual_ids):
                        result.append(html_to_json_improved(child))
                else:
                    result.append(html_to_json_improved(child))
            else:
                result.append(html_to_json_improved(child))
    return result


def filter_unwanted_tags_canonical(element):
    if element and element.tag.upper() not in unwantedTags:
        return element
