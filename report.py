import csv
from datetime import datetime
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf():

    styles = getSampleStyleSheet()

    pdf = SimpleDocTemplate("Animal_Report.pdf")

    elements = []

    # ---------------- Title ----------------

    title = Paragraph("<b><font size=20>Animal Detection Report</font></b>", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 20))

    # ---------------- Date ----------------

    date = Paragraph(
        f"<b>Generated On :</b> {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
        styles["Normal"]
    )

    elements.append(date)
    elements.append(Spacer(1, 20))

    # ---------------- Read CSV ----------------

    with open("results.csv", newline="") as file:

        reader = csv.reader(file)

        rows = list(reader)

    # ---------------- Statistics ----------------

    total_animals = len(rows) - 1

    unique_animals = len(set(
        row[1]
        for row in rows[1:]
        if row[1] != "None"
    ))

    confidence_sum = 0

    confidence_count = 0

    animal_count = {}

    for row in rows[1:]:

        if row[1] == "None":
            continue

        confidence = float(row[2].replace("%", ""))

        confidence_sum += confidence

        confidence_count += 1

        if row[1] in animal_count:

            animal_count[row[1]] += 1

        else:

            animal_count[row[1]] = 1

    average_confidence = 0

    if confidence_count > 0:

        average_confidence = confidence_sum / confidence_count

    # ---------------- Summary ----------------

    elements.append(
        Paragraph("<b>PROJECT SUMMARY</b>", styles["Heading2"])
    )

    summary_data = [

        ["Images Processed", str(total_animals)],

        ["Animals Detected", str(total_animals)],

        ["Unique Animals", str(unique_animals)],

        ["Average Confidence", f"{average_confidence:.2f}%"]

    ]

    summary_table = Table(summary_data)

    summary_table.setStyle(TableStyle([

        ('GRID', (0,0), (-1,-1), 1, colors.black),

        ('BACKGROUND', (0,0), (0,-1), colors.lightblue),

        ('ALIGN', (0,0), (-1,-1), 'CENTER'),

        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold')

    ]))

    elements.append(summary_table)

    elements.append(Spacer(1,20))

    # ---------------- Animal Count ----------------

    elements.append(
        Paragraph("<b>ANIMAL COUNT</b>", styles["Heading2"])
    )

    count_data = [["Animal", "Count"]]

    for animal, count in animal_count.items():

        count_data.append([animal, str(count)])

    count_table = Table(count_data)

    count_table.setStyle(TableStyle([

        ('GRID',(0,0),(-1,-1),1,colors.black),

        ('BACKGROUND',(0,0),(-1,0),colors.green),

        ('TEXTCOLOR',(0,0),(-1,0),colors.white),

        ('ALIGN',(0,0),(-1,-1),'CENTER')

    ]))

    elements.append(count_table)

    elements.append(Spacer(1,20))

    # ---------------- Detection Table ----------------

    elements.append(
        Paragraph("<b>DETECTION RESULTS</b>", styles["Heading2"])
    )

    detection_table = Table(rows)

    detection_table.setStyle(TableStyle([

        ('GRID',(0,0),(-1,-1),1,colors.black),

        ('BACKGROUND',(0,0),(-1,0),colors.darkblue),

        ('TEXTCOLOR',(0,0),(-1,0),colors.white),

        ('ALIGN',(0,0),(-1,-1),'CENTER'),

        ('BACKGROUND',(0,1),(-1,-1),colors.beige)

    ]))

    elements.append(detection_table)

    pdf.build(elements)