$('#load-btn').on('click', function() {
	$('#file-input').trigger('click');
});

var handleLoad = function(files) {
	f = files[0]
	/*d3.select('#load-btn')
		.attr('href', '/load/' + f.name);*/
	console.log('called');
	$('#load-frm-btn').trigger('click');
}
