var tblRowMouseover = function(data) {
	var row = d3.select(this);
	row.selectAll('.tbl-col-0')
		.style('background', 'grey')
	row.selectAll('.tbl-col-1')
		.style('background', 'grey')
	row.selectAll('.tbl-col-2')
		.style('background', 'grey')
}

var tblRowMouseout = function(data) {
	var row = d3.select(this);
	row.selectAll('.tbl-col-0')
		.style('background', 'transparent')
	row.selectAll('.tbl-col-1')
		.style('background', 'transparent')
	row.selectAll('.tbl-col-2')
		.style('background', 'transparent')
}

var tblRowClick = function(data) {
	console.log(data);
	var svg = d3.select('#mosaic-svg');
	clearSvg(svg);
	drawRand(svg);
}

var populateTable = function() {
	var tblCol = d3.select('#table-col');
	
	d3.json('/mosaic', function(data) {
		var headerRow = d3.select('#table-header-row')
		headerRow.append('div')
			.attr('class', 'col-md-4 col-sm-4 col-xs-4 col-tall tbl-col-0')
			//.style('border-right', '1px solid black')
			//.style('border-left', '1px solid black')
			.append('p')
			.text('Interactome 1')
			.attr('align', 'center')
			.style('margin-top', '5%')
			.style('margin-bottom', '5%')
			.style('font-weight', 'bold');
		headerRow.append('div')
			.attr('class', 'col-md-4 col-sm-4 col-xs-4 col-tall tbl-col-1')
			//.style('border-right', '1px solid black')
			//.style('border-left', '1px solid black')
			.append('p')
			.text('Interactome 2')
			.attr('align', 'center')
			.style('margin-top', '5%')
			.style('margin-bottom', '5%')
			.style('font-weight', 'bold');
		headerRow.append('div')
			.attr('class', 'col-md-4 col-sm-4 col-xs-4 col-tall tbl-col-2')
			//.style('border-right', '1px solid black')
			//.style('border-left', '1px solid black')
			.append('p')
			.text('P Value')
			.attr('align', 'center')
			.style('margin-top', '5%')
			.style('margin-bottom', '5%')
			.style('font-weight', 'bold');

		var rows = tblCol.selectAll('.tbl-row')
			.data(data)
			.enter()
			.append('div')
			.attr('class', 'row tbl-row')
			.attr('height', '10%')
			.on('mouseover', tblRowMouseover)
			.on('mouseout', tblRowMouseout)
			.on('click', tblRowClick)

		var col0 = rows.append('div')
			.attr('class', 'col-md-4 col-sm-4 col-xs-4 col-tall tbl-col-0')
			.style('border-right', '1px solid black')
			.style('border-left', '1px solid black')
			.style('pointer-events', 'none')
			.append('pre')
			.text(d => d.interactome1)
			.attr('align', 'center')
			.style('pointer-events', 'none')
			.style('margin-top', '5%')
			.style('margin-bottom', '5%')
		var col1 = rows.append('div')
			.attr('class', 'col-md-4 col-sm-4 col-xs-4 col-tall tbl-col-1')
			.style('border-right', '1px solid black')
			.style('border-left', '1px solid black')
			.style('pointer-events', 'none')
			.append('pre')
			.text(d => d.interactome2)
			.attr('align', 'center')
			.style('pointer-events', 'none')
			.style('margin-top', '5%')
			.style('margin-bottom', '5%')
		var col2 = rows.append('div')
			.attr('class', 'col-md-4 col-sm-4 col-xs-4 col-tall tbl-col-2')
			.style('border-right', '1px solid black')
			.style('border-left', '1px solid black')
			.style('pointer-events', 'none')
			.append('pre')
			.text(d => d.pVal)
			.attr('align', 'center')
			.style('pointer-events', 'none')
			.style('margin-top', '5%')
			.style('margin-bottom', '5%')
	})
}

var svgWidth = function(svg) {
	var svgid = svg.attr('id');
	return $('#' + svgid).width()
}
var svgHeight = function(svg) {
	var svgid = svg.attr('id');
	return $('#' + svgid).height()
}

var genRandMosaic = function() {
	var w0 = Math.random();
	var h1 = Math.random();
	var h2 = Math.random();
	return [[[w0, h1, 0], [1-w0, h2, 0]], [[w0, 1-h1, 0], [1-w0, 1-h2, 0]]]
}

var drawMosaic = function(svg, mosaicData, colors) {
	if (!colors) {
		colors = d3.schemeCategory10.slice(0,4);
	}
	var side = Math.min(svgHeight(svg), svgWidth(svg));
	var xPad = (svgWidth(svg) - side) / 2;
	var yPad = (svgHeight(svg) - side) / 2;
	
	var m00 = mosaicData[0][0]
	var r00 = svg.append('rect')
		.attr('x', xPad + 5)
		.attr('y', yPad + 5)
		.attr('width', m00[0] * side - 6)
		.attr('height', m00[1] * side - 6)
		.attr('fill', colors[0])
		.style('outline', '1px solid black')

	var m01 = mosaicData[0][1]
	var r01 = svg.append('rect')
		.attr('x', xPad + m00[0] * side + 5)
		.attr('y', yPad + 5)
		.attr('width', m01[0] * side - 6)
		.attr('height', m01[1] * side - 6)
		.attr('fill', colors[1])
		.style('outline', '1px solid black')

	var m10 = mosaicData[1][0];
	var r10 = svg.append('rect')
		.attr('x', xPad + 5)
		.attr('y', yPad + m00[1]*side + 5)
		.attr('width', m10[0] * side - 6)
		.attr('height', m10[1] * side - 6)
		.attr('fill', colors[2])
		.style('outline', '1px solid black')

	var m11 = mosaicData[1][1];
	var r11 = svg.append('rect')
		.attr('x', xPad + m10[0]*side + 5)
		.attr('y', yPad + m01[1]*side + 5)
		.attr('width', m11[0] * side - 6)
		.attr('height', m11[1] * side - 6)
		.attr('fill', colors[3])
		.style('outline', '1px solid black')
}

var drawRand = function(svg) {
	var md = genRandMosaic();
	drawMosaic(svg, md);
}

var clearSvg = function(svg) {
	svg.selectAll('rect').remove();
}
