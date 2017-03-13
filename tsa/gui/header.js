$('#load-btn').on('click', function() {
	$('#file-input').trigger('click');
});

var handleLoad = function(files) {
	f = files[0]
	/*d3.select('#load-btn')
		.attr('href', '/load/' + f.name);*/
	$('#load-frm-btn').trigger('click');
}

var insertHeader = function(title) {
	var hr = d3.select('.header-row');

	hr.append('div')
		.attr('class', 'col-md-2 col-sm-12 col-xs-12 col-tall')
		.append('div')
		.attr('class', 'jumbotron col-tall')
		.attr('id', 'jumbo-header')
		.append('p')
		.attr('id', 'jumbo-p')
		.text(title);

	var btnrow = hr.append('div')
		.attr('class', 'col-md-10 col-sm-12 col-xs-12 col-tall')
		.append('div')
		.attr('class', 'btn-group btn-group-justified nav-btn-group');

	btnrow.append('a')
		.attr('href', '/index.html')
		.attr('class', 'btn btn-muted nav-btn')
		.text('Home')
	btnrow.append('a')
		.attr('href', '/inspect.html')
		.attr('class', 'btn btn-muted nav-btn')
		.text('Inspect')
	btnrow.append('a')
		.attr('href', '#')
		.attr('class', 'btn btn-muted nav-btn')
		.text('Load')
	btnrow.append('a')
		.attr('href', '/summary.html')
		.attr('class', 'btn btn-muted nav-btn')
		.text('Summary')

}

var insertSvg = function(parentIdx, svgIdx) {
	var svg = d3.select('#' + parentIdx).append('svg')
		.attr('width', '100%')
		.attr('height', '100%')
		.attr('id', svgIdx);
	return svg;
}

var createGrid = function(parentIdx, numRows, numCols) {
	rowHeight = 100 / numRows;
	colWidth = Math.floor(12 / numCols);
	parent = d3.select('#'+parentIdx);
	for (var r = 0; r < numRows; r++) {
		var curRow = parent.append('div')
			.attr('class', 'row')
			.attr('id', 'row-'+r)
			.style('height', rowHeight + '%');
		for (var c = 0; c < numCols; c++) {
			var curCol = curRow.append('div')
				.attr('class', 'col-md-'+colWidth+' col-sm-12 col-xs-12 col-tall')
				.attr('id', 'col-'+ (c + r*numCols));
		}
	}
}
