from loader import Loader
import openpyxl as pyxl
import matplotlib
import os.path
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

class Grapher():

	def __init__(self):
		self.loader = Loader()		
		# dictionary of data sets
		self.sets = self.loader.getSets()
		# create a list with all the data sets (that are not blank)
		self.all_sets = []
		for key in self.sets:
			if key != 'blank':
				self.all_sets.append(self.sets[key])

		self.graph_width_param = 4
		self.graph_sub_width_param = 0.5
		self.marker_size = 40
		self.folder_name = 'static/images'
		self.folder_static_name = 'images'

	def findFile(self,file_name):
		#return os.path.isfile(file_name)
		return False
	def expectFileName(self,gene_name,data_set,graph_type,file_type = 'png'):
		file_name = '_'.join([gene_name,data_set.split('_')[0],graph_type])
		file_name = '.'.join([file_name,file_type])
		file_dir = '/'.join([self.folder_name,file_name])
		return file_dir

	def decodeGeneName(self,expected_file):
		file_name = expected_file.split('/')[2]
		gene_name = file_name.split('_')[0]
		print gene_name
		return gene_name

	def decodeDataSet(self,expected_file):
		file_name = expected_file.split('/')[2]
		data_set = file_name.split('_')[1]
		print data_set
		return data_set

	def bar_plot(self,gene_name,cell_name):
		exp_data = self.loader.loadCellSpecific(gene_name,cell_name)
		return exp_data

	# create a scatter of one gene for all cell types, do it for each data set. make distinction between female and male points.
	def scatter_plot(self,gene_names):
		# some condition, all sets or one set.
		# if one set make it a single item in a list.
		expected_files = []
		fig_names = []
		data_sets = self.all_sets


		for gene_name in gene_names:
			# check if gene_name exist as a key, if not, return nothing.
			if self.loader.findRowMatch(gene_name) == -1:
				return -1
			#	return 'error gene not found'
			#else:
			for data_set in data_sets:
				expected_files.append(self.expectFileName(gene_name,data_set,'scatter'))
		
		data_sets_to_load = []
		genes_names_to_load = gene_names

		for expected_file in expected_files:
			if self.findFile(expected_file):
				fig_names.append(expected_file)
			else:
				# gene_name = self.decodeGeneName(expected_file) uneeded for scatter plot
				# translate because code is messy
				data_set = self.decodeDataSet(expected_file)
				if data_set == 'Female':
					data_set = 'GenderExp'
				elif data_set == 'ImmGen':
					data_set = 'Immgen' 
				data_sets_to_load.append(self.sets[data_set])
		sets_dict = self.loader.loadGenes(genes_names_to_load,data_sets_to_load)
		fig, ax = plt.subplots()
		ax.spines['top'].set_color('none')
		ax.spines['right'].set_color('none')
		ax.xaxis.set_ticks_position('bottom')
		ax.yaxis.set_ticks_position('left')
		counter = 0

		some_data = []
		for data_set in sets_dict:
			counter += 1
			# add  counnter data sets

			for gene_name in gene_names:
				ax.set_ylabel('Expression level log2')
		
				# create a scatter graph for this set.
				data = sets_dict[data_set]
				head = data['head'][5:]
				gene_data = data[gene_name][5:]
				# splice the data for male and female.
				
				# create the labels of x axis
				xlabels = []
				for label in head:
					current = label.split('_')[0]
					if current not in xlabels:
						xlabels.append(current)
					else:
						xlabels.append('')

				x_index = []
				for label in xlabels:
					if 0 in x_index:
						if label == '':
							x_index.append(x_index[-1]+self.graph_sub_width_param)
						else:
							x_index.append(x_index[-1]+self.graph_width_param)
					else:
						x_index.append(0)

				#print x_index

				plt.xticks(x_index,xlabels,rotation=0)


				female_data = gene_data[::2]
				male_data = gene_data[1::2]
				# redo x indexing.
				x_female = []
				x_male = []
				
				current_indexed = []
				size=0
				# do shenanigans and rearrange some numbers for better apearance			
				for ind, label in enumerate(xlabels):
					if label != '':
						size = len(current_indexed)
						if size != 0:
							for i in current_indexed[:size/2]:
								x_female.append(i)
							for i in current_indexed[size/2:]:
								x_male.append(i)
						current_indexed = []
					current_indexed.append(x_index[ind])
				for i in current_indexed[:size/2]:
					x_female.append(i)
				for i in current_indexed[size/2:]:
					x_male.append(i)

				female_scatter = ax.scatter(x_female,female_data,s=self.marker_size,c = 'red',marker='^')
				male_scatter = ax.scatter(x_male,male_data,	s=self.marker_size,c = 'blue',marker='o')
				ax.legend((female_scatter,male_scatter),('female','male'),scatterpoints=1,loc='best')
				graph_title = ' '.join([gene_name,'expression level',str(counter)])
				ax.set_title(graph_title)  
				x_labels = xlabels
				data_dic = {}
				data_dic['x_index'] = x_index
				data_dic['x_labels'] = x_labels
				data_dic['title'] = graph_title
				data_dic['x_female'] = x_female
				data_dic['female_data'] = female_data
				data_dic['x_male'] = x_male
				data_dic['male_data'] = male_data


				some_data.append(data_dic)

				savename = '_'.join([gene_name,data_set.split('_')[0],'scatter'])
				filedir = '/'.join([self.folder_static_name,savename])
				savedir = '/'.join([self.folder_name,savename])
				savedir = ''.join([savedir,'.png'])
				plt.savefig(savedir)
				ax.cla()
				filedir = ''.join([filedir,'.png'])
				fig_names.append(filedir)
		plt.close(fig)
		best_data = [fig_names,some_data]
		return best_data




if __name__ == '__main__':
	# just a test to see if it works
	grapher = Grapher()
	grapher.scatter_plot(['FIRRE' ])
	#grapher.scatter_plot('FIRRE')

	#print grapher.loader.loadGenes(['FIRRE'],['Female_Male_exp_levels_norm.xlsx'])
