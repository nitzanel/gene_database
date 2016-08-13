import grapher
import forms
import flask, flask.views
import os
import functools
import flask_sijax
import pygal
from pygal.style import LightenStyle
import styles


grapher = grapher.Grapher()

bad_names = ['',' ']

def get_static_url(filedir):
	file = ''
	print filedir
	if filedir.startswith('static'):
		file = filedir.split('static/')[1]
	else:
		file = filedir
	return flask.url_for('static',filename=file)

def get_x_labels(x_index,x_labels):
	labels_list = []
	for x,label in zip(x_index,x_labels):
		labels_list.append({'label': label,'value': x})
	x_labels_tuple = tuple(labels_list)
	return x_labels_tuple


# arrange bars on the x axis
def get_bars_values(data):
	arranged_data = {}

	x_labels = []
	bar_width = 0.5
	x_loc = 0
	for key in data:
		female_count = 0
		male_count = 0
		arranged_data[key] = []
		current_serie = data[key]
		for val in current_serie:
			x_label_name = ''
			if key.startswith('m'):
				x_label_name = '_'.join([key,str(male_count)])
				male_count += 1
			else:
				x_label_name = '_'.join([key,str(female_count)])
				female_count +=1
				
			x_labels.append({'label': x_label_name,'value':x_loc})
			yx1x2 = (val,x_loc,x_loc+bar_width)
			bar_properties = {'value': yx1x2}
			arranged_data[key].append(bar_properties)
			x_loc += 1


	values = {'data':arranged_data,'x_labels': x_labels}
	return values


def get_bar_label(key,vals):
	pass

def arrange_data(data):
	if data == -1:
		return -1

	arranged_data = {}
	for key in data:
		#get female data
		name = ''.join(['female ',key])
		arranged_data[name] = data[key][::2]
		name = ''.join(['male ',key])
		arranged_data[name] = data[key][1::2]

	return arranged_data

def get_dots_labels(values):
	labels = []
	for xy in values:
		labels.append({'label':'test','tooltip':'tooltip','value':xy})
	return tuple(labels)

class Main(flask.views.MethodView):
	def get(self):
		return flask.render_template('home.html')
	def post(self):
		def say_hi(obj_response):
			obj_response.alert('Hello')
		# test sijax
		if flask.g.sijax.is_sijax_request:
			flask.g.sijax.register_callback('say_hi',say_hi)
			print 'sijax request'
			return flask.g.sijax.process_request()
		return flask.render_template('home.html')

class About(flask.views.MethodView):
	def get(self):
		return flask.render_template('about.html')

class Genes(flask.views.MethodView):
	def get(self):
		return flask.render_template('genes.html')

class Login(flask.views.MethodView):
	def get(self):
		form = forms.LoginForm()
		return flask.render_template('login.html',title='Sign In',form=form)
	def post(self):
		return flask.redirect(flask.url_for('home'))


class Cell_Type_Specific(flask.views.MethodView):
	def get(self):
		form = forms.CellTypeSpecificForm()
		return flask.render_template('cell_type_specific.html',form=form)

	def post(self):
		form = forms.CellTypeSpecificForm()
		gene_name = flask.request.form['gene_name']
		gene_name = gene_name.upper()

		cell_type = flask.request.form['cell_type']

		if gene_name in bad_names or gene_name.startswith(' '):
			print 'please enter a valid gene symbol.'
		#create the graph
		data = arrange_data(grapher.bar_plot(gene_name,cell_type))
		

		
		if data == -1:
			flask.flash('Gene not found.')
			return flask.render_template('cell_type_specific.html',form=form)
		data = get_bars_values(data)
		x_labels = data['x_labels']
		data = data['data']
		dark_lighten_style = LightenStyle('#CC2233')


		graph = pygal.Histogram(truncate_label=-1)

		graph.title = ''.join([gene_name,' expression level in ',cell_type])
		graph.y_title = 'Expression level log2'
		for key in data:
			graph.add(str(key),data[key])
		graph.x_labels = x_labels
		graph_data = graph.render_data_uri()

		graph = pygal.Histogram()
		graph.title = 'test'
		graph.add('test',[{'value': (3,1,2)},{'value':(3,2,3)}])
		graph.add('test2',[{'value':(3,3,4)}])
		second = graph.render_data_uri()

		return flask.render_template('cell_type_specific.html',form=form,data=data,graph_data=graph_data)

class Pan_Immune(flask.views.MethodView):
	def get(self):
		form = forms.GeneSearchForm()
		return flask.render_template('pan_immune.html',form=form)
	def post(self):
		form = forms.GeneSearchForm()
		gene_name = flask.request.form['gene_name']
		#data_set = flask.request.form['data_sets']
		gene_name = gene_name.upper()
		if gene_name in bad_names or gene_name.startswith(' '):
			flask.flash('Please enter a gene name.')
			return flask.render_template('pan_immune.html',form=form)
		filedirs = grapher.scatter_plot([gene_name])
		
		if filedirs == -1:
			flask.flash('Gene not found.')
		#	flask.flash_message(filedirs)
			return flask.render_template('pan_immune.html',form=form)


		some_data = filedirs[1]
		filedirs = filedirs[0]


		graphs_data = []
		for dic in some_data:
			# create a graph for each dict of data
			graph = pygal.XY(stroke=False,show_y_guides=False,truncate_label=-1, dots_size=5)
			graph.title = dic['title']
			graph.y_title = 'Expression level log2'
			x_labels = get_x_labels(dic['x_index'],dic['x_labels'])
			female_xy =get_dots_labels(zip(dic['x_female'],dic['female_data']))
			male_xy = zip(dic['x_male'],dic['male_data'])
			graph.add('Female',female_xy)
			graph.add('Male',male_xy)
			graph.x_labels = x_labels
			#graph.x_labels = 'a','c','sd'
			graphs_data.append(graph.render_data_uri())
		
		files_list = []
		#if data_set == 'All':
		for filedir in filedirs:
			file = get_static_url(filedir)
			files_list.append(file)
		#else:
		#	for filedir in filedirs:
		#		if filedir.split('_')[1] == data_set:
		#			file = get_static_url(filedir)
		#			files_list.append(file)
					#flask.flash(filedir) was once legacy hack.
		return flask.render_template('pan_immune.html',images = files_list,form=form,super_graphs=graphs_data)
