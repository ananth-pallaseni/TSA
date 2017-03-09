var allColors = d3.schemeCategory10;
var curColorPos = 0;
var cur_color = 'teal';
var timeOffset = 10;

var svgWidth = function(svg) {
	var svgid = svg.attr('id');
	return $('#' + svgid).width()
}
var svgHeight = function(svg) {
	var svgid = svg.attr('id');
	return $('#' + svgid).height()
}

var nextColor = function() {
	cur_color = allColors[curColorPos];
	curColorPos++;
	if (curColorPos >= allColors.length) {
		curColorPos = 0;
	}
}

var heatmapFrom = function(mat, numBuckets) {
	// Split mat vals into buckets
	var maxVal = 1;
	mat.forEach(row => 
		row.forEach(val => 
			{maxVal = Math.max(val, maxVal);}
			)
		);


	// Define colors for buckets (Randomly)
	var colorChoices = d3.schemeCategory10;
	
	// Create an arary of colors from white to baseColor
	var colorArr = Array.from(Array(numBuckets).keys())
		.map(i=>i/10)
		.map(d3.interpolate('white', cur_color));

	// Create a scale that maps from {0,maxVal} to colorArr 
	var colorScale = d3.scaleQuantize()
		.domain([0, maxVal])
		.range(colorArr);

	// Map colors onto bucketed vals
	var hm = mat.map(row => 
		row.map(function(val) {
			return {val: val, 
					ratio: val/maxVal, 
					color: colorScale(val)}
		}));

	return hm;
}

var transition_duration = 700;

var updateHeatmap = function(squares, numRows, squareSide) {
	var xWidth = squareSide * numRows;
	var xPad = (svgWidth(svg) - xWidth)/2;
	var yPad = (svgHeight(svg) - xWidth)/2;
	squares.attr('fill-opacity', 0)
		.attr('stroke-width', 0)
		.attr('x', 0)
		.attr('y', 0)
		.attr('width', squareSide)
		.attr('height', squareSide)
		.transition()
		.duration(transition_duration)
		.delay((d, i) => i * (500 / (numRows*numRows)))
		.attr('x', (d, i) => {
			var row = i % numRows;
			var xPos = row * squareSide + xPad;
			return xPos;
		})
		.attr('y', (d, i) => {
			var col = Math.floor(i / numRows);
			var yPos = col * squareSide + yPad;
			return yPos;

		})
		.attr('fill', d => d.color)
		.attr('fill-opacity', 1)
		.attr('stroke-width', 1);

	squares.select('title')
		.text(d => 'Num=' + d.val.toFixed(2) + '\nRatio=' + d.ratio.toFixed(2));
}

var drawHeatmapMosaic = function(svg, mat) {
	nextColor();

	var hm = heatmapFrom(mat, 10); 
	var numRows = hm.length;
	var side = Math.min(svgWidth(svg), svgHeight(svg)) / numRows;
	var flat = hm.reduce((a, b) => a.concat(b));

	// Delete all old grid squares
	svg.selectAll('rect.hm-square')
		.data(flat)
		.exit()
		/*.transition()
		.duration(transition_duration)
		.attr('x', svgWidth(svg))
		.attr('y', svgHeight(svg))
		.attr('fill-opacity', 0)*/
		.remove();

	// Create new grid squares
	var newSquares = svg.selectAll('rect.hm-square')
		.data(flat)
		.enter()
		.append('rect')
		.attr('class', 'hm-square')
		.attr('x', 0)
		.attr('y', 0)
		.attr('width', side)
		.attr('height', side)
		.attr('fill', d => d)
		.attr('fill-opacity', 0)
		.attr('stroke', 'black')
		.attr('stroke-width', 0);

	newSquares.append('title');

	// Select all grid squares
	var squares = svg.selectAll('rect.hm-square')
		.data(flat);


	// Update grid squares
	updateHeatmap(squares, numRows, side);

}

var drawColorScale = function(svg, scaleColor, numSquares) {

	// Create heatmap scale if it doesn't exist
	if (! $('#cmap-scale').length) {
		var cScale = svg.append('defs')
			.append('linearGradient')
			.attr('id', 'cmap-scale')
			.attr('x1', '0%')
			.attr('y1', '0%')
			.attr('x2', '0%')
			.attr('y2', '100%');

		cScale.append('stop')
			.attr('stop-color', 'white')
			.attr('offset', '0%');

		cScale.append('stop')
			.attr('id', 'cmap-stop')
			.attr('stop-color', scaleColor)
			.attr('offset', '100%');
	}

	// Update color of scale
	svg.select('#cmap-stop')
		/*.transition()
		.duration(transition_duration)*/
		.attr('stop-color', scaleColor);

	// Check if rect exists
	if (! $('cmap-rect').length) {
		var cRect = svg.append('rect')
			.attr('id', 'cmap-rect')
			.attr('width', '100%')
			.attr('height', 0)
			.attr('fill', 'url(#cmap-scale)')
			.attr('stroke', 'black');
	}

	svg.select('#cmap-rect')
		.attr('stroke-width', 0)
		.attr('height', 0)
		.transition()
		.duration(transition_duration)
		//.delay(timeOffset * numSquares)
		.delay(500)
		.attr('height', '100%')
		.attr('stroke-width', 1);


	// Check for axis text group
	if (! $('#text-g').length) {
		var textg = svg.append('g')
			.attr('id', 'text-g');

		textg.append('text')
			.text(0)
			.attr('transform', 'translate(25,' + svgHeight(svg)/20 + ')')
			.attr('font-family', 'Verdana')
			.attr('text-anchor', 'middle');

		textg.append('text')
			.text(1)
			.attr('transform', 'translate(25,' + (svgHeight(svg)-svgHeight(svg)/20) + ')')
			.attr('font-family', 'Verdana')
			.attr('text-anchor', 'middle');

		textg.append('text')
			.text(0.5)
			.attr('transform', 'translate(25,' + (svgHeight(svg)/2) + ')')
			.attr('font-family', 'Verdana')
			.attr('text-anchor', 'middle');
	}

	svg.select('#text-g').selectAll('text')
		.attr('fill', 'transparent')
		.transition()
		.duration(transition_duration)
		.delay(500)
		.attr('fill', 'black');

}

var drawHeatmap = function(mosaicSvg, scaleSvg, mat) {
	nextColor();
	drawHeatmapMosaic(mosaicSvg, mat);
	var numSquares = mat.reduce((a,b) => a.concat(b)).length;
	drawColorScale(scaleSvg, cur_color, numSquares);
}


