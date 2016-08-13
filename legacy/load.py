import openpyxl as pyxl

data = {}


# data bases
GenderExp_book = 'Female_Male_exp_levels_norm.xlsx'
Immgen_book = 'ImmGen_sex_exp_levels_norm.xlsx'


wb = pyxl.load_workbook(filename=Immgen_book,read_only=True)
sheet = wb.worksheets[0]

for j, row in enumerate(sheet.get_squared_range(min_col=2,max_col=2,min_row=2,max_row=sheet.max_row/4)):
	for cell in row:
		data[cell.value] = j + 2

#print data['FIRRE']

# IT WORKS!