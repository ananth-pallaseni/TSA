
var generatePrevalenceScale = function(edges, maxWidth) {
	// Find the most occurrences
	var maxNum = edges.map(e => e.occurrences)
		.reduce((a,b) => Math.max(a,b));

	// Create a scale that maps from {1, maxOccur} to {1, maxWidth}
	var sc = d3.scaleLinear()
		.domain([1, maxNum])
		.range([1, maxWidth]);

	return sc;
}

var drawPrevalenceGraph = function(svg, nodes, edges, layout) {
	var maxWidth = 10;
	var sc = generatePrevalenceScale(edges, maxWidth);

	drawGraphPadded(svg, nodes, edges, layout, sc);
}

var drawPrevalenceGraphColor = function(svg, nodes, edges, layout, color) {
	var maxWidth = 10;
	var sc = generatePrevalenceScale(edges, maxWidth);

	drawGraphPaddedColor(svg, nodes, edges, layout, color, sc);
}

var drawPrevalenceGraphFrom = function(svg, mat, color) {
	var nodes = Array.from(Array(mat.length).keys())
		.map(function(i) {
			return {id: i};
		});

	var edges = [];
	for (var r = 0; r < mat.length; r++) {
		for (var c = 0; c < mat.length; c++) {
			var occ = mat[r][c];
			if (occ > 0) {
				var e = {from: r, 
						 to: c,
						 occurrences: occ};
				edges.push(e);
			}
			
		}
	}

	var step = Math.PI * 2 / nodes.length;
	var layout = nodes.map(function(n, i) {
		return [Math.cos(i*step), Math.sin(i*step)];
	})

	if (color) {
		drawPrevalenceGraphColor(svg, nodes, edges, layout, color);
	}
	else {
		drawPrevalenceGraph(svg, nodes, edges, layout);
	}
}