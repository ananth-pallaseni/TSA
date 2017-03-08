
var generatePrevalenceScale = function(edges, maxWidth) {
	// Find the most occurrences
	var maxNum = edges.map(e => e.occurrences)
		.reduce((a,b) => Math.max(a,b));

	// Create a scale that maps from {1, maxOccur} to {1, maxWidth}
	var sc = d3.scaleLinear()
		.domain([1, maxNum])
		.range([1, maxWidth]);

	console.log(maxNum, maxWidth);

	return sc;
}

var drawPrevalenceGraph = function(svg, nodes, edges, layout) {
	var padLay = padLayoutsSquare(svg, layout);
	var nrad = rad5(svg);
	var edgeRad = 4;

	var maxWidth = 10;
	var sc = generatePrevalenceScale(edges, maxWidth);


	draw_graph(svg, nodes, edges, padLay, nrad, sc);
}