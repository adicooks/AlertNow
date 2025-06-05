from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, blue, green, red, gray, orange
import os
from pygments import highlight
from pygments.lexers import guess_lexer_for_filename
from pygments.token import Token

COLOR_MAPPING = {
    Token.Keyword: blue,
    Token.String: green,
    Token.Comment: gray,
    Token.Operator: red,
    Token.Number: orange,
    Token.Name: black,
}

output_pdf = "Project_Code.pdf"
pdf = canvas.Canvas(output_pdf)
pdf.setFont("Courier", 10)

folder_path = "/Users/adi/Downloads/AlertNow"
y_position = 800

for root, _, files in os.walk(folder_path):
    for file in files:
        if file.endswith((".py", ".js", ".cpp", ".java", ".txt", ".html", ".css", ".swift")):
            file_path = os.path.join(root, file)

            try:
                pdf.setFillColor(black)
                pdf.drawString(100, y_position, f"File: {file}")
                y_position -= 15

                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    code = f.read()
                    lexer = guess_lexer_for_filename(file, code)
                    tokens = list(lexer.get_tokens(code))

                    x_position = 100

                    for token_type, token_value in tokens:
                        try:
                            color = COLOR_MAPPING.get(token_type, black)
                            pdf.setFillColor(color)

                            words = token_value.split("\n")
                            for word in words:
                                pdf.drawString(x_position, y_position, word[:100])
                                x_position += len(word) * 6
                                if x_position > 500:
                                    x_position = 100
                                    y_position -= 12

                                if y_position < 50:
                                    pdf.showPage()
                                    pdf.setFont("Courier", 10)
                                    x_position = 100
                                    y_position = 800
                        except Exception:
                            continue

                    y_position -= 12
            except Exception:
                continue

pdf.save()
print("PDF saved as 'Project_Code.pdf'")
