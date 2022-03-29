from datetime import datetime

import xlsxwriter as xw


def results_to_excel(data, offset, offset_increment, method):
    file, page = __build_file(method)

    __build_table_header(file, page, 0, method)

    __build_table_body(page, data, 0, offset, offset_increment)

    __build_graphics(file, page)

    file.close()


def __build_file(method):
    now = datetime.now()
    day = now.strftime("%d-%m-%Y")
    time = now.strftime("%Hh%Mm%Ss")

    file = xw.Workbook(f'{method}_{day}_{time}.xlsx')
    page = file.add_worksheet('Results')
    return file, page


def __build_table_header(file, page, row, method):
    page.write(row, 0, "Method")
    page.write(row, 1, "Threshold")
    page.write(row, 2, "TP")
    page.write(row, 3, "TN")
    page.write(row, 4, "FP")
    page.write(row, 5, "FN")
    page.write(row, 6, "Sensitivity")
    page.write(row, 7, "Specificity")
    page.write(row, 8, "FP Rate")
    page.write(row, 9, "FN Rate")
    page.write(row, 10, "Youden Index")
    page.write(row, 11, "Accuracy")

    merge_format = file.add_format({'align': 'center', 'valign': 'vcenter'})
    page.merge_range('A2:A22', method, merge_format)


def __build_table_body(page, data, row, offset, offset_increment):
    split_size = 4
    data = [data[x:x + split_size] for x in range(0, len(data), split_size)]
    for value in data:
        row += 1

        page.write(row, 1, offset)
        page.write(row, 2, value[0])
        page.write(row, 3, value[1])
        page.write(row, 4, value[2])
        page.write(row, 5, value[3])
        page.write(row, 6, f"=C{row + 1}/(C{row + 1}+F{row + 1})")
        page.write(row, 7, f"=D{row + 1}/(D{row + 1}+E{row + 1})")
        page.write(row, 8, f"=E{row + 1}/(E{row + 1}+D{row + 1})")
        page.write(row, 9, f"=F{row + 1}/(F{row + 1}+C{row + 1})")
        page.write(row, 10, f"=G{row + 1}+H{row + 1}-1")
        page.write(row, 11, f"=(C{row + 1}+D{row + 1})/(C{row + 1}+D{row + 1}+E{row + 1}+F{row + 1})")

        offset += offset_increment


def __build_graphics(file, page):
    chart = file.add_chart({'type': 'line'})

    chart.add_series({'name': '=Results!$C$1', 'values': '=Results!$C$2:$C$22', 'marker': {'type': 'circle'},
                      'categories': '=Results!$B$2:$B$22'})
    chart.add_series({'name': '=Results!$D$1', 'values': '=Results!$D$2:$D$22', 'marker': {'type': 'circle'}})
    chart.add_series({'name': '=Results!$E$1', 'values': '=Results!$E$2:$E$22', 'marker': {'type': 'circle'}})
    chart.add_series({'name': '=Results!$F$1', 'values': '=Results!$F$2:$F$22', 'marker': {'type': 'circle'}})

    chart.set_x_axis({'name': '=Results!$B$1'})

    page.insert_chart('N2', chart)

    chart = file.add_chart({'type': 'line'})

    chart.add_series({'name': '=Results!$G$1', 'values': '=Results!$G$2:$G$22', 'marker': {'type': 'circle'},
                      'categories': '=Results!$B$2:$B$22'})
    chart.add_series({'name': '=Results!$H$1', 'values': '=Results!$H$2:$H$22', 'marker': {'type': 'circle'}})

    chart.set_x_axis({'name': '=Results!$B$1'})

    page.insert_chart('N17', chart)
