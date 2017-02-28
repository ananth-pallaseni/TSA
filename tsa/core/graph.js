transition_duration = 700;
edge_duration = transition_duration/2;
edge_delay = transition_duration / 2;
hover_width = 15;

var cur_color = 'teal';
var randColor = function() {
	var colors = d3.schemeCategory10;
	var i = Math.floor(Math.random() * colors.length);
	cur_color= colors[i];
}


// Define arrow endings for edges
var arrowHead = null;
    
var initArrowHead = function(svg) {
	arrowHead = svg.append('marker')
	    .attr('id', 'arrow-head')
	    .attr('orient', 'auto')
	    .attr('refX', 0.1)
	    .attr('refY', 2)
	    .attr('markerWidth', 4)
	    .attr('markerHeight', 4);

	arrowHead.append('path')
	    .attr('d', 'M 0 0 V 4 L 4 2 Z')
	    .attr('fill', 'black');
}


var line_shorten = function(a, b, d, arrow) {
   var dx = b[0] - a[0];
   var dy = b[1] - a[1];
   var dist = Math.sqrt(dx*dx + dy*dy);
   var start_ratio = d / dist;
   var end_ratio = (d + arrow) / dist;

   var x1 = dx * start_ratio + a[0];
   var y1 = dy * start_ratio + a[1];

   var x2 = dx - dx*end_ratio + a[0];
   var y2 = dy - dy*end_ratio + a[1];

   return [[x1, y1], [x2, y2]];
 }

var update_edge_hovers = function(lines, layout) {
	lines.transition()
    .duration(transition_duration/4)
    .attr('stroke', cur_color)
    .attr('stroke-width', 0)
    .transition()
    .duration(0)
    .attr('x1', function(d, i) {
    	return layout[d[0]][0];
    })
    .attr('y1', function(d, i) {
    	return layout[d[0]][1];
    })
    .attr('x2', function(d, i) {
    	return layout[d[0]][0];
    })
    .attr('y2', function(d, i) {
    	return layout[d[0]][1];
    })
    .transition()
	.duration(edge_duration)
	.delay(edge_delay)
	.attr('x1', function(d, i) {
	    var n1 = layout[d[0]];
	    var n2 = layout[d[1]];
	    pos = line_shorten(n1, n2, node_radius, 15);
	    return pos[0][0];
	})
	.attr('y1', function(d, i) {
	    var n1 = layout[d[0]];
	    var n2 = layout[d[1]];
	    pos = line_shorten(n1, n2, node_radius, 15);
	    return pos[0][1];
	})
	.attr('x2', function(d, i) {
	    var n1 = layout[d[0]];
	    var n2 = layout[d[1]];
	    pos = line_shorten(n1, n2, node_radius, 15);
	    return pos[1][0];
	})
	.attr('y2', function(d, i) {
	    var n1 = layout[d[0]];
	    var n2 = layout[d[1]];
	    pos = line_shorten(n1, n2, node_radius, 15);
	    return pos[1][1];
	})
    .attr('stroke-width', hover_width);
}

var update_edges = function(lines, layout) {
	lines.transition()
	.duration(transition_duration/4)
	.attr('opacity', 0)
	.transition()
	.duration(0)
	.attr('x1', function(d, i) {
	    var n1 = layout[d[0]];
	    var n2 = layout[d[1]];
	    pos = line_shorten(n1, n2, node_radius, 15);
	    return pos[0][0];
	})
	.attr('y1', function(d, i) {
	    var n1 = layout[d[0]];
	    var n2 = layout[d[1]];
	    pos = line_shorten(n1, n2, node_radius, 15);
	    return pos[0][1];
	})
	.attr('x2', function(d, i) {
	    var n1 = layout[d[0]];
	    var n2 = layout[d[1]];
	    pos = line_shorten(n1, n2, node_radius, 15);
	    return pos[0][0];
	})
	.attr('y2', function(d, i) {
	    var n1 = layout[d[0]];
	    var n2 = layout[d[1]];
	    pos = line_shorten(n1, n2, node_radius, 15);
	    return pos[0][1];
	})
	.transition()
	.duration(edge_duration)
	.delay(edge_delay)
	.attr('x1', function(d, i) {
	    var n1 = layout[d[0]];
	    var n2 = layout[d[1]];
	    pos = line_shorten(n1, n2, node_radius, 15);
	    return pos[0][0];
	})
	.attr('y1', function(d, i) {
	    var n1 = layout[d[0]];
	    var n2 = layout[d[1]];
	    pos = line_shorten(n1, n2, node_radius, 15);
	    return pos[0][1];
	})
	.attr('x2', function(d, i) {
	    var n1 = layout[d[0]];
	    var n2 = layout[d[1]];
	    pos = line_shorten(n1, n2, node_radius, 15);
	    return pos[1][0];
	})
	.attr('y2', function(d, i) {
	    var n1 = layout[d[0]];
	    var n2 = layout[d[1]];
	    pos = line_shorten(n1, n2, node_radius, 15);
	    return pos[1][1];
	})
	.attr('opacity', 1);
}


var draw_edge_hovers = function(svg, edges, layout, node_radius) {
	// Grab edge-hovers that need to vanish and update
	var done_edge_hovers = svg.selectAll('line.edge-hover')
		.data(edges)
		.exit()
		.remove();

	// Create new edge hovers 
	var new_edge_hovers = svg.selectAll('line.edge-hover')
		.data(edges)
		.enter()
	    .append('line')
		.attr('class', 'edge-hover')
	    .attr('stroke', cur_color)
	    .attr('stroke-width', 0)
	    .attr('stroke-opacity', 0)
	    .attr('x1', svg.attr('width')/2)
	    .attr('y1', svg.attr('height')/2)
	    .attr('x2', svg.attr('width')/2)
	    .attr('y2', svg.attr('height')/2)
	    .on('mouseover', function(d) {
	    	d3.select(this)
	    		.attr('stroke-opacity', 0.5);
	    	console.log('mouseover')
	    })
	    .on('mouseout', function(d) {
	    	d3.select(this)
	    		.attr('stroke-opacity', 0)
	    });

	new_edge_hovers.append('title')
	    .text(function(d, i) {
	        return 'Edge = (' + d[0] + ', ' + d[1] + ')';
	    });

	// Grab existing edge hovers and update
	var all_hovers = svg.selectAll('line.edge-hover')
		.data(edges);
	update_edge_hovers(all_hovers, layout);
}


var draw_edges = function(svg, edges, layout, node_radius) {

	if (arrowHead == null) {
		console.log('initializing arrowHead');
		initArrowHead(svg);
	}

	// Grab edges that need to vanish and update
	var done_edges = svg.selectAll('line.edge')
		.data(edges)
		.exit()
		.transition()
		.duration(transition_duration)
		.attr('x1', svg.attr('width')/2)
	    .attr('y1', svg.attr('height')/2)
	    .attr('x2', svg.attr('width')/2)
	    .attr('y2', svg.attr('height')/2)
		.attr('stroke-opacity', 0)
		.attr('marker-end', null)
		.remove();

	// Create new edges
	var new_edges = svg.selectAll('line.edge')
		.data(edges)
		.enter()
		.append('line')
		.attr('class', 'edge')
	    .attr('stroke', 'black')
	    .attr('stroke-width', 4)
	    .attr('marker-end', 'url(#arrow-head)')
	    .attr('x1', svg.attr('width')/2)
	    .attr('y1', svg.attr('height')/2)
	    .attr('x2', svg.attr('width')/2)
	    .attr('y2', svg.attr('height')/2)
	    .attr('opacity', 0);

	new_edges.append('title')
	    .text(function(d, i) {
	        return 'Edge = (' + d[0] + ', ' + d[1] + ')';
	    });

	// Grab all edges
	var all_edges = svg.selectAll('line.edge')
		.data(edges);

	update_edges(all_edges, layout);

}

var update_nodes = function(nodes, layout) {
	nodes.transition()
	.duration(transition_duration)
	.attr('cx', function(d, i) {
        return layout[i][0];
    })
    .attr('cy', function(d, i) {
        return layout[i][1];
    })
    .attr('fill-opacity', 1)
    .attr('fill', cur_color);
	    
}

var draw_nodes = function(svg, node_lst, layout, node_radius) {
	// Grab nodes that need to vanish and update
	var done_nodes = svg.selectAll('circle.node')
		.data(node_lst)
		.exit()
		.transition()
		.duration(transition_duration)
		.attr('cx', svg.attr('width')/2)
	    .attr('cy', svg.attr('height')/2)
	    .attr('fill-opacity', 0)
		.remove();

	// Create new nodes
	var new_nodes = svg.selectAll('circle.node')
	    .data(node_lst)
	    .enter()
	    .append('circle')
	    .attr('class', 'node')
	    .attr('r', node_radius)
	    .attr('fill', 'teal')
	    .attr('cx', svg.attr('width')/2)
	    .attr('cy', svg.attr('height')/2)
	    .attr('fill-opacity', 0);

	new_nodes.append('title')
	    .text(function(d, i) {
	        return 'Node ' + d;
	    });

	// Grab all nodes and update
	var cur_nodes = svg.selectAll('circle.node')
	    .data(node_lst);
	update_nodes(cur_nodes, layout);
	

}

var draw_graph = function(svg, node_lst, edges, layout, node_radius) {
	if (arrowHead == null) {
		console.log('initializing arrowHead');
		initArrowHead(svg);
	}

	randColor();

	draw_edges(svg, edges, layout, node_radius);

	draw_edge_hovers(svg, edges, layout, node_radius);

	draw_nodes(svg, node_lst, layout, node_radius);
}

var get_graph = function() {
	url = 'http://localhost:8081/graph';
	console.log(url);
	var new_graph = null;
	d3.json(url, function(d) {
		new_graph = d;
		console.log(d);
	})
	return new_graph;
}

