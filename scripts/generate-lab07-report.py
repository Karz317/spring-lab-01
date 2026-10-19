#!/usr/bin/env python3
"""Generate the Laboratory Work 7 report from source and captured evidence."""

from __future__ import annotations

import json
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUTPUT = DOCS / "Lab07_Kassymzhanov_Arzum.docx"
OBSERVATIONS = json.loads((DOCS / "lab07-observations.json").read_text(encoding="utf-8"))

BLACK = RGBColor(0x00, 0x00, 0x00)
NAVY = "1F4E78"
LIGHT_BLUE = "D9EAF7"
LIGHT_GRAY = "F2F2F2"
MID_GRAY = "808080"
WHITE = "FFFFFF"


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=90, start=100, bottom=90, end=100) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{margin}"))
        if node is None:
            node = OxmlElement(f"w:{margin}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_keep_with_next(paragraph, value=True) -> None:
    paragraph.paragraph_format.keep_with_next = value


def add_page_number(paragraph) -> None:
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, separate, end])


def add_bottom_border(paragraph, color=MID_GRAY, size="4") -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    borders = p_pr.find(qn("w:pBdr"))
    if borders is None:
        borders = OxmlElement("w:pBdr")
        p_pr.append(borders)
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), size)
    bottom.set(qn("w:space"), "3")
    bottom.set(qn("w:color"), color)
    borders.append(bottom)


def configure_document(doc: Document) -> None:
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(1.8)
    section.bottom_margin = Cm(1.7)
    section.left_margin = Cm(2.1)
    section.right_margin = Cm(1.7)
    section.header_distance = Cm(0.7)
    section.footer_distance = Cm(0.7)

    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(10)
    normal.font.color.rgb = BLACK
    normal.paragraph_format.line_spacing = 1.15
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.widow_control = True

    title = doc.styles["Title"]
    title.font.name = "Arial"
    title.font.size = Pt(22)
    title.font.bold = True
    title.font.color.rgb = BLACK
    title.paragraph_format.space_after = Pt(8)
    title_p_pr = title.element.get_or_add_pPr()
    existing_title_border = title_p_pr.find(qn("w:pBdr"))
    if existing_title_border is not None:
        title_p_pr.remove(existing_title_border)

    for name, size in (("Heading 1", 16), ("Heading 2", 12), ("Heading 3", 10.5)):
        style = doc.styles[name]
        style.font.name = "Arial"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = BLACK
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.space_before = Pt(10 if name != "Heading 1" else 0)
        style.paragraph_format.space_after = Pt(6)
    doc.styles["Heading 1"].paragraph_format.page_break_before = True

    code = doc.styles.add_style("Source Code", WD_STYLE_TYPE.PARAGRAPH)
    code.font.name = "Consolas"
    code.font.size = Pt(7.4)
    code.font.color.rgb = BLACK
    code.paragraph_format.space_before = Pt(0)
    code.paragraph_format.space_after = Pt(0)
    code.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    code.paragraph_format.keep_together = False
    code.paragraph_format.widow_control = False

    caption = doc.styles["Caption"]
    caption.font.name = "Arial"
    caption.font.size = Pt(9)
    caption.font.italic = True
    caption.font.color.rgb = BLACK
    caption.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption.paragraph_format.space_after = Pt(8)

    header = section.header.paragraphs[0]
    header.text = "Laboratory Work 7  |  REST API Design"
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    header.runs[0].font.name = "Arial"
    header.runs[0].font.size = Pt(8)
    header.runs[0].font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    add_bottom_border(header, color="BFBFBF", size="3")

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run("Kassymzhanov Arzum | IT1-2404IS | ")
    run.font.name = "Arial"
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    add_page_number(footer)


def add_title_page(doc: Document) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("JSC INTERNATIONAL INFORMATION TECHNOLOGY UNIVERSITY")
    r.bold = True
    r.font.name = "Arial"
    r.font.size = Pt(12)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Department of Information Systems")
    r.font.name = "Arial"
    r.font.size = Pt(11)

    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(54)

    title = doc.add_paragraph(style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.add_run("LABORATORY WORK No. 7")

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.paragraph_format.space_after = Pt(10)
    r = subtitle.add_run("REST API DESIGN")
    r.bold = True
    r.font.name = "Arial"
    r.font.size = Pt(17)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("DTO records - HTTP semantics - Problem Details - OpenAPI").font.size = Pt(11)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(32)
    r = p.add_run("Course: RWPSF 3305\nWeb Application Development with Spring Framework")
    r.font.name = "Arial"
    r.font.size = Pt(11)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.left_indent = Cm(9.2)
    p.paragraph_format.space_before = Pt(54)
    r = p.add_run(
        "Performed by: Kassymzhanov Arzum\n"
        "Group: IT1-2404IS\n"
        "Variant: 12 - RestTestClient"
    )
    r.font.name = "Arial"
    r.font.size = Pt(11)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(72)
    p.add_run("Almaty, 2026").font.size = Pt(11)
    doc.add_page_break()


def add_paragraph(doc: Document, text: str, *, bold_prefix: str | None = None):
    p = doc.add_paragraph()
    if bold_prefix and text.startswith(bold_prefix):
        p.add_run(bold_prefix).bold = True
        p.add_run(text[len(bold_prefix):])
    else:
        p.add_run(text)
    return p


def add_bullets(doc: Document, items: list[str]) -> None:
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(3)
        p.add_run(item)


def add_table(doc: Document, headers: list[str], rows: list[list[str]], widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.style = "Table Grid"
    header = table.rows[0]
    set_repeat_table_header(header)
    for idx, text in enumerate(headers):
        cell = header.cells[idx]
        cell.text = str(text)
        set_cell_shading(cell, NAVY)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_cell_margins(cell)
        for paragraph in cell.paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.space_after = Pt(0)
            for run in paragraph.runs:
                run.font.name = "Arial"
                run.font.size = Pt(8.5)
                run.font.bold = True
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for row_idx, values in enumerate(rows):
        row = table.add_row()
        for idx, value in enumerate(values):
            cell = row.cells[idx]
            cell.text = str(value)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cell)
            if row_idx % 2:
                set_cell_shading(cell, "F7F9FB")
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(0)
                paragraph.paragraph_format.line_spacing = 1.0
                for run in paragraph.runs:
                    run.font.name = "Arial"
                    run.font.size = Pt(8.3)
                    run.font.color.rgb = BLACK
    if widths:
        for row in table.rows:
            for idx, width in enumerate(widths):
                row.cells[idx].width = Cm(width)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


def add_code(doc: Document, text: str, label: str | None = None) -> None:
    if label:
        p = doc.add_paragraph()
        set_keep_with_next(p)
        r = p.add_run(label)
        r.bold = True
        r.font.size = Pt(9)
    for line in text.rstrip().splitlines() or [""]:
        p = doc.add_paragraph(style="Source Code")
        if not p.runs:
            p.add_run(line)
        else:
            p.runs[0].text = line
        set_cell = p._p.get_or_add_pPr()
        shd = set_cell.find(qn("w:shd"))
        if shd is None:
            shd = OxmlElement("w:shd")
            set_cell.append(shd)
        shd.set(qn("w:fill"), LIGHT_GRAY)
    doc.add_paragraph().paragraph_format.space_after = Pt(3)


def add_listing(doc: Document, title: str, relative_path: str) -> None:
    doc.add_heading(title, level=2)
    p = doc.add_paragraph(relative_path)
    p.paragraph_format.space_after = Pt(4)
    p.runs[0].italic = True
    p.runs[0].font.size = Pt(8.5)
    add_code(doc, (ROOT / relative_path).read_text(encoding="utf-8"))


def add_image(doc: Document, relative_path: str, caption: str, width_cm=16.2) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(DOCS / relative_path), width=Cm(width_cm))
    doc.add_paragraph(caption, style="Caption")


def observation(request: str, occurrence=0):
    matches = [item for item in OBSERVATIONS["observations"] if item["request"] == request]
    return matches[occurrence]


def json_text(value) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2)


def add_toc_note(doc: Document) -> None:
    doc.add_heading("Contents", level=1)
    p = doc.add_paragraph()
    p.add_run("1. Aim and project baseline\n")
    p.add_run("2. REST contract\n")
    p.add_run("3. DTO layer and mapper\n")
    p.add_run("4. REST controller\n")
    p.add_run("5. HTTP verification\n")
    p.add_run("6. Centralized error handling\n")
    p.add_run("7. OpenAPI and Swagger UI\n")
    p.add_run("8. Individual assignment - Variant 12\n")
    p.add_run("9. Automated verification\n")
    p.add_run("10. Defence questions\n")
    p.add_run("11. Conclusions\n")
    p.add_run("12. References")


def build_report() -> None:
    doc = Document()
    configure_document(doc)
    add_title_page(doc)
    add_toc_note(doc)

    doc.add_heading("1. Aim and project baseline", level=1)
    add_paragraph(
        doc,
        "Aim. To design and implement a REST API for the Book resource using explicit DTOs, "
        "correct HTTP semantics, Bean Validation, RFC 9457 Problem Details and OpenAPI documentation."
    )
    add_paragraph(
        doc,
        "Repository: https://github.com/Karz317/spring-lab-01/tree/lab07. The branch lab07 continues "
        "the completed laboratory 6 code and preserves the MVC catalogue, localization and previous tests."
    )
    add_table(doc, ["Item", "Actual value"], [
        ["Student", "Kassymzhanov Arzum"],
        ["Group", "IT1-2404IS"],
        ["Variant", "12 - RestTestClient"],
        ["Java / Spring Boot", "JDK 25.0.2 / Spring Boot 4.1.1"],
        ["OpenAPI", "springdoc-openapi-starter-webmvc-ui 3.1.1"],
        ["Storage", "In-memory ConcurrentHashMap with three initial books"],
        ["Verification", "36 automated tests, 11 live HTTP observations, 3 browser screenshots"],
    ], widths=[5.2, 11.0])
    add_paragraph(
        doc,
        "The implementation exposes only BookRequest and BookResponse at the HTTP boundary. The domain "
        "record retains internal state such as availability, while the API publishes id and createdAt as "
        "read-only response data."
    )

    doc.add_heading("2. REST contract", level=1)
    add_paragraph(doc, "The API uses resource-oriented paths and status codes that describe the outcome of each operation.")
    add_table(doc, ["Method and path", "Request body", "Success", "Error responses"], [
        ["GET /api/books", "-", "200 List<BookResponse>", "-"],
        ["GET /api/books/{id}", "-", "200 BookResponse", "404 ProblemDetail"],
        ["POST /api/books", "BookRequest", "201 BookResponse + Location", "400 validation; 409 duplicate"],
        ["PUT /api/books/{id}", "BookRequest", "200 BookResponse", "400; 404; 409"],
        ["DELETE /api/books/{id}", "-", "204, empty body", "404 ProblemDetail"],
        ["GET /api/books/search?q=...", "-", "200 List<BookResponse>", "400 method validation"],
    ], widths=[4.5, 3.1, 4.3, 4.3])
    add_bullets(doc, [
        "POST returns 201 Created and a Location header containing the URI of the created book.",
        "DELETE returns 204 No Content with no response body.",
        "A missing identifier produces 404; a duplicate title-author pair produces 409 Conflict.",
        "Validation failures and application errors use application/problem+json.",
    ])

    doc.add_heading("3. DTO layer and mapper", level=1)
    add_paragraph(
        doc,
        "BookRequest is the write contract. The client supplies title, author, year and genre, but cannot "
        "assign an identifier, creation timestamp or internal availability flag. BookResponse is the read "
        "contract and contains id and createdAt. This separation prevents mass assignment and allows the "
        "domain model or storage representation to change without silently breaking clients."
    )
    add_table(doc, ["Field", "BookRequest rule", "BookResponse"], [
        ["title", "@NotBlank; @Size(max=120)", "Returned"],
        ["author", "@NotBlank; @NoDigits", "Returned"],
        ["year", "@Min(1450); @Max(2100)", "Returned"],
        ["genre", "@NotNull", "Returned"],
        ["id", "Not accepted", "Returned"],
        ["createdAt", "Not accepted", "Returned"],
    ], widths=[3.7, 7.4, 5.2])
    add_listing(doc, "Listing 1. BookRequest record", "src/main/java/kz/iitu/springlab/web/dto/BookRequest.java")
    add_listing(doc, "Listing 2. BookResponse record", "src/main/java/kz/iitu/springlab/web/dto/BookResponse.java")
    add_listing(doc, "Listing 3. BookMapper", "src/main/java/kz/iitu/springlab/web/dto/BookMapper.java")

    doc.add_heading("4. REST controller", level=1)
    add_paragraph(
        doc,
        "BookApiController is mapped to /api/books. It delegates business operations to BookService and "
        "uses BookMapper in both directions. The controller never exposes Book directly. OpenAPI annotations "
        "describe the resource and expected responses; validation remains executable code on the DTO."
    )
    add_listing(doc, "Listing 4. BookApiController", "src/main/java/kz/iitu/springlab/web/BookApiController.java")

    doc.add_heading("5. HTTP verification", level=1)
    add_paragraph(
        doc,
        "The executable JAR was started on port 8080 and the following requests were made against the live "
        "application. Values shown below are captured in docs/lab07-observations.json."
    )
    rows = []
    for req, occurrence in [
        ("GET /api/books", 0),
        ("GET /api/books/1", 0),
        ("POST /api/books", 0),
        ("GET /api/books/4", 0),
        ("DELETE /api/books/4", 0),
        ("DELETE /api/books/4", 1),
    ]:
        item = observation(req, occurrence)
        result = str(item["status"])
        if item.get("location"):
            result += f"; Location: {item['location']}"
        if item["status"] == 204:
            result += "; empty body"
        elif isinstance(item.get("body"), dict) and item["body"].get("title"):
            result += f"; {item['body']['title']}"
        rows.append([req, item.get("contentType") or "-", result])
    add_table(doc, ["Request", "Content-Type", "Observed result"], rows, widths=[5.8, 5.2, 5.3])
    created = observation("POST /api/books")
    add_code(doc, json_text(created["body"]), "Created resource body")
    add_image(
        doc,
        "screenshots/lab07/01-post-201-location.jpg",
        "Figure 1. Live POST /api/books response: 201 Created, response DTO and Location header.",
    )

    doc.add_heading("6. Centralized error handling", level=1)
    add_paragraph(
        doc,
        "ApiExceptionHandler extends ResponseEntityExceptionHandler and is restricted to REST controllers. "
        "Known application exceptions become ProblemDetail responses; invalid request bodies are represented "
        "by a structured errors array naming each rejected property."
    )
    add_table(doc, ["Scenario", "Status / media type", "Handler result"], [
        ["Unknown id", "404 application/problem+json", "BookNotFoundException -> ProblemDetail"],
        ["Invalid BookRequest", "400 application/problem+json", "errors[].field and errors[].message"],
        ["Duplicate title and author", "409 application/problem+json", "DuplicateTitleException -> ProblemDetail"],
    ], widths=[4.8, 5.3, 6.2])
    add_paragraph(doc, "Complete 404 response body:")
    add_code(doc, json_text(observation("GET /api/books/999")["body"]))
    add_paragraph(doc, "Validation response (the rejected property is visible as errors[0].field):")
    add_code(doc, json_text(observation("POST /api/books", 1)["body"]))
    add_paragraph(doc, "Duplicate response:")
    add_code(doc, json_text(observation("POST /api/books", 2)["body"]))
    add_listing(doc, "Listing 5. BookNotFoundException", "src/main/java/kz/iitu/springlab/catalog/BookNotFoundException.java")
    add_listing(doc, "Listing 6. DuplicateTitleException", "src/main/java/kz/iitu/springlab/service/DuplicateTitleException.java")
    add_listing(doc, "Listing 7. ApiExceptionHandler", "src/main/java/kz/iitu/springlab/web/ApiExceptionHandler.java")
    add_image(
        doc,
        "screenshots/lab07/02-swagger-404-problem-detail.jpg",
        "Figure 2. Swagger UI executes GET /api/books/999 and displays the live 404 ProblemDetail.",
    )

    doc.add_heading("7. OpenAPI and Swagger UI", level=1)
    add_paragraph(
        doc,
        "The springdoc starter generates an OpenAPI 3.1 document at /v3/api-docs and an interactive page at "
        "/swagger-ui.html. The generated document contains /api/books, /api/books/{id} and "
        "/api/books/search. Bean Validation metadata is reused in the schema: title has maxLength 120, "
        "year has minimum 1450 and maximum 2100, and genre is an enum."
    )
    add_table(doc, ["Path", "Generated operations"], [
        ["/api/books", "GET, POST"],
        ["/api/books/{id}", "GET, PUT, DELETE"],
        ["/api/books/search", "GET"],
    ], widths=[7.0, 9.3])
    add_code(doc, """<dependency>
  <groupId>org.springdoc</groupId>
  <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
  <version>3.1.1</version>
</dependency>""", "OpenAPI dependency")
    add_image(
        doc,
        "screenshots/lab07/03-openapi-bookrequest-schema.jpg",
        "Figure 3. Generated BookRequest schema in Swagger UI, including validation limits.",
    )

    doc.add_heading("8. Individual assignment - Variant 12", level=1)
    add_paragraph(
        doc,
        "Variant 12 requires three tests with Spring RestTestClient. The client is bound to the real "
        "WebApplicationContext, so Spring MVC request mapping, validation, exception advice, message "
        "conversion and response headers are exercised without starting an external server."
    )
    add_table(doc, ["Test", "Required assertion", "Result"], [
        ["createReturns201AndLocation", "201, Location exists, created DTO can be read", "Passed"],
        ["missingBookReturns404ProblemDetail", "404, application/problem+json, standard fields", "Passed"],
        ["deleteReturns204AndNoBody", "204 and empty response body", "Passed"],
    ], widths=[6.0, 7.6, 2.7])
    add_listing(doc, "Listing 8. RestTestClient tests", "src/test/java/kz/iitu/springlab/BookApiRestTestClientTests.java")

    doc.add_heading("9. Automated verification", level=1)
    add_paragraph(
        doc,
        "The complete project was verified with .\\mvnw.cmd -q clean verify. Maven finished successfully "
        "and produced the executable JAR. Test reports contain no failures, errors or skipped tests."
    )
    add_table(doc, ["Test suite", "Tests", "Failures", "Errors", "Skipped"], [
        ["BookApiRestTestClientTests", "3", "0", "0", "0"],
        ["BookWorkflowTests", "26", "0", "0", "0"],
        ["NoDigitsValidatorTests", "6", "0", "0", "0"],
        ["SpringLab01ApplicationTests", "1", "0", "0", "0"],
        ["Total", "36", "0", "0", "0"],
    ], widths=[7.0, 2.3, 2.3, 2.3, 2.3])
    add_code(doc, ".\\mvnw.cmd clean verify\njava -jar .\\target\\spring-lab-01-0.0.1-SNAPSHOT.jar", "Reproduction commands (PowerShell)")
    add_paragraph(
        doc,
        "The live verification additionally confirmed 200 list and item responses, 201 creation and "
        "follow-up GET, 204 deletion, 404 after repeated deletion, 400 body validation, 409 duplicate "
        "detection, 400 search-parameter validation and the generated OpenAPI schema."
    )

    doc.add_heading("10. Defence questions", level=1)
    qa = [
        ("Why not accept Book directly?", "It would expose server-owned fields such as id, createdAt and internal state to mass assignment and couple clients to the domain model."),
        ("What changes if storage changes?", "The DTO contract can remain stable while the domain object, database entity or mapper changes internally."),
        ("Why does POST return 201 and Location?", "201 states that a resource was created; Location tells the client where the new resource can be retrieved."),
        ("Why does DELETE return 204?", "A successful delete has no representation to return, so an empty body is explicit and efficient."),
        ("What is ProblemDetail?", "It is Spring's representation of the RFC 9457 problem-details format with type, title, status, detail and instance fields."),
        ("Why use 409 for duplicates?", "The request is syntactically valid but conflicts with the current catalogue state."),
        ("Where does maxLength 120 in OpenAPI come from?", "springdoc reads the @Size(max=120) Bean Validation annotation on BookRequest.title."),
        ("Why use ResponseEntity for create and delete?", "Those operations must control the status and headers explicitly: Location for 201 and an empty 204 response."),
        ("Does Swagger UI replace tests?", "No. It is an interactive client and contract explorer; automated tests remain repeatable regression checks."),
        ("What does RestTestClient verify here?", "It exercises the full MVC layer through the application context, including serialization, validation, advice and headers."),
    ]
    for question, answer in qa:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.add_run(question + " ").bold = True
        p.add_run(answer)

    doc.add_heading("11. Conclusions", level=1)
    add_paragraph(
        doc,
        "The implemented API provides complete CRUD operations for books with stable request and response "
        "contracts. DTOs add mapping code, but they prevent clients from controlling server-owned fields and "
        "keep persistence changes away from the public API. Correct status codes, Location headers and "
        "ProblemDetail responses make success and failure semantics unambiguous. OpenAPI generation and the "
        "RestTestClient suite give both interactive documentation and repeatable evidence that the contract is implemented."
    )

    doc.add_heading("12. References", level=1)
    refs = [
        "Laboratory_work_7_EN.docx - primary assignment and report requirements.",
        "Presentation_Lecture_7_EN.pptx - lecture material on REST semantics, DTOs, errors and OpenAPI.",
        "Project source code: https://github.com/Karz317/spring-lab-01/tree/lab07",
        "OpenAPI document generated by the application: http://localhost:8080/v3/api-docs",
        "Swagger UI generated by the application: http://localhost:8080/swagger-ui.html",
    ]
    for ref in refs:
        doc.add_paragraph(ref, style="List Number")

    doc.core_properties.title = "Laboratory Work 7 - REST API Design"
    doc.core_properties.subject = "Spring REST API, DTOs, Problem Details and OpenAPI"
    doc.core_properties.author = "Kassymzhanov Arzum"
    doc.core_properties.keywords = "Spring Boot, REST, DTO, ProblemDetail, OpenAPI, RestTestClient"
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build_report()
