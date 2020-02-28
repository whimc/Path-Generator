import markdown2

TEMPLATE = TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <meta name="referrer" content="no-referrer" />
    <meta name="referrer" content="unsafe-url" />
    <meta name="referrer" content="origin" />
    <meta name="referrer" content="no-referrer-when-downgrade" />
    <meta name="referrer" content="origin-when-cross-origin" />
    <title>Page Title</title>
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            font-family: Helvetica,Arial,sans-serif;
        }
        code, pre {
            font-family: monospace;
        }
    </style>
</head>
<body>
<div class="container">
{{content}}
</div>
</body>
</html>
"""

def toHTML(md_file_path):
    md_file = open(md_file_path, 'r')
    content = md_file.read()
    html = markdown2.markdown(content, extras=['tables'])
    return TEMPLATE.replace('{{content}}', html)