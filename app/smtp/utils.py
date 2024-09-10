import re


def minify_html(html: str) -> str:
    def min_html(html: str) -> str:
        # Remove HTML comments
        html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
        # Remove whitespace between tags
        html = re.sub(r">\s+<", "><", html)
        # Remove leading and trailing whitespace
        return html.strip()

    def min_css(css: str) -> str:
        # Remove CSS comments
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
        # Remove unnecessary whitespace
        css = re.sub(r"\s+", " ", css)
        # Remove whitespace around colons, semicolons, and braces
        css = re.sub(r"\s*([:;{}])\s*", r"\1", css)
        # Remove leading and trailing whitespace
        return css.strip()

    def replace_style_tags(match):
        css = match.group(1)
        css = min_css(css)
        return f"<style>{css}</style>"

    html = re.sub(r"<style>(.*?)</style>", replace_style_tags, html, flags=re.DOTALL)
    html = min_html(html)

    return html
