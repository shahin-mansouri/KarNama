from html import escape
from html.parser import HTMLParser

from django import template
from django.utils.safestring import mark_safe


register = template.Library()

_ALLOWED_TAGS = {"blockquote", "h2", "h3", "li", "ol", "p", "strong", "ul"}
_SUPPRESSED_TAGS = {"script", "style"}


class _BlogHTMLSanitizer(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.open_tags = []
        self.suppressed_depth = 0

    def handle_starttag(self, tag, attrs):
        if self.suppressed_depth:
            if tag in _SUPPRESSED_TAGS:
                self.suppressed_depth += 1
            return

        if tag in _SUPPRESSED_TAGS:
            self.suppressed_depth = 1
        elif tag in _ALLOWED_TAGS:
            self.parts.append(f"<{tag}>")
            self.open_tags.append(tag)

    def handle_endtag(self, tag):
        if self.suppressed_depth:
            if tag in _SUPPRESSED_TAGS:
                self.suppressed_depth -= 1
            return

        if tag not in self.open_tags:
            return

        while self.open_tags:
            open_tag = self.open_tags.pop()
            self.parts.append(f"</{open_tag}>")
            if open_tag == tag:
                break

    def handle_data(self, data):
        if not self.suppressed_depth:
            self.parts.append(escape(data, quote=False))

    def sanitized_html(self, content):
        self.feed(content)
        self.close()
        while self.open_tags:
            self.parts.append(f"</{self.open_tags.pop()}>")
        return "".join(self.parts)


@register.filter
def render_blog_content(content):
    sanitizer = _BlogHTMLSanitizer()
    return mark_safe(sanitizer.sanitized_html(content))
