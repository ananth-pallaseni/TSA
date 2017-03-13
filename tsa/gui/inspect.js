
graph = {};
selectedEdge = null;
selectedNode = null;
numGraphs = null;

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


var redraw = function() {
	drawGraphPadded(svg, graph.nodes, graph.edges, graph.layout);
}

var initGraphData = function() {
	var dataPane = d3.select('#graph-data-col')

	dataPane.append('h4')
		.attr('id', 'graph-data-title-p')
		.attr('align', 'center')
		.text('Graph Data');

	dataPane.append('p')
		.attr('id', 'rank-p');
		
	dataPane.append('p')
		.attr('id', 'dist-p');

	dataPane.append('p')
		.attr('id', 'num-species-p');
	
	dataPane.append('p')
		.attr('id', 'num-edges-p');
}

var updateGraphData = function() {

	d3.select('#rank-p')
		.text('Rank: ' + graph.rank);
		
	d3.select('#dist-p')
		.text('Distance: ' + graph.dist);
	
	d3.select('#num-edges-p')
		.text(graph.edges.length + ' Edges');

	d3.select('#num-species-p')
		.text(graph.nodes.length + ' Species');
}

var initInfoPane = function() {
	var infoPane = d3.select('#data-col')

	infoPane.append('h4')
		.attr('id', 'node-title-p')
		.attr('align', 'center');

	infoPane.append('h4')
		.attr('id', 'edge-title-p')
		.attr('align', 'center');

	infoPane.append('h5')
		.attr('id', 'edge-inter-p')
		.attr('align', 'center');
}


var updateInfoPane = function(params) {
	var pane = d3.select('#data-col');
	var oldPars = pane.selectAll('.param')
		.data(params)
		.exit()
		.remove();

	var newPars = pane.selectAll('.param')
		.data(params)
		.enter()
		.append('pre')
		.attr('class', 'param');

	var allPars = pane.selectAll('.param')
		.text(function(d) {
			return 'Parameter Type: ' + d.paramType + '\n'
					+ 'Value: ' + d.val + '\n'
					+ 'Bounds: (' + d.bounds + ')';
		});
}

var clearInfoPane = function() {
	updateInfoPane([]);
	d3.select('#edge-title-p')
		.style('display', 'none');
	d3.select('#node-title-p')
		.style('display', 'none');
	d3.select('#edge-inter-p')
		.style('display', 'none');
}


var clearHighlights = function() {
	if (selectedEdge != null) {
		var item = d3.selectAll('.edge-hover')
			.filter(e => e.from == selectedEdge.from && e.to == selectedEdge.to);
		item.attr('stroke-opacity', 0)
		.on('mouseout', function() {
			item.attr('stroke-opacity', 0);
		}); 

	}
	if (selectedNode != null) {
		var item = d3.selectAll('.node')
			.filter(n => n.id == selectedNode.id)
			.attr('stroke-width', 0);
	}
	selectedEdge = null;
	selectedNode = null;
}

var clearInfoAndHighlights = function() {
	clearHighlights();
	clearInfoPane();
}

var highlightSelected = function() {
	if (selectedEdge != null) {
		d3.selectAll('.edge-hover')
			.filter(e => e.from == selectedEdge.from && e.to == selectedEdge.to)
			.attr('stroke-opacity', 0.5)
			.on('mouseout', null);
	}
	if (selectedNode != null) {
		d3.selectAll('.node')
			.filter(n => n.id == selectedNode.id)
			.attr('stroke-width', 10)
			.attr('stroke', 'black');
	}
}

var updateNodeData = function(n) {
	clearHighlights();
	selectedNode = n;
	highlightSelected();
	d3.select('#edge-title-p')
		.style('display', 'none');
	d3.select('#edge-inter-p')
		.style('display', 'none');
	d3.select('#node-title-p')
		.style('display', 'block')
		.text('Node ' + n.id);
	updateInfoPane(n.parameters);
}

var updateEdgeData = function(e) {
	clearHighlights();
	selectedEdge = e;
	highlightSelected();
	d3.select('#edge-title-p')
		.style('display', 'block')
		.text('Edge ' + e.from + ', ' + e.to);
	d3.select('#edge-inter-p')
		.style('display', 'block')
		.text('Interaction type ' + e.interaction);
	d3.select('#node-title-p')
		.style('display', 'none');

	updateInfoPane(e.parameters);
}

// Nav button functions:


var updateNavs = function() {
	if (numGraphs == null) {
		d3.json('/num-graphs', function(n) {
			numGraphs = n;
		})
	}
	document.getElementById('cur-page').value = graph.rank;
    d3.select('#back-btn')
    	.on('click', null)
        .on('click', function(d) {
            getGraph(Math.max(graph.rank -1, 0));
        });
    d3.select('#next-btn')
    	.on('click', null)
        .on('click', function(d) {
            getGraph(Math.min(graph.rank +1, numGraphs-1));
        });
    d3.select('#first-btn')
    	.on('click', null)
        .on('click', function(d) {
            getGraph(0);
        });

    d3.select('#last-btn')
    	.on('click', null)
        .on('click', function(d) {
            getGraph(numGraphs-1);
        });
    $('#cur-btn').text(graph.rank);
}


window.addEventListener('resize', redraw);

initGraphData();
initInfoPane();
backRect.on('click', clearInfoAndHighlights);

var getGraph = function(gnum) {
	d3.json('/graph/' + gnum, function(d) {
		if (d) {
			graph = d;
		  	redraw();
		  	updateGraphData();
		  	nodeOnClick(updateNodeData);
			edgeOnClick(updateEdgeData);
			updateNavs();
		}
			
	})
}

var goToGraph = function(event) {
	var to = document.getElementById('cur-page').value;
	console.log(to);
	if (to % 1 === 0) {
		getGraph(to);
	}
}

getGraph(0);




