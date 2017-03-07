

var svg = d3.select('#graph-col')
    .append('svg')
    .attr('class', 'graph')
    .attr('width', '100%')
    .attr('height', '100%')
    .attr('id', 'main-svg');

var backRect = svg.append('rect')
    .attr('width', '100%')
    .attr('height', '100%')
    .attr('fill', 'red')
    .attr('fill-opacity', 0);

var padLayouts = function(layout) {
	var whalf = svgWidth()/2;
	var hhalf = svgHeight()/2;
	var nrad = rad5();
	var pad = nrad * 2;

	var padded = layout.map(function(coords) {
		var x = coords[0];
		var y = coords[1];
		var nx = x * (whalf - pad) + whalf;
		var ny = y * (hhalf - pad) + hhalf;
		return [nx, ny];
	});

	return padded;
}


var node_lst = [0, 1, 2, 3, 4, 5];

var layout = [[1.0, 0.0], 
              [0.5, 0.866],
              [-0.5, 0.866],
              [-1.0, 0],
              [-0.5, -0.866],
              [0.5, -0.866]];

var edges = [[2, 0],
             [4, 0],
             [5, 1],
             [4, 2],
             [0, 3],
             [1, 4],
             [0, 5],
             [3, 5]];

/*drawGraphPadded(svg, node_lst, edges, layout);*/
nodeOnClick(nodeInfo);
edgeOnClick(edgeInfo);


var redraw = function() {
	drawGraphPadded(svg, node_lst, edges, layout);
}
window.addEventListener('resize', redraw);




d3.select('svg')
	.on('click', function(d) {
		var gnum = Math.floor(Math.random() * 1000);
		var url = window.location.hostname + '/graph/' + gnum;
		d3.json(url, function(d) {
			node_lst = d.nodes; 
			edges = d.edges;
			layout = d.layout;
		  	redraw();
	})

});