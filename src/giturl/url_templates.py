from enum import Enum, auto

class State(Enum):
    PLAIN_TEXT = auto()
    FILL_POINT_SEGMENT = auto()
    FILL_POINT = auto()

def parse_template(template_str: str) -> Template:
    state = State.PLAIN_TEXT

    text_buf = ""
    raw_fp_segment_buf = ""
    segments = []
    fp_names = []
    fill_point_name_buf = ""

    def process_char(char: str):
        nonlocal state, text_buf, raw_fp_segment_buf, fp_names, fill_point_name_buf

        match state:
            case State.PLAIN_TEXT:
                if char == "{":
                    # close text
                    if text_buf:
                        segments.append(text_buf)
                    # open fill point segment
                    raw_fp_segment_buf = ""
                    fp_names = []
                    state = State.FILL_POINT_SEGMENT
                else:
                    text_buf += char

            case State.FILL_POINT_SEGMENT:
                if char == "{":
                    raw_fp_segment_buf += char
                    # open fill point
                    fill_point_name_buf = ""
                    state = State.FILL_POINT
                elif char == "}":
                    # close fill point segment
                    segments.append(FillPointSegment(raw_fp_segment_buf, fp_names))
                    # open text
                    text_buf = ""
                    state = State.PLAIN_TEXT
                else:
                    raw_fp_segment_buf += char

            case State.FILL_POINT:
                if char == "}":
                    raw_fp_segment_buf += char
                    # close fill point
                    fp_names.append(fill_point_name_buf)
                    # back to fill point segment
                    state = State.FILL_POINT_SEGMENT
                else:
                    raw_fp_segment_buf += char
                    fill_point_name_buf += char

    for char in template_str:
        process_char(char)

    if state != State.PLAIN_TEXT:
        raise ValueError(f"Unclosed fill point segment in template string: {template_str}")

    if text_buf:
        segments.append(text_buf)

    return Template(segments)


class Template:
    def __init__(self, segments: list[str | FillPointSegment]):
        self.segments = segments

    def apply(self, template_args: dict[str, str]) -> str:
        result = ""
        for seg in self.segments:
            if isinstance(seg, str):
                result += seg
            elif isinstance(seg, FillPointSegment):
                result += seg.apply(template_args)
        return result


class FillPointSegment:
    def __init__(self, raw: str, fill_points_names: list[str]):
        self.raw = raw
        self.fill_point_names = fill_points_names

    def apply(self, template_args: dict) -> str:
        # if any of the fill points are missing or empty, return empty string
        for fpn in self.fill_point_names:
            if fpn not in template_args or not template_args[fpn]:
                return ""
        # otherwise replace all fill points with their corresponding values
        result = self.raw
        for fpn in self.fill_point_names:
            fill_point = f"{{{fpn}}}"
            result = result.replace(fill_point, template_args[fpn])
        return result
