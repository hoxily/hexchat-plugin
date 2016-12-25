/* 这是一个用于浏览器书签的脚本。
 * 例如firefox支持创建的书签里的地址填写javascript:开头的脚本代码。
 * 这样子创建的书签被点击时，将会在当前面页上下文执行
 * javascript:后面的代码。
 * 此处创建了一个script节点，以方便引入更加复杂的功能。
 */
(function(w,d){
	var h = d.getElementsByTagName('head');
	h = h[0];
	var s = d.createElement('script');
	s.src = 'http://localhost:8080/main.js';
	s.type = 'text/javascript';
	h.appendChild(s);
})(window, document);