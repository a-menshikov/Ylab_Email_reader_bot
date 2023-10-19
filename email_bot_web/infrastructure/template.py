HTML_FORMAT = """
<html>
    <head>
        <div style="width:1000px; height:1000;
        font-family: 'Noto Color Emoji',
        Arial, sans-serif;">
    </head>
    <body>
        <h3><u>От:</u> {sender}</h3>
        <h3><u>Кому:</u> {recipient}</h3>
        <h3><u>Тема:</u> {subject}</h3>
        <h3><u>Вложения:</u></h3>
        {attachments}
        <h3><u>Текст письма:</u></h3>
        {text}
    </body>
</html>
"""
