import openpyxl
for i in range(1,20):
    wb = openpyxl.Workbook()
    wb.save(f'测试数据源/DW_MX_021ABV_0213XXXXXX-202507_20250701_20250731_{i}.xlsx')


