
var svgWidth = function(svg) {
	var svgid = svg.attr('id');
	return $('#' + svgid).width()
}
var svgHeight = function(svg) {
	var svgid = svg.attr('id');
	return $('#' + svgid).height()
}

var getAndPlot = function(svg, numtop, ptype, isnode, index) {
	var url = '/pdensity/' + numtop + '?' + ptype + '?' + isnode + '?' + index;
	d3.json(url, function(d) {
		console.log(d);
	    plotDensity(svg, d.x, d.y);
	})
}

var plotDensity = function(svg, x, y, color) {
	svg.selectAll('.g-elem')
		.remove();

	var minx = x.reduce( (a,b) => Math.min(a,b))
	var maxx = x.reduce( (a,b) => Math.max(a,b))
	var miny = y.reduce( (a,b) => Math.min(a,b))
	var maxy = y.reduce( (a,b) => Math.max(a,b))

	var startx = svgWidth(svg) * 0.05;
	var endx = svgWidth(svg) - startx;
	var starty = svgHeight(svg) * 0.05;
	var endy = svgHeight(svg) - starty;

	var qqqqq = -10;
	for (var i = 0; i < y.length; i++) {
		qqqqq = Math.max(qqqqq, y[i]);
	}
	console.log(qqqqq);
	console.log(minx, maxx, miny, maxy);
	console.log(startx, endx, starty, endy);

	var xscale = d3.scaleLinear()
		.domain([minx, maxx])
		.range([startx, endx]);

	var yscale = d3.scaleLinear()
		.domain([miny, maxy])
		.range([endy, starty]);

	var coords = x.map((d, i) => [d, y[i]])

	var line = d3.line()
		.x(d => xscale(d[0]))
		.y(d => yscale(d[1]));

	var xaxis = d3.axisBottom()
		.scale(xscale);

	var yaxis = d3.axisLeft()
		.scale(yscale);

	svg.append('g')
		.attr('class', 'g-elem')
		.attr('id', 'x-axis')
		.attr('transform', 'translate(0' + ',' + endy + ')')
		.call(xaxis);

	svg.append('g')
		.attr('class', 'g-elem')
		.attr('id', 'y-axis')
		.attr('transform', 'translate(' + startx + ',0)')
		.call(yaxis);

	if (!color) {
		color = 'black'
	}

	svg.append('path')
		.datum(coords)
		.attr('class', 'g-elem')
		.attr('id', 'graph-line')
		.attr('d', line)
		.attr('fill', 'transparent')
		.attr('stroke', color);
}

var indexChange = function(isNode) {
	if (isNode) {
		populateNodeSelect();
	}
	else {
		populateEdgeSelect();
	}
}

var populateTypeSelect = function() {
	d3.selectAll('.type-opts').remove();
	var widget = d3.select('#type-select');
	d3.json('/ptypes', function(d) {
		filtered = document.getElementById('index-select').value == 'Node' ? d.filter(q => !q.is_edge_param) : d.filter(q => q.is_edge_param);
		console.log(filtered)
		for (var i = 0; i < filtered.length; i++) {
			var opt = filtered[i]
			console.log(opt)
			widget.append('option')
				.attr('class', 'type-opts')
				.text(opt.param_type);
		}
	})
}

var populateNodeSelect = function() {
	d3.selectAll('.node-opts').remove();
	d3.selectAll('.edge-select').attr('disabled', 'disabled');
	var widget = d3.select('#node-select');
	widget.attr('disabled', null);
	d3.json('/node_names', function(d) {
		for (var key in d) {
			var opt = d[key]
			widget.append('option')
				.attr('class', 'node-opts')
				.attr('value', key)
				.text(opt + '  (id:' + key + ')');
		}
	})
}

var populateEdgeSelect = function() {
	d3.selectAll('.node-opts').remove();
	d3.selectAll('.edge-select').attr('disabled', null);

	d3.select('#node-select')
		.attr('disabled', 'disabled');;

	var fromwidget = d3.select('#from-select');
	d3.json('/node_names', function(d) {
		for (var key in d) {
			var opt = d[key]
			fromwidget.append('option')
				.attr('class', 'node-opts')
				.attr('value', key)
				.text(opt + '  (id:' + key + ')');
		}
	})

	var towidget = d3.select('#to-select');
	d3.json('/node_names', function(d) {
		for (var key in d) {
			var opt = d[key]
			towidget.append('option')
				.attr('class', 'node-opts')
				.attr('value', key)
				.text(opt + '  (id:' + key + ')');
		}
	})


}

var go = function() {
	var isNode = document.getElementById('index-select').value == 'Node';

	var index = null;
	if (isNode) {
		var nsel = document.getElementById('node-select');
		var node = nsel.options[nsel.selectedIndex].value;
		index = node;
	}
	else {
		var fromsel = document.getElementById('from-select');
		var fromval = fromsel.options[fromsel.selectedIndex].value;

		var tosel = document.getElementById('to-select');
		var toval = tosel.options[tosel.selectedIndex].value;

		index = [fromval, toval]

	}
	

	var psel = document.getElementById('type-select');
	var ptype = psel.options[psel.selectedIndex].text;


	var numtop = document.getElementById('top-select').value;

	var svg = d3.select('#d-svg');

	var nodeOrEdge = isNode ? 'node' : 'edge';

	getAndPlot(svg, numtop, ptype, nodeOrEdge, index);

}
