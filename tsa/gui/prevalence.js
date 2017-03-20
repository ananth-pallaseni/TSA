
var generatePrevalenceScale = function(edges, maxWidth) {
	// Find the most occurrences
	var maxNum = edges.map(e => e.occurrences)
		.reduce((a,b) => Math.max(a,b));

	// Create a scale that maps from {1, maxNum} to {1, maxWidth}
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

var drawPrevalenceGraphFrom = function(svg, nodes, edges, layout, color) {
	var nodes_cut = nodes.filter(n => !n.complex);
	//edges = edges.filter(e => e.occurrences > 0);
	console.log(edges);
	if (color) {
	  	drawPrevalenceGraphColor(svg, nodes_cut, edges, layout, color);
	}
	else {
	  	drawPrevalenceGraph(svg, nodes_cut, edges, layout);
	}
}