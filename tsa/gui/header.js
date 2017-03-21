
var insertHeader = function(title) {
	var hr = d3.select('.header-row');

	var btnrow = hr.append('div')
		.attr('class', 'col-md-12 col-sm-12 col-xs-12 col-tall nav-col')
		.append('div')
		.attr('class', 'btn-group btn-group-justified nav-btn-group')
		.attr('id', 'btn-row');


	btnrow.append('a')
		.attr('href', '/summary.html')
		.attr('class', 'btn btn-muted nav-btn top-nav-btn')
		.attr('id', 'nav-btn-summary')
		.text('Summary')
	btnrow.append('a')
		.attr('href', '/inspect.html')
		.attr('class', 'btn btn-muted nav-btn top-nav-btn')
		.attr('id', 'nav-btn-inspect')
		.text('Inspect')
	btnrow.append('a')
		.attr('href', '/prevalence.html')
		.attr('class', 'btn btn-muted nav-btn top-nav-btn')
		.attr('id', 'nav-btn-prevalence')
		.text('Heatmap')
	btnrow.append('a')
		.attr('href', '/mosaic.html')
		.attr('class', 'btn btn-muted nav-btn top-nav-btn')
		.attr('id', 'nav-btn-mosaic')
		.text('Mosaic')

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
