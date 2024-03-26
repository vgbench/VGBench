import xlsxwriter
import json
import PIL.Image
import os
from io import BytesIO

def main():
    q_type = "relation"
    workbook = xlsxwriter.Workbook("tikz_qa_%s.xlsx"%q_type)
    worksheet = workbook.add_worksheet()
    worksheet.write("A1", "Index")
    worksheet.write("B1", "Image")
    worksheet.write("C1", "Question")
    worksheet.write("D1", "Options")
    worksheet.write("E1", "Correct Answer")

    cell_width = 256
    cell_height = 256

    worksheet.set_column_pixels('B:B', width=cell_width)

    with open("questions_%s.json"%q_type, "r") as f:
        questions = json.load(f)

    for i, question in enumerate(questions):
        row_id = i+2
        worksheet.set_row_pixels(i+1, height=cell_height)
        img = PIL.Image.open(os.path.join("pngs","%d.png"%question['idx']))

        buffered = BytesIO()
        img.save(buffered, format="PNG")

        
        worksheet.write("A%d" % row_id, str(question['idx']))
        scale_rate = min(
            cell_width/img.width, cell_height/img.height)
        worksheet.insert_image("B%d" % row_id, "%d.png", {"image_data": buffered,
                                                          'x_scale': scale_rate,
                                                          'y_scale': scale_rate})
        worksheet.write("C%d" % row_id, question['q'])
        worksheet.write("D%d" % row_id, "\n".join(question['o']))
        worksheet.write("E%d" % row_id, question['a'])

        print(i)

    workbook.close()
    
    # response = process_sample(dataset[11])

    # print(response)


if __name__ == '__main__':
    main()
