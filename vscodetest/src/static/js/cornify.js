// Adapted from https://gist.github.com/philwinkle/9916577
var cornify_count = 0;

function cornify_add(cornify_images) {
	// Add a single random image at random position on the screen.
	"use strict";

	cornify_count += 1;
	var div = document.createElement('div');
	div.style.position = 'fixed';

	var numType = 'px';
	var heightRandom = Math.random() * 0.75;
	var windowHeight = 768;
	var windowWidth = 1024;
	var height = 0;
	var de = document.documentElement;

	// Get window height and width.
	if (typeof(window.innerHeight) === 'number') {
		windowHeight = window.innerHeight;
		windowWidth = window.innerWidth;
	} else if (de && de.clientHeight) {
		windowHeight = de.clientHeight;
		windowWidth = de.clientWidth;
	} else {
		numType = '%';
		height = Math.round(height * 100) + '%';
	}

	div.style.zIndex = 10;
	div.style.outline = 0;

	// Set positioning.
	if (cornify_count === 15) {
		div.style.top = Math.max(0, Math.round((windowHeight - 530) / 2)) + 'px';
		div.style.left = Math.round((windowWidth - 530) / 2) + 'px';
		div.style.zIndex = 1000;
	} else {
		if (numType === 'px') {
			div.style.top = Math.round(windowHeight * heightRandom - 100) + numType;
		} else {
			div.style.top = height;
		}
		div.style.left = Math.round(Math.random() * 90 - 5) + '%';
	}

	var img = document.createElement('img');

	// Pick a random image from an array of arbitrary length of image filenames
	var image_count = cornify_images.length;
	var image_index = Math.floor(Math.random() * image_count);
	var image_filename = cornify_images[image_index];
	img.setAttribute('src', '/static/img/cornify/' + image_filename);
	div.style.WebkitTransition = "all .1s linear";
	div.style.WebkitTransform = "rotate(1deg) scale(1.01,1.01)";
	div.style.transition = "all .1s linear";

	// Give images a responsive effect on mouseover events by scaling and rotating them.
	div.onmouseover = function () {
		var size = 1 + Math.round(Math.random() * 10) / 100;
		var angle = Math.round(Math.random() * 20 - 10);
		var result = "rotate(" + angle + "deg) scale(" + size + "," + size + ")";
		this.style.transform = result;
		this.style.WebkitTransform = result;
	};

	div.onmouseout = function () {
		var size = 0.9 + Math.round(Math.random() * 10) / 100;
		var angle = Math.round(Math.random() * 6 - 3);
		var result = "rotate(" + angle + "deg) scale(" + size + "," + size + ")";
		this.style.transform = result;
		this.style.WebkitTransform = result;
	};

	// Finally add the div and image we've built to the page.
	var body = document.getElementsByTagName('body')[0];
	body.appendChild(div);
	div.appendChild(img);

	cornify_replace();
	cornify_update_count();
}

function cornify_update_count() {
	"use strict";
	// Show a count at the bottom of the page of how many images were added
	var p = document.getElementById('cornifycount');
	if (p === null) {
		p = document.createElement('p');
		p.id = 'cornifycount';
		p.style.position = 'fixed';
		p.style.bottom = '5px';
		p.style.left = '0px';
		p.style.right = '0px';
		p.style.zIndex = '1000000000';
		p.style.color = '#ff00ff';
		p.style.textAlign = 'center';
		p.style.fontSize = '24px';
		p.style.fontFamily = "'Comic Sans MS', 'Comic Sans', 'Marker Felt', serif";
		var body = document.getElementsByTagName('body')[0];
		body.appendChild(p);
	}
	if (cornify_count === 1) {
		p.innerHTML = cornify_count + ' CHAMPION, UNICORN OR RAINBOW CREATED';
	} else {
		p.innerHTML = cornify_count + ' CHAMPIONS, UNICORNS &AMP; RAINBOWS CREATED';
	}
}

function cornify_replace() {
	"use strict";

	// Prepend the text in headings on the page with adjectives to make them extra special
	var hc = 6;
	var hs;
	var h;
	var k;
	var words = ['Happy', 'Sparkly', 'Glittery', 'Fun', 'Magical', 'Lovely', 'Cute', 'Charming', 'Amazing', 'Wonderful'];
	while (hc >= 1) {
		hs = document.getElementsByTagName('h' + hc);
		for (k = 0; k < hs.length; k++) {
			h = hs[k];
			h.innerHTML = words[Math.floor(Math.random() * words.length)] + ' ' + h.innerHTML;
		}
		hc -= 1;
	}
}
