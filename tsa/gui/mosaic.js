var SELECTED_ROW = null;
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
	var svg = d3.select('#mosaic-svg');

	if (SELECTED_ROW != null) {
		SELECTED_ROW.selectAll('.tbl-col-0')
			.style('background', 'transparent')
		SELECTED_ROW.selectAll('.tbl-col-1')
			.style('background', 'transparent')
		SELECTED_ROW.selectAll('.tbl-col-2')
			.style('background', 'transparent')
		SELECTED_ROW.on('mouseout', tblRowMouseout);
	}
	SELECTED_ROW = d3.select(this);
	SELECTED_ROW.selectAll('.tbl-col-0')
		.style('background', 'grey')
	SELECTED_ROW.selectAll('.tbl-col-1')
		.style('background', 'grey')
	SELECTED_ROW.selectAll('.tbl-col-2')
		.style('background', 'grey')
	SELECTED_ROW.on('mouseout', null);

	clearSvg(svg);
	var md = data.contingency[0];
	var rind = data.contingency[1];
	var cind = data.contingency[2];
	var md = preprocessMosaic(md);
	var e1 = data.interactome1;
	var e2 = data.interactome2;
	drawMosaic(svg, md, rind, cind, e1, e2);
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

var drawMosaic = function(svg, mosaicData, rowlabels, collabels, e1, e2, colors) {
	if (!colors) {
		colors = d3.schemeCategory10.slice(0,4);
	}

	console.log(rowlabels)
	console.log(collabels)

	var side = Math.min(svgHeight(svg), svgWidth(svg)) * 0.85;
	var xPad = (svgWidth(svg) - side) / 2;
	var yPad = (svgHeight(svg) - side) / 2;

	svg.selectAll('rect')
		.remove();

	svg.selectAll('.edge-lbl')
		.remove();
	
	
	var m00 = mosaicData[0][0]
	var r00 = svg.append('rect')
		.attr('x', xPad + 5)
		.attr('y', yPad + 5)
		.attr('width', Math.max(1, m00[0] * side - 6))	
		.attr('height', Math.max(1, m00[1] * side - 6))
		.attr('fill', colors[0])
		.style('outline', '1px solid black')


	var m01 = mosaicData[0][1]
	var r01 = svg.append('rect')
		.attr('x', xPad + Math.max(6, m00[0] * side) + 5)
		.attr('y', yPad + 5)
		.attr('width', Math.max(1, m01[0] * side - 6))	
		.attr('height', Math.max(1, m01[1] * side - 6))
		.attr('fill', colors[1])
		.style('outline', '1px solid black')


	var m10 = mosaicData[1][0];
	var r10 = svg.append('rect')
		.attr('x', xPad + 5)
		.attr('y', yPad + Math.max(6, m00[1]*side) + 5)
		.attr('width', Math.max(1, m10[0] * side - 6))	
		.attr('height', Math.max(1, m10[1] * side - 6))
		.attr('fill', colors[2])
		.style('outline', '1px solid black')

	var m11 = mosaicData[1][1];
	var r11 = svg.append('rect')
		.attr('x', xPad + Math.max(6, m10[0]*side) + 5)
		.attr('y', yPad + Math.max(6, m01[1]*side) + 5)
		.attr('width', Math.max(1, m11[0] * side - 6))	
		.attr('height', Math.max(1, m11[1] * side - 6))
		.attr('fill', colors[3])
		.style('outline', '1px solid black')


	var e1lblX = xPad/4;
	var e1lblY = yPad + side/2;
	svg.append('text')
		.text('Has (' + e1 + ')')
		.attr('class', 'edge-lbl')
		.attr('transform', 'translate(' + e1lblX + ', ' + e1lblY + ') rotate(270)')
		.attr('font-family', 'Verdana')
		.attr('text-anchor', 'middle');

	var e2lblX = xPad + side/2;
	var e2lblY = yPad/4;
	svg.append('text')
		.text('Has (' + e2 + ')')
		.attr('class', 'edge-lbl')
		.attr('transform', 'translate(' + e2lblX + ', ' + e2lblY + ')')
		.attr('font-family', 'Verdana')
		.attr('text-anchor', 'middle');


	var c1lblX = m00[0] > 0 ? xPad + 5 + Math.max(1, m00[0] * side - 6)/2 : -1;
	var c1lblY = 3 * yPad/4;
	if (c1lblX > 0) {
		svg.append('text')
			.text(collabels[0] == -1 ? 'No' : 'Yes')
			.attr('class', 'edge-lbl')
			.attr('transform', 'translate(' + c1lblX + ', ' + c1lblY + ')')
			.attr('font-family', 'Verdana')
			.attr('text-anchor', 'middle');
	}

	var c2lblX = m01[0] > 0 ? xPad + m00[0] * side + 5 + Math.max(1, m01[0] * side - 6)/2 : -1;
	var c2lblY = 3 * yPad/4;
	if (collabels.length > 1 && c2lblX > 0) {
		svg.append('text')
			.text(collabels[1] == -1 ? 'No' : 'Yes')
			.attr('class', 'edge-lbl')
			.attr('transform', 'translate(' + c2lblX + ', ' + c2lblY + ')')
			.attr('font-family', 'Verdana')
			.attr('text-anchor', 'middle');
	}

	var r1lblX = 3*xPad/4;
	var r1lblY = m00[0] > 0 && m00[1] > 0 ? yPad + 5 + Math.max(1, m00[1] * side - 6)/2 : -1;
	if (r1lblY > 0) {
		svg.append('text')
			.text(rowlabels[0] == -1 ? 'No' : 'Yes')
			.attr('class', 'edge-lbl')
			.attr('transform', 'translate(' + r1lblX + ', ' + r1lblY + ')')
			.attr('font-family', 'Verdana')
			.attr('text-anchor', 'middle');
	}

	var r2lblX = 3*xPad/4;
	var r2lblY = m10[0] > 0 && m10[1] > 0 ? yPad + m00[1]*side + 5 + Math.max(1, m10[1] * side - 6)/2 : -1;
	if (rowlabels.length > 1 && r2lblY > 0) {
		svg.append('text')
			.text(rowlabels[1] == -1 ? 'No' : 'Yes')
			.attr('class', 'edge-lbl')
			.attr('transform', 'translate(' + r2lblX + ', ' + r2lblY + ')')
			.attr('font-family', 'Verdana')
			.attr('text-anchor', 'middle');
	}

	var r3lblX = svgWidth(svg) - 3*xPad/4;
	var r3lblY = m01[0] > 0 && m01[1] > 0 ? yPad + 5 + Math.max(1, m01[1] * side - 6)/2 : -1;
	if (r3lblY > 0) {
		svg.append('text')
			.text(rowlabels[0] == -1 ? 'No' : 'Yes')
			.attr('class', 'edge-lbl')
			.attr('transform', 'translate(' + r3lblX + ', ' + r3lblY + ')')
			.attr('font-family', 'Verdana')
			.attr('text-anchor', 'middle');
	}

	var r4lblX = svgWidth(svg) - 3*xPad/4;
	var r4lblY = m11[0] > 0 && m11[1] > 0 ? yPad + m01[1]*side + 5 + Math.max(1, m11[1] * side - 6)/2 : -1;
	if (rowlabels.length > 1 && r4lblY > 0) {
		svg.append('text')
			.text(rowlabels[1] == -1 ? 'No' : 'Yes')
			.attr('class', 'edge-lbl')
			.attr('transform', 'translate(' + r4lblX + ', ' + r4lblY + ')')
			.attr('font-family', 'Verdana')
			.attr('text-anchor', 'middle');
	}
}

var preprocessMosaic = function(m) {
	var rsum = m[0][0] + m[0][1];
	var csum1 = m[1][0] + m[0][0];
	var csum2 = m[0][1] + m[1][1];

	var data = [ [[ m[0][0] / rsum , m[0][0] / csum1], [ m[0][1] / rsum, m[0][1] / csum2]],
				 [[ m[0][0] / rsum , m[1][0] / csum1], [ m[0][1] / rsum, m[1][1] / csum2]] ];

	return data;
}

var drawRand = function(svg) {
	var md = genRandMosaic();
	drawMosaic(svg, md, [-1, -1], [-1, -1]);
}

var clearSvg = function(svg) {
	svg.selectAll('rect').remove();
}
