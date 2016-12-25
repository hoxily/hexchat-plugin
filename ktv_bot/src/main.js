/*
 * 点歌、排队、搜索的实现主体。
 */
(function (w,d) {
	// 每隔6秒，就去读取最新点歌沟通文件
	setInterval(function () {
		console.log('check newest input.');
		var h = d.getElementsByTagName('head');
		h = h[0];
		var s = d.createElement('script');
		// 加上一个总是不断变化的时间戳，以避免被缓存。
		s.src = 'http://localhost:8080/newest.js?timestamp=' + (new Date()).valueOf(); 
		s.type = 'text/javascript';
		h.appendChild(s);
	}, 6000);
	// 解析 hh:mm:ss 格式的时间，返回秒数
	w.hox_parse_time = function(s) {
		var arr = s.split(':');
		var seconds = 0;
		var k = 1;
		for (var i = arr.length - 1; i >= 0; i--) {
			seconds = seconds + (new Number(arr[i])) * k;
			k = k * 60;
		}
		return seconds;
	};
	// 每隔1秒刷新一遍当前正在播放歌曲名
	setInterval(function(){
		if (player.getPlaying().playing) {
			w.hox_message_board.children[0].innerText = '正在播放：' + d.title.substring(2);
		} else {
			w.hox_message_board.children[0].innerText = '正在播放：';
		}
	}, 1000);
	// 每当排队等待播放的歌曲队列发生变化时调用此函数
	w.hox_on_play_queue_changed = function(){
		console.log('current play queue:');
		console.log(w.hox_queue);
		var s = JSON.stringify(w.hox_queue);
		w.hox_message_board.children[1].innerText = '正在排队：' + s;
		// 把排队歌名存起来，可以实现自动恢复排队歌曲
		try {
			w.localStorage.setItem('hox_queue', s);
		} catch(e) {
			console.log(e);
		}
	};
	// 每隔1秒就检测一遍当前正在播放的歌曲是不是已经快要播放完毕，
	// 首先暂停当前播放的歌曲，并自动切换到下一首歌。
	setInterval(function(){
		// player 对象是由 music.163.com 自己提供的。
		if (w.player.getPlaying().playing) {
			var t = d.getElementsByClassName('time');
			t = t[0];
			t = t.innerText.split(' / ');
			var t0 = w.hox_parse_time(t[0]);
			var t1 = w.hox_parse_time(t[1]);
			var epsilong = 3;
			if (Math.abs(t0 - t1) < epsilong && w.hox_queue.length > 0) {
				w.player.pause(); 
				w.hox_play_by_name(w.hox_queue.shift());
				w.hox_on_play_queue_changed();
			}
		}
	}, 1000);
	// 记下前一次沟通文件里的歌名。用于避免重复加入同一首歌。
	w.hox_prev_name = '';
	// 当前的待播放排队队列
	w.hox_queue = [];
	// 自动恢复排队歌曲
	try {
		var s = w.localStorage.getItem('hox_queue');
		if (s != null && s!= undefined && s.length > 0) {
			w.hox_queue = JSON.parse(s);
			if (w.hox_queue.length > 0) {
				w.hox_prev_name = w.hox_queue[w.hox_queue.length - 1];
			}
		}
	} catch(e) {
		console.log(e);
	}
	// 处理沟通文件的函数
	w.hox_jsonp = function(o){
		if (w.hox_prev_name == o.name) {
			console.log('no change.');
			return;
		}
		w.hox_prev_name = o.name;
		w.hox_queue.push(o.name);
		console.log('add one request to play list queue: ' + o.name);
		w.hox_on_play_queue_changed();
	};
	// 在播放失败的情况下，调用此函数跳过播放失败的歌曲。
	// 播放失败有多种情况，最容易出现的是搜索出来的第一首
	// 歌曲有版权限制，不允许播放。另一种情况是搜索结果为空。
	w.hox_play_next = function() {
		if (w.hox_queue.length > 0) {
			w.hox_play_by_name(w.hox_queue.shift());
			w.hox_on_play_queue_changed();
		} else {
			var btns = d.getElementsByClassName('btns')[0];
			btns.children[1].click();
		}
	};
	// 搜索并播放指定名字的歌曲
	w.hox_play_by_name = function(name) {
		console.log('try play ' + name);
		var url = 'http://music.163.com/#/search/m/?type=1&s=' + encodeURIComponent(name);
		w.location.href = url;
		// 等待3秒后，看看能不能播放。
		setTimeout(function(){
			var plys = w.frames[0].document.getElementsByClassName('ply');
			if (plys.length > 0) {
				// 搜索结果非空的情况下，需要小心播放失败的问题。
				plys[0].click();
				// 再次等待3秒，检查是否已经在播放状态
				setTimeout(function(){
					if (!player.getPlaying().playing) {
						w.hox_play_next();
					}
				}, 3000);
			} else {
				// 搜索结果为空的话，直播跳到队列中下一首。
				w.hox_play_next();
			}
		}, 3000);
	};
	// 创建一个自定的面板区域，用于显示当前播放歌曲，和正在排队的歌曲
	var topbar = d.getElementById('g-topbar');
	var board = d.createElement('div');
	board.setAttribute('style', 'background-color:pink;width:440px;color:black;word-wrap:break-word;border-color:black;border-style:solid;margin:5px;padding:5px;border-radius:5px;font-size:24px;font-family:source code pro,microsoft yahei,monospace;font-size:24px;font-weight:bold;');
	topbar.appendChild(board);
	w.hox_message_board = board;
	var p0 = d.createElement('p');
	board.appendChild(p0);
	var p1 = d.createElement('p');
	board.appendChild(p1);
	
	w.hox_on_play_queue_changed();
})(window, document);