import xlsxwriter
import json
import PIL.Image
import os
from io import BytesIO
import argparse


def default_argument_parser():
    parser = argparse.ArgumentParser(description="convert json to spreadsheet")
    parser.add_argument(
        "--q-type", default="", required=True, help="the type of questions")
    parser.add_argument(
        "--format", choices=["tikz", "graphviz"], default="", required=True, help="the format of the vector graphics")

    return parser


def main():
    args = default_argument_parser().parse_args()
    q_type = args.q_type
    v_format = args.format
    start = 0
    end = 550
    workbook = xlsxwriter.Workbook(
        "./data/%s/%s_qa_%s_%d_%d.xlsx" % (v_format, v_format, q_type, start, end))
    worksheet = workbook.add_worksheet()
    worksheet.write("A1", "QuestionIndex")
    worksheet.write("B1", "ImgIndex")
    worksheet.write("C1", "Image")
    worksheet.write("D1", "Question")
    worksheet.write("E1", "Options")
    worksheet.write("F1", "Correct Answer")

    cell_width = 256
    cell_height = 256

    worksheet.set_column_pixels('C:C', width=cell_width)

    with open("./data/%s/questions_%s.json" % (v_format, q_type), "r") as f:
        questions = json.load(f)

    n_question = len(questions)
    for i, qid in enumerate(range(start, end)):
        question = questions[qid]
        row_id = i+2
        worksheet.set_row_pixels(i+1, height=cell_height)
        img = PIL.Image.open(os.path.join("pngs/%s" %
                             v_format, "%d.png" % question['idx']))

        buffered = BytesIO()
        img.save(buffered, format="PNG")

        worksheet.write("A%d" % row_id, str(qid))
        worksheet.write("B%d" % row_id, str(question['idx']))
        scale_rate = min(
            cell_width/img.width, cell_height/img.height)
        worksheet.insert_image("C%d" % row_id, "%d.png", {"image_data": buffered,
                                                          'x_scale': scale_rate,
                                                          'y_scale': scale_rate})
        worksheet.write("D%d" % row_id, question['q'])
        worksheet.write("E%d" % row_id, "\n".join(question['o']))
        worksheet.write("F%d" % row_id, question['a'])

        print(i)

    workbook.close()

    # response = process_sample(dataset[11])

    # print(response)


if __name__ == '__main__':
    main()
